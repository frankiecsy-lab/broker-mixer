"""離線顯示已存放的 CODES：經 Brokery.get_code 讀回，不連 OpenD 亦不連 IB。
另核對 get_code_meta 所報的行數與距今時間與實際存放的一致——三個介面顯示的「快照幾舊」即由此而來。

以腳本方式直接執行：
    python brokery/acceptance/run_get_codes.py            # 全部
    python brokery/acceptance/run_get_codes.py FUTURE     # 只顯示某類型（STOCK/FUTURE/INDEX）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import pandas as pd

from brokery import Brokery, store
from brokery.core import CODES_META_COLUMNS

# 統一欄位共 8 個，pandas 預設會隱藏中間欄位，故設定為顯示全部欄位。
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 220)

DATASET = store.CODES_DATASET


def main(symbol_type: str = "") -> dict:
    with Brokery() as b:
        result = b.get_code(DATASET)
    if not result["status"]:
        print(f"status=False message={result['message']}")
        return result

    data = result["data"]
    if symbol_type:
        data = data[data["symbol_type"] == symbol_type]
        if data.empty:
            result["status"] = False
            result["message"] = f"離線資料中沒有 symbol_type={symbol_type}"
            print(f"status=False message={result['message']}")
            return result

    meta = store.load_meta(DATASET)
    with Brokery() as b:
        got = b.get_code_meta(DATASET)
    row = dict(zip(got["data"].columns, got["data"].iloc[0])) if got["status"] else {}
    if row.get("rows") != meta["rows"] or list(got["data"].columns) != list(CODES_META_COLUMNS):
        result["status"] = False
        result["message"] = f"get_code_meta 與實際存放不一致：{str(row)[:160]}"
        print(f"status=False message={result['message']}")
        return result
    result["data"] = data
    result["message"] = (
        f"離線讀回 {len(data)} 條 CODES（存放 {meta['rows']} 條，來源 {meta['source']}，"
        f"寫入時間 {meta['saved_at']}，距今 {row['age_seconds']} 秒，"
        f"{'已過舊' if row['stale'] else '仍屬新鮮'}）"
    )
    print(f"status={result['status']} message={result['message']}")
    print(data)  # pandas 預設截斷，僅顯示頭尾各 30 行
    return result


if __name__ == "__main__":
    raise SystemExit(0 if main((sys.argv[1] if len(sys.argv) > 1 else "").upper())["status"] else 1)
