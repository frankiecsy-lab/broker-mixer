"""券商開關喜好：一個本地 JSON 檔，三個界面共用。

檔內只記「被停用的家」，不記全部名單：改了 .env 的 API_SOURCES 之後檔也不會變舊（新增的家默認
生效）。檔不存在或內容不可讀即全部生效，即等於沒有設定過，因此不需要遷移動作。

讀寫只發生在閘道：core 只接受 Brokery(disabled=...) 參數，因此逐家取數的腳本與離線分析不受
用戶在界面上關掉的開關影響，也不會因為讀檔而不可重現。
"""
from __future__ import annotations

import json
import os
from collections.abc import Iterable
from pathlib import Path

from .store import TMP_SUFFIX, data_dir

PREFS_FILE = "broker_prefs.json"


def prefs_path() -> Path:
    """喜好檔位置（與離線 CODES 同目錄，由 .env 的 BROKERY_DATA_DIR 決定）。"""
    return data_dir() / PREFS_FILE


def load_disabled() -> list[str]:
    """被停用的券商名。檔不存在或內容不可讀時返回空列表，即全部生效。"""
    try:
        payload = json.loads(prefs_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    names = payload.get("disabled") if isinstance(payload, dict) else None
    return [str(name) for name in names] if isinstance(names, list) else []


def save_disabled(disabled: Iterable[str]) -> Path:
    """原子寫入被停用的家（先寫 .tmp 再 os.replace）：寫到一半中斷不可毀掉既有喜好。"""
    names = sorted({str(name).strip().lower() for name in disabled if str(name).strip()})
    path = prefs_path()
    tmp = path.with_name(path.name + TMP_SUFFIX)
    tmp.write_text(json.dumps({"disabled": names}, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)
    return path
