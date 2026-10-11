"""驗收 list_stocks／list_futures／list_indices 的 broker 與 markets 兩個參數（core 的調度口徑）：

* broker 指定只向一家取：未啟用即 unknown_source，該家未聲明該品種即 type_unsupported（並說明它只提供
  什麼），一律明確報錯，绝不靜靜改用別家湊數；
* markets 只過濾返回行的 market，用於沒有市場參數的接口（期貨／指數）；股票清單的市場由適配器自己處理，
  這一層只確保返回的確實是所請求的市場；
* 省略 markets 即用 DEFAULT_STOCK_MARKETS，把 None 傳進去也不會炸（曾經 list_stocks(None) 拋 TypeError，
  令控制台「標的清單全部取不到、一直讀取中」）；
* 取到了但全部不在指定市場即 empty_list，不以空表冒充成功；
* 一家拋異常時仍返回別家已取得的資料，並在 message 點名失敗的一家；
* raw=True 時同一個 markets 參數只改變欄位與格式：原生行沒有 market 欄位，故不按行過濾（否則一律被丟掉、
  誤判 empty_list），市場範圍一律由市場參數／種子保證，取數範圍不變。

以進程內存根券商進行，不需要任何連線，任何環境都能重複執行；四家真實券商的格式與能力邊界由
run_list_symbols.py 驗收。

以腳本方式直接執行：
    python brokery/acceptance/run_list_filter.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import pandas as pd

import brokery.core as core
from brokery import Brokery
from brokery.brokers.base import COLUMNS, SymbolBroker
from brokery.codes import FUTURE, INDEX, STOCK

ALL_TYPES = frozenset({STOCK, FUTURE, INDEX})
NO_STOCK = frozenset({FUTURE, INDEX})


class Stub(SymbolBroker):
    """存根券商：只記錄收到的參數，並返回兩行不同市場的假資料（不連任何券商）。"""

    source = "stuball"
    capabilities = ALL_TYPES

    def __init__(self) -> None:
        self.seen: list[tuple] = []

    def row(self, market: str, symbol: str, symbol_type: str) -> dict:
        return self.make_row(f"{market}.{symbol}", f"{self.source} {symbol}", market, symbol,
                             symbol_type, "USD", "TEST")

    def list_stocks(self, markets, *, raw=False):
        self.seen.append(("stocks", tuple(markets)))
        if raw:  # 原生行沒有 market 欄位：市場範圍由參數交給適配器自己保證
            return [{"symbol": f"S{market}", "full_name": f"{self.source} S{market}"} for market in markets]
        return [self.row(market, f"S{market}", STOCK) for market in markets]

    def list_futures(self, seeds, *, raw=False):
        self.seen.append(("futures", tuple(seeds)))
        if raw:  # 原生行只有種子所屬市場的標記，沒有統一的 market 欄位
            return [{"seed_market": seed.market, "exchange": "TEST"} for seed in seeds]
        return [self.row("US", "ES", FUTURE), self.row("SG", "CN", FUTURE)]

    def list_indices(self, seeds, *, raw=False):
        self.seen.append(("indices", tuple(seeds)))
        if raw:
            return [{"seed_market": seed.market, "exchange": "TEST"} for seed in seeds]
        return [self.row("US", "SPX", INDEX), self.row("HK", "HSI", INDEX)]


class NoStock(Stub):
    source = "nostock"
    capabilities = NO_STOCK


class Broken(Stub):
    source = "broken"

    def list_indices(self, seeds, *, raw=False):
        self.seen.append(("indices", tuple(seeds)))
        raise ConnectionError("存根取不到")


def main() -> dict:
    checks: list[tuple[str, bool, str]] = []

    def check(label: str, passed: bool, detail: str = "") -> None:
        checks.append((label, bool(passed), str(detail)))

    original = dict(core.BROKERS)
    core.BROKERS.update({"stuball": Stub, "nostock": NoStock, "broken": Broken})
    try:
        with Brokery(sources=("stuball", "nostock")) as b:
            all_stub, no_stock = b.adapters()["stuball"], b.adapters()["nostock"]

            got = b.list_stocks(broker="stuball")
            check("broker 指定即只向該家取（返回全為該家）",
                  got["status"] and set(got["data"]["source"]) == {"stuball"},
                  ",".join(sorted(set(got["data"]["source"]))))
            check("broker 指定時不順帶向別家取（只呼叫該家一次）",
                  all_stub.seen == [("stocks", core.DEFAULT_STOCK_MARKETS)] and no_stock.seen == [],
                  f"stuball={all_stub.seen} nostock={no_stock.seen}")

            refused = b.list_stocks(broker="nostock")
            check("該家未聲明該品種即 type_unsupported（並說明只提供什麼）",
                  not refused["status"] and refused["message"].startswith("type_unsupported: nostock")
                  and FUTURE in refused["message"] and refused["data"].empty, refused["message"])
            unknown = b.list_indices(broker="nope")
            check("broker 未啟用即 unknown_source（點名已啟用者）",
                  not unknown["status"] and unknown["message"].startswith("unknown_source: nope")
                  and "stuball" in unknown["message"], unknown["message"])

            all_stub.seen.clear()
            defaulted = b.list_stocks()
            check("省略 markets 即用 DEFAULT_STOCK_MARKETS（None 不會傳進去炸開）",
                  defaulted["status"] and all_stub.seen == [("stocks", core.DEFAULT_STOCK_MARKETS)]
                  and set(defaulted["data"]["market"]) == set(core.DEFAULT_STOCK_MARKETS),
                  f"{all_stub.seen} 市場={sorted(set(defaulted['data']['market']))}")
            narrowed = b.list_stocks(("HK",))
            check("股票清單的市場由適配器處理，返回只含所請求的市場",
                  narrowed["status"] and all_stub.seen[-1] == ("stocks", ("HK",))
                  and set(narrowed["data"]["market"]) == {"HK"},
                  f"{all_stub.seen[-1]} 市場={sorted(set(narrowed['data']['market']))}")

            filtered = b.list_indices(markets=("US",))
            check("期貨／指數無市場參數，markets 按返回行的 market 過濾",
                  filtered["status"] and set(filtered["data"]["market"]) == {"US"}
                  and list(filtered["data"].columns) == COLUMNS,
                  f"市場={sorted(set(filtered['data']['market']))}")
            empty = b.list_indices(markets=("ZZ",))
            check("取到了但全部不在指定市場即 empty_list（不以空表冒充成功）",
                  not empty["status"] and empty["message"].startswith("empty_list") and "ZZ" in empty["message"],
                  empty["message"])

            # raw=True：原生行沒有 market 欄位，故不得按行過濾（否則一律被丟掉、誤判 empty_list）；
            # 市場範圍一律由參數/種子保證，取數範圍不變。
            raw_stocks = b.list_stocks(("HK",), broker="stuball", raw=True)
            check("股票清單 raw：市場仍由參數交給適配器，欄位為原生鍵且不做行過濾",
                  raw_stocks["status"] and all_stub.seen[-1] == ("stocks", ("HK",))
                  and list(raw_stocks["data"].columns) == ["symbol", "full_name"]
                  and list(raw_stocks["data"]["symbol"]) == ["SHK"],
                  f"{all_stub.seen[-1]} {list(raw_stocks['data'].columns)} {raw_stocks['message']}")
            raw_indices = b.list_indices(markets=("US",), broker="stuball", raw=True)
            check("指數清單 raw：市場範圍由種子保證（不做行過濾，故不會誤判 empty_list）",
                  raw_indices["status"] and list(raw_indices["data"].columns) == ["seed_market", "exchange"]
                  and set(raw_indices["data"]["seed_market"]) == {"US"},
                  f"{list(raw_indices['data'].columns)} "
                  f"{sorted(set(raw_indices['data']['seed_market']))} {raw_indices['message']}")
            raw_futures = b.list_futures(("ES",), markets=("US",), broker="stuball", raw=True)
            check("期貨清單 raw：不請求的市場根本不發出請求（範圍由種子保證）",
                  raw_futures["status"]
                  and all(seed.market == "US" for seed in all_stub.seen[-1][1])
                  and set(raw_futures["data"]["seed_market"]) == {"US"},
                  f"種子={[s.market for s in all_stub.seen[-1][1]]} {raw_futures['message']}")
            check("省略 markets 時 raw 仍用預設市場",
                  b.list_stocks(broker="stuball", raw=True)["status"]
                  and all_stub.seen[-1] == ("stocks", core.DEFAULT_STOCK_MARKETS),
                  f"{all_stub.seen[-1]}")

            both = b.list_futures(("ES",), markets=("US",), broker="stuball")
            check("broker 與 markets 同時指定：只向該家取，再按市場過濾",
                  both["status"] and set(both["data"]["source"]) == {"stuball"}
                  and set(both["data"]["market"]) == {"US"} and list(both["data"]["symbol"]) == ["ES"],
                  f"{both['data'][['source', 'market', 'symbol']].to_dict('records')}")

        with Brokery(sources=("stuball", "broken")) as b:
            partial = b.list_indices()
            check("一家失敗仍返回別家資料，並在 message 點名該家",
                  partial["status"] and set(partial["data"]["source"]) == {"stuball"}
                  and "broken: ConnectionError" in partial["message"], partial["message"])
    finally:
        core.BROKERS.clear()
        core.BROKERS.update(original)

    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）")
    failed = [label for label, passed, _ in checks if not passed]
    if failed:
        return {"status": False, "data": pd.DataFrame(), "message": "失敗：" + "；".join(failed)}
    return {"status": True, "data": pd.DataFrame(),
            "message": f"{len(checks)} 項檢查全過：broker 能力閘（unknown_source／type_unsupported）、"
                       "markets 按行過濾（empty_list）、省略 markets 用預設市場、一家失敗仍返回別家資料、"
                       "raw 時市場範圍由參數／種子保證（不做行過濾）"}


if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] else 1)
