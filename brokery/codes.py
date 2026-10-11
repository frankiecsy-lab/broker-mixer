"""統一代碼格式與各券商原生代碼的雙向轉換。

統一代碼沿用富途格式 ``市場前綴.符號``（如 US.NVDA、HK.00700）。各券商的原生代碼
只在其適配器內部出現，對外一律輸出統一代碼。新增券商時只需在此登記交易所與市場的
對應關係，不得改動統一代碼的語義。

本模組不依賴任何券商 SDK，只做純字串映射；Contract 物件的構造由各適配器負責。
"""
from __future__ import annotations

import re
from dataclasses import dataclass

CODE_PATTERN = re.compile(r"^(?P<market>[A-Z]{2,3})\.(?P<symbol>.+)$")

# 統一市場前綴 → 結算貨幣。與富途的市場前綴保持一致。
MARKET_CURRENCY = {
    "US": "USD",
    "HK": "HKD",
    "SG": "SGD",
    "SH": "CNY",
    "SZ": "CNY",
    "JP": "JPY",
    "MY": "MYR",
    "AU": "AUD",
    "CA": "CAD",
}

# 券商原生交易所 → 統一市場前綴。用於把券商返回的合約映射回統一代碼。
EXCHANGE_MARKET = {
    "SEHK": "HK",
    "HKEX": "HK",
    "HKFE": "HK",
    "SGX": "SG",
    "NASDAQ": "US",
    "NASDAQ.NGS": "US",
    "NYSE": "US",
    "NYSE ARCA": "US",
    "ARCA": "US",
    "AMEX": "US",
    "SMART": "US",
    "MEMX": "US",
    "CBOE": "US",
    "CBOE2": "US",
    "CFE": "US",
    "ISE": "US",
    "CME": "US",
    "CBOT": "US",
    "NYMEX": "US",
    "COMEX": "US",
    "NYBOT": "US",
    "ICE": "US",
    "ICEUS": "US",
    "SSE": "SH",
    "SZSE": "SZ",
    "OSE": "JP",
    "OSE.JPN": "JP",
    "JPX": "JP",
    "ASX": "AU",
    "TSX": "CA",
    "SXC": "CA",
}

# 次要交易場所：同一合約常在多處掛牌（如 CME 與 QBALGO），清單只保留主場以免重複。
SECONDARY_EXCHANGES = frozenset(
    {
        "QBALGO",
        "TRULYTA",
        "MEMX",
        "CBOE2",
        "NASDAQ.NGS",
        "AUTOX",
        "ARCA",
        "EDGX",
    }
)

# 主連（連續合約）後綴，與富途原生寫法一致（如 SG.CNmain）。
MAIN_SUFFIX = "main"

STOCK = "STOCK"
FUTURE = "FUTURE"
INDEX = "INDEX"
OPTION = "OPTION"
SYMBOL_TYPES = (STOCK, FUTURE, INDEX, OPTION)

# 富途期權代碼＝正股符號 + 到期日(YYMMDD) + 買賣標記 + 行權價（如 AAPL261106C110000）。
OPTION_PATTERN = re.compile(r"^[A-Z]{1,5}\d{6}[CP]\d+$")
# 富途的港股指數為六位數字且以 8 開頭（800000 為恒生指數）；美股指數以句點開頭（.SPX）。
HK_INDEX_PATTERN = re.compile(r"^8\d{5}$")


class CodeError(ValueError):
    """統一代碼不合法或無法映射到指定券商。"""


@dataclass(frozen=True)
class UnifiedCode:
    """拆解後的統一代碼。"""

    market: str
    symbol: str


def parse_code(code: str) -> UnifiedCode:
    """把統一代碼拆解為市場前綴與符號，格式不合法時拋出 CodeError。"""
    if not isinstance(code, str):
        raise CodeError(f"bad_code: {code!r}")
    match = CODE_PATTERN.match(code.strip())
    if not match:
        raise CodeError(f"bad_code: {code!r}，須為「市場.符號」格式（如 US.NVDA）")
    market = match.group("market").upper()
    if market not in MARKET_CURRENCY:
        raise CodeError(f"unknown_market: {market}")
    return UnifiedCode(market=market, symbol=match.group("symbol"))


def build_code(market: str, symbol: str) -> str:
    """組合統一代碼；HK 股票符號統一補零至五位，貼合富途顯示格式。"""
    return f"{market.upper()}.{to_display_symbol(market, symbol)}"


def to_native_symbol(market: str, symbol: str) -> str:
    """轉為券商原生符號。IB 的港股以不帶前導零的數字登記（00700 → 700）。"""
    if market.upper() == "HK" and symbol.isdigit():
        return symbol.lstrip("0") or "0"
    return symbol


def to_display_symbol(market: str, symbol: str) -> str:
    """轉為統一顯示符號。HK 股票補零至五位（700 → 00700）。"""
    if market.upper() == "HK" and symbol.isdigit():
        return symbol.zfill(5)
    return symbol


def currency_of(market: str) -> str:
    """取得市場對應的結算貨幣。"""
    try:
        return MARKET_CURRENCY[market.upper()]
    except KeyError:
        raise CodeError(f"unknown_market: {market}") from None


def market_of(exchange: str, currency: str = "") -> str:
    """由券商交易所與貨幣推斷統一市場前綴；無法判斷時拋出 CodeError。"""
    market = EXCHANGE_MARKET.get((exchange or "").upper())
    if market:
        return market
    # 交易所未登記時退回貨幣推斷，避免新交易所直接導致整批失敗。
    for candidate, cur in MARKET_CURRENCY.items():
        if currency and cur == currency.upper():
            return candidate
    raise CodeError(f"unmapped_exchange: {exchange!r} currency={currency!r}")


def is_secondary_exchange(exchange: str) -> bool:
    """判斷是否次要交易場所，用於去重時剔除重複掛牌。"""
    return (exchange or "").upper() in SECONDARY_EXCHANGES


def split_future_symbol(symbol: str) -> tuple[str, str]:
    """拆離期貨符號的主連後綴與到期月。

    ``ESmain`` → ("ES", "")；``ES202612`` → ("ES", "202612")；``ES20261218`` →
    ("ES", "20261218")。主連以空字串表示，與個月份合約在清單中分欄呈現。到期月可為
    YYYYMM 或 YYYYMMDD，後者是 IB 對期貨合約返回的最後交易日格式。
    """
    if symbol.endswith(MAIN_SUFFIX):
        return symbol[: -len(MAIN_SUFFIX)], ""
    match = re.match(r"^(?P<root>[A-Za-z]+)(?P<expiry>\d{4,8})$", symbol)
    if match:
        return match.group("root"), match.group("expiry")
    return symbol, ""


def classify_symbol(market: str, symbol: str) -> str:
    """由統一代碼推斷品種，返回 STOCK／FUTURE／INDEX／OPTION。

    只用於 K 線的能力閘與跨券商對映；標的清單仍以券商返回的類型欄為準。
    未帶到期月或主連後綴的符號一律按股票處理，因各市場的期貨代碼均帶後綴。
    """
    if OPTION_PATTERN.match(symbol):
        return OPTION
    if symbol.startswith("."):
        return INDEX
    if market.upper() == "HK" and HK_INDEX_PATTERN.match(symbol):
        return INDEX
    root, expiry = split_future_symbol(symbol)
    if expiry or root != symbol:
        return FUTURE
    return STOCK
