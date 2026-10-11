"""券商適配器的共同契約與統一輸出欄位。

各券商的返回在此統一為同一組欄位，且 code 一律為統一代碼（見 codes 模組）。新增券商
時只需實作本介面並聲明自身能力，不得改動欄位語義。

每個取數方法都帶 keyword-only 的 raw 參數：raw=True 時返回該券商原生的欄位與格式（字典的鍵即
上游自己的欄位名，值不做換算或歸類），取數範圍則與 raw=False 相同。欄位契約只約束 raw=False。
"""
from __future__ import annotations

import math
import time
from abc import ABC
from collections.abc import Iterable
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from ..codes import FUTURE, INDEX, STOCK, is_secondary_exchange

# 統一輸出欄位。code 為統一代碼；期貨的到期月已含在 symbol 內（如 US.ES202612、SG.CNmain），故不
# 另設到期月欄；券商原生標識屬 raw=True 的原生格式，統一格式不重複承載。欄位與順序對所有券商
# 一律相同；該券商沒有這個概念者一律留空字串（例如 Tiger 的股票清單唔附帶 exchange），嚴禁為
# 湊齊欄位而造數。
COLUMNS = [
    "code",
    "name",
    "market",
    "symbol",
    "symbol_type",
    "currency",
    "exchange",
    "source",
]

# 統一 K 線欄位（格式以富途為準）。ts 為 UTC 秒，是跨券商對齊鍵（週/月 bar 一律歸到所屬週期
# 起點，見 align_ts）；time_key 保留券商原生的 bar 時間（交易所當地時間）。IB 不提供成交額，
# 該欄為 NaN。
K_COLUMNS = [
    "code",
    "ts",
    "time_key",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "turnover",
    "source",
]

# 統一戶口欄位。只以 acc_type 區分戶口性質（cash/margin）；不再區分戶口環境（real/simulate），
# 各適配器一律只返回真實戶口（IB 的真實與模擬由所連 Gateway 決定，本身沒有這個維度；富途與
# Tiger 的模擬戶口因此不列入）。金額一律以 currency 所示幣種計，各券商以其原生匯總幣種為準，
# 不做匯率換算（嚴禁為湊齊而造數）；該券商沒有對應欄位者為 NaN，例如 Webull 無淨資產匯總。
ACCOUNT_COLUMNS = [
    "source",
    "account_id",
    "acc_type",
    "status",
    "currency",
    "net_liquidation",
    "cash",
    "market_value",
    "available_funds",
    "buying_power",
    "init_margin",
    "maint_margin",
    "equity_with_loan",
    "unrealized_pnl",
    "realized_pnl",
]

# 戶口性質的統一詞表。各券商的原生寫法由適配器映射到此處（富途 acc_type、Tiger capability、
# Webull account_type（MRGN）、IB AccountType）。無法判斷的寫法一律原樣返回，不憑空歸類。
ACC_CASH, ACC_MARGIN = "cash", "margin"

# 統一券商連線狀態欄位。connected 為該次探測成敗；latency_ms 為探測往返毫秒數，探測失敗時為 NaN
# （不以任何數字湊出）；accounts 為該次讀到的戶口數；detail 為失敗原因或空字串；checked_at 為
# 探測完成的 UTC 秒。探測以一次戶口查詢進行，故同時驗證連線與鑑權，且不需要行情數據權限。
BROKER_COLUMNS = ["source", "connected", "latency_ms", "accounts", "detail", "checked_at"]

# 統一 ktype 詞表 → 每根 bar 的分鐘數。日/周/月以分鐘計，方便 IB 由 bar 數換算時間跨度。
BAR_MINUTES = {
    "1m": 1,
    "3m": 3,
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "60m": 60,
    "day": 1440,
    "week": 7 * 1440,
    "month": 30 * 1440,
}

# 交易所當地時區。富途的 time_key 為裸字串，IB formatDate=2 在無 mapping 時亦可能返回裸
# datetime，故一律按市場時區解釋後再換算 UTC。
MARKET_TZ = {
    "HK": "Asia/Hong_Kong",
    "US": "America/New_York",
    "SH": "Asia/Shanghai",
    "SZ": "Asia/Shanghai",
    "SG": "Asia/Singapore",
    "JP": "Asia/Tokyo",
    "MY": "Asia/Kuala_Lumpur",
    "AU": "Australia/Sydney",
    "CA": "America/Toronto",
}

# 由 bar 數反推日曆跨度。一年的交易日遠少於 365 日（實測取 1200 根港股日線，按 365/252 放大
# 仍只回 1178 根，差额正是假期；港股實際約 244 個交易日），故以各市場都偏低的 240 換算，確保
# 跨度不會不足；日內 bar 先按每個交易日的有效分鐘數換算成交易日，取港股的 330 分鐘（較美股
# 390 保守）。另加固定天數緩衝兜住邊界。一律刻意多取，多出的部分由呼叫端截尾。
TRADING_DAYS_PER_YEAR = 240
MINUTES_PER_TRADING_DAY = 330
HOLIDAY_BUFFER_DAYS = 15
DAYS_PER_WEEK = 7
DAYS_PER_MONTH = 31


def span_days(ktype: str, count: int) -> int:
    """bar 數 → 足以容納該數量的日曆跨度（刻意多取，多出的部分由呼叫端截尾）。"""
    if ktype == "week":  # 每週一根，日曆跨度即 bar 數 × 7
        days = count * DAYS_PER_WEEK
    elif ktype == "month":
        days = count * DAYS_PER_MONTH
    elif ktype == "day":
        days = _calendar_days(count)
    else:
        days = _calendar_days(count * BAR_MINUTES[ktype] / MINUTES_PER_TRADING_DAY)
    return max(1, days + HOLIDAY_BUFFER_DAYS)


def _calendar_days(trading_days: float) -> int:
    """交易日 → 日曆天數（按 365/TRADING_DAYS_PER_YEAR 放大）。"""
    return int(trading_days * 365 / TRADING_DAYS_PER_YEAR)


# 帶時區偏移者（Webull 的 bar 時間為 ISO 8601，如 2026-10-08T16:00:00.000+0000）按其自身偏移換算，
# 不屬下列格式者仍按市場時區解釋（見 _aware）。
_TIME_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
    "%Y-%m-%dT%H:%M:%S.%f%z",
    "%Y-%m-%dT%H:%M:%S%z",
)
TIME_TEXT = "%Y-%m-%d %H:%M:%S"


def _zone(market: str) -> ZoneInfo:
    zone = MARKET_TZ.get(market.upper())
    if zone is None:
        raise ValueError(f"market_tz_unknown: {market}")
    return ZoneInfo(zone)


def _aware(value, market: str) -> datetime:
    """把券商回傳的 bar 時間解析為帶時區的 datetime；裸時間按市場時區解釋。"""
    if isinstance(value, str):
        parsed = None
        for fmt in _TIME_FORMATS:
            try:
                parsed = datetime.strptime(value.strip(), fmt)
                break
            except ValueError:
                continue
        if parsed is None:
            raise ValueError(f"bad_time_key: {value!r}")
        value = parsed
    if isinstance(value, date) and not isinstance(value, datetime):
        value = datetime(value.year, value.month, value.day)  # IB 對日/周/月 bar 只返回 date
    return value.replace(tzinfo=_zone(market)) if value.tzinfo is None else value


def to_utc(value, market: str) -> int:
    """把券商回傳的 bar 時間統一為 UTC 秒；帶時區者直接換算，裸時間按市場時區解釋。"""
    return int(_aware(value, market).astimezone(timezone.utc).timestamp())


def to_local_text(value, market: str) -> str:
    """把券商回傳的 bar 時間統一為交易所當地的時間文字，使各券商的 time_key 格式一致。"""
    return _aware(value, market).astimezone(_zone(market)).strftime(TIME_TEXT)


# 非日內 bar 的錨點：以週期起點或終點作為 bar 時間。各券商做法不同，須由適配器聲明。
ANCHOR_START = "start"
ANCHOR_END = "end"


def align_ts(ts: int, market: str, ktype: str, anchor: str = ANCHOR_START) -> int:
    """把週/月 bar 的對齊鍵歸到所屬週期的起點（當地時間）。

    各券商對非日內 bar 的錨點不同（實測富途週線以週一、月線以每月一日；IB 週線以週六、月線
    以下月一日，當期未走完則以今日），兩家的 OHLC 卻完全相同，故必須先按錨點還原到週期內的一
    刻，再取該週期的起點，否則跨券商會錯開一個週期。日內與日線各券商本來一致，原樣返回。
    time_key 仍保留券商原生時間，以便回溯核對。
    """
    if ktype not in ("week", "month"):
        return int(ts)
    local = datetime.fromtimestamp(int(ts), _zone(market))
    if anchor == ANCHOR_END:
        local -= timedelta(seconds=1)  # 終點本身不屬該週期，退一秒才落在週期內
    if ktype == "week":
        local -= timedelta(days=local.weekday())
    else:
        local = local.replace(day=1)
    return int(local.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())


def kline_row(
    code: str,
    ts: int,
    time_key: str,
    open_: float,
    high: float,
    low: float,
    close: float,
    volume: float,
    turnover: float,
    source: str,
) -> dict:
    """依統一 K 線欄位順序構造一列。"""
    return {
        "code": code,
        "ts": int(ts),
        "time_key": time_key,
        "open": float(open_),
        "high": float(high),
        "low": float(low),
        "close": float(close),
        "volume": float(volume),
        "turnover": float(turnover),
        "source": source,
    }


def account_num(value) -> float:
    """券商的金額欄位統一為 float；無值一律為 NaN。

    兩家的缺失寫法不同（實測富途 accinfo_query 以字串 "N/A" 表示無值、Tiger 的 Account 以 inf
    表示該幣種無此項），直接返回會把「無資料」當成 0 或 inf，故一律還原為 NaN。
    """
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return number if math.isfinite(number) else float("nan")


def account_row(
    source: str,
    account_id,
    acc_type: str,
    status: str,
    currency: str,
    funds: dict | None = None,
) -> dict:
    """依統一戶口欄位順序構造一列。funds 只填該券商有的金額欄位，其餘為 NaN（不假造）。"""
    row = {
        "source": source,
        "account_id": str(account_id),
        "acc_type": acc_type,
        "status": status,
        "currency": currency,
    }
    for column in ACCOUNT_COLUMNS:
        if column not in row:
            row[column] = account_num((funds or {}).get(column))
    return row


class BarMerger:
    """按 ts 合併各券商推送的 bar，只保留最近 count 根，並判斷最新一根有否變化。

    兩家的推送粒度不同（富途推整根 K 線、IB 直接更新同一個 bar 序列），但對外語義必須一致：
    呼叫端只会收到按 ts 升序、不超過 count 根的完整結果，而且同一幀不會重複送。
    """

    def __init__(self, count: int):
        self._count = count
        self._rows: dict[int, dict] = {}
        self._signature: tuple | None = None

    def merge(self, rows: Iterable[dict]) -> bool:
        """合併新到的 bar，返回最新一根是否新出現或有變化。"""
        for row in rows:
            self._rows[int(row["ts"])] = row
        if len(self._rows) > self._count:
            for ts in sorted(self._rows)[: -self._count]:
                del self._rows[ts]
        if not self._rows:
            return False
        newest = self._rows[max(self._rows)]
        signature = (newest["ts"], newest["open"], newest["high"], newest["low"],
                     newest["close"], newest["volume"])
        if signature == self._signature:
            return False
        self._signature = signature
        return True

    def frame(self) -> list[dict]:
        """目前這一段 bar（按 ts 升序）。"""
        return [self._rows[ts] for ts in sorted(self._rows)]


def _bar_sort_key(value) -> tuple:
    """原生時間欄位可能是 epoch 數或時間文字，兩者不可直接比較，故數字與文字各自成組排序。"""
    if isinstance(value, (int, float)):
        return (0, float(value), "")
    return (1, 0.0, str(value))


class NativeBars:
    """按券商原生的時間欄位合併推送的 bar，只保留最近 count 根。

    對外語義與 BarMerger 一致（只在最新一根有變化時回呼，且每次送不超過 count 根的完整結果），
    差別只在欄位與值一律為上游原樣：不做時間換算，亦不按統一週期歸併。時間欄位的名稱由各券商
    聲明（富途 time_key、Tiger time、Webull time、IB date）。
    """

    def __init__(self, count: int, time_field: str):
        self._count = count
        self._time_field = time_field
        self._rows: dict[object, dict] = {}
        self._signature: tuple | None = None

    def merge(self, rows: Iterable[dict]) -> bool:
        """合併新到的 bar，返回最新一根是否新出現或有變化。"""
        for row in rows:
            self._rows[row.get(self._time_field)] = row
        if len(self._rows) > self._count:
            for key in sorted(self._rows, key=_bar_sort_key)[: -self._count]:
                del self._rows[key]
        if not self._rows:
            return False
        newest = self._rows[max(self._rows, key=_bar_sort_key)]
        signature = tuple(str(value) for value in newest.values())
        if signature == self._signature:
            return False
        self._signature = signature
        return True

    def frame(self) -> list[dict]:
        """目前這一段 bar（按原生時間升序）。"""
        return [self._rows[key] for key in sorted(self._rows, key=_bar_sort_key)]


def stream_wait(seconds: float) -> None:
    """串流期間的等待：seconds 為 0 時直到 Ctrl-C。

    兩家的推送都在各自的後台執行緒到達，呼叫端只負責計時，故以短間隔輪詢，使 Ctrl-C 能及時
    返回；按 Ctrl-C 屬正常結束，不抛出。
    """
    deadline = time.monotonic() + seconds if seconds > 0 else None
    try:
        while deadline is None or time.monotonic() < deadline:
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass


CAP_STOCK = STOCK
CAP_FUTURE = FUTURE
CAP_INDEX = INDEX


class SymbolBroker(ABC):
    """單一券商的標的來源。不支援的能力不實作，由 core 依 capabilities 跳過。"""

    source = ""
    capabilities: frozenset[str] = frozenset()
    # 非日內 bar 以週期起點還是終點為 bar 時間，供 align_ts 還原週期起點（見 align_ts 說明）。
    kline_anchor = ANCHOR_START
    # 支援的複權模式（qfq/hfq/none）。不支援的模式由 core 明確拒绝，嚴禁靜靜改用另一種價格返回。
    autypes: tuple[str, ...] = ()
    # 可串流（推送）的 ktype 與該情況下的複權模式。串流的支援範圍通常比歷史查詢窄（實測 IB 的
    # keepUpToDate 不接受 ADJUSTED_LAST），故獨立聲明，不支持時由 core 在開始前就明確拒绝。
    stream_ktypes: tuple[str, ...] = ()
    stream_autypes: tuple[str, ...] = ()
    # 可取 K 線的品種（見 codes.classify_symbol）。預設只聲明股票，各適配器按實測結果擴寬；
    # 未聲明的品種由 core 明確拒绝，嚴禁把期權或指數當股票送進上游等它報錯。
    kline_symbol_types: tuple[str, ...] = (STOCK,)
    # 可返回的戶口性質（cash/margin）。未聲明的值由 core 明確拒绝，嚴禁把券商沒有的戶口憑空
    # 造出來。一律只返回真實且可用的戶口（模擬戶口與已停用戶口不列入）。
    acc_types: tuple[str, ...] = ()

    def connect(self) -> None:
        """建立與後端的連線。以每次呼叫自行管理連線的後端可沿用預設空實作。"""

    def close(self) -> None:
        """釋放連線資源。以每次呼叫自行管理連線的後端可沿用預設空實作。"""

    def supports(self, symbol_type: str) -> bool:
        return symbol_type in self.capabilities

    def supports_kline(self, symbol_type: str) -> bool:
        return symbol_type in self.kline_symbol_types

    def list_stocks(self, markets: Iterable[str], *, raw: bool = False) -> list[dict]:
        raise NotImplementedError(f"{self.source} 不提供股票清單")

    def list_futures(self, seeds: Iterable, *, raw: bool = False) -> list[dict]:
        raise NotImplementedError(f"{self.source} 不提供期貨清單")

    def list_indices(self, seeds: Iterable, *, raw: bool = False) -> list[dict]:
        raise NotImplementedError(f"{self.source} 不提供指數清單")

    def to_contract(self, code: str) -> dict:
        raise NotImplementedError(f"{self.source} 不提供代碼轉換")

    def get_kline(self, code: str, ktype: str, count: int, autype: str, *, raw: bool = False) -> list[dict]:
        """取 K 線。count 為 bar 數（以富途語義為準），各適配器自行換算成自身的時間參數。"""
        raise NotImplementedError(f"{self.source} 不提供 K 線")

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
        """串流多個代碼的最新 K 線，全部共用同一條連線（對應多張圖同時顯示）。

        先以歷史 bar 作起點，之後最新一根每次出現或變化即呼叫 on_update(code, rows)，rows 為該
        代碼按 ts 升序、不超過 count 根的完整結果。seconds 為持續秒數（0 表示直到 Ctrl-C）。
        返回各代碼最終的 bar 列表。raw=True 時 rows 為該券商原生的欄位與格式，但合併與回呼的
        語義不變（仍為按原生時間升序、不超過 count 根的完整結果）。
        """
        raise NotImplementedError(f"{self.source} 不提供 K 線串流")

    def get_accounts(self, currency: str | None = None, *, raw: bool = False) -> list[dict]:
        """取該券商的戶口清單與資金。只返回真實且已啟用的戶口；currency 為指定幣種，
        不指定時以券商原生匯總幣種為準。"""
        raise NotImplementedError(f"{self.source} 不提供戶口資料")

    def make_row(
        self,
        code: str,
        name: str,
        market: str,
        symbol: str,
        symbol_type: str,
        currency: str,
        exchange: str,
    ) -> dict:
        """依統一欄位順序構造一列，避免各適配器各自拼字典。"""
        return {
            "code": code,
            "name": name,
            "market": market,
            "symbol": symbol,
            "symbol_type": symbol_type,
            "currency": currency,
            "exchange": exchange,
            "source": self.source,
        }


def native_columns(rows: list[dict]) -> list[str]:
    """原生欄位順序：按各列鍵出現的先後合併。

    字典保持插入順序，而各列的鍵順序由適配器代碼決定，故同一份數據的重複呼叫必得同一順序
    （欄位順序不受該列有否缺值影響）。
    """
    columns: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                columns.append(key)
    return columns


def dedupe_rows(rows: list[dict]) -> list[dict]:
    """同一合約在多處掛牌時只保留一列，主場優先於次要場所。

    合約身份即統一代碼（market + symbol）；期貨的到期月已含在 symbol 內，故不同到期月的合約不會
    被合併為一列。
    """
    best: dict[tuple, dict] = {}
    for row in rows:
        key = (row["market"], row["symbol_type"], row["symbol"])
        current = best.get(key)
        if current is None or (is_secondary_exchange(current["exchange"]) and not is_secondary_exchange(row["exchange"])):
            best[key] = row
    return list(best.values())
