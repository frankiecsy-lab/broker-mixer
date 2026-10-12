"""驗收 `Brokery.stream_kline`：一條連線同時串流多個代碼（對應同時顯示多張 K 線圖），核對各家
均返回統一格式、每次回呼的 bar 數受 count 限制、持續時間受 seconds 約束，以及券商不支持的串流
複權模式在開始前就明確報錯。

另驗多週期並行（「K 線圖（多週期）」3×3 一格一週期）：同一條連線同時串流多個週期，各格必須取到
自己週期的 bar；同一週期的第二份亦必須能並行，而且兩份都不得靜靜蓋走對方（上游訂閱按引用計數，
最後一份結束才退）。可並行的週期一律取自適配器聲明的 `stream_ktypes`，本腳本不自訂第二套名單。

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
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import pandas as pd

from brokery import Brokery
from brokery.brokers.base import BAR_MINUTES, K_COLUMNS

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
# 多週期並行只取分鐘線：日線以上的 ts 間距受交易日與假期影響，不能以間距核對週期。
MULTI_MINUTES = ("1m", "3m", "5m", "15m", "30m")
MULTI_PERIODS = 3          # 三個週期已足以證明「多個」而非湊巧兩份
MULTI_SECONDS = 20.0       # 並行段只為驗證互不干扰，不需要與主段同樣長


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


def _multi(b: Brokery, name: str, code: str, count: int) -> tuple[list[tuple[str, bool, str]], str]:
    """同一條連線並行多個週期（多週期界面一格一週期）：各格必須取到自己週期的 bar，互不蓋走。

    可並行的週期一律取自適配器聲明的 stream_ktypes；只聲明一個週期的券商（tiger、webull）沒有
    多週期可驗，返回說明而不計失敗。
    """
    adapter = b.adapters()[name]
    ktypes = [k for k in adapter.stream_ktypes if k in MULTI_MINUTES][:MULTI_PERIODS]
    if len(ktypes) < 2:
        return [], f"只聲明可串流 {'/'.join(adapter.stream_ktypes) or '無'}，無多週期可驗"

    results: dict[str, dict] = {}
    pushes: dict[str, list] = {k: [] for k in ktypes}
    ctx_before = getattr(adapter, "_ctx", None)

    def run(ktype: str) -> None:
        results[ktype] = b.stream_kline(code, ktype=ktype, count=count, broker=name,
                                        seconds=MULTI_SECONDS,
                                        on_update=lambda _code, rows: pushes[ktype].append(rows))

    threads = [threading.Thread(target=run, args=(k,), daemon=True) for k in ktypes]
    for thread in threads:
        thread.start()
    time.sleep(2.0)   # 各份已在串流：此時同週期的第二份必須能並行，而不是被拒或靜靜共用同一組訂閱
    # 上游訂閱按（代碼, 週期）引用計數：第一份仍在收時退訂閱會蓋走它仍需要嘅推送，故只容許最後一份退。
    # 休市沒有推送，故只對退訂閱的時機作斷言，不數推送次數。
    unsub: list[tuple] = []
    real_unsub = getattr(ctx_before, "unsubscribe", None) if ctx_before is not None else None
    if real_unsub is not None:
        def spy(target, sub_types, *rest):
            unsub.append((tuple(target), tuple(sub_types)))
            return real_unsub(target, sub_types, *rest)
        ctx_before.unsubscribe = spy
    second = b.stream_kline(code, ktype=ktypes[0], count=count, broker=name, seconds=1)
    while_running = list(unsub)   # 第二份已收尾、其餘各份仍在串流：此刻的退訂閱清單即判準
    for thread in threads:
        thread.join(timeout=MULTI_SECONDS + 90)
    if real_unsub is not None:
        ctx_before.unsubscribe = real_unsub

    checks: list[tuple[str, bool, str]] = [
        (f"{name} 同一連線並行 {len(ktypes)} 個週期（{'/'.join(ktypes)}）",
         len(results) == len(ktypes) and all(r.get("status") for r in results.values()),
         "；".join(f"{k}={str(results.get(k, {}).get('message', '未結束'))[:70]}" for k in ktypes)),
    ]
    # 每一格必須係自己週期的 bar：ts 間距即該週期的整數倍，否則即推送被派錯週期（九格會變同一份資料）。
    for ktype in ktypes:
        # 失敗時返回嘅 data 可以係冇欄位嘅空表（例如 IB 連不上），故先確認欄位齊先核對間距。
        frame = results.get(ktype, {}).get("data")
        ts = ([] if frame is None or not {"code", "ts"}.issubset(frame.columns)
              else frame.loc[frame["code"] == code, "ts"].tolist())
        step = 60 * BAR_MINUTES[ktype]
        gaps = [later - earlier for earlier, later in zip(ts, ts[1:])]
        checks.append((f"{name}/{ktype} 並行時仍取到自己週期的 bar（ts 間距為 {step}s 的整數倍）",
                       len(ts) >= 2 and all(gap % step == 0 for gap in gaps),
                       f"{len(ts)} 根/{len(pushes[ktype])} 次推送"))
    if name == "futu":
        # 富途每條連線只有一個推送回呼，過去按 ktype 佔額；推送自帶 k_type 與代碼，各份只收自己那份，
        # 故同週期的第二份應能並行。IB 每個 (代碼,週期) 各自一次 reqHistoricalData，本來已可並行，
        # 不適用呢幾條斷言。
        from futu import SubType   # 與適配器同一個枚舉，用以核對退的是哪個（代碼, 週期）
        from brokery.brokers.futu_broker import FUTU_KTYPE

        def dropped(entries: list[tuple]) -> list[tuple]:
            return [e for e in entries if code in e[0] and getattr(SubType, FUTU_KTYPE[ktypes[0]]) in e[1]]

        checks.append((f"{name} 同週期的第二份可與第一份並行（不再返回 stream_busy）",
                       second["status"], second["message"]))
        checks.append((f"{name} 並行期間不退仍在使用的訂閱（{code}/{ktypes[0]}）",
                       not dropped(while_running), f"第二份收尾時共退訂閱 {len(while_running)} 次"))
        checks.append((f"{name} 最後一份結束才退訂閱（{code}/{ktypes[0]}）",
                       bool(dropped(unsub)), f"全部結束後累計退訂閱 {len(dropped(unsub))} 次"))
        checks.append((f"{name} 多個週期共用同一條連線（沒有另開一條）",
                       ctx_before is not None and getattr(adapter, "_ctx", None) is ctx_before,
                       "同一個 OpenQuoteContext" if ctx_before is not None else "連線未建立"))
    return checks, "/".join(ktypes)


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

        # 多週期並行：多週期界面一格一週期，故必須先證明同一條連線可以同時串流多個週期。
        multi: list[tuple[str, bool, str]] = []
        for name in BROKERS:
            if name in skipped:
                continue
            print(f"\n===== {name} 多週期並行（{MULTI_SECONDS} 秒）=====", flush=True)
            got, note = _multi(b, name, targets[name][0], min(count, 60))
            if not got:
                print(f"  {name} 跳過多週期：{note}", flush=True)
            multi += got

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

    checks.extend(multi)
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
