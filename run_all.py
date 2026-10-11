"""一次過啟動閘道與 Web UI：python run_all.py

兩個仍是各自獨立的進程；只想起其中一個，仍用 brokery_api/run.py 或 brokery_webui/run.py。
本檔只負責啟動與收尾：任何一個先結束即停止另一個，Ctrl+C 一併停止，不留半個服務在背景。
各進程的監聽地址由自己的啟動入口按 .env 決定，uvicorn 會印出自身地址，本檔不再重複。

本檔刻意不 import brokery：那會經 brokers 拉起券商 SDK，而 futu SDK 在匯入時即接管 SIGINT
（自備的 quit_handler 直接結束進程），Ctrl+C 便不會走到下面的收尾，兩個子進程會變成孤兒。
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GATEWAY = ROOT / "brokery_api" / "run.py"
WEBUI = ROOT / "brokery_webui" / "run.py"
NAMES = ("閘道", "Web UI")
POLL_SECONDS = 0.2
STOP_TIMEOUT = 10.0  # 收尾有上限：子進程不回應即強制結束，不無限等待


def default_commands() -> list[list[str]]:
    """兩個啟動入口：以同一個直譯器執行，不經 shell，Windows / Ubuntu / Docker 一致。"""
    return [[sys.executable, str(GATEWAY)], [sys.executable, str(WEBUI)]]


def _stop(procs: list[subprocess.Popen]) -> None:
    """停止仍在運行的進程（正常結束與 Ctrl+C 兩條收尾路徑共用）。"""
    for proc in procs:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=STOP_TIMEOUT)
            except subprocess.TimeoutExpired:
                proc.kill()


def launch(gateway_cmd=None, webui_cmd=None) -> int:
    """啟動閘道與 Web UI，直到其中一個結束或收到 Ctrl+C；停止其餘後返回結束者的退出碼。

    gateway_cmd / webui_cmd 可換成任意命令，讓驗收不需真的啟動服務也能核對收尾行為。
    """
    defaults = default_commands()
    commands = [list(gateway_cmd or defaults[0]), list(webui_cmd or defaults[1])]
    procs = [subprocess.Popen(cmd) for cmd in commands]
    print(f"已啟動 {NAMES[0]} 與 {NAMES[1]} 兩個進程（Ctrl+C 一併停止；端口見 .env）")
    codes = [0] * len(procs)
    try:
        while True:
            codes = [proc.poll() for proc in procs]
            if any(code is not None for code in codes):
                break
            time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        print(f"收到 Ctrl+C，一併停止 {NAMES[0]} 與 {NAMES[1]}…")
    finally:
        _stop(procs)
    for name, code in zip(NAMES, codes):
        if code:
            print(f"{name} 先結束（退出碼 {code}），已停止另一個")
            break
    return next((code for code in codes if code), 0)


if __name__ == "__main__":
    raise SystemExit(launch())
