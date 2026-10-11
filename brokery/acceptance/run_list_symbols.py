"""驗收四家券商的標的清單能力與統一輸出格式：逐家 × 逐品種（股票／期貨／指數）核對——
已聲明者必須以 COLUMNS 的欄位與順序返回，且字串欄一律不為 NaN（無值為空字串，不為湊齊造數）、
source 與 symbol_type 與該次請求一致、code 為 <市場>.<符號> 的統一代碼。統一格式不設到期月欄，
期貨的到期月一律含在符號內（主連帶 main/current 等後綴、個月份為 root+到期月），故代碼本身即
合約身份、同一清單內不得重複；未聲明者必須明確返回 no_source，不得返回空表冒充支援。能力聲明本身亦逐一核對
（futu/tiger 三項、ib 無股票、webull 無指數），因為這是調度與 UI 標示的依據，不得無聲擴大。
最後以一次跨券商期貨清單核對：四家返回同一欄位契約，且同一合約不重複列（已被別家完全覆蓋者按
去重只留一份，故不要求四家都出現喺合併結果入面）。
每個已聲明的組合再以 raw=True 取一次同一請求：信封仍為三鍵、欄位即該券商自帶的鍵（不含由適配器構造的
source／symbol_type）、不做去重故行數不少於統一格式；未聲明的品種 raw 同樣明確返回 no_source。

以腳本方式直接執行：
    python brokery/acceptance/run_list_symbols.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import pandas as pd

from brokery import Brokery
from brokery.brokers.base import COLUMNS
from brokery.codes import FUTURE, INDEX, STOCK, classify_symbol

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 240)

BROKERS = ("futu", "ib", "tiger", "webull")
# 能力聲明為各家實際聲明者（實測），非湊齊：IB 沒有可取全的股票清單、Webull 沒有指數 category。
DECLARED = {
    "futu": {STOCK, FUTURE, INDEX},
    "ib": {FUTURE, INDEX},
    "tiger": {STOCK, FUTURE, INDEX},
    "webull": {STOCK, FUTURE},
}
# 逐品種只取窄範圍：本腳本驗的是格式與能力邊界，不是重新下載全市場。
SAMPLES = {STOCK: ("list_stocks", ("HK",)), FUTURE: ("list_futures", ("ES",)), INDEX: ("list_indices", ("SPX",))}
# 統一格式不設到期月欄，故期貨的合約必須由符號唯一標識：主連以富途的 main/current/next/day 後綴
# 表示，個月份帶到期月（富途為原生代碼，IB／Tiger／Webull 以 root+到期月寫成，如 ES202612）。
# 只以 root 表達合約即不合格——同一 root 的各月份會塌成同一個代碼。
CONTINUOUS_SUFFIXES = ("main", "current", "next", "day")
MONTH_IN_SYMBOL = re.compile(r"\d{4,8}$")


def carries_contract(symbol: str) -> bool:
    """符號是否已唯一標識一份期貨合約（主連後綴或到期月）。"""
    return symbol.endswith(CONTINUOUS_SUFFIXES) or bool(MONTH_IN_SYMBOL.search(symbol))


def row_checks(name: str, symbol_type: str, frame: pd.DataFrame) -> list[tuple[str, bool, str]]:
    """統一格式：欄位與順序固定、字串欄不為 NaN、身份欄與該次請求一致、代碼為統一代碼。"""
    checks = [("欄位為 COLUMNS（順序一致）", list(frame.columns) == COLUMNS, str(list(frame.columns)))]
    checks.append(("無 NaN／None（無值一律為空字串）", not bool(frame.isna().any().any()),
                   "；".join(f"{c}={frame[c].isna().sum()}" for c in COLUMNS if frame[c].isna().any()) or "無"))
    checks.append(("source 即本次請求的券商", bool((frame["source"] == name).all()),
                   ",".join(sorted(set(frame["source"])))))
    checks.append(("symbol_type 即所請求的品種", bool((frame["symbol_type"] == symbol_type).all()),
                   ",".join(sorted(set(frame["symbol_type"])))))
    checks.append(("code 為 <市場>.<符號> 統一代碼",
                   bool((frame["code"] == frame["market"] + "." + frame["symbol"]).all()),
                   ",".join(frame["code"].head(3))))
    checks.append(("market 為統一市場前綴", set(frame["market"]) <= {"HK", "US", "SG", "SH", "SZ", "JP"},
                   ",".join(sorted(set(frame["market"])))))
    # 到期月已含在符號內，故代碼本身即合約身份：同一清單內不得出現兩個相同代碼。
    checks.append(("code 無重複（代碼即合約身份）",
                   int(frame.duplicated(subset=["code"]).sum()) == 0, f"{len(frame)} 列"))
    if symbol_type == FUTURE:
        bare = sorted({s for s in frame["symbol"].astype(str) if not carries_contract(s)})
        checks.append(("期貨符號已含主連後綴或到期月（不設到期月欄仍唯一標識合約）",
                       not bare, ",".join(bare[:6]) or "無"))
    else:
        # 股票／指數不存在月份合約：符號若帶到期月寫法，即該家錯把期貨的寫法套到本品種上。
        misread = sorted({f"{m}.{s}" for m, s in zip(frame["market"], frame["symbol"])
                          if classify_symbol(m, s) == FUTURE})
        checks.append(("股票／指數符號不帶到期月寫法", not misread, ",".join(misread[:6]) or "無"))
    return checks


def raw_checks(unified: pd.DataFrame, result: dict) -> list[tuple[str, bool, str]]:
    """raw=True：同一請求只換欄位與格式，取數範圍不變，故行數不少於去重後的統一格式。"""
    frame, columns = result["data"], list(result["data"].columns)
    unified_only = sorted({"source", "symbol_type"} & set(columns))
    return [
        ("信封仍只有三鍵", set(result) == {"status", "data", "message"}, str(sorted(result))),
        ("欄位即該券商原生鍵（不是 COLUMNS）", bool(columns) and columns != COLUMNS, ",".join(columns[:8])),
        ("不含由適配器構造的統一欄位", not unified_only, ",".join(unified_only)),
        ("不做去重：行數不少於統一格式", len(frame) >= len(unified), f"raw={len(frame)} 統一={len(unified)}"),
    ]


def main() -> dict:
    checks: list[tuple[str, bool, str]] = []
    counts: dict[str, dict[str, int]] = {}

    for name in BROKERS:
        with Brokery(sources=(name,)) as b:
            declared = set(b.adapters()[name].capabilities)
            checks.append((f"{name} 的能力聲明與實測一致", declared == DECLARED[name],
                           ",".join(sorted(declared)) or "無"))
            for symbol_type, (method, args) in SAMPLES.items():
                result = getattr(b, method)(args)
                frame = result["data"]
                counts.setdefault(name, {})[symbol_type] = len(frame)
                print(f"\n===== {name} {method} status={result['status']} "
                      f"rows={len(frame)} message={result['message']}")
                if symbol_type in DECLARED[name]:
                    if not result["status"]:
                        checks.append((f"{name} {symbol_type} 已聲明即應返回", False, result["message"]))
                        continue
                    print(frame.head(3).to_string())
                    checks += [(f"{name} {symbol_type}：{label}", passed, detail)
                               for label, passed, detail in row_checks(name, symbol_type, frame)]
                    checks.append((f"{name} {symbol_type} 有實際條目", not frame.empty, result["message"]))
                    # 同一請求再取一次 raw：能力、範圍與語義都不變，只有欄位與值換成上游原樣。
                    raw = getattr(b, method)(args, raw=True)
                    print(f"\n===== {name} {method} raw=True status={raw['status']} "
                          f"rows={len(raw['data'])} columns={list(raw['data'].columns)}")
                    checks += [(f"{name} {symbol_type} raw：{label}", passed, detail)
                               for label, passed, detail in raw_checks(frame, raw)]
                else:
                    # 未聲明即不得以空表冒充支援：必須由 core 明確拒绝，令 UI 能顯示「不提供此清單」。
                    checks.append((f"{name} {symbol_type} 未聲明即明確拒绝（no_source）",
                                   not result["status"] and result["message"].startswith("no_source"),
                                   result["message"]))
                    raw = getattr(b, method)(args, raw=True)
                    checks.append((f"{name} {symbol_type} raw 同樣明確拒绝（能力不受 raw 影響）",
                                   not raw["status"] and raw["message"].startswith("no_source"),
                                   raw["message"]))

    # 跨券商：四家同時取期貨，欄位契約必須完全相同，且同一合約不重複列（去重以主場優先）。
    with Brokery() as b:
        combined = b.list_futures(("ES",))
    frame = combined["data"]
    print(f"\n===== 四家合併期貨清單 status={combined['status']} rows={len(frame)} "
          f"message={combined['message']}")
    print(frame[["code", "symbol", "exchange", "currency", "source"]].head(20).to_string())
    checks.append(("四家合併仍為 COLUMNS", combined["status"] and list(frame.columns) == COLUMNS,
                   str(list(frame.columns))))
    keys = list(zip(frame["market"], frame["symbol_type"], frame["symbol"]))
    checks.append(("同一合約不重複列", len(keys) == len(set(keys)), f"{len(keys)} 列"))
    # 去重後某家可以完全唔見咗：佗提供嘅合約全部已被別家覆蓋即只留一份（實測 webull 嘅 ES 兩個月
    # 與 Tiger 逐欄相同，message 仍為 ok，即唔係失敗）。故只核對來源標記合法且確實跨多家。
    got = set(frame["source"])
    checks.append(("每行的 source 均為已啟用的券商", got <= set(BROKERS), ",".join(sorted(got))))
    checks.append(("合併結果確實跨多家", len(got) >= 2, ",".join(sorted(got))))

    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）")
    failed = [label for label, passed, _ in checks if not passed]
    if failed:
        return {"status": False, "data": frame, "message": "失敗：" + "；".join(failed)}
    summary = "，".join(f"{name} " + "/".join(str(counts[name][t]) for t in (STOCK, FUTURE, INDEX))
                        for name in BROKERS)
    return {"status": True, "data": frame,
            "message": f"{len(checks)} 項檢查全過：四家標的清單格式統一（條數 股票/期貨/指數："
                       f"{summary}）；未聲明品種一律明確拒绝"}


if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] else 1)
