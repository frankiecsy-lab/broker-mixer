"""啟動 Web UI：python brokery_webui/run.py

監聽地址與端口由 .env 的 GUI_HOST / GUI_PORT 指定；閘道地址與金鑰沿用 API_HOST / API_PORT / API_KEY。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # 直接執行本檔時也能 import brokery


def main() -> int:
    import uvicorn

    from brokery.config import get_settings
    from brokery_webui.app import create_app

    settings = get_settings()
    try:
        app = create_app()
    except RuntimeError as exc:  # 未設 API_KEY
        print(f"無法啟動：{exc}", file=sys.stderr)
        return 1
    # access_log 關閉：轉發結果由本應用記錄，級別與輸出位置統一由 API_LOG_* 決定。
    uvicorn.run(
        app,
        host=settings.gui_host,
        port=settings.gui_port,
        log_level=settings.api_log_level.lower(),
        access_log=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
