"""閘道日誌：控制台與滾動檔案並列，並保留最近若干條供網頁控制台顯示。

Brokery 的業務失敗（status=False）不抛異常，只寫入返回信封，因此必須由日誌記錄，否則伺服器端完全
看不到失敗原因。日誌目錄與級別一律由 .env 指定，不硬編碼。
"""
from __future__ import annotations

import logging
from collections import deque
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOGGER_NAME = "brokery.api"
LOG_FILE = "brokery_api.log"
MAX_BYTES = 2 * 1024 * 1024  # 單檔上限，超過即滾動
BACKUP_COUNT = 5
MAX_RECORDS = 500  # 記憶體中保留的條數（GET /logs 的來源）
FORMAT = "%(asctime)s %(levelname)s %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S"


class RecentLogHandler(logging.Handler):
    """把最近若干條日誌留在記憶體，供 GET /logs 顯示（對應 OpenD/IB Gateway 的日誌窗）。"""

    def __init__(self, capacity: int = MAX_RECORDS):
        super().__init__()
        self.records: deque[dict] = deque(maxlen=capacity)

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append({
            "ts": int(record.created),
            "time": datetime.fromtimestamp(record.created).strftime(DATEFMT),
            "level": record.levelname,
            "message": record.getMessage(),
        })

    def tail(self, limit: int) -> list[dict]:
        """取最近 limit 條，按時間升序。"""
        return list(self.records)[-max(limit, 0):]


def level_of(name: str) -> int:
    """日誌級別名稱 → 數值；名稱不合法時退回 INFO。"""
    value = logging.getLevelName(str(name).upper())
    return value if isinstance(value, int) else logging.INFO


def setup_logging(level: str, log_dir: Path, capacity: int = MAX_RECORDS,
                  logger_name: str = LOGGER_NAME, file_name: str = LOG_FILE) -> RecentLogHandler:
    """設定閘道與 uvicorn 的日誌輸出，回傳記憶體環形緩衝。

    可重複呼叫（測試中會建立多個應用）：每次先清空既有處理器，避免同一行被寫多次。
    logger_name / file_name 可換：Web UI 與閘道為兩個進程，各自寫自己的檔案，否則兩者會互相搶佔同一個
    滾動檔（滾動時其中一方的句柄會指向已被改名的檔案）。
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(FORMAT, DATEFMT)
    handlers: list[logging.Handler] = []
    for handler in (
        logging.StreamHandler(),
        RotatingFileHandler(
            log_dir / file_name, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
        ),
        RecentLogHandler(capacity),
    ):
        handler.setFormatter(formatter)
        handlers.append(handler)

    # uvicorn.error 一併接上：啟動、關閉與未捕獲異常才會同樣寫入檔案與 /logs。
    for name in (logger_name, "uvicorn.error"):
        target = logging.getLogger(name)
        target.handlers[:] = handlers
        target.setLevel(level_of(level))
        target.propagate = False
    return handlers[-1]


def get_logger(name: str = LOGGER_NAME) -> logging.Logger:
    """閘道自身的記錄器。"""
    return logging.getLogger(name)
