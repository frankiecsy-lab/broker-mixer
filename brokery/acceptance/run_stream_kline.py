"""驗收 `Brokery.stream_kline`：一條連線同時串流多個代碼（對應同時顯示多張 K 線圖），核對各家
均返回統一格式、每次回呼的 bar 數受 count 限制、持續時間受 seconds 約束，以及券商不支持的串流
複權模式在開始前就明確報錯。

對外的回呼語義一致，但底層方式不同：富途、IB、Tiger 為推送，Webull 沒有 K 線推送故以輪詢批量
bar 接口湊出同樣的「最新一根有變化即回呼」。

休市時段不會有推送（實測星期六各家均為 0 次），故只對回呼的規格作斷言：有推送時每一幀必須合
規格，無推送時不計失敗。

各家的驗收代碼會按其憑證實際開通的市場過濾（見 MARKETS），未開通的市場不計失敗，只打印 WARN 指出
未驗收，避免把賬戶的行情權限問題誤當為代碼錯誤。

以腳本方式直接執行：
    python brokery/acceptance/run_stream_kline.py                        # 預設 HK.00005,HK.00700,US.NVDA，1m × 30 根，60 秒
    python brokery/acceptance/run_stream_kline.py US.NVDA 5m 50 120     # 指定代碼（逗號分隔可多個）/ ktype / bar 數 / 秒數
    python brokery/acceptance/run_stream_kline.py US.NVDA 1m 30 0       # 持續到 Ctrl-C
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import pandas as pd

from brokery import Brokery
from brokery.brokers.base import K_COLUMNS

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 220)

DEFAULT_CODES = ("HK.00005", "HK.00700", "US.NVDA")
DEFAULT_KTYPE = "1m"
DEFAULT_COUNT = 30
DEFAULT_SECONDS = 60.0
BROKERS = ("futu", "ib", "tiger", "webull")
# 串流不支持復權的券商（IB 的 keepUpToDate 不接受 ADJUSTED_LAST、Tiger 的推送為原始成交價、Webull
# 沒有 K 線推送故以輪詢分鐘 bar 實現，而分鐘線只返回不復權價），以 autype=qfq 驗證明確報錯。
REFUSE_QFQ = ("ib", "tiger", "webull")
# 各券商憑證實際開通行情的市場。Webull 的 app key 註冊於 HK 區域，實測取美股一律返回
# 403 MARKET_DATA_NOT_SUBSCRIBED（該市場未開通行情），故只以 HK 代碼驗收其串流。
MARKETS = {"webull": ("HK",)}


def _codes_for(broker: str, codes: tuple[str, ...]) -> tuple[str, ...]:
    """按該券商憑證實際開通的市場過濾驗收代碼，無可驗收的代碼即跳過該家。"""
    markets = MARKETS.get(broker)
    return tuple(c for c in codes if c.split(".", 1)[0] in markets) if markets else codes


def _handler(broker: str, counter: dict, bad: list[str], count: int):
    """每次推送打印最新一根，並核對回呼內容本身合規格（升序、不重複、不超過 count 根）。"""

    def on_update(code: str, rows: list[dict]) -> None:
        counter[code] = counter.get(code, 0) + 1
        ts = [row["ts"] for row in rows]
        if len(rows) > count or any(a >= b for a, b in zip(ts, ts[1:])):
            bad.append(f"{broker}/{code} 第{counter[code]}次回呼不合規格（{len(rows)} 根）")
        last = rows[-1]
        print(f"  [{broker}] 推送 {code} 第{counter[code]}次 共{len(rows)}根 "
              f"最新={last['time_key']} 收={last['close']} 量={last['volume']}", flush=True)

    return on_update


def main(codes=DEFAULT_CODES, ktype: str = DEFAULT_KTYPE, count: int = DEFAULT_COUNT,
         seconds: float = DEFAULT_SECONDS) -> dict:
    frames: dict[str, pd.DataFrame] = {}
    updates: dict[str, dict] = {}
    timings: dict[str, float] = {}
    bad_frames: list[str] = []

    targets = {name: _codes_for(name, codes) for name in BROKERS}
    skipped = {name: f"憑證未開通 {', '.join(codes)} 所在市場的行情"
               for name, target in targets.items() if not target}

    with Brokery(autype="none") as b:
        for name in BROKERS:
            if name in skipped:
                print(f"\n===== {name} 跳過：{skipped[name]} =====", flush=True)
                continue
            counter: dict[str, int] = {}
            print(f"\n===== {name} 串流 {', '.join(targets[name])} {ktype} × {count} 根"
                  f"（{seconds} 秒）=====", flush=True)
            started = time.monotonic()
            result = b.stream_kline(targets[name], ktype=ktype, count=count, broker=name,
                                    seconds=seconds, on_update=_handler(name, counter, bad_frames, count))
            timings[name] = time.monotonic() - started
            updates[name] = counter
            print(f"status={result['status']} message={result['message']} 用時={timings[name]:.1f}s")
            if result["status"]:
                frames[name] = result["data"]
                print(result["data"].tail(3))
            else:
                print(result["message"])

        # 串流不支持復權的券商，其能力由適配器聲明、由 core 在開始前擋掉，而不是靜靜改用另一種
        # 價格或默默失敗。
        refused = {name: b.stream_kline(targets[name][:1], ktype=ktype, count=count, broker=name,
                                        autype="qfq", seconds=1)
                   for name in REFUSE_QFQ if name not in skipped}
    print("\n===== 不支持的串流複權模式（autype=qfq）=====")
    for name, result in refused.items():
        print(f"{name}: status={result['status']} message={result['message']}")

    checks: list[tuple[str, bool, str]] = []
    for name in BROKERS:
        if name in skipped:
            continue
        frame = frames.get(name)
        if frame is None:
            checks.append((f"{name} 串流成功", False, "status=False"))
            continue
        checks.append((f"{name} 欄位為 K_COLUMNS", list(frame.columns) == K_COLUMNS, str(list(frame.columns))))
        for code, group in frame.groupby("code", sort=False):
            ts = group["ts"].tolist()
            checks.append((f"{name}/{code} ts 嚴格遞增", all(a < b for a, b in zip(ts, ts[1:])), f"{len(ts)} 根"))
            checks.append((f"{name}/{code} bar 數不超過 {count}", len(ts) <= count, f"{len(ts)} 根"))
        got = sorted({str(code) for code in frame["code"].unique()})
        checks.append((f"{name} 一條連線串流全部 {len(targets[name])} 個代碼",
                       len(got) == len(targets[name]), f"實際 {', '.join(got) or '無'}"))
        checks.append((f"{name} 持續時間受 seconds 約束",
                       seconds == 0 or seconds <= timings[name] < seconds + 30,
                       f"{timings[name]:.1f}s（要求 ≥{seconds}s）"))

    checks.append(("每次回呼的幀均合規格", not bad_frames, "；".join(bad_frames) or "無不合規格的回呼"))
    for name, result in refused.items():
        checks.append((f"{name} 不支持的串流 autype 明確報錯",
                       not result["status"] and result["message"].startswith("autype_unsupported"),
                       result["message"]))

    for name in BROKERS:
        total = sum(updates.get(name, {}).values())
        print(f"INFO {name} 收到推送 {total} 次"
              f"{'（休市時段無推送屬預期，不計失敗）' if total == 0 else ''}")

    for name, reason in skipped.items():
        print(f"WARN {name} 未驗收：{reason}")

    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）")
    failed = [label for label, passed, _ in checks if not passed]
    if failed:
        return {"status": False, "data": next(iter(frames.values()), pd.DataFrame(columns=K_COLUMNS)),
                "message": "失敗：" + "；".join(failed)}

    detail = "，".join(f"{name} {len(frame)} 根/{sum(updates[name].values())} 次推送"
                       for name, frame in frames.items())
    return {"status": True, "data": next(iter(frames.values())),
            "message": f"{len(checks)} 項檢查全過：{'/'.join(codes)} {ktype} × {count} 根"
                       f"，{seconds} 秒（{detail}）"
                       f"{'；未驗收：' + '、'.join(skipped) if skipped else ''}"}


if __name__ == "__main__":
    args = sys.argv[1:]
    codes = tuple(args[0].split(",")) if len(args) > 0 else DEFAULT_CODES
    raise SystemExit(
        0 if main(codes,
                  args[1] if len(args) > 1 else DEFAULT_KTYPE,
                  int(args[2]) if len(args) > 2 else DEFAULT_COUNT,
                  float(args[3]) if len(args) > 3 else DEFAULT_SECONDS)["status"] else 1
    )
