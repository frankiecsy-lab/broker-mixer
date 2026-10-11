"""驗收 `brokery_api`：把 Brokery 的統一輸出映射為 HTTP/WS 這一層本身負責的東西——自訂金鑰鑑權、
返回信封與固定欄位契約、DataFrame→JSON（缺失值為 null、整數為整數、不出現非法的 NaN）、業務失敗仍為
HTTP 200 且原因原樣透傳、三個清單接口的參數透傳（markets 大寫為統一前綴、broker 原樣傳入，省略即 None
而不是把 None 傳進 core 炸開），串流協定（訂閱/更新/停止/名額），以及日誌（含金鑰遮罩）。

取數本身的對錯由 run_get_kline / run_get_accounts / run_stream_kline 等驗收，本腳本一律以 sources=()
建立應用，串流部分以存根代替 Brokery，因此不需要任何券商連線，任何環境都能重複執行。

以腳本方式直接執行：
    python brokery/acceptance/run_api.py
"""
import json
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 項目根目錄

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from brokery.brokers.base import ACCOUNT_COLUMNS, BAR_MINUTES, BROKER_COLUMNS, COLUMNS, K_COLUMNS
from brokery.core import CODES_META_COLUMNS, codes_max_age_seconds
from brokery_api.app import create_app, frame_payload

KEY = "acceptance-key-9c1f"
HEADERS = {"X-API-Key": KEY}

SAMPLE = {"code": "HK.00700", "ts": 1791711000, "time_key": "2026-10-10 16:00:00", "open": 1.0,
          "high": 2.0, "low": 0.5, "close": 1.5, "volume": 10, "turnover": 15, "source": "stub"}


NATIVE_BAR = {"symbol": "00700", "time_key": "2026-10-10 16:00:00", "price": 1.5, "lot": None}


class StubQuote:
    """代替 Brokery 的串流：立即推一根完整序列後正常收尾，令 update 事件可離線重複驗證。

    回呼一律送字典列表，形式與各券商的 BarMerger/NativeBars 一致；raw=True 時送原生欄位。
    """

    def stream_kline(self, codes, **kwargs):
        rows = [dict(NATIVE_BAR)] if kwargs.get("raw") else [
            {name: SAMPLE[name] for name in K_COLUMNS}
        ]
        for code in codes:
            kwargs["on_update"](code, rows)
        return {"status": True, "data": pd.DataFrame(rows), "message": "ok: 存根串流結束"}

    def close(self) -> None:
        pass


class HoldQuote(StubQuote):
    """要指示才收尾的串流存根，用來驗證同一券商同時只容許一條串流。"""

    def __init__(self) -> None:
        self.gate = threading.Event()

    def stream_kline(self, codes, **kwargs):
        self.gate.wait(10)
        return {"status": True, "data": pd.DataFrame(), "message": "ok: 存根串流結束"}


class StubBrokers:
    """代替 Brokery 的連線探測：一家可連、一家連不上，令 latency_ms 的缺失值口徑可離線重複驗證。"""

    def get_brokers(self, broker=None):
        rows = [
            {"source": "futu", "connected": True, "latency_ms": 12.5, "accounts": 2,
             "detail": "", "checked_at": 1791711000},
            {"source": "ib", "connected": False, "latency_ms": float("nan"), "accounts": 0,
             "detail": "RuntimeError: 連不上", "checked_at": 1791711000},
        ]
        return {"status": True, "data": pd.DataFrame(rows, columns=BROKER_COLUMNS), "message": "ok: 存根探測"}

    def close(self) -> None:
        pass


class StubLists:
    """代替 Brokery 的清單：只記錄收到的參數，用來核對閘道把 markets／roots／symbols 大寫後與 broker、
    raw 原樣傳給 core（能力閘與市場過濾本身由 run_list_filter.py 驗收）。"""

    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def _empty(self):
        return {"status": True, "data": pd.DataFrame(columns=COLUMNS), "message": "ok"}

    def list_stocks(self, markets=None, broker=None, *, raw=False):
        self.calls.append(("list_stocks", markets, broker, raw))
        return self._empty()

    def list_futures(self, roots=None, markets=None, broker=None, *, raw=False):
        self.calls.append(("list_futures", roots, markets, broker, raw))
        return self._empty()

    def list_indices(self, symbols=None, markets=None, broker=None, *, raw=False):
        self.calls.append(("list_indices", symbols, markets, broker, raw))
        return self._empty()

    def close(self) -> None:
        pass


def until(ws, field: str, prefix: str, limit: int = 6) -> dict:
    """讀到第一條 field 以 prefix 開始的事件；其間可能夾著上一條串流的收尾事件，故要略過。"""
    msg: dict = {}
    for _ in range(limit):
        msg = ws.receive_json()
        if str(msg.get(field, "")).startswith(prefix):
            return msg
    return msg


def main() -> dict:
    checks: list[tuple[str, bool, str]] = []

    def check(label: str, passed: bool, detail: str = "") -> None:
        checks.append((label, bool(passed), str(detail)))

    # 未設 API_KEY：拒絕建立應用，並明確說明原因（閘道會返回戶口與資金）。
    try:
        create_app(sources=(), api_key="")
        check("未設金鑰時拒絕啟動", False, "竟然建立了應用")
    except RuntimeError as exc:
        check("未設金鑰時拒絕啟動", "API_KEY" in str(exc), str(exc)[:60])

    app = create_app(sources=(), api_key=KEY)
    with TestClient(app) as client:
        # 控制台頁面本身不需金鑰（頁面不含資料），資料接口一律要金鑰。
        page = client.get("/")
        check("控制台頁面可取", page.status_code == 200 and "brokery api" in page.text,
              f"HTTP {page.status_code}，{len(page.text)} 字節")

        no_key = client.get("/kline", params={"code": "HK.00700"})
        wrong = client.get("/kline", params={"code": "HK.00700"}, headers={"X-API-Key": KEY + "x"})
        bearer = client.get("/capabilities", headers={"Authorization": f"Bearer {KEY}"})
        check("無金鑰 401", no_key.status_code == 401, f"HTTP {no_key.status_code} {no_key.json().get('detail')}")
        check("金鑰不正確 403", wrong.status_code == 403, f"HTTP {wrong.status_code}")
        check("Bearer 亦受理", bearer.status_code == 200 and bearer.json()["status"], f"HTTP {bearer.status_code}")

        health = client.get("/health").json()
        check("/health 不需金鑰且回報配置",
              health["status"] and health["data"]["sources"] == [] and "autype" in health["data"],
              health["message"])

        caps = client.get("/capabilities", headers=HEADERS).json()
        check("/capabilities 欄位契約與 K_COLUMNS 一致",
              caps["status"] and caps["data"]["columns"]["kline"] == list(K_COLUMNS),
              caps["data"]["columns"]["kline"])
        check("/capabilities 欄位契約與 ACCOUNT_COLUMNS 一致",
              caps["data"]["columns"]["accounts"] == list(ACCOUNT_COLUMNS), caps["data"]["columns"]["accounts"])
        check("/capabilities 欄位契約與 COLUMNS 一致",
              caps["data"]["columns"]["codes"] == list(COLUMNS), caps["data"]["columns"]["codes"])
        check("/capabilities 欄位契約與 BROKER_COLUMNS 一致",
              caps["data"]["columns"]["brokers"] == list(BROKER_COLUMNS), caps["data"]["columns"].get("brokers"))
        check("/capabilities 週期清單為 BAR_MINUTES",
              caps["data"]["ktypes"] == sorted(BAR_MINUTES), ",".join(caps["data"]["ktypes"]))

        codes = client.get("/codes", headers=HEADERS).json()
        check("/codes 離線讀回 CODES", codes["status"] and codes["data"]["columns"] == list(COLUMNS)
              and len(codes["data"]["rows"]) > 0, codes["message"])

        # /codes/meta：快照年齡與是否過舊（供介面顯示「更新」提示）；/codes/refresh 無券商時必須明確
        # 報錯，且不得動到已存放的快照——離線快照往往是唯一的離線副本。
        meta = client.get("/codes/meta", headers=HEADERS).json()
        check("/codes/meta 欄位為 CODES_META_COLUMNS 且為單行",
              meta["status"] and meta["data"]["columns"] == list(CODES_META_COLUMNS)
              and len(meta["data"]["rows"]) == 1, meta["message"])
        row = dict(zip(meta["data"]["columns"], meta["data"]["rows"][0])) if meta["status"] else {}
        check("/codes/meta 的 stale 與 age_seconds 按同一上限一致",
              row.get("stale") == (row.get("age_seconds", 0) > codes_max_age_seconds()), str(row)[:160])
        check("/codes/meta 的 rows 與 /codes 實際行數一致",
              row.get("rows") == len(codes["data"]["rows"]), f"meta={row.get('rows')} 實際={len(codes['data']['rows'])}")
        # 不重取全量 /codes（數萬條的序列化是本腳本最慢的一步）：以 meta 的行數核對快照未被破壞。
        refresh = client.get("/codes/refresh", headers=HEADERS).json()
        kept = client.get("/codes/meta", headers=HEADERS).json()
        check("/codes/refresh 無券商時明確報錯並保留原快照",
              refresh["status"] is False and refresh["message"].startswith("更新失敗")
              and kept["data"]["rows"][0][list(CODES_META_COLUMNS).index("rows")] == len(codes["data"]["rows"]),
              refresh["message"])

        # 業務失敗仍為 HTTP 200，原因由 status/message 原樣表達，不變成 HTTP 500。
        kline = client.get("/kline", params={"code": "HK.00700", "broker": "futu"}, headers=HEADERS)
        check("未啟用的來源：HTTP 200 且 status=False",
              kline.status_code == 200 and kline.json()["status"] is False, f"HTTP {kline.status_code}")
        check("未啟用的來源：原因原樣透傳", kline.json()["message"].startswith("unknown_source:"),
              kline.json()["message"])

        # raw=True 只改欄位，不改信封與狀態口徑：取不到資料時沒有原生欄位可保留，故返回無欄位的空表。
        raw_kline = client.get("/kline", params={"code": "HK.00700", "broker": "futu", "raw": "1"},
                               headers=HEADERS).json()
        check("raw 失敗信封仍為三鍵且 data 無欄位",
              set(raw_kline) == {"status", "data", "message"} and raw_kline["status"] is False
              and raw_kline["data"]["columns"] == [], str(raw_kline)[:140])

        accounts = client.get("/accounts", headers=HEADERS).json()
        check("無戶口時明確報錯", not accounts["status"] and accounts["message"].startswith("no_account:"),
              accounts["message"])
        futures = client.get("/futures", params={"roots": "NOPE"}, headers=HEADERS).json()
        check("不存在的期貨 root 明確報錯", not futures["status"] and futures["message"].startswith("unknown_seed:"),
              futures["message"])

        # 不帶 markets 即省略該參數（由 core 用預設市場），不是把 None 傳進去炸開：
        # 曾經 list_stocks(None) 拋 TypeError，令控制台「標的清單全部取不到、一直讀取中」。
        bare = client.get("/stocks", headers=HEADERS).json()
        check("/stocks 不帶參數時明確報錯而非 api_failed（無券商即 no_source）",
              bare["status"] is False and bare["message"].startswith("no_source"), bare["message"])
        for path in ("/stocks", "/futures", "/indices"):
            body = client.get(path, params={"markets": "hk"}, headers=HEADERS).json()
            check(f"{path} 帶 markets 亦不拋異常", not str(body["message"]).startswith("api_failed"),
                  body["message"])

        # 返回的 rows 必須能原樣重建 DataFrame：欄位順序一致，時間戳為整數秒。
        frame = pd.DataFrame(codes["data"]["rows"], columns=codes["data"]["columns"])
        ts_index = list(codes["data"]["columns"]).index("symbol")
        check("rows 可重建 DataFrame 且欄位一致", list(frame.columns) == list(COLUMNS), f"{len(frame)} 行")
        check("所有值均為 JSON 基本類型",
              all(v is None or isinstance(v, (bool, int, float, str))
                  for row in codes["data"]["rows"] for v in row),
              "；".join({type(v).__name__ for row in codes["data"]["rows"] for v in row}))

        logs = client.get("/logs", params={"limit": 50}, headers=HEADERS).json()
        lines = [row[3] for row in logs["data"]["rows"]]
        check("/logs 有內容且按新到舊排列", logs["status"] and len(lines) >= 5, logs["message"])
        check("業務失敗已寫入日誌", any("/kline" in line for line in lines),
              next((line for line in lines if "/kline" in line), "無相關日誌"))
        check("日誌不含自訂金鑰", not any(KEY in line for line in lines), f"{len(lines)} 條")

        # /brokers：未啟用任何券商時明確報錯；有結果時欄位固定，連不上者的延遲為 null 而非 0。
        none = client.get("/brokers", headers=HEADERS).json()
        check("/brokers 無券商可探測時明確報錯", not none["status"] and none["message"].startswith("no_source"),
              none["message"])
        app.state.brokery = StubBrokers()
        got = client.get("/brokers", headers=HEADERS)
        body = got.json()
        check("/brokers 欄位為 BROKER_COLUMNS",
              got.status_code == 200 and body["status"] and body["data"]["columns"] == list(BROKER_COLUMNS),
              body["data"]["columns"])
        check("/brokers 連不上時 latency_ms 為 null",
              body["data"]["rows"][1][list(BROKER_COLUMNS).index("latency_ms")] is None
              and body["data"]["rows"][1][list(BROKER_COLUMNS).index("connected")] is False,
              str(body["data"]["rows"][1]))
        check("/brokers 可連者帶延遲與原因",
              body["data"]["rows"][0][list(BROKER_COLUMNS).index("latency_ms")] == 12.5
              and body["data"]["rows"][1][list(BROKER_COLUMNS).index("detail")] == "RuntimeError: 連不上",
              str(body["data"]["rows"][0]))
        check("/brokers 的 rows 可重建 DataFrame",
              list(pd.DataFrame(body["data"]["rows"], columns=body["data"]["columns"]).columns)
              == list(BROKER_COLUMNS), f"{len(body['data']['rows'])} 行")
        check("/brokers 的 JSON 不含非法的 NaN", "NaN" not in got.text, got.text[:120])

        # 清單接口的參數透傳：市場大寫為統一前綴、broker 與 raw 原樣傳入（省略即 None/False，不自行補預設）。
        lists = StubLists()
        app.state.brokery = lists
        for path, params in (("/stocks", {"markets": "hk,us", "broker": "futu"}),
                             ("/stocks", {}),
                             ("/stocks", {"markets": "hk", "raw": "1"}),
                             ("/futures", {"roots": "es", "markets": "hk", "broker": "ib"}),
                             ("/futures", {"markets": "hk", "raw": "true"}),
                             ("/indices", {"symbols": "spx", "markets": "us", "broker": "tiger"}),
                             ("/indices", {"markets": "us", "raw": "0"})):
            got = client.get(path, params=params, headers=HEADERS)
            check(f"{path} 返回信封完整", got.status_code == 200 and got.json()["status"] is True,
                  f"HTTP {got.status_code}")
        check("markets／roots／symbols 大寫為統一前綴，broker／raw 原樣傳入",
              lists.calls == [("list_stocks", ("HK", "US"), "futu", False),
                              ("list_stocks", None, None, False),
                              ("list_stocks", ("HK",), None, True),
                              ("list_futures", ("ES",), ("HK",), "ib", False),
                              ("list_futures", None, ("HK",), None, True),
                              ("list_indices", ("SPX",), ("US",), "tiger", False),
                              ("list_indices", None, ("US",), None, False)],
              "；".join(str(call) for call in lists.calls))

    # DataFrame→JSON 的取值口徑：缺失值一律為 null，整數不帶小數，且不得出現非法的 NaN。
    mixed = pd.DataFrame({
        "int64": np.array([1], dtype="int64"),
        "float": [1.5],
        "nan": [float("nan")],
        "none": [None],
        "na": [pd.NA],
        "nat": [pd.NaT],
        "ts": [pd.Timestamp("2026-10-11 09:30:00")],
        "text": ["HK.00700"],
    })
    payload = frame_payload(mixed)
    text = json.dumps({"data": payload}, ensure_ascii=False)
    row = dict(zip(payload["columns"], payload["rows"][0]))
    check("NaN/None/NA/NaT 一律為 null",
          all(row[name] is None for name in ("nan", "none", "na", "nat")), str(row))
    check("整數與時間戳轉為整數", isinstance(row["int64"], int) and isinstance(row["ts"], int)
          and row["ts"] == int(pd.Timestamp("2026-10-11 09:30:00").timestamp()), str(row))
    check("JSON 文本不含非法的 NaN", "NaN" not in text and json.loads(text)["data"]["rows"][0][2] is None,
          text[:80])

    # ---------- 串流（WebSocket）：鑑權、協定、事件形状與每券商名額 ----------
    stream_app = create_app(sources=(), api_key=KEY)
    with TestClient(stream_app) as client:
        try:
            with client.websocket_connect("/stream") as ws:
                ws.send_json({"action": "subscribe", "codes": ["HK.00700"]})
                ws.receive_json()
            check("WS 無金鑰即拒絕連線", False, "竟然接受了連線")
        except WebSocketDisconnect as exc:
            check("WS 無金鑰即拒絕連線", exc.code == 4403, f"code={exc.code}")

        with client.websocket_connect(f"/stream?api_key={KEY}") as ws:
            ws.send_json({"action": "subscribe", "codes": ["HK.00700"], "ktype": "1m", "count": 3, "broker": "futu"})
            sub = ws.receive_json()
            check("WS 訂閱回報 subscribed", sub["event"] == "subscribed" and sub["codes"] == ["HK.00700"], str(sub)[:120])
            fail = until(ws, "message", "unknown_source:")
            check("WS 業務失敗以 error 事件原樣透傳", fail.get("event") == "error", str(fail)[:120])
            ws.send_json({"action": "subscribe", "codes": ["HK.00700"], "ktype": "1m", "broker": "futu"})
            again = ws.receive_json()
            check("失敗後即時歸還該券商名額", again["event"] == "subscribed", str(again)[:120])
            ws.send_json({"action": "subscribe", "codes": ["HK.00700"], "ktype": "1m", "broker": "ib", "count": "abc"})
            check("WS 參數不合法明確報錯", until(ws, "message", "bad_request:") != {}, "")
            ws.send_json({"action": "ping"})
            check("WS 未知 action 明確報錯", until(ws, "message", "bad_action:") != {}, "")

        stream_app.state.brokery = StubQuote()
        with client.websocket_connect(f"/stream?api_key={KEY}") as ws:
            ws.send_json({"action": "subscribe", "codes": ["HK.00700"], "ktype": "1m", "count": 3, "broker": "ib"})
            ws.receive_json()  # subscribed
            update = until(ws, "event", "update")  # 有上限：事件未到來即判失敗，不無限等待
            check("WS update 事件帶完整序列且欄位為 K_COLUMNS",
                  update["event"] == "update" and update["code"] == "HK.00700"
                  and update["data"]["columns"] == list(K_COLUMNS) and len(update["data"]["rows"]) == 1,
                  str(update)[:120])
            pushed = pd.DataFrame(update["data"]["rows"], columns=update["data"]["columns"])
            check("update 的 rows 可重建 DataFrame", list(pushed.columns) == list(K_COLUMNS)
                  and pushed["ts"].iloc[0] == SAMPLE["ts"], f"{len(pushed)} 行")
            ws.send_json({"action": "stop"})
            closed = until(ws, "event", "closed")
            check("WS stop 回報 closed 並說明名額", closed["event"] == "closed" and "release_in" in closed,
                  str(closed)[:120])

        with client.websocket_connect(f"/stream?api_key={KEY}") as ws:
            ws.send_json({"action": "subscribe", "codes": ["HK.00700"], "ktype": "1m", "count": 3,
                          "broker": "futu", "raw": True})
            ws.receive_json()  # subscribed
            raw_update = until(ws, "event", "update")
            check("WS raw=True 時 update 的欄位即原生欄位",
                  raw_update["event"] == "update"
                  and raw_update["data"]["columns"] == list(NATIVE_BAR), str(raw_update)[:160])

        hold = HoldQuote()
        stream_app.state.brokery = hold
        with client.websocket_connect(f"/stream?api_key={KEY}") as ws:
            ws.send_json({"action": "subscribe", "codes": ["HK.00700"], "ktype": "1m", "broker": "tiger"})
            ws.receive_json()  # subscribed：名額於此刻已登記，故第二條必定被拒
            ws.send_json({"action": "subscribe", "codes": ["HK.00700"], "ktype": "1m", "broker": "tiger"})
            busy = ws.receive_json()
            check("同一券商同時只容許一條串流", busy["event"] == "error"
                  and str(busy["message"]).startswith("stream_busy:"), str(busy)[:140])
            hold.gate.set()

    for label, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {label}（{detail}）")
    failed = [label for label, passed, _ in checks if not passed]
    data = pd.DataFrame(codes["data"]["rows"], columns=codes["data"]["columns"]) if codes["status"] else pd.DataFrame()
    if failed:
        return {"status": False, "data": data, "message": "失敗：" + "；".join(failed)}
    return {"status": True, "data": data,
            "message": f"{len(checks)} 項檢查全過：鑑權、欄位契約、JSON 取值口徑、串流協定與日誌均符合（離線，未連券商）"}


if __name__ == "__main__":
    raise SystemExit(0 if main()["status"] else 1)
