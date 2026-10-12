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
| 標的清單的統一輸出（四家同一欄位契約、未聲明品種明確拒绝） | ✅ 可用 | 四家逐家 × 逐品種實測（`run_list_symbols.py`）：欄位與順序一律為 `COLUMNS`、字串欄無 NaN、`code` 一律 `<市場>.<符號>`、未聲明者返回 `no_source`。`broker=` 只向一家取（未啟用即 `unknown_source`、該家不提供即 `type_unsupported`，不靜默改用別家）、`markets=` 過濾返回的市場（`run_list_filter.py` 14 項全過，不需連線） |
| 原生格式 `raw=True`（保留該券商自帶的欄位與值） | ✅ 可用 | 七個連券商方法一律支持：信封仍為三鍵、`data` 即該券商原生欄位與值，**只換欄位與格式，不改取數範圍與數值**（實測同一 K 線 raw 與統一格式的收市價逐根相同，最大相差 0.0）；跳過去重與按統一欄位的行過濾，故行數不少於統一格式；各家時間欄位即自己的寫法（富途 `time_key`、Tiger／Webull `time`、IB `date`）。`run_raw_frames.py` 37 項全過（不需連線）＋四家 raw 對照（`run_list_symbols.py`／`run_get_accounts.py`／`run_kline_matrix.py`） |
| 代碼雙向轉換（統一代碼 ↔ IB 原生合約） | ✅ 可用 | IB |
| 離線存放與讀回（parquet + meta） | ✅ 可用 | 本地 `brokery/data/`（由 `.env` 指定） |
| 離線讀取代碼清單 `get_code`（按券商各一檔 `<broker>_codes`） | ✅ 可用 | 本地 parquet，不需要 OpenD / IB（實測 38,569 條讀回 0.03s，即 250 倍於即時重拉，故搜尋一律讀快照）；讀 futu 不會混入 IB 的 conId，反之亦然 |
| 更新離線 CODES `refresh_codes`（每家一檔、照能力存放、縮細防護、按品種沿用舊快照、失敗留痕） | ✅ 可用 | 實測重拉港美全量 38,569 條約 6s：指數本次取唔到即沿用舊快照 740 條、其餘照常更新，`message` 說明增減；任何品種少於同一券商上一份快照的 90% 即拒絕覆蓋；快照內容由該家聲明的能力決定（`ib_codes` 只有期貨與指數屬正常）；`.prev.parquet` 保留被覆蓋的舊檔；`CODES_MAX_AGE_HOURS`（預設 24）決定過舊，閘道啟動時只在背景自動重拉 `CODES_SOURCE` 那一檔；`run_codes_refresh.py` 31 項檢查全過（含兩家各一檔互不覆蓋、縮細防護逐家比較、該券商已停用時不做背景自動更新） |
| K 線 `get_kline`（統一格式、以 bar 數取數） | ✅ 可用 | FUTU + IB（日/週/月線實測逐根按 `ts` 對齊，價格一致）+ Webull（日線/分鐘線實測，日線確實做了前復權，調整因子與 IB 一致：與原始成交價最大相差 0.062%）+ Tiger（日線/1 分鐘線實測，`autype="none"` 時 close 與 FUTU 逐根完全一致） |
| 前復權跨券商對照（日內與日線） | ✅ 可用 | FUTU `qfq` + IB `ADJUSTED_LAST` + Tiger `right=BR` + Webull（日線固定前復權）：`HK.00005` 日線 60 根四家共同 60 根逐根對齊，以富途為準 Tiger 最大相差 0.02%、IB/Webull 0.44% |
| 品種支持矩陣（股票／期貨／指數／期權）與復權適用範圍 | ✅ 已核實 | 四家實測（`run_kline_matrix.py`，48 項檢查）：不支持的品種由適配器聲明、`core` 統一返回 `type_unsupported`；復權只對股票有效（期貨／指數／期權的 `qfq` 與 `none` 逐根完全相同）；指數代碼可跨券商（`HK.800000` 富途與 IB 的 close 完全相同、`US..SPX` Tiger 與 IB 完全相同） |
| 戶口與資金 `get_accounts`（四家統一 15 欄） | ✅ 可用 | FUTU + IB + Tiger + Webull（實測 futu 2 個（cash/margin，模擬與已停用的不列）、IB 1 個、Tiger 1 個、Webull 2 個；`currency` 全部填到：futu/IB/Webull 為 HKD、Tiger 為 USD；IB 的 `individual` 在按 `cash`/`margin` 篩選時點名說明而不靜默丟列；59 項檢查） |
| 券商連線狀態與速度 `get_brokers`（統一 6 欄） | ✅ 可用 | FUTU + IB + Tiger + Webull 四家並行探測實測（futu 178ms／ib 542ms／tiger 1216ms／webull 954ms，總耗時 1.2s ≈ 最慢一家）；探測用一次戶口查詢，故不需要行情權限；22 項檢查全過 |
| HTTP/WS 閘道與 dashboard `brokery_api`（自訂 API Key、K 線圖、實時訂閱、戶口（四家同屏、自動更新以秒為單位、預設 0 不更新）、標的（按來源分四區；離線 CODES 按券商各一檔，以單一表格顯示，另列一行顯示該家快照年齡，並有「讀取離線 CODES／更新 CODES」兩個按鈕）、日誌窗、四家連線狀態與延遲、讀取提示；另有 `/brokers/prefs`（讀寫券商開關，見 §15）、`/capabilities` 回報 `ktypes` 與生效的適配器、`/static/chart.js`、`/static/chart_grid.js` 與 `/static/echarts.min.js` 為三個界面共用的同一份圖表與多格規格（見 §16）） | ✅ 可用 | 四家經同一閘道實測（`/kline`、`/accounts`、`/brokers`、各清單與 `/stream` 均連通）；`run_api.py` 112 項檢查全過（不需券商連線，含 `/codes?broker=` 只讀該家那一檔、兩檔互不覆蓋、未存放時點名要更新的券商、`/brokers/prefs` 寫入後被停用者一律 `broker_disabled:` 且不再出現在 `/capabilities`、重啟即照喜好檔生效、`/static/{name}` 不需金鑰且內容即 `brokery/static/` 那一份（走到目錄之外或不存在即明確 404 `static_missing`）、`/stream` 按**請求簽名**（券商, 週期, 代碼, 根數, 複權, raw）登記——一條 WS 同時訂閱多個週期、每一幀一律帶 `broker`/`ktype`、`stop` 可按其中一個只收部分、已指示停止的訂閱不被第二次 `stop` 重複發 `closed`、「停止」後同一份請求再訂閱即**接手**仍在推送的串流（`subscribed` 帶 `resumed`，接手後照樣收到其後的 `update`）、同一份請求可被**兩條連接同時訂閱**（核對向券商只訂閱了一次、兩邊各收到同一份 `update`、`subscribed` 帶 `shared`；其中一方 `stop` 只退出自己，另一條照收且不會另起一次訂閱）、同一條連接重送同一份請求為冪等（不另開一條）；**簽名不同即另一條串流，同一券商同一週期可並行多條**（同週期兩格不同代碼各自訂閱一次並各推自己代碼、換根數即另起一條、`stop` 只帶 ktype 時逐條各發一份 `closed`），不再返回 `stream_busy`；**多週期界面（3×3 九格）即以此為依據**：一條連接九個訂閱、九份 `update` 各自帶自己嘅 `ktype`、`stop` 只帶一格嘅 ktype 時其餘八格照收）；`run_ui.py` 47 項客戶端檢查全過（存根閘道 + Chromium：含兩頁的自動更新以秒為單位且預設 0 時空轉完全不打請求、按來源汇总並點名無返回者、標的頁一次點擊四區同時返回並區分「N 條／無返回／不提供此清單」、請求進行時的讀取提示、標的頁不再有「統一格式輸出」面板（即時清單只按來源分區）、離線 CODES 不分區而以單一表格顯示且欄位順序即接口原樣、該家快照一行顯示行數與距今時間且過舊以警告色提示、「更新 CODES」只向 `/codes/refresh` 送出且不带市場參數、換券商即改讀該家那一檔（不含別家的行數）、搜尋零結果且快照過舊時提示按「更新 CODES」、K 線頁預設 `HK.HSImain`／`1m`／1000 根且圖表由那份共用的 `chart.js` 與本地 echarts 畫出（已無 CDN）、下方表格按時間反序、`update` 只帶最近幾根時與已拉取的序列合併而不縮減行數） |
| 量化交易 Web UI `brokery_webui`（上方菜單六項：「戶口清單」四家戶口與資金同屏；「標的列表」上方為類型／市場／券商篩選、下方為取得的清單，默認富途；「K 線拉取」「K 線串流」兩頁同一控制列（標的預設 `HK.HSImain`、週期預設 `1m`、根數預設 1000 但**可任選數字**（上限 100000，與桌面 GUI 一致；該標的在該週期無咁深時 `message` 點名該來源的實際深度）、券商預設生效的第一家），下方 DataFrame 列出接口返回的**全部行**（不截斷，即原數據）**按時間反序（最新在最上）**；「K 線串流」在 DF 上方以那份共用的 `chart.js` 畫蠟燭＋成交量（縮放、平移、雙擊復原與現價線一律由那份規格提供，見 §16），圖與表格同一份序列：先取歷史再開串流，串流的 `update` 與已拉取的序列合併（同 `ts` 覆蓋、歷史不被縮返，保留的根數即所填的根數），開圖傳 `start: 0` 即所請求的根數全部喺圖上，訂閱只開**一條** `WebSocket /ws/stream`；一份串流由請求簽名界定，**同一券商同一週期可同時並行多條**（換根數或換代碼即另一條），閘道不再返回 `stream_busy`，界面已沒有倒數與自動重送；同簽名時與桌面 GUI 共用同一條串流（一方已訂閱即接手），協定錯誤（`ktype_unsupported`、`broker_disabled`、`bad_request`）原樣呈現、唔自動重送；「K 線串流（多週期）」**一格一週期、九格同時串流**：格子與每格上方的水平週期按鈕一律取所選券商聲明的 `stream_ktypes`（futu 九個正好 3×3、IB 得部分、只聲明 `1m` 者得返一格），界面唔自行排列亦唔憑空補週期；下方唔列 DF，一格一份序列，根數由控制列一個共用輸入（預設 300），一個「開始／停止」管全部格子，逐格只有週期按鈕——換一格即只重取嗰格、只退該週期的串流，別格已顯示同一週期時即同簽名，沿用同一份推送唔另起一條，九個訂閱仍只用**一條** `WebSocket /ws/stream`（瀏覽器對同一來源只有數條 HTTP/1.1 連線，九條必死）；「BROKER 管理」以開關列出全部券商，套用後即時生效並令各頁下拉框即時去掉被停用者；戶口與標的兩頁均有「自動更新（秒）」，預設 0 即不更新） | ✅ 可用 | 資料經同一閘道取得（實測 `http://127.0.0.1:8282` 顯示 6 個戶口：futu 2／ib 1／tiger 1／webull 2，15 欄與 `ACCOUNT_COLUMNS` 逐欄一致、缺失值為破折號）；券商選項由能力聲明填充、不提供該品種者標註且不可選，市場選項只由實際返回的 `market` 填充；標的頁另列一行顯示**所選券商**離線快照的行數與距今時間（過舊以警告色提示）、「讀取離線 CODES」轉發 `/codes?broker=`、「更新離線 CODES」轉發 `/codes/refresh?broker=`，換券商即改讀該家那一檔；定時更新預設只重讀離線快照，勾上「自動向券商重拉」才向券商取清單；K 線各頁一律經閘道（`/api/kline` 轉 `/kline`、`WebSocket /ws/stream` 雙向透傳 `/stream`，金鑰仍只在服務端），BROKER 開關經 `/api/brokers/prefs`；`run_webui.py` 111 項檢查全過（存根閘道 + Chromium，不需券商連線，含 WS 代理雙向透傳與上游不可達時返回明確 `error`、`/static` 只有一份圖表規格、兩頁預設值與 DF 反序、**DF 列出接口返回的全部行（120 行的存根返回 120 行，不截斷）**、根數可任填（上限 100000）且 3000 原樣送到閘道、合併器上限跟住 3000（唔會裁返 1000）、開圖 `start: 0` 即圖上的 bar 數即合併後的根數、換週期後 x 軸格式跟住改、**同一券商同一週期可並行多條**（多週期頁已佔住 `futu/1m` 時「K 線串流」頁照樣訂閱同一券商同一週期，另開一條連接、唔被拒、唔使等；兩條各自收到推送各 +2 根，互不取代；停其中一條只收返該條，另一條照舊串流並繼續收推送）、協定錯誤原樣呈現且唔被自動重送、串流合併、訂閱只開一條上游 WebSocket、串流頁在 DF 上方以本地 echarts 畫出 canvas 且表格行數即合併後的根數（圖與表格同一份序列）、一律先取歷史才建立串流（取不到歷史即不訂閱，故畫面永遠一條連續序列）、開關寫入後下拉框即時更新、`/static/chart_grid.js` 與 `brokery/static/` 那一份逐 byte 相同、**多週期頁按聲明起九格**（九個實例、每格九個水平按鈕只有該格高亮、無 DF 表格）、九格逐格取歷史先至開**一條**連接的九個訂閱、`update` 按自帶的 `ktype` 只畫對應嘅格（日線格與分鐘格的 x 軸格式必然不同）、一格只畫一個 grid 一條 series（緊湊規格，唔帶成交量格與現價大字）、換一格只送帶該 ktype 的 `stop` 且唔開第二條連接、換返一個已無格子顯示的週期即補訂閱、舊週期仍有別格顯示即唔退它、一個「停止」只送一次裸 stop 並就地提示已停止、換券商即按該家聲明的順序原樣重建格子（IB 未排序的聲明即見其原序）） |
| 量化交易桌面 GUI `brokery_gui`（PySide6：六個分頁同 Web UI——「戶口清單」「標的列表」（**上方為該券商原生格式（`raw=True`）、下方為統一格式**，兩張表同一時刻同一篩選條件）、「K 線拉取」「K 線串流」（同一控制列，標的預設 `HK.HSImain`、週期預設 `1m`、根數預設 1000 但**可任選數字**（上限 100000；該標的在該週期無咁深時 `message` 會點名該來源的實際深度），下方表格列出返回的**全部行**並**按時間反序**）、「K 線串流（多週期）」（**一格一週期、九格同時串流**：格子與每格上方的水平週期按鈕一律取所選券商聲明的 `stream_ktypes`，界面唔自行排列亦唔憑空補週期；一格一份序列，根數由控制列一個共用輸入（預設 300），一個「開始／停止」管全部格子，逐格只有週期按鈕——換一格即只重取嗰格、只退該週期的串流，別格已顯示同一週期時即同簽名，沿用同一份推送；九個訂閱只用**一條** `QWebSocket`；下方唔列 DF，格子由 `brokery/static/chart_grid.js` 在 `QWebEngineView` 內生成，按鈕只帶語言中性的週期名，換語言唔使重建格子）、「BROKER 管理」（開關列出全部券商，未配置者不可勾並顯示原因）；「K 線串流」在表格上方以 `QWebEngineView` 載入那份共用的 `chart.js` 畫圖（由可重用元件 `KlineChart` 持有：容器 + 提示列 + 惰性視圖封成一個物件，每個有圖表區的分頁各持一個，日後任何頁要加圖只傳容器與提示列），渲染時傳 `start: 0`，即本次所請求的根數全部喺圖上（`dataZoom` 照可縮放，Web UI 不受影響），故自定義指標在三個界面看到的完全一樣，圖與表格同一份序列；QtWebEngine 起不來時明確說明原因，下方表格照常；**訂閱咗就唔好再訂閱，直接串流**——該串流執行緒要到時窗走完才停下（「停止」只提前收尾），故「停止」後再訂閱同一份請求（同簽名）由它**接手**仍在推送的串流，即刻繼續收；同一份參數（同代碼、同根數）亦可與 Web UI **同時收同一份 bar**，一邊停止或收線都唔影響另一邊；**簽名不同即另一條串流，同一券商同一週期可同時並行多條**（換根數或換代碼即另一條），閘道不再返回 `stream_busy`，界面已沒有倒數與自動重送（`kline.quota_wait`／`kline.wait_cancelled` 已從三份字庫刪除），協定錯誤原樣呈現、唔自動重送；界面以 `.ui` 檔分離且檔內不含任何文字；繁體中文／简体中文／English 即時切換，每個語言一個 `.json`（現為 74 鍵，三份鍵集合一致）；戶口與標的兩頁均有「自動更新（秒）」，預設 0 即不更新） | ✅ 可用 | 與 Web UI 同一閘道、同一口徑（表格欄位由返回的 `columns` 決定、缺失值為破折號、資金欄千分位、券商選項由能力聲明填充且不提供該品種者標註並不可選、市場選項只由實際返回的 `market` 填充）；兩張表按同一請求先統一格式、再 `raw=True` 順序取數（同一閘道同一券商連線，不併發），舊回應不會蓋過新選擇；取數在背景執行緒，界面不因券商連線而凍結；標的頁另列一行顯示**所選券商**離線快照的行數與距今時間（過舊以警告色而非錯誤色提示）、「讀取離線 CODES」只向 `/codes?broker=` 讀該家那一檔、「更新離線 CODES」只向 `/codes/refresh?broker=` 送出且不带市場參數、換券商即改讀該家那一檔、切換語言時該行一併重貼；定時更新以秒為單位（預設 0 完全不請求，預設只重讀離線快照，勾「自動向券商重拉」才向券商取清單）；K 線各頁只經閘道（`/kline` 取歷史、`QWebSocket` 對 `/stream` 訂閱，收到的 `update` 經序列合併而非取代；一個訂閱只開一條 `QWebSocket`），取數一律在背景執行緒、回應由屬主執行緒的轉接物件交回 GUI 執行緒（PySide6 中連到普通可呼叫物件的信號會在發射執行緒執行，直接碰 `runJavaScript` 會崩潰）；`run_gui.py` 120 項檢查全過（存根閘道 + Qt 離屏，不需券商連線亦不需顯示器，含六個分頁與轉語言後全部標題、各頁預設值、根數可任選（`countSpin` 上限 100000；`count=3000` 原樣轉發且序列容器上限跟隨它，唔會裁返 1000）、圖表為可重用元件且每個有圖表區的分頁各持一個（主窗口不再持有視圖）、渲染傳 `start: 0` 即所請求的根數全部喺圖上、表格欄位即 `K_COLUMNS` 且反序、訂閱與停止的按鈕狀態、一個訂閱只開一條連接、合併後不縮返歷史、圖表惰性建立且渲染的根數與表格一致（圖與 DF 同一份序列，並照控制列的週期顯示時間軸）、圖表起不來時以明確原因提示而下方 DF 照常、先取歷史才建立串流（取不到歷史即不訂閱）、取歷史在途時撳「停止」即取消意圖、停止後重按「訂閱」會重新先取歷史（不被已收尾的連接擋住）、**接手唔使等**（按「停止」後不預先記低 `closed` 帧給的收尾秒數——同一份請求由閘道接手，界面唔該白等 → 「停止」後再按「訂閱」即刻送訂閱幀、即刻串流）、載入成功即清走「正在載入圖表」的提示、K 線圖佔盡圖表區的高度、K 圖佔頁面高度的一半以上（圖表區與 DF 按 .ui 的 3:2 分配）、開關一改即重讀能力聲明、多週期頁的 .ui 無任何文字亦無週期下拉框與表格、格子數與順序即該家聲明的 `stream_ktypes`（存根把 ib 刻意排成未排序的順序，一排序即露餂）、九格逐格取歷史先至開**一條** `QWebSocket` 的九個訂閱、`update` 按自帶的 `ktype` 只餵對應嘅格、換一格只重取嗰格並只送帶該 ktype 的退訂、別格已顯示同一週期即同簽名，唔退它亦唔另起一條、**同一券商同一週期可並行多條**（多週期頁已佔住 `futu/1m` 時另一頁照樣訂閱，另開一條連接、唔使等；兩條各自收到推送各 +2 根；停一條唔影響另一條；已收返嘅連接唔再被填）、協定錯誤原樣呈現且唔被自動重送、`GridView` 惰性建立且起不來時以明確原因提示） |
| 券商開關（BROKER 管理，全域生效） | ✅ 可用 | 一個本地 JSON 檔 `<data_dir>/broker_prefs.json`（由 `.env` 的資料目錄決定），**只記被停用的家**，故 `.env API_SOURCES` 改了也不會留下舊名單；檔不存在或壞咗即全部生效（不需遷移）。生效集合 = `.env API_SOURCES` ∩ 喜好，由 `core` 統一執行：被停用者一律不經過它（`get_kline`／`stream_kline`／三個清單／`get_accounts`／`get_brokers`／`convert` 全部返回 `broker_disabled:`，與連不上、未聲明（`unknown_source`／`type_unsupported`）在 message 上分清楚），三個界面的券商下拉框因此自動更新，不需要逐處開關。開關只影響界面：喜好檔只由閘道讀寫，`core` 只接受 `Brokery(disabled=…)`，故逐家取數的驗收與離線分析（唔傳 `disabled`）不受界面上嘅開關影響。`run_broker_prefs.py` 18 項檢查全過（存根券商 + 臨時資料目錄，不需連線、不觸及實際喜好檔） |
| 共用圖表層（一份規格，三個界面同畫） | ✅ 可用 | `brokery/static/chart.js` 是唯一一份渲染規格（`window.BrokeryChart`：蠟燭 + 成交量兩格、`dataZoom`、x 軸一律用原始 `ts`，時間文字只由 formatter 產生；`opts.compact` 為同一份規格的緊湊形態：只畫價格圖一個 grid、唔帶成交量格與現價大字，縮放平移照常，多格界面因此唔使第二份規格），`brokery/static/chart_grid.js` 是唯一一份**多格**規格（`window.BrokeryGrid.build(el, {ktypes, onPick})`：一格一週期，每格上方一排水平週期按鈕只有當前者高亮，頁內零文字（按鈕只帶 `1m`/`day` 呢類語言中性嘅週期名，換語言唔使重建格子），`set(i,…)` 只重畫一格、`takePicks()` 供桌面 GUI 輪詢（QWebChannel 喺 offscreen 載入即 segfault，已實測）），`brokery/chart.py` 是 Python 側唯一入口（`payload`/`render_js`/`BarStore`，多格一側為 `grid_page`/`grid_js`/`grid_set_js`/`grid_note_js`/`grid_picks_js`）；`echarts.min.js` 為本地 vendor（已無 CDN，故 GUI 與 Docker 離線都畫到圖）。**疊加指標是資料不是圖**：由 pandas 按 `OVERLAY_COLUMNS`（`code/kind/name/start_ts/end_ts/start_price/end_price/side`）算出行，`chart.js` 只把行變圖形，`overlays.register(kind, fn)` 為掛點（內置 `zone`/`line`；日後 ICT order block 只 register 一個函數，三處自動一樣）。序列合併規則三處同一口徑（key=(code,ts)、同 `ts` 以新到者覆蓋、每個代碼只保留最新 N 根、內部一律升序；「最新在最上」只屬顯示層）。`BrokeryChart.create(el, opts)` 為一圖一實例（`update`/`overlays`/`reset`/`destroy`，各自記自己的縮放範圍，故串流 `update` 唔會跳返原位），**縮放、平移、雙擊復原與現價水平線一律由這份規格提供，界面不寫一行**（滾輪縮 X 軸、Shift+滾輪只縮 Y 軸即單軸、拖曳左右平移、雙擊復原、現價線取序列最後一根的收市價）；`run_chart_spec.py` 47 項檢查全過（含真畫到嘢、真滾輪/真拖曳/真雙擊、同一實例可重用、`store().setLimit()` 令上限跟界面請求的根數、`render()` 每次都帶規格（換週期後 x 軸格式跟住改）、現價大字只在價格真的改變時閃一次，並真執行 Python 生成的 `render_js`；`compact` 時 `option()` 只一條 series 一個 grid 無現價大字，非 `compact` 逐項照舊；`BrokeryGrid` 九格九實例互不影響、撳按鈕只重畫一格並只上報 `[格, 週期]`、`takePicks()` 取走即清空、`resizeAll()` 涵蓋全部格子） |
| 一次過啟動閘道與 Web UI `run_all.py`（其中一個先結束即停止另一個，Ctrl+C 一併停止） | ✅ 可用 | 實測 `python run_all.py`：兩個端口同時回應、Web UI 可經剛啟動的閘道取數、送 Ctrl+C 後兩個一併退出且端口釋放；`run_launch.py` 7 項檢查全過（存根命令，不需券商連線，亦不真的啟動服務） |
| K 線串流 `stream_kline`（一條連線同時串流多個代碼，同一條連線亦可並行多個週期，同一週期亦可並行多條） | ✅ 可用 | FUTU 實時推送 + IB `keepUpToDate` + Tiger `subscribe_kline` 原生推送 + Webull 輪詢批量 bar（憑證只開通 HK 行情，美股明確報錯 `market_data_not_subscribed`）；實測 futu/ib/tiger/webull 全部合規格（Tiger 一條連線同時串流港美 3 個代碼；Webull 以 2 個 HK 代碼共用一次輪詢）；推送本身要開市才收得到。**多週期並行**：可並行的週期一律由適配器聲明（`SymbolBroker.stream_ktypes`；futu 為全部 9 個、IB 為其 `BarSize` 表、tiger/webull 只聲明 `1m`），futu 實測同一條連線並行 1m/3m/5m 時各週期取到自己週期的 bar（`ts` 間距分別為 60/180/300s 的整數倍）且沒有另開連線；**同一週期的第二份照樣並行**——上游訂閱按**（代碼, 週期）引用計數**，並行期間不退訂閱，全部結束才退一次（見 §17）；`run_stream_kline.py` 35 項 PASS / 5 FAIL，5 個 FAIL 全部係 IB 連唔到 TWS（`WinError 1225`，屬環境而非代碼） |

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
| `source` | 資料來源券商 |

不設到期月欄：期貨的到期月一律含在 `symbol` 內（主連帶 `main` 等後綴、個月份為 root+到期月，如
`US.ES202612`），故 `code` 本身即合約身份。券商原生標識（IB 的 `conId`、Webull 的 `instrument_id` 等）
不在統一格式重複承載，需要回溯時用 `raw=True` 取原生格式。

### 2.1 原生格式 `raw=True`
七個連券商的方法（`list_stocks`／`list_futures`／`list_indices`／`list_all`／`get_kline`／`stream_kline`／
`get_accounts`）一律接受 `raw=True`：信封仍只有三鍵，`data` 直接是該券商自帶的欄位與值，欄位順序即上游原樣。

* **只換欄位與格式，不改取數範圍與數值**：同一請求的市場、bar 數、篩選範圍與價格一律不變（實測同一
  K 線 raw 與統一格式的收市價逐根相同，最大相差 0.0）。
* 因此 raw 會跳過只認統一欄位的後處理：不按統一鍵去重（同一合約的多列原生行全部保留，故行數不少於
  統一格式），亦不按 `market` 做行過濾（原生行無該欄位，市場範圍一律由市場參數／種子保證）。
* 由適配器構造的欄位（`ts`、`source`、`symbol_type` 等）不出現；上游本來就有的鍵一律保留，包括富途
  自帶的 `code` 與 `acc_type`（名稱、寫法與值均為上游原樣，不改寫）。
* 時間欄位即各家自己的寫法：富途 `time_key`、Tiger／Webull `time`、IB `date`。raw 的串流合併
  （`NativeBars`）與 `BarMerger` 對外語義一致：只在最新一根有變化時回報、只留最近 count 根、按原生
  時間升序（各家的時間形態不同，故數字與文字各自成組）。
* 能力閘與參數邊界不受 raw 影響：未聲明的品種仍在發出請求前即 `type_unsupported`；`get_accounts` 在
  raw 下明確要求 `acc_type` 一律拒绝（原生記錄無該欄位，不能假裝已過濾），不支持的幣種仍明確報錯。
* 失敗時仍為三鍵信封，空表不帶欄位（原生欄位無從得知）。

```python
bk.get_kline("HK.00700", ktype="day", count=10, broker="futu", raw=True)  # data 即富途的 time_key 等欄位
bk.get_accounts(broker="futu", raw=True)                                  # data 即富途自帶的戶口記錄
```

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
| Webull | `list_instruments` 按 `category` + `sub_category` 分頁（每頁 1000，只取 `status=OC`，故隔走認股證與 CBBC） | HK 3,170／US 12,306；`exchange` 為 Webull 自有的場所代號（HKG／XGEM／NAS／NSQ／NMS…），各券商對同一場所的寫法本來不同，不憑空歸一；原生 `instrument_id` 只在 `raw=True` 的原生格式中出現 |
| IB | **不提供**：無「一次列出全市場股票」的接口（空 symbol 的 `reqContractDetails` 150s 無回應、`reqMatchingSymbols` 只為 top-N 且混入 BOND、`reqScannerData` error 162） | 能力未聲明，`core` 返回 `no_source: 已啟用的券商（ib）不提供股票清單`，UI 顯示「不提供此清單」 |

### 4. 期貨清單
```python
bk.list_futures()                          # 內建種子（ES/NQ/YM/RTY/VIX/CL/GC/SI/HG/ZN/ZS/ZW/ZC/HSI/MHI）
bk.list_futures(["ES"])                    # 指定產品
bk.list_futures(["ES"], markets=("US",))   # 期貨接口沒有市場參數：markets 按返回行的 market 過濾
```
主連以 `main` 後綴表示；個月份的到期月一律寫進符號（統一格式不設到期月欄，合約必須由代碼唯一標識）。
四家全部提供，但取得方式與月份寫法不同：

| 來源 | 取得方式 | 主連 | 個月份代碼 |
| --- | --- | --- | --- |
| FUTU | 按市場一次列舉全部期貨（實測港美 14,078 條） | `US.10Ymain`（另有 `current`/`next`/`day`） | 富途原生代碼 `US.10Y2609`（YYMM） |
| IB | 依內建種子展開（ES/NQ/YM/RTY/VIX/CL/GC/SI/HG/ZN/ZS/ZW/ZC/HSI/MHI） | `US.ESmain`（IB `CONTFUT`，含 conId） | `US.ES20261218`（root + IB 的最後交易日 `YYYYMMDD`） |
| Tiger | 原生批量：`get_future_exchanges` + `get_future_contracts`，不需種子（實測 649 條，含種子外的 MEUR／ZM／XW 等；`trade=False` 者不列） | `US.ESmain` | `US.ES202512`（root + `contract_month`） |
| Webull | 無批量接口：按種子 root 逐個 `get_futures_instrument(code=root)` 展開（實測 41 條／14 個 root） | 無主連概念，不憑空補 `main` 行 | `US.ES202612`（root + `contract_month`）；只掛近月（實測美股每個 root 只有最近兩個月）；種子中無提供者（實測 VIX）返回空，不憑空補出 |

預設四家都會取，結果合併去重；只要其中一家，用 `Brokery(sources=("futu",))`。同一 root 的各月份是
不同的行（到期月已含在符號內），`code` 即合約身份，故去重鍵為 market + symbol_type + symbol。去重後
某家可能不再出現：其提供的合約若全部已被別家覆蓋，即只保留一份（實測 Webull 的 ES 兩個月與 Tiger
逐欄相同，`message` 仍為 `ok`）；同一合約在多處掛牌（如 CME 與 QBALGO）只保留主場。各家的月份寫法與
產品代碼本來不同（富途 YYMM、IB 最後交易日、Tiger／Webull `contract_month`），只有寫法一致者會被合併，
不憑空對齊。

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
bk.convert("US.ES20261218") # 個月份亦可輸入；代碼自帶到期月，原樣返回（與清單所出者一致），到期月只作 IB 的合約參數
```
IB 原生合約轉回統一代碼：`brokery.brokers.ib_broker.IbBroker.to_unified_code(contract)`。

### 7. 離線存放
所有取得的資料統一經 `brokery.store` 寫入離線資料目錄（預設 `brokery/data/`，路徑讀
`.env` 的 `BROKERY_DATA_DIR`，不入版本控制）。每個資料集一檔 `<name>.parquet`，另有一份
`<name>.meta.json` 記錄行數、欄位、來源與寫入時間（UTC），方便日後判斷是否過期。
覆蓋寫入是先寫 `<name>.parquet.tmp` 再 `os.replace`，故中途斷電或寫入失敗不會留下半檔；被覆蓋
的舊檔保留為 `<name>.prev.parquet`（只一份，供誤覆蓋後回溯）。

```python
from brokery import store

store.save_frame("futu_codes", df, source="futu", note="港美全量 CODES")  # 覆蓋寫入
df = store.load_frame("futu_codes")      # 未存放時拋 StoreError，不會以空表冒充「沒有」
store.load_meta("futu_codes")            # {'rows': 38568, 'saved_at': '2026-10-10T12:30:00+00:00', ...}
store.list_stored()                      # 目錄內所有已存放的資料集
```

`Brokery.get_code()` 讀回同一份資料，但走統一入口並返回標準信封（未存放時 `status=False` 並在
`message` 說明先執行邊個腳本）。離線 CODES 按券商各存一檔 `<broker>_codes.parquet`，預設讀
`store.codes_dataset(CODES_SOURCE)`（即 `futu_codes`）：

```python
bk.get_code()                            # {'status': True, 'data': 38568 條, 'message': 'ok: 離線讀回 …'}
bk.get_code(broker="ib")                 # 讀 ib 那一檔（ib_codes）
```
離線檢視可直接跑 `python brokery/acceptance/run_get_codes.py`（可帶 `STOCK`/`FUTURE`/`INDEX`
參數只顯示某一類型），不需要任何連線。IDE 的 parquet 預覽會把字串欄位顯示成位元組數組，屬檢視器
限制，檔案內容本身正常，以 `load_frame` 讀回即為正確文字。

#### 更新離線 CODES
讀一份快照 0.03 秒，向富途重拉港美全量約 6 秒（實測 38,569 條），相差約 250 倍：搜尋與離線檢視一律
讀快照，重拉放喺請求路徑之外。快照因此需要更新，但快照往往是唯一嘅離線副本，所以更新嘅設計重點係
「幾時拉」與「點樣唔搞壞一份好嘅快照」：

```python
bk = Brokery()
bk.get_code_meta()                       # 一行：行數、欄位數、saved_at、age_seconds、stale、last_refresh_error
bk.refresh_codes()                       # 重拉 DEFAULT_STOCK_MARKETS（HK/US）全量並覆蓋快照；force=True 跳過過舊判斷
bk.refresh_codes(["HK"])                 # 只拉部分市場（會被下面的縮細防護拒絕，除非 force=True）
bk.refresh_codes(broker="ib")            # 只更新 ib 那一檔（ib_codes）
```

- **每家一檔**：`<broker>_codes.parquet`，讀寫與防護都只針對該家。各家的標識体系與能力不同（IB 以
  conId/ISIN 且不提供股票、Webull 不提供指數），混進同一檔會互相污染，縮細防護亦無法逐家比較。
- **照能力存放**：快照內容由該適配器聲明的 `capabilities` 決定，不提供即由 `_gather` 明確報錯，不為
  湊齊而造數；故 `ib_codes` 只有期貨與指數屬正常狀態，並非缺數。
- **縮細防護**：按 `symbol_type` 逐個比較，任何品種少於同一券商上一份快照的 `CODES_MIN_KEEP_RATIO`
  （0.9）即拒絕覆蓋，原因寫進 `message`，快照保持原樣。一次部分市場失敗唔應該把全量快照削走一半。
- **沿用舊快照**：某品種本次取唔到（實測指數清單被拒），該品種沿用舊快照的行，其餘照常更新，
  `message` 說明沿用了幾多條。
- **失敗也留痕**：失敗原因記進 meta 的 `last_refresh_error`，界面讀回時以警告色提示，唔會靜靜當做成功。
- **過舊的界限**：`.env` 的 `CODES_MAX_AGE_HOURS`（預設 24）決定 `stale`；閘道啟動時若 `CODES_SOURCE`
  （預設 futu）那一檔已過舊，會喺背景线程自動重拉一次（`brokery_api/app.py: auto_refresh_codes`），
  唔阻塞啟動、亦唔放進任何請求；其餘各家只由用戶在界面按「更新離線 CODES」觸發。
- 三個界面（dashboard、Web UI、桌面 GUI）都另列一行顯示**所選券商**快照的行數與距今時間，並有兩個按鈕：
  「讀取離線 CODES」只讀該家那一檔（不打券商，明確標註未向券商取數）、「更新離線 CODES」只向該家重拉；
  該行與即時取數的統計分開，快照狀態唔會混入各來源的條數。標的頁嘅定時更新預設只重讀離線快照，另有
  「自動向券商重拉」開關（預設關閉）才改為向券商取清單。

### 8. K 線
```python
bk.get_kline("HK.00001")                                  # 富途日線最近 60 根
bk.get_kline("HK.00001", ktype="5m", count=200)          # 日內
bk.get_kline("HK.00001", broker="ib", autype="none")     # 同一組 bar，改經 IB 取
bk.get_kline("HK.00005", broker="ib", autype="qfq")      # IB 前復權（僅日內/日線，因子與富途不同）
bk.get_kline("US.NVDA", ktype="day", count=3000)         # 根數可任選：不足即自動補富途歷史接口
bk.get_kline("HK.00001", autype="hfq")                   # 後復權（只有富途支援）
Brokery(autype="none")                                   # 全域預設複權模式，逐次呼叫可再覆蓋
```
`ktype` 為 `1m/3m/5m/15m/30m/60m/day/week/month`；`count` 一律是 **bar 數**（富途語義），**與週期無關**：
各家一律取盡自己在該週期可取的深度，唔會因為取數路徑而少返（富途實測傳 1000 根時 `1m`–`week` 皆得 1000 根，
`run_futu_kline.py` 13 項離線檢查即重現呢個口徑）。該標的在該週期確實無咁深時 `status` 仍為 `True`，
但 `message` 會點名該來源的實際深度（`ok: 257 根 month K 線（…），futu 的 month 深度只有 257 根（請求 1000 根）`），
唔會靜靜少返。`broker` 選來源，`autype` 為 `qfq`/`hfq`/`none`（見下）。`data` 的欄位固定為 `brokers.base.K_COLUMNS`：

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
| FUTU | 原生就是 bar 數，但 `get_cur_kline` 對多數週期只給最近幾十根（實測傳 1000 根時只有 `1m`/`15m` 給足），故它只作快路徑：不足即以 `request_history_kline` 按日期範圍分頁多取，兩段按 `ts` 去重合併（同一根以快路徑者為準，其價格為最新狀態）再截尾。起日由 `span_days` 推算，過早會被上游拒（F3CNN 錯誤），故把跨度折半重試至一年下限，仍失敗即明確抛出而不少返 | `qfq`/`hfq`/`none`（所有 ktype） | 有 |
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

**同一條連線亦可並行多個週期，同一週期亦可並行多條**：可並行的週期一律由適配器聲明（`SymbolBroker.stream_ktypes`：
futu 為全部九個、IB 為其 `BarSize` 表、tiger/webull 只聲明 `1m`）。富途的推送回呼（`_KlinePushRouter`）按推送行上的
`k_type` 分派給各週期各自的接收器，故 1m/3m/5m 並行時各週期取到自己週期的 bar（實測 `ts` 間距分別為
60/180/300s 的整數倍）且沒有另開連線；同一週期的第二份（例如另一個代碼，或另一條同週期的串流）照樣並行——富途的
上游訂閱按**（代碼, 週期）引用計數**，最後一份結束才 `unsubscribe`，故並行時不會互相蓋走訂閱（舊行為「同週期第二份
即拒」已移除）。IB 每個（代碼, 週期）各自一次 `reqHistoricalData(keepUpToDate)`，本來就可並行。界面如何用一條
連接覆蓋九個週期見 §17。

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
| `GET /codes?broker=` | `get_code`（離線讀回該券商那一檔 `<broker>_codes`；不带 `broker` 即 `CODES_SOURCE`） |
| `GET /codes/meta?broker=` | `get_code_meta`（該券商快照的行數、距今時間、是否過舊、上次更新失敗的原因；離線讀回，不需券商連線） |
| `GET /codes/refresh?broker=&markets=` | `refresh_codes`（重拉全量並覆蓋該券商那一檔；需券商連線，約數秒。不带 `markets` 即全量，只拉部分市場會被縮細防護拒絕） |
| `GET /stocks?markets=&raw=`、`/futures?roots=&raw=`、`/indices?symbols=&raw=`、`/all?markets=&raw=` | 各標的清單 |
| `GET /convert?code=&source=` | `convert` |
| `GET /kline?code=&ktype=&count=&broker=&autype=&raw=` | `get_kline` |
| `GET /accounts?broker=&acc_type=&currency=&raw=` | `get_accounts` |
| `GET /brokers?broker=` | `get_brokers`（各券商連線狀態與延遲） |
| `WS /stream` | `stream_kline`（協定見下，訂閱訊息可帶 `"raw":true`） |

- **鑑權**：金鑰自訂（`.env` 的 `API_KEY`，未設即拒絕啟動並明確報錯）。HTTP 受理 `X-API-Key`
  或 `Authorization: Bearer` 其一（缺少 401、不符 403）；WebSocket 因瀏覽器不能自訂握手標頭，另受理
  `?api_key=`（不符即以 code 4403 關閉）。
- **返回**：一律 HTTP 200，`{"status":bool,"data":{"columns":[…],"rows":[[…]]},"message":str}`，`data`
  即 DataFrame 的欄位與行；缺失值一律為 `null`（不出現非法的 `NaN`）。業務失敗（`unknown_source:`、
  `no_account:` 等）由 `status=False` 表達，原因原樣透傳，不變成 HTTP 500。
- **原生格式**：上述六個取數端點一律接受 `raw=1`（`1`／`true`／`yes`／`on` 同義），此時 `data.columns`／`data.rows`
  即該券商自帶的欄位與值，取數範圍與數值不變；不帶該參數時仍為統一欄位。
- **串流**：送 `{"action":"subscribe","codes":[…],"ktype":…,"count":…,"broker":…,"autype":…}`，
  收 `subscribed` → 每次推送為 `update`（附該代碼目前**完整**的序列，客戶端整份覆蓋，不做本地合併）
  → 到時結束為 `end`；送 `{"action":"stop"}` 即 `closed`（只帶 `ktype` 時只停該週期的各條，逐條各發一份；
  `closed` 仍附 `release_in` 說明該執行緒還差多少秒才真正收尾，但界面已不再照它倒數）。
  **一份串流由「請求簽名」界定**（券商、週期、代碼、根數、複權、raw）：同簽名即同一份請求，可被**多條連接
  同時訂閱**——閘道只向券商訂閱一次，每條連接各收到同一份 `update`（`subscribed` 帶 `shared`），故桌面 GUI 與
  Web UI 可同時睇同一張圖；其中一方停止或斷線不影響另一方，最後一方退出才結束該串流。該執行緒要到時窗走完
  才停下，故一時無人收時照樣仍在——同一份請求再訂閱即**接手**那條仍在推送的串流（`subscribed` 帶 `resumed`，
  `seconds` 為剩餘秒數），不重新向券商訂閱。**簽名不同即另一條串流，同一券商同一週期亦可同時並行多條**
  （例如兩格同週期但代碼不同，或根數不同），各自向券商訂閱、各自收推送，閘道不再返回 `stream_busy`，界面亦
  沒有名額可等。剩下的拒絕只係「改參數先解決到」的協定錯誤（`ktype_unsupported`、`broker_disabled`、
  `bad_request`），其 error 帧點名 `broker`/`ktype` 且不收線，由用戶改參數，界面不自動重送訂閱。歷史起點由
  `/kline` 取，`/stream` 只推更新。
  ktype、複權與品種是否支持一律由 Brokery 判定，閘道不另設規則。
- **日誌**：每個請求與每個業務結果一律寫入控制台、`logs/brokery_api.log`（滾動檔）與記憶體環形
  緩衝（由 `/logs` 讀）；自訂金鑰一律遮罩，不會落入日誌檔。
- **連線狀態**：dashboard 頂欄以四家券商的指示（可連／斷開 + 延遲毫秒，懸停顯示原因與戶口數）顯示，
  由 `/brokers` 於頁面載入時探測一次，其後只由「探測連線」按鈕手動觸發（探測會真的向各家發請求，
  故不設定時輪詢）。
- **戶口頁**：沒有「來源」選擇，一律一次取四家全部戶口（請求不带 `broker` 參數）。進入該頁即取一次，
  其後按「自動更新（秒）」填的間隔重取（只在該頁可見時才請求；**預設 0，即完全不自動請求**；「取得戶口」
  手動刷新照樣可用）。頁頂按來源列出各券商的戶口數，沒有返回者點名，避免用戶只見到「少咗一間」而不知原因。
- **標的頁**：即時清單（股票／期貨／指數／全部）按來源分四區同時顯示 —— 一次點擊即四區一起填充
  （後端本来就是一次向各家取齊，不需逐間點），區內不再重複 `source` 欄。每區如實顯示該家狀態：
  「N 條」／「無返回」（理應有份却取不到，如未連線或無行情權限）／「不提供此清單」（該券商本就不提供
  該清單，如 IB 無股票清單、Webull 無指數清單，依 `/capabilities` 的能力聲明判定）——三者含義不同，
  不可混為一談。個別券商失敗時 `message` 以警告色顯示，結果仍算成功。各區欄位一律為
  `brokers.base.COLUMNS`（8 欄，順序即接口原樣，只去掉區內重複的 `source` 欄）。
- **離線 CODES**：存放好的快照不涉及即時取數，故不分區，以單一表格顯示（`source` 保留在欄位中）。
  該頁另列一行顯示**所選券商**那一檔的行數與距今時間（`/codes/meta?broker=`），過舊時以警告色而非錯誤色
  提示（已存放的資料仍可用）；「讀取離線 CODES」只向 `/codes?broker=` 讀該家那一檔（不打券商）、「更新
  CODES」只向 `/codes/refresh?broker=` 送出且不带市場參數，完成後原樣顯示更新報告（含各品種增減與沿用
  舊快照的說明），再重讀快照與表格；換券商即改讀該家那一檔，顯示的只是該家的行數。本頁是唯一以自由文字
  搜尋離線快照的界面，故搜尋零結果且快照過舊時會提示按「更新 CODES」——查唔到往往只係快照冇咗新上市的
  代碼。
- **標的頁的定時更新**：同戶口頁一樣以秒為單位，**預設 0（不請求）**；非 0 時預設只重讀離線快照（不打
  券商），另有「自動向券商重拉」開關（預設關閉）才改為向券商取清單。請求進行中不會再排下一次，進入該頁
  或改動秒數即重新計時。
- **讀取提示**：所有取數（K 線、戶口、標的、日誌、探測）在請求進行時明確顯示「讀取中…」並以強調色
  標示，同時禁用觸發按鈕防止重復送出；較快的請求（如日誌）會延後約 0.4 秒才顯示，避免閃爍。
- **金鑰記憶**：dashboard 填入的金鑰即時存入瀏覽器 `localStorage`（鍵 `gw_key`），重新載入或重開頁面
  自動回填，其後所有請求（含 WS 訂閱）自動帶上，不需每次重填。

### 12. 量化交易 Web UI（`brokery_webui`）
與 `brokery/`、`brokery_api/` 同級的獨立進程：上方為菜單六項——「戶口清單」（四家的戶口與資金同屏）、
「標的列表」（上方為類型／市場／券商篩選，下方為取得的清單，默認富途）、「K 線拉取」「K 線串流」
（兩頁同一控制列與同一張下方表格；串流頁另在表格上方畫出 K 線圖，見下）、「K 線串流（多週期）」
（3×3 九格同時串流，下方無表格，見 §17）與「BROKER 管理」（券商開關，見 §15）。

```bash
python brokery_webui/run.py   # 監聽 .env 的 GUI_HOST/GUI_PORT；需先啟動 brokery_api 閘道
```

- **只負責頁面與轉發，不連券商**：`/api/accounts`、`/api/capabilities`、`/api/symbols`、`/api/kline`、
  `/api/brokers/prefs` 與 `/api/codes`、`/api/codes/meta`、`/api/codes/refresh`（一律帶 `broker`，即當前所選券商）以 `X-API-Key`
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
- **離線 CODES**：標的頁另列一行顯示**所選券商**那一檔的行數與距今時間（轉發 `/codes/meta?broker=`，離線
  讀回，不需券商連線，故與即時取數的統計分開），過舊或上次更新失敗以警告色提示；「讀取離線 CODES」轉發
  `/codes?broker=`（只讀該家那一檔，並明確標註未向券商取數）、「更新離線 CODES」轉發 `/codes/refresh?broker=`
  且不带市場參數，結果（含各品種增減）原樣顯示後重讀該家那一檔的狀態；換券商即改讀該家那一檔。本頁沒有對
  快照的自由文字搜尋，故不提供「查唔到即提示更新」。
- **定時更新（秒）**：戶口頁與標的頁各有一個「自動更新（秒）」輸入，**預設 0 即完全不請求**；非 0 時只在
  該頁可見時才排下一次，請求進行中不會重複送出，進入該頁或改動秒數即重新計時。標的頁的定時更新預設只
  重讀離線快照，勾上「自動向券商重拉」（預設關閉）才改為向券商取清單。
- **K 線兩頁**：控制列一律為標的（預設 `HK.HSImain`）、週期（由 `/api/capabilities` 的 `ktypes` 填充，預設
  `1m`）、根數（預設 1000，**可任選數字**，上限 100000，與桌面 GUI 一致；該標的在該週期無咁深時 `message`
  會點名該來源的實際深度，見 §6）、券商（只列生效的家，預設 futu）。取歷史一律經 `/api/kline` 轉
  `/kline`，界面不另設一套參數判定。下方表格欄位即 `K_COLUMNS`，**列出接口返回的全部行**（不做「只列最近
  N 行」的截斷：原數據是幾多根就列幾多行），**按時間反序（最新在最上）**；升序只存在於
  合併用的序列，反序屬顯示層，故圖表與跨券商對齊不受影響。
- **K 線串流**：`WebSocket /ws/stream` 連上游 `ws://…/stream?api_key=`，訂閱幀與 `update` 雙向原樣透傳，上游
  不可達即返回明確 `error`（不把連線失敗留給頁面猜），金鑰仍只在服務端。按「訂閱實時」即**先取歷史、再開串流**
  （先向 `/api/kline` 取控制列現值的歷史，歷史已在圖上才建立連接；取不到歷史即不訂閱，免得得返一張只有最近
  幾十根實時 bar 的圖）。收到的 `update` 只帶最近 `count` 根，故一律與已拉取的序列合併（key=(code,ts)、同 `ts`
  以新到者覆蓋、保留最新 N 根），不會把 1000 根歷史縮返最近幾根；N 即控制列所填的根數（`store().setLimit()`，
  寫死時取 3000 根會被裁返 1000）。一個訂閱只開一條上游連接；多週期頁（§17）的九個訂閱同样只用一條——瀏覽器對
  同一來源的 HTTP/1.1 連線約得六條，九條會直接排唔上，所以分派靠 `update` 自帶的 `ktype` 而唔靠連接。
- **沒有名額可等，協定錯誤原樣呈現**：一份串流由請求簽名界定（見 §11），同一券商同一週期可同時並行多條，閘道
  不再返回 `stream_busy`，故界面已沒有倒數與自動重送（舊的「名額尚未釋放，約 N 秒後自動訂閱」一律刪除）。同簽名
  即同一份：桌面 GUI 與 Web UI 填一樣參數即同時收同一份 bar（`subscribed` 帶 `shared`），一方已訂閱時另一方再送
  即接手（帶 `resumed`），唔使等。剩下被拒的只有「改參數先解決到」的協定錯誤（`ktype_unsupported`、
  `broker_disabled`、`bad_request`）：`error` 帧點名 `broker`/`ktype` 且**不收線**，頁面把原因原樣顯示、不自動重送
  訂閱，按鈕亦唔解鎖，由用戶改參數或撳「停止」收返呢條連接（與桌面 GUI 同一口徑，見 §13）。
- **K 線圖在 DF 上方**：圖表由那份共用的 `brokery/static/chart.js` 畫（經 `/static/chart.js` 與本地
  `/static/echarts.min.js`，已無 CDN），頁面不寫 series 與座標軸（見 §16）；縮放、平移、雙擊復原與現價線一律由
  那份規格提供，頁面不需要傳任何交互參數；開圖時傳 `start: 0`，即本次所請求的根數全部喺圖上（`dataZoom` 照可
  再收窄，`DEFAULT_START` 只是省略該項時的預設）。圖與下方表格讀同一份合併後的序列，故兩者看到的根數與時間範圍
  永遠一致；換週期後 x 軸格式即跟住改（規格屬該次輸入的一部分，每次渲染都要交）。圖高為固定的 420px（瀏覽器
  內不隨視窗拉伸，與桌面 GUI 的「K 圖佔頁面一半以上」屬兩回事）。
- **BROKER 管理**：開關列出全部券商（含未配置者，否則被停用者會由頁面上消失、無法再啟用），「套用」一次交齊
  完整生效名單到 `/api/brokers/prefs/update`，並直接以回應重畫（回應即最新狀態，不需再讀一次）；成功後重讀
  `/api/capabilities`，各頁的券商下拉框即時去掉被停用者。
- **日誌**：與閘道同一套（級別與目錄由 `API_LOG_LEVEL`/`API_LOG_DIR` 決定），但寫自己的
  `logs/brokery_webui.log`：兩個進程共用同一個滾動檔會在滾動時互相搶佔句柄。

### 13. 量化交易桌面 GUI（`brokery_gui`）

與 Web UI 同一功能的桌面窗口（PySide6）：六個分頁——「戶口清單」「標的列表」（類型／市場／券商篩選在上、
清單在下，默認富途）、「K 線拉取」「K 線串流」（串流頁在表格上方畫出 K 線圖，見下）、「K 線串流（多週期）」
（3×3 九格同時串流，下方無表格，見 §17）與「BROKER 管理」。標的列表為**上下兩張表**：上方為
該券商自帶的欄位與格式（`raw=True`），下方為統一格式，兩張表同一時刻用同一篩選條件，可直接對照同一份資料在
轉換前後的样子。

```bash
python brokery_gui/run.py     # 閘道地址與金鑰讀自 .env 的 API_HOST/API_PORT/API_KEY；需先啟動閘道
```

- **界面與文字分離**：七個 `.ui` 檔（`main_window`、`accounts_page`、`symbols_page`、`kline_pull_page`、
  `kline_stream_page`、`kline_grid_page`、`brokers_page`）在運行時由 QUiLoader 載入，檔內不含任何文字；多週期頁連
  週期下拉框都冇（週期由該券商聲明的 `stream_ktypes` 生成嘅按鈕決定），故檔內亦無該類控件；顯示文字
  一律按鍵取自 `locales/<語言>.json`。分頁以 object name 辨認（不按 index 硬編碼），故增減分頁不會錯頁觸發。
- **三種語言即時切換**：繁體中文／简体中文／English 各一個 `.json`（三者鍵集合一致），頂欄切換即重貼標籤，不需
  重建窗口、亦不重新取數；缺譯時返回鍵名本身，不憑空造一句湊數。
- **取數只經閘道**：與 Web UI 同一理由（閘道已持有各券商連線，IB 只容許一個 client id）。請求在背景執行緒進行，
  界面不會因券商連線（IB 可達 40s）而凍結；失敗口徑與閘道一致（`gateway_unreachable:`／`gateway_http_403:` 原樣
  顯示，狀態列同時標為「取數失敗」），未設 `API_KEY` 即在啟動時拒绝建立客戶端。
- **表格即契約**：欄位與順序一律由返回的 `columns` 決定（即 `ACCOUNT_COLUMNS`／`COLUMNS`，上方 raw 表則為該券商
  自帶的欄位），不另設欄位；缺失值顯示破折號、資金欄為千分位兩位小數、按來源統計條數（只統計實際返回者）；券商
  選項由 `/capabilities` 的能力聲明填充（默認 futu，不提供該品種者標註原因且不可選），市場選項只由實際返回行的
  `market` 填充，轉類型即重設為全部。
- **離線 CODES**：標的頁另列一行顯示**所選券商**那一檔的行數與距今時間（經 `/codes/meta?broker=`，離線讀回，
  不需券商連線，故與即時取數的統計分開），過舊或上次更新失敗以警告色（`COLOR_WARN`）而非錯誤色提示；
  「讀取離線 CODES」只向 `/codes?broker=` 讀該家那一檔、「更新離線 CODES」只向 `/codes/refresh?broker=`
  送出且不带市場參數，結果原樣顯示並重讀該行；換券商即改讀該家那一檔；該列的文字屬語言鍵，切換語言時一併
  重貼（重繪不需重新取數）。
- **定時更新（秒）**：兩個分頁各有一個「自動更新（秒）」數字輸入，**預設 0 即完全不請求**；由一個 1 秒的
  `QTimer` 統一計時，只對當前分頁觸發，請求進行中（`_inflight`）不再排下一次，切換分頁或改動秒數即重新
  計時。標的頁的定時更新預設只重讀離線快照，勾上「自動向券商重拉」（預設關閉）才改為向券商取清單。
- **兩張表順序取數**：同一篩選條件先取統一格式、再帶 `raw=1` 取一次（同一閘道持有各券商連線，IB 只容許一個
  client id，故不併發）；兩張表各自顯示自己的失敗原因，舊回應不會蓋過已改變的篩選條件。
- **K 線兩頁**：控制列與 Web UI 同一口徑（標的預設 `HK.HSImain`、週期由 `/capabilities` 的 `ktypes` 填充並預設
  `1m`、根數預設 1000 但**可任選數字**（上限 100000；實際可得根數取決於該來源在該週期的可取深度，不足時
  閘道的 `message` 會點名該來源的實際深度）、券商只列生效者）；表格欄位即 `K_COLUMNS`，**列出返回的全部行**
  （不做「只列最近 N 行」的截斷）並按時間反序（最新在最上），另按來源統計根數。兩個單格 K 線頁各持一個序列容器
  （控件參照 + `chart.BarStore` + 串流客戶端），其上限跟隨本次請求的根數（`BarStore.set_limit`），故取 3000 根
  不會被裁返 1000 根；取數路徑只有一條。多週期頁（§17）唔屬呢個單格模型：一格一份 `BarStore`，但全頁只有一條
  串流客戶端。
- **K 線串流**：`brokery_gui/stream.py` 以 `QWebSocket` 對 `/stream`（桌面端不直接連券商，理由同取數），收到的事件
  轉成同名信號，不在客戶端解讀、合併或重排資料；`update` 一律經 `chart.BarStore` 合併（同 `ts` 覆蓋、保留最新
  N 根）。按「訂閱」即先向 `/kline` 取歷史、歷史已在圖上才建立連接（取不到歷史即不訂閱，不留一張只有實時 bar 的
  圖）；結束時連該條連接一併丟掉，故換參數重按「訂閱」不會被上一條連接擋住。
- **訂閱咗就唔好再訂閱，直接串流**：該串流執行緒要到時窗走完才停下——按「停止」只是提前收尾。故「停止」後再按
  「訂閱」同一份請求（同簽名）照樣送到閘道，由它接手仍在推送的串流，即刻繼續收（`subscribed` 帶 `resumed`）；
  界面唔會預先記低 `closed` 帧的 `release_in`（那只會白等一段根本唔使等嘅時間）。換咗參數即係另一條串流，同一
  券商同一週期照樣並行多條，兩邊唔使互相等（Web UI 同時訂閱同簽名即加入呢條串流，各收同一份 `update`，其中一邊
  「停止」或收線都唔影響呢邊，見 §12）。舊的 `kline.quota_wait` 倒數、`retry_stream` 與 `kline.wait_cancelled`
  已一併刪除（再無名額可等）。被拒只剩協定錯誤（`ktype_unsupported`、`broker_disabled`、`bad_request`）：
  `_on_stream_error` 把閘道點名的原因原樣以警告色顯示，唔自造原因亦唔代用戶重送訂閱（會話參數由用戶改，界面自己
  重送只會出現用戶看不見嘅訂閱），按鈕亦唔解鎖，由用戶撳「停止」收返呢條連接再改參數。
- **K 線圖在表格上方，且是可重用元件**（K 線串流頁）：`brokery_gui/chart_view.py` 的 `KlineChart` 把「圖表容器 +
  提示列 + 惰性 `ChartView` + 狀態提示」封成一個物件，界面只傳該頁的 `chartBox`／`chartNoteLabel` 與翻譯器；每個
  有 `chartBox` 的分頁各持一個（`pane.chart`，由該頁有無該容器決定，無圖的分頁為 `None`），不再由主窗口持有單一
  視圖，日後任何頁面要加圖即照這三行接駁。渲染只交一份 DataFrame 經 `brokery.chart.render_js` 注入，座標軸與
  series 全由那份共用的 JS 決定（用 WebEngine 而非 QtCharts，正是為了自定義指標在三個界面零翻譯）。圖與表格讀
  同一份 `BarStore`，故根數與時間範圍永遠一致；**渲染時傳 `start: 0`，即本次所請求的根數全部喺圖上**（唔再只顯
  最近幾十根；`dataZoom` 照可再收窄，`chart.js` 的 `DEFAULT_START` 只是省略該項時的預設；Web UI 同樣傳
  `start: 0`，兩個界面所請求的根數都全部喺圖上）。
  視圖惰性建立（首次進入該分頁才載入）；載入提示由視圖的載入狀態驅動（`ChartView.on_state`）：未就緒顯示
  「正在載入圖表…」、就緒即清走、起不來才顯示原因，不由界面猜，換語言時由元件自己重貼。視圖以 `Expanding` 並帶
  stretch 加入佈局，故圖佔盡圖表區的高度，提示列不與圖平分空間；圖表區與下方表格按 `.ui` 的 `verstretch` 3:2
  分配，故圖佔內容的一半以上。無顯示環境（offscreen、部分 Docker 鏡像）起不來時，下方表格照常填充並反序，功能
  不會半途而廢。
- **多週期頁的圖表容器**（`brokery_gui/grid_view.py`）：`GridView` 照 `KlineChart` 同一口徑（惰性 `ensure()`、載入
  提示由視圖狀態驅動、起不來顯示原因而唔係空白），但載嘅係 `brokery/chart.py` 的 `grid_page()`，格子由
  `BrokeryGrid` 喺 `QWebEngineView` 內生成。週期按鈕只帶 `1m`／`day` 呢類 token，完全唔涉及語言，故換語言唔使重建
  格子。按鈕嘅點擊靠輪詢 `takePicks()` 交回 Python（`QWebChannel` 喺 offscreen 載 `qrc:///qtwebchannel/qwebchannel.js`
  即 segfault，已實測），只在該分頁可見且載體頁已就緒時先輪詢，唔喺後台空轉（見 §17）。
- **BROKER 管理**：以開關列出全部券商（未配置者不可勾並顯示原因，那不是開關能改的事），「應用」一次交齊完整
  生效名單，直接以回應重畫，並重讀 `/capabilities` 令各頁下拉框即時去掉被停用者。
- **背景取數交回 GUI 執行緒**：取數在 `QThread` 進行，但 PySide6 中連到普通可呼叫物件的信號會在**發射**執行緒
  執行，在該處直接碰 `QWebEnginePage.runJavaScript` 即崩潰（`0x80000003`）；故回應一律經一個屬主執行緒的
  `ReplyRelay` 轉接，靠 Qt 的佇列連線交回 GUI 執行緒。

### 14. 一次過啟動閘道與 Web UI（`run_all.py`）

```bash
python run_all.py             # 兩個一齊起；只想起一個仍用上面兩個入口
```

- 兩個仍是各自獨立的進程，本檔只負責啟動與收尾：其中一個先結束（例如未設 `API_KEY`、或端口已被佔用）
  即停止另一個並原樣返回其退出碼，不會留半個系統在背景；Ctrl+C 一併停止，收尾有 10 秒上限，不無限等待。
- 本檔刻意不 import `brokery`：futu SDK 在匯入時即接管 SIGINT（自備的 `quit_handler` 直接結束進程），
  接管後 Ctrl+C 不會走到收尾，兩個子進程會變成孤兒。`run_launch.py` 有一項檢查專為守住這個前提。

### 15. 券商開關（BROKER 管理，全域生效）

「邊家券商生效」不再是改 `.env` 再重啟的事：三個界面都有一個 BROKER 管理頁，開關即時生效。

```python
from brokery import Brokery, prefs

# 閘道先讀檔再交俾 core（core 唔自己讀檔）；生效集合 = .env 的 API_SOURCES − 被停用者
bk = Brokery(disabled=prefs.load_disabled())
bk.get_broker_prefs()["data"]               # 一律列出全部可用券商：source/enabled/configured/detail
bk.set_broker_enabled(["futu", "ib"])       # 一次交齊完整生效名單；回應即最新狀態，不需重建
bk.get_kline("HK.00700", broker="webull")   # {"status": False, …, "message": "broker_disabled: webull（已在 BROKER 管理中停用）"}
```

- **存放**：`<data_dir>/broker_prefs.json`（`pathlib`，跨平台；資料目錄由 `.env` 決定），**只記被停用的家**。
  記全部名單的話，`.env API_SOURCES` 一改就會留下舊名單；只記差額就沒有這個問題。檔不存在或內容不可讀即
  全部生效（等同未用過這功能，不需遷移）；寫入為原子（`.tmp` → `os.replace`）。三個界面共用同一份檔。
- **由 `core` 統一執行，不在界面各處開關**：`Brokery.__init__` 照樣建立全部適配器，只把被停用者記在 `_disabled`
  （故重新啟用唔使重建物件，既有串流連線亦唔會變孤兒）。
  多券商路徑（`list_all`、`get_accounts(broker=None)`、`get_brokers()`）本來就只走生效集合，`/capabilities`
  也只列生效的適配器，因此**被停用者不會被任何動作經過，三個界面的券商下拉框自動更新**。
- **三種失敗分清楚**：已停用 → `broker_disabled:`；根本不在 `API_SOURCES` → `unknown_source:`；不提供該品種 →
  `type_unsupported`；連不上 → 該家的連線錯誤。全部停用時為 `no_source` 並點名被停用者，不砌出「已啟用的券商（）」
  這種空列表。背景自動更新（`auto_refresh_codes`）亦不會碰已被停用的預設券商。
- **界面以外不受影響**：喜好檔只由調用方（閘道）讀寫，`core` 只接受 `Brokery(disabled=…)` 而不自己讀檔；
  逐家循環的驗收與離線分析本來就唔傳 `disabled`，因此照 `.env` 取齊全部券商，用戶喺界面熄咗一家唔會令佢哋憑空失敗。
- **HTTP**：`GET /brokers/prefs`（讀）、`GET /brokers/prefs/update?enabled=futu,ib`（寫；省略參數即全部停用；
  名字原樣保留，不經大寫化）。`/health` 回報當前生效的來源與喜好檔路徑。

### 16. 共用圖表層（一份規格，三個界面同畫）

圖表只有一份定義，放在 `brokery/static/chart.js`（`window.BrokeryChart`）；Python 側唯一入口是
`brokery/chart.py`。閘道 dashboard、Web UI 與桌面 GUI 載入的是同一個檔案，所以任何指標在三處看到的完全一樣。

```python
from brokery import chart

bars = bk.get_kline("HK.HSImain", ktype="1m", count=1000)["data"]
chart.render_js(bars, ktype="1m")           # 可直接交 runJavaScript / <script> 的呼叫（GUI 用這個）
# Web 側則由頁面自行 load /static/chart.js 再 BrokeryChart.render(el, chart.payload(bars))
```

- **x 軸一律是原始 `ts`（UTC 秒）**，時間文字只由 formatter 產生。這是疊加指標能與 bar 對齊的前提：任何一側
  先把時間轉成文字，指標就會對唔齊。
- **疊加指標是資料，不是圖**：指標由 pandas 算出行，欄位即 `OVERLAY_COLUMNS`（`code/kind/name/start_ts/
  end_ts/start_price/end_price/side`），`chart.overlay_rows()` 只補齊欄位（缺值為 null，不憑空猜）。渲染層只把
  行變圖形：內置 `zone`（markArea）與 `line`，新指標只 register 一個函數，三處自動一樣。

  ```js
  BrokeryChart.overlays.register("order_block", (rows, api) => ({   // 例：ICT order block
      type: "line", markArea: { data: rows.map(r => [[
          {xAxis: r.start_ts, yAxis: r.start_price},
          {xAxis: r.end_ts, yAxis: r.end_price}]] } }));
  ```
- **一圖一實例（`BrokeryChart.create(el, opts)`）**：所有 K 線圖走同一個實例模組，實例自己記住縮放與平移的
  範圍，故串流每次 `update` 都不會把畫面跳返原位；`update`/`overlays`/`reset`/`destroy` 為界面唯一需要的動作，
  `opts` 為該次輸入的一部分（縮放範圍只作初始值，圖形規格 `ktype` 決定 x 軸的時間格式，故**每次渲染都要交**，
  只喺開圖時給一次的話界面換週期後 x 軸仍照舊格式）。`render()`／`resizeAll()` 只是舊簽名的外殼（同一元素重入
  即取返同一個實例，換標的不會疊加舊圖），既有頁面不必改呼叫口徑。
- **緊湊形態與多格由同一份規格提供**（`opts.compact` + `brokery/static/chart_grid.js`，`window.BrokeryGrid`）：
  `compact` 時 `option()` 只生成一個 grid 與一條 candlestick series（唔畫成交量格、唔畫右上角現價大字，現價虛線
  保留但 label 縮細），非 `compact` 逐項完全唔變，故既有頁面與斷言照過。`BrokeryGrid.build(el, {ktypes, onPick})`
  為每個 ktype 建一格（上方一排水平週期按鈕 + 一個圖表 div），每格一個獨立實例（即上面嗰條），`set(i, payload,
  ktype)` 只重畫一格，`resizeAll()` 一次過涵蓋全部格子。**頁內零文字**：按鈕只帶 `1m`／`day` 呢類 ktype token，
  所以換語言唔使重建格子。撳按鈕嘅點擊記低 `[格, 週期]`：Web UI 用 `onPick` 即時回調，桌面 GUI 用 `takePicks()`
  輪詢取走（`QWebChannel` 喺 offscreen 載 `qrc:///qtwebchannel/qwebchannel.js` 即 segfault，已實測）。Python 側只多
  幾個入口：`chart.grid_page()`（載體頁）、`grid_js(ktypes)`、`grid_set_js(index, frame, ktype)`、
  `grid_note_js(index, text)`、`grid_picks_js()`。
- **交互與標註一律由這份規格提供，界面不寫一行**：滾輪縮 X 軸、**Shift+滾輪只縮 Y 軸**（單軸）、拖曳左右平移、
  **雙擊即復原**；**現價水平線**與**右上角現價大字**一律取序列最後一根的收市價，故串流更新時兩者自己移動，界面
  不需要另外傳值；大字只在現價真的改變時閃一次（首次載入與重複繪製同一價格不閃；計時由實例做，因本圖
  `animation: false`）；最新一根 K 線右側留位（現價數字即疊於該右側留白之上），兩個 y 軸不繪水平網格線。
  （ECharts 的 `zoomOnMouseWheel: true` 唔理修飾鍵，且 zrender 先註冊 wheel 並切斷後續 listener，故單軸縮小要由
  實例在 **capture** 階段自己分派 `dataZoom`。）
- **序列合併規則三處同一口徑**（`chart.BarStore` 與 `chart.js` 的 `store()`）：key=(code,ts)、同 `ts` 以新到者
  覆蓋、每個代碼只保留最新 N 根、內部一律 ts 升序。串流的 `update` 只帶最近 `count` 根，直接取代會把 1000 根
  歷史縮返最近幾根，故一律合併。N 由 `set_limit()`／`setLimit()` 跟界面請求的根數調整（寫死時取 3000 根會被
  裁返 1000，即「1000條只顯幾十條」的另一半成因）。
- **「最新在最上」只屬顯示層**：`rowsDesc()`／`desc()` 只在表格顯示時反序，存放與圖表一律升序，故跨券商對齊
  與指標計算不受界面排序影響。
- **離線可用**：`echarts.min.js` 為本地 vendor（已無 CDN），故 GUI 與 Docker 鏡像在無外網時照樣畫到圖。
  閘道與 Web UI 的 `/static/{name}` 只准取 `brokery/static/` 內的檔案（路徑不可走到該目錄之外，否則 404
  `static_missing`），三個界面載的是同一份。

### 17. 多週期 K 線與連線數（實測結論）

同一個代碼可同時用多個週期，每個週期就是一次正常的取數與訂閱，界面不需要為「多週期」寫任何特殊處理：

```python
bk.get_kline("HK.HSImain", ktype="5m", count=200)                     # 各帶自己的 ktype
bk.stream_kline("HK.HSImain", ktype="5m", count=200, seconds=..., on_update=...)   # 一個週期一份訂閱
```

- **週期順序只有一份定義**：`brokery/brokers/base.py` 的 `KTYPE_ORDER`（即 `BAR_MINUTES` 的鍵順序：1m、3m、5m、
  15m、30m、60m、day、week、month，正好九個）。`/capabilities` 照呢份返回，三個界面的週期下拉框一律照
  佢排列，唔准自己排序或憑空補週期。
- **能並行的週期由適配器聲明**（`SymbolBroker.stream_ktypes`）：futu 為其全部週期、IB 為其全部 bar size，
  tiger／webull 只支援 `1m`（故該兩家不會出現多週期）。不支持的組合由適配器聲明、由 `core` 明確拒绝，不靜靜
  改用另一個週期。
- **同一條券商連線可同時串流多個週期，同一週期亦可並行多條**（futu）：`set_handler` 每條連線只有一個推送回呼，故以
  `_KlinePushRouter` 按推送行上的 `k_type` 分派給各週期的接收器，並以引用計數管理 start/stop；上游訂閱按
  **（代碼, 週期）引用計數**，同一週期的第二份照樣並行，最後一份結束才 `unsubscribe`（舊行為「同週期第二份即拒」
  已移除，故並行時不會互相蓋走訂閱）。實測同一條連線並行 1m/3m/5m，各週期取到自己週期的 bar（`ts` 間距分別為
  60/180/300s 的整數倍），且沒有另開連線。
- **連線數的結論**：券商端的訂閱數唔可以少過週期數（每個週期係上游一份獨立訂閱），但**可以共用同一條券商
  連線**；真正會排塞的是界面→閘道那一層——瀏覽器對同一來源只得約 6 條 HTTP/1.1 併發連線。故一個界面的多個
  訂閱一律**只開一條** `/stream`（一條連接上逐週期 `subscribe`，每一幀帶 `broker`/`ktype`，`update` 按 `ktype`
  分派），閘道的串流登記亦由「每券商一名額」改為按
  **請求簽名（券商, 週期, 代碼, 根數, 複權, raw）** 計，`stop` 可按 `broker` 或 `ktype` 只收其中一部分。換週期即只
  重取該週期的歷史、並只退該週期的串流，其餘訂閱不受影響。
- **多週期界面（「K 線串流（多週期）」，Web UI 與桌面 GUI 同一頁）**：一格一週期，格子數與順序即所選券商聲明的
  `stream_ktypes`（照 `KTYPE_ORDER` 排列）——futu 聲明九個，正好 3×3；IB 得部分；tiger／webull 只得一格。界面唔會
  憑空補出該券商不支持的週期，所以唔會見到八格同時報 `ktype_unsupported`。每格上方一排水平週期按鈕，內容同樣係
  呢份聲明嘅清單（按鈕只帶 `1m`／`day` 呢類 token，語言中性，換語言唔使重建格子）。流程照單格串流頁：先逐格取歷史
  （根數為控制列一個共用輸入，預設 300；九格 × 1000 根會令富途走九次分頁路徑，明顯慢），全部返回先至喺**一條**
  連接上送九個 `subscribe`；`update` 按 `ktype` 只重畫對應格；一個「開始／停止」管全部格子（逐格只有週期按鈕），
  換某一格嘅週期即只重取嗰格、只退該週期的串流，若該舊週期仍有別格顯示則唔退（退咗會斷咗嗰格嘅推送）。
  格子與圖表規格由 `brokery/static/chart_grid.js`（`window.BrokeryGrid`）一份提供，兩邊讀到嘅逐 byte 相同；下方無
  DataFrame，故呢頁無表格、無 `columns` 渲染。

## 設計前提（實測結論，改動前請先讀）
- 股票清單出自富途、Tiger 與 Webull（富途 `get_stock_basicinfo` 一次取全、Tiger `get_symbol_names`
  按市場一次取全、Webull `list_instruments` 分頁）；IB 無「一次過列出全市場股票」的接口，故不聲明
  `STOCK` 能力、由 `core` 統一返回 `no_source`，不為湊齊四家而改用 top-N 樣本（實測
  `reqMatchingSymbols` 混入 BOND）。
- 各券商對同一掛牌場所的寫法本來不同（Webull 以 HKG／XGEM／NAS／NSQ／NMS 登記，富途以 HKEX／NASDAQ
  登記），一律原樣返回、不憑空歸一；需要回溯時用 `raw=True` 取原生格式。期貨的場所則已歸一到 `codes` 詞表
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
python brokery/acceptance/run_get_codes.py          # get_code：離線讀回已存放的 CODES（預設 futu），不連 OpenD
python brokery/acceptance/run_get_codes.py FUTURE   # 只顯示某一類型（STOCK/FUTURE/INDEX）
python brokery/acceptance/run_get_codes.py "" ib    # 讀 ib 那一檔（各券商各一檔）
python brokery/acceptance/run_codes_refresh.py      # refresh_codes 的更新路徑：按券商各存一檔（<broker>_codes）且互不覆蓋、縮細防護只與同一券商的上一份比較、原子寫入與 .prev 備份、某品種明顯縮細時拒絕覆蓋、某品種本次取不到時沿用舊快照該品種、取數失敗時保留原快照、差額回報、過期判定（CODES_MAX_AGE_HOURS）、閘道只在快照過舊時才在背景自動更新、該券商已被停用時不做背景自動更新（以存根代替 list_all，不需任何連線；用 acceptance_ 前綴的臨時資料集，跑完即刪，不動到實際快照）
python brokery/acceptance/run_list_symbols.py      # 四家 × 三品種的標的清單：能力聲明與實測一致、欄位與順序一律為 COLUMNS、字串欄無 NaN、code 為統一代碼、未聲明品種返回 no_source、跨券商合併不重複列；每家再以 raw=True 取一次，核對欄位即該券商自帶的鍵且行數不少於統一格式（需 OpenD + IB + Tiger + Webull）
python brokery/acceptance/run_list_filter.py       # 清單的 broker 與 markets 兩個參數（core 調度口徑）：只向一家取、unknown_source／type_unsupported、markets 按行過濾、empty_list、省略 markets 用預設市場、一家失敗仍返回別家資料；raw=True 時不做按行的市場過濾（原生行無 market 欄位），市場範圍一律由參數／種子保證（以存根券商進行，不需任何連線）
python brokery/acceptance/run_raw_frames.py        # raw=True 的契約（以存根適配器進行，不需任何連線）：信封仍三鍵且 data 即原生欄位、非 raw 的 COLUMNS／K_COLUMNS／ACCOUNT_COLUMNS 不變、raw 跳過去重與統一欄位行過濾但取數範圍不變、多來源欄位為首見聯集、失敗時空表無欄位、NativeBars 與 BarMerger 對外語義一致
python brokery/acceptance/run_broker_prefs.py  # 券商開關喜好（BROKER 管理，見 §15）：以存根適配器與臨時資料目錄核對喜好檔只記被停用者、檔不存在或不可讀即全部生效、寫入為原子、生效集合為 API_SOURCES ∩ 喜好、被停用者不經過任何動作（get_kline／stream_kline／list_stocks／get_accounts／get_brokers 一律 broker_disabled）、與 unknown_source／no_source 清楚分開、get_broker_prefs 列出全部券商（未配置者 configured=False）、set_broker_enabled 即時生效不需重建、core 不讀檔故不傳 `disabled` 即照 `.env` 取齊全部券商、檔內多餘的名字無害（不需任何連線）
python brokery/acceptance/run_chart_spec.py    # 共用圖表層（見 §16）：payload() 保持 ts 升序且 NaN/Inf 轉 null、overlay_rows() 欄位即 OVERLAY_COLUMNS、render_js() 產生可直接執行的呼叫、static_file() 不可走到 static 之外、frame() 把 BarStore 還原成 DataFrame（故界面的圖與 DF 同一份序列）、x 軸為原始 ts、option() 為 candlestick + volume 兩條 series、內置 zone 的 markArea（端點喺範圍外即貼最近一根）、register 後多出對應 series、未註冊的 kind 被跳過、store() 合併（key=(code,ts)、同 ts 以新到者覆蓋、每代碼只保留最新 N 根）並還原原欄位、setLimit() 令上限跟界面請求的根數（取 3000 根唔會被裁返 1000，調低即裁走最舊）、rowsDesc()/desc() 只屬顯示層；以 Chromium 核對本地 echarts 載入（無 CDN）、render() 真畫到嘢且同一實例可重用、render() 每次都帶規格（換週期後 x 軸格式跟住改，只喺開圖時給一次即永遠照舊週期）、create() 一圖一實例（兩張圖互不影響、縮放範圍跨 update 保持）、真滾輪縮 X 軸／Shift+滾輪只縮 Y 軸／拖曳平移／雙擊復原、現價線取序列最後一根並跟住串流走、destroy() 釋放實例、timeText 日線只到日期；`compact` 時 `option()` 只一條 series 一個 grid 無現價大字（非 `compact` 逐項照舊）、`BrokeryGrid` 九格九實例互不影響／撳按鈕只重畫一格並只上報 `[格, 週期]`／`takePicks()` 取走即清空／`resizeAll()` 涵蓋全部格子；`chart.py` 的 `grid_page()/grid_js()/grid_set_js()/grid_note_js()/grid_picks_js()` 產生可在載體頁直接執行的呼叫（不需券商連線）
python brokery/acceptance/run_get_kline.py          # 同一 code 經 futu/ib/tiger 取 K 線並核對對齊，另核對 Webull 的取數與明確報錯（需 OpenD + IB；Tiger 需私鑰）
python brokery/acceptance/run_get_kline.py HK.00700 week 120   # 指定代碼 / ktype / bar 數
python brokery/acceptance/run_futu_kline.py       # 富途 K 線的根數口徑（不需 OpenD，以存根 _ctx）：各週期足數、兩段去重、起日折半、深度不足會點名
python brokery/acceptance/run_align_kline.py        # 四家的前復權以 futu 為準逐根並列，量化各家與它的偏差（需 OpenD + IB + Tiger + Webull；美股代碼會跳過 Webull 並打印 WARN）
python brokery/acceptance/run_align_kline.py US.NVDA day 120   # 指定代碼 / ktype（日內或日線）/ bar 數
python brokery/acceptance/run_stream_kline.py          # 一條連線同時串流多個代碼（futu/ib/tiger/webull），核對回呼規格與 seconds 約束；另核對多週期並行（同一連線並行多個週期、各週期仍取到自己週期的 bar（ts 間距為該週期的整數倍）、同週期的第二份照樣並行（上游訂閱按（代碼,週期）引用計數：並行期間不退訂閱、全部結束才退一次）、多個週期共用同一條連線；可並行的週期一律取自適配器聲明的 stream_ktypes，只聲明 1m 者明確跳過）（需 OpenD + IB；Tiger 需私鑰）
python brokery/acceptance/run_stream_kline.py US.NVDA 5m 50 120   # 指定代碼（逗號分隔可多個）/ ktype / bar 數 / 秒數
python brokery/acceptance/run_kline_matrix.py      # 品種 × 券商矩陣：品種推斷、能力閘（type_unsupported）、復權只對股票有效、指數跨券商對齊；raw=True 的根數與收市價與統一格式逐根相同、時間欄位為該券商自己的寫法（需 OpenD + IB + Tiger）
python brokery/acceptance/run_get_accounts.py      # 四家戶口與資金：統一欄位、只列真實且已啟用的戶口、幣種有無填到、acc_type/currency/broker 三個參數的邊界、詞表外的戶口性質（IB individual）在篩選時點名說明；每家再以 raw=True 取一次，核對欄位即該券商自帶的戶口記錄、不支持的幣種仍明確報錯、明確 acc_type 一律拒绝（需 OpenD + IB + Tiger + Webull）
python brokery/acceptance/run_get_brokers.py   # 四家連線狀態與延遲：統一欄位、延遲為正數且戶口數與 get_accounts 一致、連不上為 NaN 並附原因、並行探測、參數邊界（需四家後端在線）
python brokery/acceptance/run_api.py           # 閘道本身：未設金鑰拒絕啟動、HTTP/WS 鑑權、返回信封與欄位契約、JSON 取值口徑、業務失敗原樣透傳、三個清單接口的 markets／broker 原樣透傳為統一前綴（含 markets 省略時不再拋 TypeError 的回歸檢查）、`/codes/meta` 返回快照元資料欄位（即 CODES_META_COLUMNS）與 `/codes/refresh` 透傳更新結果、三個 /codes* 端點按 broker 各讀一檔且兩檔互不覆蓋、六個取數端點與 `/stream` 的 `raw` 原樣透傳、串流協定與日誌遮罩、串流按**請求簽名**（券商,週期,代碼,根數,複權,raw）登記（一條 WS 同時訂閱多個週期、每一幀帶 broker/ktype、`stop` 可按 broker 或 ktype 只收部分、多週期界面（3×3 九格）的實際形態：一條連接一次過訂閱九個週期、九份 `update` 各自帶自己嘅 `ktype`（界面靠呢個欄位分派到對應嘅格）、`stop` 只帶一格嘅 ktype 時該格回 `closed` 而其餘八格照收推送、再送一次唔帶 ktype 的 `stop` 即逐個 `closed` 收齊剩低八格、已停止的訂閱不被第二次 stop 重複發 closed、「停止」後同一份請求再訂閱即接手仍在推送的串流（`resumed`，接手後照樣收到其後的 `update`）、同一份請求由**兩條連接同時訂閱**時向券商只訂閱一次且兩邊各收到同一份 `update`（`subscribed` 帶 `shared`）、其中一方 `stop` 只退出自己而另一條照收（不會另起一次訂閱）、同一條連接重送同一份請求為冪等、**換了參數即另一條串流，同一券商同一週期可並行多條**（同週期兩格不同代碼各自訂閱一次並各推自己代碼、換根數即另起一條、`stop` 只帶 ktype 時逐條各發一份 `closed`），不再返回 `stream_busy`）、`/brokers/prefs` 讀出全部券商（含未配置者）與 `/brokers/prefs/update` 以完整名單寫入並即時生效（被停用者其後一律 `broker_disabled`、`/capabilities` 不再列它、全部停用時為 `no_source` 並點名被停用者）、`/capabilities` 的 `ktypes` 即 `BAR_MINUTES`、`/health` 回報生效來源與喜好檔路徑、`/static/{name}` 不需金鑰且內容即 `brokery/static/` 那一份、目錄外與不存在者明確 404（不需券商連線）
python brokery/acceptance/run_ui.py            # dashboard 客戶端：以存根閘道 + Chromium 核對腳本無語法錯誤、頂欄四家指示、金鑰記憶與回填、探測只由載入與按鈕觸發、兩頁的自動更新以秒為單位且預設 0 時空轉完全不打請求（設 1 秒即定時重取、改回 0 即停止）、按來源汇总並點名無返回者、標的頁區分「不提供／無返回」、標的頁不再有「統一格式輸出」面板、離線 CODES 不分區而以單一表格顯示且欄位順序即接口原樣、該家快照一行顯示行數與距今時間且過舊以警告色提示、「更新 CODES」只向 `/codes/refresh` 送出且不带市場參數、換券商即改讀該家那一檔（顯示的只是該家的行數）、完成後原樣顯示結果並重讀快照與表格、搜尋零結果且快照過舊時提示按「更新 CODES」、K 線頁預設 `HK.HSImain`／`1m`／1000 根且券商為生效的第一家、圖表由 `/static/chart.js` 與本地 echarts 畫出（已無 CDN）、下方表格按時間反序、`update` 只帶最近幾根時與已拉取的序列合併而不縮減行數（不需券商連線；需 `playwright install chromium`，未裝即跳過）
python brokery/acceptance/run_webui.py         # Web UI：以存根閘道核對轉發原樣透傳信封與金鑰只在服務端、金鑰不符與閘道不可達均明確報錯、`/api/kline` 帶 `code/ktype/count/broker` 轉到 `/kline`（週期與根數省略時不自訂第二套預設）、`/api/brokers/prefs`（讀）與 `/api/brokers/prefs/update`（寫，省略參數即交空名單即全部停用）原樣透傳、被停用者不再出現在 `/api/capabilities`、`/static/chart.js` 與 `/static/echarts.min.js` 即 `brokery/static/` 那一份（只有一份，不存在者明確 `static_missing`）、`WebSocket /ws/stream` 以 `websockets.serve` 起上游存根核對訂閱與 `update` 雙向原樣透傳且上游不可達時返回明確 `error`；以 Chromium 核對選單為六項、欄位即 ACCOUNT_COLUMNS、千分位與破折號、按來源統計；標的頁先取能力聲明再取清單、券商選項由聲明填充且默認 futu（不提供該品種者標註且不可選）、表格欄位即 COLUMNS、市場選項只由返回的 market 填充、選市場與轉類型均向對應接口再取一次、離線 CODES 的讀取與更新均按券商原樣轉發（`/codes?broker=` 只讀該家那一檔、`/codes/refresh?broker=` 不带市場參數）、該家快照一行顯示行數與距今時間且過舊及上次更新失敗以警告色提示、換券商即改讀該家那一檔（不含別家的行數）、更新結果原樣顯示（含各品種增減）、兩頁的自動更新以秒為單位且預設 0 時完全不打請求、標的頁定時更新預設只重讀離線快照（勾上「自動向券商重拉」才向券商取清單）、兩個 K 線頁預設值（`HK.HSImain`／`1m`／1000，根數可任填、上限 100000，與桌面 GUI 一致）與 DF 按時間反序、**DF 列出接口返回的全部行（120 行的存根返回 120 行，不做「只列最近 N 行」的截斷）**、`count=3000` 原樣送到閘道且合併器上限跟住 3000（唔會裁返 1000）、開圖傳 `start: 0` 即圖上的 bar 數即合併後的根數、換週期後 x 軸格式跟住改（日線只到日期）、K 線串流頁在 DF 上方以本地 echarts 畫出 canvas 且圖與表格同一份序列（表格行數即合併後的根數）、串流 `update` 合併後不縮返已取的歷史、**同一券商同一週期可並行多條**（多週期頁已佔住 `futu/1m` 時「K 線串流」頁照樣訂閱同一券商同一週期：2 條連接、唔被拒、唔使等；存根以 `/push` 代替券商推送，兩條各自收到（`pushed:2`）並各 +2 根，互不取代；停其中一條只收返該條（`pushed:1`），另一條照舊串流並繼續收推送，已收返嘅連接唔再被填）、協定錯誤（存根對 `HK.BAD` 返回 `ktype_unsupported`）原樣呈現且唔被自動重送訂閱（被拒後撳「停止」即收返呢條連接並解鎖按鈕）、訂閱只開**一條**上游 WebSocket 且內容與閘道協定相同、一律先取歷史才建立串流（`/kline` 在 `subscribe` 之前；取不到歷史即不訂閱並清走舊標的的序列）、BROKER 管理頁列出全部券商（含未配置者）且開關一改即重讀能力聲明並重畫所有券商下拉框；多週期頁：`/static/chart_grid.js` 與桌面 GUI 讀到嘅逐 byte 相同（只有一份）、格子數與順序即該券商聲明的 `stream_ktypes`（futu 九格、IB 按未排序嘅聲明原樣排列、tiger 一格）、每格一排水平週期按鈕且只有該格自己高亮、下方無 DF、根數為一個共用輸入且預設 300、九格逐格先取歷史（`/kline` 九次）先開**一條** `/ws/stream` 送九個訂閱、`update` 按 `ktype` 只重畫對應格、每格緊湊規格（一格一 grid 一 series）、換一格只重取嗰格並只送帶該 ktype 的 `stop`（唔再開第二條連接）、該舊週期仍有別格顯示即同簽名，唔退它、換返一個已無格子顯示的週期即補訂閱、一個「停止」只送一次裸 `stop` 並就地提示已停止（唔依賴閘道的 `closed` 帧：瀏覽器一 `close()` 代理即拆上游）、換券商即按新聲明重建格子（不需券商連線；未裝 Chromium 即跳過）
python brokery/acceptance/run_gui.py           # 桌面 GUI（brokery_gui）：以存根閘道 + Qt 離屏核對六個頁面 .ui 檔齊全且檔內不含任何文字（多週期頁連週期下拉框與表格都冇）、三種語言各一個 .json 且鍵集合一致（現為 74 鍵）、切換即時生效且不重建窗口、缺譯返回鍵名、界面用到的鍵三種語言均無缺譯、表格欄位即 ACCOUNT_COLUMNS／COLUMNS、缺失值破折號與資金欄千分位、按來源統計、券商選項由能力聲明填充且默認 futu（不提供該品種者標註且不可選）、市場選項只由返回的 market 填充、選市場與轉類型均向對應接口再取一次、標的列表為上下兩張表（上表欄位即閘道 raw=1 返回的該券商自帶欄位、下表仍為 COLUMNS）、同一篩選條件順序取兩次（先統一格式、再同參數 `raw=1`）且舊回應不蓋過新選擇、raw 取不到只寫自己的標籤、該家離線快照一行顯示行數與距今時間且過舊及上次更新失敗以警告色（非錯誤色）提示、「讀取離線 CODES」只向 `/codes?broker=` 讀該家那一檔、「更新離線 CODES」只向 `/codes/refresh?broker=` 送出且不带市場參數並重讀該行、換券商即改讀該家那一檔、切換語言時該行一併重貼、兩頁的自動更新以秒為單位且預設 0 時完全不打請求、標的頁定時更新預設只重讀離線快照（勾上「自動向券商重拉」才向券商取清單）、閘道不可達與金鑰不符均明確報錯、六個分頁齊全且標題由字庫按鍵取（轉語言後六個標題全部重貼、不重建窗口）、兩個 K 線頁預設 `HK.HSImain`／`1m`／1000（上限 1000）、K 頁券商下拉框只列生效者（不像標的頁按品種過濾）、週期選項只由 `/capabilities` 的 `ktypes` 填充且順序原樣、表格欄位即 `K_COLUMNS` 且按時間反序（存放仍為升序，反序只屬顯示層）、訂閱與停止的按鈕狀態、`update` 經序列合併（同 ts 覆蓋、已取的歷史不縮返最近幾根）、K 線串流頁惰性建立 DF 上方的 `ChartView`（無顯示環境起不來即說明原因而非留空白，DF 照常填充並反序）、只交一份 DataFrame 給那份共用的 `chart.js`，並核對渲染的根數與 DF 一致（圖與 DF 同一份序列，並照控制列的週期顯示時間軸）、BROKER 管理頁列出全部券商且開關一改即重讀能力聲明、背景取數的回應經一個屬主執行緒的轉接交回 GUI 執行緒（PySide6 中連到普通可呼叫物件的信號在發射執行緒執行，直接碰 `runJavaScript` 即崩潰）、按「訂閱」先向 `/kline` 取歷史、歷史已在圖上才建立連接且只開**一條** `/stream`（取不到歷史即不訂閱並解鎖按鈕）、收到的 `update` 原樣合併並保持反序、取歷史在途時撳「停止」即取消意圖、停止後重按「訂閱」會重新先取歷史（不被已收尾的連接擋住）、接手唔使等（「停止」後不預先記低 `closed` 帧給的收尾秒數 → 同一份請求再按「訂閱」即刻送訂閱幀、即刻串流）、K 圖佔頁面高度的一半以上（圖表區與 DF 按 .ui 的 3:2 分配）、多週期分頁：格子數與順序即該券商聲明的 `stream_ktypes`（存根刻意把 ib 排成未排序，界面照原樣）、每格一排水平週期按鈕且只有該格高亮、無表格無 DF、根數為一個共用輸入、九格逐格先取歷史先開**一條** `QWebSocket` 送九個訂閱、`update` 按 `ktype` 只餵對應格、換一格只重取嗰格並只送帶該 ktype 的退訂、該舊週期仍有別格顯示即同簽名，唔退它、**同一券商同一週期可並行多條**（多週期頁已佔住 `futu/1m` 時另一頁照樣訂閱：另開一條連接、唔被拒、唔使等；兩條各自收到推送各 +2 根；停一條唔影響另一條；已收返嘅連接唔再被填）、協定錯誤原樣呈現且唔被自動重送、一個「停止」收齊全部格子並就地提示已停止、`GridView` 惰性建立且起不來即說明原因而非留空白（按鈕只帶 ktype token，換語言唔使重建格子）、直接啟動 `brokery_gui/run.py` 核對窗口會存活（不需券商連線，亦不需顯示器）
python brokery/acceptance/run_launch.py        # 啟動器 run_all.py：以存根命令核對兩個同時啟動、先結束者停止另一個並返回其退出碼、正常結束返回 0、Ctrl+C 一併停止、預設命令即兩個既有入口、啟動器不引入券商 SDK（不需券商連線，亦不真的啟動服務）
```
測試以腳本方式直接執行（不使用 pytest）：執行後即輸出 `status`、`message` 與完整代碼表，
並以退出碼 `0`/`1` 表示成敗。涉及 IB 的檢查在 IB Gateway 未開通歷史行情或連線不可達時，一律以
`timeout: IB 連線 超過 40.0s` 明確失敗（同為環境缺口，不改 `core` 湊數）；Webull 的美股同理為
`market_data_not_subscribed`（該憑證只開通 HK 行情），需要實測時改用港股代碼。
文中所列的檢查項數只反映最近一次實跑：連不上嘅來源會令對應檢查整項被跳過（例如 IB 不可達時
`run_get_accounts.py` 少 11 項、`run_kline_matrix.py` 少 6 項），因此項數會隨環境浮動，
真正嘅契約以每項 PASS/FAIL 為準。
喜好檔只由閘道讀寫，`core` 只接受 `Brokery(disabled=…)`；逐家循環的腳本（`run_get_accounts.py`、
`run_get_brokers.py`、`run_list_symbols.py`、`run_kline_matrix.py`、`run_align_kline.py`）不傳 `disabled`，
因此用戶在界面上停用某家不會令這些腳本憑空失敗（見 §15）。

## 環境
- 連線參數與離線資料目錄全部讀自 `.env`（`FUTU_OPEND_HOST/PORT`、`IB_HOST/PORT/CLIENT_ID`、
  `IB_REQ_TIMEOUT`、`BROKERY_DATA_DIR`、`CODES_MAX_AGE_HOURS`（離線 CODES 視為過舊的時數，預設 24）、
  `TIGER_ID/ACCOUNT/TOKEN/PUBLIC_KEY/PRIVATE_KEY`、
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
