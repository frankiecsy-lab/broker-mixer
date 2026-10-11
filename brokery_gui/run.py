"""啟動桌面 GUI：python brokery_gui/run.py

閘道地址與金鑰沿用 .env 的 API_HOST / API_PORT / API_KEY；沒有金鑰即明確報錯，不開一個讀不到數的窗口。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # 直接執行本檔時也能 import brokery


def main() -> int:
    from PySide6 import QtWidgets

    from brokery_gui.api import GatewayClient
    from brokery_gui.app import DesktopGui

    try:
        client = GatewayClient()
    except RuntimeError as exc:  # 未設 API_KEY
        print(f"無法啟動：{exc}", file=sys.stderr)
        return 1
    qt = QtWidgets.QApplication(sys.argv)
    DesktopGui(client).show()
    return qt.exec()


if __name__ == "__main__":
    raise SystemExit(main())
