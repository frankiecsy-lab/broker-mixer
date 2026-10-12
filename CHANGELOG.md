# CHANGELOG

## 未發布
### 新增
- `brokery` 統一入口：`list_stocks` / `list_futures` / `list_indices` / `list_all` / `convert`，
  一律返回 `{"status", "data", "message"}` 信封，欄位固定為 `brokers.base.COLUMNS`。
- 券商適配層全面更名為 broker：`brokery/backends/` → `brokery/brokers/`，`*_backend.py` →
  `*_broker.py`，`SymbolBackend`/`FutuBackend`/`IbBackend` → `SymbolBroker`/`FutuBroker`/`IbBroker`。
- 統一代碼層（`codes.py`）：富途格式 `MARKET.SYMBOL`、市場↔貨幣↔交易所映射、港股前導零雙向
  轉換、期貨 `main` 主連後綴與到期月拆離。本層不依賴任何券商 SDK。
- FUTU 適配器：改用 `get_stock_basicinfo` 按（市場, 證券類型）一次取全，涵蓋 `STOCK`/`ETF`、
  `FUTURE`、`IDX` 三類；無分頁、無條件選股限頻，港美兩市數秒完成（實測股票 23750、期貨 14078、
  指數 740 條）。同時以 `exchange_type` 填充 `exchange` 欄。
- IB 適配器：以 `CONTFUT` 取主連、`FUT` 展開所有到期月、`IND` 解析指數；提供統一代碼與
  IB Contract 的雙向轉換。每次呼叫在獨立 `asyncio.run` 內完成連線與查詢，每個請求以
  `asyncio.wait_for` 設超時。
- 期貨與指數種子表（`universe.py`）：只收錄實測可解析的條目。
- `brokery/acceptance`：單一驗收測試，直接取全量 CODES（股票 + 期貨 +
  指數）並輸出結果；驗收目錄由項目根目錄的 `acceptance/` 移入 `brokery/acceptance`。
- 驗收一律以腳本直接執行（`python brokery/acceptance/run_futu_codes.py`），不引入 pytest：
  沒有 `test_*` 入口函數亦無 `pytest.ini`。IDE 的 pytest 面板會捕獲 stdout，看不到 status /
  message / DataFrame 的實際輸出，直接跑腳本可在控制台即刻看到並以退出碼表示成敗。
- 驗收檔名由 `test_futu_codes.py` 改為 `run_futu_codes.py`：`test_*.py` 會被 IDE 自動套用
  pytest runner（`collected 0 items`／`Empty suite`），改前綴後一律按普通 Python 腳本執行。

- 離線存放層 `brokery/store.py`：`save_frame` / `load_frame` / `load_meta` / `list_stored`，每個
  資料集一檔 `<name>.parquet` 加一份 `<name>.meta.json`（行數、欄位、來源、UTC 寫入時間）。
  目錄由 `.env` 的 `BROKERY_DATA_DIR` 指定（預設 `brokery/data/`，即主資料夾之內，已加入
  `.gitignore`；相對路徑一律以項目根目錄為基準）。
- `brokery/acceptance/run_futu_codes_store.py`：取全量 CODES → 離線存放 → 讀回核對行數與欄位。
- `Brokery.get_code(name)`：離線讀回已存放的 CODES（預設 `store.CODES_DATASET`，即 `futu_codes`），
  返回同一個 `{"status", "data", "message"}` 信封；未存放時 `status=False`。券商連線為按需建立，
  故本方法不需要 OpenD 或 IB。
- `brokery/acceptance/run_get_codes.py`：驗收 `get_code`，輸出 meta（行數、來源、寫入時間）
  與內容，可帶 `STOCK`/`FUTURE`/`INDEX` 參數只顯示某一類型；不需要任何連線。
- 新增依賴 `pyarrow`（parquet 讀寫）。

- `Brokery.get_kline(code, ktype, count, autype, broker)`：以 bar 數取 K 線，統一以富途格式輸出，
  欄位固定為 `brokers.base.K_COLUMNS`（`code/ts/time_key/open/high/low/close/volume/turnover/source`）。
  `ktype` 詞表 `1m/3m/5m/15m/30m/60m/day/week/month`；`ts` 為 UTC 秒，作跨券商對齊鍵，`time_key`
  保留券商原生 bar 時間（統一為 `YYYY-MM-DD HH:MM:SS`）。
- 富途 K 線：≤1000 根用 `get_cur_kline`（原生 bar 數接口，需先訂閱同類型），更多改用
  `request_history_kline` 按日期範圍分頁再截尾。
- IB K 線：無 bar 數參數，故由 `span_days` 反推時間跨度（刻意多覆蓋周末與假期）再取最後 `count` 根。
- 跨券商對齊：`base.align_ts` 把週/月 bar 的 `ts` 一律歸到所屬週期起點，錨點由各適配器以
  `kline_anchor` 聲明（富途 `ANCHOR_START`、IB `ANCHOR_END`）。
- `brokery/acceptance/run_get_kline.py`：同一 code 兩家各取一次，核對欄位、`ts` 嚴格遞增、bar 數不超
  過請求值、可按 `ts` 對齊，並在同取 `autype="none"` 時逐根比對 close。
- 統一的複權設定：`Brokery(autype=...)` 設全域預設（預設 `qfq`），`get_kline(autype=...)` 逐次覆蓋；
  各券商支援的模式由 `SymbolBroker.autypes` 聲明（富途 `qfq`/`hfq`/`none`、IB `none`/`qfq`）。要求了
  不支持的模式返回 `status=False` 與 `autype_unsupported:` 訊息，不再靜靜忽略（此前傳 IB `qfq` 會
  若無其事地返回原始成交價）。
- IB 的前復權路徑：`autype="qfq"` 改用 `whatToShow=ADJUSTED_LAST`（`IB_WHAT_TO_SHOW`）。只適用日內與
  日線，週/月線由適配器以 `MULTI_DAY_KTYPES` 明確拒绝並附上 IB 的 error 321 原文。
- `brokery/acceptance/run_align_kline.py`：同一 code 分別取兩家的前復權，按 `ts` 逐根並列顯示，並與
  各自的原始成交價對照（顯示被調整的根數與最大調整幅度），同時驗證 IB 週線要求復權時明確拒绝。

- `Brokery.stream_kline(codes, ktype, count, broker, autype, seconds, on_update)`：串流最新 K 線。多個
  代碼共用一條連線（對應同時顯示多張 K 線圖）；先返回歷史 bar 作起點，之後最新一根每次變化即回呼
  `on_update(code, rows)`，`rows` 為該代碼按 `ts` 升序、不超過 `count` 根的完整結果。`seconds` 為持續
  秒數，`0` 表示直到 Ctrl-C；返回的 `data` 為各代碼最終的合併結果，欄位同 `K_COLUMNS`。
- 串流一律用原生推送，不是輪詢：富途以 `CurKlineHandlerBase` 接收實時 K 線推送（起點由 `get_cur_kline`
  取得，同時完成訂閱）；IB 以 `reqHistoricalData(keepUpToDate=True)`，同一請求先返回歷史、之後持續更新。
- IB 適配器改為單一持續連線 `_SharedConnection`：由專用的 event loop 執行緒驅動，清單、代碼轉換、K 線與
  串流全部共用，並快取合約解析。`call(coro_factory, budget)` 的兜底超時可按一段協程內的請求次數放宽
  （逐個代碼建立訂閱時不因多張圖而誤報超時）。
- 串流的支援範圍由券商另行聲明（`SymbolBroker.stream_ktypes` / `stream_autypes`），由 core 在開始前校验：
  IB 的推送只能 `autype="none"`（`keepUpToDate` 與 `ADJUSTED_LAST` 同時使用被拒，error 321），要求復權
  即返回 `autype_unsupported:`，不靜靜改用另一種價格。
- `base.BarMerger`（按 `ts` 合併、只保留最新 `count` 根、以 OHLCV 簽名去重、`frame()` 升序輸出）與
  `base.stream_wait`（`seconds=0` 時直到 Ctrl-C，以短間隔輪詢使 Ctrl-C 能及時返回並視為正常結束）。
- `brokery/acceptance/run_stream_kline.py`：一條連線同時串流 2 個代碼 × 兩家，核對欄位為 `K_COLUMNS`、
  各代碼 `ts` 嚴格遞增、bar 數不超過 `count`、持續時間受 `seconds` 約束、每次回呼的幀本身合規格，以及
  IB 不支持的串流複權模式明確報錯；可帶 `codes(逗號) ktype count seconds` 參數。
- 修正 `IB_BAR_SIZE["1m"]`：原寫 `1 mins` 被 TWS 拒（error 321 並列出合法值），改為 `1 min`。既有验收
  一律用日線，故這個錯誤從未被觸發。

### 技術決策與實測限制
- 股票清單只取自富途；IB 無批量列出全市場股票的接口，只作代碼轉換與逐個解析。
- 向 IB 查詢股票／個月份不得指定 `exchange`（指定後常回報 `No security definition found`）；主連
  （`CONTFUT`）則相反，必須帶 exchange，詳見下文「主連解析」。港股符號須去前導零。
- 單一合約解析改用 `reqContractDetails` 而非 `qualifyContracts`：同一合約常在 CME 與 QBALGO
  等處同時掛牌，`qualifyContracts` 會直接回報 Ambiguous。
- 清單去重：同一合約多處掛牌時只保留主場，次要場所（QBALGO、TRULYTA、MEMX、CBOE2 等）剔除。
- 個月份的到期月只寫入 `expiry` 欄，不寫進 `code`；`US.ES20261218` 這類輸入會正規化為
  `US.ES` + `expiry`。
- 富途股票清單不用 `get_stock_filter`：它是條件選股，需分頁且受「每 30 秒 10 次」限頻（實測取
  美股中途被拒、且 `has_next` 在 `total=2831` 時返回 False）；`get_stock_basicinfo` 一次返回全量、
  無該限頻、`name` 無空值、`delisting` 全為 False，故改用後者。
- 富途 `get_stock_basicinfo` 無 `ALL` 類型（`NONE` 回報「未知股票類型」），需按類型分別請求。
- 富途的期貨/指數批量清單（`FUTURE`/`IDX`）已一併納入：主連同樣用 `main` 後綴（實測
  `US.10Ymain`，另有 `current`/`next`/`day` 變體，`last_trade_time` 為空），與本專案約定一致；
  但個月份為富途原生代碼（`US.10Y2609`），與 IB 的 root + 到期月無法直接對映，故跨券商對映仍
  以 IB 為準。
- 富途 `get_stock_basicinfo` 不支持日本市場的指數（「获取静态数据接口不支持日本市场的指数」）；
  後端把這類明確不支持的（市場, 類型）視為能力缺口跳過，其餘非零返回照樣抛出。
- 此版本 futu-api 的 `SysConfig` 不收 `timeout`，`get_stock_basicinfo` 亦無 timeout 參數；因每個
  （市場, 類型）只發一次請求，無無界迴圈風險。
- 離線格式選 parquet 而非 CSV：保留欄位型別、體積小，其後 K 線等大批量資料同樣經本層存放。
- IDE 的 parquet 預覽把字串欄位顯示為位元組數組（`{72,75,46,…}` 即 `HK.`，中文為負數即 UTF-8 多
  字節），改寫成 `string` 亦同樣，屬檢視器限制；實測 schema 為 `large_string`、`load_frame` 讀回
  文字完全正確，故存放格式不變。
- 富途 `get_cur_kline` 需先訂閱同類型 K 線，此版本無分頁參數、單次上限 1000 根；更多 bar 只能改經
  `request_history_kline`（受帳戶歷史 K 線配額限制）。`autype` 只接受小寫 `qfq`/`hfq` 與字串 `"None"`
  （傳 `QFQ`、Python `None` 或 `"none"` 均被拒，儘管錯誤訊息寫住 `(None,qfq,hfq)`）；成交額欄名為
  `turnover`。
- 一年的交易日遠少於 365 日（港股實測約 244）：只按周末 2/7 放大跨度會取不足數（1200 根日線只回
  1178 根），故 `span_days` 一律按 365/240 換算並加固定假期緩衝。
- IB 的 `durationStr` 超過 365 日必須以「年」為單位（實測 error 321），故 `_duration` 按年向上取整；
  `whatToShow="TABS"` 對股票被拒，一律用 `TRADES`；IB 不返回成交額，`turnover` 只能為 `NaN`；
  日/週/月 bar 返回的是 `datetime.date`；查詢失敗只以 `errorEvent` 回報而 `reqHistoricalData` 返回
  空表，故收集 162/300/321 錯誤碼一併抛出。
- 非日內 bar 的錨點兩家不同：富途以週期起點（週線週一、月線每月一日）、IB 以週期終點（週線週六、
  月線下月一日，當期未走完則以今日）為 bar 時間，OHLC 卻完全相同。只按原生時間排序會錯開一個週期
  （週線 120 根零重疊、月線出現 `ts` 碰撞），故以 `align_ts` + `kline_anchor` 統一歸到週期起點。
- 富途預設前復權、IB 為原始成交價，兩者隨除淨日累積相差（月線 60 根最大相差 53%），跨券商比價必須
  兩家同取 `autype="none"`；實測此下面對月線 close 完全一致、日/週線最大相差 < 0.2%。
- IB 的復權只有 `ADJUSTED_LAST`（無後復權對應值），實測確會調整（2 年日線 492 根中 451 根被改），
  但**對週/月線直接報 error 321「Multi day bar size not supported with adjusted last」**。故 `autypes`
  聲明 `none`/`qfq`，而週/月線要求復權時由適配器明確拒绝並附上該錯誤原文，不靜靜返回原始價。
- 兩家的前復權一律可按 `ts` 逐根對齊（`HK.00005` 60/60、`US.NVDA` 120/120）；數值是否一致則視市場：
  美股日線 120 根兩家調整了同一 98 根且幅度完全相同（最大 0.2281%），逐根一致；港股日線 60 根雖同樣
  調整了 19 根，幅度卻差一個量級（富途最大 0.50%、IB 最大 0.062%），對照後最大相差 0.44%，即 IB 對
  港股派息的調整明顯偏小。故不涉及復權的比價仍一律用 `autype="none"`（原始價逐根吻合，最大 < 0.4%）。

- 環境：pyarrow 26 要求 NumPy ≥ 2.0，故全局 NumPy 由 1.26.4 升至 2.5.3；實測 futu-api
  10.5.6508、ib_async 2.1、pandas 3.0.2 在此組合下全部正常。`pip check` 另回報 dctorch 0.1.2、
  numba 0.65.1、scipy 1.12.0 仍要求 numpy < 2 / < 2.5，使用這些套件時需另行升級。
- 多圖不各開連線：4 圖、8 圖的全部訂閱都掛在同一條持久連線（IB `_SharedConnection`、富途同一
  `OpenQuoteContext`）上；結束時一律退訂（富途 `unsubscribe`、IB `cancelHistoricalData`），實測 4 個
  訂閱退訂後 `reqId2Subscriber` 歸零、連線其後仍可正常取歷史。
- 推送回調一律在券商的推送／連線執行緒中發生，故回呼內只做合併與回調，不做耗時工作；有變化才回呼
  （由 `BarMerger.merge` 的返回值決定），避免每 tick 空轉。
- 富途的推送帶 `k_type` 欄，同一連線亦會收到 `get_kline` 訂閱的其他 ktype，故回呼按 `k_type` 過濾；
  自訂 handler 必須呼叫 `super().__init__()`，否則 SDK 的 `RspHandlerBase.__del__` 會在解譯器退出時抛
  `AttributeError: '_KlinePushHandler' object has no attribute '_file'`。
- IB 的 `keepUpToDate` 要求 `endDateTime=""`，返回活的 `BarDataList`，每次更新只改寫最後一根或在末尾
  追加新根，故合併只需處理末尾兩根；全部 ktype 均可推送（實測 `1 min`…`1 month` 訂閱皆存活並持續更新）。
- 休市時段兩家均無推送（實測星期六兩家皆 0 次），故验收只對回呼的規格作斷言、推送次數以 INFO 顯示；
  真正的推送要在開市時段才看得到。

### 新增（Tiger / Webull 兩家 K 線適配器）
- `brokers/tiger_broker.py`：`get_bars(symbols, period, limit=count, right=QuoteRight.BR)` 原生按 bar
  數取數；`autypes=("qfq","none")`（無後復權概念）；串流以 `subscribe_kline` 原生推送，
  `stream_ktypes=("1m",)`、`stream_autypes=("none",)`。鑑權為 RSA 簽名，缺 `TIGER_PRIVATE_KEY` 時明確
  返回 `not_configured`。
- `brokers/webull_broker.py`：`get_batch_history_bar` 按 bar 數取數（單次上限 1200 根）；無 3 分鐘
  週期（`Timespan` 無 M3）；無 K 線推送，故 `stream_kline` 以 2 秒間隔輪詢批量 bar 接口，按 `category`
  分組、每市場一次請求覆蓋該市場全部代碼，最新一根有變化才回呼，對外語義與推送券商一致。
- `core.BROKERS` / `DEFAULT_SOURCES` 註冊 `tiger`、`webull`；`config.py` 讀取 `TIGER_*`、`WEBULL_*`
  （金鑰一律在 `.env`）。新增依賴 `tigeropen`、`webull-openapi-python-sdk`。
- `base._TIME_FORMATS` 增加 ISO 8601 帶時區偏移的格式：Webull 的 bar `time` 為
  `2026-10-08T16:00:00.000+0000`，原有格式全部解析失敗（`bad_time_key`）。帶偏移者按其自身偏移換算，
  裸時間仍按市場時區解釋。
- `run_get_kline.py` 新增 `webull_checks()`：Webull 的複權由週期固定，無法參與以 `autype="none"` 的
  跨券商比價，故獨立核對「日線以 qfq 取數成功 + 格式與 bar 數 + 日線 none／分鐘線 qfq／3m 三組明確
  報錯」，不隨命令行的 ktype 改變。`run_stream_kline.py` 的 `BROKERS`、`REFUSE_QFQ` 納入 `webull`。
- `webull_broker._bars` 把 403 `MARKET_DATA_NOT_SUBSCRIBED` 轉為 `market_data_not_subscribed`，說明該
  市場未開通行情；其餘 `ServerException` 原樣抛出，由 core 統一轉 `kline_failed`。
- `run_stream_kline.py` 新增 `MARKETS`／`_codes_for()`：按各券商憑證實際開通的市場過濾驗收代碼，無可
  驗收代碼者跳過並打印 WARN，不把賬戶的行情權限問題當做代碼錯誤。預設代碼增加 `HK.00700`，使只開通
  HK 的 Webull 仍以兩個代碼驗收一條連線的批量取數。

### 實測結論（Tiger / Webull）
- Webull 只有 LIVE 憑證可用：SDK 的 host 表只有各區域正式網域，沒有模擬環境，實測
  `WEBULL_SIM_APP_KEY` 在 `api.webull.com`／`.hk`／`.co.jp`／`.com.sg`／`.com.au`／`webull-uk.com`
  全部返回 401，故 SIM 金鑰只存放不使用。
- Webull 的 token 需在使用者的 Webull App 中批准；未批准時 SDK 抛 `ERROR_INIT_TOKEN status:PENDING`，
  由適配器轉為 `token_unapproved` 並說明 token 存放位置。批准後 token 以 `NORMAL` 持久化，之後直接沿用。
  SDK 預設等待 300 秒，過長會令呼叫長時間阻塞，故改為 30 秒上限、5 秒間隔。
- Webull 的接口沒有復權參數：日線及以上只給前復權、分鐘線只給不復權。因此 `autypes` 聲明兩種、由
  `_check_autype` 按週期把關，要求另一種即明確報錯，不靜靜返回另一種價格。實測 `HK.00001` 日線
  close（67.90 / 66.05）與 IB 原始價（67.90 / 66.04）吻合。
- Webull 返回只有 OHLCV，無成交額，`turnover` 一律 `NaN`；批量接口返回原始 `requests.Response`，
  需自行取 json，且外層結構不固定（`{result:[...]}`、`[{symbol,result:[...]}]` 或裸 bar 列表）。
- Webull 的行情限額為港股 60 次/60 秒、美股 600 次/分鐘，故輪詢間隔取 2 秒（每市場 30 次/分鐘）。
- app key 綁定註冊區域：同一金鑰改用 `region_id="us"` 即 401 `UNAUTHORIZED`；且行情按市場開通，實測
  `HK_STOCK` 正常（`real_time_required` 真假皆可），`US_STOCK` 一律 403 `MARKET_DATA_NOT_SUBSCRIBED`，
  與 `real_time_required` 無關，屬賬戶未開通美股行情。另 token 與 token 目錄綁定，換目錄即需重新批准。
- Tiger 的 token 有效期為 30 日且需 RSA 私鑰做簽名鑑權，缺私鑰時無法實跑（`get_kline` 返回
  `not_configured`）。私鑰由平台在生成密鑰對時顯示一次、服務端不保存（官方文件已註明），故無法事後
  取回，只能在「您的RSA KEY」下重新生成一對並同時更新 `.env` 的兩個值；格式為單行 base64，
  `load_private_key` 對 PKCS#1 與 PKCS#8 均可解析，帶 PEM 頭尾亦由 `_bare_key` 去除。實測平台「您的Token」
  的「下載」導出 `tiger_openapi_token.properties`，內容只有 `token=` 一行，不含私鑰，故該導出不能取回私鑰。
- 適配器不設 `config.license`（本賬戶牌照為 TBHK）：`tiger_open_config.py` 中 license 只用於
  `refresh_server_info()` 的域名選擇，且需 `enable_dynamic_domain` 與已取得的域名清單同時成立，否則一律
  用內建預設域名。故不設 license 不影響 TBHK 取數；如日後出現域名相關失敗，再經 `TIGEROPEN_LICENSE`
  或 `config.license` 指定。
- Tiger 已實跑通（用戶提供舊版 `tiger_openapi_config.properties` 的內容，含 `private_key_pk1`/
  `private_key_pk8`/`license=TBHK`/`env=PROD`，live 與 demo 兩段共用同一對密鑰）。取 `.env` 的
  `TIGER_PRIVATE_KEY` 即通過鑑權：日線 60 根、1 分鐘線一條連線串流港美 3 個代碼，`autype="none"` 時
  收盤價與 FUTU 逐根完全一致（最大相差 0.0000%）。
- 該可用私鑰與平台頁面顯示的公鑰 **modulus 不同（並非同一密鑰對）**，伺服器仍接受其簽名。故
  `TIGER_PUBLIC_KEY` 只作記錄，不能用「私鑰與公鑰是否配對」判斷私鑰可用與否，唯一可靠判據是實跑。
- `acceptance/run_stream_kline.py` 的汇总行把 `sum(updates[name])` 寫成對 dict 的鍵求和（應為
  `.values()`），只在全部檢查通過時才執行，故先前 tiger 失敗時未觸發；已修正。
- `TIGER_TOKEN` 不能取代 RSA 私鑰：token 只作 `Authorization` 頭（`_update_header`），每個請求仍必須由
  私鑰簽名（構造客戶端時即 `private key can not be empty`，每次請求 `sign_with_rsa`）。實測以本地臨時
  生成、未在平台登記的私鑰簽名，伺服器返回 `code=1000 failed to verify signature, please make sure you
  use the correct rsa private key`，故私鑰無可取代。token 有效期 30 日（解碼其前段即起止毫秒時間戳）。
- SDK 的 `config.tiger_public_key` 是「老虎自己的公鑰」（`verify_with_rsa` 用它驗證返回簽名，
  `tiger_open_config.py` 自帶生產環境預設值），與本帳戶在平台登記的公鑰是兩回事。實測兩者的 base64
  並不相同，故適配器**不再**把 `.env` 的 `TIGER_PUBLIC_KEY`（帳戶公鑰）餵給該字段——若餵錯，返回帶
  `sign` 時會抛 `ResponseException: response sign verify failed`。該 `.env` 項只作記錄（不可作配對核對，
  見上文 modulus 一條）。
- `acceptance/run_align_kline.py` 由 futu + IB 擴展為四家（futu/ib/tiger/webull），以 `REFERENCE = "futu"`
  為準逐家與它 `merge(on="ts")` 並列，逐家斷言可對齊根數與與富途的偏差；Webull 按 `MARKETS` 只驗 HK
  （美股代碼跳過並打印 WARN，與 `run_stream_kline.py` 同一處理）。實測 `HK.00005` 日線 60 根：四家共同
  60 根、都調整了同一 19 根，但幅度差一個量級（富途 0.50%、Tiger 0.49%、IB 0.062%），與富途對照最大
  相差 Tiger 0.02%、IB 與 Webull 各 0.44%。Webull 的日線無法取 `autype="none"` 對照（復權由週期固定），
  腳本改為打印該明確報錯而不計失敗。
- Webull 日線**確實做了復權調整**（不是只返回原始價）：`HK.00005` 日線 60 根與富途、IB 的原始成交價
  逐根比較，調整了同一 19 根、最大 0.062%，即調整因子與 IB 的 `ADJUSTED_LAST` 一致。故先前「Webull 日線
  close 與 IB 原始價吻合」的講法不準確（實為相差 <0.07%），兩家對港股派息的調整都明顯小於富途（0.50%）。

### 新增（品種能力閘）
- `codes.classify_symbol(market, symbol)`：由統一代碼推斷品種（`STOCK`/`FUTURE`/`INDEX`/`OPTION`）。
  判據只靠代碼形態：帶 `main` 後綴或到期月為期貨，`US..SPX`（前導點）與 `HK.8xxxxx`（六位、8 開頭）
  為指數，`AAPL261106C110000`（正股+YYMMDD+C/P+行權價）為期權，其餘按股票。不新增任何欄位，亦不改變
  標的清單（清單仍以券商返回的 `symbol_type` 為準）。
- `SymbolBroker.kline_symbol_types` + `supports_kline()`：各適配器聲明可取 K 線的品種，基類預設只含
  `STOCK`（保守），實測可用者擴寬：futu 四類、ib `STOCK/FUTURE/INDEX`、tiger `STOCK/INDEX`、
  webull 只餘 `STOCK`。
- `core._check_kline_type()`：`get_kline` 與 `stream_kline` 在發出請求前統一拒绝未聲明的品種，返回
  `type_unsupported`（例：`tiger 不提供 FUTURE 的 K 線（tiger 只提供 STOCK/INDEX）`）。此前這些組合會
  被當股票送進上游，回報為 `empty_kline`（Tiger 期貨）、上游 417（Webull 指數）或 IB 的解析失敗，
  無法區分「不支援」與「取不到」。
- `ib_broker.IB_INDEX_ALIAS` 與 `_resolve` 按品種構造候選：IB 的指數以**名稱**登記且 `IND` 查詢不接受
  `currency`（實測帶 currency 的 IND 查詢一律 0 筆），故美股指數去前導點即同名（`.SPX`→`SPX`），港股
  六位數字只登記 `HK.800000→HSI`、`HK.800100→HSCEI`、`HK.800125→VHSI`、`HK.800700→HSTECH`，其餘明確
  返回 `unresolvable`。同時移除股票候選鏈中那個永遠解析不到的 `IND` 候選。
- `brokery/acceptance/run_kline_matrix.py`：品種 × 券商矩陣驗收（31 項）。期權代碼由富途期權鏈
  （`get_option_expiration_date` → `get_option_chain`）即時取得，不寫死到期日。

### 實測結論（品種與復權）
- **復權只對股票有效**：期貨、指數、期權沒有公司行動，實測各家 `autype="qfq"` 與 `none` 逐根完全相同
  （futu `HK.A50main`、`HK.800000` 各 60 根 0 根有差別；ib `US.10Ymain`、tiger `US..SPX` 同樣 0 根；
  富途期權 11 根亦 0 根）。對照組 `HK.00005` 日線 250 根則有 209 根被調整、最大 5.8118%。故復權參數
  對非股票品種傳哪一種都不影響價格，不需要為它們另設模式。
- 指數代碼已可跨券商使用：`HK.800000` 富途與 IB 共同 60 根、close 完全相同（24211.35）；`US..SPX`
  Tiger 與 IB 完全相同（7811.54）。IB 另可取 `US..VIX`（14.84）、`HK.800700`、`HK.800125`；
  `HK.800121` 在 IB 查無同名合約，明確返回 `unresolvable` 並列出已登記的四隻。
- 各市場的實際範圍：股票——futu/ib/tiger 港美、webull 只餘港（美股 403 未開通）。期貨——futu 只港
  （`HK.A50main`；美股期貨為賬戶行情權限不足）、ib 只美股主連（`US.10Ymain`；HKEX A50 在 IB 查無
  合約）、tiger 未接入、webull 無。指數——futu 只港（富途不提供美股指數）、tiger 只美、ib 見上、
  webull 無。期權——只有 futu（美股為完整序列，港股期權實測只返回當日一根）；IB 未聲明，因其期權需
  完整結構（行權價、到期月、買賣方向），統一代碼無法唯一還原。

### 新增（戶口與資金）
- `Brokery.get_accounts(broker=None, acc_type="all", currency=None)`：四家一律以
  `brokers.base.ACCOUNT_COLUMNS`（15 欄）返回戶口與資金。一律只返回真實且已啟用的戶口，不區分
  real/simulate：IB 的真實與模擬由所連 Gateway 決定、接口本身沒有這個維度，富途與 Tiger 的模擬戶口
  及富途已停用的戶口因此不列入。
- 戶口性質 `acc_type`（`cash`/`margin`）為返回欄位，取值由 `SymbolBroker.acc_types` 聲明、core 統一
  拒绝不支持者；無法判定的帳戶類別（如 IB 個人戶口的 `individual`）原樣返回，不憑空歸類。
- 各家來源：富途 `get_acc_list` + `accinfo_query`；IB `accountSummary`（group `All`，自組 tag 清單，
  因 ib_async 內建清單缺少 `Currency`/`UnrealizedPnL`/`RealizedPnL`）；Tiger `get_managed_accounts`
  （只 `account_type=STANDARD`）+ `get_assets`；Webull `get_account_list` + `get_account_balance`。
- `currency` 一律取各券商原生匯總幣種、不做匯率換算：富途的 `accinfo_query` 必須帶幣種，故取戶口首個
  授權市場的結算幣；IB 的 `Currency` tag 不返回，改以每個金額自帶的結算幣為準，多幣種戶口按幣種各列
  一欄，`core._dedupe_accounts` 的去重鍵因此亦含幣種。
- `brokery/acceptance/run_get_accounts.py`：核對四家格式統一、只列真實且已啟用的戶口、`currency` 有無
  真係填到，以及 `acc_type` / `currency` / `broker` 三個參數在非法或不支持時明確報錯（38 項）。

### 技術變更（IB 主連解析）
- `CONTFUT` 必須帶 `exchange`：本次實測不帶 exchange 的主連查詢一律返回 `No security definition found`
  （ES/ZN/10Y/HSI 皆然），帶上同 root 的 `FUT` 結果中的 exchange 即解析到（同一 root 喺 CME 與 QBALGO
  返回同一 conId）。故主連一律先以 `FUT` 取得掛牌交易所再查 `CONTFUT`：`_collect_futures` 按此順序展開，
  `_best_match` 對無 exchange 的 `CONTFUT` 亦自行補上。
- 影響：`list_futures` 恢復返回主連行（此前 IB 對所有種子 root 的主連一律 0 筆），`US.10Ymain`、
  `US.ESmain`、`US.ZNmain` 等主連 K 線亦恢復可取；`run_kline_matrix.py` 的 `ib US.10Ymain` 一項由
  `unresolvable` 轉為通過。

### 新增（HTTP/WS 閘道與控制台）
- `brokery_api/`（與 `brokery/` 同級）：以 FastAPI 把 Brokery 的全部能力對外為 HTTP 與
  WebSocket，並附一個瀏覽器 dashboard（`ui.html`，ECharts 畫 K 線）。`run.py` 按 `.env` 的
  host/port 起 uvicorn。
- 鑑權為自訂金鑰：`X-API-Key` 或 `Authorization: Bearer` 皆受理；WebSocket 因瀏覽器不能自訂握手
  標頭，另受理 `?api_key=`。未設 `API_KEY` 時 `create_app` 與 `run.py` 一律明確報錯並拒絕
  啟動（閘道會返回戶口與資金）。
- 接口：`/`（控制台）、`/health`、`/capabilities`（欄位契約與各券商能力聲明）、`/logs`、`/codes`、
  `/stocks`、`/futures`、`/indices`、`/all`、`/convert`、`/kline`、`/accounts`、`/brokers`、`WS /stream`。
  一律沿用 Brokery 的 `{"status","data","message"}` 信封；業務失敗仍為 HTTP 200（WS 為 `error`
  事件），原因原樣透傳，不改寫成 HTTP 錯誤碼。
- `frame_payload` 統一 DataFrame→JSON：缺失值（NaN/None/NA/NaT）一律為 `null`、整數與時間戳為整數，
  輸出文本不含非法的 `NaN`；`rows` 可按 `columns` 原樣重建 DataFrame。
- 串流：`WS /stream` 以 `subscribe`/`stop` 協定對應 `stream_kline`，每條 `update` 帶該代碼的完整序列
  （客戶端直接覆蓋，不做本地合併）。每券商同時只容許一條：名額於回報 `subscribed` 前登記，並在执行
  緒真正結束時、推送 `end`/`error` 之前歸還，故收到收尾事件即可立即重新訂閱；`stop` 只標記結束並回報
  `release_in`（`stream_wait` 無停止鉤子，需待 `seconds` 屆滿）。
- 日誌三處輸出（`brokery_api/log.py`）：控制台、`logs/brokery_api.log` 滾動檔、最近若干條的
  記憶體環形緩衝（經 `/logs` 讀，按新到舊）；金鑰一律遮罩。
- 配置全部走 `.env`（`API_HOST`/`_PORT`、`API_KEY`、`_SOURCES`/`_AUTYPE`/`_LOG_*`/`_STREAM_SECONDS`），
  經 `brokery/config.py` 讀取；`Brokery.adapters()` 新增，供閘道讀各券商能力聲明，閘道本身不重複做
  能力校验（不支持仍由 core 統一拒绝）。
- `requirements.txt` 新增 `fastapi`、`uvicorn`、`websockets`、`httpx`。
- `brokery/acceptance/run_api.py`：驗收閘道這一層（金鑰缺失/錯誤、Bearer、WS 鑑權、欄位契約、
  JSON 取值口徑、失敗透傳、串流協定與名額、日誌遮罩）。一律 `sources=()` 並以存根代替串流，故不需
  券商連線、任何環境可重複執行（現 40 項，含 `/brokers`）。

### 新增（券商連線狀態與速度）
- `brokers.base.BROKER_COLUMNS`：`source`/`connected`/`latency_ms`/`accounts`/`detail`/`checked_at`。
- `Brokery.get_brokers(broker=)`：四家並行探測，一律以該欄位返回。探測即一次 `get_accounts(None)`，
  只驗證連線與鑑權、**不需要行情數據權限**，故行情權限缺失或某市場無歷史數據不會被誤報為斷開（實測
  IB 港股歷史數據失靈期間，IB 連線仍探測為 542ms）。連不上時 `connected=False`、`latency_ms` 為
  `NaN`（不以任何數字湊出）並附原因；超過 `.env` 的請求超時即記 `timeout`。無快取、不輪詢。
- `GET /brokers?broker=`；dashboard 頂欄以四家指示顯示可連／斷開與延遲毫秒（懸停顯示原因與戶口數），
  頁面載入時探測一次，其後只由「探測連線」按鈕手動觸發。
- `brokery/acceptance/run_get_brokers.py`（22 項，需四家後端在線）與 `run_api.py` 的 `/brokers` 檢查
  （以存根令 `latency_ms` 的缺失值口徑可離線重複驗證）。

### 修復（dashboard 客戶端）
- `brokery_api/ui.html` 的 `probeBrokers()` 少一個右括號（`esc(r[at('source']))` 應為
  `esc(r[at('source')])`）。內聯腳本因此整段無法解析：頁面載入後零個請求、「連接」按鈕與金鑰記憶全部
  失效、頂欄四家指示不出現，即一個括號造成三個症狀。Node 與 Chromium 的報錯一致（`missing ) after
  argument list`），但只有真瀏覽器能定位到具體行。
- 新增 `brokery/acceptance/run_ui.py`（9 項）：以存根閘道（自配端口，不佔用 `API_PORT`）+ Chromium
  驗收客戶端，正是先前缺少的這一層才讓上述錯誤漏過；未裝 Chromium 即跳過並返回成功。
- 新增依賴 `playwright`（只供驗收；瀏覽器需另執行 `playwright install chromium`）。

### 變更（戶口頁與標的來源標示）
- `get_accounts`：按 `cash`/`margin` 篩選時，詞表外且原樣透傳的戶口性質（IB `AccountType=INDIVIDUAL`
  → `individual`）一律在 `message` 點名該戶口（`acc_type_other:`）。此前該戶口只是靜默消失，結果變成
  「無故少咗一间 IB」而無從得知原因；不過濾時照樣列回，篩選時亦不會憑空出現。
- `brokery_api/ui.html`：新增 `sourceSummary()`（按來源汇总各頁取數，沒有返回者點名；標的頁依
  `/capabilities` 的能力聲明區分「不提供」與「無返回」，兩者含義不同）與 `sourceFirst()`（`source`
  移到第一欄，合併清單必須一眼見到每條出自邊間）；`note()` 對 `status=True` 但 `message` 帶
  「注意：／部分…失敗」者改用警告色（仍算成功）。
- 戶口頁：進入該頁即取一次全部戶口，其後每 10 秒自動刷新（只在该頁可見時才請求，可勾選關閉），
  「取得戶口」手動刷新保留。
- `run_ui.py` 9 → 19 項：存根新增 `/accounts`、`/stocks` 與 `capabilities.adapters.capabilities`，
  以真瀏覽器驗自動刷新（10 秒內再取一次、取消後不再取）與來源汇总的三種狀態（有返回／無返回／不提供）。
- `run_get_accounts.py` 38 → 39 項：IB 的 `individual` 在 `acc_type=margin` 篩選時必須點名該戶口，
  實測返回 `no_account: acc_type_other: ib 的 U11976982 為 individual（非 cash/margin），未列入`。

### 變更（讀取提示、戶口不分來源、標的分四區）
- `brokery_api/ui.html`：新增 `loading()`（請求進行時以強調色顯示「讀取…中…」，較快的請求延後約
  0.4 秒才顯示以免閃爍）與 `withBusy()`（請求期間禁用觸發按鈕，防止重復送出）；K 線、戶口、標的、
  日誌、探測五條取數路徑一律套用。此前只能靠結果表格突然變化判斷有無在取數。
- 標的頁：即時清單改為按來源分四區同時顯示（`buildPanels()` 先建四區並各自顯示讀取中，`filterCodes()`
  按 `source` 分組填充），一次點擊即四區一起返回 —— 後端本来就是一次向各家取齊，不需逐間點。各區
  如實顯示「N 條／無返回／不提供此清單」（後兩者含義不同，前者依 `/capabilities` 判定）；區內以
  `dropSource()` 去掉重複的 `source` 欄。離線 CODES 不涉及即時取數，仍以單一表格顯示。
- 戶口頁：移除「來源」選擇，一律一次取四家全部戶口（請求不带 `broker` 參數）。四家同屏先對照先決定，
  比逐間點更合理。
- `run_ui.py` 19 → 27 項：存根對 `/stocks` 故意延遲 0.8 秒以觀察讀取提示；新增四區同時填充、三種
  區內狀態、區內不重複 `source` 欄、離線 CODES 不分區等檢查。

### 新增（四家皆有標的清單）
- Tiger 適配器：`list_stocks`（`get_symbol_names` 按市場一次取全，實測 HK 3,763／US 14,609；接口不附
  掛牌場所，`exchange` 一律空字串）、`list_futures`（`get_future_exchanges` + `get_future_contracts`
  原生批量，實測 649 條且含種子外的 MEUR／ZM／XW 等，不需種子表；`trade=False` 者不列）、
  `list_indices`（符號表中句點前綴的 4 隻美股指數）。
- Webull 適配器：`list_stocks`（`list_instruments` 按 `category` + `sub_category` 分頁，只取
  `status=OC`，實測 HK 3,170／US 12,306；429 屬限速故等待後重試）、`list_futures`（無批量接口，
  按種子 root 逐個 `get_futures_instrument(code=root)` 展開，實測 41 條／14 個 root；只掛近月、無
  主連概念，故不生成 `main` 行；場所代號 XCME／XCBT／XCEC／XNYM／HFE 歸一到 `codes` 詞表，否則
  `market_of()` 無法判定市場）。
- 能力聲明一律按實測、不湊齊對稱：futu 與 tiger 為 STOCK/FUTURE/INDEX；**ib 不含 STOCK**（空 symbol
  的 `reqContractDetails` 150s 無回應、`reqMatchingSymbols` 只為 top-N 且混入 BOND、`reqScannerData`
  error 162）；**webull 不含 INDEX**（接口沒有指數類別）。未聲明的品種由 `core._gather` 統一返回
  `no_source`，適配器不自行返回空表冒充支援。
- `brokers/base.py`：`COLUMNS` 註釋明確寫出字串欄無值一律為空字串（不出現 NaN），嚴禁為湊齊欄位造數。
- `brokery_api/ui.html`：離線 CODES 的單一表格由 `#c-merged` 改為 `#c-raw`（即時清單仍只按來源分四區，
  不另設跨來源的合併表格）。
- 新增 `run_list_symbols.py`：四家 × 三品種逐項核對（能力聲明與實測一致、欄位與順序固定、字串欄無
  NaN、`code` 為 `<市場>.<符號>`、期貨 `expiry` 一律為空或 `YYYYMM(DD)`、未聲明品種返回 `no_source`、
  跨券商合併同一合約不重複列）。`run_ui.py` 27 → 29 項（真實能力存根、離線 CODES 以單一表格顯示）。
- 實測更正：以 root 表達合約的三家（IB／Tiger／Webull）同一 `code` 會跨多個到期月，故期貨行的唯一鍵
  為 `code` + `expiry`；跨券商合併去重後某家可以完全不出現（Webull 的 ES 兩個月與 Tiger 逐欄相同，
  `message` 仍為 `ok`），這是去重而非失敗。

### 新增（量化交易 Web GUI）
- `brokery_gui/`（與 `brokery/`、`brokery_api/` 同級）：FastAPI 頁面應用，上方菜單目前只有一項
  「戶口清單」。`run.py` 按 `.env` 的 `GUI_HOST`/`GUI_PORT`（預設 `127.0.0.1:8282`）起 uvicorn。
- **GUI 不連券商，只轉發閘道**：`/api/accounts` 以 `X-API-Key` 請求閘道的 `/accounts` 並原樣透傳
  信封。決定性理由在進程層面：閘道進程已持有各券商連線，IB 只容許一個 client id（先前實測
  `clientId 99 already in use` → Error 326），GUI 自己再建一份連線即互相搶佔，兩邊都取不到數。金鑰
  只在 GUI 服務端使用，不出現在頁面與瀏覽器中。
- 失敗口徑與閘道一致：閘道不可達、金鑰不符（4xx）、回應不是信封時，一律由 GUI 構造
  `status=False` 並點名原因（`gateway_unreachable:`／`gateway_http_403:`），不變成 HTTP 500；
  轉發超時取 60s，必須高於閘道內部最慢的兜底（IB 連線 40s），否則用戶見到的是 GUI 超時而不是券商
  實際給出的原因。未設 `API_KEY` 時 `create_app` 即拒絕建立應用。
- `brokery_api/log.py`：`setup_logging()` 新增 `logger_name`/`file_name` 參數（預設不變），GUI 以
  logger `brokery.gui` 寫 `logs/brokery_gui.log`。兩個進程共用同一個 `RotatingFileHandler` 檔案時，
  滾動會令其中一方的句柄指向已被改名的檔案，故必須分開寫。
- `home.html`：表格欄位與順序即接口返回的 `ACCOUNT_COLUMNS`（不另設欄位），缺失值顯示破折號、資金欄
  千分位兩位小數、按實際返回的行統計各來源戶口數（不會憑空列出一間「0 個戶口」）、`message` 帶
  「注意」時以警告色顯示。
- `brokery/acceptance/run_gui.py`（18 項）：存根閘道 + 真 HTTP（系統分配端口，不佔用 `API_PORT`）+
  Chromium。核對轉發逐字透傳信封與 `X-API-Key`、頁面不含金鑰、金鑰不符與閘道不可達均明確報錯、
  未設金鑰拒绝啟動；再以真瀏覽器核對菜單只有一項、進入即取一次、欄位即 `ACCOUNT_COLUMNS`、千分位與
  破折號、來源統計與警告色、「重新整理」再取一次。不需券商連線。
- 實測（真閘道 + 真瀏覽器）：`/api/accounts` 返回 6 個戶口（futu 2／ib 1／tiger 1／webull 2），15 欄
  與 `ACCOUNT_COLUMNS` 逐欄一致；頁面頂欄顯示「已連接閘道」、四枚來源統計、IB 缺失的三欄為破折號。

### 新增（一次過啟動閘道與 GUI）
- `run_all.py`（項目根目錄）：以 `sys.executable` 直接啟動 `brokery_api/run.py` 與 `brokery_gui/run.py`
  兩個進程（不經 shell，Windows / Ubuntu / Docker 一致）。其中一個先結束即停止另一個並原樣返回其退出碼
  （未設 `API_KEY`、端口已被佔用均會這樣反映，不會留半個系統在背景），Ctrl+C 一併停止；收尾先
  `terminate()`，最多等 10 秒才 `kill()`，不無限等待。
- 本檔刻意不 import `brokery`：連 `brokery.config` 都會經 `brokery/__init__.py` 載入 futu / ib_async /
  tigeropen，而 futu SDK 在匯入時即把 SIGINT 換成自己的 `quit_handler`（直接結束進程、退出碼 0），令
  `except KeyboardInterrupt` 與後面的收尾完全不會執行，兩個子進程變成孤兒。
- `brokery/acceptance/run_launch.py`（7 項）：以存根命令代替兩個入口，核對兩個同時啟動、先結束者停止
  另一個並返回其退出碼、兩者正常結束返回 0、Ctrl+C 一併停止兩個、預設命令即兩個既有入口、啟動器不引入
  券商 SDK。不需券商連線，亦不真的啟動服務；需 `psutil`（已列入 `requirements.txt`）。
- 實測（真 `run_all.py`、空 `API_SOURCES`、系統分配端口）：兩個端口同時回應、`/health` 為真、GUI 頁面含
  「戶口清單」、GUI 經剛啟動的閘道取數（`no_account`，屬業務結果而非 HTTP 錯誤）；Ctrl+C 後兩個端口均釋放。
  Windows 以控制台事件結束 Python 進程一律返回 `0xC000013A`（STATUS_CONTROL_C_EXIT），即使進程自己已捕獲
  `KeyboardInterrupt`，屬平台行為而非收尾失敗，故實測接受 `0` 與 `0xC000013A` 兩種。

### 新增（GUI「標的列表」頁；清單可按券商與市場取）
- `core`：`list_stocks` / `list_futures` / `list_indices` 新增 `broker` 與 `markets` 兩個參數，與
  `get_kline`／`get_accounts` 同一口徑。`broker` 指定只向一家取，能力閘由適配器聲明、`core` 統一拒绝：
  未啟用即 `unknown_source`，該家未聲明該品種即 `type_unsupported`（並說明它只提供什麼），一律明確報錯而
  不靜默改用別家湊數。`markets` 只過濾返回行的 `market`，用於沒有市場參數的接口（期貨／指數）；股票清單
  的市場仍由適配器自己處理，這一層只確保返回的確實是所請求的市場。取到了但全部不在指定市場即 `empty_list`，
  不以空表冒充成功。
- **修正**：`list_stocks(markets=None)` 會因 `tuple(m.upper() for m in None)` 拋 `TypeError`。閘道的
  `GET /stocks` 不帶 `markets` 時必然傳 `None`，故控制台「標的清單全部取不到、一直讀取中」由此而來
  （`api_failed: TypeError`，從不返回可用資料）。現省略該參數即用 `DEFAULT_STOCK_MARKETS`。
- 閘道：`/stocks`、`/futures`、`/indices` 接受 `markets`（逗號分隔，大寫為統一前綴）與 `broker`，原樣傳入
  `core`；能力閘與空清單一律由 `core` 決定，閘道不自行改選別家。
- `brokery_gui`：菜單加第二項「標的列表」。`/api/symbols` 按類型（股票／期貨／指數）轉到對應的清單接口，
  市場與券商原樣傳為 `markets`／`broker`，類型不認識即 `unknown_kind`；`/api/capabilities` 轉發能力聲明，
  供頁面填充券商選項（頁面不硬寫券商名單）。不提供該品種的券商在選項上標註原因且不可選，用戶不必按了就
  知道會 `type_unsupported`。市場選項只由實際返回行的 `market` 填充，不憑空給出前綴；轉類型時重設為全部
  市場，選項再由新品种重建。默認券商為 futu。
- `brokery/acceptance/run_list_filter.py`（10 項）：以進程內存根券商驗收上述兩個參數的調度口徑
  （`unknown_source`／`type_unsupported`／`markets` 按行過濾／`empty_list`／省略 markets 用預設市場／一家
  失敗仍返回別家資料），不需任何連線。`run_api.py` 增至 47 項（參數透傳與 `markets=None` 不再拋異常的
  回歸檢查）、`run_gui.py` 增至 30 項（類型與市場/券商的轉發、券商選項由能力聲明填充且默認 futu、市場選項
  只由返回值填充、轉類型即轉接口並重設市場）。

### 更名（`brokery_gui` → `brokery_webui`）
- 目錄與套件、啟動入口（`brokery_webui/run.py`）、`run_all.py` 的預設入口、日誌檔
  （`logs/brokery_webui.log`，logger `brokery.webui`）與驗收腳本（`run_webui.py`）一併改名；行為與接口不變。
- `.env` 的 `GUI_HOST`/`GUI_PORT` 與 `config.py` 的 `gui_host`/`gui_port` 未改，既有 `.env` 不需改動作。

### 量化交易桌面 GUI（`brokery_gui`，PySide6）
- 新增與 `brokery_webui` 同功能的桌面窗口：兩個分頁（戶口清單、標的列表，篩選為類型／市場／券商，默認富途）。
  只經 `brokery_api` 閘道取數，不連券商、不另設欄位（表格欄位一律由返回的 `columns` 決定），失敗口徑與閘道一致。
  取數在 `QThread` 背景執行，界面不因券商連線（IB 可達 40s）而凍結。
- 界面與文字分離：三個 `.ui` 檔在運行時由 QUiLoader 載入，檔內不含任何文字；顯示文字一律按鍵取自
  `locales/<語言>.json`。繁體中文／简体中文／English 各一個語言檔（鍵集合一致），頂欄即時切換、不需重建窗口，
  缺譯時返回鍵名本身。
- 啟動即崩潰（Windows 0xC0000005、窗口不顯示）：頂層窗口無父，`run.py` 若不持有 `DesktopGui` 引用即被解構，
  連同以其為父的背景 `QThread` 一併被拆，事件循環 abort（faulthandler 顯示無 Python 幀）。啟動腳本改為持有引用。
- `requirements.txt` 加 `PySide6>=6.6`；新增 `brokery/acceptance/run_gui.py`（29 項），以存根閘道 + Qt 離屏
  （`QT_QPA_PLATFORM=offscreen`）驗收，不需券商連線亦不需顯示器；其中一項直接啟動 `brokery_gui/run.py` 核對窗口會存活。
- 只在 IDE（PyCharm）崩潰、CMD 正常：PyCharm 注入的 plot 後端 `sitecustomize` 喺解釋器啟動階段已 import
  pandas → pyarrow，pyarrow 17 自帶舊版 `msvcp140.dll` 先入場，其後 `Qt6Core.dll` 用咗呢份舊 VC++ runtime 即
  access violation（0xC0000005，無 Python 幀）。pyarrow 26 不再附該 DLL，故 `requirements.txt` 底線改為
  `pyarrow>=26.0`（全局環境同步升到 26.0.0）。順序排喺 `run.py` 內救唔返——IDE 已喺我方代碼之前 load pyarrow。

### 新增（連券商功能的原生格式 `raw=True`）
- `brokers/base.py`：`SymbolBroker` 的七個連券商方法一律加 keyword-only `raw=False`；新增 `native_columns(rows)`
  （按各列鍵的首見順序，不排序、不憑空補欄位）與 `NativeBars(count, time_field)`（raw 模式的串流合併，對外語義與
  `BarMerger` 一致：只在最新一根有變化時回報、只留最近 count 根、按原生時間升序；各券商時間欄位形態不同，故
  `_bar_sort_key` 把數字與文字各自成組）。本層仍不 import pandas（DataFrame 只在 core 構造）。
- `core.py`：新增 `_native_frame(rows)`；`_ok`／`_fail`／`_accounts_ok`／`_accounts_fail` 在 raw 下以原生欄位構表，
  失敗時空表不帶欄位（原生欄位無從得知）。raw 會跳過只認統一欄位的後處理——`dedupe_rows`、按 `market` 的行過濾、
  `_dedupe_accounts`、串流的 `(code, ts)` 排序；取數範圍改由市場參數原樣交給適配器、期貨／指數的種子以
  `_seeds_in_market` 過濾、幣種過濾由各適配器按原生欄位執行。`get_accounts` 在 raw 下明確要求 `acc_type` 一律
  `bad_acc_type`（原生記錄無該欄位，不能假裝已過濾）。能力閘（`unknown_source`／`type_unsupported`）不受 raw 影響。
- 四家適配器：`raw=True` 時原樣返回上游的鍵與值，不做欄位映射與時間轉換（時間欄位為各家自己的寫法）。適配器簽名
  變更的附帶要求：任何 `SymbolBroker` 子類重寫這七個方法時必須接受 `raw=`，否則被 core 包成失敗信封。
- `brokery_api`：六個取數端點加 `raw: bool = False`（受理 `1/true/yes/on`），`WS /stream` 的訂閱訊息可帶
  `"raw":true`；`StreamWorker` 按 raw 透傳。修復 `_on_update` 把推送的 `list[dict]` 當 DataFrame 處理（四家推送一律
  為 dict 列表），改以新增的 `rows_payload()` 產生 `{"columns","rows"}`。
- `brokery_gui`：「標的列表」改為上下兩張表——上方為 raw（欄位即閘道返回的該券商自帶欄位）、下方為統一格式；同一
  篩選條件先取統一格式、再同參數 `raw=1` 順序取兩次（同一閘道持有各券商連線，IB 只容許一個 client id，故不併發），
  新增 `_symbols_seq` 使舊回應不會蓋過已改變的篩選條件，兩表各自顯示自己的失敗原因。`ui/symbols_page.ui` 只加控件
  （仍不含任何文字），三個語言檔各加 `symbols.raw_title`／`symbols.unified_title`。
- 新增 `brokery/acceptance/run_raw_frames.py`（37 項，存根適配器，不需任何連線）；既有驗收各加 raw 對照：
  `run_list_filter.py`（10→14）、`run_list_symbols.py`（四家可達時 142 項）、`run_get_accounts.py`（IB 可達時 59 項）、
  `run_kline_matrix.py`（四家可達時 48 項）、`run_api.py`（40→54）、`run_gui.py`（29→33）。項數隨來源可達性浮動，
  連不上者整項跳過並明確報錯。
- 實測：同一請求在 raw 與統一格式下的根數與收市價逐根相同（最大相差 0.0）。原生欄位為——富途 K 線
  `code,name,time_key,open,close,high,low,volume,turnover,pe_ratio,turnover_rate,last_close`（`code` 屬上游自帶，
  一律保留）、Tiger `symbol,next_page_token,time,volume,open,close,high,low`、Webull
  `time,open,close,high,low,volume,trading_session`、IB 以 `date` 為時間欄；富途戶口記錄約 80 欄且自帶數字型的
  `acc_type`。Webull 的憑證只開通 HK 行情，故其 K 線對照一律以港股代碼實測（美股為 `market_data_not_subscribed`）。

### 變更（統一格式去掉 `expiry`／`raw_code`；標的列表可選券商）
- `brokers/base.COLUMNS` 由 10 欄減為 8 欄（`code,name,market,symbol,symbol_type,currency,exchange,source`），
  `make_row` 同步去掉兩個引數。券商原生標識（富途 `code`、Webull `instrument_id` 等）只在 `raw=True` 的原生格式
  中出現。
- 去掉 `expiry` 會令 IB／Tiger／Webull 同一 root 的各月份塌成同一個代碼（呢三家原本只靠 `expiry` 區月），故到期月
  一律寫進 `symbol`／`code`：IB 為 root + 最後交易日（`US.ES20261218`）、Tiger／Webull 為 root + `contract_month`
  （`US.ES202512`／`US.ES202612`），與富途既有的寫法（`US.10Y2609`、主連 `main`/`current`）一致。各家月份寫法與
  產品代碼本來不同，跨券商仍不憑空對齊。`dedupe_rows` 的鍵相应改為 market + symbol_type + symbol（`code` 即合約身份）。
- IB 的 `convert` 對帶月份的代碼原樣返回該月份（不再只把月份作 IB 的合約參數），使清單所出的代碼可原樣回查。
- 標的列表選唔到券商：`/capabilities` 返回的是 `symbol_type` 嘅大寫常量（`STOCK/FUTURE/INDEX`），而兩個界面嘅
  kind 值為細寫，`kind in caps` 恒為 False → 所有券商選項被標為不可選。兩個界面改為顯式的 kind→capability 對映
  （`brokery_gui/app.py` 的 `KIND_CAPABILITIES`、`brokery_webui/home.html` 的 `KIND_CAPABILITY`）；`brokery_api/ui.html`
  本來已正確。存根閘道（`run_gui.py`／`run_webui.py`）嘅能力聲明原本用細寫，正好掩蓋呢個錯誤，已改為與真實閘道一致。
- 驗收由「有冇到期月欄」改為「代碼係咪唯一標識合約」：`run_list_symbols.py` 新增 `carries_contract()`（主連後綴或
  結尾 4–8 位月份），核對 `code` 無重複、期貨符號已含主連後綴或到期月、股票／指數不帶到期月寫法。

### 新增（離線 CODES 的更新機制）
- 前提以實測定調：讀一份快照 0.03s（38,569 條），向富途重拉港美全量約 6s，相差約 250 倍。故搜尋與離線檢視一律
  讀快照，重拉唔放進任何請求路徑；而快照往往是唯一嘅離線副本，更新時先至要考虑點樣唔搞壞佢。
- `store.save_frame` 改為原子寫入：先寫 `<name>.parquet.tmp` 再 `os.replace`，中途失敗唔會留下半檔；被覆蓋嘅舊檔
  保留為 `<name>.prev.parquet`（只一份）。新增 `prev_path()`、`update_meta(**fields)`、`meta_age()`（非有限值視為
  無存放時間）、`meta_stale()`。
- `core.refresh_codes(markets=None, *, force=False)`：重拉並覆蓋快照。三層防護——
  **縮細防護**按 `symbol_type` 逐個比較，任何品種少於原本嘅 `CODES_MIN_KEEP_RATIO`（0.9）即拒絕覆蓋（只拉部分市場
  唔應該把全量快照削走一半，故不带 `markets` 即全量係唯一正常用法）；**沿用舊快照**：某品種本次取唔到（實測指數
  清單被拒）即沿用該品種舊快照嘅行，其餘照常更新；**失敗留痕**：原因記進 meta 嘅 `last_refresh_error`。
  返回仍為信封，`data` 為一行元資料（欄位即 `CODES_META_COLUMNS`），`message` 為差額報告（各品種增減與沿用說明）。
  單靠縮細防護會令呢度永遠更新唔到（指數一直取唔到），所以兩層要一齊先至行得通。
- `core.get_code_meta()` 返回一行 DataFrame（`age_seconds`、`stale`、`last_refresh_error` 等），行而唔係 dict，
  先至塞得落信封嘅 `frame_payload`。過舊界限讀 `.env` 嘅 `CODES_MAX_AGE_HOURS`（預設 24）。
- 閘道新增 `GET /codes/meta`、`GET /codes/refresh`（保持只有 GET）；`auto_refresh_codes` 只在啟動時發現快照已過舊
  先至喺背景线程重拉一次，唔阻塞啟動。Web UI 以 `/api/codes/meta`、`/api/codes/refresh` 原樣轉發，唔自行解讀。
- 三個界面一律另列一行顯示快照的行數與距今時間，並有「更新」按鈕；呢行同即時取數嘅按來源統計分開，快照狀態唔會
  混入各來源嘅條數。過舊屬警告（`COLOR_WARN` / `.msg.warn`）而唔係錯誤：已存放嘅資料仍然可用。只有
  `brokery_api/ui.html` 會以自由文字搜尋離線快照，故只有佢喺「零結果且快照過舊」時提示按「更新 CODES」。
- 驗收：新增 `run_codes_refresh.py`（22 項，以存根代替 `list_all`，用 `acceptance_` 前綴嘅臨時資料集，跑完即刪）；
  `run_api.py` 加 `/codes/meta`、`/codes/refresh`（58 項）、`run_ui.py` 加快照行與更新按鈕與零結果提示（33 項）、
  `run_webui.py` 加轉發與快照行（36 項）、`run_gui.py` 加快照行與警告色與語言切換（38 項）。三個界面嘅存根一律給
  一筆**過舊且上次更新失敗**嘅快照（90,000 秒 → 「1 天前」），因為容易出事嘅係警告渲染而唔係正常路徑。
- 測試揪出兩個真實界面缺陷（改界面而唔放寬測試）：兩個 HTML 嘅 `ageText()` 用「日前」而 GUI 語言檔用「天前」，
  統一為「天前」；`ui.html` 嘅 `refreshCodes()` 先 `note()` 再 `loadCodes()`，更新報告即時被重讀表格嘅訊息蓋掉，
  改為重讀後把報告還原返上去。
- 三個 `.ui` 檔仍不含任何文字、三種語言鍵集合仍一致（新增 `symbols.codes_*` 與 `age.*` 十個鍵）。

### 變更（離線 CODES 按券商各存一檔；自動更新改為以秒為單位）
- `store.CODES_DATASET`（單檔 `futu_codes`）改為 `store.codes_dataset(broker)`，即每家一檔 `<broker>_codes`。
  原因有兩：各家的標識系統不同（IB 以 conId/ISIN 為主），混進同一檔會互相污染；而各家能力不同，單檔無法逐家做縮細防護。
  既有 `futu_codes.parquet` 正好等於新方案為 futu 產生嘅檔名，故唔需要遷移。
- `get_code()` / `get_code_meta()` / `refresh_codes()` 嘅參數由資料集名改為 `broker`（預設 `CODES_SOURCE`）；
  閘道 `/codes`、`/codes/meta`、`/codes/refresh` 一律新增 `?broker=`，Web UI 新增 `/api/codes` 轉發（一律帶當前所選券商）。
  `CODES_SOURCE` 保留，語義收窄為「唔指定時嘅券商」同唯一喺啟動時自動重拉嘅一檔，其餘各家只由用戶喺界面觸發。
- 縮細防護改為只與**同一券商**嘅上一份快照比較；快照內容完全由該適配器聲明嘅 `capabilities` 決定
  （`ib_codes` 只有期貨與指數、`webull_codes` 只有股票與期貨屬正常），唔為湊齊而造數。
- 三個界面嘅標的頁新增「讀取離線 CODES／更新離線 CODES」兩個按鈕，一律作用於當前所選券商；換券商即改讀該家那一檔。
- 自動更新由固定 10 秒改為可填秒數，**預設 0 即完全唔自動請求**。三個界面共用同一個 1 秒 tick：讀當前頁、
  讀秒數（0 即返回）、`inFlight > 0` 即跳過、以 `lastAuto[頁]` 計時；進入該頁或修改秒數即重置計時。
  標的頁嘅定時更新預設只重讀離線快照（0.03s，唔產生券商請求），另有「自動向券商重拉」開關（預設關閉）。
- 驗收：`run_codes_refresh.py` 22 → 30 項（兩家各一檔互不覆蓋、縮細防護逐家比較）；`run_ui.py` 33 → 42、
  `run_webui.py` 36 → 51、`run_gui.py` 38 → 52（存根按券商給唔同行數，界面顯示錯券商即即刻失敗）；
  `run_api.py` 自建 `apitest` 臨時快照並喺 `finally` 清理，以證兩檔互不覆蓋。
- 語言檔三份鍵集合仍一致（現為 44 個，新增 `accounts.auto_interval`、`symbols.auto_interval`、`symbols.live_refresh`
  與 `symbols.codes_load*`）；`.ui` 檔仍不含任何文字。

### 新增（全域券商開關與共用圖表層；四個 K 線頁面）
- 券商開關喜好 `brokery/prefs.py`：`<data_dir>/broker_prefs.json`（`pathlib`，跨平台）**只記被停用嘅家**，
  寫入為原子（`.tmp` → `os.replace`）；檔不存在或內容不可讀即全部生效，故唔需要遷移。只記差額而唔記全部名單，
  係為免 `.env API_SOURCES` 一改之後檔即變舊。三個界面共用同一份檔。
- `Brokery.__init__` 新增 `disabled=`（喜好由調用方讀檔後傳入，`core` 唔自己讀檔，故唔傳即照 `.env` 取齊全部，
  逐家循環嘅驗收與離線分析不受界面開關影響）。生效集合 = `API_SOURCES` − `disabled`，被剔除者記喺 `_disabled`。新增 `get_broker_prefs()`（欄位 `PREF_COLUMNS`，
  一律列出全部券商，未配置者 `configured=False`）與 `set_broker_enabled()`（即時套用到現有實例，唔使重建；
  持久化由閘道負責）。
- 失敗語義分清：`_source_error()` 對已停用者返回 `broker_disabled:`，根本唔喺 `API_SOURCES` 者仍為
  `unknown_source:`，連不上者仍為該家嘅連線錯誤；全部停用時為 `no_source:` 並點名被停用者，唔再砌出
  「已啟用的券商（）」呢種空列表。
- **冇喺任何界面或調度處逐個加 if**：多券商路徑（`list_all`、`get_accounts(broker=None)`、`get_brokers()`）本來就
  iterate 生效集合，`/capabilities` 亦只列生效適配器，所以被停用者自動唔會被任何動作經過，三個界面嘅券商下拉框
  自動更新。
- 閘道新增 `/brokers/prefs`（讀）與 `/brokers/prefs/update?enabled=`（寫，一次交齊完整名單，省略參數即全部停用；
  名字原樣保留，唔經大寫化）；`/capabilities` 新增 `ktypes`（即 `BAR_MINUTES`）；`/health` 回報生效來源與喜好檔路徑；
  `/static/{name}` 只放行白名單兩檔且唔需要金鑰；`auto_refresh_codes` 開頭先查 `CODES_SOURCE in brokery.sources()`。
- 共用圖表層：`brokery/static/chart.js`（`window.BrokeryChart`：`option`／`render`／`store`／`overlays.register`／
  `timeText`）+ 本地 vendor `echarts.min.js`（**取代 CDN**，GUI 與 Docker 離線照樣畫到圖）+ `chart_host.html`；
  `brokery/chart.py` 為唯一 Python 入口（`payload`／`render_js`／`frame`／`overlay_rows`／`static_file`／`BarStore`）。
  閘道 dashboard、Web UI 與桌面 GUI 載入嘅係同一個檔案，故任何指標喺三處完全一樣。
- **疊加指標係資料唔係圖**：指標由 pandas 算出行，欄位即 `brokers/base.OVERLAY_COLUMNS`（`code/kind/name/
  start_ts/end_ts/start_price/end_price/side`），渲染層只按 `kind` 分派（內置 `zone`／`line`），新指標只
  `overlays.register(kind, fn)`。日後嘅自定義指標（例如 ICT order block）只寫運算同一個掛點，三處自動一致。
- x 軸一律為原始 `ts`（UTC 秒），時間文字只由 formatter 產生——呢個係疊加指標能同 bar 對齊嘅前提。
- 序列合併規則三處同一口徑（`chart.BarStore` 與 `chart.js` 嘅 `store()`）：key=(code,ts)、同 `ts` 以新到者覆蓋、
  每個代碼只保留最新 N 根、內部一律升序。串流 `update` 只帶最近 `count` 根，直接取代會將 1000 根縮返最近幾根。
  「最新喺最上」一律只屬顯示層（`rowsDesc()`／`desc()`），`core` 與圖表仍為升序，故跨券商對齊同指標計算唔受界面排序影響。
- 桌面 GUI：`brokery_gui/stream.py`（`QWebSocket` 連 `/stream`，金鑰放 query string，因為 `QWebSocket` 唔可以設握手
  header；只翻譯協定，不含業務）、`brokery_gui/chart_view.py`（惰性建立，起唔到即記 `webengine_missing:`／
  `host_load_failed:`／`chart_js_missing:` 而唔係留空白）、四個新 `.ui`；六個分頁以 object name 辨認，唔再按 index 硬編碼。
- **修復（GUI 背景取數會崩潰）**：PySide6 中連到普通可呼叫物件嘅信號會喺**發射**執行緒執行，而 `GatewayWorker.finished`
  喺 worker `QThread` 發射，喺嗰度直接碰 `QWebEnginePage.runJavaScript` 即 `Windows fatal exception: code 0x80000003`。
  改由一個屬主執行緒嘅 `ReplyRelay`（QObject）轉接，靠 Qt 嘅佇列連線交回 GUI 執行緒。
- Web UI 新增 `/api/kline`、`/api/brokers/prefs`（讀寫）、`/static/chart.js` 與 `/static/echarts.min.js`（同一份檔）、
  `WebSocket /ws/stream`（以 `websockets` 連上游，雙向原樣透傳；金鑰仍然只在服務端，唔落 browser）。
- 驗收：新增 `run_broker_prefs.py`（18 項，存根適配器，唔使連線）與 `run_chart_spec.py`（17 項）；
  `run_api.py` 62 → 80、`run_ui.py` 42 → 47、`run_gui.py` 52 → 84、`run_codes_refresh.py` 30 → 31（被停用者不做背景
  自動更新）；`run_webui.py` 51 → 79（重寫時一度丟失戶口／標的／離線 CODES／自動更新嘅覆蓋，已照今日嘅契約補回）。
- 語言檔三份鍵集合仍一致（44 → 73 個）；七個 `.ui` 檔仍不含任何文字。

### 新增（K 線圖（多週期 3×3）、圖表模組化與多週期串流）
- 週期順序得返一份定義：`brokers/base.KTYPE_ORDER = tuple(BAR_MINUTES)`（`1m/3m/5m/15m/30m/60m/day/week/month`
  九個），`/capabilities` 照呢份返回，界面唔准自排、唔准憑空補。
- 可並行的週期由適配器聲明：`SymbolBroker.stream_ktypes`（futu 為全部九個、IB 為其 `IB_BAR_SIZE` 表、
  tiger/webull 只聲明 `1m`）。驗收與界面一律照呢份取名單，唔自己寫死。
- **futu 同一條連線容許多個 ktype 並行**：`_KlinePushRouter`（`CurKlineHandlerBase`）按推送行上的 `k_type`
  分派俾各 `_KlineSink`（推送幀本身包含全部已訂閱的週期），`_streams` 引用計數決定 start/stop，同週期的第二份
  明確返回 `stream_busy`。順手修 `connect()` 嘅 race：三條執行緒同時首次取數會建出三個 `OpenQuoteContext`，
  現以 `_conn_lock` 使 `connect()` 冪等，只建一條。
- 閘道 `/stream` 名額由「每券商一名額」改為按**（券商, 週期）** 計（九個週期今日先至訂閱到，舊名額第 2 個即
  `stream_busy`）；一條 WS 容許多個訂閱與多個 `stop`，`stop` 的 `broker`/`ktype` 皆可省略且只收該部分，
  `subscribed`/`update`/`closed`/`error` 一律帶 `broker`/`ktype`。
  **修復**：`stop` 冇由本連接嘅 `workers` 表除名 → 已指示停止但執行緒未收尾嘅訂閱會被第二次 `stop` 重複發
  `closed`（實測 5m 出現兩次）；現先除名，名額仍由執行緒收尾時歸還。
- **圖表模組化**：`BrokeryChart.create(el, opts)` 一格一實例（`update`/`overlays`/`reset`/`destroy`，
  `opts.compact` 供小格），各自記自己嘅縮放範圍，故串流 `update` 唔會跳返原位；`render()`／`resizeAll()`
  變為舊簽名嘅外殼，三張既有頁面唔改調用口徑。縮放、平移、雙擊復原與現價水平線一律由呢份規格提供，界面唔寫一行。
  - **實測限制**：ECharts 嘅 `zoomOnMouseWheel: true` 唔理修飾鍵（Shift+滾輪會連 X 軸一齊縮，單軸縮小失效），
    且 zrender 先喺容器註冊 wheel 並切斷後續 listener。故 `dataZoom` 一律關滾輪，由實例喺 **capture** 階段按
    修飾鍵 `dispatchAction`（滾輪只縮 X 軸、Shift+滾輪只縮 Y 軸）。現價線一律取序列最後一根嘅收市價，故跟住
    串流走，界面唔使另外傳值（無資料時唔畫）。
- 多週期載體頁 `brokery/static/chart_grid.html`（`BrokeryGrid.build/pick/takePicks/set/note`，3×3、每格以水平
  按鈕自選週期、頁內冇任何 `select`）；Python 側為 `chart.grid_page()`／`grid_js(index, frame, ktype, overlays)`／
  `grid_note_js(index, text)`，overlays 與單張圖同一格式，故自訂指標九格一致。載體頁本身唔含文字，提示文案一律
  由界面嘅語言鍵提供。
- 桌面 GUI：`brokery_gui/grid_view.py`（`QWebEngineView` 載入載體頁，`GridView.build/set_cell/note` + `picked`
  信號）與 `ui/kline_grid_page.ui`（刻意冇 `ktypeCombo`，週期喺格內選）。
  **唔用 QWebChannel**：offscreen 環境下載入 `qrc:///qtwebchannel/qwebchannel.js` 即令 WebEngine segfault
  （`setWebChannel` 本身冇事），故格內點選由 `BrokeryGrid.takePicks()` 以短周期輪詢交回 Qt。
- `brokery_gui/stream.py` 由「一條連接一個訂閱」改為一條連接多個訂閱：`subscribe()` 未連接時排隊、連接後補發，
  `unsubscribe(broker, ktype)`，`_open` 為剩餘嘅 (broker, ktype) 且只喺空時先 `_finish()`，`stop()` 發裸
  `{"action":"stop"}`。順手修真 bug：`active` 用咗 `QAbstractSocket.Unconnected`（呢個 PySide6 冇呢名，要
  `UnconnectedState`），未連接時給 `isValid()` 短路所以一直冇爆。
- **連線數嘅實測結論**：券商端嘅訂閱數唔可以少過週期數（每個週期係上游一份訂閱），但可共用同一條券商連線；
  真正會排塞嘅係界面→閘道嗰一层——瀏覽器對同一來源只得約 6 條 HTTP/1.1 併發連線，九條 WS 會排到塞住，
  故九個週期只開**一條** `/stream`（多訂閱、`update` 帶 `ktype`）。改一格週期即只重取那一格、並只退該週期嘅名額。
- `/static/{name}` 由「白名單兩檔」改為只准取 `brokery/static/` 內嘅檔案（解析後嘅路徑不可走出該目錄，否則
  明確 404 `static_missing`）——載體頁需要第三個檔案，逐個加白名單一定會有漏。
- 驗收：`run_chart_spec.py` 17 → 31（`create()` 一格一實例、真滾輪／真拖曳／真雙擊、現價線、`chart_grid` 嘅
  build/set/note/takePicks，並真執行 Python 生成嘅 `grid_js`/`grid_note_js`）、`run_api.py` 80 → 85、
  `run_gui.py` 84 → 98、`run_webui.py` 79 → 93；`run_stream_kline.py` 加多週期並行（各週期 `ts` 間距為該週期嘅
  整數倍、同週期第二份 `stream_busy`、多個週期共用同一個 `OpenQuoteContext`）→ 35 PASS / 5 FAIL，5 個 FAIL
  全部係 IB 連唔到 TWS（`WinError 1225`，屬環境而非代碼）。
- 語言檔三份鍵集合仍一致（73 → 85 個）；八個 `.ui` 檔仍不含任何文字。

### 變更（訂閱實時一律先取歷史，再喺同一張圖合併串流）
- 三個界面（閘道面板 `ui.html`、Web UI `home.html`、桌面 GUI `app.py`）同一規則：撳「訂閱實時」即先為該（代碼,
  週期）向 `/kline` 取歷史，歷史回到序列先至建立 WS 訂閱；**歷史都無 bar 即唔訂閱**——只靠串流撐出來嘅圖得返最近
  幾十根實時 bar，卻會被誤認為完整歷史。合併規則不變（key =（代碼, ts），同 ts 以新到者為準，保留最新 N 根），
  故畫面永遠係一條連續序列，唔會變成第二張圖。
- 多週期：先為九格各取自己週期的歷史，九格齊了先至喺同一條連接訂閱（只訂閱有 bar 嘅格）。串流中改一格：先退舊
  週期嘅名額，該格的新週期歷史回到圖上才喺同一條連接 `subscribe`（先訂閱即該格得返最近幾十根；不重連、不影響
  其餘各格）。
- 桌面端取歷史在途時撳「停止」：`wants_stream`／`_grid_wanted` 記低意圖，歷史返到時不再建立連接。
- **修復**：`end_stream`／`end_grid_stream` 冇丟掉已收尾嘅 `StreamClient`，「停止」後重按「訂閱」被防重入擋住而
  靜靜冇反應。同步放手又會喺該連接自己嘅 `finished` 信號鏈中途析構 QObject（access violation，offscreen 跑驗收
  即崩）→ 建立時 `parent=self.window`（`DesktopGui` 唔係 QObject，`parent=self` 即 constructor 錯），收尾改用
  `deleteLater()`。
- 驗收：`run_gui.py` 98 → 103、`run_webui.py` 93 → 97。順序斷言嘅手法：HTTP 存根只識 `/kline`、WS 存根只識
  `/stream`，故以 wrapper 喺「歷史已返、未建連接」嗰一瞬間先換 `base_url` 指向（真實閘道兩者同一地址）；「先退
  名額、歷史回到圖上才訂閱」以每幀到達那一刻嘅根數快照核對（事後再查 frames 證明唔到訂閱嗰一刻嘅狀態）。順手修
  兩處會攰斗嘅斷言：「停止」後等一句可能已經喺度嘅說話（改一格週期退名額都會寫「已停止 futu 串流」）→ 改等
  `pane.stream`／`_grid_stream` 真正為 `None`。

### 修復（拖曳之後雙擊復原靜靜冇效）
- `dataZoom.throttle` 預設 100ms：拖曳最後幾個平移動作會喺雙擊復原**之後**先送達，`chart.on('dataZoom')` 再把它
  們寫返入 `view`，復原即被蓋走（實測復原後範圍變返拖曳前嗰段）。roam 驅動嘅事件唔帶 `start`/`end`，無法靠 payload
  區分，故喺 x 軸嗰份 dataZoom 設 `throttle: 0`（即時生效），復原守得住，拖曳手感亦更直接。
- 由 `run_chart_spec.py` 嘅真拖曳＋真雙擊斷言捉到（30 PASS / 1 FAIL，重跑兩次同樣，非偶發）。

### 變更（K 線界面收返兩頁：刪除「K 線圖」與「K 線圖（多週期）」，圖移入「K 線串流」的 DF 上方）
- 只刪頁面，唔刪能力：`home.html` 的 `kq-*` 與 `.grid` CSS、GUI 的 `KlineChartPage`／`KlineGridPage`、
  `ui/kline_chart_page.ui`／`ui/kline_grid_page.ui`、`brokery_gui/grid_view.py`、`static/chart_grid.html`、
  `chart.py` 的 `grid_page()`／`grid_js()`／`grid_note_js()` 一併移除，冇留任何相容性外殼。
- `static/chart.js` 與 `brokery_gui/chart_view.py` 保留：圖表改由「K 線串流」頁在表格上方畫出（Web UI
  `#ks-chart`、GUI `chartBox`），沿用同一個 `KlinePane`／`BarStore` 與同一條「先取歷史、歷史回到圖上才訂閱」的
  規則，故 `paint_kline`／`renderTable` 永遠同一份序列（表格行數即合併後的根數）。
- `BrokeryChart.create(el, opts)` 的 `opts` 只剩初始縮放範圍與圖形規格（`ktype`，換週期由 `update` 帶新值）；
  `opts.compact` 隨 3×3 載體頁一併去掉（再無其他呼叫者）。
- 多週期仍是 **API 層**能力：`stream_ktypes`、`/stream` 名額按（券商, 週期）、一條 WS 多個訂閱照樣保留，
  只係冇咗 3×3 嗰個界面。
- **Web UI 的 DF 表格去掉 30 行截斷**（`K_TABLE_ROWS`）：接口返回幾多根就列幾多行。查證過資料層冇手腳——
  `raw=True` 與統一行的 `volume`/`turnover` 逐行相同（富途原生 dtype 本身即 float64），transport、core、適配器與
  推送 sink 一律原樣傳遞；真正的「簡化」只發生喺顯示層。桌面 GUI 本來就無此上限。
- 語言檔 85 → 69 鍵（三份鍵集合仍一致）；`.ui` 由八個減至六個（`kline_stream_page.ui` 加
  `chartBox`／`chartLayout`／`chartNoteLabel`，圖表區由程式延後放入，.ui 仍不引用任何 QtWebEngine 型別）。
- 驗收計數：`run_chart_spec.py` 31 → 26、`run_gui.py` 103 → 86、`run_webui.py` 97 → 82。新增斷言：選單為五項、
  DF 列出接口返回的全部行（120 行的存根返回 120 行）、串流頁 canvas 在表格之前且與表格同一份序列、訂閱只開
  **一條**上游 WebSocket。全閘口 20 檔：14 檔 exit=0，6 檔的 FAIL 全部為 IB 連唔到 TWS
  （`ConnectionRefusedError: WinError 1225`，屬環境而非代碼）。

### 變更（閘道接手仍在推送的串流；桌面 GUI 的載入提示、圖表高度與現價大字）
- **「訂閱咗就唔好再訂閱，直接串流」**：名額按（券商, 週期），而 `Brokery.stream_kline` 沒有 stop 鉤子——`StreamWorker.stop()`
  只標記，執行緒要到該次時窗（`API_STREAM_SECONDS`）走完才返回並經 `on_done` 釋放。故「停止」之後名額本來就未釋放，再訂閱
  同一份請求只會在閘道換來一次 `stream_busy` 同一段睇唔到最新價嘅空窗。改法在閘道：`StreamWorker` 加
  `attach`/`detach`/`resume`/`same_request`，`attached` 建立時即為 True（綁住創建它嘅連接），客戶端停止或斷線即 `detach()`；
  同一（券商, 週期）再訂閱，若代碼、根數、複權、`raw` 完全一致且暫無連接在收，即**接手**呢條仍在跑的串流（換的只是收事件
  的佇列，不重新向券商訂閱），回 `subscribed` 帶 `resumed` 與剩餘秒數；換了參數或該週期已被別條連接收住才照舊明確返回
  `stream_busy`，其 error 帧附 `release_in`（自然結束的 `end` 帧不帶該欄位，名額已歸還）。不改 core 與適配器：接手屬閘道
  的連接管理。GUI 因此不再預先記低 `closed` 帧的 `release_in`（只會白等一段根本唔使等嘅時間），只喺真被拒時把
  `release_in` 記在 `KlinePane.quota` 並以 `wait_quota` 的 1 秒 `QTimer` 倒數（`kline.quota_wait`、`COLOR_WARN`）、到點
  `retry_stream` 自動重送訂閱，期間按「停止」即取消（用可 `stop()` 的計時器而非 `singleShot`）。
- **載入提示由狀態驅動**：`ChartView` 以 `ready`/`error` 與 `on_state` 回報載入狀態，`note_chart()` 據此顯示「正在載入
  圖表…」、就緒即清走、失敗才顯示原因。之前是畫圖時順手寫上、成功時不清走，故圖已出現仍掛住提示。
- **圖要佔盡圖表區，並佔頁面高度一半以上**：`ChartView` 的 view 以 `QSizePolicy.Expanding` 並帶 stretch 加入佈局（之前與
  提示列平分該區高度）。`kline_stream_page.ui` 的圖表區／DF `verstretch` 由 2:3 改為 **3:2**（實測 1280×800 下圖佔頁 54%）。
- **現價大字與右側留位（`static/chart.js`，三處界面同畫）**：`graphic` 於右上角以 22px 粗體顯示序列最後一根的收市價
  （升紅跌綠），`room.right` 16 → 64 讓最新一根 K 線不緊貼右邊界（現價數字即疊於該留白之上）；兩個 `yAxis` 一律
  `splitLine: {show: false}`。本圖 `animation: false`，故閃爍由實例自己做：`paint()` 比較新舊現價，只在價格真的改變時
  以反色底蓋一次（`FLASH_MS = 700`，`destroy()` 一併清計時器）；首次載入與重畫同一價格不閃。
- **測試側的兩處修正**（非 core 改動）：① 串流存根的 `closed` 帧要照真實閘道逐個訂閱帶 `broker`＋`ktype`（stop 幀本身
  唔帶呢兩個欄位），否則名額記成空週期，`quota_left` 永遠配唔上；② 按「停止」之前要先等到 `subscribe` 幀真的送達存根
  ——`StreamClient.stop()` 只在 `ConnectedState` 才發帧，連接未建立時 stop 會被丟掉，`closed` 亦唔會返。
- **取消等名額的收尾分兩條路徑**：解鎖按鈕原本只由 `end_stream()` 做，而佢由該連接自己的 `finished` 觸發。被
  `stream_busy` 拒咗之後連接仍然在（閘道只回一帧 error），故呢種取消照舊由 `closed`/`finished` 收尾，提示以「已停止 …
  串流」為準，唔應該再寫「已取消等待訂閱」；只有根本未開連接嘅等待（舊名額未過又重按「訂閱」）先要 `stop_stream()` 自己
  解鎖並改以 `kline.wait_cancelled` 說明，否則撳「停止」之後「訂閱」一直灰住，用戶連改參數重來嘅門都冇（取歷史在途嗰種
  取消仍由 `open_stream` 的 `wants_stream` 防護收尾）。
- 語言檔 69 → 71 鍵（新增 `kline.quota_wait`、`kline.wait_cancelled`，三份鍵集合仍一致）。驗收計數：`run_chart_spec.py`
  26 → 30（新增現價大字的取值/配色/只在新價改變時閃、取消 y 軸格線、最新一根右側留位）、`run_api.py` 85 → 90（新增
  「同一份請求在新連接上被接手：不另起名額、不返回 `stream_busy`」與接手後即刻收到仍在推送的 bar）、`run_gui.py` 86 → 93
  （新增名額四步：停止後即刻重訂閱即刻串流、真被拒先倒數、到點自動重送、等名額期間停止即取消；另加載入提示清走、圖佔盡
  圖表區高度、K 圖佔頁面高度一半以上）。
- **測試側第三處修正**：名額到點嗰次訂閱係由 `QTimer` 直接呼叫 `retry_stream`（連接還在即照同一條再送訂閱幀，已收尾才經
  `open_stream` 重建），唔再經過 `stream_after_history` 嗰次性嘅地址換指向，故該節要把 `app.StreamClient` 固定指向 WS 存根
  （取歷史照樣打 HTTP 存根）。真實閘道 `/kline` 與 `/stream` 同一地址，無此問題——呢係存根分成兩條造成，唔係界面嘅缺陷。
- **測試側第四處分工**：`stream_busy` 嘅反例由 WS 存根一次性注入（`StreamStub.reject_in`），存根**唔重寫**閘道的名額規則
  （接手與否由 `run_api.py` 對住真閘道驗）；`run_gui.py` 只驗界面收到協定帧之後嘅反應，兩檔唔重疊。

### 變更（`count` 在任何週期足數、根數可任選、K 圖為可重用元件）
- **根因喺取數路徑，唔係界面**：實測 `HK.HSImain` 傳 `count=1000` 時，`1m`/`15m` 得 1000 根，`5m`/`30m`/`60m`/`day`/
  `week`/`month` 一律只得 60 根——因為 `FutuBroker.get_kline` 以 `count ≤ FUTU_PAGE_MAX` 分路徑，而 `get_cur_kline` 喺呢啲
  週期根本唔給足。「1000 條只顯幾十條」同樣係數據層只得 60 根，唔係 `chart.js` 的視窗問題。
- **改法**：`get_cur_kline` 降為**快路徑**，不足即以 `request_history_kline` 分頁（`max_count = FUTU_PAGE_MAX`）多取，兩段按
  `ts`（`raw=True` 則 `time_key`）去重合併——同一根以快路徑者為準——再取尾 `count` 根。起日由 `span_days` 推算，過早會被
  上游拒（`F3CNN返回錯誤，可能是參數錯誤或者斷線`），故以 `HISTORY_MIN_SPAN_DAYS = 365` 為下限折半重試，到下限仍失敗即
  明確抛出而唔靜靜少返。`span_days` 本身冇改（IB 同用）；無任何 hardcode 最大回溯。實測 `count=3000`：`1m`–`day` 足數，
  `week` 1114 根、`month` 257 根（該標的的真實深度），每條 ≤1.3 秒。
- **深度不足會點名**（core）：實際根數少於請求時 `status` 仍為 `True`，但 `message` 加「`{broker} 的 {ktype} 深度只有 M 根
  （請求 N 根）`」，閘道原樣透傳，界面即刻見到邊家邊個週期只得幾多根。
- **根數可任選**：`kline_pull_page.ui`／`kline_stream_page.ui` 的 `countSpin` `maximum` 1000 → **100000**（core 本來就無上限，
  只有 `count < 1` 報 `bad_count:`）。
- **合併器上限跟請求根數**：`chart.BarStore` 新增 `set_limit()`（改上限即刻按新值裁剪），`KlinePane.select()` 按控制列的
  `count` 縮放；之前寫死 `BarStore(DEFAULT_COUNT)`，取 3000 根會被裁返 1000 根。
- **顯示所請求**：`chart.render_js` 新增 `start`/`end` 透傳（`chart.js` 的 `option()` 本來就收 `opts.start`，`DEFAULT_START = 60`
  只是省略時的預設），桌面 GUI 渲染時傳 `start: 0`，即本次所請求的根數全部喺圖上（`dataZoom` 照可再收窄）。呢一步只改
  GUI，`chart.js` 的預設行為不變（Web UI 其後跟上一輪，見下一節）。
- **K 圖模組化重用**：`brokery_gui/chart_view.py` 新增 `KlineChart`（圖表容器 + 提示列 + 惰性 `ChartView` + 狀態提示，換語言
  自行重貼），每個有 `chartBox` 的分頁各持一個（`pane.chart`，無該容器嘅頁為 `None`）；移除 `app.py` 的 `self._chart`／
  `ensure_chart`／`note_chart`／`paint_chart` 與 `page is self.kline_stream` 特例，日後任何頁要加圖只傳容器與提示列即可。
- 驗收計數：新增 `run_futu_kline.py` **13 項**（離線存根 `_ctx`，唔使 OpenD：六個週期各取足 1000 根、兩段重疊去重且以快
  路徑者為準、`count=3000` 唔行快路徑、起日折半序列、到下限明確报错、month 只得 257 根、core 的 shortfall message 原樣送到
  信封、`raw=True` 按原生 `time_key` 排序截尾）；`run_chart_spec.py` 30 → **32**（`render_js` 帶 `start`/`end`、省略時不帶；
  `BrokeryChart.create(el, {start: 0})` 即 1000 根全部喺圖上）、`run_api.py` 90 → **91**（閘道原樣透傳 shortfall message）、
  `run_gui.py` 93 → **94**（`countSpin` 上限、`count=3000` 原樣轉發且 `store.limit == 3000`、每頁各一張圖且 `gui._chart` 已無、
  渲染帶 `start: 0` 且圖與表格同一份根數）。

### 變更（Web UI 與桌面 GUI 功能同步；順帶修走 `chart.js` 兩處潛藏缺陷）
- **同步清單**：桌面 GUI 上一輪的五項一律補到 Web UI（`brokery_webui/home.html` 的 `klinePane`，即 GUI `KlinePane`／
  `KlineChart` 喺頁面的對應物，兩頁各持一份控件、序列與連接）：根數可任填（`min=1 max=100000`）、合併器上限跟本次請求的
  根數、開圖傳 `start: 0`、換週期即換該次輸入的規格、`stream_busy` 照 `release_in` 倒數後自動重送訂閱。
- **`store()` 上限寫死**（共用層）：`BrokeryChart.store(1000)` 之後無法調整，取 3000 根會被 `trim()` 裁返 1000 根——即
  「1000 條只顯幾十條」在 JS 側的另一半成因。新增 `setLimit(next)`（即刻按新值裁剪，並回報新值），與 Python 側
  `BarStore.set_limit()` 同一口徑。
- **`render()` 重入唔帶規格**（共用層）：外殼只喺首次 `create(el, opts)` 時交 `opts`，其後 `update()` 收到 `undefined`，
  故界面換咗週期後 x 軸 formatter 永遠照開圖時嘅週期（日線仍顯示 `MM-DD HH:MM`）。圖形規格屬該次輸入的一部分，改為每次
  都交落該實例的 `update`；同一元素重入仍取返同一個實例（換標的不會疊加舊圖）。兩處都係三個界面共用，閘道面板同桌面
  GUI 一併受益。
- **名額被拒嘅正確客戶端行為**：真實閘道對 `stream_busy` 只發一幀帶 `release_in` 的 `error` 而**唔收線**（`app.py` 該分支
  其後 `continue`），所以喺同一條連接上重送訂閱先係對路；Web UI 之前只把訊息顯示出嚟就解鎖按鈕，用戶要自己再撳一次。
  現照 GUI 口徑：倒數只認而家的控件（換券商或週期即唔再等舊名額），撳「停止」即取消倒數。
- **有意保留的差異**（唔係缺口）：Web UI 的圖高為 CSS 固定的 420px，唔隨視窗拉伸——「K 圖佔頁面高度一半以上」屬桌面
  窗口嘅版面要求；閘道面板 `brokery_api/ui.html` 的根數輸入仍為 `max=1000`（該頁為除錯面板，且 1000 以內唔會觸及上述
  上限缺陷）。
- 驗收計數：`run_webui.py` 82 → **86**（根數可任填且 3000 原樣送達、`store.limit == 3000`、開圖 `start: 0` 且圖上的 bar 數
  即合併後的根數、換週期後 x 軸格式跟住改、`stream_busy` 由 WS 存根只拒一次並帶 `release_in`，核對 2 次訂閱／1 條連接）、
  `run_chart_spec.py` 32 → **34**（`store().setLimit()` 調高即取足 3000 根、調低即裁走最舊；`render()` 每次帶規格）。

### 變更（一條串流同時送俾多個界面：`StreamWorker` 由單佇列改為多訂閱者）
- **成因**：用戶實測「GUI 可以串流／WEBUI 1m 串流名額尚未釋放，約 166 秒後自動訂閱」。名額按（券商, 週期）全閘道計，
  而 `StreamWorker` 只綁**一條**連接的佇列（`_loop`/`_queue`/`attached`），故第二個界面一定被拒——不同週期或不同券商本來
  就唔使等，同一份請求先會。
- **改法**：`_loop`/`_queue`/`attached` → `_subs: dict[asyncio.Queue, asyncio.AbstractEventLoop]`（佇列 → 該佇列所屬的
  事件循環；跨事件循環仍须经 `call_soon_threadsafe`）。`push()` 逐個送，並先取 `list(...)` 快照：券商執行緒推送期間，
  事件循環可能同時 `join`/`leave`。
- `attach`/`detach`/`resume` → `join(loop, queue)`（回傳是否由「無人收」回到有，即接手，並撤銷 `_stopping`）、
  `leave(queue)`（回傳是否已無人收，只有最後一個退出先 `stop()`）、`watchers`（而家幾條連接在收）。`stop` 動作與連接
  收尾的 `finally` 一律改調 `leave`：先退出者不該把別家仍在收的串流一併停掉。
- `subscribed` 幀新增 `resumed`（接手一條暫無人收的串流）與 `shared`（超過一條連接在收）。同一條連接重送同一份請求為
  冪等——`_subs` 以佇列為 key，watchers 仍為 1，故 `shared` 為 False。
- `stream_busy:` 只剩**參數不同**先出現（一份請求 = 同代碼、同根數、同復權口徑、同 `raw`）；前綴不變，客戶端靠佢倒數，
  故 Web UI 與桌面 GUI 一律唔使改。要共用即兩邊根數要填一樣（兩邊預設都是 1000，开箱即用）。
- 唔改 core 與適配器：富途的推送回調按連線設置，同一（代碼, 週期）一條連線只容一份，而閘道本來就只向券商訂閱一次，
  fan-out 屬閘道的分派。
- 驗收：`run_api.py` 91 → **96**（`HoldPushQuote` 加「向券商訂閱了幾次」計數；兩條連接同一份請求 → 只訂閱一次、兩邊各收
  同一份 `update`、`shared`；一方 `stop` 只退出自己、另一條照收且不會另起一次訂閱；同一連接重送同一份請求為冪等；換
  `count` 仍 `stream_busy`）。改走舊斷言「同一（券商, 週期）同時只容許一份串流」（語義已變），拒絕一例改錨在參數不同。
  Starlette `TestClient` 可同時持有兩條 `websocket_connect`（已探測），故呢項可在進程內驗收，不需要真閘道。

### 新增（「K 線串流（多週期）」3×3：一格一週期、九格同一條連接）
- **格子與按鈕的來源只有一處**：所選券商聲明的 `stream_ktypes`（`/capabilities` 的 `adapters[name].stream_ktypes`，
  照 `KTYPE_ORDER` 排列）。futu 聲明九個 → 正好 3×3；IB 得部分；tiger／webull 只有 `1m` → 得返一格。界面唔排序、
  唔憑空補週期，所以唔會見到八格同時報 `ktype_unsupported`（與「能力不支持由適配器聲明、core 統一拒绝」同一口徑）。
- **圖表層加緊湊形態**（`brokery/static/chart.js` 的 `opts.compact`）：`option()` 只生成一個 grid 與一條 candlestick
  series（唔畫成交量格與 `xAxis[1]`/`yAxis[1]`、唔畫右上角現價大字，現價虛線保留但 label 縮細、`room` 收細）。
  非 `compact` 逐項完全唔變，故兩個單格 K 線頁與既有斷言照過。
- **一份共用嘅多格 JS**（`brokery/static/chart_grid.js`，`window.BrokeryGrid.build(el, {ktypes, onPick})`）：為每個
  ktype 建一格（上方一排水平週期按鈕 + 一個圖表 div），每格一個獨立實例；`set(i, payload, ktype)` 只重畫一格，
  `note(i, text)` 逐格提示，`takePicks()` 取走並清空點擊佇列。**頁內零文字**：按鈕只帶 `1m`／`day` 呢類 ktype token，
  語言中性，故換語言唔使重建格子（三份字庫因此完全唔需要為按鈕加鍵）。載體頁 `brokery/static/chart_grid.html`
  （唯一容器 `#grid`，探針 `brokeryGridReady`/`brokeryGridMissing`）。
- **Python 側只多幾個入口**（`brokery/chart.py`）：`grid_page()`（經既有 `static_file`）、`grid_js(ktypes)`、
  `grid_set_js(index, frame, ktype)`、`grid_note_js(index, text)`、`grid_picks_js()`。`render_js`/`host_page` 冇郁。
- **桌面 GUI**：新 `brokery_gui/ui/kline_grid_page.ui`（檔內零 `<string>`，冇 `ktypeCombo`、冇 `klineTable`）+ 新
  `brokery_gui/grid_view.py`（`GridView` 照 `chart_view.KlineChart` 同一口徑：惰性 `ensure()`、載入提示由視圖狀態驅動、
  起不來顯示原因而唔係空白）。按鈕點擊靠 `QTimer` 輪詢 `takePicks()` 交回 Python，並只在該分頁可見且載體頁已就緒時
  輪詢——`QWebChannel` 喺 offscreen 載 `qrc:///qtwebchannel/qwebchannel.js` 即 segfault（已實測）。
- **逐格狀態，唔係逐頁**：`brokery_gui/app.py` 的 `GridPane` 同一頁持有 `stores: list[BarStore]`（一格一份）、
  `current: list[ktype]`、`keys`、**一條** `StreamClient`、`quotas: dict[(broker,ktype), 可再訂閱時刻]`。現有 `KlinePane`
  假設一頁一序列一 `ktypeCombo`，九格塞唔入去，故另寫一份而唔硬改。Web UI 側對應為 `home.html` 的 `gridPane(prefix)`。
- **流程照單格串流頁**：先逐格 `/kline` 取歷史（根數為控制列一個共用輸入，預設 300），全部返回先至喺**一條**連接上
  送九個 `subscribe`；`update` 按 `ktype` 只重畫對應格；一個「開始／停止」管全部格子（逐格只有週期按鈕）。換某一格
  嘅週期即只重取嗰格、只退該 (券商, 週期) 名額；若該舊週期仍有別格顯示則唔退（退咗會斷咗嗰格嘅推送）。
- **閘道與 core 冇改**：名額按（券商, 週期）、`update` 一律帶 `ktype`、`stop` 可帶 `broker`/`ktype` 只收一部分，全部
  係上一輪已落地嘅協定（`brokery_api/app.py` 的註解本來就寫明「多週期界面（例如 3×3）只用一條 WS」）。呢次只係界面
  第一次真係咁用。九個訂閱共用一條連接唔係偏好而係必須：瀏覽器對同一來源只得約 6 條 HTTP/1.1 併發連線。
- **順帶修走兩個真缺陷**（`brokery_webui/home.html`）：① `pick()` 嘅守門用咗 `current`（而家邊格顯示緊咩）而唔係
  `layout`（聲明嘅清單）→ 某週期被別格換走之後就永遠換唔返，而按鈕已經高亮咗，界面即刻矛盾（桌面 GUI 嘅守門本來就
  係 `ktype not in pane.layout`，兩邊自此一致）；② 「停止」嘅收尾提示靠 `closed` 帧，但瀏覽器一 `close()`，Web UI 嘅
  `/ws/stream` 代理即拆上游，閘道逐個回嘅 `closed` 未必返到嚟，訊息會留低「已更新 X」→ 收尾改由 `stop()` 自己寫，
  並喺 `readyState === OPEN` 先送（與桌面 GUI `stop_stream` 同一口徑；`end`/`closed` 分支只留註解，全頁只有一處報停止）。
  同一類問題喺 GUI 側為「等名額期間按『停止』」：該連接喺閘道無 worker，換唔到 `closed`，故 `stop_stream` 就地改寫
  （有連接即「已停止 X 串流」，無連接即「已取消等待訂閱」）。
- 驗收：`run_chart_spec.py` 34 → **47**（`compact` 的 `option()` 只一條 series 一個 grid 無現價大字、非 `compact` 逐項
  照舊；`BrokeryGrid` 九格九實例互不影響、撳按鈕只重畫一格並只上報 `[格, 週期]`、`takePicks()` 取走即清空、
  `resizeAll()` 涵蓋全部格子；`chart.py` 五個 `grid_*` 入口產生可在載體頁直接執行的呼叫）。
  `run_gui.py` 94 → **115**（六個分頁、七個 `.ui` 檔齊全且無文字、格子數與順序即聲明的 `stream_ktypes`（存根刻意把
  ib 排成未排序）、九格逐格取歷史先開一條 `QWebSocket` 九個訂閱、`update` 按 ktype 只餵對應格、換一格只重取嗰格並只送
  帶該 ktype 的退訂、別格同週期唔退名額、一格等名額唔阻其余、`GridView` 惰性與起不來明確提示）。
  `run_webui.py` 86 → **106**（選單六項、`/static/chart_grid.js` 與 GUI 讀到嘅逐 byte 相同、九格九實例、每格九個水平
  按鈕只有該格高亮、無 DF、九次逐格取數先開一條連接九個訂閱、`update` 按 ktype 只畫對應格、帶 ktype 的 `stop` 且唔開
  第二條連接、換返已無格子顯示的週期即補訂閱、一個「停止」只送一次裸 `stop` 並就地提示已停止、換券商即按 IB 未排序嘅
  聲明原樣重建）。`run_api.py` 96 → **108**（一條連接一次過訂閱九個週期、九份 `update` 各自帶自己嘅 `ktype`、`stop`
  只帶一格嘅 ktype 時該格 `closed` 而其餘八格照收、再送一次唔帶 ktype 的 `stop` 即逐個 `closed` 收齊剩低八格）。
  三份字庫 71 → **76 鍵**（鍵集合必須一致）。

### 變更（一份串流由請求簽名界定：同一券商同一週期可並行多條，名額倒數全線刪除）
- **動機**：用戶要「同一 BROKER、同一週期要多條串流，不管是 Web UI 定 GUI」。舊協定按（券商, 週期）只留一條，第二份
  即 `stream_busy`，界面只能倒數等名額（「futu 的 1m 串流名額尚未釋放，約 168 秒後自動訂閱…」），兩邊根數填唔一樣就
  睇唔到同一張圖。
- **適配器（futu）**：訂閱由「按 ktype 佔額」改為按 **（代碼, 週期）引用計數**（`brokery/brokers/futu_broker.py`）：
  `held = tuple(dict.fromkeys(codes))`，喺 `self._stream_lock` 之下 `self._subs[(code, ktype)] += 1`，且先於取起點；
  `finally` 逐鍵減返，只有歸零者先 `self._ctx.unsubscribe(...)`，串流數為 0 先 `stop()`。故同週期並行時唔會蓋走別份
  仍需要嘅訂閱（舊行為「同週期第二份即拒」已移除）。IB 逐個（代碼, 週期）各一次 `reqHistoricalData(keepUpToDate)`，
  本來已可並行；`core` 冇改。
- **閘道**：`app.state.streams` 與每連接 `workers` 的鍵由（券商, 週期）改為**請求簽名**
  `stream_key(broker, ktype, codes, count, autype, raw)`（`brokery_api/app.py`）。同簽名照樣 fan-out（`subscribed` 帶
  `shared`）／接手（帶 `resumed`）；簽名不同即另起一條並行 worker；`stream_busy` 由閘道彻底消失（`release()` 以身份為
  守，唔會誤退別人嘅 worker）。`closed` 帧仍附 `release_in`（該執行緒收尾尚差嘅秒數），只係客戶端不再照它行事。
- **界面：名額 UX 全部刪除，唔留半截**：桌面 GUI 走 `KlinePane.quota`／`quota_timer`／`retry_stream` 與
  `GridPane.quotas`／`grid_quota_left`／`wait_grid_quota`，三份字庫走 `kline.quota_wait`／`kline.wait_cancelled`
  （76 → **74 鍵**）；Web UI 走 `klinePane`／`gridPane` 的 `waitQuota`／`clearQuota` 與 `stream_busy` 分支。
  `brokery_gui/stream.py` 的 `_open` 由 set 改為計數（同一週期有兩條時唔會誤判「已收齊」而收走連接）。
- **剩下被拒只有「改參數先解決到」嘅協定錯誤**（`ktype_unsupported`、`broker_disabled`、`bad_request`）：兩邊一律原樣
  顯示閘道點名嘅原因、唔自動重送訂閱、亦唔解鎖按鈕（用戶撳「停止」即收返呢條連接）。界面自己重送只會出現用戶看不見
  嘅訂閱。
- **多週期頁照樣按 ktype 去重**：一格一週期即同簽名，本來就係同一份串流，故呢次唔需要協定擴展（冇 stream id，`stop`
  亦唔帶 `codes`）。
- 驗收：`run_stream_kline.py` 補三條（同週期第二份可並行／並行期間退訂閱 0 次／全部結束後退訂閱 1 次），整檔仍為
  35 PASS / 5 FAIL（5 個全係 IB 連唔到 TWS，屬環境而非代碼）。`run_api.py` 108 → **112**（同週期兩格不同代碼可並行、
  各自訂閱一次並各推自己代碼、`stop` 帶 ktype 即逐條 `closed`、換根數即另起一條、接手唔另訂閱）。`run_gui.py`
  115 → **120**（多週期頁已佔住 `futu/1m` 時另一頁照樣訂閱、兩條各自收推送各 +2 根、停一條唔影響另一條、已收返嘅
  連接唔再被填、協定錯誤原樣呈現且唔被自動重送）。`run_webui.py` 106 → **111**（存根按連接記訂閱，另加 `/push` 代替
  券商推送以核對兩條各自收到與「已收返嘅連接唔再被填」；推送必須帶新時間戳——同一 `ts` 只係覆蓋，唔會多根）。
