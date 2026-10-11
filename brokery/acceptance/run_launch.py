"""驗收 `run_all.py`（一次過啟動閘道與 Web UI）：以存根命令代替兩個啟動入口，不需券商連線，
也不需要真的啟動任何服務。核對：

* 兩個進程同時啟動：兩者的啟動標記均出現；
* 其中一個先結束即停止另一個（較慢者未跑完即被終止，不是自己結束），並原樣返回其退出碼；
* 兩者正常結束即返回 0；Ctrl+C（SIGINT）同樣停止兩個並返回 0；
* 預設命令即兩個既有啟動入口（brokery_api/run.py 與 brokery_webui/run.py，兩檔均存在）；
* 啟動器本身不引入券商 SDK：futu SDK 在匯入時即接管 SIGINT，若被帶進來，Ctrl+C 便不會走到收尾。

以腳本方式直接執行：
    python brokery/acceptance/run_launch.py
"""
import signal
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import psutil

import run_all

# 存根：寫下自己的 PID 後長時間不結束，用於核對「被停止」而非「自己跑完」。
STAY = ("import pathlib,sys,time;"
        "pathlib.Path(sys.argv[1]).write_text(str(__import__('os').getpid()));"
        "time.sleep(8)")
# 存根：寫下 PID，稍後以指定退出碼結束，模擬其中一個服務先倒下（如未設 API_KEY）。
EXIT_WITH = ("import pathlib,sys,time;"
             "pathlib.Path(sys.argv[1]).write_text(str(__import__('os').getpid()));"
             "time.sleep(1.5);sys.exit(int(sys.argv[2]))")


def pid_of(marker: Path) -> int:
    """讀回存根寫下的 PID；存根未寫成即返回 0（視為未啟動）。"""
    return int(marker.read_text()) if marker.exists() else 0


def stopped(pid: int) -> bool:
    """存根已不在（被終止）：PID 讀到且進程不存在。"""
    return pid != 0 and not psutil.pid_exists(pid)


def main() -> dict:
    checks: list[tuple[str, bool, str]] = []

    def check(label: str, passed: bool, detail: str = "") -> None:
        checks.append((label, bool(passed), str(detail)))

    sdk = sorted({name for name in ("futu", "ib_async", "tigeropen") if name in sys.modules})
    check("啟動器不引入券商 SDK（否則 SIGINT 被 SDK 接管，收尾不會執行）", not sdk, "、".join(sdk) or "無")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # 閘道以退出碼 3 結束（如未設 API_KEY）：Web UI 必須被一併停止，退出碼原樣返回
        code = run_all.launch(gateway_cmd=[sys.executable, "-c", EXIT_WITH, str(tmp / "gw1"), "3"],
                              webui_cmd=[sys.executable, "-c", STAY, str(tmp / "gui1")])
        gw1, gui1 = pid_of(tmp / "gw1"), pid_of(tmp / "gui1")
        check("兩個進程同時啟動（兩者的啟動標記均出現）", gw1 != 0 and gui1 != 0,
              f"閘道 PID={gw1} Web UI PID={gui1}")
        check("其中一個先結束即停止另一個（較慢者未跑完）", stopped(gui1), f"Web UI PID={gui1} 已結束")
        check("先結束者的退出碼原樣返回", code == 3, f"返回 {code}")

        code = run_all.launch(gateway_cmd=[sys.executable, "-c", EXIT_WITH, str(tmp / "gw2"), "0"],
                              webui_cmd=[sys.executable, "-c", STAY, str(tmp / "gui2")])
        check("兩者正常結束即返回 0", code == 0, f"返回 {code}")

        # Ctrl+C：SIGINT 未被券商 SDK 接管，會轉為 KeyboardInterrupt；兩個存根均不會自行結束，故須被停止
        threading.Timer(1.0, lambda: signal.raise_signal(signal.SIGINT)).start()
        started = time.time()
        code = run_all.launch(gateway_cmd=[sys.executable, "-c", STAY, str(tmp / "gw3")],
                              webui_cmd=[sys.executable, "-c", STAY, str(tmp / "gui3")])
        pids = [pid_of(tmp / "gw3"), pid_of(tmp / "gui3")]
        check("Ctrl+C 一併停止兩個並返回 0",
              code == 0 and all(stopped(pid) for pid in pids),
              f"返回 {code} 耗時 {time.time() - started:.1f}s PIDs={pids}")

    commands = run_all.default_commands()
    check("預設命令即兩個既有啟動入口（兩檔均存在）",
          commands == [[sys.executable, str(run_all.GATEWAY)], [sys.executable, str(run_all.WEBUI)]]
          and run_all.GATEWAY.is_file() and run_all.WEBUI.is_file(),
          "、".join(path.name for path in (run_all.GATEWAY, run_all.WEBUI)))

    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）")
    failed = [label for label, passed, _ in checks if not passed]
    if failed:
        return {"status": False, "data": None, "message": "失敗：" + "；".join(failed)}
    return {"status": True, "data": None,
            "message": f"{len(checks)} 項檢查全過：兩個同時啟動、先結束者停止另一個並返回其退出碼、"
                       "Ctrl+C 一併停止、預設命令即兩個既有入口"}


if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] else 1)
