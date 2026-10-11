"""Brokery：多券商標的清單與 K 線的統一入口。

對外只有一個 class。所有方法一律返回 {"status": bool, "data": DataFrame, "message": str}，
其中 data 的欄位固定為 brokers.base.COLUMNS（清單）或 brokers.base.K_COLUMNS（K 線），
code 一律為統一代碼（見 codes 模組）。

各券商的能力並不對稱，由 capabilities 調度而非強行湊齊：股票、期貨與指數的批量清單均由
富途按（市場, 證券類型）一次取全；IB 依種子展開所有到期月與交易所，並負責代碼轉換。某類
標的若無券商可提供，會明確返回失敗而不是空表，避免把「取不到」誤當「不存在」。只做 K 線的
券商（如 Tiger）不聲明清單能力，因此在清單流程中被跳過，在 K 線流程中仍可用。
"""
from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from . import store, universe
from .brokers.base import COLUMNS, K_COLUMNS, SymbolBroker, dedupe_rows
from .brokers.futu_broker import FutuBroker
from .brokers.ib_broker import IbBroker
from .brokers.tiger_broker import TigerBroker
from .brokers.webull_broker import WebullBroker
from .codes import FUTURE, INDEX, STOCK, CodeError, classify_symbol, parse_code
from .store import StoreError

BROKERS = {"futu": FutuBroker, "ib": IbBroker, "tiger": TigerBroker, "webull": WebullBroker}
DEFAULT_SOURCES = ("futu", "ib", "tiger", "webull")

# 預設只取港美兩市：全市場（含滬深日馬澳新加）動輒數萬條，需時自行傳入 markets。
DEFAULT_STOCK_MARKETS = ("HK", "US")


def _frame(rows: list[dict]) -> pd.DataFrame:
    """固定欄位順序構造 DataFrame；空結果亦保留欄位。"""
    return pd.DataFrame(rows, columns=COLUMNS)


def _ok(rows: list[dict], message: str = "ok") -> dict:
    return {"status": True, "data": _frame(rows), "message": message}


def _fail(message: str) -> dict:
    return {"status": False, "data": _frame([]), "message": message}


class Brokery:
    """以統一代碼格式取得標的清單與 K 線。"""

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

    def close(self) -> None:
        for broker in self._brokers.values():
            broker.close()

    def __enter__(self) -> "Brokery":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()

    # ---------- 清單 ----------

    def list_stocks(self, markets: Iterable[str] = DEFAULT_STOCK_MARKETS) -> dict:
        """全市場股票清單。markets 為統一市場前綴（如 HK、US、SH）。"""
        wanted = tuple(m.upper() for m in markets)
        return self._gather(STOCK, lambda b: b.list_stocks(wanted), "股票清單")

    def list_futures(self, roots: Iterable[str] | None = None) -> dict:
        """期貨清單：含主連（code 帶 main 後綴）與所有到期月（expiry 欄）。"""
        seeds = _pick(universe.FUTURE_ROOTS, roots, "root")
        return self._gather(FUTURE, lambda b: b.list_futures(seeds), "期貨清單")

    def list_indices(self, symbols: Iterable[str] | None = None) -> dict:
        """指數清單。"""
        seeds = _pick(universe.INDEX_SYMBOLS, symbols, "symbol")
        return self._gather(INDEX, lambda b: b.list_indices(seeds), "指數清單")

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

    def _gather(self, symbol_type: str, call, label: str) -> dict:
        providers = [b for b in self._brokers.values() if b.supports(symbol_type)]
        if not providers:
            return _fail(f"no_source: 已啟用的券商（{', '.join(self._brokers)}）不提供{label}")

        rows: list[dict] = []
        errors: list[str] = []
        for broker in providers:
            try:
                rows.extend(call(broker))
            except Exception as exc:
                errors.append(f"{broker.source}: {type(exc).__name__}: {exc}")

        rows = dedupe_rows(rows)
        if not rows and errors:
            return _fail(f"{label}取得失敗：" + "；".join(errors))
        message = "ok" if not errors else f"ok（{len(rows)} 條，部分券商失敗）" + "；".join(errors)
        return _ok(rows, message)


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
