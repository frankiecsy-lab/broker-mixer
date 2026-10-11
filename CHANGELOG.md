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
- 向 IB 查詢不得指定 `exchange`（指定後常回報 `No security definition found`）；港股符號須去
  前導零。
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
