"""閘道客戶端：桌面 GUI 只經 brokery_api 的 HTTP 接口取數，不直接連券商。

不連券商的理由與 Web UI 相同：閘道進程已持有各券商連線（IB 只容許一個 client id），桌面端再建一份即
互相搶佔，兩邊都取不到數。返回一律為 {"status", "data", "message"} 信封，業務失敗亦原樣透傳；取不到時
由本模組構造 status=False，界面只需看一個欄位。
"""
from __future__ import annotations

from urllib.parse import urlencode

import httpx

from brokery.config import get_settings

# 超時必須高於閘道內部最慢的兜底（IB 連線 40s），否則界面會先斷，用戶見到的是界面超時而不是券商給出的原因。
UPSTREAM_TIMEOUT = 60.0


class GatewayClient:
    """一個閘道的只讀客戶端：GET 一個接口並返回信封。"""

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        settings = get_settings()
        self.base_url = (base_url or f"http://{settings.api_host}:{settings.api_port}").rstrip("/")
        self.api_key = settings.api_key if api_key is None else api_key
        if not self.api_key:
            raise RuntimeError(
                "API_KEY 未設定：桌面 GUI 經閘道讀取資料，請在 .env 設 API_KEY=<自訂金鑰> 後重新啟動"
            )

    def get(self, path: str, params: dict | None = None) -> dict:
        """請求一個閘道接口：信封原樣返回，不可達或非信封內容即構造 status=False。"""
        query = f"?{urlencode(params)}" if params else ""
        url = f"{self.base_url}{path}{query}"
        try:
            resp = httpx.get(url, headers={"X-API-Key": self.api_key}, timeout=UPSTREAM_TIMEOUT)
            payload = resp.json()
        except Exception as exc:  # 閘道未啟動、端口錯誤、回應不是 JSON，一律點名原因
            return {"status": False, "data": {"columns": [], "rows": []},
                    "message": f"gateway_unreachable: {url}（{type(exc).__name__}: {exc}）"}
        if resp.status_code != 200 or not isinstance(payload, dict) or "status" not in payload:
            detail = payload.get("detail") if isinstance(payload, dict) else payload
            return {"status": False, "data": {"columns": [], "rows": []},
                    "message": f"gateway_http_{resp.status_code}: {detail}"}
        return payload
