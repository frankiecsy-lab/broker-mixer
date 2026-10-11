"""離線資料存放層：把取得的 DataFrame 以 parquet 存到統一目錄，之後可離線讀回。

目錄由 .env 的 BROKERY_DATA_DIR 指定（預設主資料夾下的 brokery/data/）。每個資料集固定一檔
<name>.parquet，並附一份 <name>.meta.json 記錄行數、欄位、來源與寫入時間，
方便日後判斷資料是否過期。
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .config import get_settings

META_SUFFIX = ".meta.json"
PREV_SUFFIX = ".prev"
TMP_SUFFIX = ".tmp"

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


def prev_path(name: str) -> Path:
    """上一次成功存放的副本；本次寫入失敗或被拒絕時仍可回退。"""
    return data_dir() / f"{name}{PREV_SUFFIX}.parquet"


def save_frame(name: str, frame: pd.DataFrame, *, source: str = "", note: str = "") -> Path:
    """原子寫入 <name>.parquet（先寫 .tmp 再替換），舊檔保留為 <name>.prev.parquet。

    離線快照往往是唯一的離線副本，寫到一半中斷不應把它毀掉，故不直接覆蓋。
    """
    path = frame_path(name)
    tmp = path.with_name(path.name + TMP_SUFFIX)
    frame.to_parquet(tmp, index=False)
    if path.exists():
        os.replace(path, prev_path(name))
    os.replace(tmp, path)
    meta = {
        "name": name,
        "file": path.name,
        "rows": int(len(frame)),
        "columns": list(frame.columns),
        "source": source,
        "note": note,
        "last_refresh_error": "",
        "saved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    meta_path(name).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def update_meta(name: str, **fields) -> dict:
    """把指定欄位合併進既有 meta，不改动 parquet 資料。用於記錄更新失敗等原因。"""
    meta = load_meta(name)
    meta.update(fields)
    meta_path(name).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


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


def meta_age(meta: dict) -> float:
    """快照距今的秒數；saved_at 缺失或不可解析時返回 float('inf')，即視為最舊。"""
    try:
        saved = datetime.fromisoformat(str(meta.get("saved_at", "")))
    except ValueError:
        return float("inf")
    if saved.tzinfo is None:
        saved = saved.replace(tzinfo=timezone.utc)
    return max(0.0, (datetime.now(timezone.utc) - saved).total_seconds())


def meta_stale(meta: dict, max_age_seconds: float) -> bool:
    """快照是否已超過允許的最長_age。max_age_seconds <= 0 表示不做自動更新。"""
    if max_age_seconds <= 0:
        return False
    return meta_age(meta) > max_age_seconds


def list_stored() -> list[dict]:
    """列出目錄內所有已存放的資料集（按 meta 內容）。"""
    return [
        json.loads(p.read_text(encoding="utf-8"))
        for p in sorted(data_dir().glob(f"*{META_SUFFIX}"))
    ]
