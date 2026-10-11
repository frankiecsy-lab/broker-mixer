"""富途適配器：以 get_stock_basicinfo 一次取得全市場標的清單。

選用 get_stock_basicinfo 而非 get_stock_filter：後者是條件選股，需分頁且受「每 30 秒 10 次」
限頻，實測取美股時常被拒；前者每個（市場, 證券類型）一次調用即返回全量，無分頁、無該限頻，
且 name 無空值、delisting 全為 False（實測港美 STOCK/ETF 共 23750 條）。

富途同時提供期貨與指數清單（FUTURE/IDX 類型），故三類能力均在此聲明。富途的期貨主連以
`main` 後綴表示（如 US.10Ymain，另有 current/next/day 變體），與本專案的主連約定一致；但
個月份用富途原生代碼（如 US.10Y2609）。統一格式不設到期月欄，各月份一律由符號唯一標識（IB／
Tiger／Webull 亦寫成 root+到期月），但各家的產品代碼與月份寫法仍不相同，跨券商對映仍須經 IB。
"""
from __future__ import annotations

from collections.abc import Iterable
from datetime import date, timedelta

import futu

from ..codes import FUTURE, INDEX, OPTION, STOCK, CodeError, currency_of, parse_code
from ..config import get_settings
from .base import (
    ACC_CASH,
    ACC_MARGIN,
    CAP_FUTURE,
    CAP_INDEX,
    CAP_STOCK,
    BarMerger,
    NativeBars,
    SymbolBroker,
    account_row,
    align_ts,
    kline_row,
    span_days,
    stream_wait,
    to_utc,
)

# 統一市場前綴 → 富途 Market 枚舉。
FUTU_MARKET = {
    "HK": futu.Market.HK,
    "US": futu.Market.US,
    "SG": futu.Market.SG,
    "SH": futu.Market.SH,
    "SZ": futu.Market.SZ,
    "JP": futu.Market.JP,
    "MY": futu.Market.MY,
    "AU": futu.Market.AU,
    "CA": futu.Market.CA,
}

# 富途 get_stock_basicinfo 的類型 → 統一 symbol_type。無 ALL 類型（NONE 回報「未知股票類型」），
# 需逐類型請求；ETF 與正股同屬掛牌證券，統一歸為 STOCK。
STOCK_TYPES = ("STOCK", "ETF")
FUTURE_TYPES = ("FUTURE",)
INDEX_TYPES = ("IDX",)
TYPE_OF = {"STOCK": STOCK, "ETF": STOCK, "FUTURE": FUTURE, "IDX": INDEX}

# 富途對部分（市場, 類型）明確不支持（實測「获取静态数据接口不支持日本市场的指数」），屬能力缺口
# 而非請求失敗，故跳過該市場繼續；其餘非零返回仍照樣抛出。
UNSUPPORTED_HINT = "不支持"

# 統一 ktype / autype → 富途參數。K 線以 bar 數取數，與富途 get_cur_kline 的 num 語義一致。
FUTU_KTYPE = {
    "1m": "K_1M", "3m": "K_3M", "5m": "K_5M", "15m": "K_15M", "30m": "K_30M", "60m": "K_60M",
    "day": "K_DAY", "week": "K_WEEK", "month": "K_MON",
}
# 此版本的 autype 只接受小寫 "qfq"/"hfq" 與字串 "None"（實測傳 "QFQ" 回報「autype is QFQ, which is
# not valid. (None,qfq,hfq)」，傳 Python None 或 "none" 同樣被拒），故不經 AuType 枚舉而直接傳值。
FUTU_AUTYPE = {"qfq": "qfq", "hfq": "hfq", "none": "None"}
FUTU_PAGE_MAX = 1000  # get_cur_kline 單次上限；此版本無分頁參數，更多 bar 需改用 request_history_kline

# get_acc_list 的 acc_type → 統一詞表（實測該欄為 CASH/MARGIN，與 trd_env 各自獨立）。
ACC_OF_ACC_TYPE = {"CASH": ACC_CASH, "MARGIN": ACC_MARGIN}


def _account_currency(acc: dict) -> str:
    """未指定幣種時的依據：accinfo_query 一定要傳幣種，故取該戶口首個授權市場的結算幣。

    實測 trdmarket_auth 為市場代碼的 list（['HK', 'US', 'HKCC', 'SG', 'HKFUND', 'USFUND', 'JP']），
    順序即富途的排序，故取首個能映射到結算幣的市場；基金市場（HKFUND/USFUND）與 HKCC 沒有結算幣
    映射，跳過不計。
    """
    for market in acc.get("trdmarket_auth") or []:
        try:
            return currency_of(market)
        except CodeError:
            continue
    raise ValueError(f"currency_undetermined: 戶口 {acc.get('acc_id')} 無授權市場，請傳 currency")


def _funds_of(item: dict, ccy: str) -> dict:
    """accinfo_query 的原生欄位 → 統一金額欄位。富途的總資產即淨資產值。"""
    return {
        "currency": str(item.get("currency") or ccy),
        "net_liquidation": item.get("total_assets"),
        "cash": item.get("cash"),
        "market_value": item.get("market_val"),
        "available_funds": item.get("available_funds"),
        "buying_power": item.get("power"),
        "init_margin": item.get("initial_margin"),
        "maint_margin": item.get("maintenance_margin"),
        "unrealized_pnl": item.get("unrealized_pl"),
        "realized_pnl": item.get("realized_pl"),
    }


class FutuBroker(SymbolBroker):
    """富途 OpenAPI 標的來源。"""

    source = "futu"
    capabilities = frozenset({CAP_STOCK, CAP_FUTURE, CAP_INDEX})
    autypes = tuple(FUTU_AUTYPE)
    # 富途的实时 K 線推送與 get_cur_kline 用同一組 ktype/autype，故支援範圍相同。
    stream_ktypes = tuple(FUTU_KTYPE)
    stream_autypes = tuple(FUTU_AUTYPE)
    # 四類品種的 K 線接口皆可用（期權需先有正股的期權行情權限；美股期貨與指數另受賬戶
    # 行情權限限制，缺權限時由上游返回「行情权限不足」）。
    kline_symbol_types = (STOCK, FUTURE, INDEX, OPTION)
    # 富途的 get_acc_list 以 acc_type 欄位表明現金或保證金戶口（實測 CASH/MARGIN 皆存在）。
    acc_types = (ACC_CASH, ACC_MARGIN)

    def __init__(self, host: str | None = None, port: int | None = None):
        settings = get_settings()
        self.host = host or settings.futu_host
        self.port = port or settings.futu_port
        self._ctx = None

    def connect(self) -> None:
        if self._ctx is not None:
            return
        # 此 SDK 版本的 SysConfig 不收 timeout，get_stock_basicinfo 亦無 timeout 參數，故網絡層
        # 無法定時；每個（市場, 類型）只發一次請求，無無界迴圈。
        self._ctx = futu.OpenQuoteContext(host=self.host, port=self.port)

    def close(self) -> None:
        if self._ctx is not None:
            self._ctx.close()
            self._ctx = None

    # ---------- 清單 ----------

    def list_stocks(self, markets: Iterable[str], *, raw: bool = False) -> list[dict]:
        """全市場股票與 ETF。markets 為統一市場前綴；raw 見 _codes。"""
        return self._codes(tuple(m.upper() for m in markets), STOCK_TYPES, raw=raw)

    def list_futures(self, seeds: Iterable, *, raw: bool = False) -> list[dict]:
        """按種子所涉市場列出全部期貨。

        富途按市場一次列舉，不認產品 root，故 seeds 只用於決定要訪問哪些市場。主連以
        `main`/`current`/`next`/`day` 後綴表示，個月份則為富途原生代碼。
        """
        return self._codes({seed.market.upper() for seed in seeds}, FUTURE_TYPES, raw=raw)

    def list_indices(self, seeds: Iterable, *, raw: bool = False) -> list[dict]:
        """按種子所涉市場列出全部指數。"""
        return self._codes({seed.market.upper() for seed in seeds}, INDEX_TYPES, raw=raw)

    # ---------- K 線 ----------

    def get_kline(self, code: str, ktype: str, count: int, autype: str, *, raw: bool = False) -> list[dict]:
        """按 bar 數取 K 線，返回按 ts 升序的最近 count 根。

        ≤1000 根用 get_cur_kline（富途原生的 bar 數接口，需先訂閱同類型 K 線）；此版本的
        get_cur_kline 無分頁參數，故更多時改用 request_history_kline，按日期範圍多取再分頁，
        最後截尾。bar 時間為交易所當地時間，統一換算成 UTC 秒以便與其它券商對齊。
        raw=True 時列為 get_cur_kline/request_history_kline 的原生欄位，排序與截尾改按原生
        time_key（同一格式的時間文字，升序即時間升序），取數範圍不變。
        """
        if ktype not in FUTU_KTYPE:
            raise CodeError(f"ktype_unsupported: {ktype}（可用：{'/'.join(FUTU_KTYPE)}）")
        if autype not in FUTU_AUTYPE:
            raise CodeError(f"autype_unsupported: {autype}（可用：{'/'.join(FUTU_AUTYPE)}）")
        market = parse_code(code).market
        self.connect()

        if count <= FUTU_PAGE_MAX:
            rows = self._kline_recent(code, market, ktype, count, autype, raw=raw)
        else:
            rows = self._kline_history(code, market, ktype, count, autype, raw=raw)
        rows.sort(key=lambda row: str(row.get("time_key", "")) if raw else row["ts"])
        return rows[-count:]

    def _kline_recent(self, code: str, market: str, ktype: str, count: int, autype: str,
                      raw: bool = False) -> list[dict]:
        ret, err = self._ctx.subscribe([code], [getattr(futu.SubType, FUTU_KTYPE[ktype])])
        if ret != 0:
            raise RuntimeError(f"upstream_error: subscribe {code} 失敗: {err}")
        ret, df = self._ctx.get_cur_kline(code, count, ktype=FUTU_KTYPE[ktype], autype=FUTU_AUTYPE[autype])
        if ret != 0:
            raise RuntimeError(f"upstream_error: get_cur_kline {code} 失敗: {df}")
        return self._kline_rows(code, market, ktype, df, raw=raw)

    def _kline_history(self, code: str, market: str, ktype: str, count: int, autype: str,
                       raw: bool = False) -> list[dict]:
        start = date.today() - timedelta(days=span_days(ktype, count))
        rows: list[dict] = []
        page = None
        while True:
            ret, df, page = self._ctx.request_history_kline(
                code,
                start=start.isoformat(),
                end=date.today().isoformat(),
                ktype=FUTU_KTYPE[ktype],
                autype=FUTU_AUTYPE[autype],
                max_count=FUTU_PAGE_MAX,
                page_req_key=page,
            )
            if ret != 0:
                raise RuntimeError(f"upstream_error: request_history_kline {code} 失敗: {df}")
            if df is None or df.empty:
                break
            rows.extend(self._kline_rows(code, market, ktype, df, raw=raw))
            if not page:
                break
        return rows

    def _kline_rows(self, code: str, market: str, ktype: str, df, raw: bool = False) -> list[dict]:
        if raw:
            return df.to_dict("records")
        return [self._to_kline_row(code, market, ktype, item) for item in df.itertuples()]

    def _to_kline_row(self, code: str, market: str, ktype: str, item) -> dict:
        time_key = str(item.time_key)
        return kline_row(
            code=code,
            ts=align_ts(to_utc(time_key, market), market, ktype, self.kline_anchor),
            time_key=time_key,
            open_=item.open,
            high=item.high,
            low=item.low,
            close=item.close,
            volume=item.volume,
            turnover=item.turnover,
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
        """串流多個代碼的最新 K 線，全部共用同一條富途連線。

        先以 get_cur_kline 取最近 count 根作起點（這一步同時完成訂閱），之後富途每次推送即更新
        最新一根（未走完的 bar 亦會持續推送），有變化才呼叫 on_update(code, rows)。回調在 SDK 的
        推送執行緒中發生。seconds 為持續秒數，0 表示直到 Ctrl-C。
        raw=True 時起點與推送一律為富途原生欄位，按原生 time_key 合併（見 NativeBars）。
        """
        if ktype not in FUTU_KTYPE:
            raise CodeError(f"ktype_unsupported: {ktype}（可用：{'/'.join(FUTU_KTYPE)}）")
        if autype not in FUTU_AUTYPE:
            raise CodeError(f"autype_unsupported: {autype}（可用：{'/'.join(FUTU_AUTYPE)}）")
        self.connect()

        markets = {code: parse_code(code).market for code in codes}
        mergers: dict[str, BarMerger] = {}
        for code in codes:
            seed = self._kline_recent(code, markets[code], ktype, min(count, FUTU_PAGE_MAX), autype, raw=raw)
            merger = NativeBars(count, "time_key") if raw else BarMerger(count)
            merger.merge(seed)
            mergers[code] = merger

        self._ctx.set_handler(_KlinePushHandler(self, ktype, markets, mergers, on_update, raw=raw))
        self._ctx.start()  # 對稱於結束時的 stop()；此 SDK 連線後預設已在接收推送
        try:
            stream_wait(seconds)
        finally:
            self._ctx.stop()
            self._ctx.unsubscribe(list(codes), [getattr(futu.SubType, FUTU_KTYPE[ktype])])
        return {code: mergers[code].frame() for code in codes}

    # ---------- 戶口 ----------

    def get_accounts(self, currency: str | None = None, *, raw: bool = False) -> list[dict]:
        """戶口清單與資金：get_acc_list 定戶口性質，accinfo_query 取該戶口的資金。

        只取 trd_env=REAL 且 acc_status=ACTIVE 的戶口：統一格式不再區分 real/simulate，模擬戶口的
        紙面資金不應混入真實資金；INACTIVE 為已停用的戶口（實測開過又取消的戶口即為 INACTIVE），
        既不可交易，accinfo_query 亦取不到資金。
        富途以 acc_type（CASH/MARGIN）表明戶口性質，原樣映射為統一的 acc_type。accinfo_query 必須
        傳幣種且沒有跨幣種匯總（實測其數字只屬該幣種，另有各幣種明細欄），故未指定 currency 時以
        該戶口首個授權市場的結算幣為準。富途以字串 "N/A" 表示無值，一律還原為 NaN；富途沒有的欄位
        （負債權益）亦為 NaN，不以任何數字湊出。
        raw=True 時每列為該戶口的原生記錄：get_acc_list 的各欄加上 accinfo_query 的各欄（每個所查
        幣種各一列），不做任何映射或換算；取數範圍（只取 REAL 且 ACTIVE 的戶口）不變。
        """
        ctx = futu.OpenSecTradeContext(
            filter_trdmarket=futu.TrdMarket.NONE,
            host=self.host,
            port=self.port,
            security_firm=futu.SecurityFirm.FUTUSECURITIES,
        )
        try:
            ret, listing = ctx.get_acc_list()
            if ret != 0:
                raise RuntimeError(f"get_acc_list: {listing}")
            rows: list[dict] = []
            errors: list[str] = []
            for acc in listing.to_dict("records"):
                if str(acc["trd_env"]) != "REAL" or str(acc["acc_status"]) != "ACTIVE":
                    continue
                item, ccy, error = self._acc_funds(ctx, acc, currency)
                if item is None:
                    errors.append(f"acc_id={acc['acc_id']}: {error}")
                    continue
                if raw:
                    rows.append({**acc, **item})
                    continue
                funds = _funds_of(item, ccy)
                rows.append(account_row(
                    source=self.source,
                    account_id=acc["acc_id"],
                    acc_type=ACC_OF_ACC_TYPE.get(str(acc["acc_type"]), str(acc["acc_type"]).lower()),
                    status=str(acc["acc_status"]),
                    currency=funds["currency"],
                    funds=funds,
                ))
            if not rows and errors:
                raise RuntimeError("accinfo_query: " + "；".join(errors))
            return rows
        finally:
            ctx.close()

    def _acc_funds(self, ctx, acc: dict, currency: str | None) -> tuple[dict | None, str, str]:
        """單一戶口的資金：返回 (accinfo_query 的原生單行, 所查幣種, 原因)。取不到時首項為 None。"""
        try:
            ccy = currency or _account_currency(acc)
        except ValueError as exc:
            return None, "", str(exc)
        ret, df = ctx.accinfo_query(
            trd_env=futu.TrdEnv.REAL,
            acc_id=acc["acc_id"],
            currency=ccy,
            refresh_cache=True,  # 不強制刷新時可能返回舊值（實測模擬戶口更會回報「此数据暂时还未准备好」）
        )
        if ret != 0 or df.empty:
            return None, ccy, str(df)
        return df.to_dict("records")[0], ccy, ""

    # ---------- 內部 ----------

    def _codes(self, markets: Iterable[str], type_names: tuple[str, ...], raw: bool = False) -> list[dict]:
        self.connect()
        rows: list[dict] = []
        for market in markets:
            futu_market = FUTU_MARKET.get(market)
            if futu_market is None:
                raise ValueError(f"market_unsupported: 富途不支援 {market}")
            for type_name in type_names:
                ret, df = self._ctx.get_stock_basicinfo(
                    futu_market, stock_type=getattr(futu.SecurityType, type_name)
                )
                if ret != 0:
                    if UNSUPPORTED_HINT in str(df):
                        continue
                    raise RuntimeError(
                        f"upstream_error: get_stock_basicinfo {market}/{type_name} 失敗: {df}"
                    )
                if raw:
                    rows.extend(df.to_dict("records"))
                    continue
                rows.extend(self._to_row(market, type_name, item) for item in df.itertuples())
        return rows

    @staticmethod
    def _venue(exchange_type: str) -> str:
        """富途 exchange_type 形如 US_NASDAQ / HK_HKEX；市場已是獨立欄位，故只留場所含義。"""
        return exchange_type.split("_", 1)[1] if "_" in exchange_type else ""

    def _to_row(self, market: str, type_name: str, item) -> dict:
        code = getattr(item, "code", "")
        symbol = code.split(".", 1)[1] if "." in code else code
        return self.make_row(
            code=code,
            name=getattr(item, "name", ""),
            market=market,
            symbol=symbol,
            symbol_type=TYPE_OF[type_name],
            currency=currency_of(market),
            exchange=self._venue(str(getattr(item, "exchange_type", "") or "")),
        )


class _KlinePushHandler(futu.CurKlineHandlerBase):
    """把富途推送的 K 線轉成統一列並交回各代碼的合併器。

    回調在 SDK 的獨立執行緒中執行。同一連線亦可能收到其他 ktype 的推送（get_kline 同樣會訂閱），
    故只處理本次串流所訂閱的 k_type；推送未帶代碼或代碼不在本次串流範圍時一併忽略。
    raw=True 時不做任何轉換，各代碼的合併器為 NativeBars（按原生 time_key 合併）。
    """

    def __init__(self, broker: FutuBroker, ktype: str, markets: dict, mergers: dict, on_update,
                 raw: bool = False):
        super().__init__()  # SDK 的 RspHandlerBase.__del__ 依賴其 __init__ 建立的屬性
        self._broker = broker
        self._ktype = ktype  # 統一 ktype，供 _to_kline_row 的週期對齊使用
        self._push_type = FUTU_KTYPE[ktype]  # 推送帶 k_type 欄，需按此過濾（同一連線可能有多種 ktype）
        self._markets = markets
        self._mergers = mergers
        self._on_update = on_update
        self._raw = raw

    def on_recv_rsp(self, rsp_pb):
        ret, df = super().on_recv_rsp(rsp_pb)
        if ret != futu.RET_OK:
            return ret, df
        if self._raw:
            grouped: dict[str, list[dict]] = {}
            for row in df.to_dict("records"):
                if row.get("k_type") == self._push_type and row.get("code") in self._mergers:
                    grouped.setdefault(str(row["code"]), []).append(row)
            for code, rows in grouped.items():
                if self._mergers[code].merge(rows) and self._on_update is not None:
                    self._on_update(code, self._mergers[code].frame())
            return futu.RET_OK, None
        for item in df.itertuples():
            merger = self._mergers.get(item.code)
            if merger is None or item.k_type != self._push_type:
                continue
            row = self._broker._to_kline_row(
                item.code, self._markets[item.code], self._ktype, item
            )
            if merger.merge([row]) and self._on_update is not None:
                self._on_update(item.code, merger.frame())
        return futu.RET_OK, None
