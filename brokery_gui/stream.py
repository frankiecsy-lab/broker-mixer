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
    """一條 /stream 連接：start()/subscribe() 訂閱，unsubscribe()/stop() 結束；事件以信號交回界面。

    閘道按「請求簽名」（券商、週期、代碼、根數、復權、raw）界定一份串流：同簽名即同一份請求，再訂閱即接手
    仍在跑的那條（不另向券商訂閱）；簽名不同即另一條，同一券商同一週期可並行多條，不會再被拒。多週期界面
    九個週期因此仍只經本模組這一條連接。本模組不代界面重連，避免用戶看不見的连接反覆發生。
    """

    subscribed = Signal(dict)   # {"broker","codes","ktype","seconds"}
    update = Signal(dict)       # {"code","data":{columns,rows}}：該代碼目前完整的 bar
    closed = Signal(dict)       # {"event":"end"|"closed", …}：正常結束
    error = Signal(dict)        # {"event":"error", …}：協定錯誤原樣交回（含 broker/ktype）
    failed = Signal(str)        # 連接失敗或無法解讀的訊息：內容即閘道原樣返回的訊息
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
        self._queue: list[dict] = []           # 未送出的訂閱：連接就緒即照順序送出
        # 已訂閱嘅 (broker,ktype) → 尚有多少條：同一週期可並行多條，故要計數，否則其中一條結束就會誤判收齊
        self._open: dict[tuple[str, str], int] = {}
        self._socket = QWebSocket()
        self._socket.textMessageReceived.connect(self._on_message)
        self._socket.connected.connect(self._on_connected)
        self._socket.disconnected.connect(self._on_disconnected)
        self._socket.errorOccurred.connect(self._on_error)

    @property
    def active(self) -> bool:
        """是否仍有一条在用的連接：界面據此決定「訂閱」與「停止」哪個可用。"""
        # 名稱必須用 UnconnectedState：這個 PySide6 唔暴露 QAbstractSocket.Unconnected（寫錯即喺已連接時先爆，
        # 未連接時反而給 isValid() 短路掩蓋走）。
        return self._socket.isValid() and self._socket.state() != QAbstractSocket.UnconnectedState

    def start(self, code: str, ktype: str, count: int, broker: str,
              autype: str | None = None) -> None:
        """訂閱一個代碼的串流（單週期頁沿用此口徑）：先連上，再在連上的一刻送出訂閱，故界面不需自己排隊。

        週期、根數與復權口徑一律原樣交閘道判定（不支持即返回 ktype_unsupported、被停用即返回
        broker_disabled），本層不自訂第二套預設，也不憑空補參數。
        """
        if self.active:
            return
        self._queue = [self._subscribe(code, ktype, count, broker, autype)]
        self._socket.open(QUrl(self._url))

    def subscribe(self, code: str, ktype: str, count: int, broker: str,
                  autype: str | None = None) -> None:
        """在同一條連接上再加一個週期的訂閱：多週期界面九個週期因此只經一條 WS（連線數由九減至一）。

        未連上即照順序排隊，連上即逐個送出；已連上即即時送出。
        """
        action = self._subscribe(code, ktype, count, broker, autype)
        self._queue.append(action)
        if self._socket.state() == QAbstractSocket.ConnectedState:
            self._socket.sendTextMessage(json.dumps(action))
        elif not self.active:
            self._socket.open(QUrl(self._url))

    def _subscribe(self, code: str, ktype: str, count: int, broker: str,
                   autype: str | None) -> dict:
        action = {"action": "subscribe", "codes": [code], "ktype": ktype,
                  "count": count, "broker": broker}
        if autype:
            action["autype"] = autype
        key = (broker, ktype)
        self._open[key] = self._open.get(key, 0) + 1
        return action

    def unsubscribe(self, broker: str, ktype: str) -> None:
        """只停該週期（換某一格的週期時用）：閘道會停該週期在本連接上的全部串流，其餘週期各格不受影響。"""
        if self._socket.state() == QAbstractSocket.ConnectedState:
            self._socket.sendTextMessage(json.dumps({"action": "stop", "broker": broker, "ktype": ktype}))
        self._open.pop((broker, ktype), None)

    def stop(self) -> None:
        """結束訂閱：先送 stop 讓閘道立即停止推送，再關閉連接。"""
        if self._socket.state() == QAbstractSocket.ConnectedState:
            self._socket.sendTextMessage(json.dumps({"action": "stop"}))
        self._queue.clear()
        self._open.clear()
        if self._socket.isValid():
            self._socket.close()

    @Slot()
    def _on_connected(self) -> None:
        for action in self._queue:
            self._socket.sendTextMessage(json.dumps(action))

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
            # 一個週期結束不等於整條連接結束：多週期時要待所有訂閱都結束先收口。同一週期可能有幾條，
            # 故逐條扣數。消息唔帶 broker/ktype 即唔係某一條嘅結束，一律按整條連接結束處理。
            key = (str(msg.get("broker") or ""), str(msg.get("ktype") or ""))
            if all(key):
                left = self._open.get(key, 0) - 1
                if left > 0:
                    self._open[key] = left
                else:
                    self._open.pop(key, None)
            else:
                self._open.clear()
            if not self._open:
                self._finish()
        elif event == "error":   # 含 bad_request / ktype_unsupported / broker_disabled：連 broker/ktype 一併交回
            self.error.emit(msg)
        else:  # 未知事件一律按失敗呈現，不假裝收到
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
        self._queue.clear()
        self._open.clear()
        self.finished.emit()
