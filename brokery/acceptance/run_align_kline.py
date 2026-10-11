"""驗收跨券商前復權可否對齊：同一個 code 分別取 futu、ib、tiger、webull 的前復權 K 線，以富途為準
按 ts 逐根並列，並量化各家與富途的調整差異。

以腳本方式直接執行：
    python brokery/acceptance/run_align_kline.py                     # 預設 HK.00005，日線 60 根
    python brokery/acceptance/run_align_kline.py HK.00700 day 120     # 指定代碼 / ktype / bar 數

各家前復權的實現互不相同：富途 autype=qfq、IB whatToShow=ADJUSTED_LAST（只適用日內與日線，週/月線
由適配器明確拒绝）、Tiger right=BR、Webull 沒有復權參數（日線及以上固定為前復權）。調整因子由各家
自行計算，故本腳本以實際數據顯示可對齊的程度；對齊一律以富途為準，其餘各家只作遷就，不為對齊改價。

Webull 的 app key 註冊於 HK 區域，取美股返回 403 MARKET_DATA_NOT_SUBSCRIBED，故按 MARKETS 過濾市場，
未開通者跳過並打印 WARN，避免把賬戶的行情權限問題誤當為代碼錯誤。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import pandas as pd

from brokery import Brokery
from brokery.brokers.base import K_COLUMNS

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 260)

DEFAULT_CODE = "HK.00005"  # 期內有派息，各家的調整結果都會體現出來
DEFAULT_KTYPE = "day"
DEFAULT_COUNT = 60
BROKERS = ("futu", "ib", "tiger", "webull")
REFERENCE = "futu"  # 對齊基準：其餘各家一律與它逐根比較
# 各券商憑證實際開通行情的市場。Webull 的 app key 註冊於 HK 區域，實測取美股一律返回
# 403 MARKET_DATA_NOT_SUBSCRIBED（該市場未開通行情），故只以 HK 代碼驗收它。
MARKETS = {"webull": ("HK",)}

PRICE_EPS = 1e-6  # 判斷某一根是否被調整過
MAX_DIVERGENCE = 0.02  # 前復權的容許偏差：只用於排除錯位與量級錯誤，因子差異以實際數值顯示


def _brokers_for(code: str) -> tuple[str, ...]:
    """按各券商憑證實際開通的市場過濾，未開通該市場即跳過該家（見 MARKETS）。"""
    market = code.split(".", 1)[0]
    return tuple(name for name in BROKERS if market in MARKETS.get(name, (market,)))


def _divergence(left: pd.Series, right: pd.Series) -> tuple[float, int]:
    """兩條收盤序列的最大相對差距，以及數值不同的根數。"""
    ratio = (left - right).abs() / right.abs().clip(lower=1e-9)
    return float(ratio.max()), int((ratio > PRICE_EPS).sum())


def main(code: str = DEFAULT_CODE, ktype: str = DEFAULT_KTYPE, count: int = DEFAULT_COUNT) -> dict:
    brokers = _brokers_for(code)
    market = code.split(".", 1)[0]
    skipped = {name: f"憑證未開通 {market} 市場行情" for name in BROKERS if name not in brokers}
    frames: dict[str, pd.DataFrame] = {}
    raw: dict[str, pd.DataFrame] = {}
    no_raw: dict[str, str] = {}  # 取不到原始成交價的券商與原因（復權由週期固定等）
    with Brokery(autype="qfq") as b:
        for name in brokers:
            result = b.get_kline(code, ktype=ktype, count=count, broker=name)
            print(f"\n===== {name} 前復權（autype=qfq）=====")
            print(f"status={result['status']} message={result['message']}")
            if result["status"]:
                frames[name] = result["data"]
                print(result["data"][["time_key", "open", "high", "low", "close"]].tail(5))
        # 對照組：原始成交價。用以確認各家確實做了調整，而不是把原始價當前復權返回。
        for name in brokers:
            result = b.get_kline(code, ktype=ktype, count=count, broker=name, autype="none")
            if result["status"]:
                raw[name] = result["data"]
            else:
                no_raw[name] = result["message"]
        # 邊界：IB 的復權只適用日內與日線，週/月線必須明確拒绝（IB 對多於一日的 bar 報 error 321）。
        weekly = b.get_kline(code, ktype="week", count=count, broker="ib")

    checks: list[tuple[str, bool, str]] = []
    for name in brokers:
        frame = frames.get(name)
        if frame is None:
            checks.append((f"{name} 前復權取數成功", False, "status=False"))
            continue
        ts = frame["ts"].tolist()
        checks.append((f"{name} 前復權取數成功", True, f"{len(frame)} 根"))
        checks.append((f"{name} 欄位為 K_COLUMNS", list(frame.columns) == K_COLUMNS, str(list(frame.columns))))
        checks.append((f"{name} ts 嚴格遞增", all(x < y for x, y in zip(ts, ts[1:])), f"{len(ts)} 根"))

    print(f"\n===== IB 週線要求復權（不適用，應明確拒绝）=====\nstatus={weekly['status']} message={weekly['message']}")
    checks.append(("IB 週線要求復權時明確拒绝",
                   not weekly["status"] and weekly["message"].startswith("autype_unsupported"),
                   weekly["message"]))

    merged = pd.DataFrame()
    others = [name for name in brokers if name != REFERENCE and name in frames]
    if REFERENCE in frames and others:
        base = frames[REFERENCE]
        for name in others:
            pair = base.merge(frames[name], on="ts", suffixes=("", f"_{name}"))
            shortest = min(len(base), len(frames[name]))
            checks.append((f"{name} 前復權可按 ts 對齊 {REFERENCE}", len(pair) >= 0.9 * shortest,
                           f"共同 {len(pair)} 根／較短的一邊 {shortest} 根"))
            worst, changed = _divergence(pair["close"], pair[f"close_{name}"])
            checks.append((f"{name} 前復權收盤價與 {REFERENCE} 同向（{len(pair)} 根共同 bar）",
                           worst < MAX_DIVERGENCE, f"{changed} 根數值不同，最大相差 {worst:.4%}"))
        merged = base.copy()
        for name in others:
            merged = merged.merge(frames[name][["ts", "close"]], on="ts", suffixes=("", f"_{name}"))
            merged[f"diff_{name}"] = ((merged[f"close_{name}"] / merged["close"] - 1) * 100).round(4)
        columns = ["time_key", "close"] + [f"close_{n}" for n in others] + [f"diff_{n}" for n in others]
        print(f"\n===== 前復權逐根對照（以 {REFERENCE} 為準，最後 10 根共同 bar，{code} {ktype}）=====")
        print(merged[columns].tail(10).to_string(index=False))

    for name in brokers:
        if name in raw and name in frames:
            base = frames[name].merge(raw[name][["ts", "close"]], on="ts", suffixes=("", "_raw"))
            worst, changed = _divergence(base["close"], base["close_raw"])
            print(f"\n===== {name} 復權對照（autype=qfq vs none）=====")
            print(f"{changed}/{len(base)} 根與原始成交價不同，最大調整幅度 {worst:.4%}")
        elif name in no_raw:
            print(f"\n===== {name} 復權對照（autype=qfq vs none）=====\n無法對照：{no_raw[name]}")

    for name, reason in skipped.items():
        print(f"WARN {name} 未驗收：{reason}")
    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）")
    failed = [label for label, passed, _ in checks if not passed]
    if failed:
        return {"status": False, "data": merged if not merged.empty else next(iter(frames.values()), pd.DataFrame(columns=K_COLUMNS)),
                "message": "失敗：" + "；".join(failed)}

    return {
        "status": True,
        "data": merged,
        "message": f"{len(checks)} 項檢查全過：{code} {ktype} × {count} 根的前復權以 {REFERENCE} 為準"
                   f"可對齊 {len(merged)} 根（{'/'.join(brokers)}）"
                   f"{'；未驗收：' + '、'.join(skipped) if skipped else ''}",
    }


if __name__ == "__main__":
    args = sys.argv[1:]
    raise SystemExit(
        0 if main(args[0] if len(args) > 0 else DEFAULT_CODE,
                  args[1] if len(args) > 1 else DEFAULT_KTYPE,
                  int(args[2]) if len(args) > 2 else DEFAULT_COUNT)["status"] else 1
    )
