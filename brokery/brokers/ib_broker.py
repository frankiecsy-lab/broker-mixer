"""IB 適配器：展開期貨與指數，並提供統一代碼與 IB Contract 的雙向轉換。

IB 沒有「一次過列出全市場股票」的接口，故本適配器不聲明股票清單能力，只提供代碼轉換
與逐個解析。期貨與指數以種子 root 展開所有到期月與掛牌交易所。

兩處與直覺不同，均為實測結論，實作必須遵守：
- 查詢時不可指定 exchange。指定後 IB 常回傳「No security definition found」；留空由
  IB 自行 resolve 才取得到（港股與期貨尤其明顯）。
- 同一合約常在多個場所掛牌（如 CME 與 QBALGO），需去重並保留主場。

ib_async 為非同步介面。此處只維持一條持續連線（由專屬 event loop 執行緒驅動），所有查詢與
keepUpToDate 訂閱共用它：訂閱依附連線而存在，且同時顯示多張 K 線圖時反覆重建連線既慢又會
令訂閱失效。每個請求仍各自設定超時，避免同步封裝下無限阻塞。
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import threading
from collections.abc import Iterable

from ib_async import Contract, IB

from ..codes import (
    FUTURE,
    INDEX,
    MAIN_SUFFIX,
    STOCK,
    CodeError,
    classify_symbol,
    currency_of,
    is_secondary_exchange,
    market_of,
    parse_code,
    split_future_symbol,
    to_display_symbol,
    to_native_symbol,
)
from ..config import get_settings
from .base import (
    ANCHOR_END,
    CAP_FUTURE,
    CAP_INDEX,
    BarMerger,
    SymbolBroker,
    align_ts,
    dedupe_rows,
    kline_row,
    span_days,
    stream_wait,
    to_local_text,
    to_utc,
)

# 統一 ktype → IB 的 barSizeSetting。單位為一時必須用單數：實測「1 mins」被拒（error 321
# 「Historical data bar size setting is invalid. Legal ones are: 1 secs, 5 secs, …, 1 min, 2 mins,
# 3 mins, 4 mins, 5 mins, 10 mins, 15 mins, 20 mins, 30 mins, 1 hour, …, 1 day, 1W, 1M」），
# 改「1 min」後正常返回。週/月線用「1 week/1 month」（實測可用），TWS 提示中的 1W/1M 為另一寫法。
IB_BAR_SIZE = {
    "1m": "1 min", "3m": "3 mins", "5m": "5 mins", "15m": "15 mins", "30m": "30 mins",
    "60m": "1 hour", "day": "1 day", "week": "1 week", "month": "1 month",
}

# 複權模式 → whatToShow。IB 只有兩種：TRADES 為原始成交價；ADJUSTED_LAST 把價格調整至最近一次
# 除淨日之前的水平（方向與前復權一致，最近一次除淨日之後的 bar 不變）。沒有後復權對應值。
IB_WHAT_TO_SHOW = {"none": "TRADES", "qfq": "ADJUSTED_LAST"}

# ADJUSTED_LAST 只適用於日內與日線：多於一日的 bar 直接被拒（實測 error 321「Multi day bar size
# not supported with adjusted last」），故週/月線要求復權時由 get_kline 明確拒绝。
MULTI_DAY_KTYPES = ("week", "month")

# 歷史 K 線失敗時的錯誤碼（實測：whatToShow 用 TABS 對股票回報 321「What to show value of
# TABS rejected」，故股票與指數一律用 TRADES）。其餘 errorEvent 屬連線提示，不作失敗依據。
KLINE_ERROR_CODES = (162, 300, 321)

# durationStr 的單位上限：超過 365 日仍用「D」會被拒（實測 error 321「Historical data requests
# for durations longer than 365 days must be made in years.」），需改以年計並向上取整。
MAX_DAY_DURATION = 365
DAYS_PER_YEAR = 365

# 港股指數在 IB 以名稱登記（富途為六位數字），只登記實測可解析的幾隻；其餘港股指數在 IB
# 查無同名合約，由 _resolve 明確返回 unresolvable。美股指數去前導點即同名，不需別名。
IB_INDEX_ALIAS = {
    "HK.800000": "HSI",
    "HK.800100": "HSCEI",
    "HK.800125": "VHSI",
    "HK.800700": "HSTECH",
}


def _duration(days: int) -> str:
    """日曆跨度 → IB 的 durationStr。一律向上取整到可用單位，多出的部分由呼叫端截尾。"""
    if days <= MAX_DAY_DURATION:
        return f"{days} D"
    return f"{-(-days // DAYS_PER_YEAR)} Y"


class IbBroker(SymbolBroker):
    """IB 標的來源（期貨與指數）及代碼轉換器。"""

    source = "ib"
    capabilities = frozenset({CAP_FUTURE, CAP_INDEX})
    # 實測 IB 的週線以週六、月線以下月一日為 bar 時間，即以週期終點為錨點。
    kline_anchor = ANCHOR_END
    # IB 的複權只有兩種：none（原始成交價）與 qfq（ADJUSTED_LAST，調整至最近一次除淨日，方向同
    # 前復權）。qfq 不適用於週/月線（見 MULTI_DAY_KTYPES），亦無後復權概念，故 hfq 一律不支持。
    # 注意 ADJUSTED_LAST 的調整因子與富途不同（實測日線 60 根最大相差 0.44%），不可視為等價數據。
    autypes = ("none", "qfq")
    # 串流以 keepUpToDate 實現，全部 ktype 均可用（實測 1 min…1 month 訂閱皆存活並持續更新）；
    # 但 keepUpToDate 與 ADJUSTED_LAST 不能同時使用（實測被拒 error 321），故串流只支持 none。
    stream_ktypes = tuple(IB_BAR_SIZE)
    stream_autypes = ("none",)
    # 期權不聲明：IB 的期權合約需完整結構（行權價、到期月、買賣方向），統一代碼無法唯一還原。
    kline_symbol_types = (STOCK, FUTURE, INDEX)

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        client_id: int | None = None,
        timeout: float | None = None,
    ):
        settings = get_settings()
        self.host = host or settings.ib_host
        self.port = port or settings.ib_port
        self.client_id = client_id if client_id is not None else settings.ib_client_id
        self.timeout = timeout or settings.request_timeout
        self._conn = _SharedConnection(self.host, self.port, self.client_id, self.timeout)
        # 同一代碼的合約只解析一次：多張圖反覆取數時，解析本身每次都要多一次往返。
        self._contracts: dict[str, dict] = {}

    # ---------- 連線 ----------

    def connect(self) -> None:
        """建立（或沿用）那一條共用連線。所有方法都會自動呼叫，無需手動调用。"""
        self._conn.start()

    def close(self) -> None:
        self._conn.stop()
        self._contracts.clear()

    # ---------- 清單 ----------

    def list_futures(self, seeds: Iterable) -> list[dict]:
        """按種子 root 展開主連與所有到期月。"""
        return self._run(lambda ib: self._collect(ib, seeds, self._future_contracts))

    def list_indices(self, seeds: Iterable) -> list[dict]:
        """按種子符號解析指數。"""
        return self._run(lambda ib: self._collect(ib, seeds, self._index_contracts))

    async def _collect(self, ib: IB, seeds: Iterable, expand) -> list[dict]:
        rows: list[dict] = []
        for seed in seeds:
            for contract in expand(seed):
                rows.extend(await self._details(ib, contract, seed.market))
        return dedupe_rows(rows)

    @staticmethod
    def _future_contracts(seed):
        # 主連以 CONTFUT 取得真實連續合約；個月份以 FUT 展開所有到期月。
        return [Contract(secType="CONTFUT", symbol=seed.root), Contract(secType="FUT", symbol=seed.root)]

    @staticmethod
    def _index_contracts(seed):
        return [Contract(secType="IND", symbol=seed.symbol)]

    async def _details(self, ib: IB, contract: Contract, hint_market: str) -> list[dict]:
        try:
            details = await asyncio.wait_for(ib.reqContractDetailsAsync(contract), timeout=self.timeout)
        except asyncio.TimeoutError:
            raise RuntimeError(f"timeout: IB reqContractDetails {contract.symbol} 超過 {self.timeout}s") from None
        rows = []
        for cd in details:
            row = self._row_from_details(cd, contract.secType, hint_market)
            if row:
                rows.append(row)
        return rows

    def _row_from_details(self, cd, sec_type: str, hint_market: str) -> dict | None:
        c = cd.contract
        exchange = c.exchange or ""
        currency = c.currency or ""
        raw_expiry = c.lastTradeDateOrContractMonth or ""
        root = c.symbol or ""
        continuous = sec_type == "CONTFUT"

        try:
            market = market_of(exchange, currency)
        except CodeError:
            market = hint_market

        if continuous:
            symbol = f"{root}{MAIN_SUFFIX}"
            expiry = ""
        else:
            symbol = root
            expiry = raw_expiry

        name = getattr(cd, "contractSymbolDescription", "") or getattr(cd, "longName", "") or ""
        return self.make_row(
            code=f"{market}.{to_display_symbol(market, symbol)}",
            name=name,
            market=market,
            symbol=to_display_symbol(market, symbol),
            symbol_type=FUTURE if sec_type in ("FUT", "CONTFUT") else INDEX,
            currency=currency,
            exchange=exchange,
            expiry=expiry,
            raw_code=f"{sec_type}|{root}|{exchange}|{currency}|{raw_expiry}|{c.conId}",
        )

    # ---------- 代碼轉換 ----------

    def to_contract(self, code: str) -> dict:
        """統一代碼 → 已解析的 IB 合約資訊。回傳含 contract 與推斷出的 symbol_type。"""
        parsed = parse_code(code)
        return self._run(lambda ib: self._resolve(ib, parsed))

    async def _resolve(self, ib: IB, parsed) -> dict:
        symbol_type = classify_symbol(parsed.market, parsed.symbol)
        root, expiry = split_future_symbol(parsed.symbol)
        native = to_native_symbol(parsed.market, root)
        currency = currency_of(parsed.market)
        # 個月份的到期月一律放 expiry 欄，不寫進代碼；US.ES20261218 正規化為 US.ES。
        if expiry:
            normalised = root
        elif root != parsed.symbol:
            normalised = f"{root}{MAIN_SUFFIX}"
        else:
            normalised = parsed.symbol
        code = f"{parsed.market}.{to_display_symbol(parsed.market, normalised)}"

        if symbol_type == INDEX:
            # IB 的指數以名稱登記，且不接受 currency（實測帶 currency 的 IND 查詢一律返回 0 筆）。
            # 美股去前導點即同名（.SPX → SPX）；港股的六位數字只有下表幾隻登記了名稱。
            name = IB_INDEX_ALIAS.get(f"{parsed.market}.{parsed.symbol}")
            if not name and parsed.market.upper() == "US":
                name = parsed.symbol.lstrip(".")
            if not name:
                raise CodeError(
                    f"unresolvable: {code} 在 IB 沒有對應的指數名稱"
                    f"（已登記 {', '.join(sorted(IB_INDEX_ALIAS))}）"
                )
            candidates: list[tuple[str, Contract]] = [(INDEX, Contract(secType="IND", symbol=name))]
        elif expiry:
            candidates = [
                (FUTURE, Contract(secType="FUT", symbol=native, currency=currency,
                                  lastTradeDateOrContractMonth=expiry))
            ]
        elif root != parsed.symbol:  # 帶 main 後綴 → 主連
            candidates = [(FUTURE, Contract(secType="CONTFUT", symbol=native, currency=currency))]
        else:
            candidates = [
                (STOCK, Contract(secType="STK", symbol=native, currency=currency)),
                (FUTURE, Contract(secType="CONTFUT", symbol=native, currency=currency)),
            ]

        for symbol_type, contract in candidates:
            matched = await self._best_match(ib, contract)
            if matched is not None:
                return {
                    "contract": matched,
                    "symbol_type": symbol_type,
                    "code": code,
                    "raw_code": f"{matched.secType}|{matched.symbol}|{matched.exchange}|{matched.currency}"
                    f"|{matched.lastTradeDateOrContractMonth or ''}|{matched.conId}",
                }
        raise CodeError(f"unresolvable: {code} 在 IB 找不到對應合約（已嘗試 {', '.join(t for t, _ in candidates)}）")

    async def _best_match(self, ib: IB, contract: Contract):
        """解析單一合約並取主場掛牌。

        不用 qualifyContracts：同一合約常在多處掛牌（CME 與 QBALGO），qualify 會直接
        回報 Ambiguous。reqContractDetails 可取回全部掛牌，再自行剔除次要場所。
        """
        try:
            details = await asyncio.wait_for(ib.reqContractDetailsAsync(contract), timeout=self.timeout)
        except asyncio.TimeoutError:
            raise RuntimeError(f"timeout: IB 解析 {contract.symbol} 超過 {self.timeout}s") from None
        except Exception:
            return None  # 該類型無此合約（IB 以 Error 200 回報），改試下一個候選
        primary = [cd for cd in details if not is_secondary_exchange(cd.contract.exchange or "")]
        pool = primary or list(details)
        return pool[0].contract if pool else None

    def to_unified_code(self, contract) -> str:
        """IB 原生合約 → 統一代碼。"""
        market = market_of(contract.exchange or "", contract.currency or "")
        root, expiry = split_future_symbol(contract.symbol or "")
        symbol = f"{root}{MAIN_SUFFIX}" if contract.secType == "CONTFUT" else (root or contract.symbol)
        return f"{market}.{to_display_symbol(market, symbol)}"

    # ---------- K 線 ----------

    def get_kline(self, code: str, ktype: str, count: int, autype: str) -> list[dict]:
        """按 bar 數取 K 線：先換算出足夠的時間跨度，再取最後 count 根（對齊富途的 bar 數語義）。

        IB 沒有 bar 數參數，故跨度刻意多覆蓋周末與假期。autype 只可能是 none 或 qfq（其餘由 core
        擋掉），其中 qfq 僅適用日內與日線。IB 不返回成交額，turnover 為 NaN。
        """
        if ktype not in IB_BAR_SIZE:
            raise CodeError(f"ktype_unsupported: {ktype}（可用：{'/'.join(IB_BAR_SIZE)}）")
        if autype != "none" and ktype in MULTI_DAY_KTYPES:
            raise CodeError(
                f'autype_unsupported: ib 的 {ktype} 線不支持複權 {autype}'
                "（IB 對多於一日的 bar 直接報 error 321「Multi day bar size not supported with"
                ' adjusted last」）；週/月線請用 autype="none"'
            )
        return self._run(lambda ib: self._kline(ib, code, ktype, count, autype))

    async def _resolve_cached(self, ib: IB, code: str) -> dict:
        """按統一代碼解析合約，結果快取。"""
        info = self._contracts.get(code)
        if info is None:
            info = await self._resolve(ib, parse_code(code))
            self._contracts[code] = info
        return info

    async def _kline(self, ib: IB, code: str, ktype: str, count: int, autype: str) -> list[dict]:
        parsed = parse_code(code)
        resolved = await self._resolve_cached(ib, code)
        # IB 查詢失敗時只以 errorEvent 回報，reqHistoricalData 則返回空表；不留痕便無法判斷是
        # 無權限還是參數被拒，故收集與歷史查詢相關的錯誤碼。
        failures: list[str] = []

        def _note(_ib, error_code, message, *_) -> None:
            if error_code in KLINE_ERROR_CODES:
                failures.append(f"{error_code}: {message}")

        ib.errorEvent += _note
        try:
            bars = await ib.reqHistoricalDataAsync(
                resolved["contract"],
                endDateTime="",
                durationStr=_duration(span_days(ktype, count)),
                barSizeSetting=IB_BAR_SIZE[ktype],
                whatToShow=IB_WHAT_TO_SHOW[autype],
                useRTH=1,
                formatDate=2,
                timeout=self.timeout,
            )
        except asyncio.TimeoutError:
            raise RuntimeError(f"timeout: IB reqHistoricalData {code} 超過 {self.timeout}s") from None
        finally:
            ib.errorEvent -= _note
        if not bars:
            raise RuntimeError(f"no_bars: {code} IB 未返回任何 bar（{ '；'.join(failures) or '可能無市場數據權限' }）")
        rows = [self._to_kline_row(resolved["code"], parsed.market, ktype, bar) for bar in bars]
        rows.sort(key=lambda row: row["ts"])
        return rows[-count:]

    def _to_kline_row(self, code: str, market: str, ktype: str, bar) -> dict:
        return kline_row(
            code=code,
            ts=align_ts(to_utc(bar.date, market), market, ktype, self.kline_anchor),
            time_key=to_local_text(bar.date, market),
            open_=bar.open,
            high=bar.high,
            low=bar.low,
            close=bar.close,
            volume=bar.volume,
            turnover=float("nan"),
            source=self.source,
        )

    # ---------- K 線串流 ----------

    def stream_kline(
        self,
        codes: tuple[str, ...],
        ktype: str,
        count: int,
        autype: str,
        seconds: float,
        on_update,
    ) -> dict[str, list[dict]]:
        """串流多個代碼的最新 K 線，全部共用同一條 IB 連線。

        以 reqHistoricalData(keepUpToDate=True) 實現：該請求先返回歷史 bar，之後同一個 bar 序列由
        IB 持續更新（最新一根未走完時反覆改寫，走完後追加新根），故起點即歷史，不需另一次查詢。
        回調在連線執行緒中發生。seconds 為持續秒數，0 表示直到 Ctrl-C。
        """
        if ktype not in IB_BAR_SIZE:
            raise CodeError(f"ktype_unsupported: {ktype}（可用：{'/'.join(IB_BAR_SIZE)}）")
        if autype != "none":
            raise CodeError(
                'autype_unsupported: ib 的 K 線串流只支持 autype="none"'
                "（實測 keepUpToDate 與 ADJUSTED_LAST 同時使用被拒，error 321）；"
                '串流請用 autype="none"'
            )
        # 每個代碼各自有一次歷史請求，外層兜底須按代碼數放宽，否則多張圖時會誤報超時。
        sessions = self._run(
            lambda ib: self._open_streams(ib, codes, ktype, count, autype, on_update),
            budget=self.timeout * len(codes) + 10,
        )
        try:
            stream_wait(seconds)
        finally:
            self._run(lambda ib: self._close_streams(ib, sessions))
        return {code: merger.frame() for code, _bars, _handler, merger in sessions}

    async def _open_streams(self, ib: IB, codes, ktype: str, count: int, autype: str, on_update) -> list:
        """逐個代碼建立 keepUpToDate 訂閱，返回 (代碼, bar 序列, 更新回調, 合併器)。"""
        sessions = []
        for code in codes:
            parsed = parse_code(code)
            resolved = await self._resolve_cached(ib, code)
            failures: list[str] = []

            def _note(_ib, error_code, message, *_) -> None:
                if error_code in KLINE_ERROR_CODES:
                    failures.append(f"{error_code}: {message}")

            ib.errorEvent += _note
            try:
                bars = await ib.reqHistoricalDataAsync(
                    resolved["contract"],
                    endDateTime="",
                    durationStr=_duration(span_days(ktype, count)),
                    barSizeSetting=IB_BAR_SIZE[ktype],
                    whatToShow=IB_WHAT_TO_SHOW[autype],
                    useRTH=1,
                    formatDate=2,
                    keepUpToDate=True,
                    timeout=self.timeout,
                )
            except asyncio.TimeoutError:
                raise RuntimeError(f"timeout: IB reqHistoricalData {code} 超過 {self.timeout}s") from None
            finally:
                ib.errorEvent -= _note
            if not bars:
                raise RuntimeError(f"no_bars: {code} IB 未返回任何 bar（{ '；'.join(failures) or '可能無市場數據權限' }）")
            merged_code = resolved["code"]
            merger = BarMerger(count)
            merger.merge(
                self._to_kline_row(merged_code, parsed.market, ktype, bar) for bar in bars
            )

            def _on_bar_update(live_bars, _has_new_bar, code_=merged_code, market=parsed.market,
                               merger_=merger) -> None:
                # 每次更新只改寫最後一根，或在末尾追加新根，故只需合併末尾兩根。
                rows = [self._to_kline_row(code_, market, ktype, bar) for bar in live_bars[-2:]]
                if merger_.merge(rows) and on_update is not None:
                    on_update(code_, merger_.frame())

            bars.updateEvent += _on_bar_update
            sessions.append((merged_code, bars, _on_bar_update, merger))
        return sessions

    async def _close_streams(self, ib: IB, sessions) -> None:
        """退訂。訂閱依附連線而存在，不退訂會一直佔用帳戶的歷史數據訂閱名額。"""
        for _code, bars, handler, _merger in sessions:
            bars.updateEvent -= handler
            ib.cancelHistoricalData(bars)

    # ---------- 內部 ----------

    def _run(self, coro_factory, budget: float | None = None):
        """在共用連線的 event loop 上執行一個查詢協程（對外仍為同步介面）。"""
        return self._conn.call(coro_factory, budget)


class _SharedConnection:
    """一條持續的 IB 連線，由專屬 event loop 執行緒驅動。

    keepUpToDate 訂閱只在連線存續期間有效；而同時顯示多張 K 線圖時每次查詢重建連線會明顯
    變慢（每次另加連線與合約解析的往返），故所有查詢與訂閱都走同一條連線。
    """

    def __init__(self, host: str, port: int, client_id: int, timeout: float):
        self._host = host
        self._port = port
        self._client_id = client_id
        self._timeout = timeout
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._ib: IB | None = None

    def start(self) -> None:
        if self._ib is not None:
            return
        loop = asyncio.new_event_loop()
        thread = threading.Thread(target=loop.run_forever, name="brokery-ib", daemon=True)
        thread.start()
        self._loop, self._thread = loop, thread
        ib = IB()
        try:
            self._await(
                ib.connectAsync(
                    self._host, self._port, clientId=self._client_id, timeout=min(10.0, self._timeout)
                ),
                "連線",
            )
        except BaseException:
            try:
                ib.disconnect()
            except Exception:
                pass
            self._shutdown()
            raise
        self._ib = ib

    def call(self, coro_factory, budget: float | None = None):
        """在連線執行緒上完成一次請求。協程內部各自已設超時，這裡只作兜底；

        一段協程內含多次請求時（如逐個代碼建立串流訂閱）須按次數放宽 budget。
        """
        if self._ib is None:
            self.start()
        return self._await(coro_factory(self._ib), "請求", budget)

    def stop(self) -> None:
        self._shutdown()

    def _await(self, coro, label: str, budget: float | None = None):
        loop = self._loop
        if loop is None:
            raise RuntimeError(f"not_connected: IB 連線未建立，無法執行{label}")
        limit = budget if budget is not None else self._timeout + 10
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        try:
            return future.result(limit)
        except concurrent.futures.TimeoutError:
            future.cancel()
            raise RuntimeError(f"timeout: IB {label} 超過 {limit}s") from None

    def _shutdown(self) -> None:
        if self._ib is not None and self._loop is not None:
            try:
                self._loop.call_soon_threadsafe(self._ib.disconnect)
            except RuntimeError:
                pass  # 迴圈已停止，連線已斷
            self._ib = None
        if self._loop is not None and self._thread is not None:
            try:
                self._loop.call_soon_threadsafe(self._loop.stop)
                self._thread.join(5)
            except RuntimeError:
                pass
            self._loop, self._thread = None, None
