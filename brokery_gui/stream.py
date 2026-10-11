"""K 線串流的閘道客戶端：QWebSocket 對接 brokery_api 的 /stream。

桌面端不直接連券商（理由與 api.py 相同：閘道進程已持有各券商連線），串流亦只經閘道。金鑰放進查詢串是
因為 QWebSocket 與瀏覽器一樣不便自訂握手標頭，而這個 URL 不會出現在界面上。

本模組只按協定收發：收到什麼事件即轉成同名信號，不在此解讀、合併或重排資料，協定變更（新增事件、改欄位）
都不需要改這裡。
"""
from __future__ import annotations

import json

from PySide6.QtCore import QUrl, QObject, Signal, Slot
from PySide6.QtNetwork import QAbstractSocket
from PySide6.QtWebSockets import QWebSocket

from brokery.config import get_settings


class StreamClient(QObject):
    """一條 /stream 連接：start() 訂閱，stop() 結束；事件以信號交回界面。

    同一券商在閘道同時只容許一條串流，名額要待上一條結束才釋放，故界面必須先 stop() 再換參數重試；
    本模組不代界面重連，避免用戶看不見的连接反覆發生。
    """

    subscribed = Signal(dict)   # {"broker","codes","ktype","seconds"}
    update = Signal(dict)       # {"code","data":{columns,rows}}：該代碼目前完整的 bar
    closed = Signal(dict)       # {"event":"end"|"closed", …}：正常結束
    failed = Signal(str)        # 協定錯誤（error 事件）或連接失敗：內容即閘道原樣返回的訊息
    finished = Signal()         # 連接已結束：界面據此解鎖按鈕

    def __init__(self, base_url: str | None = None, api_key: str | None = None,
                 parent: QObject | None = None) -> None:
        super().__init__(parent)
        settings = get_settings()
        base_url = (base_url or f"http://{settings.api_host}:{settings.api_port}").rstrip("/")
        api_key = settings.api_key if api_key is None else api_key
        if not api_key:
            raise RuntimeError(
                "API_KEY 未設定：桌面 GUI 經閘道訂閱串流，請在 .env 設 API_KEY=<自訂金鑰> 後重新啟動"
            )
        # http→ws 只換協定：閘道與界面同一主機同一端口，不存在另一套串流地址。
        self._url = f"{base_url.replace('http', 'ws', 1)}/stream?api_key={api_key}"
        self._pending: dict | None = None
        self._socket = QWebSocket()
        self._socket.textMessageReceived.connect(self._on_message)
        self._socket.connected.connect(self._on_connected)
        self._socket.disconnected.connect(self._on_disconnected)
        self._socket.errorOccurred.connect(self._on_error)

    @property
    def active(self) -> bool:
        """是否仍有一条在用的連接：界面據此決定「訂閱」與「停止」哪個可用。"""
        return self._socket.isValid() and self._socket.state() != QAbstractSocket.Unconnected

    def start(self, code: str, ktype: str, count: int, broker: str,
              autype: str | None = None) -> None:
        """訂閱一個代碼的串流：先連上，再在連上的一刻送出訂閱，故界面不需自己排隊。

        週期、根數與復權口徑一律原樣交閘道判定（不支持即返回 ktype_unsupported、被停用即返回
        broker_disabled），本層不自訂第二套預設，也不憑空補參數。
        """
        if self.active:
            return
        self._pending = {"action": "subscribe", "codes": [code], "ktype": ktype,
                         "count": count, "broker": broker}
        if autype:
            self._pending["autype"] = autype
        self._socket.open(QUrl(self._url))

    def stop(self) -> None:
        """結束訂閱：先送 stop 讓閘道立即停止推送並歸還名額，再關閉連接。"""
        if self._socket.state() == QAbstractSocket.ConnectedState:
            self._socket.sendTextMessage(json.dumps({"action": "stop"}))
        self._pending = None
        if self._socket.isValid():
            self._socket.close()

    @Slot()
    def _on_connected(self) -> None:
        if self._pending is not None:
            self._socket.sendTextMessage(json.dumps(self._pending))

    @Slot(str)
    def _on_message(self, text: str) -> None:
        try:
            msg = json.loads(text)
        except ValueError as exc:  # 非 JSON 即協定已被破壞，說清楚比假裝沒收到好
            self.failed.emit(f"bad_payload: {exc}")
            self._finish()
            return
        event = str(msg.get("event", ""))
        if event == "subscribed":
            self.subscribed.emit(msg)
        elif event == "update":
            self.update.emit(msg)
        elif event in ("end", "closed"):
            self.closed.emit(msg)
            self._finish()
        else:  # error（含 stream_busy / bad_request / broker_disabled）與未知事件一律按失敗呈現
            self.failed.emit(str(msg.get("message") or msg.get("event") or "empty_event"))

    @Slot(QAbstractSocket.SocketError)
    def _on_error(self, code: QAbstractSocket.SocketError) -> None:
        # 閘道未啟動時 QWebSocket 只給 SocketError 代碼，點名它才能與協定錯誤分清。
        self.failed.emit(f"socket_error_{int(code)}: {self._socket.errorString()}")

    @Slot()
    def _on_disconnected(self) -> None:
        self._finish()

    def _finish(self) -> None:
        if self._socket.isValid():
            self._socket.close()
        self._pending = None
        self.finished.emit()
