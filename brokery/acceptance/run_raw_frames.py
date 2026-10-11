"""驗收連券商功能的 raw=True 契約（離線：以存根適配器，不連任何券商）。raw 只改變欄位與格式，
不改變取數範圍與語義。核對：

* 信封一律只有 status／data／message 三鍵；raw=True 時 data 即該券商自帶的欄位與值（不另加第四鍵）；
* raw=False 時欄位仍嚴格為 COLUMNS／K_COLUMNS／ACCOUNT_COLUMNS，去重與行過濾照常；
* raw=True 時跳過去重與按統一欄位的行過濾，故同一合約的多列原生行全部保留；但取數範圍仍不變
  （市場參數原樣交給適配器、期貨的市場範圍由種子保證、幣種過濾由適配器以原生欄位執行）；
* raw=True 且明確要求 acc_type 時一律拒绝（原生行沒有 acc_type，不能假裝已過濾）；
* 多來源時 raw 欄位為各來源鍵的首見聯集；失敗時仍為三鍵信封且空表不帶欄位；
* raw 的串流合併（NativeBars）與 BarMerger 對外語義一致：只在最新一根有變化時回報、只留最近 count
  根、按原生時間升序（各券商時間欄位形態不同，故數字與文字各自成組）。

以腳本方式直接執行：
    python brokery/acceptance/run_raw_frames.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

from brokery import core  # noqa: E402
from brokery.brokers.base import (  # noqa: E402
    ACCOUNT_COLUMNS,
    CAP_FUTURE,
    CAP_STOCK,
    COLUMNS,
    K_COLUMNS,
    NativeBars,
    SymbolBroker,
    native_columns,
)

# 富途 basicinfo 那類原生列：欄位名與值一律上游原樣，且刻意含兩列相同的合約（統一格式會被去重）。
NATIVE_STOCK = [{"symbol": "00700", "full_name": "騰訊控股", "last_trade_time": "2026-10-09 16:08:00"},
                {"symbol": "00700", "full_name": "騰訊控股", "last_trade_time": "2026-10-09 16:08:00"}]
NATIVE_FUTURE = [{"contract_code": "HSI2512", "exchange": "HKEX", "contract_month": "202512"}]
NATIVE_BAR = [{"time_key": "2026-10-08 09:30:00", "open": 1, "close": 2},
              {"time_key": "2026-10-09 09:30:00", "open": 2, "close": 3}]
NATIVE_ACC = [{"account": "U1", "tag": "NetLiquidation", "value": "1000", "currency": "USD"},
              {"account": "U1", "tag": "Cash", "value": "900", "currency": "HKD"}]
UNIFIED_STOCK = [
    {"code": "HK.00700", "name": "騰訊控股", "market": "HK", "symbol": "00700", "symbol_type": "stock",
     "currency": "HKD", "exchange": "HKEX", "source": "stub"},
    {"code": "HK.00700", "name": "騰訊控股", "market": "HK", "symbol": "00700", "symbol_type": "stock",
     "currency": "HKD", "exchange": "HKEX", "source": "stub"}]
UNIFIED_ACCOUNT = dict(zip(ACCOUNT_COLUMNS, ["stub", "U1", "margin", "ACTIVE", "USD",
                                            1000.0, 900.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]))


class Stub(SymbolBroker):
    """存根適配器：raw 與非 raw 各自返回對應格式，並記錄收到的參數，以核對取數範圍沒有改變。"""

    source = "stub"
    capabilities = frozenset({CAP_STOCK, CAP_FUTURE})
    autypes = ("none",)
    stream_ktypes = ("1m",)
    stream_autypes = ("none",)
    acc_types = ("margin",)

    def list_stocks(self, markets, *, raw=False):
        self.seen_markets = markets
        return list(NATIVE_STOCK) if raw else [dict(row) for row in UNIFIED_STOCK]

    def list_futures(self, seeds, *, raw=False):
        self.seen_seeds = [(seed.market, seed.root) for seed in seeds]
        if raw:
            return list(NATIVE_FUTURE)
        return [self.make_row(code="HK.HSImain", name="HSI", market="HK", symbol="HSImain",
                              symbol_type="future", currency="HKD", exchange="HKEX")]

    def get_kline(self, code, ktype, count, autype, *, raw=False):
        return list(NATIVE_BAR) if raw else [dict(zip(K_COLUMNS, [code] * len(K_COLUMNS)))]

    def stream_kline(self, codes, ktype, count, autype, seconds, on_update, *, raw=False):
        collected = {}
        for code in codes:
            rows = list(NATIVE_BAR) if raw else [dict(zip(K_COLUMNS, [code] * len(K_COLUMNS)))]
            collected[code] = rows
            if on_update is not None:  # 與各適配器一致：core 可傳入 None（只要起點，不接推送）
                on_update(code, rows)
        return collected

    def get_accounts(self, currency=None, *, raw=False):
        self.seen_currency = currency
        if not raw:
            return [dict(UNIFIED_ACCOUNT)]
        return [row for row in NATIVE_ACC if currency is None or row["currency"] == currency]


class Stub2(SymbolBroker):
    """第二間存根：原生欄位與第一間部分重疊，用以核對多來源的欄位為首見聯集。"""

    source = "stub2"
    capabilities = frozenset({CAP_STOCK})
    autypes = ("none",)
    stream_ktypes = ("1m",)
    stream_autypes = ("none",)
    acc_types = ("margin",)

    def list_stocks(self, markets, *, raw=False):
        row = {"symbol": "00005", "full_name": "匯豐控股", "industry": "銀行"}
        return [row] if raw else [self.make_row(code="HK.00005", name="匯豐控股", market="HK", symbol="00005",
                                                symbol_type="stock", currency="HKD", exchange="HKEX")]


core.BROKERS["stub"] = Stub
core.BROKERS["stub2"] = Stub2
bk = core.Brokery(sources=("stub",), autype="none")
bk2 = core.Brokery(sources=("stub", "stub2"), autype="none")


def main() -> dict:
    checks: list[tuple[str, bool, str]] = []

    def check(label: str, passed: bool, detail: str = "") -> None:
        checks.append((label, bool(passed), str(detail)))

    # ---------------------------------------------------------------- 原生欄位順序與串流合併
    mixed = [{"b": 1}, {"a": 2, "b": 3}]
    check("native_columns 按各列鍵的首見順序合併（不排序、不憑空補欄位）",
          native_columns(mixed) == ["b", "a"], ",".join(native_columns(mixed)))
    check("native_columns 重複呼叫順序一致，且順序只跟數據不跟呼叫",
          native_columns(mixed) == native_columns(mixed) and native_columns(list(reversed(mixed))) == ["a", "b"]
          and native_columns([]) == [], f"{native_columns(mixed)} / {native_columns(list(reversed(mixed)))}")

    merger = NativeBars(2, "time")
    fired = []
    for bar in ({"time": "2026-10-08", "close": 1}, {"time": "2026-10-08", "close": 1},
                {"time": "2026-10-09", "close": 2}, {"time": "2026-10-10", "close": 3}):
        if merger.merge([bar]):
            fired.append(merger.frame())
    check("NativeBars 只在最新一根有變化時回報（同一幀不重複送）",
          len(fired) == 3 and [len(f) for f in fired] == [1, 2, 2], [len(f) for f in fired])
    check("NativeBars 只留最近 count 根且按原生時間升序",
          [row["time"] for row in merger.frame()] == ["2026-10-09", "2026-10-10"],
          [row["time"] for row in merger.frame()])
    numeric = NativeBars(3, "time")
    numeric.merge([{"time": 9}, {"time": 10}, {"time": 100}])
    check("NativeBars 按原生時間排序：epoch 數按數值而非文字（各券商時間欄位形態不同）",
          [row["time"] for row in numeric.frame()] == [9, 10, 100], [row["time"] for row in numeric.frame()])

    # ---------------------------------------------------------------- raw 信封與欄位
    # 「統一格式專屬欄位」只指由適配器構造的鍵：code／market／acc_type 等在富途原生記錄裏本來就有
    # （寫法與值一律上游原樣），不得列在這裡。
    cases = [
        ("list_stocks", lambda raw: bk.list_stocks(["HK"], raw=raw), NATIVE_STOCK, ["symbol_type", "source"]),
        ("list_futures", lambda raw: bk.list_futures(markets=["HK"], raw=raw), NATIVE_FUTURE,
         ["symbol_type", "source"]),
        ("get_kline", lambda raw: bk.get_kline("HK.00700", "1m", 2, broker="stub", autype="none", raw=raw),
         NATIVE_BAR, ["ts", "source"]),
        ("stream_kline", lambda raw: bk.stream_kline("HK.00700", "1m", 2, broker="stub", autype="none",
                                                     seconds=0, raw=raw), NATIVE_BAR, ["ts", "source"]),
        ("get_accounts", lambda raw: bk.get_accounts(raw=raw), NATIVE_ACC, ["net_liquidation", "source"]),
    ]
    for label, call, native, unified_only in cases:
        res = call(True)
        check(f"{label} raw 信封仍只有三鍵（不另加第四鍵）", set(res) == {"status", "data", "message"}, sorted(res))
        check(f"{label} raw 的 data 欄位即該券商原生鍵", list(res["data"].columns) == list(native[0]),
              f"{res['message']} cols={list(res['data'].columns)}")
        check(f"{label} raw 行數不變", len(res["data"]) == len(native), len(res["data"]))
        leaked = [name for name in unified_only if name in res["data"].columns]
        check(f"{label} raw 不含統一格式專屬欄位", not leaked, ",".join(leaked))

    # ---------------------------------------------------------------- 非 raw 的契約不受影響
    unified = bk.list_stocks(["HK"])
    check("list_stocks 非 raw 欄位仍為 COLUMNS", list(unified["data"].columns) == COLUMNS,
          ",".join(unified["data"].columns))
    check("非 raw 仍按統一鍵去重（同一合約只留一列）", len(unified["data"]) == 1, len(unified["data"]))
    kline = bk.get_kline("HK.00700", "1m", 2, broker="stub", autype="none")
    check("get_kline 非 raw 欄位仍為 K_COLUMNS", list(kline["data"].columns) == K_COLUMNS,
          ",".join(kline["data"].columns))
    accounts = bk.get_accounts()
    check("get_accounts 非 raw 欄位仍為 ACCOUNT_COLUMNS", list(accounts["data"].columns) == ACCOUNT_COLUMNS,
          ",".join(accounts["data"].columns))

    # ---------------------------------------------------------------- 取數範圍與語義不變
    raw_stocks = bk.list_stocks(["HK"], raw=True)
    check("raw 跳過去重：同一合約的多列原生行全部保留", len(raw_stocks["data"]) == 2, len(raw_stocks["data"]))
    check("raw 時市場參數仍原樣交給適配器", bk.adapters()["stub"].seen_markets == ("HK",),
          bk.adapters()["stub"].seen_markets)
    seen = getattr(bk.adapters()["stub"], "seen_seeds", [])
    check("list_futures raw 的市場範圍由種子保證", bool(seen) and all(market == "HK" for market, _ in seen), seen)
    bad = bk.get_accounts(acc_type="cash", raw=True)
    check("get_accounts raw + 明確 acc_type 一律拒绝", not bad["status"] and "bad_acc_type" in bad["message"],
          bad["message"])
    usd = bk.get_accounts(currency="USD", raw=True)
    check("raw 時幣種過濾由適配器以原生欄位執行（core 不做行過濾）",
          bk.adapters()["stub"].seen_currency == "USD" and len(usd["data"]) == 1
          and list(usd["data"]["currency"]) == ["USD"], (usd["message"], list(usd["data"].columns)))
    both = bk2.list_stocks(["HK"], raw=True)
    check("多來源 raw 欄位為各來源鍵的首見聯集",
          both["status"] and list(both["data"].columns) == ["symbol", "full_name", "last_trade_time", "industry"]
          and len(both["data"]) == 3, (list(both["data"].columns), len(both["data"])))
    all_raw = bk.list_all(["HK"], raw=True)
    check("list_all raw 串接各類原生行（無該能力的來源不影響已取得的資料）",
          all_raw["status"] and len(all_raw["data"]) == 3
          and list(all_raw["data"].columns) == list(NATIVE_STOCK[0]) + list(NATIVE_FUTURE[0]),
          (len(all_raw["data"]), list(all_raw["data"].columns), all_raw["message"]))
    failed = bk.get_kline("HK.999999", "1m", 2, broker="nope", raw=True)
    check("raw 失敗信封仍為三鍵且空表不帶欄位（原生欄位無從得知）",
          set(failed) == {"status", "data", "message"} and not failed["status"]
          and list(failed["data"].columns) == [], list(failed["data"].columns))

    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）")
    missed = [label for label, passed, _ in checks if not passed]
    if missed:
        return {"status": False, "data": None, "message": "失敗：" + "；".join(missed)}
    return {"status": True, "data": None,
            "message": f"{len(checks)} 項檢查全過：raw 只改欄位與格式（信封仍三鍵、data 即原生欄位）、"
                       "非 raw 契約不變、取數範圍與語義不變、多來源欄位為首見聯集、失敗時空表無欄位"}


if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] else 1)
