"""富途全量代碼清單的離線存放：取得 CODES 後寫入離線資料目錄，並讀回核對。

以腳本方式直接執行：python brokery/acceptance/run_futu_codes_store.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import pandas as pd

from brokery import Brokery, store

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 220)

DATASET = store.codes_dataset("futu")
MARKETS = ("HK", "US")


def main() -> dict:
    with Brokery(sources=("futu",)) as b:
        result = b.list_all(MARKETS)
    if not result["status"]:
        print(f"status=False message={result['message']}")
        return result

    data = result["data"]
    path = store.save_frame(DATASET, data, source="futu", note=f"{'/'.join(MARKETS)} 全量 CODES")
    stored = store.load_frame(DATASET)  # 離線讀回，確認存放內容完整
    result["status"] = len(stored) == len(data) and list(stored.columns) == list(data.columns)
    result["message"] = (
        f"{len(stored)} 條 CODES 已存放 → {path}"
        if result["status"]
        else f"讀回核對失敗：存放 {len(stored)} 條 ≠ 取得 {len(data)} 條"
    )
    print(f"status={result['status']} message={result['message']}")
    print(store.load_meta(DATASET))
    print(stored.head(10))  # 離線讀回的內容（前 10 行）
    return result


if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] else 1)
