# 共用接口討論表

## 表單定位與填寫規則

本表供四組異步討論，不是完成證據。2026-09-12 使用者已採納 I01～I09 所涉四組方案；產品與公開契約以 [PRD](../../PRD.md)、[backend](../contracts/backend-contract.md)、[H1～H8](../contracts/adaptation-contract.md)及 [D1～D9](adaptation-decisions.md) 為權威。本輪未查驗組員分支／服務，所有 I 項仍待真實實作、試接或 main 證據。

整合協調人：**本次對話使用者暫兼任**。各列真實版本、需答案時間與接通證據由團隊填寫；不要求 SP-01 改原排程。每個問題一列，需要拆分則沿用 ID 加後綴並同步引用，不新增產品權威。

狀態依序：待討論 → 已決定（附核可及權威落點）→ 已實作（附版本）→ 開發版已接通（附真實證據）→ 正式已整合（附 main 證據）。問題重開時保留舊結論與版本。單純命名／格式適配且不改語意，可由雙方確認並記錄；產品、責任、安全、公開 schema 變更須人類核准並更新權威後使用。

## 接口工作清單（方案已決，實作待接通）

| ID／優先時點 | 提供者 → 使用者 | 已採納權威與待補實作證據 | 尚待接通／驗證的問題 | 不接通會卡住什麼；可先做什麼 |
| --- | --- | --- | --- | --- |
| I01／讀取前 | SP-01 → SP-02～04 | H1；D8；現有 Snapshot／revision，實作位置待填 | 讀取方式、返回形狀、過時結果拒收；優先適配 SP-01 已有介面 | 卡真實狀態接入；可做組內資料呈現與流程 |
| I02／控制前 | SP-01 既有 seam＋各流程 Owner → SP-02～04；分工已採納、seam 待證 | H2、H7；D1、D4、D7、D8 | 實際 controller pause／啟用／恢復與四項拒絕操作如何接通；不新增 SP-01 責任 | 卡 trigger 控制、activation、resume；可做非副作用邏輯 |
| I03／優先 | SP-02 共用 evaluator Provider → SP-03 reuse | H3；D2～D4、D6、D7；baseline／negative semantics 已採納 | 同一 checkpoint、FIFO baseline、outcome 分類與 gate 的真實 Provider 版本 | 卡評估與 gate 實測；可做版本、收集與流程結構 |
| I04／重放執行前 | SP-01 checkpoint seam → SP-02 sandbox/evaluator → SP-03 | H3；D2、D6、D7；重放／隔離規則已採納 | 真實 clone／isolated runner seam 與可變 evidence 的驗證 | 卡隔離／重放驗證；可做不操作 Live Run 的組內工作 |
| I05／外部呼叫與恢復前 | 各階段 Owner；checkpoint/controller seam 待證 → 各組 UI／流程 | H5、H7；D4、D5、D7、D8 | 60/60/10 timeout、取消、部分完成、安全 retry/resync/reset 的真實接通 | 卡外部操作與恢復實測；可做錯誤呈現、保留已知狀態的內部部分 |
| I06／登錄前 | SP-03 → SP-04；storage/register seam 待證 | H6；D4、D8、D9 | accepted Candidate query、重複登錄與精確結果 binding 的真實實作 | 卡實際 register／promotion；可做最小欄位呈現與接收流程 |
| I07／跨組交接前 | SP-02 → SP-03；SP-03 → SP-04 | H4、H6；D2～D4、D9 | 完整結果集合、run/window/adaptation 關聯；缺失／外部中斷不是全敗，passed 不可只靠布林 | 卡真實 Planner 觸發／promotion；可做集合完整性、組內版本處理 |
| I08／接 UI 前 | SP-01 shell＋SP-02～04 evidence → 同一 UI | H8；D4、D6、D8、D9 | 插入位置、查詢方式、同版本證據、失敗保留畫面；優先下游適配現有 shell | 卡同版本 UI 聯測；可做各組呈現結構，不猜共享 shape |
| I09／優先，S01-FULL 前 | 真實 Hybrid gate 來源 Provider 待確認 → SP-01 驗收 | D6；backend fixture A 要求真實通過及註冊 | 已有合法來源嗎？若沒有，main 與 SP-01 決定前置提供安排，不能等下游而循環等待或直接免驗 | 卡 SP-01 Hybrid 完整驗收；不阻擋其他已承接工作，也不增加其職責 |

## 決策與接通紀錄（團隊直接填寫）

下列空白代表尚無證據，不代表已同意。討論建議寫上表；實際結論寫下表並連到更新後的權威章節，避免複製完整契約。

| ID | 討論負責人／提供與使用雙方人名 | 決策者／最晚需答案時間 | 狀態 | 結論、核可者／日期／證據、權威位置／版本 | 真實提供版／使用版、試接案例／結果 | 正式 main 證據／剩餘問題 |
| --- | --- | --- | --- | --- | --- | --- |
| I01 | 使用者兼任 SP-01 接口確認／待填 | 使用者／2026-09-12 | 已決定，待實作 | PRD「Metrics」、backend「Session」、H1 | read/controller seam、兩 session 證據 |
| I02 | 使用者兼任 SP-01 接口確認／SP-02／待填 | 使用者／2026-09-12 | 已決定，待實作 | PRD「自動 adaptation」、backend「共同規則」、H2 | pause/checkpoint/control seam |
| I03 | SP-02 evaluator Provider／SP-03／待填 | 使用者／2026-09-12 | 已決定，待實作 | PRD gate、backend EvaluationResult、H3 | gate、baseline、負結果實測 |
| I04 | 使用者兼任 SP-01 接口確認／SP-02／待填 | 使用者／2026-09-12 | 已決定，待實作 | backend checkpoint/sandbox、H3 | clone/isolated runner seam |
| I05 | 各 stage Owner／待填 | 使用者／2026-09-12 | 已決定，待實作 | PRD retry、backend Session、H5/H7 | timeout/cancel/recovery 實測 |
| I06 | SP-03 → SP-04／待填 | 使用者／2026-09-12 | 已決定，待實作 | backend accepted query、H6 | trusted store/register seam |
| I07 | SP-02 → SP-03 → SP-04／待填 | 使用者／2026-09-12 | 已決定，待實作 | backend EvaluationResult、H4 | complete all-failed 實測 |
| I08 | 使用者兼任 SP-01 接口確認／各 evidence Owner／待填 | 使用者／2026-09-12 | 已決定，待實作 | backend Session、H8 | UI envelope/shell seam |
| I09 | gate/register Provider → SP-01 fixture／待填 | 使用者／2026-09-12 | 已決定，待實作 | backend fixture A、H3/H6 | true gate→register fixture evidence |

開發版試接須另附：隔離環境、Owner 同意、真實輸入來源、必要安全／錯誤案例、未驗證範圍。無通過結果就記未通過；不得用固定 passed／all-failed 或人工接受候選補證據。
