"""Tiger 適配器：以 get_bars 取 K 線，以 subscribe_kline 推送最新分鐘 bar，並提供標的清單。

Tiger 的 get_bars 以 limit 指定 bar 數，與富途的 count 語義相同，故不需要像 IB 那樣由 bar 數
反推時間跨度。返回的 time 為毫秒時間戳（本身即絕對時刻，不按市場時區解釋），amount 為成交額，
故 turnover 有值（IB 無此欄）。

標的清單三家接口各自不同：股票與指數同出自 get_symbol_names（Tiger 把指數以句點前綴混在同一張
符號表中，實測 US 只有 .SPX/.IXIC/.DJI/.XSP 四隻，HK 沒有），期貨則由 get_future_exchanges 與
get_future_contracts 原生展開全部到期月，不需要種子表。
"""
from __future__ import annotations

import math
from collections.abc import Iterable
from datetime import datetime, timezone

from tigeropen.common.consts import BarPeriod, QuoteRight
from tigeropen.push.push_client import PushClient
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.trade.trade_client import TradeClient

from ..codes import (
    FUTURE,
    INDEX,
    MAIN_SUFFIX,
    STOCK,
    CodeError,
    build_code,
    currency_of,
    market_of,
    parse_code,
    split_future_symbol,
    to_display_symbol,
)
from ..config import get_settings
from .base import (
    ACC_CASH,
    ACC_MARGIN,
    ANCHOR_START,
    CAP_FUTURE,
    CAP_INDEX,
    CAP_STOCK,
    BarMerger,
    NativeBars,
    SymbolBroker,
    account_row,
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

# 統一市場前綴 → Tiger 的 Market。Tiger 只有 US/HK/CN/SG 四個市場，其中 CN 同時含上交所與深交所
# 而 Tiger 不區分，統一格式以 SH/SZ 分列，故不支持 CN（不憑空猜交易所）。
TIGER_MARKET = {"US": "US", "HK": "HK", "SG": "SG"}

# get_managed_accounts 的 account_type：STANDARD 為真實戶口、PAPER 為模擬戶口。統一格式不再區分環
# 境，故只取 STANDARD。capability 另為獨立欄位，含 margin 者（RegTMargin/PortfolioMargin 等）為保
# 證金戶口，其餘（BasicCash/InstCash）為現金戶口。
REAL_ACCOUNT_TYPE = "STANDARD"


def _summary_funds(summary) -> dict:
    """Tiger 的 Account 摘要 → 統一金額欄位（無值由 account_row 把 inf 還原為 NaN）。"""
    return {
        "net_liquidation": getattr(summary, "net_liquidation", None),
        "cash": getattr(summary, "cash", None),
        "market_value": getattr(summary, "gross_position_value", None),
        "available_funds": getattr(summary, "available_funds", None),
        "buying_power": getattr(summary, "buying_power", None),
        "init_margin": getattr(summary, "initial_margin_requirement", None),
        "maint_margin": getattr(summary, "maintenance_margin_requirement", None),
        "equity_with_loan": getattr(summary, "equity_with_loan", None),
        "unrealized_pnl": getattr(summary, "unrealized_pnl", None),
        "realized_pnl": getattr(summary, "realized_pnl", None),
    }


class TigerBroker(SymbolBroker):
    """Tiger OpenAPI 的標的來源（股票、期貨、指數）與 K 線。"""

    source = "tiger"
    # 股票與期貨為原生全量；指數只有 Tiger 符號表登記的四隻美股指數（無獨立接口），故照樣聲明，
    # 由返回的行數自行表明其範圍。
    capabilities = frozenset({CAP_STOCK, CAP_FUTURE, CAP_INDEX})
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
    # 實測 get_managed_accounts 的 capability 表明現金或保證金（BasicCash/RegTMargin），兩種皆聲明。
    acc_types = (ACC_CASH, ACC_MARGIN)

    def __init__(self):
        self._config: TigerOpenClientConfig | None = None
        self._quote: QuoteClient | None = None
        self._push: PushClient | None = None
        self._trade: TradeClient | None = None

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

    def _trade_client(self) -> TradeClient:
        if self._trade is None:
            self._trade = TradeClient(self._client_config())
        return self._trade

    # ---------- 標的清單 ----------

    def list_stocks(self, markets: Iterable[str], *, raw: bool = False) -> list[dict]:
        """股票清單：get_symbol_names 一次返回該市場的全部符號與名稱（實測 HK 3763／US 14609）。

        清單接口不附帶交易所與貨幣（get_stock_details 需行情權限，實測本戶口被拒），故 exchange
        留空；currency 由統一市場前綴推得，與富途適配器同一處理。以句點開頭者為指數，交由
        list_indices 返回，不在此列作股票。
        raw=True 時每列只有 get_symbol_names 的原生內容：symbol 與 name 即其返回的兩欄，market 為該次
        請求的市場參數（Tiger 的寫法，非統一市場代碼）；不做代碼構造與市場推導，取數範圍不變。
        """
        quote = self._quote_client()
        rows: list[dict] = []
        for market in markets:
            tiger_market = TIGER_MARKET.get(str(market).upper())
            if tiger_market is None:
                raise ValueError(
                    f"market_unsupported: Tiger 不提供 {market} 的股票清單"
                    f"（可用：{'/'.join(sorted(TIGER_MARKET))}）"
                )
            for symbol, name in quote.get_symbol_names(market=tiger_market):
                symbol = str(symbol)
                if symbol.startswith("."):
                    continue
                if raw:
                    rows.append({"market": str(tiger_market), "symbol": symbol, "name": str(name)})
                    continue
                rows.append(self.make_row(
                    code=build_code(market, symbol),
                    name=str(name),
                    market=market,
                    symbol=to_display_symbol(market, symbol),
                    symbol_type=STOCK,
                    currency=currency_of(market),
                    exchange="",
                ))
        return rows

    def list_indices(self, seeds: Iterable, *, raw: bool = False) -> list[dict]:
        """指數清單：取 Tiger 符號表中以句點前綴登記的指數（實測僅 US 四隻）。

        Tiger 沒有獨立的指數列舉接口，其指數只作為符號表的一小部分出現，故這裡返回的就是 Tiger
        自身登記的全部指數，範圍遠小於富途；seeds 只用於限定市場，不據此補出 Tiger 沒有的指數。
        raw=True 時的欄位同 list_stocks。
        """
        markets = {str(seed.market).upper() for seed in seeds}
        quote = self._quote_client()
        rows: list[dict] = []
        for market, tiger_market in TIGER_MARKET.items():
            if market not in markets:
                continue
            for symbol, name in quote.get_symbol_names(market=tiger_market):
                symbol = str(symbol)
                if not symbol.startswith("."):
                    continue
                if raw:
                    rows.append({"market": str(tiger_market), "symbol": symbol, "name": str(name)})
                    continue
                rows.append(self.make_row(
                    code=build_code(market, symbol),
                    name=str(name),
                    market=market,
                    symbol=symbol,
                    symbol_type=INDEX,
                    currency=currency_of(market),
                    exchange="",
                ))
        return rows

    def list_futures(self, seeds: Iterable, *, raw: bool = False) -> list[dict]:
        """期貨清單：get_future_exchanges 列出接入的交易所，逐個以 get_future_contracts 取全部
        合約（實測 CME 240／HKEX 84，已含全部到期月與主連），故不需要種子表；seeds 只作市場限定。

        主連以 contract_month 為空識別（continuous 欄不可靠，實測 CME 的 ESmain 回報 False），統一
        寫成 root+main；個月份寫成 root+contract_month（如 ES202512），因統一格式不設到期月欄，
        合約必須由代碼唯一標識。trade=False 的合約不可
        交易，不列入。Tiger 接入但無統一市場前綴的交易所（如 EUREX）一律跳過，不憑空造出市場。
        raw=True 時每列為 get_future_contracts 返回的原生欄位（contract_code/exchange/currency/type/
        contract_month/name 等），不做市場推導與符號構造；取數範圍不變（仍只取可交易且市場在 seeds 內
        的合約，市場判定仍按 exchange 與 currency 計算）。
        """
        wanted = {str(seed.market).upper() for seed in seeds}
        rows: list[dict] = []
        for venue in self._quote_client().get_future_exchanges().itertuples():
            frame = self._quote_client().get_future_contracts(exchange=venue.code)
            for item in frame.itertuples():
                if not item.trade:
                    continue
                currency = _text(item.currency)
                exchange = _text(item.exchange) or str(venue.code)
                try:
                    market = market_of(exchange, currency)
                except CodeError:
                    continue
                if market not in wanted:
                    continue
                if raw:
                    rows.append(dict(zip(frame.columns, item)))
                    continue
                contract = _text(item.contract_code)
                root = (_text(item.type) or split_future_symbol(contract)[0]).upper()
                expiry = _text(item.contract_month)
                symbol = f"{root}{expiry}" if expiry else f"{root}{MAIN_SUFFIX}"
                rows.append(self.make_row(
                    code=build_code(market, symbol),
                    name=_text(item.name),
                    market=market,
                    symbol=to_display_symbol(market, symbol),
                    symbol_type=FUTURE,
                    currency=currency,
                    exchange=exchange,
                ))
        return rows

    # ---------- K 線 ----------

    def get_kline(self, code: str, ktype: str, count: int, autype: str, *, raw: bool = False) -> list[dict]:
        """按 bar 數取 K 線，返回按 ts 升序的最近 count 根。

        get_bars 的 limit 即 bar 數（不給時間範圍時返回最近的 bar），與富途語義一致；超過單次
        上限時改用 SDK 的 get_bars_by_page（向後分頁後已按 time 升序合併）。
        raw=True 時列為 get_bars/get_bars_by_page 返回的原生欄位（time 為毫秒 epoch），排序與截尾改按
        原生 time（同一格式，升序即時間升序），取數範圍不變。
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
        if raw:
            rows = frame.to_dict("records")
            rows.sort(key=lambda row: row.get("time") or 0)
            return rows[-count:]
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
        *,
        raw: bool = False,
    ) -> dict[str, list[dict]]:
        """串流多個代碼的最新 1 分鐘 K 線，全部共用同一條推送長連接。

        先以 get_bars 取最近 count 根作起點，之後訂閱 subscribe_kline：Tiger 每次成交即推送當前
        分鐘的 bar（未走完的 bar 反覆推送），有變化才呼叫 on_update(code, rows)。回調在 SDK 的
        推送執行緒中發生。訂閱必須在連上時才建立：斷線自動重連後訂閱不會恢復。
        raw=True 時起點與推送一律為原生欄位（time 為毫秒 epoch），按原生 time 合併（見 NativeBars）。
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
            merger = NativeBars(count, "time") if raw else BarMerger(count)
            merger.merge(self.get_kline(code, ktype, min(count, PAGE_MAX), autype, raw=raw))
            mergers[code] = merger

        config = self._client_config()
        protocol, host, port = config.socket_host_port
        push = PushClient(host, port, use_ssl=(protocol == "ssl"), client_config=config)
        push.kline_changed = self._push_handler(owners, markets, ktype, mergers, on_update, raw=raw)
        push.connect_callback = lambda *_: push.subscribe_kline(list(owners))
        self._push = push
        try:
            push.connect(config.tiger_id, config.private_key)
            stream_wait(seconds)
        finally:
            self.close()
        return {code: mergers[code].frame() for code in codes}

    # ---------- 戶口 ----------

    def get_accounts(self, currency: str | None = None, *, raw: bool = False) -> list[dict]:
        """戶口清單與資金：get_managed_accounts 定戶口性質，get_assets 取資金。

        只取 account_type=STANDARD 的真實戶口（PAPER 為模擬戶口，統一格式不再區分環境，紙面資金
        不應混入）。capability（RegTMargin、BasicCash 等）獨立表明現金或保證金，映射為 acc_type。
        get_assets 只按帳戶返回其結算幣的數字，沒有按幣種的參數（實測傳 base_currency 被拒），故
        currency 只作篩選：與該戶口結算幣不符即不返回該戶口，一律不做匯率換算。Tiger 以 inf 表示
        該幣種無此項（實測空戶口的保證金要求為 inf），一律還原為 NaN。
        raw=True 時每列為該戶口的原生記錄：get_managed_accounts 的 AccountProfile 各欄加上 get_assets
        的 summary（Account）各欄，不做映射或改名；inf 即原生的 inf，不還原為 NaN。取數範圍不變
        （仍只取 STANDARD 戶口，currency 仍按該戶口結算幣篩選）。
        """
        trade = self._trade_client()
        rows: list[dict] = []
        for profile in trade.get_managed_accounts():
            if str(profile.account_type) != REAL_ACCOUNT_TYPE:
                continue
            account = str(profile.account)
            assets = trade.get_assets(account=account, market_value=True)
            if not assets:
                continue
            summary = assets[0].summary
            currency_of_account = str(getattr(summary, "currency", "") or "")
            if currency and currency_of_account and currency.upper() != currency_of_account.upper():
                continue
            if raw:
                rows.append({**vars(profile), **vars(summary)})
                continue
            capability = str(profile.capability)
            rows.append(account_row(
                source=self.source,
                account_id=account,
                acc_type=ACC_MARGIN if "margin" in capability.lower() else ACC_CASH,
                status=str(profile.status),
                currency=currency_of_account,
                funds=_summary_funds(summary),
            ))
        return rows

    # ---------- 內部 ----------

    def _push_handler(self, owners, markets, ktype, mergers, on_update, raw: bool = False):
        """構造推送回調：把 Tiger 的分鐘 bar 換算為統一列並併入各代碼的合併器。"""

        def _on_kline(frame) -> None:
            code = owners.get(frame.symbol)
            merger = mergers.get(code)
            if merger is None:
                return
            if raw:
                # KlineData 為 protobuf 訊息，按其字段原樣取值，不做任何換算或改名。
                row = {field.name: getattr(frame, field.name) for field in frame.DESCRIPTOR.fields}
            else:
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


def _text(value) -> str:
    """把 DataFrame 空值（None/NaN）還原為空字串：統一清單欄位以空字串表示缺失。"""
    try:
        if value is None or math.isnan(value):
            return ""
    except TypeError:
        pass
    return str(value)


def _bare_key(value: str) -> str:
    """去掉 PEM 標記與換行：SDK 的金鑰載入只接受 Base64 主體。"""
    return "".join(line.strip() for line in value.splitlines() if "-----" not in line)
