# Adaptive Scheduler Arena 驗收矩陣

本文件承接總 PRD 的每項需求、負責子 PRD 與驗收證據，也作正式流程的 closeout 索引，不重複改寫產品需求。所有項目仍為待驗收；比賽開發與流程修改不等於產品或文件已驗收。

## 證據規則

- 每列填入結果、證據連結或命令輸出、日期與驗收者；未通過須保留限制，不能以 local 結果宣稱 team mode 通過。
- 子 PRD closeout 必須有：完整功能驗收、相關測試、AI review、Owner 自查、另一位成員確認、正式 PR merge，以及 `main` 整合驗收。
- 所有子 PRD完成仍不足以宣告產品完成；必須再通過本表的整合、90 秒短展示與 progression run 項目。

## 原型試接與正式驗收

原型工作與開發版試接依 [workflow](workflow.md)；可以記錄真實未合併版本、已跑通路徑及未覆蓋限制，但不能據此把下表正式驗收標為通過。第一個展示情境由人類另行選定，不自動縮減產品範圍或要求必然通過。接口協調使用[討論表](docs/product/interface-discussion-board.md)，不是驗收替代品。

## 真實切片證據

SP-01 保留整份 PR；SP-02～04 每切片依 [workflow](workflow.md) 記錄上游交付 ID、契約版本、真實輸入、commit／PR、人類授權、main 版本與驗證結果。切片通過只涵蓋對應範圍，不能把下面整列或整份子 PRD 標為完成。

交接逐項核對 [H1～H8](docs/contracts/adaptation-contract.md)，未決事項核對 [D1～D9](docs/product/adaptation-decisions.md)。R07～R18 所需全敗、passed、錯誤恢復與 UI 必須來自真實能力；固定 Jobs／邊界資料保留，但替身結果不構成正式整合。R02 Hybrid gate 來源與 R11 Snapshot 不變範圍仍待 D6，不刪除原要求或擅自縮小驗收。

責任調整待 D4 核准才更新下表負責子 PRD；尤其既有評估錯誤、共同 gate 與底層恢復不能因目前列在另一功能便被省略。受影響列在決策及實際驗證完成前維持待驗收。

| ID | 總 PRD需求 | 負責子 PRD | 驗收證據 | 結果／日期／驗收者 |
| --- | --- | --- | --- | --- |
| R01 | Job 驗證、狀態、單 worker、不可搶占、deadline 與同時刻事件順序正確。 | SP-01 | 後端契約共同 deterministic fixtures B、D 與契約測試。 | 待填 |
| R02 | FIFO、SJF、Priority、EDF 排序與 tie-break 正確；Hybrid 未通過 gate 前不是初始 Skill。 | SP-01 | 後端契約共同 deterministic fixture A、tie-break 測試與 reset 初始 Skill 檢查。 | 待填 |
| R03 | `advance` 切分一致；seed、注入、20 筆上限與 reset 可重現且原子。 | SP-01 | 大步／分段、RNG、無效批次、名額、reset 測試。 | 待填 |
| R04 | 三個 tabs、Arena 控制、動畫、Metrics & Code、初始 Skill Library 同一 Snapshot 且可讀。 | SP-01 | controller／revision／單一更新來源測試；初始控制狀態、捲動保留、1440×900、1280×720 瀏覽器證據。 | 待填 |
| R05 | Demo mode 只允許播放、暫停、單步、reset、倍速與 workload；Developer mode 才可手動套用已驗證 Skill。 | SP-01 | 兩種 mode 的控制可見性與操作測試。 | 待填 |
| R06 | provider-neutral 的 team backend 與外部 Agent adapter 可用，或明確標示為 local／Mock；team 載入失敗不 fallback。 | SP-01、SP-03 | Python／uv 環境、契約指定 CLI、`--backend team --factory`、外部 adapter、Mock 標示與失敗 factory 的啟動／整合證據。 | 待填 |
| R07 | trigger 未成立不 adaptation；指標惡化成立後立即暫停 simulation clock，以相同 baseline 評估所有已驗證 Skills；同 run／window 重複 trigger 沿用同一 `adaptation_id`。 | SP-01、SP-02 | 模擬時間與 Job 凍結、重複 trigger、相同 workload／seed／state／window、sandbox fixture 測試。 | 待填 |
| R08 | AI 自動完成既有 Skill 比較；目前 Policy 通過時只記重用並恢復，不重建 activation；其他 Skill 通過時依固定順序啟用並恢復；兩者皆不建立 Candidate。 | SP-02 | 目前 Policy 無新 segment／activation、多 Skill tie-break、無人工調參、無 Planner／Candidate、running Job、resume 與 next-dispatch 測試。 | 待填 |
| R09 | UI 顯示 degradation、既有 Skill 比較、選擇原因與 `existing_skill_reused`；只有切換至不同 Skill 才另有 `policy_activated`。 | SP-02 | 同一 Snapshot 的條件式 event、metrics、瀏覽器證據。 | 待填 |
| R10 | Candidate 只在全部既有 Skills 失敗後由 AI 自動建立與迭代；ID／父版本／原因／code／workload／feedback 可追溯。 | SP-03 | all-failed gate、無人工調參、Candidate lineage 與 UI 證據。 | 待填 |
| R11 | Candidate sandbox 評估與 evaluator gate 正確；sandbox 不修改 Live Run。 | SP-03 | baseline／Candidate metrics、契約檢查、Live Snapshot before/after 測試。 | 待填 |
| R12 | Critic feedback 最多推動五版；拒絕、契約錯誤、第五版失敗皆維持 Live Policy 與暫停狀態。 | SP-03 | 版本上限、failure reason、`adaptation_failed`、simulation clock 不前進測試與畫面。 | 待填 |
| R13 | 外部 Planner／Evaluator／Critic／LLM 錯誤停止 loop、保持暫停、保留最後有效 Snapshot、記錄並顯示錯誤；只提供安全的手動 retry，且不自動轉 Mock。 | SP-03 | timeout／schema／服務錯誤、`adaptation_error`、retry／resync／reset 與 UI 證據。 | 待填 |
| R14 | 僅 gate-passed Candidate 可註冊為 verified Skill，並在 Skill Library 顯示來源與使用記錄。 | SP-04 | passed／rejected input、register、Library Snapshot／瀏覽器測試。 | 待填 |
| R15 | 註冊後自動啟用並恢復 simulation clock；新 Policy 只在下次 dispatch 生效；建立 Policy segment 與 `policy_activated`。 | SP-01、SP-04 | running Job、resume、next dispatch、segment／event 測試。 | 待填 |
| R16 | promotion／activation／同步錯誤時保持暫停、保留最後有效 Snapshot；安全狀態可手動 retry，狀態不明只可 resync／reset。 | SP-03、SP-04 | state-uncertain、無自動 retry、手動 retry／resync／reset、Skill／segment 清理測試。 | 待填 |
| R17 | Live、segment、existing evaluation、Candidate evaluation metrics 分開；已 dispatch Job 依 dispatch segment 歸屬，未 dispatch 即 expired 者歸 expiry 時 segment；Skill 不增加契約外 metadata。 | SP-01、SP-02、SP-03、SP-04 | 跨切換完成、未 dispatch expiry、最小欄位 contract 測試、UI 標示及人工資料解讀檢查。 | 待填 |
| R18 | Snapshot、Event、EvaluationResult、adapter timeout／錯誤與 session revision 契約一致。 | SP-01、SP-02、SP-03、SP-04 | contract tests、兩個 session、舊回應拒收、錯誤恢復。 | 待填 |
| R19 | 90 秒短展示導覽可追溯的 team-mode 適應證據，不要求外部 AI 在 90 秒內完成；不固定時長的 progression run 實際完成多輪惡化、暫停、adaptation、啟用與恢復，且只以相同 baseline gate 證明採用時改善且無退步。 | SP-01、SP-02、SP-03、SP-04 | 短展示 stopwatch、Run／Snapshot／Event 來源、progression timeline、逐輪 baseline／gate、外部 adapter 執行紀錄與必要截圖。 | 待填 |
| R20 | 不含未核定 scope：Round Robin、搶占、worker failure、多 worker、長期 evaluator、登入、部署、未驗證動態 code。 | SP-01、SP-02、SP-03、SP-04 | code／設定人工審查與最終 AI review。 | 待填 |

## Closeout 總檢

| ID | 條件 | 證據 | 結果／日期／驗收者 |
| --- | --- | --- | --- |
| C01 | 每個子 PRD 已依流程完成完整功能驗收、測試、AI review、Owner 自查、另一位成員確認、正式 PR merge 與 `main` 整合驗收。 | 四份子 PRD 的 closeout 連結與 `main` 驗收結果。 | 待填 |
| C02 | `DEPENDENCIES.md` 與每份子 PRD 的直接交付依賴一致；所有 Contract／Integration 邊完成真正整合。 | S01-FULL／各切片的上游交付、H1～H8 契約版本、PR／main 證據逐邊核對；D1～D9 影響項均已核准並驗證。 | 待填 |
| C03 | team mode 的所有必要測試、lint、format check 與瀏覽器驗收通過；local 證據未被混作 team 證據。 | 命令輸出與來源標示。 | 待填 |
| C04 | 已核定的 trigger pause／去重、dispatch attribution、最小 Skill metadata、錯誤 event／手動 retry 及短／長展示行為均已寫入產品權威並完成驗收。 | 決定紀錄及 R07、R08、R12、R13、R15、R16、R17、R19 證據。 | 待填 |
| C05 | 交接包可由獨立 implementation repository 讀取並執行，不需要 planning repository、會議紀錄、AO 草案或預先建立 Ticket。 | 獨立讀取／rehearsal 證據。 | 待填 |
