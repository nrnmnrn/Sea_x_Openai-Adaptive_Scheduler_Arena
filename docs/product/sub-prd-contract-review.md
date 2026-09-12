# 子 PRD Contract 審閱草案

> 歷史調查：本文保留原調查時點的判斷與未核准提案，不是現行流程。現已進入比賽；SP-01 保留完整交付、SP-02～04 真實切片依 [ADR 0003](../adr/0003-real-slice-delivery.md) 及後續原型例外 [ADR 0004](../adr/0004-prototype-parallel-development.md) 與 [workflow](../../workflow.md)。目前交接／阻擋以 [交接契約](../contracts/adaptation-contract.md)及[待決清單](adaptation-decisions.md)核對。以下來源連結已指向本 repository 對應文件，內容可能已修訂，不代表仍支持歷史治理描述；未隨附的舊文件僅保留文字路徑。

## 定位與結論

> 狀態：調查與設計草案；未核定，不是 Contract，亦不移入交接包。

本稿審閱候選包 `build-handoff_final/` 的四份子 PRD 與跨功能交接處。
Contract 是模組交換資料或呼叫方式的共同約定；Provider 提供結果，Consumer 使用結果。
baseline 是比較基準，gate 是通過條件；Snapshot 是某時刻狀態快照，promotion 是將通過的 Candidate 升格為可用 Skill。
候選包仍待獨立驗收；題目獲准更換，不等於本包或 Contract 已核可。
來源：[候選包 README](../../README.md)、[總 PRD](../../PRD.md)。

**結論：可先寫並核可共同 Contract。**
其後，各人可依固定測試資料（deterministic fixture）及替代上游介面平行開發。
此僅限 Contract 開始；正式整合與 closeout 仍須 Provider merge 至 `main` 並驗證。
來源：[依賴索引](../../sub-PRDs/DEPENDENCIES.md)、[候選 workflow](../../workflow.md)。

現有 [backend-contract](../../docs/contracts/backend-contract.md) 已定排程、Snapshot、錯誤與部分 adapter 規則。
但未足以讓四人無需猜測地完成 adaptation、gate、promotion、recovery 與 UI evidence 的交接。
此為本稿根據下列缺口所作推論，未經核定。

四份子 PRD 皆標記 `0.1-draft`、待人類核可，且核可紀錄待填。
未見可證實的 Contract 凍結紀錄。
來源：[SP-01](../../sub-PRDs/scheduling-arena.md)、[SP-02](../../sub-PRDs/existing-skill-adaptation.md)、[SP-03](../../sub-PRDs/candidate-evaluation-loop.md)、[SP-04](../../sub-PRDs/skill-promotion-and-recovery.md)。

共同 Contract 應依跨功能交接處組織，毋須每份子 PRD 重複一套。
此為建議，未核定。

## 治理邊界與已見不一致

候選 README 與總 PRD 都明示此包尚未獨立驗收，不能宣稱已取代其他文件。
來源：[候選包 README](../../README.md)、[總 PRD](../../PRD.md)。
根目錄規範仍指定 `build-handoff/` 為未來 implementation repo 唯一文件介面。
來源：[根 AGENTS.md](../../AGENTS.md)。
候選包的 AGENTS、DEPENDENCIES 與 workflow 已允許「Contract 核定後」用 fixture 平行準備。
來源：[候選 AGENTS](../../AGENTS.md)、[依賴索引](../../sub-PRDs/DEPENDENCIES.md)、[候選 workflow](../../workflow.md)。
既有 歷史團隊 workflow（原路徑 `../playbook/workflow.md`，本 repository 未隨附） 只允許前置成果已在 `main`，或取得于喬明確例外同意後承接。
候選包規則不可暗自套用為此既有流程的例外。
來源：歷史團隊 workflow（原路徑 `../playbook/workflow.md`，本 repository 未隨附）。
競賽 README 記載題目可於正式開發前調整；候選 README 記載題目更換已獲核准。
根 AGENTS 仍寫產品決策暫停至主辦方回覆題目變更請求。
來源：歷史競賽 README（原路徑 `../competition/README.md`，本 repository 未隨附）、[候選包 README](../../README.md)、[根 AGENTS.md](../../AGENTS.md)。

此為文件不一致紀錄。本稿不處理批准、不宣告可開始競賽實作，亦不查私人通知。

## 四子 PRD：交接地圖

| 子 PRD | 既有宣告的輸出 | Consumer | 建議補足的交接物（未核定） |
| --- | --- | --- | --- |
| SP-01 Arena | Scheduler、Snapshot、Job、Skill、Event、metrics、segments、pause/resume seam、UI shell。<br>來源：[SP-01](../../sub-PRDs/scheduling-arena.md) | SP-02／03／04。<br>來源：[依賴索引](../../sub-PRDs/DEPENDENCIES.md) | 固定 baseline fixture、單一 UI shell binding、Snapshot 取得與修改結果規則；SP-03 依賴表所需的 sandbox 執行能力。 |
| SP-02 Existing adaptation | `TriggerResult`、完整 existing `EvaluationResult[]`、all-skills-failed、active `adaptation_id`、adaptation context。<br>來源：[SP-02](../../sub-PRDs/existing-skill-adaptation.md) | SP-03。<br>來源：[SP-03](../../sub-PRDs/candidate-evaluation-loop.md) | `EvaluationContext`、`ExistingEvaluationSummary` 與全敗完整性規則。 |
| SP-03 Candidate loop | gate-passed Candidate、完整 `EvaluationResult`、不可變 promotion input。<br>來源：[SP-03](../../sub-PRDs/candidate-evaluation-loop.md) | SP-04。<br>來源：[SP-04](../../sub-PRDs/skill-promotion-and-recovery.md) | Candidate／result 對應、保存與可讀取的不可變證據。 |
| SP-04 Promotion/recovery | register、activate、resume、錯誤恢復與 UI 證據。<br>來源：[SP-04](../../sub-PRDs/skill-promotion-and-recovery.md) | 整體整合。<br>來源：[總 PRD](../../PRD.md) | retry/checkpoint 操作語意、resync 後採納規則、各 session 隔離的 evidence。 |

表中「建議」皆不是既有承諾；不得據此改寫依賴圖或開始實作。

## 缺口 A：責任與 Adapter 倒掛

`BackendAdapter` 同表列 Scheduler、trigger、existing evaluation、Candidate、register、activate 等全部方法。
來源：[backend-contract：方法表](../../docs/contracts/backend-contract.md)。
子 PRD 卻分別由 SP-01／02／03／04 負責 Scheduler／adaptation／gate／promotion。
來源：[總 PRD：子 PRD 責任](../../PRD.md)。
SP-01 明列 pause/resume；SP-02 依賴表要求從 SP-01 取得 activation，SP-03 依賴表要求 sandbox。共同 backend 方法有 `activate_skill`，但底層操作實作歸屬尚需對齊。
案例 A 又要求已通過 gate 並註冊的 Hybrid fixture。
來源：[SP-01](../../sub-PRDs/scheduling-arena.md)、[SP-02](../../sub-PRDs/existing-skill-adaptation.md)、[SP-03](../../sub-PRDs/candidate-evaluation-loop.md)、[backend-contract](../../docs/contracts/backend-contract.md)。
若 SP-02 直接等 SP-03 提供共同 gate，會新增依賴索引未列出的反向依賴；目前缺的是共用實作歸屬，不是已證實的程式循環依賴。
來源：[SP-02](../../sub-PRDs/existing-skill-adaptation.md)、[SP-03](../../sub-PRDs/candidate-evaluation-loop.md)。

**建議，待決策：**SP-01 擁有排程狀態修改與 sandbox 執行底層能力；SP-02／04 編排既有重用與 Candidate 晉升，SP-01 不實作完整 SP-03／04。共同 gate 僅一份，可隨 SP-02 首次需要時交付，SP-03 重用。此改變責任邊界，須人類決策。
SP-01 的 Hybrid gate-passed fixture 驗收，應與真實 SP-03／04 串接分開。
整體 R19 仍待四份子 PRD 全部完成，不能要求 SP-01 closeout 證明整個產品。
來源：[SP-01](../../sub-PRDs/scheduling-arena.md)、[驗收矩陣](../../ACCEPTANCE.md)。

## 缺口 B：baseline、window 與 gate

PRD 要求相同 workload、seed、初始 state、evaluation window、baseline Policy；卻未定 trigger 門檻、window 長度、評估區間或 baseline 來源。
來源：[總 PRD：自動 adaptation](../../PRD.md)、[backend-contract：TriggerResult](../../docs/contracts/backend-contract.md)。
factory 的 `initial_jobs` 僅規定完成 `t=0` 到達與 dispatch 後回傳，未足以指定非零 checkpoint 重放。
來源：[backend-contract：共同規則](../../docs/contracts/backend-contract.md)。

**建議，待產品決策：**共同 baseline fixture 固定 `workload`、`seed`、完整 state、`evaluation_window`、`baseline_policy`。
具體 baseline Policy 選擇仍待決定。若保留「目前 Policy 通過即維持」，應明定可與目前 Policy 不同的基準策略；固定參考基準只證明勝過該基準，不代表勝過前一 live Policy。不得替團隊指定 FIFO 或閾值。
gate 必須逾期數下降，或逾期數相同而完成數增加；兩條路徑皆要求完成數不下降、P95 不惡化，且全部契約檢查與 sandbox 成功。若以目前 Policy 本身為 baseline 做相同條件 deterministic 評估，完全持平，因此目前 Policy 通過分支不可達。
此為條件推論。
來源：[總 PRD：gate 與目前 Policy 重用](../../PRD.md)。
P95 空值目前定義為 null；null 對 null 或數值的 gate 比較未定。
不得自行視為 0 或自動通過。
來源：[backend-contract：metrics](../../docs/contracts/backend-contract.md)。

## 缺口 C：context 與 all-failed payload

現有 Contract 列 `TriggerResult`、`EvaluationResult` 最小欄位；SP-02 宣告輸出 adaptation context 與 all-skills-failed。
兩者未定完整交接 schema。
來源：[backend-contract](../../docs/contracts/backend-contract.md)、[SP-02](../../sub-PRDs/existing-skill-adaptation.md)。
**提案名稱，非現有 schema：**`EvaluationContext` 至少含 `run_id`、`baseline_snapshot_version`、`adaptation_id`、`workload_window`、`evaluation_window`、`workload`、`seed`、`baseline_state`、`baseline_policy_id`、`expected_skill_ids`。
**提案名稱，非現有 schema：**`ExistingEvaluationSummary` 至少含 `context`、完整 `results`、`selected_skill_id`（或 null）、`all_failed`。
`all_failed=true` 不可只信布林。它應要求非空且完整的已驗證 Skill 集合；每個預期 Skill 恰有一項完整有效 `EvaluationResult`，且皆未通過 gate。
完整有效結果不等同每次 sandbox 成功：policy runtime／契約違反可為已記錄負結果；外部 timeout、遺失結果、重複 ID、未知 ID 均不得判定全敗。

以上為防止錯誤 Candidate 建立的建議；既有 PRD 僅要求完整結果與全敗判定。
來源：[SP-02](../../sub-PRDs/existing-skill-adaptation.md)、[SP-03](../../sub-PRDs/candidate-evaluation-loop.md)。

## 缺口 D：promotion 不可變證據

現有 `register_skill(candidate_id)` 僅收 Candidate ID，且只接受通過 gate 的 Candidate。
來源：[backend-contract：方法表](../../docs/contracts/backend-contract.md)。
SP-03 要提供不可變 promotion input；SP-04 要拒絕未通過、重複或狀態不明 input。
來源：[SP-03](../../sub-PRDs/candidate-evaluation-loop.md)、[SP-04](../../sub-PRDs/skill-promotion-and-recovery.md)。

**提案，待核定：**`PromotionInput` 包含 context identity、Candidate（唯一 ID、version、parent、code）與其 `EvaluationResult`。
同一 run、adaptation、baseline、Candidate version 必須完整對應且 passed，才可註冊。SP-04 驗證後保存於該 session/run 受控交接狀態。
`register_skill(candidate_id)` 只解析已接納記錄，不讀 SP-03 私有可變物件，也不只信 caller 傳入的 passed 布林；明定保存與查詢方式，不必改公開簽名或新增類別。
不得新增 Skill metadata；關聯資料置於 handoff／evaluation 記錄。
來源：[backend-contract：Skill、Candidate、EvaluationResult](../../docs/contracts/backend-contract.md)。

重複 register 依既有規格拒絕；安全 retry 不可藉再 register 實現。
來源：[SP-04](../../sub-PRDs/skill-promotion-and-recovery.md)。

## 缺口 E：pause、recovery 與副作用

現有規格要求 controller 序列化、拒收舊 revision、state-uncertain 分流及禁止自動重送修改操作。
來源：[backend-contract：共同規則與錯誤](../../docs/contracts/backend-contract.md)。

但未逐一規定 pause/resume、寫入序列化、舊 run 回應、retry checkpoint 的呼叫、回傳與副作用。
此為 schema 層缺口推論。
**設計草案，非公開方法名：**開始適應、讀進度、完成既有重用、登錄、啟用、手動 retry、resync、reset。
每項需定 identity、前置 stage、結果、是否副作用與錯誤規則。正常 adaptation 不前進 live simulation。
來源：[總 PRD](../../PRD.md)、[backend-contract：共同規則](../../docs/contracts/backend-contract.md)。

僅由使用者手動、沿用原 `adaptation_id`、從已確認 checkpoint 接續；不重送已成功 register。只有已證明 activate 未執行且 `state_uncertain=false` 才可 retry activate，否則 resync/reset；activate 已成功而讀 Snapshot 失敗則先 resync，不得重複 segment/event。
此為依「不重送有副作用操作」提出的建議。
來源：[backend-contract：錯誤](../../docs/contracts/backend-contract.md)。

**建議，待核定：**手動 retry 僅重試未完成的外部 stage，不重開版本預算。
五版已確定失敗後能做什麼待產品決策；不得暗中開第六版。
來源：[總 PRD](../../PRD.md)。

## 缺口 F：UI evidence 與 Snapshot 範圍

現有 Snapshot 有 adaptation 最小狀態；UI 要顯示比較、Candidate、feedback、gate、註冊與啟用原因。
完整比較表、版本與 feedback 的讀取契約未凍結。
來源：[backend-contract：Snapshot](../../docs/contracts/backend-contract.md)、[總 PRD：Demo mode](../../PRD.md)。

**建議，待核定：**同一 session controller 持有單一 accepted Snapshot 與 keyed evidence envelope。
SP-01 提供 UI 插入點及 binding 約定；SP-02／03／04 各產生資料，不各自計時或改共同 shell。
render input、更新規則、錯誤型別須凍結。

現有規格一面要求修改操作回 Snapshot，一面列 `register_skill` 回 Skill、`detect_adaptation_trigger` 回 TriggerResult。
應定每個操作的結果及取得最新 Snapshot 的方式，連同錯誤 checkpoint 一起定。
來源：[backend-contract：共同規則與方法表](../../docs/contracts/backend-contract.md)。

SP-03 要求 Live Snapshot loop 前後不變；又要 Snapshot 顯示 events/adaptation 進度。
建議釐清「不變」限排程投影：time、jobs、worker、policy、live metrics、segments、usage 等。
不得直接改既有驗收。
來源：[SP-03](../../sub-PRDs/candidate-evaluation-loop.md)、[backend-contract：Snapshot](../../docs/contracts/backend-contract.md)。

## 缺口 G：外部 Adapter

Planner、Evaluator、Critic 只有名稱與錯誤原則；未定輸入、輸出、schema 校驗、timeout 所有權、sync/async、取消或舊結果丟棄。
來源：[總 PRD](../../PRD.md)、[backend-contract：錯誤](../../docs/contracts/backend-contract.md)。
**建議，待核定：**逐一列出每個 adapter 的輸入、輸出、identity 檢查與失敗結果。

| Adapter | 最小輸入（提案） | 最小輸出（提案） |
| --- | --- | --- |
| Planner | `EvaluationContext`、feedback | Candidate 或可讀錯誤 |
| Evaluator | context、subject、baseline | `EvaluationResult` 或可讀錯誤 |
| Critic | context、Candidate、失敗結果 | feedback 或可讀錯誤 |

controller 僅在同一 session/run/adaptation/revision 身份通過後接納外部結果。
外部 adapter 不得觸碰 live scheduler。

timeout 數值與供應商均不在本稿猜定；維持 provider-neutral。

## 建議 Contract 落點

先補現有 backend-contract 的 SP-01/common shape、操作結果與 Snapshot 取得規則。

另擬一份 `adaptation-contract`，集中 context、evaluation、外部 adapters、promotion、retry、UI evidence。

四份子 PRD 改為指向各節，不造四套重複 Contract。
此回合不新增或修改上述權威文件。
來源：[候選 AGENTS](../../AGENTS.md)、[候選 INDEXER](../../INDEXER.md)。

## Fixture 矩陣（設計測試，非可執行程式）

| 類別 | 固定／提案場景 | 最小預期 |
| --- | --- | --- |
| 排程 | A–D | 保留既有 Policy、deadline、metrics、不搶占 fixtures。來源：[backend-contract：共同 fixtures](../../docs/contracts/backend-contract.md) |
| trigger | 提案：no-trigger／current-reuse／other-reuse／all-failed | 不觸發不評估；目前重用不建 activation；其他重用下次 dispatch 啟用；全敗才交 SP-03。來源：[SP-02](../../sub-PRDs/existing-skill-adaptation.md) |
| 評估 | 提案：incomplete-error／candidate-fail-then-pass／five-fails | 不完整不全敗；失敗回饋；第五版停止。來源：[SP-03](../../sub-PRDs/candidate-evaluation-loop.md) |
| promotion | 提案：promotion-pass／wrong-run-candidate／duplicate-register | 僅對應且 passed 可註冊；錯 run 與重複均拒絕。來源：[SP-04](../../sub-PRDs/skill-promotion-and-recovery.md) |
| recovery | 提案：partial-success-retry／reset-stale-result／two-sessions | 不重送已成功寫入；reset 拒舊結果；session 隔離。來源：[backend-contract：Session 與錯誤](../../docs/contracts/backend-contract.md) |

建議 gate 數字例：baseline `completed=6`、`expired=4`、`p95=5`。

結果斜線順序為 completed／expired／P95：`7/3/4`、`7/4/5` 通過；`6/4/5`、`6/4/4`、`7/3/6` 不通過。

此僅是假設全部 Contract 與 sandbox checks 成功的推導例，不宣稱真實 workload 結果，亦未解決 P95 null。
來源：[總 PRD：gate](../../PRD.md)。

固定結果可證明接線與拒絕規則，不能證明真 gate、sandbox 安全或全隊整合。
正式整合仍依 `main` 證據。
來源：[依賴索引](../../sub-PRDs/DEPENDENCIES.md)。

## 建議工作順序與開始門檻

1. 先決定 trigger 門檻、既有 gate 的 P95 null 語意、baseline、五版 retry，及責任調整。
2. 凍結共同 Contract 與 fixture inputs/expected outputs。
3. 核可四份子 PRD，依 Contract 平行開發。
4. 正式整合依 SP-01、SP-02、SP-03、SP-04 順序；每步等直接 Provider 的 `main` 證據。

來源：[依賴索引](../../sub-PRDs/DEPENDENCIES.md)、[候選 workflow](../../workflow.md)。

開發門檻：已核可子 PRD、對應 Contract、固定輸入與預期、實作窗口。

目前未能宣稱符合此門檻。

## 假設、限制與 ELI5

假設：本稿只以 repository 可讀文件判斷，未查 web、私人訊息或實作 repo。

限制：這不是正式核可，亦不證明產品已可安全開工或可整合。

白話說，四人像各自裝一段水管；先定接頭尺寸，才能同時施工。這裡的接頭包含拿哪一批資料作比較、資料不全時不得誤判全敗、以及改到一半失敗時只能重試尚未完成且安全的步驟。

隊長與產品提出者須決定比較基準、空值、五次失敗後處置與共同判斷責任。現在不能宣稱介面約定已核定；真系統能否接通仍待實作與整合驗證。

## 本回合檢查紀錄

- 僅新增本檔；未改權威文件、索引、程式、issue。
- `git diff --check`：回傳 0；新檔差異回傳 1，未輸出空白錯誤。
- 相對連結檢查：無缺失；不跑 Ruff/Pytest。
- 未發現 pre-commit 設定檔。
- codebase-design 影響：按實際跨功能介面一起定順序、錯誤、狀態與 fixture，不複製四套共用欄位。
