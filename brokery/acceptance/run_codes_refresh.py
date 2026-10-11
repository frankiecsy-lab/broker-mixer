"""驗收離線快照的更新路徑：原子寫入與 .prev 備份、某品種明顯縮細時拒絕覆蓋、某品種本次取不到時
沿用舊快照該品種、取數失敗時保留原快照、差額回報、過期判定（CODES_MAX_AGE_HOURS），以及閘道只在
快照過舊時才在背景自動更新。

不連任何券商：list_all 以存根代替，寫盤與防護一律走真實代碼。資料集用 acceptance_ 前綴的臨時名稱，
跑完即刪，因此不會動到實際的 futu_codes 快照。

以腳本方式直接執行：
    python brokery/acceptance/run_codes_refresh.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import pandas as pd

from brokery import Brokery, store
from brokery.brokers.base import COLUMNS
from brokery.core import CODES_META_COLUMNS
from brokery_api.app import auto_refresh_codes

DATASET = "acceptance_codes_refresh"
TMP_FILE = store.frame_path(DATASET).with_name(store.frame_path(DATASET).name + store.TMP_SUFFIX)


def frame(**counts) -> pd.DataFrame:
    """按品種造出統一格式的行，欄位與 COLUMNS 一致（防護只讀 symbol_type，其餘為占位）。"""
    rows = [
        {"code": f"US.{kind}{i:04d}", "name": f"{kind}{i}", "market": "US", "symbol": f"{kind}{i}",
         "symbol_type": kind, "currency": "USD", "exchange": "US", "source": "stub"}
        for kind, count in counts.items() for i in range(count)
    ]
    return pd.DataFrame(rows, columns=list(COLUMNS))


def payload(**counts) -> dict:
    return {"status": True, "data": frame(**counts), "message": "ok: 存根清單"}


class StubList(Brokery):
    """只把 list_all 換成存根：返回預先準備的快照，其餘（縮細防護、沿用舊檔、差額、寫盤）走真實代碼。"""

    def __init__(self) -> None:
        super().__init__(sources=())
        self.payload = {"status": True, "data": pd.DataFrame(columns=list(COLUMNS)), "message": "ok"}

    def list_all(self, markets=None, *, broker=None, raw=False) -> dict:
        return self.payload


class SilentLog:
    def info(self, *args, **kwargs) -> None:
        pass

    warning = info


class CountingRefresh:
    """代替 Brokery 的自動更新調用點：只記錄被呼叫的次數，用來核對閘道的過期判定。"""

    def __init__(self) -> None:
        self.calls = 0

    def refresh_codes(self, **kwargs) -> dict:
        self.calls += 1
        return {"status": True, "data": pd.DataFrame(), "message": "ok: 存根更新"}


def main() -> dict:
    checks: list[tuple[str, bool, str]] = []

    def check(label: str, passed: bool, detail: str = "") -> None:
        checks.append((label, bool(passed), str(detail)))

    original, brokery = store.CODES_DATASET, StubList()
    store.CODES_DATASET = DATASET
    limit, api_app = None, sys.modules["brokery_api.app"]
    try:
        for path in (store.frame_path(DATASET), store.meta_path(DATASET), store.prev_path(DATASET)):
            path.unlink(missing_ok=True)

        brokery.payload = payload(STOCK=100, INDEX=10)
        first = brokery.refresh_codes()
        check("首次更新寫入快照", first["status"] and len(store.load_frame(DATASET)) == 110, first["message"])
        check("寫入不留 .tmp 中間檔", not TMP_FILE.exists(), str(TMP_FILE))
        check("首次更新沒有 .prev（無舊檔可保留）", not store.prev_path(DATASET).exists())
        meta = store.load_meta(DATASET)
        check("meta 記錄來源、行數與無錯誤", meta["rows"] == 110 and meta["source"] == "futu"
              and meta["last_refresh_error"] == "", str(meta)[:120])

        brokery.payload = payload(STOCK=105, INDEX=10)
        second = brokery.refresh_codes()
        check("增量更新回報逐品種差額", second["status"] and "STOCK 105（+5）" in second["message"],
              second["message"])
        check("舊快照保留為 .prev", store.prev_path(DATASET).exists()
              and len(store.load_frame(f"{DATASET}{store.PREV_SUFFIX}")) == 110, second["message"])

        brokery.payload = payload(STOCK=105, INDEX=1)
        shrunk = brokery.refresh_codes()
        check("某品種明顯縮細時拒絕覆蓋", not shrunk["status"] and "拒絕更新" in shrunk["message"],
              shrunk["message"])
        check("拒絕後快照不變", len(store.load_frame(DATASET)) == 115)
        check("拒絕原因記進 meta", store.load_meta(DATASET)["last_refresh_error"].startswith("rejected"),
              store.load_meta(DATASET)["last_refresh_error"])
        forced = brokery.refresh_codes(force=True)
        check("force=True 可越過防護", forced["status"] and len(store.load_frame(DATASET)) == 106,
              forced["message"])

        brokery.payload = payload(STOCK=105)
        carried = brokery.refresh_codes()
        check("某品種本次取不到時沿用舊快照該品種",
              carried["status"] and "沿用舊快照 1 條" in carried["message"]
              and len(store.load_frame(DATASET)) == 106, carried["message"])

        brokery.payload = {"status": False, "data": pd.DataFrame(columns=list(COLUMNS)),
                           "message": "no_source: 未启用任何来源"}
        failed = brokery.refresh_codes()
        check("取數失敗時保留原快照並明確回報",
              not failed["status"] and failed["message"].startswith("更新失敗")
              and len(store.load_frame(DATASET)) == 106, failed["message"])

        got = brokery.get_code_meta(DATASET)
        row = dict(zip(got["data"].columns, got["data"].iloc[0])) if got["status"] else {}
        check("get_code_meta 欄位為 CODES_META_COLUMNS 且為單行",
              got["status"] and list(got["data"].columns) == list(CODES_META_COLUMNS)
              and len(got["data"]) == 1, str(list(got["data"].columns)))
        check("get_code_meta 的行數與上次失敗原因與實際一致",
              row.get("rows") == 106 and row.get("last_refresh_error", "").startswith("failed"),
              str(row)[:160])

        fresh_meta = store.load_meta(DATASET)
        check("剛寫入的快照不判為過舊", store.meta_age(fresh_meta) < 5
              and not store.meta_stale(fresh_meta, 3600), str(store.meta_age(fresh_meta)))
        old = dict(fresh_meta, saved_at="2020-01-01T00:00:00+00:00")
        check("超過上限判為過舊", store.meta_stale(old, 3600))
        check("上限為 0 即不做自動更新", not store.meta_stale(old, 0))
        check("saved_at 缺失時視為最舊", store.meta_age({"saved_at": ""}) == float("inf"))

        counter, real_limit = CountingRefresh(), api_app.codes_max_age_seconds
        limit = real_limit
        api_app.codes_max_age_seconds = lambda: 0.0
        auto_refresh_codes(counter, SilentLog())
        check("CODES_MAX_AGE_HOURS=0 時不自動更新", counter.calls == 0, f"calls={counter.calls}")
        api_app.codes_max_age_seconds = lambda: 3600.0
        auto_refresh_codes(counter, SilentLog())
        check("快照新鮮時不自動更新", counter.calls == 0, f"calls={counter.calls}")
        store.update_meta(DATASET, saved_at="2020-01-01T00:00:00+00:00")
        auto_refresh_codes(counter, SilentLog())
        check("快照過舊時才自動更新", counter.calls == 1, f"calls={counter.calls}")
        store.meta_path(DATASET).unlink()
        auto_refresh_codes(counter, SilentLog())
        check("尚無快照時視為最舊並自動更新", counter.calls == 2, f"calls={counter.calls}")
    finally:
        if limit is not None:
            api_app.codes_max_age_seconds = limit
        store.CODES_DATASET = original
        brokery.close()
        for path in (store.frame_path(DATASET), store.meta_path(DATASET),
                     store.prev_path(DATASET), TMP_FILE):
            path.unlink(missing_ok=True)

    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）")
    failed = [label for label, passed, _ in checks if not passed]
    if failed:
        return {"status": False, "data": pd.DataFrame(), "message": "失敗：" + "；".join(failed)}
    return {"status": True, "data": pd.DataFrame(),
            "message": f"{len(checks)} 項檢查全過：原子寫入、縮細防護、沿用舊檔、過期判定與背景自動更新均符合（離線，未連券商）"}


if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] else 1)
