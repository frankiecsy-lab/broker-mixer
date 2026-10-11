"""量化交易 Web UI 的應用：只提供頁面，資料一律轉發 brokery_api 閘道。

不直接連券商：閘道進程已持有各券商連線（IB 只容許一個 client id），Web UI 再建一份即互相搶佔，兩邊都
取不到數。金鑰只在服務端使用，不會出現在頁面或瀏覽器中。
轉發原樣透傳 {"status", "data", "message"} 信封（含 status=False 的業務失敗）；閘道不可達或返回非信封
內容時由本模組構造 status=False，不變成 HTTP 500，令客戶端只需看一個欄位。
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from urllib.parse import urlencode

import httpx
import websockets
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import FileResponse

from brokery import chart
from brokery.config import get_settings
from brokery_api import log as api_log

HOME_FILE = Path(__file__).with_name("home.html")
WEBUI_LOGGER = "brokery.webui"
WEBUI_LOG_FILE = "brokery_webui.log"
# 轉發超時必須高於閘道內部最慢的兜底（IB 連線 40s），否則 Web UI 會先斷，用戶見到的是 Web UI 超時而不是
# 券商實際給出的原因。
UPSTREAM_TIMEOUT = 60.0
# 頁面「類型」選項 → 閘道的清單接口。只有這三項，其餘一律 unknown_kind，不猜用戶想要什麼。
SYMBOL_PATHS = {"stock": "/stocks", "future": "/futures", "index": "/indices"}
DEFAULT_BROKER = "futu"
# 一條 update 帶的是該代碼目前完整的 bar（最多 1000 根），遠超 websockets 預設的 1 MiB，故放宽上限。
WS_MAX_SIZE = 8 * 2 ** 20


def create_app(base_url: str | None = None, api_key: str | None = None) -> FastAPI:
    """建立應用；參數省略時一律取 .env（測試可直接傳入）。

    API_KEY 未設定時拒絕建立應用：沒有金鑰就讀不到戶口，與其每個頁面都報錯，不如在啟動時說清楚。
    """
    settings = get_settings()
    base_url = (base_url or f"http://{settings.api_host}:{settings.api_port}").rstrip("/")
    api_key = settings.api_key if api_key is None else api_key
    if not api_key:
        raise RuntimeError(
            "API_KEY 未設定：Web UI 經閘道讀取戶口，請在 .env 設 API_KEY=<自訂金鑰> 後重新啟動"
        )

    api_log.setup_logging(settings.api_log_level, settings.api_log_dir,
                         logger_name=WEBUI_LOGGER, file_name=WEBUI_LOG_FILE)
    logger = api_log.get_logger(WEBUI_LOGGER)

    app = FastAPI(title="brokery webui", description="量化交易 Web UI：頁面與閘道轉發，不直接連券商。")
    app.state.base_url = base_url
    # 瀏覽器的 WebSocket 不能自訂握手標頭，金鑰只能放進查詢串；這條只用於連上游，不出現在頁面中。
    ws_url = f"{base_url.replace('http', 'ws', 1)}/stream?api_key={api_key}"

    def forward(path: str, params: dict | None = None) -> dict:
        """轉發一個閘道接口：信封原樣透傳，取不到即明確返回 status=False。"""
        query = f"?{urlencode(params)}" if params else ""
        url = f"{base_url}{path}{query}"
        try:
            resp = httpx.get(url, headers={"X-API-Key": api_key}, timeout=UPSTREAM_TIMEOUT)
            payload = resp.json()
        except Exception as exc:  # 閘道未啟動、端口錯誤、回應不是 JSON，一律點名原因
            message = f"gateway_unreachable: {url}（{type(exc).__name__}: {exc}）"
            logger.warning("%s", message)
            return {"status": False, "data": {"columns": [], "rows": []}, "message": message}
        if resp.status_code != 200 or not isinstance(payload, dict) or "status" not in payload:
            # 鑑權失敗與請求不合法由閘道以 4xx 返回（內容為 {"detail": …}），這裡還原為同一信封。
            detail = payload.get("detail") if isinstance(payload, dict) else payload
            message = f"gateway_http_{resp.status_code}: {detail}"
            logger.warning("%s", message)
            return {"status": False, "data": {"columns": [], "rows": []}, "message": message}
        logger.info("%s → status=%s %s", url, bool(payload["status"]), payload.get("message", ""))
        return payload

    @app.get("/", include_in_schema=False)
    def home() -> FileResponse:
        """主頁。頁面本身不含資料，資料仍由 /api/* 取得，故不需鑑權。"""
        return FileResponse(HOME_FILE)

    @app.get("/api/accounts")
    def accounts() -> dict:
        """所有戶口的資料清單：轉發閘道 /accounts（一律四家，只列真實且已啟用的戶口）。"""
        return forward("/accounts")

    @app.get("/api/capabilities")
    def capabilities() -> dict:
        """券商清單與能力聲明：轉發閘道 /capabilities，供頁面填充券商選項，不在 Web UI 內硬寫券商名單。"""
        return forward("/capabilities")

    @app.get("/api/symbols")
    def symbols(kind: str = "stock", market: str | None = None,
                broker: str = DEFAULT_BROKER) -> dict:
        """標的列表：按類型轉發對應的清單接口。

        市場與券商只負責轉傳：某家券商不提供該品種（type_unsupported）或根本未啟用（unknown_source）
        由 core 明確報錯，Web UI 不會靜靜改用別家湊數。
        """
        path = SYMBOL_PATHS.get(kind)
        if path is None:
            return {"status": False, "data": {"columns": [], "rows": []},
                    "message": f"unknown_kind: {kind}；可用 {', '.join(SYMBOL_PATHS)}"}
        params = {"broker": broker}
        if market:
            params["markets"] = market
        return forward(path, params)

    @app.get("/api/codes")
    def codes(broker: str = DEFAULT_BROKER) -> dict:
        """離線讀回某券商存放的 CODES：轉發閘道 /codes。各券商各一檔，讀取不打券商，故不需要連線。"""
        return forward("/codes", {"broker": broker})

    @app.get("/api/codes/meta")
    def codes_meta(broker: str = DEFAULT_BROKER) -> dict:
        """某券商離線 CODES 快照的元資料（行數、存放時間、距今秒數、是否過舊）：轉發閘道 /codes/meta，
        離線執行，不需要任何券商連線。"""
        return forward("/codes/meta", {"broker": broker})

    @app.get("/api/codes/refresh")
    def codes_refresh(broker: str = DEFAULT_BROKER) -> dict:
        """向某券商重拉全量 CODES 並覆蓋該券商的離線快照：轉發閘道 /codes/refresh。不带市場參數——
        快照本身就是全量，只拉部分市場會被閘道的縮細防護拒絕。"""
        return forward("/codes/refresh", {"broker": broker})

    @app.get("/api/kline")
    def kline(code: str, ktype: str | None = None, count: int | None = None,
              broker: str = DEFAULT_BROKER, autype: str | None = None) -> dict:
        """K 線：轉發閘道 /kline。週期與根數省略時一律交閘道用其預設，本層不自訂第二套預設；
        代碼不支持該週期（ktype_unsupported）或被停用（broker_disabled）由 core 明確報錯。"""
        params = {"code": code, "broker": broker}
        for name, value in (("ktype", ktype), ("count", count), ("autype", autype)):
            if value is not None:
                params[name] = value
        return forward("/kline", params)

    @app.get("/api/brokers/prefs")
    def brokers_prefs() -> dict:
        """券商開關狀態：轉發閘道 /brokers/prefs（只讀，不取任何券商資料）。開關是全域喜好，故只此
        一處寫檔，三個界面讀到的是同一份。"""
        return forward("/brokers/prefs")

    @app.get("/api/brokers/prefs/update")
    def brokers_prefs_update(enabled: str | None = None) -> dict:
        """設定生效的券商：轉發閘道 /brokers/prefs/update。enabled 原樣透傳（逗號分隔的完整名單，
        不可在本層大寫化或裁剪，否則會變成不存在的名字）；省略即全部停用，與界面取消全部開關一致。"""
        return forward("/brokers/prefs/update", {} if enabled is None else {"enabled": enabled})

    @app.get("/static/{name}", include_in_schema=False)
    def static_asset(name: str) -> FileResponse:
        """圖表規格（chart.js 與 echarts.min.js）：與閘道同一份，由 brokery.chart.static_file() 定位，
        嚴禁在 Web UI 另存一份。頁面本身不需鑑權，載入圖表規格亦不需。"""
        try:
            path = chart.static_file(name)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"static_missing: {name}")
        return FileResponse(path)

    @app.websocket("/ws/stream")
    async def stream_proxy(ws: WebSocket) -> None:
        """K 線串流的代理：瀏覽器 ↔ 本應用 ↔ 閘道，雙向原樣透傳，不改事件內容。

        之所以要代理而不是讓頁面直連閘道：金鑰只在服務端，放進頁面即等於公開。協定（subscribe/
        update/stop…）與每券商名額一律由閘道判定，本層只負責接兩條線，任何協定變更都不需要改這裡。
        """
        await ws.accept()
        try:
            upstream = await websockets.connect(ws_url, max_size=WS_MAX_SIZE)
        except Exception as exc:  # 閘道未啟動或端口錯誤：以與 /api/* 同一口徑說明原因，不讓頁面空白等待
            message = f"gateway_unreachable: {ws_url.split('?')[0]}（{type(exc).__name__}: {exc}）"
            logger.warning("%s", message)
            await ws.send_json({"event": "error", "message": message})
            await ws.close()
            return

        async def to_client() -> None:
            async for raw in upstream:
                await ws.send_text(raw)

        async def to_upstream() -> None:
            while True:
                await upstream.send(await ws.receive_text())

        try:
            tasks = [asyncio.create_task(to_client()), asyncio.create_task(to_upstream())]
            _, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()
            # 兩端都要取回：只取第一個異常的話，另一個會變成「Task exception was never retrieved」
            # 混進日誌，與真正的故障分不清。頁面或上游斷開屬正常結束，不算錯誤。
            errors = [exc for exc in await asyncio.gather(*tasks, return_exceptions=True)
                      if isinstance(exc, Exception)]
            if errors:
                raise errors[0]  # 異常要留低痕跡，否則查不到斷開的原因
        except Exception as exc:
            logger.info("串流代理結束：%s", type(exc).__name__)
        finally:
            await upstream.close()
            if ws.client_state.name != "DISCONNECTED":
                await ws.close()

    return app
