"""啟動閘道：python brokery_api/run.py

監聽地址、端口、自訂金鑰、啟用的券商與日誌設定一律由 .env 指定，不在本檔硬編碼。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # 直接執行本檔時也能 import brokery


def main() -> int:
    import uvicorn

    from brokery.config import get_settings
    from brokery_api.app import create_app

    settings = get_settings()
    try:
        app = create_app()
    except RuntimeError as exc:  # 未設 API_KEY
        print(f"無法啟動：{exc}", file=sys.stderr)
        return 1
    # access_log 關閉：請求由閘道自身的中間件記錄，級別與輸出位置統一由 API_LOG_* 決定。
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.api_log_level.lower(),
        access_log=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
