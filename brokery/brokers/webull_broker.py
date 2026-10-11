"""Webull 適配器：以 get_batch_history_bar 取 K 線，以輪詢同一接口串流最新分鐘 bar，並提供標的清單。

Webull 的 count 即 bar 數，與富途語義相同，不需要像 IB 那樣由 bar 數反推時間跨度。返回只有 OHLCV，
不含成交額，故 turnover 一律為 NaN（與 IB 相同）。

復權不可選擇：接口沒有復權參數，價格只按週期固定（日線及以上為前復權、分鐘線為不復權）。因此本適配器
按週期聲明實際會返回的那一種，要求另一種時明確報錯，而不是靜靜返回另一種價格。

標的清單：股票由 instruments/stocks/profiles/list 分頁取全（實測 HK 3170／US 11680），期貨由
instruments/futures/contracts/list 逐個產品展開到期月。指數不聲明：Webull 的 category 詞表沒有
指數（實測只有 US_STOCK/HK_STOCK/CN_STOCK/US_ETF/HK_ETF/US_OPTION/US_FUTURES/HK_FUTURES/US_CRYPTO/
US_EVENT），由 core 依 capabilities 跳過。
"""
from __future__ import annotations

import time
from collections.abc import Iterable
from datetime import datetime, timezone

from webull.core.client import ApiClient
from webull.core.exception.exceptions import ClientException, ServerException
from webull.data.data_client import DataClient
from webull.trade.trade_client import TradeClient

from ..codes import FUTURE, STOCK, CodeError, build_code, parse_code, to_display_symbol
from ..config import get_settings
from .base import (
    ACC_CASH,
    ACC_MARGIN,
    ANCHOR_START,
    CAP_FUTURE,
    CAP_STOCK,
    BarMerger,
    NativeBars,
    SymbolBroker,
    account_row,
    align_ts,
    kline_row,
    to_local_text,
    to_utc,
)

# 統一 ktype → Webull 的 timespan。Webull 沒有 3 分鐘週期（Timespan 無 M3），與富途、IB 不同，
# 故 3m 不聲明，由 core 統一作為不支持的週期拒绝。傳字符串而非枚舉：SDK 以 json.dumps 序列化，
# 傳枚舉對象會抛 TypeError。
WEBULL_TIMESPAN = {
    "1m": "M1",
    "5m": "M5",
    "15m": "M15",
    "30m": "M30",
    "60m": "M60",
    "day": "D",
    "week": "W",
    "month": "M",
}

# 統一市場 → Webull 的 category（股票）。其餘市場無對應 category，明確報錯。
WEBULL_CATEGORY = {"HK": "HK_STOCK", "US": "US_STOCK"}

# 股票清單只取的 sub_category。Webull 把認股證、牛熊證等與普通股混在同一 category，故按
# sub_category 過濾；各市場可用的值由接口錯誤訊息取得（實測 HK: [COMMON_STOCK, ETF]、US:
# [COMMON_STOCK, ETF, PREFERRED_STOCK, WARRANT, UNITS, RIGHT]）。此處只取普通股、ETF 與優先股，
# 與富途 list_stocks 的 STOCK/ETF 範圍一致（認股證等在富途屬另外的類型，不在股票清單內）。
WEBULL_STOCK_SUBCATEGORY = {
    "HK": ("COMMON_STOCK", "ETF"),
    "US": ("COMMON_STOCK", "ETF", "PREFERRED_STOCK"),
}

# 統一市場 → Webull 的期貨 category。期貨沒有批量清單接口，只能逐個產品 root 展開（見 list_futures）。
WEBULL_FUTURE_CATEGORY = {"HK": "HK_FUTURES", "US": "US_FUTURES"}

# Webull 的期貨交易所代號 → 統一詞表（見 codes.EXCHANGE_MARKET）。Webull 以 OMS 代號登記（實測
# XCME 即 CME Globex、XCBT 即 CBOT、XCEC 即 COMEX、HFE 即港交所期交所），與富途、Tiger 對同一
# 交易所的寫法不同，故先歸一才寫入 exchange，使同一合約在各券商可對照。未登記的交易所原樣返回。
WEBULL_FUTURE_EXCHANGE = {
    "HFE": "HKFE",
    "XCME": "CME",
    "XCBT": "CBOT",
    "XNYM": "NYMEX",
    "XCEC": "COMEX",
}

# 各週期實際返回的複權模式（日線及以上為前復權、分鐘線為不復權，見 get_batch_history_bar 文件）。
WEBULL_AUTYPE = {
    "1m": "none", "5m": "none", "15m": "none", "30m": "none", "60m": "none",
    "day": "qfq", "week": "qfq", "month": "qfq",
}

BAR_MAX = 1200  # 單次請求的 bar 數上限（接口限制，超過即按此取，返回根數相應較少）
POLL_SECONDS = 2.0  # 串流的輪詢間隔：港股行情限制為 60 次/60 秒，2 秒（30 次/分鐘）留有餘地
REQUEST_TIMEOUT = (10, 30)  # 連線/讀取超時（秒），防止請求無限掛起
TOKEN_CHECK_SECONDS = 30  # token 未獲批准時的等待上限：SDK 預設 300 秒，過長會令呼叫長時間阻塞
TOKEN_CHECK_INTERVAL = 5

# 標的清單為多次請求（分頁或逐個產品），Webull 的元數據接口限速約 1 次/秒（實測不等待時約 75 頁
# 後開始 429），故每次請求之間固定等待，並對 429 重試；重試仍失敗才向上報錯。
LIST_REQUEST_INTERVAL = 1.2
LIST_RETRY = 2
LIST_RETRY_WAIT = 5.0


def _payload(response, what: str):
    """Webull 的接口返回 requests.Response：非 200 即抛出，不把錯誤內容當資料返回。"""
    if response.status_code != 200:
        raise RuntimeError(f"{what}: HTTP {response.status_code} {response.text[:200]}")
    return response.json()


def _acc_type_of(account_type: str) -> str:
    """Webull 的 account_type → 統一戶口性質。實測返回 MRGN（account_class 亦帶 MRGN 字樣）。"""
    text = account_type.upper()
    if "MRGN" in text or "MARGIN" in text:
        return ACC_MARGIN
    if "CASH" in text:
        return ACC_CASH
    return account_type.lower()


def _balance_funds(balance: dict, block: dict | None) -> dict:
    """Webull 的資金返回 → 統一金額欄位。

    匯總（total_*）只有市值、現金與未實現盈虧；按幣種明細另有購買力與期初保證金。兩處都沒有淨資產
    與可用資金（只有可提現金額，語義不同），故該兩欄一律不填，由 account_row 轉為 NaN。
    """
    if block is None:
        return {
            "cash": balance.get("total_cash_balance"),
            "market_value": balance.get("total_market_value"),
            "init_margin": balance.get("init_margin"),
            "unrealized_pnl": balance.get("total_unrealized_profit_loss"),
        }
    return {
        "cash": block.get("cash_balance"),
        "market_value": block.get("market_value"),
        "buying_power": block.get("buying_power"),
        "init_margin": block.get("init_margin"),
        "unrealized_pnl": block.get("unrealized_profit_loss"),
    }


class WebullBroker(SymbolBroker):
    """Webull OpenAPI 的標的來源（股票、期貨）與 K 線。"""

    source = "webull"
    # 股票為原生全量（按 category + sub_category 分頁）；期貨只有近月合約且需逐個產品展開，仍屬
    # 可取的清單。指數不聲明：Webull 沒有指數 category（見模組 docstring），不憑種子表湊出。
    capabilities = frozenset({CAP_STOCK, CAP_FUTURE})
    # 接口的 time 為 bar 起點（日線為該交易日零時，並帶時區偏移），故以起點為錨點；週/月線經 align_ts
    # 歸到所屬週期起點，與富途一致。
    kline_anchor = ANCHOR_START
    # 兩種價格都可能出現，取決於週期而非參數，故這裡只聲明「可能返回的集合」，逐週期的準確約束由
    # _check_autype 把關。
    autypes = ("qfq", "none")
    # 推送接口只有報價（quote/snapshot/tick），沒有 K 線推送，故串流以輪詢 1 分鐘 bar 實現；分鐘線
    # 只返回不復權價，故串流只支持 none。
    stream_ktypes = ("1m",)
    stream_autypes = ("none",)
    # Webull 的 account_type 表明戶口性質（實測為 MRGN）。其 OpenAPI 只有真實戶口（account_v2 無
    # 模擬戶口，SDK 亦無模擬交易接口），故不需再按環境過濾。
    acc_types = (ACC_CASH, ACC_MARGIN)

    def __init__(self):
        self._api: ApiClient | None = None
        self._data: DataClient | None = None

    # ---------- 鑑權 ----------

    def _api_client(self) -> ApiClient:
        """構造（並複用）API 客戶端。行情與交易客戶端共用同一份鑑權與 token。"""
        if self._api is None:
            settings = get_settings()
            if not settings.webull_app_key or not settings.webull_app_secret:
                raise CodeError("not_configured: 缺少 WEBULL_APP_KEY / WEBULL_APP_SECRET")
            api = ApiClient(
                settings.webull_app_key,
                settings.webull_app_secret,
                settings.webull_region_id,
                connect_timeout=REQUEST_TIMEOUT[0],
                timeout=REQUEST_TIMEOUT[1],
                token_check_duration_seconds=TOKEN_CHECK_SECONDS,
                token_check_interval_seconds=TOKEN_CHECK_INTERVAL,
            )
            api.set_token_dir(str(settings.webull_token_dir))
            self._api = api
        return self._api

    def _data_client(self) -> DataClient:
        """構造（並複用）數據客戶端：行情與標的元數據共用同一份鑑權與 token。未獲批准即在此報錯。"""
        if self._data is None:
            try:
                self._data = DataClient(self._api_client())
            except ClientException as exc:
                settings = get_settings()
                raise CodeError(
                    f"token_unapproved: {exc}；請在 Webull App 中批准本次 API 授權請求後重試"
                    f"（token 已存放於 {settings.webull_token_dir}，批准後可直接沿用）"
                ) from exc
        return self._data

    def _market_data(self):
        return self._data_client().market_data

    def _instrument_api(self):
        return self._data_client().instrument

    def _trade_client(self) -> TradeClient:
        return TradeClient(self._api_client())

    # ---------- 標的清單 ----------

    def list_stocks(self, markets: Iterable[str], *, raw: bool = False) -> list[dict]:
        """股票清單：按 category + sub_category 分頁取全部在市代碼（實測 HK 3170／US 11680）。

        currency 與 exchange 一律為接口原生值：Webull 以自有的場所代號登記（實測港股為 HKG／XGEM，
        美股為 NYSE／NAS／NSQ／NMS／PSE／BAT 等），各券商對同一場所的寫法本來不同，不憑空歸一；
        原生 instrument_id 只在其原生格式（raw=True）中出現，統一格式不重複承載。

        raw=True 時每列即 list_instruments 單條記錄的原生欄位（symbol 為 Webull 原生符號，不含市場
        前綴；無 market/code/symbol_type 等統一欄位），不做符號歸一化與構造；取數範圍不變（同一批
        category/sub_category 與 status="OC" 條件）。
        """
        rows: list[dict] = []
        for market in markets:
            market = str(market).upper()
            category = self._category(market)
            for sub_category in WEBULL_STOCK_SUBCATEGORY[market]:
                for item in self._paged_instruments(
                    category=category, sub_category=sub_category, status="OC"
                ):
                    if raw:
                        rows.append(dict(item))
                        continue
                    symbol = _native_symbol(market, str(item["symbol"]))
                    rows.append(self.make_row(
                        code=build_code(market, symbol),
                        name=str(item.get("name", "")),
                        market=market,
                        symbol=symbol,
                        symbol_type=STOCK,
                        currency=str(item.get("currency", "")),
                        exchange=str(item.get("exchange_code", "")),
                    ))
        return rows

    def list_futures(self, seeds: Iterable, *, raw: bool = False) -> list[dict]:
        """期貨清單：逐個種子 root 展開其在市合約（實測 HSI 13 個月、ES 2 個月）。

        Webull 沒有批量期貨清單接口（contracts/list 不带 code 或 symbol 即 417），而 products/list
        對 HK 返回 89 個、對 US 返回 2552 個產品，逐個展開需上千次請求，故與 IB 一樣以種子 root
        為準（見 universe.FUTURE_ROOTS）。種子中 Webull 未提供者返回空列表，不憑空補出（實測 VIX
        即如此）。Webull 只掛近月合約（實測美股每個 root 只有最近兩個月），亦沒有主連概念，故不
        生成 main 行。currency 原樣返回（實測農產品期貨為 Webull 自有的 USX，非 ISO 代碼）。

        raw=True 時每列即 get_futures_instrument 單條記錄的原生欄位，不做市場推導、場所映射或符號
        構造；取數範圍不變（仍按種子所屬市場的 category 逐個 root 展開，仍只留在市合約）。
        """
        rows: list[dict] = []
        for seed in seeds:
            market = str(seed.market).upper()
            category = WEBULL_FUTURE_CATEGORY.get(market)
            if category is None:
                continue
            time.sleep(LIST_REQUEST_INTERVAL)
            for item in self._futures_instruments(category, seed.root):
                if item.get("status") not in (None, "OC"):
                    continue
                if raw:
                    rows.append(dict(item))
                    continue
                native_exchange = str(item.get("exchange_code", ""))
                # 到期月寫進符號（如 ES202612）：統一格式不設到期月欄，只以 root 表達會令各月份同碼。
                contract_month = str(item.get("contract_month", ""))
                symbol = f"{seed.root}{contract_month}" if contract_month else seed.root
                rows.append(self.make_row(
                    code=build_code(market, symbol),
                    name=str(item.get("name", "")),
                    market=market,
                    symbol=to_display_symbol(market, symbol),
                    symbol_type=FUTURE,
                    currency=str(item.get("currency", "")),
                    exchange=WEBULL_FUTURE_EXCHANGE.get(native_exchange.upper(), native_exchange),
                ))
        return rows

    # ---------- K 線 ----------

    def get_kline(self, code: str, ktype: str, count: int, autype: str, *,
                  raw: bool = False) -> list[dict]:
        """按 bar 數取 K 線，返回按 ts 升序的最近 count 根。

        count 即 bar 數（與富途語義相同），但接口單次上限為 BAR_MAX，要求多於上限時只能取到該上限。

        raw=True 時列為 get_batch_history_bar 單根 bar 的原生欄位（time 為 epoch 秒，數值可能為字符串），
        排序與截尾改按原生 time（同一格式，升序即時間升序），不做復權判定以外的任何處理；取數範圍不變。
        """
        timespan = self._timespan(ktype)
        self._check_autype(ktype, autype)
        parsed = parse_code(code)
        category = self._category(parsed.market)
        symbol = _native_symbol(parsed.market, parsed.symbol)
        bars = self._bars([symbol], category, timespan, min(count, BAR_MAX)).get(symbol, [])
        if raw:
            rows = [dict(bar) for bar in bars]
            rows.sort(key=lambda row: row.get("time") or 0)
            return rows[-count:]
        rows = [self._to_kline_row(code, parsed.market, ktype, bar) for bar in bars]
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
        """串流多個代碼的最新 1 分鐘 K 線，全部共用同一個客戶端。

        Webull 沒有 K 線推送，故以輪詢批量 bar 接口實現：先取一次作起點，之後每 POLL_SECONDS 取一次，
        最新一根有變化才呼叫 on_update(code, rows)，對外的回呼語義與推送券商一致。不同市場各一次請求
        （category 按市場區分），但共用同一客戶端與 token，對應同時顯示多張 K 線圖。

        raw=True 時起點與推送一律為原生 bar 欄位，按原生 time 合併（見 NativeBars）。
        """
        if ktype not in self.stream_ktypes:
            raise CodeError(
                f"ktype_unsupported: {ktype}（webull 的 K 線串流只支持 {'/'.join(self.stream_ktypes)}）"
            )
        if autype not in self.stream_autypes:
            raise CodeError(
                'autype_unsupported: webull 的 K 線串流只支持 autype="none"（分鐘線只返回不復權價）'
            )
        # category →（該 category 的市場, 原生符號 → 統一代碼）。原生符號可能與請求時不完全一致，
        # 故兩側均以 _native_symbol 歸一化後比對。
        groups: dict[str, tuple[str, dict[str, str]]] = {}
        markets: dict[str, str] = {}
        for code in codes:
            parsed = parse_code(code)
            category = self._category(parsed.market)
            market, owners = groups.setdefault(category, (parsed.market, {}))
            owners[_native_symbol(parsed.market, parsed.symbol)] = code
            markets[code] = parsed.market
        count = min(count, BAR_MAX)
        mergers = {
            code: NativeBars(count, "time") if raw else BarMerger(count) for code in codes
        }

        def pull() -> None:
            for category, (market, owners) in groups.items():
                for symbol, bars in self._bars(
                    list(owners), category, WEBULL_TIMESPAN[ktype], count, real_time=True
                ).items():
                    code = owners.get(_native_symbol(market, symbol))
                    merger = mergers.get(code)
                    if merger is None:
                        continue
                    rows = [dict(bar) for bar in bars] if raw else [
                        self._to_kline_row(code, market, ktype, bar) for bar in bars
                    ]
                    if merger.merge(rows) and on_update is not None:
                        on_update(code, merger.frame())

        pull()
        deadline = time.monotonic() + seconds if seconds > 0 else None
        try:
            while deadline is None or time.monotonic() < deadline:
                time.sleep(POLL_SECONDS)
                pull()
        except KeyboardInterrupt:  # 按 Ctrl-C 屬正常結束
            pass
        return {code: mergers[code].frame() for code in codes}

    # ---------- 戶口 ----------

    def get_accounts(self, currency: str | None = None, *, raw: bool = False) -> list[dict]:
        """戶口清單與資金：account_v2.get_account_list 定戶口，get_account_balance 取資金。

        Webull 只有真實戶口，不需按環境過濾；acc_type 由 account_type 映射（實測為 MRGN）。
        get_account_balance 同時返回各幣種明細（account_currency_assets），故指定 currency 時改讀
        該幣種的明細（沒有該幣種即不返回該戶口），未指定時以 total_asset_currency 的匯總為準，
        一律不做匯率換算。Webull 沒有淨資產與可用資金欄位（只有可提現金額，語義不同），該兩欄為
        NaN；get_account_list 亦不返回戶口狀態，status 為空字串，不以任何數字湊出。

        raw=True 時每列為該戶口的原生記錄：get_account_list 單條與 get_account_balance 返回的合併
        （含 account_currency_assets 的各幣種明細），不做欄位映射、改名或金額轉換。取數範圍不變
        （currency 仍按該戶口有無該幣種的明細來篩選）。
        """
        account_api = self._trade_client().account_v2
        rows: list[dict] = []
        for acc in _payload(account_api.get_account_list(), "get_account_list"):
            account_id = str(acc["account_id"])
            balance = _payload(account_api.get_account_balance(account_id), "get_account_balance")
            block = None
            if currency:
                block = next(
                    (item for item in balance.get("account_currency_assets", [])
                     if str(item.get("currency", "")).upper() == currency.upper()),
                    None,
                )
                if block is None:
                    continue
            if raw:
                rows.append({**acc, **balance})
                continue
            rows.append(account_row(
                source=self.source,
                account_id=account_id,
                acc_type=_acc_type_of(str(acc.get("account_type", ""))),
                status="",
                currency=(currency or str(balance.get("total_asset_currency") or "")).upper(),
                funds=_balance_funds(balance, block),
            ))
        return rows

    # ---------- 內部 ----------

    def _bars(
        self, symbols: list[str], category: str, timespan: str, count: int, real_time: bool = False
    ) -> dict[str, list[dict]]:
        """取 bar 並展開為「原生符號 → bar 列表」。

        接口返回原始 requests 響應，需自行取 json；外層可能是 {result: [...]}，批量結果可能是
        [{symbol, result: [...]}] 分組，亦可能只是一個 bar 列表（單一代碼時）。
        """
        try:
            payload = self._market_data().get_batch_history_bar(
                list(symbols), category, timespan,
                count=str(count), real_time_required=True if real_time else None,
            ).json()
        except ServerException as exc:
            # 403 MARKET_DATA_NOT_SUBSCRIBED 是賬戶在該區域未開通此市場的行情（實測：HK 區域的 app key
            # 取美股即如此），屬權限而非參數錯誤，故指出需開通行情，而非留下方 SDK 的原始錯誤。
            if exc.get_error_code() == "MARKET_DATA_NOT_SUBSCRIBED":
                raise CodeError(
                    f"market_data_not_subscribed: {category} 未開通行情權限"
                    f"（{exc.get_error_msg()}）；請在 Webull 開通該市場的行情，或改用已開通的市場代碼"
                ) from exc
            raise
        if isinstance(payload, dict):
            payload = payload.get("result", [])
        grouped: dict[str, list[dict]] = {}
        flat: list[dict] = []
        for item in payload or []:
            if not isinstance(item, dict):
                continue
            if "result" in item:
                grouped[str(item["symbol"])] = [bar for bar in item["result"] or [] if isinstance(bar, dict)]
            else:
                flat.append(item)
        if flat and len(symbols) == 1:
            grouped[symbols[0]] = flat
        return grouped

    def _to_kline_row(self, code: str, market: str, ktype: str, bar: dict) -> dict:
        """由原生 bar（數值可能為字符串）構造統一列。"""
        ts = to_utc(bar.get("time"), market)
        return kline_row(
            code=code,
            ts=align_ts(ts, market, ktype, self.kline_anchor),
            time_key=to_local_text(datetime.fromtimestamp(ts, timezone.utc), market),
            open_=bar.get("open"),
            high=bar.get("high"),
            low=bar.get("low"),
            close=bar.get("close"),
            volume=bar.get("volume"),
            turnover=float("nan"),  # 接口不返回成交額
            source=self.source,
        )

    def _timespan(self, ktype: str) -> str:
        if ktype not in WEBULL_TIMESPAN:
            raise CodeError(f"ktype_unsupported: {ktype}（可用：{'/'.join(WEBULL_TIMESPAN)}）")
        return WEBULL_TIMESPAN[ktype]

    def _check_autype(self, ktype: str, autype: str) -> None:
        """複權由週期決定而非參數，故只能接受該週期實際返回的那一種，其餘明確報錯。"""
        expected = WEBULL_AUTYPE[ktype]
        if autype != expected:
            raise CodeError(
                f"autype_unsupported: webull 的 {ktype} K 線只返回"
                f"{'前復權' if expected == 'qfq' else '不復權'}價（接口沒有復權參數）；"
                f'請用 autype="{expected}"'
            )

    def _category(self, market: str) -> str:
        if market not in WEBULL_CATEGORY:
            raise CodeError(
                f"market_unsupported: webull 只提供 {'/'.join(WEBULL_CATEGORY)} 市場的股票"
                "（K 線與股票清單）"
            )
        return WEBULL_CATEGORY[market]

    def _paged_instruments(self, **params):
        """按 pagination_key 逐頁取 list_instruments 的結果（每頁 1000 條）。

        429 屬限速而非參數錯誤，故等待後重試；無資料或無 pagination_key 即結束。
        """
        key = None
        while True:
            for attempt in range(LIST_RETRY + 1):
                try:
                    payload = _payload(
                        self._instrument_api().list_instruments(pagination_key=key, **params),
                        "list_instruments",
                    )
                    break
                except RuntimeError as exc:
                    if "HTTP 429" not in str(exc) or attempt == LIST_RETRY:
                        raise
                    time.sleep(LIST_RETRY_WAIT)
            data = payload.get("data", [])
            yield from data
            key = payload.get("pagination_key")
            if not data or not key:
                return
            time.sleep(LIST_REQUEST_INTERVAL)

    def _futures_instruments(self, category: str, root: str) -> list[dict]:
        """取某期貨產品的全部在市合約（Webull 需逐個產品查詢，無批量接口）。"""
        return _payload(
            self._instrument_api().get_futures_instrument(code=root, category=category),
            f"get_futures_instrument {root}",
        ) or []


def _native_symbol(market: str, symbol: str) -> str:
    """轉為 Webull 原生符號。港股以五位補零登記（700 → 00700），與統一顯示格式相同。"""
    return to_display_symbol(market, symbol)
