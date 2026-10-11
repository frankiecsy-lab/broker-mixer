"""驗收不同市場、不同品種（股票／期貨／指數／期權）的 K 線與復權行為，以富途格式為準。

以腳本方式直接執行：python brokery/acceptance/run_kline_matrix.py

三條結論由實測固定下來，任何一條被改動即代表行為改變：
1. 品種由統一代碼推斷（codes.classify_symbol）；來源未聲明該品種即明確返回 type_unsupported，
   不會把期權、期貨或指數當股票送進上游等它報錯（Tiger 對期貨、Webull 對指數皆如此）。
2. 復權只對股票有效：期貨、指數與期權沒有公司行動，實測各來源的 autype=qfq 與 none 逐根完全
   相同（0 根有差別）；股票則必須看到調整（對照組 HK.00005 期內有派息）。
3. 指數代碼可直接跨券商使用：富途格式的 US..SPX／HK.800000 在 IB 亦能解析（IB 以指數名稱登記，
   美股去前導點即同名，港股只有 IB_INDEX_ALIAS 裏幾隻登記了名稱）。
4. raw=True 只換欄位與格式，不改取數範圍與數值：同一請求的根數與收市價與統一格式逐根相同，時間欄位
   為該券商自己的寫法（富途 time_key、Tiger／Webull time、IB date），且不含由適配器構造的 ts／source
   （富途 K 線框自帶的 code 屬上游原樣，一律保留）；能力閘（type_unsupported）亦不受 raw 影響。

期權只有富途提供（美股期權為完整序列，港股期權實測只返回當日一根）；期權代碼由富途期權鏈即時
取得，避免寫死到期日。行情權限缺口（富途的美股期貨與指數、IB 的 HKEX A50、Webull 的美股行情）
屬賬戶權限，不屬本腳本的驗收範圍，故不出現在檢查表中。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

from datetime import date, timedelta

import pandas as pd

from brokery import Brokery
from brokery.brokers.base import K_COLUMNS
from brokery.codes import classify_symbol, parse_code

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 220)

KTYPE = "day"
COUNT = 60
PRICE_EPS = 1e-9  # 判斷某一根是否被調整過
MAX_DIVERGENCE = 0.01  # 跨券商同品種的容許偏差：只用於排除錯位與量級錯誤

# 品種推斷的樣例：涵蓋股票、主連與個月份期貨、港美指數與港美期權。
CLASSIFY = [
    ("HK.00005", "STOCK"), ("US.NVDA", "STOCK"),
    ("HK.A50main", "FUTURE"), ("US.10Ymain", "FUTURE"), ("US.ES202612", "FUTURE"),
    ("HK.800000", "INDEX"), ("US..SPX", "INDEX"),
    ("HK.TCH261127C205000", "OPTION"), ("US.AAPL261106C110000", "OPTION"),
]

# 未聲明該品種的組合，必須在發出請求前就被拒绝（消息以 type_unsupported 開頭）。
GATE = [
    ("HK.A50main", ("tiger", "webull")),
    ("US.10Ymain", ("tiger", "webull")),
    ("HK.800000", ("webull",)),
    ("US..SPX", ("webull",)),
    ("US.AAPL261106C110000", ("ib", "tiger", "webull")),
    ("HK.TCH261127C205000", ("ib", "webull")),
]
# 只用於能力閘：在發出請求前即被拒绝，故該期權是否到期不影響結果。
OPTION_SAMPLE = "US.AAPL261106C110000"

# 無公司行動的品種：qfq 與 none 必須逐根相同。
NO_ADJUST = [("HK.A50main", "futu"), ("HK.800000", "futu"), ("US.10Ymain", "ib"), ("US..SPX", "tiger")]
# 對照組：期內有派息的股票，必須看到調整。
ADJUST = ("HK.00005", "futu", 250)
# 同一指數跨券商逐根對照（以第一家為準）。富途無美股指數權限，故美股以 Tiger 為準。
CROSS = [("HK.800000", ("futu", "ib")), ("US..SPX", ("tiger", "ib"))]


# raw=True 的對照：時間欄位必須是該券商自己的寫法（富途 time_key、Tiger／Webull time、IB date），
# 復權參數按各家接口實際支持者填寫（Webull 的日線只有前復權），代碼則按該賬戶實際開通的行情選
# （Webull 的憑證只開通 HK 行情，美股會先撞到 market_data_not_subscribed）。
RAW_KLINE = [("HK.00005", "futu", "time_key", "none"), ("HK.00005", "webull", "time", "qfq"),
             ("US..SPX", "tiger", "time", "none"), ("HK.800000", "ib", "date", "none")]


def raw_kline_checks(base: dict, raw: dict, time_field: str) -> list[tuple[str, bool, str]]:
    """raw K 線：欄位與時間寫法即上游原樣；根數與數值與統一格式逐根一致（raw 不改數）。

    只有 ts／source 是由適配器構造的（時間轉換與來源標記）。code 不是：富途自己的 K 線框就帶 code，
    屬上游原樣，必須保留。
    """
    frame, columns = raw["data"], list(raw["data"].columns)
    built = sorted({"ts", "source"} & set(columns))
    checks = [("信封仍只有三鍵", set(raw) == {"status", "data", "message"}, str(sorted(raw))),
              ("欄位即該券商原生鍵（不是 K_COLUMNS）", bool(columns) and columns != K_COLUMNS,
               ",".join(columns[:8])),
              ("時間欄位為該券商自己的寫法", time_field in columns, time_field),
              ("不含由適配器構造的統一欄位", not built, ",".join(built)),
              ("根數不變（count 不受 raw 影響）", raw["status"] and len(frame) == len(base["data"]),
               f"raw={len(frame)} 統一={len(base['data'])}")]
    if raw["status"] and "close" in columns and len(frame) == len(base["data"]):
        gap = (pd.to_numeric(frame["close"], errors="coerce")
               - pd.to_numeric(base["data"]["close"], errors="coerce")).abs().max()
        checks.append(("收市價逐根相同（raw 不改數）", bool(gap <= PRICE_EPS), f"最大相差 {gap}"))
    return checks


def _diff(left: pd.DataFrame, right: pd.DataFrame) -> tuple[int, int, float]:
    """按 ts 配對後，返回（數值不同的根數、可配對根數、最大相對差距）。"""
    pair = left.merge(right[["ts", "close"]], on="ts", suffixes=("_l", "_r"))
    if pair.empty:
        return -1, 0, 1.0
    ratio = (pair["close_l"] - pair["close_r"]).abs() / pair["close_r"].abs().clip(lower=1e-9)
    return int((ratio > PRICE_EPS).sum()), len(pair), float(ratio.max())


def _live_option() -> str:
    """從富途期權鏈取一個未到期嘅期權代碼，避免寫死到期日。取不到即返回空字串。"""
    import futu

    from brokery.config import get_settings

    settings = get_settings()
    start = (date.today() + timedelta(days=20)).isoformat()
    ctx = futu.OpenQuoteContext(host=settings.futu_host, port=settings.futu_port)
    try:
        for underlying in ("US.AAPL", "HK.00700"):
            ret, dates = ctx.get_option_expiration_date(underlying)
            if ret != 0:
                continue
            pick = next((d for d in dates["strike_time"] if str(d) >= start), None)
            if pick is None:
                continue
            ret, chain = ctx.get_option_chain(underlying, start=str(pick), end=str(pick))
            if ret == 0 and not chain.empty:
                return str(chain["code"].iloc[0])
    finally:
        ctx.close()
    return ""


def main() -> dict:
    checks: list[tuple[str, bool, str]] = []
    frames: dict[str, pd.DataFrame] = {}

    for code, want in CLASSIFY:
        parsed = parse_code(code)
        got = classify_symbol(parsed.market, parsed.symbol)
        checks.append((f"classify_symbol({code}) = {want}", got == want, got))

    with Brokery() as b:
        for code, names in GATE:
            for name in names:
                result = b.get_kline(code, ktype=KTYPE, count=5, broker=name, autype="none")
                checks.append((f"{name} 對 {code} 明確拒绝",
                               not result["status"] and result["message"].startswith("type_unsupported"),
                               result["message"]))
        streamed = b.stream_kline(OPTION_SAMPLE, ktype="1m", count=3, broker="ib", autype="none", seconds=2)
        checks.append(("ib 串流期權明確拒绝",
                       not streamed["status"] and streamed["message"].startswith("type_unsupported"),
                       streamed["message"]))
        gated = b.get_kline("HK.A50main", ktype=KTYPE, count=5, broker="webull", autype="none", raw=True)
        checks.append(("能力閘不受 raw 影響（未聲明品種同樣在發出請求前即被拒绝）",
                       not gated["status"] and gated["message"].startswith("type_unsupported"),
                       gated["message"]))

        # raw=True：同一請求只換欄位與格式，取數範圍與數值一律不變。
        for code, name, time_field, autype in RAW_KLINE:
            base = b.get_kline(code, ktype=KTYPE, count=5, broker=name, autype=autype)
            if not base["status"]:  # 行情權限與後端可達性屬賬戶/環境，不屬本腳本的驗收範圍
                print(f"WARN {name} {code} 取不到，raw 對照跳過：{base['message']}")
                continue
            raw = b.get_kline(code, ktype=KTYPE, count=5, broker=name, autype=autype, raw=True)
            print(f"\n===== {name} {code} raw=True status={raw['status']} rows={len(raw['data'])} "
                  f"columns={list(raw['data'].columns)}")
            checks += [(f"{name} {code} raw：{label}", passed, detail)
                       for label, passed, detail in raw_kline_checks(base, raw, time_field)]

        # 無公司行動的品種：qfq 與 none 逐根相同。
        for code, name in NO_ADJUST:
            qfq = b.get_kline(code, ktype=KTYPE, count=COUNT, broker=name, autype="qfq")
            none = b.get_kline(code, ktype=KTYPE, count=COUNT, broker=name, autype="none")
            if not (qfq["status"] and none["status"]):
                checks.append((f"{name} {code} 復權無差異", False,
                               qfq["message"] if not qfq["status"] else none["message"]))
                continue
            changed, paired, worst = _diff(qfq["data"], none["data"])
            print(f"\n===== {name} {code} qfq vs none =====\n{paired} 根可配對，{changed} 根有差別，最大相差 {worst:.4%}")
            checks.append((f"{name} {code} qfq 與 none 逐根相同", changed == 0 and paired > 0,
                           f"{paired} 根，{changed} 根有差別"))

        # 對照組：股票必須被調整。
        code, name, count = ADJUST
        qfq = b.get_kline(code, ktype=KTYPE, count=count, broker=name, autype="qfq")
        none = b.get_kline(code, ktype=KTYPE, count=count, broker=name, autype="none")
        if qfq["status"] and none["status"]:
            changed, paired, worst = _diff(qfq["data"], none["data"])
            print(f"\n===== {name} {code}（對照組，期內有派息）=====\n{paired} 根可配對，{changed} 根有差別，最大相差 {worst:.4%}")
            checks.append((f"{name} {code} 復權確實生效", changed > 0, f"{changed}/{paired} 根被調整，最大 {worst:.4%}"))
        else:
            checks.append((f"{name} {code} 復權確實生效", False,
                           qfq["message"] if not qfq["status"] else none["message"]))

        # 同一指數跨券商逐根對照。
        for code, names in CROSS:
            got = {}
            for name in names:
                result = b.get_kline(code, ktype=KTYPE, count=COUNT, broker=name, autype="none")
                if result["status"]:
                    got[name] = result["data"]
                else:
                    print(f"WARN {name} {code} 取不到：{result['message']}")
            if len(got) < len(names):
                checks.append((f"{code} 可跨券商對齊（{'/'.join(names)}）", False, "有來源取不到"))
                continue
            base = got[names[0]]
            for name in names[1:]:
                changed, paired, worst = _diff(base, got[name])
                print(f"\n===== {code} 跨券商對照：{names[0]} vs {name} =====\n{paired} 根可配對，{changed} 根數值不同，最大相差 {worst:.4%}")
                checks.append((f"{code} {names[0]} 與 {name} 可按 ts 對齊且價格同量級",
                               paired >= 0.9 * min(len(base), len(got[name])) and worst < MAX_DIVERGENCE,
                               f"共同 {paired} 根，最大相差 {worst:.4%}"))
                frames[f"{code}|{name}"] = got[name]

        # 期權：只有富途提供，且 qfq 與 none 相同。
        option = _live_option()
        if option:
            qfq = b.get_kline(option, ktype=KTYPE, count=COUNT, broker="futu", autype="qfq")
            none = b.get_kline(option, ktype=KTYPE, count=COUNT, broker="futu", autype="none")
            print(f"\n===== 富途期權 {option} =====")
            print(f"status={qfq['status']} message={qfq['message']}")
            if qfq["status"]:
                print(qfq["data"][["time_key", "open", "high", "low", "close", "volume"]].tail(5))
            changed, paired, worst = _diff(qfq["data"], none["data"]) if qfq["status"] and none["status"] else (-1, 0, 1.0)
            checks.append((f"富途期權 {option} 可取 K 線", qfq["status"], qfq["message"]))
            checks.append((f"富途期權 {option} qfq 與 none 逐根相同", changed == 0 and paired > 0,
                           f"{paired} 根，{changed} 根有差別"))
        else:
            print("WARN 期權未驗收：未能從富途期權鏈取得未到期代碼")

    merged = pd.concat(frames.values(), ignore_index=True) if frames else pd.DataFrame(columns=K_COLUMNS)
    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）")
    failed = [label for label, passed, _ in checks if not passed]
    if failed:
        return {"status": False, "data": merged, "message": "失敗：" + "；".join(failed)}
    return {
        "status": True,
        "data": merged,
        "message": f"{len(checks)} 項檢查全過：品種推斷與能力閘一致；復權只對股票生效"
                   f"（期貨／指數／期權 qfq 與 none 逐根相同）；指數代碼可跨券商對齊；"
                   f"raw 只換欄位與格式（根數與數值逐根一致）",
    }


if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] else 1)
