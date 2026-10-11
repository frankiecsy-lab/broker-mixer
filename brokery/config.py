"""集中管理環境配置。

所有可變配置（各券商後端地址、客戶端編號、超時、離線資料目錄）統一從項目根目錄的 .env 讀取，
禁止在程式碼中硬編碼。使用 pathlib 保證 Windows / Ubuntu / Docker 通用。
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


@dataclass(frozen=True)
class Settings:
    """各券商後端的連線參數與離線資料目錄。"""

    futu_host: str
    futu_port: int
    ib_host: str
    ib_port: int
    ib_client_id: int
    request_timeout: float
    data_dir: Path
    tiger_id: str
    tiger_account: str
    tiger_token: str
    tiger_public_key: str
    tiger_private_key: str
    webull_app_key: str
    webull_app_secret: str
    webull_sim_app_key: str
    webull_sim_app_secret: str
    webull_region_id: str
    webull_token_dir: Path
    api_host: str
    api_port: int
    api_key: str
    api_sources: tuple[str, ...]
    api_autype: str
    api_log_level: str
    api_log_dir: Path
    api_stream_seconds: float
    gui_host: str
    gui_port: int


def get_settings() -> Settings:
    """從項目根目錄的 .env 載入配置，缺漏時退回安全預設值。"""
    load_dotenv(ENV_FILE)
    return Settings(
        futu_host=os.getenv("FUTU_OPEND_HOST", "127.0.0.1"),
        futu_port=int(os.getenv("FUTU_OPEND_PORT", "11111")),
        ib_host=os.getenv("IB_HOST", "127.0.0.1"),
        ib_port=int(os.getenv("IB_PORT", "4001")),
        ib_client_id=int(os.getenv("IB_CLIENT_ID", "99")),
        request_timeout=float(os.getenv("IB_REQ_TIMEOUT", "30")),
        data_dir=_path("BROKERY_DATA_DIR", "brokery/data"),
        tiger_id=os.getenv("TIGER_ID", ""),
        tiger_account=os.getenv("TIGER_ACCOUNT", ""),
        tiger_token=os.getenv("TIGER_TOKEN", ""),
        tiger_public_key=os.getenv("TIGER_PUBLIC_KEY", ""),
        tiger_private_key=_read_key("TIGER_PRIVATE_KEY"),
        webull_app_key=os.getenv("WEBULL_APP_KEY", ""),
        webull_app_secret=os.getenv("WEBULL_APP_SECRET", ""),
        webull_sim_app_key=os.getenv("WEBULL_SIM_APP_KEY", ""),
        webull_sim_app_secret=os.getenv("WEBULL_SIM_APP_SECRET", ""),
        webull_region_id=os.getenv("WEBULL_REGION_ID", "hk"),
        webull_token_dir=_path("WEBULL_TOKEN_DIR", "brokery/data/webull_token"),
        api_host=os.getenv("API_HOST", "127.0.0.1"),
        api_port=int(os.getenv("API_PORT", "8181")),
        api_key=os.getenv("API_KEY", "").strip(),
        api_sources=_names("API_SOURCES", "futu,ib,tiger,webull"),
        api_autype=os.getenv("API_AUTYPE", "qfq"),
        api_log_level=os.getenv("API_LOG_LEVEL", "INFO"),
        api_log_dir=_path("API_LOG_DIR", "logs"),
        api_stream_seconds=float(os.getenv("API_STREAM_SECONDS", "300")),
        gui_host=os.getenv("GUI_HOST", "127.0.0.1"),
        gui_port=int(os.getenv("GUI_PORT", "8282")),
    )


def _names(name: str, default: str) -> tuple[str, ...]:
    """讀取逗號分隔的名單（如启用的券商）。未設定時用預設，設定為空即得空名單。"""
    raw = os.getenv(name, default)
    return tuple(item.strip() for item in raw.split(",") if item.strip())


def _read_key(name: str) -> str:
    """讀取金鑰：值為既有檔案路徑時讀其內容，否則視為金鑰內容本身。"""
    raw = os.getenv(name, "").strip()
    if not raw:
        return ""
    path = Path(raw)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.read_text(encoding="utf-8").strip() if path.is_file() else raw


def _path(name: str, default: str) -> Path:
    """讀取目錄配置：相對路徑以項目根目錄為基準，保證 Windows / Ubuntu / Docker 通用。"""
    raw = Path(os.getenv(name, default))
    return raw if raw.is_absolute() else PROJECT_ROOT / raw
