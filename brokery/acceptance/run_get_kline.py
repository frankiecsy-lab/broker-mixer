"""驗收 `Brokery.get_kline`：同一個 code 分別經 futu、ib 與 tiger 取 K 線，核對統一格式可否對齊，
並核對統一的複權參數（`Brokery(autype=...)` / `get_kline(autype=...)`）在券商不支持時明確報錯。

Webull 另以 webull_checks() 核對：它的接口沒有復權參數，價格由週期固定（日線及以上前復權、分鐘線不復權），
亦沒有 3 分鐘週期，故不参與上面以 autype="none" 的跨券商比價，只核對其取數格式與明確報錯。

以腳本方式直接執行：
    python brokery/acceptance/run_get_kline.py                      # 預設 HK.00001，日線 60 根，全部券商都取
    python brokery/acceptance/run_get_kline.py HK.00700 5m 200      # 指定代碼 / ktype / bar 數
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import pandas as pd

from brokery import Brokery
from brokery.brokers.base import K_COLUMNS

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 220)

DEFAULT_CODE = "HK.00001"
DEFAULT_KTYPE = "day"
DEFAULT_COUNT = 60
BROKERS = ("futu", "ib", "tiger")
# 無後復權概念的券商（IB 的 hfq 在任何 ktype 都不支持、Tiger 只有前復權與不復權），以 hfq 驗證明確報錯。
REFUSE_HFQ = ("ib", "tiger")
# Webull 的複權由週期固定（日線前復權、分鐘線不復權），且無 3 分鐘週期，故固定以日線核對其行為，
# 不隨命令行的 ktype 改變。
WEBULL_REFUSE = {"日線 autype=none": "autype_unsupported", "分鐘線 autype=qfq": "autype_unsupported",
                 "3m": "ktype_unsupported"}


def webull_checks(count: int) -> list[tuple[str, bool, str]]:
    """核對 Webull：日線只能以 qfq 取數（格式仍須統一），其餘組合必須明確報錯。"""
    with Brokery(sources=("webull",)) as b:
        day = b.get_kline(DEFAULT_CODE, ktype="day", count=count, broker="webull", autype="qfq")
        refused = {
            "日線 autype=none": b.get_kline(DEFAULT_CODE, ktype="day", count=count,
                                            broker="webull", autype="none"),
            "分鐘線 autype=qfq": b.get_kline(DEFAULT_CODE, ktype="1m", count=count,
                                             broker="webull", autype="qfq"),
            "3m": b.get_kline(DEFAULT_CODE, ktype="3m", count=count, broker="webull", autype="none"),
        }
    print("\n===== Webull（復權由週期固定，無 3m）=====")
    print(f"日線 autype=qfq: status={day['status']} message={day['message']}")
    if day["status"]:
        print(day["data"].tail(3))
    for label, result in refused.items():
        print(f"{label}: status={result['status']} message={result['message']}")

    checks: list[tuple[str, bool, str]] = [("webull 日線以 qfq 取數成功", day["status"], day["message"])]
    if day["status"]:
        frame = day["data"]
        ts = frame["ts"].tolist()
        checks.append(("webull 欄位為 K_COLUMNS", list(frame.columns) == K_COLUMNS, str(list(frame.columns))))
        checks.append(("webull ts 嚴格遞增", all(x < y for x, y in zip(ts, ts[1:])), f"{len(ts)} 根"))
        checks.append((f"webull bar 數不超過 {count}", len(frame) <= count, f"{len(frame)} 根"))
    for label, result in refused.items():
        checks.append((f"webull {label} 明確報錯",
                       not result["status"] and result["message"].startswith(WEBULL_REFUSE[label]),
                       result["message"]))
    return checks


def main(code: str = DEFAULT_CODE, ktype: str = DEFAULT_KTYPE, count: int = DEFAULT_COUNT) -> dict:
    frames: dict[str, pd.DataFrame] = {}
    # 跨券商比價要各家同取不復權：IB 的復權只適用日內與日線，且調整因子與富途不同（見 run_align_kline.py
    # 的實測），故一律以 autype="none" 對照，並在構造函數一處統一設定。
    with Brokery(autype="none") as b:
        for name in BROKERS:
            result = b.get_kline(code, ktype=ktype, count=count, broker=name)
            print(f"\n===== {name}（autype=none）=====")
            print(f"status={result['status']} message={result['message']}")
            if result["status"]:
                frames[name] = result["data"]
                print(result["data"].tail(5))

    # 不支持的複權模式必須明確報錯，不能靜靜返回另一種價格。IB 與 Tiger 均無後復權概念，故以 hfq
    # 逐一驗證；富途則按預設 autype=qfq 取數。
    with Brokery() as b:
        adjusted = b.get_kline(code, ktype=ktype, count=count, broker="futu")
        refused = {name: b.get_kline(code, ktype=ktype, count=count, broker=name, autype="hfq")
                   for name in REFUSE_HFQ}
    print("\n===== 不支持的複權模式（autype=hfq）=====")
    print(f"futu: status={adjusted['status']} message={adjusted['message']}")
    for name, result in refused.items():
        print(f"{name}: status={result['status']} message={result['message']}")

    checks: list[tuple[str, bool, str]] = []
    for name in BROKERS:
        frame = frames.get(name)
        if frame is None:
            checks.append((f"{name} 取數成功", False, "status=False"))
            continue
        ts = frame["ts"].tolist()
        checks.append((f"{name} 欄位為 K_COLUMNS", list(frame.columns) == K_COLUMNS, str(list(frame.columns))))
        checks.append((f"{name} ts 嚴格遞增", all(a < b for a, b in zip(ts, ts[1:])), f"{len(ts)} 根"))
        checks.append((f"{name} bar 數不超過 {count}", len(frame) <= count, f"{len(frame)} 根"))

    checks.append(("預設 autype=qfq 時富途取數成功", adjusted["status"], adjusted["message"]))
    for name, result in refused.items():
        checks.append((f"{name} 不支持的 autype 明確報錯",
                       not result["status"] and result["message"].startswith("autype_unsupported"),
                       result["message"]))
    checks += webull_checks(count)

    # 以富途為基準逐家按 ts 對齊並比價：只核對重疊數量會漏走「對齊鍵錯開一個週期」，各家 ts 集合
    # 仍然高度重疊，但同一 ts 對應的已是不同週期的數據，故必須比對價格。錯開一個週期的差距遠大於
    # 此處的閾值。
    base = BROKERS[0]
    if len(frames) == len(BROKERS):
        for name in BROKERS[1:]:
            merged = frames[base].merge(frames[name], on="ts", suffixes=(f"_{base}", f"_{name}"))
            checks.append((f"{base} 與 {name} 可按 ts 對齊", not merged.empty, f"共同 bar {len(merged)} 根"))
            if merged.empty:
                continue
            print(f"\n===== 對齊核對（{base} 與 {name}，最後 5 根共同 bar）=====")
            print(merged[["ts", f"time_key_{base}", f"time_key_{name}",
                          f"close_{base}", f"close_{name}"]].tail(5))
            ratio = ((merged[f"close_{base}"] - merged[f"close_{name}"]).abs()
                     / merged[f"close_{name}"].abs().clip(lower=1e-9))
            worst = float(ratio.max())
            checks.append((f"共同 bar 的 close 一致（{base} 與 {name} 均不復權，{len(merged)} 根）",
                           worst < 0.005, f"最大相差 {worst:.4%}"))

    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）")
    failed = [label for label, passed, _ in checks if not passed]
    if failed:
        return {"status": False, "data": next(iter(frames.values()), pd.DataFrame(columns=K_COLUMNS)),
                "message": "失敗：" + "；".join(failed)}

    counts = "，".join(f"{name} {len(frames[name])} 根" for name in BROKERS)
    return {"status": True, "data": frames[BROKERS[0]],
            "message": f"{len(checks)} 項檢查全過：{code} {ktype} × {count} 根（{counts}）"}


if __name__ == "__main__":
    args = sys.argv[1:]
    raise SystemExit(
        0 if main(args[0] if len(args) > 0 else DEFAULT_CODE,
                  args[1] if len(args) > 1 else DEFAULT_KTYPE,
                  int(args[2]) if len(args) > 2 else DEFAULT_COUNT)["status"] else 1
    )
