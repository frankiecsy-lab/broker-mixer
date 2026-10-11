"""驗收券商開關喜好（BROKER 管理頁的後端口徑）：

* 喜好為一個本地 JSON 檔（<data_dir>/broker_prefs.json），只記「被停用的家」；檔不存在或內容不可讀
  即全部生效，因此不需要遷移；寫入為原子（不留 .tmp）；
* 檔只由調用方（閘道）讀寫，core 只接受 Brokery(disabled=...)：因此逐家取數的腳本與離線分析不受
  界面上的開關影響，也不會因為讀檔而不可重現；
* 被停用者一律不經過它：get_kline／stream_kline／清單／get_accounts／get_brokers／convert 全部返回
  broker_disabled，且存根適配器完全沒有被呼叫；省略 broker 的多券商路徑亦只向生效者取數；
* 不存在與已停用要分清楚：前者仍是 unknown_source；全部停用時為 no_source 並點名被停用者，不砌出
  「已啟用的券商（）」這種空列表；
* get_broker_prefs 一律列出全部可用券商（含被停用與未配置者），否則該頁無法把它重新啟用；
  set_broker_enabled 即時生效，不需重建 Brokery（既有連線不會變成孤兒）。

以進程內存根券商與臨時資料目錄進行，不需要任何連線，也不觸及用戶實際的喜好檔。

以腳本方式直接執行：
    python brokery/acceptance/run_broker_prefs.py
"""
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import pandas as pd

import brokery.core as core
from brokery import Brokery, prefs
from brokery.brokers.base import ACCOUNT_COLUMNS, K_COLUMNS, SymbolBroker
from brokery.codes import FUTURE, INDEX, STOCK

ALL_TYPES = frozenset({STOCK, FUTURE, INDEX})
TYPED = (STOCK, FUTURE, INDEX)
TMP_DIR = Path(tempfile.mkdtemp(prefix="brokery_prefs_"))
os.environ["BROKERY_DATA_DIR"] = str(TMP_DIR)  # 不觸及用戶實際的喜好檔


class Stub(SymbolBroker):
    """存根券商：只記錄被呼叫了哪些方法，不連任何券商。"""

    source = "stubone"
    capabilities = ALL_TYPES
    kline_symbol_types = TYPED
    autypes = ("none",)
    stream_ktypes = ("1m",)
    stream_autypes = ("none",)
    acc_types = ("cash",)

    def __init__(self) -> None:
        self.seen: list[str] = []

    def krow(self, code: str) -> dict:
        return dict(zip(K_COLUMNS, [code, 1_760_000_000, "2026-10-09 09:30:00",
                                    100.0, 101.0, 99.0, 100.5, 10, 1005.0, self.source]))

    def list_stocks(self, markets, *, raw=False):
        self.seen.append("list_stocks")
        return [self.make_row("US.NVDA", f"{self.source} NVDA", "US", "NVDA", STOCK, "USD", "TEST")]

    def list_indices(self, seeds, *, raw=False):
        self.seen.append("list_indices")
        return [self.make_row("HK.HSI", f"{self.source} HSI", "HK", "HSI", INDEX, "USD", "TEST")]

    def to_contract(self, code: str) -> dict:
        self.seen.append("to_contract")
        return {"code": code, "raw_code": code, "contract": type("C", (), {"exchange": "TEST"})()}

    def get_kline(self, code, ktype, count, autype, *, raw=False):
        self.seen.append("get_kline")
        return [self.krow(code)]

    def stream_kline(self, codes, ktype, count, autype, seconds, on_update, *, raw=False):
        self.seen.append("stream_kline")
        return {code: [self.krow(code)] for code in codes}

    def get_accounts(self, currency=None, *, raw=False):
        self.seen.append("get_accounts")
        row = dict.fromkeys(ACCOUNT_COLUMNS)
        row.update({"source": self.source, "account_id": f"{self.source}-1", "acc_type": "cash",
                    "status": "active", "currency": "USD"})
        return [row]


class StubTwo(Stub):
    source = "stubtwo"


def main() -> dict:
    checks: list[tuple[str, bool, str]] = []

    def check(label: str, passed: bool, detail: str = "") -> None:
        checks.append((label, bool(passed), str(detail)))

    original = dict(core.BROKERS)
    created: dict[str, Stub] = {}

    def factory(cls):
        """建立存根並留低實例：被停用者唔喺 adapters() 內，唯有咁先验到佢完全冇被呼叫。"""
        def make() -> Stub:
            created[cls.source] = inst = cls()
            return inst
        return make

    core.BROKERS.update({cls.source: factory(cls) for cls in (Stub, StubTwo)})
    try:
        check("檔不存在即全部生效（無遷移動作）",
              prefs.load_disabled() == [] and not prefs.prefs_path().exists(),
              str(prefs.prefs_path()))

        path = prefs.save_disabled(["stubtwo", "STUBTWO", ""])
        check("save_disabled 只記被停用者、去重後可讀回、不留 .tmp",
              prefs.load_disabled() == ["stubtwo"] and not path.with_name(path.name + ".tmp").exists(),
              f"{prefs.load_disabled()} {path.read_text(encoding='utf-8')!r}")

        path.write_text("不是 JSON", encoding="utf-8")
        check("檔內容不可讀即全部生效（不擲出）", prefs.load_disabled() == [], path.read_text()[:20])
        path.unlink()

        with Brokery(sources=("stubone", "stubtwo"), disabled=("stubtwo",)) as b:
            one, two = created["stubone"], created["stubtwo"]

            check("disabled 後 sources()／adapters() 不再包含被停用者",
                  b.sources() == ["stubone"] and list(b.adapters()) == ["stubone"],
                  f"{b.sources()} {list(b.adapters())}")

            refused = {}
            for label, call in (
                ("get_kline", lambda: b.get_kline("HK.HSImain", "1m", 5, broker="stubtwo", autype="none")),
                ("stream_kline", lambda: b.stream_kline("HK.HSImain", "1m", 5, broker="stubtwo",
                                                        autype="none", seconds=0)),
                ("list_stocks", lambda: b.list_stocks(broker="stubtwo")),
                ("get_accounts", lambda: b.get_accounts(broker="stubtwo")),
                ("get_brokers", lambda: b.get_brokers(broker="stubtwo")),
                ("convert", lambda: b.convert("US.NVDA", "stubtwo")),
            ):
                refused[label] = call()
            check("被停用者一律 broker_disabled（六條路徑口徑一致）",
                  all(not res["status"] and res["message"].startswith("broker_disabled: stubtwo")
                      for res in refused.values()),
                  "；".join(f"{k}={v['message']}" for k, v in refused.items()))
            check("所有動作都不經過被停用者（存根完全沒被呼叫）",
                  two.seen == [], f"stubtwo.seen={two.seen}")

            unknown = b.get_kline("HK.HSImain", "1m", 5, broker="nope", autype="none")
            check("不存在與已停用分清楚：前者仍是 unknown_source",
                  not unknown["status"] and unknown["message"].startswith("unknown_source: nope")
                  and "stubone" in unknown["message"], unknown["message"])

            one.seen.clear()
            both = b.list_stocks()
            check("省略 broker 的多券商路徑只向生效者取數",
                  both["status"] and set(both["data"]["source"]) == {"stubone"}
                  and one.seen == ["list_stocks"] and two.seen == [],
                  f"stubone={one.seen} stubtwo={two.seen} {both['message']}")

            accounts = b.get_accounts()
            check("get_accounts 省略 broker 時亦跳過被停用者",
                  accounts["status"] and set(accounts["data"]["source"]) == {"stubone"},
                  accounts["message"])

            prefs_frame = b.get_broker_prefs()
            rows = {row["source"]: row for row in prefs_frame["data"].to_dict("records")}
            check("get_broker_prefs 列出全部券商（含被停用者），否則該頁無法重新啟用",
                  prefs_frame["status"]
                  and list(prefs_frame["data"].columns) == core.PREF_COLUMNS
                  and {"stubone": True, "stubtwo": False}.items() <= {s: r["enabled"]
                                                                      for s, r in rows.items()}.items(),
                  prefs_frame["data"].to_string())

            with Brokery(sources=("stubone", "stubtwo"), disabled=("stubone", "stubtwo")) as off:
                empty = off.get_brokers()
                check("全部停用即 no_source 並點名被停用者（不砌出空列表）",
                      not empty["status"] and empty["message"].startswith("no_source")
                      and "stubone" in empty["message"] and "stubtwo" in empty["message"]
                      and "（）" not in empty["message"], empty["message"])
                check("全部停用時清單與戶口同樣是 no_source（不是空表冒充成功）",
                      not off.list_stocks()["status"]
                      and off.list_stocks()["message"].startswith("no_source")
                      and not off.get_accounts()["status"],
                      f"{off.list_stocks()['message']} {off.get_accounts()['message']}")

            switched = b.set_broker_enabled(["stubone", "stubtwo"])
            check("set_broker_enabled 即時生效，不需重建（同一適配器實例仍可取數）",
                  switched["status"] and b.sources() == ["stubone", "stubtwo"]
                  and b.adapters()["stubtwo"] is two
                  and b.get_kline("HK.HSImain", "1m", 5, broker="stubtwo", autype="none")["status"],
                  f"{b.sources()} {b.get_kline('HK.HSImain', '1m', 5, broker='stubtwo', autype='none')['message']}")

            rejected = b.set_broker_enabled(["stubone", "nope"])
            check("set_broker_enabled 含未知名稱即拒絕，狀態不變",
                  not rejected["status"] and rejected["message"].startswith("unknown_source")
                  and b.sources() == ["stubone", "stubtwo"],
                  f"{rejected['message']} {b.sources()}")

            check("set_broker_enabled 停用後生效集合即時縮細",
                  b.set_broker_enabled(["stubone"])["status"] and b.sources() == ["stubone"],
                  f"{b.sources()}")

        saved = prefs.save_disabled(["stubtwo"])
        with Brokery(sources=("stubone", "stubtwo"), disabled=prefs.load_disabled()) as b:
            check("喜好檔可跨進程重現：讀檔後傳入即得同一生效集合",
                  b.sources() == ["stubone"], f"{saved} {b.sources()}")
            unconfigured = b.get_broker_prefs()["data"]
            row = unconfigured[unconfigured["source"] == "futu"].iloc[0]
            check("未配置（不在 API_SOURCES）者以 configured=False 列出並說明原因",
                  not bool(row["enabled"]) and not bool(row["configured"])
                  and "API_SOURCES" in str(row["detail"]), str(row.to_dict()))
            check("檔中記了不存在的家不影響生效集合",
                  prefs.save_disabled(["nope"]) and prefs.load_disabled() == ["nope"]
                  and Brokery(sources=("stubone",), disabled=prefs.load_disabled()).sources() == ["stubone"],
                  f"{prefs.load_disabled()}")
    finally:
        core.BROKERS.clear()
        core.BROKERS.update(original)
        shutil.rmtree(TMP_DIR, ignore_errors=True)

    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）")
    failed = [label for label, passed, _ in checks if not passed]
    if failed:
        return {"status": False, "data": pd.DataFrame(), "message": "失敗：" + "；".join(failed)}
    return {"status": True, "data": pd.DataFrame(),
            "message": f"{len(checks)} 項檢查全過：喜好檔（缺檔即全部生效、只記被停用者、原子寫、"
                       "不可讀時不擲出）、被停用者一律 broker_disabled 且完全不被呼叫、"
                       "unknown_source 與之分清、全部停用即 no_source 點名被停用者、"
                       "get_broker_prefs 列出全部、set_broker_enabled 即時生效不需重建"}


if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] else 1)
