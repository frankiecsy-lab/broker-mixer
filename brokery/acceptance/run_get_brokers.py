"""驗收 `Brokery.get_brokers`：四個券商一律以 BROKER_COLUMNS 返回連線狀態與探測延遲。核對每家都有
一行結果、可連者延遲為正數且戶口數與 get_accounts 一致、連不上者 connected=False 且 latency_ms 為
NaN（不以任何數字湊出）並附原因、探測為並行（總耗時接近最慢一家而非各家總和；有券商連不上時，該家
以請求超時計入基準），以及未啟用的券商與
未啟用任何券商兩種情況明確報錯。

探測以一次戶口查詢進行，因此需要各券商後端在線；某家連不上本身不是失敗，但全部連不上即屬環境問題。

以腳本方式直接執行：
    python brokery/acceptance/run_get_brokers.py
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import pandas as pd

from brokery import Brokery
from brokery.brokers.base import BROKER_COLUMNS
from brokery.config import get_settings

SOURCES = ("futu", "ib", "tiger", "webull")

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 240)


def main() -> dict:
    checks: list[tuple[str, bool, str]] = []

    def check(label: str, passed: bool, detail: str = "") -> None:
        checks.append((label, bool(passed), str(detail)))

    direct: dict[str, dict] = {}
    with Brokery(sources=SOURCES) as b:
        started = time.perf_counter()
        result = b.get_brokers()
        elapsed = time.perf_counter() - started
        # 探測用的就是戶口查詢，故 accounts 必須與直接呼叫 get_accounts 的結果一致（須在同一連線內對照）。
        for name in result["data"].loc[result["data"]["connected"], "source"]:
            direct[name] = b.get_accounts(broker=name)
        unknown = b.get_brokers(broker="bogus")
    with Brokery(sources=()) as b:
        empty = b.get_brokers()

    print(f"\n===== get_brokers status={result['status']} 用時={elapsed:.1f}s message={result['message']}")
    frame = result["data"]
    print(frame.to_string())

    check("status=True", result["status"], result["message"])
    check("欄位為 BROKER_COLUMNS", list(frame.columns) == BROKER_COLUMNS, str(list(frame.columns)))
    check("每個已啟用券商各一行", sorted(frame["source"]) == sorted(SOURCES), ",".join(frame["source"]))
    check("connected 為布林、latency_ms 為浮點",
          pd.api.types.is_bool_dtype(frame["connected"]) and pd.api.types.is_float_dtype(frame["latency_ms"]),
          f"connected={frame['connected'].dtype} latency_ms={frame['latency_ms'].dtype}")

    rows = frame.set_index("source")
    up = [name for name in SOURCES if name in rows.index and bool(rows.loc[name, "connected"])]
    down = [name for name in SOURCES if name not in up]
    check(f"至少一家可連（現為 {len(up)} 家）", bool(up), f"可連 {'、'.join(up) or '無'}；斷開 {'、'.join(down) or '無'}")

    for name in up:
        row = rows.loc[name]
        check(f"{name} 延遲為正數", float(row["latency_ms"]) > 0, f"{row['latency_ms']:.0f}ms")
        check(f"{name} 成功時不附錯誤原因", not str(row["detail"]), str(row["detail"])[:80])
        got = direct.get(name) or {"status": False, "message": "未對照"}
        expect = len(got["data"]) if got["status"] else -1
        check(f"{name} 戶口數與 get_accounts 一致", int(row["accounts"]) == expect and expect >= 0,
              f"探測={row['accounts']} 直接={expect}（{got['message'][:60]}）")

    for name in down:
        row = rows.loc[name]
        check(f"{name} 連不上時 latency_ms 為 NaN", pd.isna(row["latency_ms"]), repr(row["latency_ms"]))
        check(f"{name} 連不上時附原因", bool(str(row["detail"])), str(row["detail"])[:120])

    now = int(time.time())
    check("checked_at 為近現時的 UTC 秒",
          all(abs(int(v) - now) <= 300 for v in frame["checked_at"]),
          ",".join(str(v) for v in frame["checked_at"]))

    # 並行探測：總耗時應接近最慢一家，而不是各家相加。少於兩家可連時無從對照。
    # 連不上的一家要等滿請求超時才被記為 timeout，呢個同樣是並行的結果，故基準須計入該超時；
    # 只以可連者的延遲計基準，會把「某家後端不在線」誤判成探測未並行。
    if len(up) >= 2:
        slowest = max(float(rows.loc[n, "latency_ms"]) for n in up) / 1000.0
        limit = max(1.0, float(get_settings().request_timeout))
        wait = limit * len(down)
        bound = max(slowest, limit if down else 0.0)
        serial = sum(float(rows.loc[n, "latency_ms"]) for n in up) / 1000.0 + wait
        check("各家並行探測（總耗時接近最慢一家）", elapsed < bound + 3.0,
              f"總耗時={elapsed:.1f}s 最慢={slowest:.1f}s 斷開 {len(down)} 家（等滿 {limit:.0f}s）"
              f" 基準={bound:.1f}s 若串行={serial:.1f}s")

    check("未啟用的券商明確報錯", not unknown["status"] and unknown["message"].startswith("unknown_source"),
          unknown["message"])
    with Brokery(sources=()) as b:
        empty = b.get_brokers()
    check("未啟用任何券商明確報錯", not empty["status"] and empty["message"].startswith("no_source"),
          empty["message"])

    rebuilt = pd.DataFrame(frame.to_dict("records"), columns=BROKER_COLUMNS)
    check("結果可重建 DataFrame", list(rebuilt.columns) == BROKER_COLUMNS and len(rebuilt) == len(frame),
          f"{len(rebuilt)} 行")

    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）")
    failed = [label for label, passed, _ in checks if not passed]
    if failed:
        return {"status": False, "data": frame, "message": "失敗：" + "；".join(failed)}
    return {"status": True, "data": frame,
            "message": f"{len(checks)} 項檢查全過：可連 {'、'.join(up) or '無'}，斷開 {'、'.join(down) or '無'}"}


if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] else 1)
