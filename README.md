# brokery

跨券商標的與行情統一層。以富途代碼格式為唯一對外格式（`US.NVDA`、`HK.00700`、`US.ESmain`），
把不同券商的原生代碼與能力差異藏在內部。清單與代碼轉換支援 **FUTU（富途）** 與 **IB（Interactive
Brokers）**；K 線與 K 線串流另支援 **Tiger（老虎）** 與 **Webull**。

## 當前狀態

| 功能 | 狀態 | 資料來源 |
| --- | --- | --- |
| 全量代碼清單 `list_all`（股票 + 期貨 + 指數） | ✅ 可用 | FUTU（港美兩市實測 38,568 條） |
| 股票清單（含 ETF，一次取全） | ✅ 可用 | FUTU |
| 期貨清單（主連 + 所有到期月） | ✅ 可用 | FUTU + IB |
| 指數清單 | ✅ 可用 | FUTU + IB |
| 代碼雙向轉換（統一代碼 ↔ IB 原生合約） | ✅ 可用 | IB |
| 離線存放與讀回（parquet + meta） | ✅ 可用 | 本地 `brokery/data/`（由 `.env` 指定） |
| 離線讀取代碼清單 `get_code` | ✅ 可用 | 本地 parquet，不需要 OpenD / IB |
| K 線 `get_kline`（統一格式、以 bar 數取數） | ✅ 可用 | FUTU + IB（日/週/月線實測逐根按 `ts` 對齊，價格一致）+ Webull（日線/分鐘線實測，日線確實做了前復權，調整因子與 IB 一致：與原始成交價最大相差 0.062%）+ Tiger（日線/1 分鐘線實測，`autype="none"` 時 close 與 FUTU 逐根完全一致） |
| 前復權跨券商對照（日內與日線） | ✅ 可用 | FUTU `qfq` + IB `ADJUSTED_LAST` + Tiger `right=BR` + Webull（日線固定前復權）：`HK.00005` 日線 60 根四家共同 60 根逐根對齊，以富途為準 Tiger 最大相差 0.02%、IB/Webull 0.44% |
| 品種支持矩陣（股票／期貨／指數／期權）與復權適用範圍 | ✅ 已核實 | 四家實測（`run_kline_matrix.py`，31 項檢查）：不支持的品種由適配器聲明、`core` 統一返回 `type_unsupported`；復權只對股票有效（期貨／指數／期權的 `qfq` 與 `none` 逐根完全相同）；指數代碼可跨券商（`HK.800000` 富途與 IB 的 close 完全相同、`US..SPX` Tiger 與 IB 完全相同） |
| K 線串流 `stream_kline`（一條連線同時串流多個代碼） | ✅ 可用 | FUTU 實時推送 + IB `keepUpToDate` + Tiger `subscribe_kline` 原生推送 + Webull 輪詢批量 bar（憑證只開通 HK 行情，美股明確報錯 `market_data_not_subscribed`）；實測 futu/ib/tiger/webull 全部合規格（Tiger 一條連線同時串流港美 3 個代碼；Webull 以 2 個 HK 代碼共用一次輪詢）；推送本身要開市才收得到 |

## 快速開始

前置條件：富途 OpenD 已啟動、IB TWS/IB Gateway 已啟動，連線參數與各券商金鑰寫在 `.env`（Tiger 需
RSA 私鑰、Webull 需在 App 中批准一次授權）。

```python
from brokery import Brokery

with Brokery() as bk:                      # 預設同時啟用 futu / ib / tiger / webull
    codes = bk.list_all(["HK", "US"])      # 全量 CODES：股票 + 期貨 + 指數
    stocks = bk.list_stocks(["HK"])        # 只取股票與 ETF
    futures = bk.list_futures(["ES", "HSI"])  # 指定產品（IB 種子展開）
    mapping = bk.convert("HK.00700")       # 統一代碼 → IB 原生合約（含 conId）
    kline = bk.get_kline("HK.00001")                                 # 富途日線最近 60 根（預設前復權）
    kline_ib = bk.get_kline("HK.00001", broker="ib", autype="none")  # 同一組 bar，改由 IB 取（比價一律取原始價）
    kline_wb = bk.get_kline("HK.00001", broker="webull")             # 改由 Webull 取（日線只能前復權，無復權參數）

    # 串流：四個代碼共用一條連線（對應同時顯示四張 K 線圖），最新一根每次變化即回呼
    live = bk.stream_kline(["HK.00005", "US.NVDA"], ktype="1m", count=30, broker="futu",
                           seconds=60, on_update=lambda code, rows: print(code, rows[-1]["time_key"]))

print(stocks["status"], len(stocks["data"]))
print(stocks["data"].head())
print(live["status"], len(live["data"]))

from brokery import store
store.save_frame("futu_codes", codes["data"], source="futu")  # 離線存放

offline = Brokery().get_code()           # 之後離線讀回 CODES：不需 OpenD、不需 IB
print(offline["status"], len(offline["data"]))
```

## 核心功能

### 1. 統一返回信封
所有方法返回同一結構，可直接自動化驗收：

```python
{"status": bool, "data": pandas.DataFrame, "message": str}
```

取不到資料時 `status=False` 並在 `message` 說明原因，不會以空表冒充「不存在」。

### 2. 統一欄位
`data` 的欄位固定：

| 欄位 | 說明 |
| --- | --- |
| `code` | 統一代碼（富途格式），如 `US.NVDA`、`HK.00700`、`US.ESmain` |
| `name` | 名稱 |
| `market` / `symbol` | 市場前綴與符號 |
| `symbol_type` | `STOCK` / `FUTURE` / `INDEX` |
| `currency` / `exchange` | 結算貨幣與掛牌交易所 |
| `expiry` | 期貨到期日（`YYYYMMDD`）；主連與非期貨為空字串 |
| `source` | 資料來源券商 |
| `raw_code` | 券商原生標識（IB 含 `conId`），供回溯核對 |

### 3. 股票清單
```python
bk.list_stocks(["HK", "US"])              # 預設港美；可傳 SH/SZ/SG/JP/MY/AU/CA
```
富途 `get_stock_basicinfo` 每個（市場, 證券類型）一次調用即返回全量，無分頁、無條件選股限頻，
港美兩市數秒完成。涵蓋類型為 `STOCK` 與 `ETF`（見 `brokers.futu_broker.STOCK_TYPES`）。

### 4. 期貨清單
```python
bk.list_futures()                          # 內建種子（ES/NQ/YM/RTY/VIX/CL/GC/SI/HG/ZN/ZS/ZW/ZC/HSI/MHI）
bk.list_futures(["ES"])                    # 指定產品
```
主連以 `main` 後綴表示；個月份的到期月放 `expiry` 欄。兩個來源的差別：

| 來源 | 取得方式 | 主連 | 個月份代碼 |
| --- | --- | --- | --- |
| FUTU | 按市場一次列舉全部期貨（實測港美 14,078 條） | `US.10Ymain`（另有 `current`/`next`/`day`） | 富途原生格式 `US.10Y2609` |
| IB | 依內建種子展開（ES/NQ/YM/RTY/VIX/CL/GC/SI/HG/ZN/ZS/ZW/ZC/HSI/MHI） | `US.ESmain`（IB `CONTFUT`，含 conId） | `US.ES` + `expiry=YYYYMMDD` |

預設兩個來源都會取，結果合併去重；只要其中一個，用 `Brokery(sources=("futu",))`。同一 IB 合約
在多處掛牌（如 CME 與 QBALGO）只保留主場。

### 5. 指數清單
```python
bk.list_indices()                          # FUTU 按市場列全（港美 740 條）+ IB 種子解析
```

### 6. 代碼轉換
```python
bk.convert("HK.00700")      # → STK|700|SEHK|HKD||152791428
bk.convert("US.ESmain")     # → CONTFUT|ES|CME|USD|20261218|515416632
bk.convert("US.ES20261218") # 個月份亦可輸入；正規化為 code=US.ES，到期月寫入 expiry
```
IB 原生合約轉回統一代碼：`brokery.brokers.ib_broker.IbBroker.to_unified_code(contract)`。

### 7. 離線存放
所有取得的資料統一經 `brokery.store` 寫入離線資料目錄（預設 `brokery/data/`，路徑讀
`.env` 的 `BROKERY_DATA_DIR`，不入版本控制）。每個資料集一檔 `<name>.parquet`，另有一份
`<name>.meta.json` 記錄行數、欄位、來源與寫入時間（UTC），方便日後判斷是否過期。

```python
from brokery import store

store.save_frame("futu_codes", df, source="futu", note="港美全量 CODES")  # 覆蓋寫入
df = store.load_frame("futu_codes")      # 未存放時拋 StoreError，不會以空表冒充「沒有」
store.load_meta("futu_codes")            # {'rows': 38568, 'saved_at': '2026-10-10T12:30:00+00:00', ...}
store.list_stored()                      # 目錄內所有已存放的資料集
```

`Brokery.get_code()` 讀回同一份資料，但走統一入口並返回標準信封（未存放時 `status=False` 並在
`message` 說明先執行邊個腳本），預設讀 `store.CODES_DATASET`（即 `futu_codes`）：

```python
bk.get_code()                            # {'status': True, 'data': 38568 條, 'message': 'ok: 離線讀回 …'}
bk.get_code("futu_codes")                # 亦可指定資料集名稱
```
離線檢視可直接跑 `python brokery/acceptance/run_get_codes.py`（可帶 `STOCK`/`FUTURE`/`INDEX`
參數只顯示某一類型），不需要任何連線。IDE 的 parquet 預覽會把字串欄位顯示成位元組數組，屬檢視器
限制，檔案內容本身正常，以 `load_frame` 讀回即為正確文字。

### 8. K 線
```python
bk.get_kline("HK.00001")                                  # 富途日線最近 60 根
bk.get_kline("HK.00001", ktype="5m", count=200)          # 日內
bk.get_kline("HK.00001", broker="ib", autype="none")     # 同一組 bar，改經 IB 取
bk.get_kline("HK.00005", broker="ib", autype="qfq")      # IB 前復權（僅日內/日線，因子與富途不同）
bk.get_kline("US.NVDA", ktype="day", count=1200)         # 超過 1000 根自動改用富途歷史接口
bk.get_kline("HK.00001", autype="hfq")                   # 後復權（只有富途支援）
Brokery(autype="none")                                   # 全域預設複權模式，逐次呼叫可再覆蓋
```
`ktype` 為 `1m/3m/5m/15m/30m/60m/day/week/month`；`count` 一律是 **bar 數**（富途語義），
`broker` 選來源，`autype` 為 `qfq`/`hfq`/`none`（見下）。`data` 的欄位固定為 `brokers.base.K_COLUMNS`：

| 欄位 | 說明 |
| --- | --- |
| `code` | 統一代碼（富途格式） |
| `ts` | bar 時間的 UTC 秒，**跨券商對齊鍵**；週/月 bar 一律歸到所屬週期起點（見 `align_ts`） |
| `time_key` | 券商原生的 bar 時間（交易所當地時間），格式統一為 `YYYY-MM-DD HH:MM:SS` |
| `open/high/low/close` | 價格 |
| `volume` | 成交量 |
| `turnover` | 成交額；IB 不提供，該欄為 `NaN` |
| `source` | 資料來源券商 |

兩家的取數方式不同，但輸出可完全對齊（實測 `HK.00001` 日線 60 根、`HK.00700` 週線 120 根、
`HK.00005` 月線 60 根、`US.NVDA` 5 分鐘 100 根均按 `ts` 一一對上；兩家同取 `autype="none"` 時
close 逐根吻合，最大相差 < 0.4%）：

| 來源 | 取數方式 | 複權 | 成交額 |
| --- | --- | --- | --- |
| FUTU | 原生就是 bar 數：≤1000 根用 `get_cur_kline`（需先訂閱同類型），更多改用 `request_history_kline` 按日期範圍分頁再截尾 | `qfq`/`hfq`/`none`（所有 ktype） | 有 |
| IB | 無 bar 數參數：由 bar 數反推時間跨度（`brokers.base.span_days`，按 365/240 放大並加假期緩衝，刻意多取）再取最後 `count` 根 | `none`（原始成交價）；`qfq` 只適用日內與日線（`ADJUSTED_LAST`） | 無（`NaN`） |
| Tiger | `get_bars` 原生就是 bar 數（`limit`）；鑑權為 RSA 簽名，需 `.env` 的 `TIGER_PRIVATE_KEY` | `qfq`（`right=BR`）/`none`；無後復權概念 | 無（`NaN`） |
| Webull | `get_batch_history_bar` 原生就是 bar 數（單次上限 1200 根，要求更多只能取到上限） | **不可選**：接口沒有復權參數，價格由週期固定（日線及以上為前復權、分鐘線為不復權），要求另一種即報錯 | 無（`NaN`） |

`ktype` 的可用範圍以適配器聲明，各家不同：Webull 沒有 `3m`（`Timespan` 無 M3），Tiger 與 Webull 只
提供 HK/US 股票。要求不支持的 `ktype` 或 `autype` 一律 `status=False` 並說明原因。

#### 複權（`autype`）
一個參數統一設定，可在 `Brokery(autype=...)` 一處設預設，或逐次在 `get_kline(autype=...)` 覆蓋。
各券商支援嘅模式由適配器以 `SymbolBroker.autypes` 聲明（富途 `qfq`/`hfq`/`none`；IB `none`/`qfq`，
而 `qfq` 不適用週/月線；Tiger `qfq`/`none`；Webull 按週期固定，見下）；**要求了不支持的模式或
ktype 即 `status=False`**，不會靜靜改用另一種價格返回：

```
autype_unsupported: ib 不支援複權 hfq（ib 只支援 none/qfq）；取原始成交價請用 autype="none"
autype_unsupported: ib 的 week 線不支持複權 qfq（IB 對多於一日的 bar 直接報 error 321「Multi day bar
size not supported with adjusted last」）；週/月線請用 autype="none"
autype_unsupported: webull 的 day K 線只返回前復權價（接口沒有復權參數）；請用 autype="qfq"
autype_unsupported: webull 的 1m K 線只返回不復權價（接口沒有復權參數）；請用 autype="none"
ktype_unsupported: 3m（可用：1m/5m/15m/30m/60m/day/week/month）
```

四家的前復權**一律可按 `ts` 逐根對齊**（`run_align_kline.py`，實測 `HK.00005` 日線 60 根四家共同 60
根），並一律以富途為準比較，不為對齊改價；數值會否一致則視市場與各家的調整因子：

- `US.NVDA` 日線 120 根：富途與 IB 調整了同一 98 根且幅度完全相同（最大 0.2281%），對照後**逐根一致**。
- `HK.00005` 日線 60 根：四家都調整了同一 19 根，但幅度差一個量級（富途最大 0.50%、Tiger 0.49%、
  IB 0.062%），與富途對照的最大相差：Tiger 0.02%、IB 與 Webull 各 0.44% —— IB 對港股派息的調整明顯
  偏小，故港股前復權不可跨券商互換。

不涉及復權的比價一律用 `Brokery(autype="none")`（原始價逐根吻合，最大 < 0.4%）；富途前復權與 IB
原始價則隨除淨日累積相差（實測月線 60 根最大相差 53%）。

#### 品種（股票／期貨／指數／期權）
品種由統一代碼推斷（`codes.classify_symbol`：帶 `main` 後綴或到期月為期貨，`US..SPX`、`HK.8xxxxx`
為指數，`AAPL261106C110000` 為期權，其餘為股票）。各來源可取 K 線的品種由適配器以
`SymbolBroker.kline_symbol_types` 聲明，未聲明的品種在發出請求前即 `status=False`，不會把期權或指數
當股票送進上游等它報錯：

```
type_unsupported: tiger 不提供 FUTURE 的 K 線（tiger 只提供 STOCK/INDEX）
type_unsupported: webull 不提供 INDEX 的 K 線（webull 只提供 STOCK）
type_unsupported: ib 不提供 OPTION 的 K 線（ib 只提供 STOCK/FUTURE/INDEX）
```

四家的實際範圍（`run_kline_matrix.py` 逐項核實）：

| 品種 | FUTU | IB | Tiger | Webull |
| --- | --- | --- | --- | --- |
| 股票 | HK/US | HK/US | HK/US | 僅 HK（美股未開通行情） |
| 期貨 | 僅 HK（`HK.A50main`）；美股期貨受賬戶行情權限限制 | 僅美股主連（`US.10Ymain`）；HKEX A50 在 IB 查無合約 | 未接入 | ❌ |
| 指數 | 僅 HK（`HK.800000`）；富途不提供美股指數 | 以指數名稱登記：美股指數去前導點即同名（`US..SPX`→`SPX`），港股只有 `IB_INDEX_ALIAS` 裏四隻登記了名稱 | 僅 US（`US..SPX`） | ❌ |
| 期權 | ✅（美股為完整序列；港股期權實測只返回當日一根） | ❌ 未實作合約對映 | ❌ | ❌ |

**復權只對股票有效**：期貨、指數與期權沒有公司行動，實測各家 `qfq` 與 `none` 逐根完全相同（0 根有
差別），傳哪一種都不影響價格；同一隻股票（`HK.00005` 日線 250 根）則有 209 根被調整。指數代碼已可
跨券商對齊：`HK.800000` 富途與 IB 共同 60 根且 close 完全相同，`US..SPX` Tiger 與 IB 同樣完全相同。

### 9. K 線串流
```python
bk.stream_kline("US.NVDA", ktype="1m", count=60, seconds=60, on_update=cb)   # 單個代碼，60 秒
bk.stream_kline(["HK.00005", "US.NVDA", "HK.HSI", "US.ES"], broker="ib",
                autype="none", seconds=0, on_update=cb)                       # 四張圖共用一條連線，直到 Ctrl-C
```
`on_update(code, rows)` 在最新一根每次變化时被回呼：`rows` 為該代碼按 `ts` 升序、不超過 `count` 根的
完整結果（未走完的 bar 亦會持續更新），回呼發生在券商的推送執行緒中，故內部不要做耗時工作。
`seconds` 為持續秒數，`0` 表示直到 Ctrl-C（按 Ctrl-C 屬正常結束）。方法返回時 `data` 為各代碼最終的
bar 合併結果，欄位與 `get_kline` 完全相同（`K_COLUMNS`）。

**多個代碼只有一條連線**：所有代碼的訂閱都掛在同一條持久連線（IB 的 `_SharedConnection`、富途的同一
`OpenQuoteContext`、Webull 的同一 `DataClient`/token）上，因此 4 圖、8 圖不會各自開連線；結束時一律
退訂，不佔用帳戶的訂閱名額。

三家（FUTU/IB/Tiger）用**原生推送**，Webull 沒有 K 線推送故以輪詢湊出相同的回呼語義：

| 來源 | 更新方式 | 支援範圍 |
| --- | --- | --- |
| FUTU | 先 `get_cur_kline` 取起點（同時完成訂閱），其後 `CurKlineHandlerBase` 收到實時 K 線推送即更新 | 全部 `ktype`；`qfq`/`hfq`/`none` |
| IB | `reqHistoricalData(keepUpToDate=True)`：同一請求先返回歷史、之後持續更新最後一根 | 全部 `ktype`；**只能 `autype="none"`** |
| Tiger | `subscribe_kline` 原生推送 | **只 `1m`**；**只能 `autype="none"`**（推送為原始成交價） |
| Webull | 沒有 K 線推送（`DataStreamingClient` 只有 quote/snapshot/tick）：先取一次批量 bar 作起點，其後每 2 秒輪詢同一接口，最新一根有變化才回呼 | **只 `1m`**；**只能 `autype="none"`**（分鐘線只返回不復權價） |

IB 的推送只能取原始成交價：`keepUpToDate` 與 `ADJUSTED_LAST` 不能同時使用（實測 error 321），故
`stream_autypes=("none",)`，要求復權時在開始前就明確返回 `status=False`：

```
autype_unsupported: ib 的 K 線串流不支援複權 qfq（ib 串流只支援 none）；串流請用 autype="none"
autype_unsupported: webull 的 K 線串流只支持 autype="none"（分鐘線只返回不復權價）
```

Webull 的輪詢按 `category` 分組，每個市場一次請求覆蓋該市場全部代碼（不是每圖一次）；間隔 2 秒
即每市場 30 次/分鐘，在其实測的港股 60 次/60 秒限額之內。

## 設計前提（實測結論，改動前請先讀）
- 股票清單只出自富途：`get_stock_basicinfo` 一次取全；IB 無「一次過列出全市場股票」的接口。
- 富途的期貨/指數批量清單（`FUTURE`/`IDX` 類型）同樣一次取全，且主連就用 `main` 後綴，與本專案
  約定一致；但其個月份為富途原生代碼（`US.10Y2609`），與 IB 的 root + 到期月無法直接對映。
- 富途 `get_stock_basicinfo` 不支援日本市場的指數（「获取静态数据接口不支持日本市场的指数」），
  後端對這類明確不支持的（市場, 類型）會跳過而非報錯。
- 向 IB 查詢時不可指定 `exchange`，指定後常回報 `No security definition found`；留空由 IB
  自行 resolve 才取得到（港股與期貨尤其明顯）。
- IB 的港股以不帶前導零的數字登記（`700`），顯示層統一補零為 `00700`。
- 富途不提供指數與期貨的 snapshot，故這類標的的統一代碼由本專案按富途格式定義。
- 種子清單只收錄實測可解析的條目；新加 root 前須確認帳戶有該市場權限（例如本帳戶無 SGX
  期貨權限，故 SGX 期貨未列入）。
- 富途 `get_cur_kline` 需先訂閱同類型 K 線，且此版本無分頁參數、單次上限 1000 根；更多 bar
  只能改經 `request_history_kline`（按日期範圍 + `page_req_key` 分頁），該接口另受帳戶歷史 K 線
  配額限制。
- 富途此版本的 `autype` 只接受小寫 `qfq`/`hfq` 與**字串** `"None"`（傳 `QFQ` 回報「autype is QFQ,
  which is not valid.」，傳 Python `None` 或 `"none"` 同樣被拒，儘管錯誤訊息寫住 `(None,qfq,hfq)`）；
  K 線 DataFrame 的成交額欄名是 `turnover`（不是 `turnover_amount`）。
- IB 的復權只有 `ADJUSTED_LAST`（無後復權對應值）：把價格調整至最近一次除淨日，方向同前復權，但
  **對週/月線直接被拒**（error 321「Multi day bar size not supported with adjusted last」）。調整因子
  各券商自行計算：美股日線 120 根與富途逐根一致，港股日線 60 根則差一個量級（富途最大 0.50%、
  IB 最大 0.062%，對照後最大相差 0.44%）。故 IB 聲明 `autypes=("none", "qfq")`，週/月線要求復權時
  由適配器明確拒绝，不靜靜返回原始價。
- IB 沒有 bar 數參數，只能給時間跨度，且跨度超過 365 日必須以「年」為單位（實測 error 321
  「durations longer than 365 days must be made in years」）；換算一律向上取整，多取的由 `tail` 截掉。
- 一年的交易日遠少於 365 日（港股實測約 244），只按周末 2/7 放大會取不足數；故一律按 365/240
  換算（見 `brokers.base.span_days`）。
- IB 的 `whatToShow="TABS"` 對股票被拒（error 321），股票與指數一律用 `TRADES`；IB 亦不返回成交額，
  該欄只能留 `NaN`。
- IB 查詢失敗時只以 `errorEvent` 回報，`reqHistoricalData` 則返回空表；不留痕便分不清是無權限還是
  參數被拒，故收集 162/300/321 錯誤碼，空表時連原因一併抛出。
- IB 對日/週/月 bar 返回的是 `datetime.date`（不是 `datetime`）。
- 非日內 bar 的錨點兩家不同：富途以週期起點（週線週一、月線每月一日）、IB 以週期終點（週線週六、
  月線下月一日）為 bar 時間，OHLC 卻完全相同。故 `ts` 一律歸到所屬週期起點（`align_ts` +
  `kline_anchor`），`time_key` 保留原生時間。
- 富途的實時 K 線推送與 `get_cur_kline` 用同一組 ktype/autype，但推送帶 `k_type` 欄，且同一連線亦會
  收到 `get_kline` 訂閱的其他 ktype，故回呼必須按 `k_type` 過濾。`CurKlineHandlerBase` 由 `futu` 頂層
  導出（定義在 `futu.quote.quote_response_handler`），自訂 handler 必須呼叫 `super().__init__()`，否則
  SDK 的 `RspHandlerBase.__del__` 會在解譯器退出時抛 `AttributeError`。
- IB 的 `keepUpToDate=True` 要求 `endDateTime=""`，返回活的 `BarDataList`：每次更新只改寫最後一根或在
  末尾追加新根，故合併只需處理末尾兩根。訂閱依附連線而存在，不退訂會一直佔用帳戶的歷史數據訂閱名額
  （實測 4 個訂閱退訂後 `reqId2Subscriber` 歸零、連線其後仍可正常取歷史）。全部 ktype 均可推送（實測
  `1 min`…`1 month` 訂閱皆存活），唯 `keepUpToDate` 與 `ADJUSTED_LAST` 不能同時使用（error 321）。
- IB 的 `barSizeSetting` 單位為一時必須用單數：實測 `1 mins` 被拒（321，錯誤訊息列出合法值
  `1 secs, …, 1 min, 2 mins, …, 1 day, 1W, 1M`），改 `1 min` 後正常；`1 week`/`1 month` 亦實測可用。
- 一段協程內含多次請求時（逐個代碼建立串流訂閱），外層兜底超時須按請求次數放宽，否則多張圖時會把
  「還在訂閱」誤報成超時。
- 休市時段各家均不會有推送（實測星期日 futu/ib 皆 0 次），故 `run_stream_kline.py` 只對回呼的規格作斷言，
  推送次數以 INFO 顯示，不計成敗。
- 各家的驗收代碼按 `MARKETS` 過濾為其憑證實際開通的市場：Webull 的 app key 註冊於 HK 區域，取美股返回
  403 `MARKET_DATA_NOT_SUBSCRIBED`（該市場未開通行情），故只以 HK 代碼驗收其串流，未驗收者打印 WARN 而
  不計失敗，免得把賬戶的行情權限問題誤當為代碼錯誤。

## 測試
```bash
python brokery/acceptance/run_futu_codes.py         # 全量 CODES：股票 + 期貨 + 指數（需 OpenD）
python brokery/acceptance/run_futu_codes_store.py   # 取 CODES → 離線存放 → 讀回核對（需 OpenD）
python brokery/acceptance/run_get_codes.py          # get_code：離線讀回已存放的 CODES，不連 OpenD
python brokery/acceptance/run_get_codes.py FUTURE   # 只顯示某一類型（STOCK/FUTURE/INDEX）
python brokery/acceptance/run_get_kline.py          # 同一 code 經 futu/ib/tiger 取 K 線並核對對齊，另核對 Webull 的取數與明確報錯（需 OpenD + IB；Tiger 需私鑰）
python brokery/acceptance/run_get_kline.py HK.00700 week 120   # 指定代碼 / ktype / bar 數
python brokery/acceptance/run_align_kline.py        # 四家的前復權以 futu 為準逐根並列，量化各家與它的偏差（需 OpenD + IB + Tiger + Webull；美股代碼會跳過 Webull 並打印 WARN）
python brokery/acceptance/run_align_kline.py US.NVDA day 120   # 指定代碼 / ktype（日內或日線）/ bar 數
python brokery/acceptance/run_stream_kline.py          # 一條連線同時串流多個代碼（futu/ib/tiger/webull），核對回呼規格與 seconds 約束（需 OpenD + IB；Tiger 需私鑰）
python brokery/acceptance/run_stream_kline.py US.NVDA 5m 50 120   # 指定代碼（逗號分隔可多個）/ ktype / bar 數 / 秒數
python brokery/acceptance/run_kline_matrix.py      # 品種 × 券商矩陣：品種推斷、能力閘（type_unsupported）、復權只對股票有效、指數跨券商對齊（需 OpenD + IB + Tiger）
```
測試以腳本方式直接執行（不使用 pytest）：執行後即輸出 `status`、`message` 與完整代碼表，
並以退出碼 `0`/`1` 表示成敗。

## 環境
- 連線參數與離線資料目錄全部讀自 `.env`（`FUTU_OPEND_HOST/PORT`、`IB_HOST/PORT/CLIENT_ID`、
  `IB_REQ_TIMEOUT`、`BROKERY_DATA_DIR`、`TIGER_ID/ACCOUNT/TOKEN/PUBLIC_KEY/PRIVATE_KEY`、
  `WEBULL_APP_KEY/APP_SECRET`、`WEBULL_REGION_ID`、`WEBULL_TOKEN_DIR`）。
- Tiger 的鑑權為 RSA 簽名，**必須有 `TIGER_PRIVATE_KEY`**；缺少時 `get_kline` 明確返回
  `not_configured`。該私鑰只在 developer.itigerup.com/profile **生成密鑰對的當下顯示一次**，服務端不
  保存、刷新即消失，故無法事後取回（實測：「您的Token」的「下載」導出 `tiger_openapi_token.properties`，
  內裡只有 `token=` 一行，不含私鑰）；遺失只能在「您的RSA KEY」下**重新生成**一對，並同時更新 `.env`
  的 `TIGER_PUBLIC_KEY` 與 `TIGER_PRIVATE_KEY`。格式為單行 base64（PKCS#1 或 PKCS#8 皆可，帶 PEM 頭尾亦會自動去除）。
  `TIGER_TOKEN`（有效期 30 日）只作 `Authorization` 頭，**不能取代私鑰**：實測以未在平台登記的私鑰簽名，
  伺服器即返回 `code=1000 failed to verify signature`。
- `.env` 的 `TIGER_PUBLIC_KEY` 只是平台頁面顯示的公鑰，**不可用作配對核對**：實測目前可用的私鑰與它的
  modulus 並不相同（即非同一密鑰對），但伺服器接受該私鑰、取數正常，故判據只有實跑。它也**不會**餵給
  SDK 的 `config.tiger_public_key`——該字段是「老虎自己的公鑰」（用於驗證返回簽名，SDK 自帶生產環境
  預設值），餵成帳戶公鑰會令驗簽失敗。
- Webull 只有 **LIVE** 憑證可用：SDK 沒有模擬環境的 host，實測 `WEBULL_SIM_APP_KEY` 在全部區域
  host 均返回 401，故 SIM 金鑰只存放、不使用。首次取數需在 Webull App 中批准 API 授權請求，
  批准後的 token 存放在 `WEBULL_TOKEN_DIR`，之後直接沿用（換 token 目錄即需重新批准）。
- Webull 的 app key **綁定註冊區域**：實測 HK 的金鑰改用 `WEBULL_REGION_ID=us` 即 401。行情亦按市場
  開通，實測取美股返回 403 `MARKET_DATA_NOT_SUBSCRIBED`，故現況只可取 HK；未開通的市場明確報錯，
  不會靜靜返回空表。
- 需同時運行於 Windows、Ubuntu 與 Docker；路徑一律用 `pathlib`。
- 安裝：`pip install -r requirements.txt`。
