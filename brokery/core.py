"""Brokery：多券商標的清單、K 線與戶口的統一入口。

對外只有一個 class。所有方法一律返回 {"status": bool, "data": DataFrame, "message": str}，
其中 data 的欄位固定為 brokers.base.COLUMNS（清單）、brokers.base.K_COLUMNS（K 線）、
brokers.base.ACCOUNT_COLUMNS（戶口）或 brokers.base.BROKER_COLUMNS（連線狀態），code 一律為統一
代碼（見 codes 模組）。

各券商的能力並不對稱，由 capabilities 調度而非強行湊齊：股票、期貨與指數的批量清單均由
富途按（市場, 證券類型）一次取全；IB 依種子展開所有到期月與交易所，並負責代碼轉換。某類
標的若無券商可提供，會明確返回失敗而不是空表，避免把「取不到」誤當「不存在」。只做 K 線的
券商（如 Tiger）不聲明清單能力，因此在清單流程中被跳過，在 K 線流程中仍可用。
"""
from __future__ import annotations

import time
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout

import pandas as pd

from . import store, universe
from .brokers.base import (
    ACC_CASH,
    ACC_MARGIN,
    ACCOUNT_COLUMNS,
    BROKER_COLUMNS,
    COLUMNS,
    K_COLUMNS,
    SymbolBroker,
    dedupe_rows,
)
from .brokers.futu_broker import FutuBroker
from .brokers.ib_broker import IbBroker
from .brokers.tiger_broker import TigerBroker
from .brokers.webull_broker import WebullBroker
from .codes import FUTURE, INDEX, STOCK, CodeError, classify_symbol, parse_code
from .config import get_settings
from .store import StoreError

BROKERS = {"futu": FutuBroker, "ib": IbBroker, "tiger": TigerBroker, "webull": WebullBroker}
DEFAULT_SOURCES = ("futu", "ib", "tiger", "webull")

# 預設只取港美兩市：全市場（含滬深日馬澳新加）動輒數萬條，需時自行傳入 markets。
DEFAULT_STOCK_MARKETS = ("HK", "US")

# 戶口性質篩選的取值（all 為不篩選）。戶口環境不再區分：各券商一律只返回真實戶口。
ACC_FILTERS = ("all", ACC_CASH, ACC_MARGIN)


def _frame(rows: list[dict]) -> pd.DataFrame:
    """固定欄位順序構造 DataFrame；空結果亦保留欄位。"""
    return pd.DataFrame(rows, columns=COLUMNS)


def _ok(rows: list[dict], message: str = "ok") -> dict:
    return {"status": True, "data": _frame(rows), "message": message}


def _fail(message: str) -> dict:
    return {"status": False, "data": _frame([]), "message": message}


def _accounts_ok(rows: list[dict], message: str) -> dict:
    return {"status": True, "data": pd.DataFrame(rows, columns=ACCOUNT_COLUMNS), "message": message}


def _accounts_fail(message: str) -> dict:
    return {"status": False, "data": pd.DataFrame([], columns=ACCOUNT_COLUMNS), "message": message}


def _brokers_frame(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=BROKER_COLUMNS)


def _brokers_ok(rows: list[dict], message: str) -> dict:
    return {"status": True, "data": _brokers_frame(rows), "message": message}


def _brokers_fail(message: str) -> dict:
    return {"status": False, "data": _brokers_frame([]), "message": message}


class Brokery:
    """以統一代碼格式取得標的清單與 K 線，並取得各券商的戶口與資金。"""

    def __init__(self, sources: Iterable[str] = DEFAULT_SOURCES, autype: str = "qfq"):
        """autype 為 K 線的預設複權模式（qfq/hfq/none），逐次呼叫可用 get_kline 的參數覆蓋。

        跨券商比價建議在這一處統一設為 none：各券商只支援自己聲明的模式，不支持的一律報錯。
        """
        names = tuple(sources)
        unknown = [name for name in names if name not in BROKERS]
        if unknown:
            raise CodeError(f"unknown_source: {', '.join(unknown)}；可用券商為 {', '.join(BROKERS)}")
        self._brokers: dict[str, SymbolBroker] = {name: BROKERS[name]() for name in names}
        self.autype = autype

    # ---------- 生命週期 ----------

    def sources(self) -> list[str]:
        """目前啟用的券商名稱。"""
        return list(self._brokers)

    def adapters(self) -> dict[str, SymbolBroker]:
        """目前啟用的適配器實例（唯讀用途：供閘道查詢各券商的能力聲明，不應用它直接取數）。"""
        return dict(self._brokers)

    def close(self) -> None:
        for broker in self._brokers.values():
            broker.close()

    def __enter__(self) -> "Brokery":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()

    # ---------- 清單 ----------

    def list_stocks(self, markets: Iterable[str] | None = None, broker: str | None = None) -> dict:
        """股票清單。markets 為統一市場前綴（如 HK、US、SH），省略即用 DEFAULT_STOCK_MARKETS；
        broker 指定只向該券商取（未啟用即 unknown_source，不提供該品種即 type_unsupported，
        一律明確報錯，不會靜靜改用別家湊數）。"""
        wanted = tuple(m.upper() for m in markets) if markets else DEFAULT_STOCK_MARKETS
        return self._gather(STOCK, lambda b: b.list_stocks(wanted), "股票清單",
                            broker=broker, markets=wanted)

    def list_futures(self, roots: Iterable[str] | None = None,
                     markets: Iterable[str] | None = None, broker: str | None = None) -> dict:
        """期貨清單：含主連（code 帶 main 後綴）與所有到期月（expiry 欄）。

        期貨接口沒有市場參數，故 markets（統一市場前綴）由本層按返回行的 market 過濾。
        """
        seeds = _pick(universe.FUTURE_ROOTS, roots, "root")
        return self._gather(FUTURE, lambda b: b.list_futures(seeds), "期貨清單",
                            broker=broker, markets=markets)

    def list_indices(self, symbols: Iterable[str] | None = None,
                     markets: Iterable[str] | None = None, broker: str | None = None) -> dict:
        """指數清單。markets 的處理同期貨清單（按返回行的 market 過濾）。"""
        seeds = _pick(universe.INDEX_SYMBOLS, symbols, "symbol")
        return self._gather(INDEX, lambda b: b.list_indices(seeds), "指數清單",
                            broker=broker, markets=markets)

    def list_all(self, markets: Iterable[str] = DEFAULT_STOCK_MARKETS) -> dict:
        """一次取得股票、期貨與指數。部分券商失敗時仍返回已取得的資料。"""
        results = [self.list_stocks(markets), self.list_futures(), self.list_indices()]
        rows = [row for res in results for row in res["data"].to_dict("records")]
        failed = [res["message"] for res in results if not res["status"]]
        if len(failed) == len(results):
            return _fail("；".join(failed))
        message = "ok" if not failed else "ok（部分失敗）" + "；".join(failed)
        return _ok(dedupe_rows(rows), message)

    # ---------- 代碼轉換 ----------

    def convert(self, code: str, source: str = "ib") -> dict:
        """統一代碼 → 該券商原生合約。用於把 US.NVDA、HK.00700、US.ESmain 換成券商內部標識。"""
        broker = self._brokers.get(source)
        if broker is None:
            return _fail(f"unknown_source: {source}；已啟用 {', '.join(self._brokers) or '無'}")
        try:
            info = broker.to_contract(code)
        except CodeError as exc:
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"convert_failed: {type(exc).__name__}: {exc}")

        contract = info["contract"]
        parsed = parse_code(info["code"])
        row = broker.make_row(
            code=info["code"],
            name="",
            market=parsed.market,
            symbol=parsed.symbol,
            symbol_type=info["symbol_type"],
            currency=contract.currency or "",
            exchange=contract.exchange or "",
            expiry=contract.lastTradeDateOrContractMonth or "",
            raw_code=info["raw_code"],
        )
        return _ok([row], f"ok: {info['code']} → {info['raw_code']}")

    # ---------- K 線 ----------

    @staticmethod
    def _check_kline_type(adapter: SymbolBroker, code: str) -> None:
        """按統一代碼推斷品種，來源未聲明該品種即拋出 CodeError。

        嚴禁把期權、期貨或指數當股票送進上游等它報錯：不支持與否由適配器聲明，此處統一拒绝。
        """
        parsed = parse_code(code)
        symbol_type = classify_symbol(parsed.market, parsed.symbol)
        if not adapter.supports_kline(symbol_type):
            raise CodeError(
                f"type_unsupported: {adapter.source} 不提供 {symbol_type} 的 K 線"
                f"（{adapter.source} 只提供 {'/'.join(adapter.kline_symbol_types) or '無'}）"
            )

    def get_kline(
        self,
        code: str,
        ktype: str = "day",
        count: int = 60,
        broker: str = "futu",
        autype: str | None = None,
    ) -> dict:
        """取 K 線，統一以富途格式輸出（欄位固定為 brokers.base.K_COLUMNS）。

        count 為 bar 數（富途語義），IB 由 bar 數反推時間跨度後再截尾；broker 選擇來源。
        autype 省略時用構造函數的預設值；各券商只支援自己聲明的複權模式（見 SymbolBroker.autypes），
        要求了不支持的模式即返回 status=False，不會靜靜改用另一種價格。品種（股票／期貨／指數／期權）
        由代碼推斷，來源未聲明該品種亦返回 status=False（type_unsupported）。複權只對股票有效：期貨、
        指數與期權沒有公司行動，實測各來源的 qfq 與 none 逐根完全相同，傳哪一種都不影響價格。
        """
        adapter = self._brokers.get(broker)
        if adapter is None:
            return _fail(f"unknown_source: {broker}；已啟用 {', '.join(self._brokers) or '無'}")
        if count < 1:
            return _fail(f"bad_count: {count}，bar 數須為正整數")
        autype = self.autype if autype is None else autype
        if autype not in adapter.autypes:
            return _fail(
                f"autype_unsupported: {broker} 不支援複權 {autype}"
                f"（{broker} 只支援 {'/'.join(adapter.autypes) or '無'}）；"
                f"取原始成交價請用 autype=\"none\""
            )
        try:
            self._check_kline_type(adapter, code)
            rows = adapter.get_kline(code, ktype, count, autype)
        except ValueError as exc:  # CodeError 與時間換算錯誤均屬輸入問題
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"kline_failed: {type(exc).__name__}: {exc}")
        if not rows:
            return _fail(f"empty_kline: {code} 未取到任何 bar（請檢查代碼、ktype 或券商權限）")
        return {
            "status": True,
            "data": pd.DataFrame(rows, columns=K_COLUMNS),
            "message": f"ok: {len(rows)} 根 {ktype} K 線（{code}，來源 {broker}）",
        }

    def stream_kline(
        self,
        codes: str | Iterable[str],
        ktype: str = "1m",
        count: int = 60,
        broker: str = "futu",
        autype: str | None = None,
        seconds: float = 60,
        on_update=None,
    ) -> dict:
        """串流最新 K 線：先返回歷史 bar，之後最新一根每次變化即回呼 on_update(code, rows)。

        codes 可為一個代碼或一組代碼；多個代碼共用同一條連線，對應同時顯示多張 K 線圖。rows 為
        該代碼按 ts 升序、不超過 count 根的完整結果，回呼在券商的推送執行緒中發生，故回呼內不要做
        耗時工作。兩家均以原生推送實現（富途的實時 K 線回呼、IB 的 keepUpToDate）。

        seconds 為持續秒數，0 表示直到 Ctrl-C（按 Ctrl-C 屬正常結束）。返回的 data 為各代碼最終的
        bar 合併結果。串流的支援範圍由券商另行聲明（stream_ktypes/stream_autypes）：IB 的推送只能
        用 autype="none"，不支持時在開始前就明確返回 status=False。
        """
        adapter = self._brokers.get(broker)
        if adapter is None:
            return _fail(f"unknown_source: {broker}；已啟用 {', '.join(self._brokers) or '無'}")
        wanted = (codes,) if isinstance(codes, str) else tuple(codes)
        if not wanted:
            return _fail("bad_codes: 至少需要一個代碼")
        if count < 1:
            return _fail(f"bad_count: {count}，bar 數須為正整數")
        if ktype not in adapter.stream_ktypes:
            return _fail(
                f"ktype_unsupported: {broker} 不支持串流 {ktype}"
                f"（可串流 {'/'.join(adapter.stream_ktypes) or '無'}）"
            )
        autype = self.autype if autype is None else autype
        if autype not in adapter.stream_autypes:
            return _fail(
                f"autype_unsupported: {broker} 的 K 線串流不支援複權 {autype}"
                f"（{broker} 串流只支援 {'/'.join(adapter.stream_autypes) or '無'}）；"
                '串流請用 autype="none"'
            )
        try:
            for code in wanted:
                self._check_kline_type(adapter, code)
            frames = adapter.stream_kline(wanted, ktype, count, autype, seconds, on_update)
        except ValueError as exc:  # CodeError 與時間換算錯誤均屬輸入問題
            return _fail(str(exc))
        except Exception as exc:
            return _fail(f"stream_failed: {type(exc).__name__}: {exc}")

        rows = [row for bars in frames.values() for row in bars]
        if not rows:
            return _fail(f"empty_kline: {', '.join(wanted)} 未取到任何 bar（請檢查代碼、ktype 或券商權限）")
        rows.sort(key=lambda row: (row["code"], row["ts"]))
        return {
            "status": True,
            "data": pd.DataFrame(rows, columns=K_COLUMNS),
            "message": (
                f"ok: 串流結束，{len(frames)} 個代碼共 {len(rows)} 根 {ktype} K 線"
                f"（來源 {broker}，{seconds} 秒）"
            ),
        }

    # ---------- 戶口 ----------

    def get_accounts(
        self,
        broker: str | None = None,
        acc_type: str = "all",
        currency: str | None = None,
    ) -> dict:
        """戶口清單與資金，四家一律以 brokers.base.ACCOUNT_COLUMNS 為欄位。

        一律只返回真實且已啟用的戶口，不區分 real/simulate：IB 的真實與模擬由所連 Gateway 決定，
        本身沒有這個維度；富途與 Tiger 的模擬戶口、富途的已停用戶口因此不列入。
        acc_type 為戶口性質（all/cash/margin），是返回欄位，不傳即全部列回；filter 只在本處做一次，
        各券商只返回自己聲明的 acc_type（見 SymbolBroker.acc_types），要求了不支持的值即明確返回
        status=False，不會憑空造出戶口。券商原樣透傳、不在詞表內的性質（如 IB 的 individual）只在不過濾時
        列回，過濾時一律在 message 點名說明（acc_type_other），不會靜默消失。

        broker 省略時查所有已啟用的券商，個別券商連線失敗或沒有該類戶口時仍返回已取得的戶口，並在
        message 中逐項說明。currency 指定時金額以該幣種計（Webull 改讀該幣種的明細），省略時以各券商
        原生匯總幣種為準，一律不做匯率換算；該券商沒有對應欄位者為 NaN（如 Webull 無淨資產匯總）。
        """
        if acc_type not in ACC_FILTERS:
            return _accounts_fail(f"bad_acc_type: {acc_type}，可取 {'/'.join(ACC_FILTERS)}")
        if broker is None:
            adapters = list(self._brokers.values())
        else:
            adapter = self._brokers.get(broker)
            if adapter is None:
                return _accounts_fail(f"unknown_source: {broker}；已啟用 {', '.join(self._brokers) or '無'}")
            adapters = [adapter]

        rows: list[dict] = []
        notes: list[str] = []
        for adapter in adapters:
            if acc_type != "all" and acc_type not in adapter.acc_types:
                notes.append(
                    f"acc_type_unsupported: {adapter.source} 沒有 {acc_type} 戶口"
                    f"（{adapter.source} 只有 {'/'.join(adapter.acc_types) or '無'}）"
                )
                continue
            try:
                rows.extend(adapter.get_accounts(currency))
            except Exception as exc:
                notes.append(f"{adapter.source}: {type(exc).__name__}: {exc}")

        kept: list[dict] = []
        for row in rows:
            if acc_type == "all" or row["acc_type"] == acc_type:
                kept.append(row)
            elif row["acc_type"] not in ACC_FILTERS:
                # 券商原樣透傳的戶口性質（如 IB 的 AccountType=INDIVIDUAL → individual）不在統一詞表內：
                # 既不能當它符合篩選，亦不可靜默丟列，否則該券商在結果中無故消失而無從得知原因。
                notes.append(f"acc_type_other: {row['source']} 的 {row['account_id']} 為 {row['acc_type']}"
                             f"（非 {'/'.join(ACC_FILTERS[1:])}），未列入")
        rows = _dedupe_accounts(kept)
        detail = f"{len(rows)} 個戶口（來源 {', '.join(a.source for a in adapters)}）"
        if not rows:
            return _accounts_fail("no_account: " + "；".join(notes or ["沒有符合條件的戶口"]))
        message = f"ok: {detail}" + ("" if not notes else "；注意：" + "；".join(notes))
        return _accounts_ok(rows, message)

    # ---------- 連線狀態 ----------

    def get_brokers(self, broker: str | None = None) -> dict:
        """各券商的連線狀態與探測延遲，一律以 brokers.base.BROKER_COLUMNS 為欄位。

        探測用一次戶口查詢：只需連線與鑑權，不需要行情數據權限，因此行情權限缺失、市場休市或
        某市場沒有歷史數據時，不會被誤報為連線斷開。各家並行探測，每家一律有一行結果：連不上者
        connected=False、latency_ms 為 NaN（不以任何數字湊出），原因原樣寫入 detail。
        只要已啟用的券商都取得了結果即 status=True（哪怕全部連不上，「全部斷開」本身即有效答案）；
        只有無券商可探測或指定了未啟用的券商時才 status=False。

        探測會實際建立連線，故不設快取，也不應定時輪詢；超過 .env 的請求超時仍未返回者記為
        timeout，本方法不會因此無限等待（該次呼叫仍會在後台跑完，但不影響本次返回）。
        """
        if broker is None:
            adapters = list(self._brokers.values())
        else:
            adapter = self._brokers.get(broker)
            if adapter is None:
                return _brokers_fail(f"unknown_source: {broker}；已啟用 {', '.join(self._brokers) or '無'}")
            adapters = [adapter]
        if not adapters:
            return _brokers_fail(f"no_source: 未啟用任何券商（可用 {', '.join(BROKERS)}）")

        limit = max(1.0, float(get_settings().request_timeout))
        # 不用 with：退出時會 join 仍在跑的執行緒，令上面的超時失效。
        pool = ThreadPoolExecutor(max_workers=len(adapters))
        try:
            futures = [pool.submit(self._probe, adapter) for adapter in adapters]
            rows = []
            for adapter, future in zip(adapters, futures):
                try:
                    rows.append(future.result(timeout=limit))
                except FutureTimeout:
                    rows.append({"source": adapter.source, "connected": False, "latency_ms": float("nan"),
                                 "accounts": 0, "detail": f"timeout: 超過 {limit}s 未返回",
                                 "checked_at": int(time.time())})
        finally:
            pool.shutdown(wait=False, cancel_futures=True)

        down = [row["source"] for row in rows if not row["connected"]]
        speed = "，".join(f"{row['source']} {row['latency_ms']:.0f}ms" for row in rows if row["connected"])
        detail = f"{len(rows)} 個券商（{speed or '無一可連'}）"
        message = f"ok: 已探測 {detail}" if not down else f"ok（{detail}，未能連接 {'、'.join(down)}）"
        return _brokers_ok(rows, message)

    def _probe(self, adapter: SymbolBroker) -> dict:
        """以一次戶口查詢量該券商的往返時間；失敗不拋出，改為 connected=False。"""
        started = time.perf_counter()
        try:
            accounts = adapter.get_accounts(None)
            latency = (time.perf_counter() - started) * 1000.0
            return {"source": adapter.source, "connected": True, "latency_ms": latency,
                    "accounts": len(accounts), "detail": "", "checked_at": int(time.time())}
        except Exception as exc:
            return {"source": adapter.source, "connected": False, "latency_ms": float("nan"),
                    "accounts": 0, "detail": f"{type(exc).__name__}: {exc}", "checked_at": int(time.time())}

    # ---------- 離線讀取 ----------

    def get_code(self, name: str = store.CODES_DATASET) -> dict:
        """讀回已存放的 CODES（parquet）。離線執行，不需要任何券商連線。"""
        try:
            frame = store.load_frame(name)
        except StoreError as exc:
            return _fail(f"{exc}；請先執行 run_futu_codes_store.py")
        return {
            "status": True,
            "data": frame,
            "message": f"ok: 離線讀回 {len(frame)} 條 CODES（{name}）",
        }

    # ---------- 內部 ----------

    def _gather(self, symbol_type: str, call, label: str,
                broker: str | None = None, markets: Iterable[str] | None = None) -> dict:
        """向聲明支持該品種的券商取清單。

        broker 指定只向一家取：未啟用即 unknown_source，該家未聲明該品種即 type_unsupported，一律明確
        報錯而不靜默改用別家。markets 只過濾返回行的 market，用於沒有市場參數的接口（期貨／指數）；
        股票清單的市場由適配器自己處理，這裡的過濾只是確保返回的確實是所請求的市場。
        """
        if broker:
            adapter = self._brokers.get(broker)
            if adapter is None:
                return _fail(f"unknown_source: {broker}；已啟用 {', '.join(self._brokers) or '無'}")
            if not adapter.supports(symbol_type):
                return _fail(
                    f"type_unsupported: {broker} 不提供{label}"
                    f"（{broker} 只提供 {'/'.join(adapter.capabilities) or '無'}）"
                )
            providers = [adapter]
        else:
            providers = [b for b in self._brokers.values() if b.supports(symbol_type)]
            if not providers:
                return _fail(f"no_source: 已啟用的券商（{', '.join(self._brokers)}）不提供{label}")

        rows: list[dict] = []
        errors: list[str] = []
        for adapter in providers:
            try:
                rows.extend(call(adapter))
            except Exception as exc:
                errors.append(f"{adapter.source}: {type(exc).__name__}: {exc}")

        rows = dedupe_rows(rows)
        if not rows and errors:
            return _fail(f"{label}取得失敗：" + "；".join(errors))
        if markets:
            keep = {str(m).upper() for m in markets}
            kept = [row for row in rows if row["market"] in keep]
            if not kept and rows:
                # 取到了但全部不在指定市場：空表不是成功，必須點名（不以空表冒充）
                return _fail(f"empty_list: {label}在 {'/'.join(sorted(keep))} 沒有條目")
            rows = kept
        message = "ok" if not errors else f"ok（{len(rows)} 條，部分券商失敗）" + "；".join(errors)
        return _ok(rows, message)


def _dedupe_accounts(rows: list[dict]) -> list[dict]:
    """同一戶口的同一幣種只保留一列，保留先到的那一列。

    幣種要列入鍵：IB 的多幣種戶口按幣種各列一欄（各欄的金額互不重疊），只按戶口去重會把它們合併
    成一欄而丟掉其餘幣種的資金。
    """
    best: dict[tuple, dict] = {}
    for row in rows:
        best.setdefault((row["source"], row["account_id"], row["currency"]), row)
    return list(best.values())


def _pick(seeds: tuple, wanted: Iterable[str] | None, attr: str) -> list:
    """依名稱篩選種子；名稱不在種子清單時明確報錯，避免靜默返回空清單。"""
    if not wanted:
        return list(seeds)
    names = {name.upper() for name in wanted}
    picked = [seed for seed in seeds if getattr(seed, attr).upper() in names]
    missing = names - {getattr(seed, attr).upper() for seed in picked}
    if missing:
        raise CodeError(f"unknown_seed: {', '.join(sorted(missing))} 不在種子清單中")
    return picked
