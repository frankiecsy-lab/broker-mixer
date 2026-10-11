"""期貨與指數的種子清單。

IB 沒有「一次過列出全市場」的接口，期貨與指數必須先給出產品代碼（root）或指數符號，
再由適配器展開所有到期月與掛牌交易所。本模組就是這份種子清單，全部條目均為實測可
解析者；新增時請先確認該 root 在目標帳戶確實有行情權限，避免清單出現取不到數據的
條目。

種子亦用於推斷富途要訪問哪些市場：富途按市場一次列舉期貨與指數，不認產品 root，故
只取種子所屬市場的清單。

股票不在此列：全市場股票由富途的 get_stock_basicinfo 一次取全，IB 只負責代碼轉換。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FutureSeed:
    """期貨產品種子。root 為券商原生產品代碼，market 僅作貨幣與市場提示。"""

    root: str
    market: str
    label: str


@dataclass(frozen=True)
class IndexSeed:
    """指數種子。symbol 為券商原生指數符號。"""

    symbol: str
    market: str
    label: str


# 美股指數期貨、商品期貨與期貨指數；root 已實測可在 IB 展開所有到期月。
FUTURE_ROOTS: tuple[FutureSeed, ...] = (
    FutureSeed("ES", "US", "S&P 500 E-mini"),
    FutureSeed("NQ", "US", "Nasdaq-100 E-mini"),
    FutureSeed("YM", "US", "Dow Jones E-mini"),
    FutureSeed("RTY", "US", "Russell 2000 E-mini"),
    FutureSeed("VIX", "US", "VIX Futures"),
    FutureSeed("CL", "US", "WTI Crude Oil"),
    FutureSeed("GC", "US", "Gold"),
    FutureSeed("SI", "US", "Silver"),
    FutureSeed("HG", "US", "Copper"),
    FutureSeed("ZN", "US", "10-Year Treasury Note"),
    FutureSeed("ZS", "US", "Soybean"),
    FutureSeed("ZW", "US", "Wheat"),
    FutureSeed("ZC", "US", "Corn"),
    FutureSeed("HSI", "HK", "恒生指數期貨"),
    FutureSeed("MHI", "HK", "恒生指數小型期貨"),
)

# 指數；symbol 已實測可在 IB 解析出交易所與貨幣。
INDEX_SYMBOLS: tuple[IndexSeed, ...] = (
    IndexSeed("HSI", "HK", "恒生指數"),
    IndexSeed("HSTECH", "HK", "恒生科技指數"),
    IndexSeed("VHSI", "HK", "恒生波動指數"),
    IndexSeed("SPX", "US", "S&P 500"),
    IndexSeed("NDX", "US", "Nasdaq-100"),
    IndexSeed("VIX", "US", "CBOE VIX"),
    IndexSeed("N225", "JP", "Nikkei 225"),
)
