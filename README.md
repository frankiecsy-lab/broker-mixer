# brokery

跨券商標的與行情統一層。以富途代碼格式為唯一對外格式（`US.NVDA`、`HK.00700`、`US.ESmain`），
把不同券商的原生代碼與能力差異藏在內部。**四家（FUTU 富途、IB、Tiger 老虎、Webull）都提供標的
清單與 K 線**，但每個品種是否可得一律按各家能力聲明（見下表；未聲明者由 `core` 明確返回
`no_source`，不以空表冒充）。代碼轉換只支援 **IB**。同級的 `brokery_api/` 再把以上全部能力以
FastAPI 對外為 HTTP/WebSocket 與一個 dashboard（見 §11）；`brokery_webui/` 則是一個只負責頁面與轉發的
量化交易 Web UI（見 §12）；`brokery_gui/` 是同一功能的 PySide6 桌面 GUI，界面以 `.ui` 分離、支援三種語言即時
切換（見 §13）。

## 當前狀態

| 功能 | 狀態 | 資料來源 |
| --- | --- | --- |
| 全量代碼清單 `list_all`（股票 + 期貨 + 指數） | ✅ 可用 | FUTU（港美兩市實測 38,568 條）+ Tiger + Webull（合併去重） |
| 股票清單（含 ETF） | ✅ 可用 | FUTU（一次取全）+ Tiger（實測 HK 3,763／US 14,609）+ Webull（分頁，實測 HK 3,170／US 12,306）；**IB 不提供**（無「一次列出全市場股票」的接口，未聲明即返回 `no_source`） |
| 期貨清單（主連 + 所有到期月） | ✅ 可用 | FUTU + IB + Tiger（原生全量，實測 649 條，含種子外的 MEUR/ZM 等）+ Webull（按種子展開，實測 41 條、只掛近月；種子中無提供者如 VIX 如實留空） |
| 指數清單 | ✅ 可用 | FUTU（按市場列全，港美 740 條）+ IB（種子解析）+ Tiger（符號表內的 4 隻美股指數）；**Webull 不提供**（無指數類別） |
| 標的清單的統一輸出（四家同一欄位契約、未聲明品種明確拒绝） | ✅ 可用 | 四家逐家 × 逐品種實測（`run_list_symbols.py`）：欄位與順序一律為 `COLUMNS`、字串欄無 NaN、`code` 一律 `<市場>.<符號>`、未聲明者返回 `no_source`。`broker=` 只向一家取（未啟用即 `unknown_source`、該家不提供即 `type_unsupported`，不靜默改用別家）、`markets=` 過濾返回的市場（`run_list_filter.py` 10 項全過，不需連線） |
| 代碼雙向轉換（統一代碼 ↔ IB 原生合約） | ✅ 可用 | IB |
| 離線存放與讀回（parquet + meta） | ✅ 可用 | 本地 `brokery/data/`（由 `.env` 指定） |
| 離線讀取代碼清單 `get_code` | ✅ 可用 | 本地 parquet，不需要 OpenD / IB |
| K 線 `get_kline`（統一格式、以 bar 數取數） | ✅ 可用 | FUTU + IB（日/週/月線實測逐根按 `ts` 對齊，價格一致）+ Webull（日線/分鐘線實測，日線確實做了前復權，調整因子與 IB 一致：與原始成交價最大相差 0.062%）+ Tiger（日線/1 分鐘線實測，`autype="none"` 時 close 與 FUTU 逐根完全一致） |
| 前復權跨券商對照（日內與日線） | ✅ 可用 | FUTU `qfq` + IB `ADJUSTED_LAST` + Tiger `right=BR` + Webull（日線固定前復權）：`HK.00005` 日線 60 根四家共同 60 根逐根對齊，以富途為準 Tiger 最大相差 0.02%、IB/Webull 0.44% |
| 品種支持矩陣（股票／期貨／指數／期權）與復權適用範圍 | ✅ 已核實 | 四家實測（`run_kline_matrix.py`，31 項檢查）：不支持的品種由適配器聲明、`core` 統一返回 `type_unsupported`；復權只對股票有效（期貨／指數／期權的 `qfq` 與 `none` 逐根完全相同）；指數代碼可跨券商（`HK.800000` 富途與 IB 的 close 完全相同、`US..SPX` Tiger 與 IB 完全相同） |
| 戶口與資金 `get_accounts`（四家統一 15 欄） | ✅ 可用 | FUTU + IB + Tiger + Webull（實測 futu 2 個（cash/margin，模擬與已停用的不列）、IB 1 個、Tiger 1 個、Webull 2 個；`currency` 全部填到：futu/IB/Webull 為 HKD、Tiger 為 USD；IB 的 `individual` 在按 `cash`/`margin` 篩選時點名說明而不靜默丟列；39 項檢查全過） |
| 券商連線狀態與速度 `get_brokers`（統一 6 欄） | ✅ 可用 | FUTU + IB + Tiger + Webull 四家並行探測實測（futu 178ms／ib 542ms／tiger 1216ms／webull 954ms，總耗時 1.2s ≈ 最慢一家）；探測用一次戶口查詢，故不需要行情權限；22 項檢查全過 |
| HTTP/WS 閘道與 dashboard `brokery_api`（自訂 API Key、K 線圖、實時訂閱、戶口（四家同屏、10 秒自動刷新）、標的（按來源分四區；離線 CODES 以單一表格顯示）、日誌窗、四家連線狀態與延遲、讀取提示） | ✅ 可用 | 四家經同一閘道實測（`/kline`、`/accounts`、`/brokers`、各清單與 `/stream` 均連通）；`run_api.py` 40 項檢查全過（不需券商連線）；`run_ui.py` 29 項客戶端檢查全過（存根閘道 + Chromium：含戶口頁自動刷新與不分來源、按來源汇总並點名無返回者、標的頁一次點擊四區同時返回並區分「N 條／無返回／不提供此清單」、請求進行時的讀取提示、標的頁不再有「統一格式輸出」面板（即時清單只按來源分區）、離線 CODES 不分區而以單一表格顯示且欄位順序即接口原樣） |
| 量化交易 Web UI `brokery_webui`（上方菜單兩項：「戶口清單」四家戶口與資金同屏；「標的列表」上方為類型／市場／券商篩選、下方為取得的清單，默認富途） | ✅ 可用 | 資料經同一閘道取得（實測 `http://127.0.0.1:8282` 顯示 6 個戶口：futu 2／ib 1／tiger 1／webull 2，15 欄與 `ACCOUNT_COLUMNS` 逐欄一致、缺失值為破折號）；券商選項由能力聲明填充、不提供該品種者標註且不可選，市場選項只由實際返回的 `market` 填充；`run_webui.py` 30 項檢查全過（存根閘道 + Chromium，不需券商連線） |
| 量化交易桌面 GUI `brokery_gui`（PySide6：兩個分頁同 Web UI——「戶口清單」與「標的列表」；界面以 `.ui` 檔分離且檔內不含任何文字；繁體中文／简体中文／English 即時切換，每個語言一個 `.json`） | ✅ 可用 | 與 Web UI 同一閘道、同一口徑（表格欄位由返回的 `columns` 決定、缺失值為破折號、資金欄千分位、券商選項由能力聲明填充且不提供該品種者標註並不可選、市場選項只由實際返回的 `market` 填充）；取數在背景執行緒，界面不因券商連線而凍結；`run_gui.py` 29 項檢查全過（存根閘道 + Qt 離屏，不需券商連線亦不需顯示器） |
| 一次過啟動閘道與 Web UI `run_all.py`（其中一個先結束即停止另一個，Ctrl+C 一併停止） | ✅ 可用 | 實測 `python run_all.py`：兩個端口同時回應、Web UI 可經剛啟動的閘道取數、送 Ctrl+C 後兩個一併退出且端口釋放；`run_launch.py` 7 項檢查全過（存根命令，不需券商連線，亦不真的啟動服務） |
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

    accounts = bk.get_accounts()                   # 四家的戶口與資金，欄位完全相同
    accounts = bk.get_accounts(broker="futu", acc_type="margin", currency="HKD")

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

要經 HTTP 取數或直接睇 dashboard，起同級的閘道：

```bash
python run_all.py             # 一次過起閘道 + Web UI（端口見 .env）：其中一個先結束即停止另一個，Ctrl+C 一併停止
python brokery_api/run.py     # 只起閘道 http://127.0.0.1:8181；金鑰讀自 .env 的 API_KEY
python brokery_webui/run.py   # 只起量化交易 Web UI：http://127.0.0.1:8282（要先起閘道，Web UI 只轉發不連券商）
python brokery_gui/run.py     # 只起量化交易桌面 GUI（PySide6 窗口；同樣要先起閘道，地址與金鑰讀自 .env）
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
bk.list_stocks(["HK"], broker="futu")     # 只向富途取；未啟用即 unknown_source，該家不提供即 type_unsupported
```
四家中三家提供，取得方式與如實保留的原生差異：

| 來源 | 取得方式 | 實測與原生差異 |
| --- | --- | --- |
| FUTU | `get_stock_basicinfo` 按（市場, 證券類型）一次取全，無分頁、無選股限頻 | 港美兩市數秒完成；涵蓋 `STOCK` 與 `ETF`（見 `brokers.futu_broker.STOCK_TYPES`） |
| Tiger | `get_symbol_names` 按市場一次取全 | HK 3,763／US 14,609；接口不附帶掛牌場所（`get_stock_details` 本戶口 `permission denied`），`exchange` 一律空字串 |
| Webull | `list_instruments` 按 `category` + `sub_category` 分頁（每頁 1000，只取 `status=OC`，故隔走認股證與 CBBC） | HK 3,170／US 12,306；`exchange` 為 Webull 自有的場所代號（HKG／XGEM／NAS／NSQ／NMS…），各券商對同一場所的寫法本來不同，不憑空歸一；原生 `instrument_id` 留在 `raw_code` |
| IB | **不提供**：無「一次列出全市場股票」的接口（空 symbol 的 `reqContractDetails` 150s 無回應、`reqMatchingSymbols` 只為 top-N 且混入 BOND、`reqScannerData` error 162） | 能力未聲明，`core` 返回 `no_source: 已啟用的券商（ib）不提供股票清單`，UI 顯示「不提供此清單」 |

### 4. 期貨清單
```python
bk.list_futures()                          # 內建種子（ES/NQ/YM/RTY/VIX/CL/GC/SI/HG/ZN/ZS/ZW/ZC/HSI/MHI）
bk.list_futures(["ES"])                    # 指定產品
bk.list_futures(["ES"], markets=("US",))   # 期貨接口沒有市場參數：markets 按返回行的 market 過濾
```
主連以 `main` 後綴表示；個月份的到期月放 `expiry` 欄。四家全部提供，但取得方式與到期月的寫法不同：

| 來源 | 取得方式 | 主連 | 個月份代碼 |
| --- | --- | --- | --- |
| FUTU | 按市場一次列舉全部期貨（實測港美 14,078 條） | `US.10Ymain`（另有 `current`/`next`/`day`） | 富途原生格式 `US.10Y2609`，`expiry` 為富途原生的最後交易日 `YYYYMMDD` |
| IB | 依內建種子展開（ES/NQ/YM/RTY/VIX/CL/GC/SI/HG/ZN/ZS/ZW/ZC/HSI/MHI） | `US.ESmain`（IB `CONTFUT`，含 conId） | `US.ES` + `expiry=YYYYMMDD` |
| Tiger | 原生批量：`get_future_exchanges` + `get_future_contracts`，不需種子（實測 649 條，含種子外的 MEUR／ZM／XW 等；`trade=False` 者不列） | `US.ESmain` | `US.ES` + `expiry=YYYYMM` |
| Webull | 無批量接口：按種子 root 逐個 `get_futures_instrument(code=root)` 展開（實測 41 條／14 個 root） | 無主連概念，不憑空補 `main` 行 | `US.ES` + `expiry=YYYYMM`；只掛近月（實測美股每個 root 只有最近兩個月）；種子中無提供者（實測 VIX）返回空，不憑空補出 |

預設四家都會取，結果合併去重；只要其中一家，用 `Brokery(sources=("futu",))`。以 root 表達合約的
三家（IB／Tiger／Webull）同一 `code` 會跨多個到期月，故期貨行的唯一鍵為 `code` + `expiry`。去重
（鍵為 market + symbol_type + symbol + expiry）後某家可能不再出現：其提供的合約若全部已被別家
覆蓋，即只保留一份（實測 Webull 的 ES 兩個月與 Tiger 逐欄相同，`message` 仍為 `ok`）；同一合約
在多處掛牌（如 CME 與 QBALGO）只保留主場。

### 5. 指數清單
```python
bk.list_indices()                          # FUTU 按市場列全 + IB 種子解析 + Tiger 符號表
bk.list_indices(["SPX"])                   # 指定符號
bk.list_indices(markets=("HK",))           # 只保留港股；全部不在指定市場即 empty_list，不以空表冒充
```
三個方法一律接受 `broker=`（只向一家取，能力閘由適配器聲明、`core` 統一拒绝，不會靜默改用別家湊數）與
`markets=`（過濾返回行的 `market`；股票清單的市場由適配器自己處理，這一層只確保返回的確實是所請求的市場）。
| 來源 | 取得方式 | 實測 |
| --- | --- | --- |
| FUTU | 按市場一次列舉 `IDX` 類型 | 港美 740 條 |
| IB | 依內建種子（HSI/HSTECH/VHSI/SPX/NDX/VIX/N225）解析 | 只返回可解析者 |
| Tiger | 符號表中以句點前綴登記的指數（`US..SPX`、`US..DJI`、`US..IXIC`） | 4 隻美股指數；不把種子外的句點符號當指數 |
| Webull | **不提供**：接口沒有指數類別 | 返回 `no_source: 已啟用的券商（webull）不提供指數清單` |

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

### 10. 戶口與資金
```python
bk.get_accounts()                                  # 四家全部戶口，欄位完全相同
bk.get_accounts(broker="futu", acc_type="margin")  # 只取富途的保證金戶口
bk.get_accounts(broker="ib", currency="USD")       # 只取以美元結算的金額
```
一律只返回**真實且已啟用**的戶口，不區分 real/simulate：IB 的真實與模擬由所連 Gateway/TWS 決定，
接口本身沒有這個維度；富途與 Tiger 的模擬戶口、富途的已停用（`INACTIVE`/`DISABLED`）戶口因此不列入。
`data` 的欄位固定為 `brokers.base.ACCOUNT_COLUMNS`：

| 欄位 | 說明 |
| --- | --- |
| `source` / `account_id` | 來源券商與券商的戶口標識 |
| `acc_type` | 戶口性質 `cash` / `margin`；券商表明瞭才歸類，無法判定的原樣返回（如 IB 個人戶口的 `individual`） |
| `status` | 券商回報的戶口狀態；Webull 與 IB 無此欄位，為空字串 |
| `currency` | 該行金額的計價幣種（一律不換算） |
| `net_liquidation` … `realized_pnl` | 資金與保證金各欄；該券商沒有者為 `NaN`，不以任何數字湊出 |

`acc_type` 只可傳 `all`/`cash`/`margin`，各券商能表明哪一種由適配器以 `SymbolBroker.acc_types` 聲明，
要求了不支持的值即 `status=False`（`acc_type_unsupported:`），不會憑空造出戶口。原樣透傳、不在該詞表內的
性質（如 IB 的 `individual`）只在不過濾時列回；按 `cash`/`margin` 篩選時一律在 `message` 點名該戶口
（`acc_type_other:`），不會令該券商在結果中無故消失而無從得知原因。`currency` 只作篩選：
與該戶口的計價幣種不符即不返回該戶口。`broker` 省略時查全部已啟用的券商，個別券商失敗仍返回已取得的
戶口並在 `message` 逐項說明（`ok（…，部分券商未完成）`）；全部失敗才是 `no_account:`。

四家的取數方式不同，但輸出可完全相同（實測 futu 2 個、IB 1 個、Tiger 1 個、Webull 2 個）：

| 來源 | 戶口與性質 | 資金 | 幣種 |
| --- | --- | --- | --- |
| FUTU | `get_acc_list`（只 `trd_env=REAL` 且 `acc_status=ACTIVE`）；性質為 `acc_type`（CASH/MARGIN） | `accinfo_query`（必須傳幣種） | 未指定時取該戶口首個可映射結算幣的授權市場 |
| IB | `accountSummary`（group `All`）；性質由 `AccountType` tag 映射（`C`→cash、`M`/`LIMITED_MARGIN`→margin） | 同一請求的 `NetLiquidation`/`TotalCashValue` 等 tag | 每個金額自帶結算幣，多幣種按幣種各列一欄 |
| Tiger | `get_managed_accounts`（只 `account_type=STANDARD`，即非 PAPER）；性質由 `capability`（RegTMargin/BasicCash）表明 | `get_assets`（無幣種參數） | 帳戶結算幣；不符即不返回該戶口 |
| Webull | `get_account_list`（只有真實戶口，無需過濾）；性質為 `account_type`（實測 `MRGN`） | `get_account_balance` | 匯總幣種；指定時改讀 `account_currency_assets` 中該幣種的明細 |

### 10.1 連線狀態與速度（`get_brokers`）
```python
bk.get_brokers()              # 四個券商並行探測
bk.get_brokers(broker="ib")   # 只探一家
```
`data` 的欄位固定為 `brokers.base.BROKER_COLUMNS`：

| 欄位 | 說明 |
| --- | --- |
| `source` | 券商 |
| `connected` | 該次探測成敗 |
| `latency_ms` | 探測往返毫秒數；連不上為 `NaN`（不以任何數字湊出） |
| `accounts` | 該次讀到的戶口數 |
| `detail` | 失敗原因；成功為空字串 |
| `checked_at` | 探測完成的 UTC 秒 |

探測用一次戶口查詢：只需連線與鑑權，**不需要行情數據權限**，因此行情權限缺失、休市或某市場沒有
歷史數據時不會被誤報為連線斷開（實測 IB 港股歷史數據失靈期間，IB 連線仍探測為 542ms）。四家並行，
總耗時接近最慢一家而非各家相加；超過 `.env` 的請求超時仍未返回者記為 `timeout`，不會無限等待。
無快取，也不應定時輪詢（每次探測都會真的發一次請求）。

### 11. HTTP/WS 閘道與控制台（`brokery_api`）
與 `brokery/` 同級，只經 `Brokery` 的公開接口把功能映射為 HTTP/WebSocket，並附一個完整 dashboard
（K 線圖 + 實時訂閱、戶口資金、標的清單、日誌窗、頂欄四家連線狀態與延遲）。

```bash
python brokery_api/run.py     # 監聽 .env 的 API_HOST/PORT，開瀏覽器即得 dashboard
```

| 端點 | 對應 |
| --- | --- |
| `GET /` | dashboard 頁面（不需金鑰，頁面本身不含資料） |
| `GET /health` | 進程與配置概覽（不需金鑰，供探活） |
| `GET /capabilities` | 欄位契約、ktype 清單、各券商能力聲明 |
| `GET /logs?limit=` | 最近日誌（記憶體環形緩衝，新到舊） |
| `GET /codes` | `get_code`（離線讀回） |
| `GET /stocks?markets=`、`/futures?roots=`、`/indices?symbols=`、`/all?markets=` | 各標的清單 |
| `GET /convert?code=&source=` | `convert` |
| `GET /kline?code=&ktype=&count=&broker=&autype=` | `get_kline` |
| `GET /accounts?broker=&acc_type=&currency=` | `get_accounts` |
| `GET /brokers?broker=` | `get_brokers`（各券商連線狀態與延遲） |
| `WS /stream` | `stream_kline`（協定見下） |

- **鑑權**：金鑰自訂（`.env` 的 `API_KEY`，未設即拒絕啟動並明確報錯）。HTTP 受理 `X-API-Key`
  或 `Authorization: Bearer` 其一（缺少 401、不符 403）；WebSocket 因瀏覽器不能自訂握手標頭，另受理
  `?api_key=`（不符即以 code 4403 關閉）。
- **返回**：一律 HTTP 200，`{"status":bool,"data":{"columns":[…],"rows":[[…]]},"message":str}`，`data`
  即 DataFrame 的欄位與行；缺失值一律為 `null`（不出現非法的 `NaN`）。業務失敗（`unknown_source:`、
  `no_account:` 等）由 `status=False` 表達，原因原樣透傳，不變成 HTTP 500。
- **串流**：送 `{"action":"subscribe","codes":[…],"ktype":…,"count":…,"broker":…,"autype":…}`，
  收 `subscribed` → 每次推送為 `update`（附該代碼目前**完整**的序列，客戶端整份覆蓋，不做本地合併）
  → 到時結束為 `end`；送 `{"action":"stop"}` 即 `closed`（附還差多少秒才釋放名額）。同一券商同時只
  容許一條串流（富途的推送回調按連線設置，兩條會互相覆蓋），第二條即 `stream_busy:`；失敗或結束時
  名額即時歸還。歷史起點由 `/kline` 取，`/stream` 只推更新。ktype、複權與品種是否支持一律由 Brokery
  判定，閘道不另設規則。
- **日誌**：每個請求與每個業務結果一律寫入控制台、`logs/brokery_api.log`（滾動檔）與記憶體環形
  緩衝（由 `/logs` 讀）；自訂金鑰一律遮罩，不會落入日誌檔。
- **連線狀態**：dashboard 頂欄以四家券商的指示（可連／斷開 + 延遲毫秒，懸停顯示原因與戶口數）顯示，
  由 `/brokers` 於頁面載入時探測一次，其後只由「探測連線」按鈕手動觸發（探測會真的向各家發請求，
  故不設定時輪詢）。
- **戶口頁**：沒有「來源」選擇，一律一次取四家全部戶口（請求不带 `broker` 參數）。進入該頁即取一次，
  其後每 10 秒自動刷新（只在該頁可見時才請求，可勾選關閉；「取得戶口」手動刷新照樣可用）。頁頂按
  來源列出各券商的戶口數，沒有返回者點名，避免用戶只見到「少咗一間」而不知原因。
- **標的頁**：即時清單（股票／期貨／指數／全部）按來源分四區同時顯示 —— 一次點擊即四區一起填充
  （後端本来就是一次向各家取齊，不需逐間點），區內不再重複 `source` 欄。每區如實顯示該家狀態：
  「N 條」／「無返回」（理應有份却取不到，如未連線或無行情權限）／「不提供此清單」（該券商本就不提供
  該清單，如 IB 無股票清單、Webull 無指數清單，依 `/capabilities` 的能力聲明判定）——三者含義不同，
  不可混為一談。個別券商失敗時 `message` 以警告色顯示，結果仍算成功。各區欄位一律為
  `brokers.base.COLUMNS`（10 欄，順序即接口原樣，只去掉區內重複的 `source` 欄）。
- **離線 CODES**：存放好的快照不涉及即時取數，故不分區，以單一表格顯示（`source` 保留在欄位中）。
- **讀取提示**：所有取數（K 線、戶口、標的、日誌、探測）在請求進行時明確顯示「讀取中…」並以強調色
  標示，同時禁用觸發按鈕防止重復送出；較快的請求（如日誌）會延後約 0.4 秒才顯示，避免閃爍。
- **金鑰記憶**：dashboard 填入的金鑰即時存入瀏覽器 `localStorage`（鍵 `gw_key`），重新載入或重開頁面
  自動回填，其後所有請求（含 WS 訂閱）自動帶上，不需每次重填。

### 12. 量化交易 Web UI（`brokery_webui`）
與 `brokery/`、`brokery_api/` 同級的獨立進程：上方為菜單兩項——「戶口清單」（四家的戶口與資金同屏）
與「標的列表」（上方為類型／市場／券商篩選，下方為取得的清單，默認富途）。

```bash
python brokery_webui/run.py   # 監聽 .env 的 GUI_HOST/GUI_PORT；需先啟動 brokery_api 閘道
```

- **只負責頁面與轉發，不連券商**：`/api/accounts`、`/api/capabilities` 與 `/api/symbols` 以 `X-API-Key`
  轉發閘道的對應接口，信封原樣透傳（`/api/symbols` 按類型轉到 `/stocks`／`/futures`／`/indices`，市場與
  券商原樣傳為 `markets`／`broker`，類型不認識即 `unknown_kind`）。理由在進程層面：閘道已持有各券商連線，IB 更只容許一個 client id，Web UI 再建一份即互相搶佔，
  兩邊都取不到數。金鑰只在 Web UI 服務端使用，不出現在頁面或瀏覽器中。
- **失敗口徑與閘道一致**：閘道不可達、金鑰不符或返回非信封內容，一律由 Web UI 構造
  `{"status": false, …}` 並在 `message` 點名原因（`gateway_unreachable:`／`gateway_http_403:`），
  不變成 HTTP 500，客戶端只需看一個欄位。未設 `API_KEY` 時在啟動時即拒绝建立應用。
- **表格即契約**：欄位與順序一律為接口返回的 `ACCOUNT_COLUMNS`，不另設欄位；缺失值顯示破折號（不湊
  數）、資金欄為千分位兩位小數、頁頂按來源統計戶口數（只統計實際返回者，不會憑空列出一間「0 個戶
  口」）；`message` 帶「注意」（個別券商失敗）時以警告色顯示，結果仍算成功。
- **標的列表**：類型（股票／期貨／指數）、市場、券商三個篩選在上方，清單在下方，欄位即 `COLUMNS`。券商
  選項由 `/api/capabilities` 的能力聲明填充（默認 futu；不提供該品種者標註原因且不可選，不必按了才知道會
  `type_unsupported`），市場選項只由實際返回行的 `market` 填充，頁面不硬寫券商或市場名單；真正的能力閘在
  `core`，Web UI 不會靜靜改用別家湊數。轉類型時市場重設為全部，選項再由新品种返回的資料重建。
- **日誌**：與閘道同一套（級別與目錄由 `API_LOG_LEVEL`/`API_LOG_DIR` 決定），但寫自己的
  `logs/brokery_webui.log`：兩個進程共用同一個滾動檔會在滾動時互相搶佔句柄。

### 13. 量化交易桌面 GUI（`brokery_gui`）

與 Web UI 同一功能的桌面窗口（PySide6）：兩個分頁——「戶口清單」與「標的列表」（類型／市場／券商篩選在上、
清單在下，默認富途）。

```bash
python brokery_gui/run.py     # 閘道地址與金鑰讀自 .env 的 API_HOST/API_PORT/API_KEY；需先啟動閘道
```

- **界面與文字分離**：三個 `.ui` 檔（`ui/main_window.ui`、`ui/accounts_page.ui`、`ui/symbols_page.ui`）在運行時由
  QUiLoader 載入，檔內不含任何文字；顯示文字一律按鍵取自 `locales/<語言>.json`。
- **三種語言即時切換**：繁體中文／简体中文／English 各一個 `.json`（三者鍵集合一致），頂欄切換即重貼標籤，不需
  重建窗口、亦不重新取數；缺譯時返回鍵名本身，不憑空造一句湊數。
- **取數只經閘道**：與 Web UI 同一理由（閘道已持有各券商連線，IB 只容許一個 client id）。請求在背景執行緒進行，
  界面不會因券商連線（IB 可達 40s）而凍結；失敗口徑與閘道一致（`gateway_unreachable:`／`gateway_http_403:` 原樣
  顯示，狀態列同時標為「取數失敗」），未設 `API_KEY` 即在啟動時拒绝建立客戶端。
- **表格即契約**：欄位與順序一律由返回的 `columns` 決定（即 `ACCOUNT_COLUMNS`／`COLUMNS`），不另設欄位；缺失值
  顯示破折號、資金欄為千分位兩位小數、按來源統計條數（只統計實際返回者）；券商選項由 `/capabilities` 的能力聲明
  填充（默認 futu，不提供該品種者標註原因且不可選），市場選項只由實際返回行的 `market` 填充，轉類型即重設為全部。

### 14. 一次過啟動閘道與 Web UI（`run_all.py`）

```bash
python run_all.py             # 兩個一齊起；只想起一個仍用上面兩個入口
```

- 兩個仍是各自獨立的進程，本檔只負責啟動與收尾：其中一個先結束（例如未設 `API_KEY`、或端口已被佔用）
  即停止另一個並原樣返回其退出碼，不會留半個系統在背景；Ctrl+C 一併停止，收尾有 10 秒上限，不無限等待。
- 本檔刻意不 import `brokery`：futu SDK 在匯入時即接管 SIGINT（自備的 `quit_handler` 直接結束進程），
  接管後 Ctrl+C 不會走到收尾，兩個子進程會變成孤兒。`run_launch.py` 有一項檢查專為守住這個前提。

## 設計前提（實測結論，改動前請先讀）
- 股票清單出自富途、Tiger 與 Webull（富途 `get_stock_basicinfo` 一次取全、Tiger `get_symbol_names`
  按市場一次取全、Webull `list_instruments` 分頁）；IB 無「一次過列出全市場股票」的接口，故不聲明
  `STOCK` 能力、由 `core` 統一返回 `no_source`，不為湊齊四家而改用 top-N 樣本（實測
  `reqMatchingSymbols` 混入 BOND）。
- 各券商對同一掛牌場所的寫法本來不同（Webull 以 HKG／XGEM／NAS／NSQ／NMS 登記，富途以 HKEX／NASDAQ
  登記），一律原樣返回、不憑空歸一；需要回溯時讀 `raw_code`。期貨的場所則已歸一到 `codes` 詞表
  （Webull 的 XCME／XCBT／XCEC／XNYM／HFE → CME／CBOT／COMEX／NYMEX／HKFE），否則 `market_of()`
  無法判定市場。
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

- IB 的 `accountSummary` 只能用 group `"All"`：實測 `"Individual"` 完全不返回資料，亦不會送
  `accountSummaryEnd`，即會一直等到超時。ib_async 內建的 tag 清單不含 `Currency`/`UnrealizedPnL`/
  `RealizedPnL`，故自組清單（`IB_ACCOUNT_TAGS`）；本帳戶的 `Currency` tag 仍被後端略過（不報錯），
  幣種附在每個金額的 `currency` 欄上，故按（戶口, 幣種）分組取幣種。`AccountType` 對個人戶口返回
  `INDIVIDUAL`，未表明現金或保證金，故原樣返回 `individual`，不憑空歸類。
- 富途 `get_acc_list` 的 `trdmarket_auth` 是 **list**（不是字符串），按字符串拆分會連引號一起拆出來而
  全部映射失敗；`accinfo_query` 必須傳幣種，且返回的數字只屬該幣種（另有各幣種明細欄），故未指定幣種時
  取首個可映射結算幣的授權市場，同一戶口只列一欄。已停用的戶口（實測值為 `DISABLED`）取不到資金。
- Tiger 的 `get_assets` 沒有幣種參數（實測傳 `base_currency` 被拒），只按帳戶結算幣返回；`inf` 表示該
  幣種無此項（實測空戶口的保證金要求為 `inf`），一律還原為 `NaN`。
- Webull 的 `get_account_balance` 同時返回各幣種明細（`account_currency_assets`），故指定幣種時改讀該
  明細；它沒有淨資產與可用資金欄位（只有可提現金額，語義不同），該兩欄為 `NaN`。

## 測試
```bash
python brokery/acceptance/run_futu_codes.py         # 全量 CODES：股票 + 期貨 + 指數（需 OpenD）
python brokery/acceptance/run_futu_codes_store.py   # 取 CODES → 離線存放 → 讀回核對（需 OpenD）
python brokery/acceptance/run_get_codes.py          # get_code：離線讀回已存放的 CODES，不連 OpenD
python brokery/acceptance/run_get_codes.py FUTURE   # 只顯示某一類型（STOCK/FUTURE/INDEX）
python brokery/acceptance/run_list_symbols.py      # 四家 × 三品種的標的清單：能力聲明與實測一致、欄位與順序一律為 COLUMNS、字串欄無 NaN、code 為統一代碼、未聲明品種返回 no_source、跨券商合併不重複列（需 OpenD + IB + Tiger + Webull）
python brokery/acceptance/run_list_filter.py       # 清單的 broker 與 markets 兩個參數（core 調度口徑）：只向一家取、unknown_source／type_unsupported、markets 按行過濾、empty_list、省略 markets 用預設市場、一家失敗仍返回別家資料（以存根券商進行，不需任何連線）
python brokery/acceptance/run_get_kline.py          # 同一 code 經 futu/ib/tiger 取 K 線並核對對齊，另核對 Webull 的取數與明確報錯（需 OpenD + IB；Tiger 需私鑰）
python brokery/acceptance/run_get_kline.py HK.00700 week 120   # 指定代碼 / ktype / bar 數
python brokery/acceptance/run_align_kline.py        # 四家的前復權以 futu 為準逐根並列，量化各家與它的偏差（需 OpenD + IB + Tiger + Webull；美股代碼會跳過 Webull 並打印 WARN）
python brokery/acceptance/run_align_kline.py US.NVDA day 120   # 指定代碼 / ktype（日內或日線）/ bar 數
python brokery/acceptance/run_stream_kline.py          # 一條連線同時串流多個代碼（futu/ib/tiger/webull），核對回呼規格與 seconds 約束（需 OpenD + IB；Tiger 需私鑰）
python brokery/acceptance/run_stream_kline.py US.NVDA 5m 50 120   # 指定代碼（逗號分隔可多個）/ ktype / bar 數 / 秒數
python brokery/acceptance/run_kline_matrix.py      # 品種 × 券商矩陣：品種推斷、能力閘（type_unsupported）、復權只對股票有效、指數跨券商對齊（需 OpenD + IB + Tiger）
python brokery/acceptance/run_get_accounts.py      # 四家戶口與資金：統一欄位、只列真實且已啟用的戶口、幣種有無填到、acc_type/currency/broker 三個參數的邊界、詞表外的戶口性質（IB individual）在篩選時點名說明（需 OpenD + IB + Tiger + Webull）
python brokery/acceptance/run_get_brokers.py   # 四家連線狀態與延遲：統一欄位、延遲為正數且戶口數與 get_accounts 一致、連不上為 NaN 並附原因、並行探測、參數邊界（需四家後端在線）
python brokery/acceptance/run_api.py           # 閘道本身：未設金鑰拒絕啟動、HTTP/WS 鑑權、返回信封與欄位契約、JSON 取值口徑、業務失敗原樣透傳、三個清單接口的 markets／broker 原樣透傳為統一前綴（含 markets 省略時不再拋 TypeError 的回歸檢查）、串流協定與日誌遮罩（不需券商連線）
python brokery/acceptance/run_ui.py            # dashboard 客戶端：以存根閘道 + Chromium 核對腳本無語法錯誤、頂欄四家指示、金鑰記憶與回填、探測只由載入與按鈕觸發、戶口頁自動刷新與按來源汇总、標的頁區分「不提供／無返回」、標的頁不再有「統一格式輸出」面板、離線 CODES 不分區而以單一表格顯示且欄位順序即接口原樣（不需券商連線；需 `playwright install chromium`，未裝即跳過）
python brokery/acceptance/run_webui.py         # Web UI：以存根閘道核對轉發原樣透傳信封與金鑰只在服務端、金鑰不符與閘道不可達均明確報錯；以 Chromium 核對菜單兩項、欄位即 ACCOUNT_COLUMNS、千分位與破折號、按來源統計；標的頁先取能力聲明再取清單、券商選項由聲明填充且默認 futu（不提供該品種者標註且不可選）、表格欄位即 COLUMNS、市場選項只由返回的 market 填充、選市場與轉類型均向對應接口再取一次（不需券商連線；未裝 Chromium 即跳過）
python brokery/acceptance/run_gui.py           # 桌面 GUI（brokery_gui）：以存根閘道 + Qt 離屏核對三個 .ui 檔內不含任何文字、三種語言各一個 .json 且鍵集合一致、切換即時生效且不重建窗口、缺譯返回鍵名、表格欄位即 ACCOUNT_COLUMNS／COLUMNS、缺失值破折號與資金欄千分位、按來源統計、券商選項由能力聲明填充且默認 futu（不提供該品種者標註且不可選）、市場選項只由返回的 market 填充、選市場與轉類型均向對應接口再取一次、閘道不可達與金鑰不符均明確報錯、直接啟動 `brokery_gui/run.py` 核對窗口會存活（不需券商連線，亦不需顯示器）
python brokery/acceptance/run_launch.py        # 啟動器 run_all.py：以存根命令核對兩個同時啟動、先結束者停止另一個並返回其退出碼、正常結束返回 0、Ctrl+C 一併停止、預設命令即兩個既有入口、啟動器不引入券商 SDK（不需券商連線，亦不真的啟動服務）
```
測試以腳本方式直接執行（不使用 pytest）：執行後即輸出 `status`、`message` 與完整代碼表，
並以退出碼 `0`/`1` 表示成敗。

## 環境
- 連線參數與離線資料目錄全部讀自 `.env`（`FUTU_OPEND_HOST/PORT`、`IB_HOST/PORT/CLIENT_ID`、
  `IB_REQ_TIMEOUT`、`BROKERY_DATA_DIR`、`TIGER_ID/ACCOUNT/TOKEN/PUBLIC_KEY/PRIVATE_KEY`、
  `WEBULL_APP_KEY/APP_SECRET`、`WEBULL_REGION_ID`、`WEBULL_TOKEN_DIR`）。
- 閘道（`brokery_api`）的參數同樣只在 `.env`：`API_HOST/PORT`、`API_KEY`（自訂金鑰，
  **未設即拒絕啟動**）、`API_SOURCES`（启用的券商，逗號分隔）、`API_AUTYPE`、`API_LOG_LEVEL`、
  `API_LOG_DIR`（預設 `logs/`，不入版本控制）、`API_STREAM_SECONDS`（單次串流的秒數上限，客戶端
  要求更長即被截至此值）。
- Web UI（`brokery_webui`）只多兩個參數：`GUI_HOST`/`GUI_PORT`（預設 `127.0.0.1:8282`，變數名沿用未改）。閘道地址與金鑰
  沿用上面的 `API_HOST`/`API_PORT`/`API_KEY`，日誌沿用 `API_LOG_*`，不另設一套。
- 桌面 GUI（`brokery_gui`）不新增任何參數：窗口沒有填金鑰的位置，閘道地址與金鑰一律讀 `API_HOST`/`API_PORT`/
  `API_KEY`，未設 `API_KEY` 即在啟動時明確報錯，不開一個讀不到數的窗口。
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
