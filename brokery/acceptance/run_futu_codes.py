"""富途全量代碼清單：一次取得港美兩市的股票、期貨與指數，直接輸出所有 CODES。

以腳本方式直接執行：python brokery/acceptance/run_futu_codes.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import pandas as pd

from brokery import Brokery

# 統一欄位共 10 個，pandas 預設會隱藏中間欄位，故設定為顯示全部欄位。
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 220)

MARKETS = ("HK", "US")


def main() -> dict:
    with Brokery(sources=("futu",)) as b:
        result = b.list_all(MARKETS)
    if result["status"]:
        data = result["data"]
        result["message"] = f"{len(data)} 條 CODES：{data['symbol_type'].value_counts().to_dict()}"
    print(f"status={result['status']} message={result['message']}")
    print(result["data"])  # pandas 預設截斷，僅顯示頭尾各 30 行
    return result


if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] else 1)
