"""多語文字：每個語言一個 JSON（locales/<語言碼>.json），運行時切換，不需重啟。

界面檔（.ui）內不寫任何文字，文字一律由本模組按鍵取；缺鍵時返回鍵名本身並記錄，令缺譯一眼可見，
不憑空造一句湊數。語言碼與界面顯示的語言名稱由 LANGUAGES 統一，不在各處硬寫。
"""
from __future__ import annotations

import json
from pathlib import Path

LOCALE_DIR = Path(__file__).with_name("locales")
LANGUAGES = {"zh-Hant": "繁體中文", "zh-Hans": "简体中文", "en": "English"}
DEFAULT_LANGUAGE = "zh-Hant"


def available() -> list[str]:
    """可用的語言碼（與 LANGUAGES 一致）。"""
    return list(LANGUAGES)


def load(language: str) -> dict:
    """讀出該語言的全部文字；檔不存在即明確報錯，不退回其他語言。"""
    if language not in LANGUAGES:
        raise ValueError(f"unknown_language: {language}；可用 {', '.join(LANGUAGES)}")
    path = LOCALE_DIR / f"{language}.json"
    if not path.is_file():
        raise ValueError(f"locale_missing: {path.name}（{language} 沒有對應的語言檔）")
    return json.loads(path.read_text(encoding="utf-8"))


class Translator:
    """按鍵取字。切換語言即換一份字庫，界面用同一組鍵，故不需重建窗口。"""

    def __init__(self, language: str = DEFAULT_LANGUAGE) -> None:
        self.missing: list[str] = []
        self.set_language(language)

    def set_language(self, language: str) -> None:
        self.language = language
        self._strings = load(language)

    def t(self, key: str, **fmt) -> str:
        text = self._strings.get(key)
        if text is None:
            self.missing.append(key)
            return key
        return text.format(**fmt) if fmt else text
