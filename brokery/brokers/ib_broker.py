"""IB 適配器：展開期貨與指數，並提供統一代碼與 IB Contract 的雙向轉換。

IB 沒有「一次過列出全市場股票」的接口，故本適配器不聲明股票清單能力，只提供代碼轉換
與逐個解析。期貨與指數以種子 root 展開所有到期月與掛牌交易所。

兩處與直覺不同，均為實測結論，實作必須遵守：
- 一般查詢不可指定 exchange：指定後 IB 常回傳「No security definition found」，留空由 IB 自行
  resolve 才取得到（港股與股票尤其明顯）。主連（CONTFUT）則相反，實測不帶 exchange 一律無結果
  （ES/ZN/10Y/HSI 皆然），必須先以同 root 的 FUT 取得掛牌交易所再查。
- 同一合約常在多個場所掛牌（如 CME 與 QBALGO），需去重並保留主場。

ib_async 為非同步介面。此處只維持一條持續連線（由專屬 event loop 執行緒驅動），所有查詢與
keepUpToDate 訂閱共用它：訂閱依附連線而存在，且同時顯示多張 K 線圖時反覆重建連線既慢又會
令訂閱失效。每個請求仍各自設定超時，避免同步封裝下無限阻塞。
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import dataclasses
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
    ACC_CASH,
    ACC_MARGIN,
    ANCHOR_END,
    CAP_FUTURE,
    CAP_INDEX,
    BarMerger,
    NativeBars,
    SymbolBroker,
    account_row,
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


# 戶口所需的 accountSummary tag。ib_async 內建的清單（見 IB.reqAccountSummaryAsync）沒有 Currency、
# UnrealizedPnL 與 RealizedPnL，少了 Currency 就不知道金額以何種幣種計，故自組清單一次取回。
# 實測個人戶口只返回其餘 tag（Currency 與兩個 PnL tag 被略過、不報錯），幣種附在每個金額的
# currency 欄上；多幣種帳戶則各幣種分行返回，故 Currency tag 仍保留，後端有返回時即可用作基準。
IB_ACCOUNT_TAGS = (
    "AccountType,NetLiquidation,TotalCashValue,GrossPositionValue,AvailableFunds,BuyingPower,"
    "InitMarginReq,MaintMarginReq,EquityWithLoanValue,UnrealizedPnL,RealizedPnL,Currency"
)
# tag → 統一金額欄位。IB 沒有「負債權益」對應 tag，該欄一律為 NaN。
IB_FUND_TAGS = {
    "NetLiquidation": "net_liquidation",
    "TotalCashValue": "cash",
    "GrossPositionValue": "market_value",
    "AvailableFunds": "available_funds",
    "BuyingPower": "buying_power",
    "InitMarginReq": "init_margin",
    "MaintMarginReq": "maint_margin",
    "EquityWithLoanValue": "equity_with_loan",
    "UnrealizedPnL": "unrealized_pnl",
    "RealizedPnL": "realized_pnl",
}


def _acc_type_of(account_type: str) -> str:
    """IB 的 AccountType → 統一戶口性質。

    該 tag 的取值為 C/M/INDIVIDUAL/LIMITED_MARGIN/PF/DEMO 等，只表明帳戶類別，未必含現金或保證金
    （INDIVIDUAL 兩者皆可能），故只對明確寫法歸類，其餘原樣返回，不憑空判定。
    """
    text = account_type.strip().upper()
    if text in ("C", "CASH"):
        return ACC_CASH
    if text in ("M", "MARGIN", "LIMITED_MARGIN", "PF"):
        return ACC_MARGIN
    return text.lower()


def _primary_exchanges(details) -> list[str]:
    """由個月份的掛牌結果取得交易所，主場排先（CONTFUT 一定要帶 exchange 先查得到）。"""
    return sorted({cd.contract.exchange for cd in details if cd.contract.exchange}, key=is_secondary_exchange)


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
    # 戶口性質由 AccountType tag 表明（C/M 等明確寫法），故兩種皆聲明。
    acc_types = (ACC_CASH, ACC_MARGIN)

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

    def list_futures(self, seeds: Iterable, *, raw: bool = False) -> list[dict]:
        """按種子 root 展開主連與所有到期月。

        raw=True 時每列為 reqContractDetails 返回的原生欄位（見 _native_row），不做任何映射；取數範圍
        （同一批種子、同樣先展開個月份再取主連）不變。
        """
        return self._run(lambda ib: self._collect_futures(ib, seeds, raw=raw))

    def list_indices(self, seeds: Iterable, *, raw: bool = False) -> list[dict]:
        """按種子符號解析指數。raw=True 時同上。"""
        return self._run(lambda ib: self._collect(ib, seeds, self._index_contracts, raw=raw))

    async def _collect(self, ib: IB, seeds: Iterable, expand, raw: bool = False) -> list[dict]:
        rows: list[dict] = []
        for seed in seeds:
            for contract in expand(seed):
                rows.extend(await self._details(ib, contract, seed.market, raw=raw))
        return rows if raw else dedupe_rows(rows)

    async def _collect_futures(self, ib: IB, seeds: Iterable, raw: bool = False) -> list[dict]:
        """個月份以 FUT 展開所有到期月，主連其後以該 root 的掛牌交易所查 CONTFUT。

        順序不能對調：CONTFUT 不帶 exchange 一律返回「No security definition found」，而 exchange 只能
        從同 root 的 FUT 結果取得。同一 root 的 CONTFUT 喺唔同場所返回同一 conId，故取首個主場即止。
        """
        rows: list[dict] = []
        for seed in seeds:
            months = await self._req_details(ib, Contract(secType="FUT", symbol=seed.root))
            rows.extend(self._rows(months, "FUT", seed.market, raw=raw))
            for exchange in _primary_exchanges(months):
                continuous = await self._req_details(
                    ib, Contract(secType="CONTFUT", symbol=seed.root, exchange=exchange))
                if continuous:
                    rows.extend(self._rows(continuous, "CONTFUT", seed.market, raw=raw))
                    break
        return rows if raw else dedupe_rows(rows)

    @staticmethod
    def _index_contracts(seed):
        return [Contract(secType="IND", symbol=seed.symbol)]

    async def _details(self, ib: IB, contract: Contract, hint_market: str,
                       raw: bool = False) -> list[dict]:
        return self._rows(await self._req_details(ib, contract), contract.secType, hint_market, raw=raw)

    async def _req_details(self, ib: IB, contract: Contract):
        try:
            return await asyncio.wait_for(ib.reqContractDetailsAsync(contract), timeout=self.timeout)
        except asyncio.TimeoutError:
            raise RuntimeError(f"timeout: IB reqContractDetails {contract.symbol} 超過 {self.timeout}s") from None

    def _rows(self, details, sec_type: str, hint_market: str, raw: bool = False) -> list[dict]:
        if raw:
            return [self._native_row(cd) for cd in details]
        rows = []
        for cd in details:
            row = self._row_from_details(cd, sec_type, hint_market)
            if row:
                rows.append(row)
        return rows

    @staticmethod
    def _native_row(cd) -> dict:
        """reqContractDetails 單條結果的原生欄位：ContractDetails 各欄加上其 Contract 各欄。

        contract 欄的值即後者，展開後再保留便重複，故略去。值一律原樣（含 secIdList、comboLegs 等物件），
        不轉為文字也不拆值。
        """
        row = {field.name: getattr(cd, field.name, None) for field in dataclasses.fields(cd)}
        row.pop("contract", None)
        contract = cd.contract
        row.update({field.name: getattr(contract, field.name, None)
                    for field in dataclasses.fields(contract)})
        return row

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

        # IB 以 root 表達個月份合約，到期月只在 lastTradeDateOrContractMonth。統一格式不設到期月欄，
        # 故與富途一樣把到期月寫進符號（如 ES202612），否則各月份合約會成爲同一個代碼。
        if continuous:
            symbol = f"{root}{MAIN_SUFFIX}"
        else:
            symbol = f"{root}{raw_expiry}" if raw_expiry else root

        name = getattr(cd, "contractSymbolDescription", "") or getattr(cd, "longName", "") or ""
        return self.make_row(
            code=f"{market}.{to_display_symbol(market, symbol)}",
            name=name,
            market=market,
            symbol=to_display_symbol(market, symbol),
            symbol_type=FUTURE if sec_type in ("FUT", "CONTFUT") else INDEX,
            currency=currency,
            exchange=exchange,
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
        # 個月份合約的代碼自帶到期月（US.ES202612），與清單所出者一致；到期月只作 IB 的合約參數，
        # 不從代碼中剝走，否則同一 root 的各月份會成爲同一個代碼。
        if expiry:
            normalised = parsed.symbol
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

        主連（CONTFUT）一定要帶掛牌交易所，故先以同 root 的 FUT 取得交易所，再逐個嘗試。
        """
        if contract.secType == "CONTFUT" and not contract.exchange:
            months = await self._req_details(
                ib, Contract(secType="FUT", symbol=contract.symbol, currency=contract.currency))
            for exchange in _primary_exchanges(months):
                matched = await self._best_match(ib, Contract(
                    secType="CONTFUT", symbol=contract.symbol, exchange=exchange, currency=contract.currency))
                if matched is not None:
                    return matched
            return None
        try:
            details = await self._req_details(ib, contract)
        except RuntimeError:
            raise  # 超時屬連線問題，要向上抛出，不能當做「無此合約」
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

    def get_kline(self, code: str, ktype: str, count: int, autype: str, *, raw: bool = False) -> list[dict]:
        """按 bar 數取 K 線：先換算出足夠的時間跨度，再取最後 count 根（對齊富途的 bar 數語義）。

        IB 沒有 bar 數參數，故跨度刻意多覆蓋周末與假期。autype 只可能是 none 或 qfq（其餘由 core
        擋掉），其中 qfq 僅適用日內與日線。IB 不返回成交額，turnover 為 NaN。
        raw=True 時列為 BarData 的原生欄位（date 為 datetime），排序與截尾改按原生 date（同一格式，
        升序即時間升序），取數範圍不變。
        """
        if ktype not in IB_BAR_SIZE:
            raise CodeError(f"ktype_unsupported: {ktype}（可用：{'/'.join(IB_BAR_SIZE)}）")
        if autype != "none" and ktype in MULTI_DAY_KTYPES:
            raise CodeError(
                f'autype_unsupported: ib 的 {ktype} 線不支持複權 {autype}'
                "（IB 對多於一日的 bar 直接報 error 321「Multi day bar size not supported with"
                ' adjusted last」）；週/月線請用 autype="none"'
            )
        return self._run(lambda ib: self._kline(ib, code, ktype, count, autype, raw=raw))

    async def _resolve_cached(self, ib: IB, code: str) -> dict:
        """按統一代碼解析合約，結果快取。"""
        info = self._contracts.get(code)
        if info is None:
            info = await self._resolve(ib, parse_code(code))
            self._contracts[code] = info
        return info

    async def _kline(self, ib: IB, code: str, ktype: str, count: int, autype: str,
                     raw: bool = False) -> list[dict]:
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
        if raw:
            rows = [self._native_bar(bar) for bar in bars]
            rows.sort(key=lambda row: row["date"])
        else:
            rows = [self._to_kline_row(resolved["code"], parsed.market, ktype, bar) for bar in bars]
            rows.sort(key=lambda row: row["ts"])
        return rows[-count:]

    @staticmethod
    def _native_bar(bar) -> dict:
        """reqHistoricalData 單根 bar 的原生欄位（BarData 各欄），值不做換算。"""
        return {field.name: getattr(bar, field.name, None) for field in dataclasses.fields(bar)}

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
        *,
        raw: bool = False,
    ) -> dict[str, list[dict]]:
        """串流多個代碼的最新 K 線，全部共用同一條 IB 連線。

        以 reqHistoricalData(keepUpToDate=True) 實現：該請求先返回歷史 bar，之後同一個 bar 序列由
        IB 持續更新（最新一根未走完時反覆改寫，走完後追加新根），故起點即歷史，不需另一次查詢。
        回調在連線執行緒中發生。seconds 為持續秒數，0 表示直到 Ctrl-C。
        raw=True 時起點與推送一律為 BarData 的原生欄位，按原生 date 合併（見 NativeBars）。
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
            lambda ib: self._open_streams(ib, codes, ktype, count, autype, on_update, raw=raw),
            budget=self.timeout * len(codes) + 10,
        )
        try:
            stream_wait(seconds)
        finally:
            self._run(lambda ib: self._close_streams(ib, sessions))
        return {code: merger.frame() for code, _bars, _handler, merger in sessions}

    async def _open_streams(self, ib: IB, codes, ktype: str, count: int, autype: str, on_update,
                           raw: bool = False) -> list:
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
            merger = NativeBars(count, "date") if raw else BarMerger(count)

            def _row(bar) -> dict:
                return self._native_bar(bar) if raw else self._to_kline_row(
                    merged_code, parsed.market, ktype, bar)

            merger.merge(_row(bar) for bar in bars)

            # _row 是迴圈內的區域名稱，回調為共用同一個變數，故以預設參數綁定本輪的轉換器。
            def _on_bar_update(live_bars, _has_new_bar, code_=merged_code, merger_=merger,
                               row_=_row) -> None:
                # 每次更新只改寫最後一根，或在末尾追加新根，故只需合併末尾兩根。
                rows = [row_(bar) for bar in live_bars[-2:]]
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

    # ---------- 戶口 ----------

    def get_accounts(self, currency: str | None = None, *, raw: bool = False) -> list[dict]:
        """戶口清單與資金：accountSummary 一次取回所連後端能看到的所有戶口。

        IB 的真實與模擬由所連 Gateway/TWS 決定，接口本身沒有這個維度，故一律按真實戶口返回。
        acc_type 由 AccountType tag 映射（見 _acc_type_of），無法判定的類別原樣返回。currency 取每
        個金額自帶的結算幣，多幣種帳戶按幣種各列一欄；currency 參數只作篩選，一律不做匯率換算。
        IB 沒有戶口狀態與負債權益欄位，該兩欄為空字串與 NaN，不以任何數字湊出。
        raw=True 時每列為 accountSummary 單條結果的原生欄位（account/tag/value/currency/modelCode），
        即一個 tag 一列，不做 tag 歸併、類型映射或金額轉換；取數範圍不變（currency 參數仍按該列
        自帶的結算幣篩選）。
        """
        summary = self._run(lambda ib: self._account_summary(ib))
        if raw:
            rows = []
            for value in summary:
                if currency and str(value.currency).upper() != currency.upper():
                    continue
                rows.append(dict(value._asdict()))
            return rows
        acc_type: dict[str, str] = {}
        base_ccy: dict[str, str] = {}
        funds: dict[tuple[str, str], dict] = {}
        for value in summary:
            account = str(value.account)
            if value.tag == "AccountType":
                acc_type[account] = _acc_type_of(str(value.value))
            elif value.tag == "Currency":
                base_ccy[account] = str(value.value).upper()
            elif value.tag in IB_FUND_TAGS:
                # 每個金額自帶其結算幣，故按（戶口, 幣種）分組：多幣種帳戶各幣種另列一欄，同一幣種
                # 的多項 tag 則合併到同一欄。
                funds.setdefault((account, str(value.currency).upper()), {})[IB_FUND_TAGS[value.tag]] = value.value

        rows = []
        for (account, ccy), values in funds.items():
            ccy = ccy or base_ccy.get(account, "")
            if currency and currency.upper() != ccy:
                continue
            rows.append(account_row(
                source=self.source,
                account_id=account,
                acc_type=acc_type.get(account, ""),
                status="",
                currency=ccy,
                funds=values,
            ))
        return rows

    @staticmethod
    async def _account_summary(ib: IB) -> list:
        """以自組的 tag 清單請求 accountSummary（ib_async 的預設清單缺少需要的三個 tag）。

        wrapper 的 acctSummary 會把多次請求的結果合併保留，不清空會把上一次查詢的舊值一併返回。
        取回後必須取消訂閱：IB 只容許有限數量的 accountSummary 訂閱同時存在，不取消便會累積，到上限
        即回 error 322（Maximum number of account summary requests exceeded），其後的查詢靜默返回空值，
        戶口因此無故消失（實測同一連線連續數次查詢即觸發，定時刷新時必定發生）。
        """
        req_id = ib.client.getReqId()
        future = ib.wrapper.startReq(req_id)
        ib.wrapper.acctSummary.clear()
        ib.client.reqAccountSummary(req_id, "All", IB_ACCOUNT_TAGS)
        await future
        values = list(ib.wrapper.acctSummary.values())
        ib.client.cancelAccountSummary(req_id)
        return values

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
