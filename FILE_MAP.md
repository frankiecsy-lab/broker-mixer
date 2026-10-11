# FILE_MAP

| 檔案 | 核心職責 |
| --- | --- |
| `brokery/__init__.py` | 對外導出 `Brokery` 與 `CodeError`。 |
| `brokery/core.py` | 唯一入口：按券商能力調度清單、統一返回信封與欄位、去重、失敗原因彙總；`get_code` 離線讀回已存放的 CODES；`get_kline` 按 `broker` 選來源取 K 線，並按券商聲明的 `autypes` 校验複權參數、按 `kline_symbol_types` 校验品種（不支持即報錯，`_check_kline_type` 統一拒绝）；`stream_kline` 串流多個代碼，按 `stream_ktypes`/`stream_autypes` 校验串流範圍；`get_accounts` 按券商聲明的 `acc_types` 校验戶口性質並統一过滤（`bad_acc_type`/`acc_type_unsupported`），只列真實且已啟用的戶口，個別券商失敗仍返回已取得的，`_dedupe_accounts` 以 (來源, 戶口, 幣種) 去重。 |
| `brokery/codes.py` | 統一代碼格式與雙向映射（市場/貨幣/交易所、港股前導零、期貨 main 與到期月拆離）；`classify_symbol` 由代碼推斷品種（STOCK/FUTURE/INDEX/OPTION）；不依賴券商 SDK。 |
| `brokery/config.py` | 讀 `.env` 得連線參數與離線資料目錄；全專案唯一配置來源。 |
| `brokery/store.py` | 離線存放層：DataFrame 以 parquet 寫入/讀回 `<data>/<name>.parquet`，並維護 `<name>.meta.json`；`CODES_DATASET` 為代碼清單的資料集名稱。 |
| `brokery/universe.py` | 期貨 root 與指數符號的種子清單，只收錄實測可解析條目。 |
| `brokery/brokers/base.py` | 券商契約基類、統一欄位 `COLUMNS`/`K_COLUMNS`、能力聲明與跨來源去重；ktype 詞表、市場時區與 UTC 換算、bar 數→日曆跨度（`span_days`）、週期錨點對齊（`align_ts`）、能力聲明（`capabilities`/`autypes`/`stream_ktypes`/`stream_autypes`/`kline_symbol_types`，後者聲明可取 K 線的品種，預設只含股票；`acc_types` 聲明可返回的戶口性質）；戶口欄位 `ACCOUNT_COLUMNS` 與 `account_row`/`account_num`（缺欄一律留空不臆造）、`ACC_CASH`/`ACC_MARGIN` 詞表；串流用的 `BarMerger`（按 `ts` 合併、保留最新 count 根）與 `stream_wait`。 |
| `brokery/brokers/futu_broker.py` | 富途標的清單：`get_stock_basicinfo` 按市場與類型一次取全（股票/ETF、期貨、指數），含 `exchange_type` 映射與不支持組合的跳過；K 線 ≤1000 根用 `get_cur_kline`、更多改用 `request_history_kline` 分頁；K 線串流经 `_KlinePushHandler`（`CurKlineHandlerBase`）接收實時推送，按 `k_type` 過濾，全部代碼共用同一條連線；`get_accounts` 由 `get_acc_list` 只留 REAL 且 `acc_status` 為 ACTIVE 的戶口，再逐戶 `accinfo_query` 取資金，幣種取 `trdmarket_auth` 首個有結算幣的市場（全無則 `currency_undetermined`）。 |
| `brokery/brokers/ib_broker.py` | IB 期貨/指數展開與代碼雙向轉換；指數按名稱解析（美股指數去前導點即同名，港股只認 `IB_INDEX_ALIAS` 四隻，`IND` 查詢不带 `currency`，其餘明確返回 unresolvable）；K 線由 bar 數換算 `durationStr`（>365 日以年計）再截尾，複權支援 `none` 與 `qfq`（`ADJUSTED_LAST`，僅日內/日線，週/月線明確拒绝）；全部請求共用 `_SharedConnection`（單一持續連線 + event loop 執行緒 + 合約解析快取，兜底超時可按請求次數放宽）；K 線串流以 `keepUpToDate=True` 原生推送，只支持 `autype="none"`，結束時退訂；主連（`CONTFUT`）實測不帶 exchange 一律查唔到，故 `_collect_futures`/`_best_match` 一律先以同 root 的 `FUT` 取得掛牌場（`_primary_exchanges` 主場排先）再查；`get_accounts` 以 `accountSummary`（自備 tag 清單，每次請求前清空 `wrapper.acctSummary`）配 `accountValues` 取資金，按 (戶口, 幣種) 分行，戶口性質由 `AccountType` 原樣小寫透傳。 |
| `brokery/brokers/tiger_broker.py` | Tiger OpenAPI 的 K 線來源：`get_bars` 按 bar 數取數（`right` 對應複權，只支持 `none`/`qfq`，無後復權概念）；K 線串流经 `subscribe_kline` 原生推送，只支持 `1m` 與 `autype="none"`；鑑權用 `.env` 的 RSA 私鑰對每個請求簽名（缺私鑰即 `not_configured`），不改寫 SDK 的 `tiger_public_key`（老虎自己的公鑰，用於驗簽）；`get_accounts` 由 `get_managed_accounts` 只取 STANDARD 真實戶口（PAPER 在發 `get_assets` 前即跳過），戶口性質按 `capability` 的 BasicCash/RegTMargin 判定，資金取 `get_assets`，只有結算幣一筆（接口無按幣種參數）。 |
| `brokery/brokers/webull_broker.py` | Webull OpenAPI 的 K 線來源：`get_batch_history_bar` 按 bar 數取數（無成交額，`turnover` 為 NaN）；接口無復權參數，價格由週期固定（日線及以上前復權、分鐘線不復權），要求另一種即明確報錯；無 3 分鐘週期；無 K 線推送，故串流以輪詢批量 bar 接口湊出相同的回呼語義（2 秒間隔，按 category 分組共用同一客戶端）；`get_accounts` 由 `get_account_list` 定戶口、`get_account_balance` 取資金（指定 currency 時改讀 `account_currency_assets` 的該幣種明細），接口不返回戶口狀態故 `status` 留空。 |
| `brokery/acceptance/run_futu_codes.py` | 取全港美 CODES（股票 + 期貨 + 指數），以腳本直接執行並輸出 status、message 與 DataFrame。 |
| `brokery/acceptance/run_futu_codes_store.py` | 取全港美 CODES 後離線存放，並讀回核對行數與欄位一致。 |
| `brokery/acceptance/run_get_codes.py` | 驗收 `get_code`：經統一入口離線讀回 CODES 並輸出 meta 與內容，可按 `symbol_type` 過濾，不需連線。 |
| `brokery/acceptance/run_get_kline.py` | 驗收 `get_kline`：同一 code 分別經 futu、ib、tiger 取 K 線，核對欄位、`ts` 遞增、bar 數與跨券商對齊（含逐根價格一致），並核對券商不支持的複權模式明確報錯；另以 `webull_checks()` 獨立核對 Webull 的取數與三組明確報錯（其價格由週期固定，不参與跨券商比價），可帶 `code ktype count` 參數。 |
| `brokery/acceptance/run_align_kline.py` | 驗收跨券商前復權：同一 code 分別取 futu、ib、tiger、webull 的 `qfq`，以 futu 為準按 `ts` 逐根並列並量化各家與它的偏差，並與各自的原始成交價對照（調整根數與幅度），另核對 ib 週線要求復權時明確報錯；驗收券商按 `MARKETS` 過濾為各憑證實際開通的市場（未開通者跳過並打印 WARN）。 |
| `brokery/acceptance/run_stream_kline.py` | 驗收 `stream_kline`：一條連線同時串流多個代碼（futu/ib/tiger/webull 四家），核對欄位、各代碼 `ts` 嚴格遞增、bar 數不超過 `count`、持續時間受 `seconds` 約束、每次回呼的幀合規格，以及不支持復權的三家明確報錯；驗收代碼按 `MARKETS` 過濾為各憑證實際開通的市場（未開通者跳過並打印 WARN），可帶 `codes ktype count seconds` 參數。 |
| `brokery/acceptance/run_kline_matrix.py` | 驗收品種 × 券商矩陣：`classify_symbol` 的推斷、未聲明品種在發請求前即返回 `type_unsupported`（含 `stream_kline`）、期貨/指數/期權的 `qfq` 與 `none` 逐根相同而股票對照組必須被調整、同一指數跨券商逐根對齊；期權代碼由富途期權鏈即時取得。 |
| `brokery/acceptance/run_get_accounts.py` | 驗收 `get_accounts`：四家一律以 `ACCOUNT_COLUMNS` 返回，核對格式統一、只列真實且已啟用的戶口、`currency` 欄有無真係填到，以及 `acc_type`/`currency`/`broker` 三個參數在非法或不支持時明確報錯。 |
| `brokery/data/` | 離線資料目錄（`<name>.parquet` + `<name>.meta.json`），路徑由 `.env` 指定，不入版本控制。 |
