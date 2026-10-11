"""Tiger 適配器：以 get_bars 取 K 線，以 subscribe_kline 推送最新分鐘 bar。

Tiger 的 get_bars 以 limit 指定 bar 數，與富途的 count 語義相同，故不需要像 IB 那樣由 bar 數
反推時間跨度。返回的 time 為毫秒時間戳（本身即絕對時刻，不按市場時區解釋），amount 為成交額，
故 turnover 有值（IB 無此欄）。

只做 K 線：本專案的標的清單以富途為準，故不聲明清單能力（capabilities 為空），由 core 依
capabilities 跳過。期貨與指數亦未實作（Tiger 需另用期貨接口與合約映射），此類代碼會由接口明確
報錯。
"""
from __future__ import annotations

from datetime import datetime, timezone

from tigeropen.common.consts import BarPeriod, QuoteRight
from tigeropen.push.push_client import PushClient
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.tiger_open_config import TigerOpenClientConfig

from ..codes import INDEX, STOCK, CodeError, parse_code, to_display_symbol
from ..config import get_settings
from .base import (
    ANCHOR_START,
    BarMerger,
    SymbolBroker,
    align_ts,
    kline_row,
    stream_wait,
    to_local_text,
)

# 統一 ktype → Tiger 的 period。Tiger 的 BarPeriod 雖有 3min，但 get_bars 文件所列的可用值沒有
# 3min（與富途、IB 不同），未實測前不聲明，避免把不支持的週期變成請求期錯誤。
TIGER_PERIOD = {
    "1m": BarPeriod.ONE_MINUTE,
    "5m": BarPeriod.FIVE_MINUTES,
    "15m": BarPeriod.FIFTEEN_MINUTES,
    "30m": BarPeriod.HALF_HOUR,
    "60m": BarPeriod.ONE_HOUR,
    "day": BarPeriod.DAY,
    "week": BarPeriod.WEEK,
    "month": BarPeriod.MONTH,
}

# 複權模式 → QuoteRight。Tiger 只有前復權（BR）與不復權（NR），無後復權對應值，故 hfq 不支持。
TIGER_RIGHT = {"qfq": QuoteRight.BR, "none": QuoteRight.NR}

PAGE_MAX = 1000  # 單次請求的保守 bar 數，超過即改用 SDK 的分頁接口


class TigerBroker(SymbolBroker):
    """Tiger OpenAPI 的 K 線來源（股票）。"""

    source = "tiger"
    # Tiger 的 time 為 bar 起點的毫秒時間戳（示例中日線為開市時刻），故以起點為錨點；週/月線經
    # align_ts 歸到所屬週期起點，與富途一致。
    kline_anchor = ANCHOR_START
    autypes = tuple(TIGER_RIGHT)
    # 推送只有「當前分鐘」的 bar（KlineData 為分鐘 bar），其他週期無對應推送，故只聲明 1m。
    # 推送不帶復權參數，即原始成交價，故串流只支持 none（起點亦以同一模式取，避免混價）。
    stream_ktypes = ("1m",)
    stream_autypes = ("none",)
    # 實測美股指數（US..SPX）可用，故聲明 INDEX；港股指數與期貨（含主連）一律返回空 bar，
    # 即未接入對應接口。
    kline_symbol_types = (STOCK, INDEX)

    def __init__(self):
        self._config: TigerOpenClientConfig | None = None
        self._quote: QuoteClient | None = None
        self._push: PushClient | None = None

    # ---------- 鑑權 ----------

    def close(self) -> None:
        """斷開推送長連接。同一 tiger_id 只允許一條推送連接，殘留的連接會把後續連接踢掉。"""
        if self._push is not None:
            self._push.disconnect()
            self._push = None

    def _client_config(self) -> TigerOpenClientConfig:
        """構造 SDK 配置（HTTP 查詢與推送長連接共用同一份）。"""
        if self._config is None:
            settings = get_settings()
            if not settings.tiger_id or not settings.tiger_private_key:
                raise CodeError(
                    "not_configured: 缺少 TIGER_ID / TIGER_PRIVATE_KEY"
                    "（Tiger 的簽名鑑權必須有與 TIGER_PUBLIC_KEY 配對的 RSA 私鑰）"
                )
            config = TigerOpenClientConfig()
            config.tiger_id = settings.tiger_id
            config.account = settings.tiger_account
            config.private_key = _bare_key(settings.tiger_private_key)
            # 不設 config.tiger_public_key：該字段是「老虎自己的公鑰」，用於驗證返回的簽名，SDK 已自帶
            # 生產環境的預設值。`.env` 的 TIGER_PUBLIC_KEY 是本帳戶在開發者平台登記的公鑰（與私鑰配對，
            # 只作核對用途），餵進去會令驗簽失敗（ResponseException: response sign verify failed）。
            if settings.tiger_token:
                config.token = settings.tiger_token
            self._config = config
        return self._config

    def _quote_client(self) -> QuoteClient:
        if self._quote is None:
            self._quote = QuoteClient(self._client_config())
        return self._quote

    # ---------- K 線 ----------

    def get_kline(self, code: str, ktype: str, count: int, autype: str) -> list[dict]:
        """按 bar 數取 K 線，返回按 ts 升序的最近 count 根。

        get_bars 的 limit 即 bar 數（不給時間範圍時返回最近的 bar），與富途語義一致；超過單次
        上限時改用 SDK 的 get_bars_by_page（向後分頁後已按 time 升序合併）。
        """
        if ktype not in TIGER_PERIOD:
            raise CodeError(f"ktype_unsupported: {ktype}（可用：{'/'.join(TIGER_PERIOD)}）")
        if autype not in TIGER_RIGHT:
            raise CodeError(f"autype_unsupported: {autype}（可用：{'/'.join(TIGER_RIGHT)}）")
        parsed = parse_code(code)
        symbol = _native_symbol(parsed.market, parsed.symbol)
        if count <= PAGE_MAX:
            frame = self._quote_client().get_bars(
                symbols=[symbol],
                period=TIGER_PERIOD[ktype],
                right=TIGER_RIGHT[autype],
                limit=count,
            )
        else:
            frame = self._quote_client().get_bars_by_page(
                symbol=symbol,
                period=TIGER_PERIOD[ktype],
                right=TIGER_RIGHT[autype],
                total=count,
                page_size=PAGE_MAX,
            )
        rows = [
            self._to_kline_row(
                code, parsed.market, ktype, item.time, item.open, item.high, item.low,
                item.close, item.volume, getattr(item, "amount", float("nan")),
            )
            for item in frame.itertuples()
        ]
        rows.sort(key=lambda row: row["ts"])
        return rows[-count:]

    def stream_kline(
        self,
        codes: tuple[str, ...],
        ktype: str,
        count: int,
        autype: str,
        seconds: float,
        on_update,
    ) -> dict[str, list[dict]]:
        """串流多個代碼的最新 1 分鐘 K 線，全部共用同一條推送長連接。

        先以 get_bars 取最近 count 根作起點，之後訂閱 subscribe_kline：Tiger 每次成交即推送當前
        分鐘的 bar（未走完的 bar 反覆推送），有變化才呼叫 on_update(code, rows)。回調在 SDK 的
        推送執行緒中發生。訂閱必須在連上時才建立：斷線自動重連後訂閱不會恢復。
        """
        if ktype not in self.stream_ktypes:
            raise CodeError(
                f"ktype_unsupported: {ktype}（tiger 的 K 線串流只支持 {'/'.join(self.stream_ktypes)}）"
            )
        if autype not in self.stream_autypes:
            raise CodeError(
                'autype_unsupported: tiger 的 K 線串流只支持 autype="none"'
                "（推送為當前分鐘的原始成交價，無復權參數）"
            )
        markets = {code: parse_code(code).market for code in codes}
        # 推送只帶券商原生符號，故需由原生符號還原統一代碼。
        owners = {_native_symbol(market, parse_code(code).symbol): code for code, market in markets.items()}
        mergers: dict[str, BarMerger] = {}
        for code in codes:
            merger = BarMerger(count)
            merger.merge(self.get_kline(code, ktype, min(count, PAGE_MAX), autype))
            mergers[code] = merger

        config = self._client_config()
        protocol, host, port = config.socket_host_port
        push = PushClient(host, port, use_ssl=(protocol == "ssl"), client_config=config)
        push.kline_changed = self._push_handler(owners, markets, ktype, mergers, on_update)
        push.connect_callback = lambda *_: push.subscribe_kline(list(owners))
        self._push = push
        try:
            push.connect(config.tiger_id, config.private_key)
            stream_wait(seconds)
        finally:
            self.close()
        return {code: mergers[code].frame() for code in codes}

    # ---------- 內部 ----------

    def _push_handler(self, owners, markets, ktype, mergers, on_update):
        """構造推送回調：把 Tiger 的分鐘 bar 換算為統一列並併入各代碼的 BarMerger。"""

        def _on_kline(frame) -> None:
            code = owners.get(frame.symbol)
            merger = mergers.get(code)
            if merger is None:
                return
            row = self._to_kline_row(
                code, markets[code], ktype, frame.time, frame.open, frame.high, frame.low,
                frame.close, frame.volume, getattr(frame, "amount", float("nan")),
            )
            if merger.merge([row]) and on_update is not None:
                on_update(code, merger.frame())

        return _on_kline

    def _to_kline_row(
        self, code, market, ktype, time_ms, open_, high, low, close, volume, amount
    ) -> dict:
        """由原生數值構造統一列（歷史的 DataFrame 行與推送的 protobuf 行共用）。"""
        ts = int(time_ms) // 1000  # 毫秒時間戳本身即絕對時刻，無需按市場時區解釋
        return kline_row(
            code=code,
            ts=align_ts(ts, market, ktype, self.kline_anchor),
            time_key=to_local_text(datetime.fromtimestamp(ts, timezone.utc), market),
            open_=open_,
            high=high,
            low=low,
            close=close,
            volume=volume,
            turnover=amount,
            source=self.source,
        )


def _native_symbol(market: str, symbol: str) -> str:
    """轉為 Tiger 原生符號。Tiger 的港股以五位補零登記（700 → 00700），與統一顯示格式相同。"""
    return to_display_symbol(market, symbol)


def _bare_key(value: str) -> str:
    """去掉 PEM 標記與換行：SDK 的金鑰載入只接受 Base64 主體。"""
    return "".join(line.strip() for line in value.splitlines() if "-----" not in line)
