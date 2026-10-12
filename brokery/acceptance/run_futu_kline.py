"""富途 K 線的取數策略：請求的根數只由該標的在該週期的可取深度決定，與取數路徑無關。

以腳本方式直接執行：python brokery/acceptance/run_futu_kline.py

實測 get_cur_kline 對多數週期只給最近幾十根（傳 1000 時 5m/30m/60m/day/week/month 只回 60 根，
只有 1m/15m 給足），故 bar 數不能只靠該接口：不足時要補 request_history_kline，去重合併後截尾。
本腳本以存根 _ctx 重現上游的三種行為（快路徑只給幾十根、按日期範圍分頁給足、起日過早即回報
「F3CNN返回錯誤」），全程不連 OpenD，因此驗的是取數策略本身，不受行情權限或連線狀態影響。
"""
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import pandas as pd

from brokery import Brokery, core
from brokery.brokers.base import TIME_TEXT, span_days
from brokery.brokers.futu_broker import FUTU_KTYPE, HISTORY_MIN_SPAN_DAYS, FutuBroker

CODE = "HK.HSImain"
REJECT_TEXT = "F3CNN返回錯誤，可能是參數錯誤或者斷線"
# 生成 bar 的步長，只用於構造時間序列，與真實交易時段無關。
BAR_STEP = {"1m": timedelta(minutes=1), "3m": timedelta(minutes=3), "5m": timedelta(minutes=5),
            "15m": timedelta(minutes=15), "30m": timedelta(minutes=30), "60m": timedelta(minutes=60),
            "day": timedelta(days=1), "week": timedelta(weeks=1), "month": timedelta(days=31)}
# 存根只收得到上游的 ktype 名稱（適配器傳的是 FUTU_KTYPE 的值），故以該名稱索引步長。
STEP = {name: BAR_STEP[ktype] for ktype, name in FUTU_KTYPE.items()}
NATIVE = ("time_key", "open", "high", "low", "close", "volume", "turnover")


class StubCtx:
    """假 OpenQuoteContext：快路徑只給 recent 根，歷史按日期範圍分頁給足，起日過早即拒。

    兩段用同一個回溯生成器（以今天 16:00 為最後一根），故必然重疊，重疊部分正可用來驗去重。
    收盤價以 close 標記區分：快路徑為 1.0（最新狀態）、歷史為 2.0（較舊狀態）。
    """

    def __init__(self, *, recent: int = 60, depth: int = 100_000, reject_span: int | None = None):
        self.recent = recent            # get_cur_kline 實際返回的根數（可遠少於傳入的 num）
        self.depth = depth              # 該標的在該週期實際可取的最大根數
        self.reject_span = reject_span  # 起日與今日相距超過此日數即拒（重現 F3CNN 錯誤）
        self.cur_calls: list[int] = []      # get_cur_kline 收到的 num
        self.history_calls: list[int] = []  # request_history_kline 收到的日曆跨度
        self.served = 0                 # 最近一次歷史請求實際返回的根數

    def close(self) -> None:
        pass

    def subscribe(self, codes, sub_types):
        return 0, ""

    def get_cur_kline(self, code, num, ktype=None, autype=None):
        self.cur_calls.append(num)
        return 0, self._frame(self._bars(ktype, date.today(), min(num, self.recent)), 1.0)

    def request_history_kline(self, code, start=None, end=None, ktype=None, autype=None,
                             max_count=None, page_req_key=None):
        today = date.today()
        span = (today - date.fromisoformat(start)).days
        self.history_calls.append(span)
        if self.reject_span is not None and span > self.reject_span:
            return 1, f"{REJECT_TEXT}（起日 {start}）", None
        stop = datetime(today.year, today.month, today.day, 16, 0)
        want = int((stop - datetime.fromisoformat(start)).total_seconds() // STEP[ktype].total_seconds()) + 1
        rows = self._bars(ktype, today, min(want, self.depth))
        self.served = len(rows)
        at = int(page_req_key) if page_req_key else 0
        return 0, self._frame(rows[at:at + max_count], 2.0), \
            str(at + max_count) if at + max_count < len(rows) else None

    @staticmethod
    def _bars(ktype: str, end: date, n: int) -> list[dict]:
        """以 end 當日 16:00 為最後一根，按 ktype 步長回溯 n 根（升序返回）。"""
        moment, rows = datetime(end.year, end.month, end.day, 16, 0), []
        for _ in range(max(0, n)):
            rows.append({"time_key": moment.strftime(TIME_TEXT)})
            moment -= STEP[ktype]
        return list(reversed(rows))

    @staticmethod
    def _frame(rows: list[dict], close: float) -> pd.DataFrame:
        for row in rows:
            row.update(open=close, high=close, low=close, close=close, volume=1, turnover=1)
        return pd.DataFrame(rows, columns=list(NATIVE))


def stubbed(**kw) -> tuple[FutuBroker, StubCtx]:
    """帶存根連線的適配器：connect() 見 _ctx 已存在即直接返回，故全程不連 OpenD。"""
    ctx = StubCtx(**kw)
    broker = FutuBroker()
    broker._ctx = ctx
    return broker, ctx


def main() -> dict:
    checks: list[tuple[str, bool, str]] = []

    def check(label: str, passed: bool, detail: str = "") -> None:
        checks.append((label, bool(passed), detail))

    def ascending(rows: list[dict]) -> bool:
        ts = [row["ts"] for row in rows]
        return all(a < b for a, b in zip(ts, ts[1:]))

    # ① 各週期一致：快路徑只給幾十根時補歷史，取足請求的根數（用戶所見「根數與週期不符」即出於此）
    for ktype in ("1m", "5m", "15m", "30m", "60m", "day"):
        broker, ctx = stubbed(recent=60)
        rows = broker.get_kline(CODE, ktype, 1000, "qfq")
        check(f"{ktype} 傳 1000 根即得 1000 根（快路徑只得 {ctx.recent} 根亦會補歷史）",
              len(rows) == 1000 and ascending(rows),
              f"cur={ctx.cur_calls}|歷史嘗試 {len(ctx.history_calls)} 次|{len(rows)} 根")

    # ② 兩段去重合併：重疊部分只出現一次，且以快路徑者為準（其價格為最新狀態）
    broker, ctx = stubbed(recent=60)
    rows = broker.get_kline(CODE, "5m", 1000, "qfq")
    closes = [row["close"] for row in rows]
    check("快路徑與歷史重疊的 bar 不會出現兩次，且同一根以快路徑的最新狀態為準",
          len(rows) == 1000 and ascending(rows) and closes == [2.0] * 940 + [1.0] * 60,
          f"唯一 ts {len({row['ts'] for row in rows})} 個|尾部收盤 {sorted(set(closes[-60:]))}")

    # ③ 多於單次上限即不走快路徑，直接按日期範圍分頁取足
    broker, ctx = stubbed(recent=60)
    rows = broker.get_kline(CODE, "1m", 3000, "qfq")
    check("請求根數多於單次上限時不再調用 get_cur_kline，改按日期範圍分頁取足（根數可任選數字）",
          ctx.cur_calls == [] and len(rows) == 3000 and ascending(rows),
          f"cur={ctx.cur_calls}|歷史 {len(ctx.history_calls)} 次|{len(rows)} 根")

    # ④ 起日過早被上游拒：把跨度折半重試，而不是直接報錯或靜靜少返
    first = span_days("day", 1000)
    accepted = max(first // 2, HISTORY_MIN_SPAN_DAYS)
    broker, ctx = stubbed(recent=60, reject_span=first - 1)
    rows = broker.get_kline(CODE, "day", 1000, "qfq")
    check("起日過早被上游拒時把跨度折半重試並取到該窗口可取的深度（只重試一次，不無限重試）",
          ctx.history_calls == [first, accepted] and len(rows) == ctx.served and ascending(rows),
          f"跨度序列={ctx.history_calls}|返回 {len(rows)} 根（該窗口可取 {ctx.served} 根）")

    # ⑤ 折半至下限仍被拒：明確抛出，不把只有幾十根的結果當成功
    broker, ctx = stubbed(recent=60, depth=2000, reject_span=HISTORY_MIN_SPAN_DAYS - 1)
    try:
        broker.get_kline(CODE, "day", 1000, "qfq")
        check("起日折半至下限（一年）仍被上游拒時明確抛出，不靜靜少返", False, "沒有抛出")
    except RuntimeError as exc:
        check("起日折半至下限（一年）仍被上游拒時明確抛出，不靜靜少返",
              str(exc).startswith("upstream_error: request_history_kline")
              and ctx.history_calls[-1] == HISTORY_MIN_SPAN_DAYS,
              f"跨度序列={ctx.history_calls}|{exc}")

    # ⑥ 深度不足請求數：返回實際深度，不虛構 bar
    broker, ctx = stubbed(recent=0, depth=257)
    rows = broker.get_kline(CODE, "month", 1000, "qfq")
    check("該標的在該週期的可取深度不足請求數時返回實際深度，不虛構 bar",
          len(rows) == 257 and ascending(rows), f"{len(rows)} 根（請求 1000 根）")

    # ⑦ core 層：深度不足時在 message 點名該來源的實際深度（界面與调用方不會被靜靜少返矇住）
    class DepthFutu(FutuBroker):
        source = "futudepth"

    core.BROKERS["futudepth"] = DepthFutu
    try:
        with Brokery(sources=("futudepth",)) as b:
            b._brokers["futudepth"]._ctx = StubCtx(recent=0, depth=257)
            result = b.get_kline(CODE, ktype="month", count=1000, broker="futudepth")
        check("深度不足時 core 仍返回成功，但 message 點名該來源該週期的實際深度",
              result["status"] and len(result["data"]) == 257
              and "futudepth 的 month 深度只有 257 根（請求 1000 根）" in result["message"],
              result["message"])
    finally:
        core.BROKERS.pop("futudepth", None)

    # ⑧ raw=True：排序與截尾改按原生 time_key，欄位原樣交回
    broker, ctx = stubbed(recent=60)
    rows = broker.get_kline(CODE, "5m", 1000, "qfq", raw=True)
    keys = [row["time_key"] for row in rows]
    check("raw=True 時以原生 time_key 排序與截尾，欄位原樣交回",
          len(rows) == 1000 and set(rows[0]) >= set(NATIVE) and keys == sorted(keys),
          f"{len(rows)} 根|欄位={sorted(rows[0]) if rows else '空'}")

    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）")
    failed = [label for label, passed, _ in checks if not passed]
    if failed:
        return {"status": False, "data": pd.DataFrame(), "message": "失敗：" + "；".join(failed)}
    return {"status": True, "data": pd.DataFrame(),
            "message": f"{len(checks)} 項檢查全過：富途取数以存根 _ctx 驗證，根數只受實際可取深度限制"
                       f"（各週期傳 1000 根皆得 1000 根，深度不足時點名實際深度）"}


if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] else 1)
