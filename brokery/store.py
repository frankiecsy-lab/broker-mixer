"""離線資料存放層：把取得的 DataFrame 以 parquet 存到統一目錄，之後可離線讀回。

目錄由 .env 的 BROKERY_DATA_DIR 指定（預設主資料夾下的 brokery/data/）。每個資料集固定一檔
<name>.parquet，並附一份 <name>.meta.json 記錄行數、欄位、來源與寫入時間，
方便日後判斷資料是否過期。
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .config import get_settings

META_SUFFIX = ".meta.json"

# 代碼清單的資料集名稱（由 run_futu_codes_store.py 寫入，Brokery.get_code 預設讀此檔）
CODES_DATASET = "futu_codes"


class StoreError(RuntimeError):
    """離線資料不存在或不可讀。"""


def data_dir() -> Path:
    """離線資料目錄；不存在時建立。"""
    directory = get_settings().data_dir
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def frame_path(name: str) -> Path:
    return data_dir() / f"{name}.parquet"


def meta_path(name: str) -> Path:
    return data_dir() / f"{name}{META_SUFFIX}"


def save_frame(name: str, frame: pd.DataFrame, *, source: str = "", note: str = "") -> Path:
    """以 parquet 覆蓋寫入 <name>.parquet，並寫下同名 meta；返回檔案路徑。"""
    path = frame_path(name)
    frame.to_parquet(path, index=False)
    meta = {
        "name": name,
        "file": path.name,
        "rows": int(len(frame)),
        "columns": list(frame.columns),
        "source": source,
        "note": note,
        "saved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    meta_path(name).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_frame(name: str) -> pd.DataFrame:
    """讀回已存放的 DataFrame；未存放時拋 StoreError，避免以空表冒充「沒有」。"""
    path = frame_path(name)
    if not path.exists():
        raise StoreError(f"not_stored: {name}；{path} 不存在，請先執行對應的取得腳本")
    return pd.read_parquet(path)


def load_meta(name: str) -> dict:
    path = meta_path(name)
    if not path.exists():
        raise StoreError(f"not_stored: {name} 的 meta 不存在（{path}）")
    return json.loads(path.read_text(encoding="utf-8"))


def list_stored() -> list[dict]:
    """列出目錄內所有已存放的資料集（按 meta 內容）。"""
    return [
        json.loads(p.read_text(encoding="utf-8"))
        for p in sorted(data_dir().glob(f"*{META_SUFFIX}"))
    ]
