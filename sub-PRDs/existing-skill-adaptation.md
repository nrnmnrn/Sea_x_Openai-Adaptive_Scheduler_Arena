# SP-02：Existing Skill Adaptation

## 基本資料

- 狀態：`Unclaimed`
- 核可狀態：2026-09-12 本次對話使用者已採納四組規格方案；本草案可作權威同步基準。SP-01 seam、真實版本與整合證據尚未確認，只阻擋受影響操作、正式交付與完整驗收。
- 版本：`0.4-draft`
- Owner：待比賽當日認領
- GitHub parent issue：待比賽當日認領後建立
- 核可紀錄：本次對話使用者，2026-09-12；使用者兼任 SP-01 接口確認人與開發版 integrator，姓名與實際版本／證據待 Ticket 據實記錄

## 交付結果

交付「指標惡化後重用既有 Skill」的完整可見路徑：系統偵測 trigger，在相同 sandbox 條件比較所有已驗證 Skills，依固定規則選出最佳通過者，自動啟用，並在 UI 顯示原因、比較與 event；此路徑絕不建立 Candidate。

## 範圍

- 實作 `detect_adaptation_trigger`、既有 Skill evaluation、固定選擇順序與 `existing_skill_reused` 證據。
- 有效 trigger 立即要求 SP-01 暫停 simulation clock；以 `(run_id, workload_window.id)` 去重並沿用 active `adaptation_id`，不排隊、不開第二輪。
- 為每個已驗證 Skill 建立相同 workload、seed、初始 state、evaluation window 與 baseline 的 sandbox evaluation。
- 對目前 Policy 通過、其他 Skill 通過、沒有 Skill 通過三種結果，提供可觀察的 adaptation stage、原因與比較結果。
- 經既定 `activate_skill` seam 自動安排下次 dispatch 使用選定 Skill；不搶占 running Job。
- 在既有 UI shell 顯示 degradation 原因、每項既有 Skill 的 baseline／受測 metrics、選擇原因與啟用 event。

## 不在範圍

不產生 Candidate、不呼叫 Planner、不註冊 Skill、不定義 Candidate evaluator gate 或 Critic feedback。也不修改基礎 scheduler 的排程規則、UI shell 或 Snapshot 基本結構。

## PRD requirement coverage

| PRD 要求 | 本子 PRD 如何覆蓋 | 驗收證據 |
| --- | --- | --- |
| `PRD.md`「自動 adaptation」之 trigger、baseline 與固定選擇 | trigger 成立即暫停並依 run／window 去重；以相同 workload、seed、state、window 評估全部 verified Skills，依固定順序選擇。 | [ACCEPTANCE R07](../ACCEPTANCE.md)：pause、去重、baseline 與 tie-break 證據；局部案例 S02-R01、S02-R02、S02-R04、S02-R05。 |
| `PRD.md`「自動 adaptation」之啟用時點 | 一律記錄 `existing_skill_reused`；目前 Policy 通過時不重建 activation，不同 Skill 通過才記錄 `policy_activated`；成功後恢復。 | [ACCEPTANCE R08](../ACCEPTANCE.md)：條件式 event、resume、running Job 與 next-dispatch 證據；局部案例 S02-R03、S02-R07、S02-R08。 |
| `PRD.md`「Metrics、Snapshot 與 Adapter」 | 分開 sandbox／live metrics，保留同一 Snapshot 與 adaptation context。 | [ACCEPTANCE R17–R18](../ACCEPTANCE.md)：隔離、contract 與同版本 Snapshot evidence；局部案例 S02-R04、S02-R09。 |
| `PRD.md`「Demo 與 Developer mode」 | 顯示 degradation、比較、選擇原因與 events；手動操作不冒充 Agent 決策。 | [ACCEPTANCE R09](../ACCEPTANCE.md)：三 tabs、來源標示與錯誤 evidence；局部案例 S02-R09、S02-R10。 |
| `PRD.md`「90 秒短展示與 progression run」 | 提供可重複的 trigger、既有 Skill evaluation、重用及 resume 路徑。 | [ACCEPTANCE R19](../ACCEPTANCE.md)：team mode 展示與 progression 紀錄；局部案例 S02-R01、S02-R03、S02-R07、S02-R08。 |

## 原型開發分類

依[工作分類表](../docs/product/prototype-work-plan.md)在原 Ticket 內先做 A 獨立或 B 邊做邊談的內部部分，開始前記錄範圍、接口 ID 及未驗證項，不等待整份契約凍結。C 僅停止依賴未決答案的部分。接口討論與決策紀錄集中於[共用表單](../docs/product/interface-discussion-board.md)。開發版試接可使用可辨識的真實未合併版本，條件依 [workflow](../workflow.md)；下表整合條件均指正式交付，並非開發版試接門檻。

## 介面與直接依賴

| 方向（Consumer depends on Provider） | 類型 | 需要的輸出或 contract | 可開始條件 | 整合條件 | 理由 |
| --- | --- | --- | --- | --- | --- |
| SP-02 depends on SP-01 | Contract | SchedulerBackendAdapter、Snapshot、metrics、events、verified Skills、activation、pause／resume seam、UI 插入點 | A／B 依原型分類先行；C 的受影響操作先決定，真實試接依 workflow | S01-FULL merge 並在 main 驗證，使用真實 Arena | 評估與展示必須使用同一 scheduling evidence。 |
| SP-02 depends on SP-01 | Integration | 實際 Snapshot、pause／resume 與 UI shell | A／B 依原型分類先行；C 的受影響操作先決定，真實試接依 workflow | team mode 中以同一 Snapshot 聯合驗收 | 驗證真實 Arena 整合。 |

本子 PRD 向 SP-03 提供含 run／window 唯一鍵的 `TriggerResult`、完整既有 Skill `EvaluationResult[]`、all-skills-failed 判定、active `adaptation_id` 與可追溯 adaptation context。

## I01–I09 介面決策對照與停止門檻

下表只界定本子 PRD 使用或提供的交接，跨功能欄位、操作回傳與責任仍以[交接契約](../docs/contracts/adaptation-contract.md)及同步後的權威文件為準。I01–I09 是本草案採用的審查識別，完整決策內容在本表；主工作樹的[接口討論表](../docs/product/interface-discussion-board.md)目前只是協調入口。2026-09-12 本次對話使用者已採納四組方案；尚未確認的 SP-01 seam、真實版本與驗證證據不能假定存在，本表也不把任何工作轉交 SP-01。

| Interface issue | SP-02 的交付／使用邊界 | 對應交付與驗收案例 | 未決時可做／必須停止的門檻 |
| --- | --- | --- | --- |
| I01 | 使用 SP-01 的 Snapshot、revision 與接受規則，讓 S02-A～C 的讀取、比較與 evidence 對應同一已接受狀態。 | S02-A、S02-C；S02-R02、S02-R09。 | 可做組內缺項檢查與顯示結構；真實 read/envelope seam 與同版本 evidence 未證前不交付相應整合。 |
| I02 | 消費 trigger、pause／resume 與 activation seam；SP-02 只編排既有 Skill 重用流程。 | S02-A、S02-B；S02-R01、S02-R03、S02-R07。 | 已採納 trigger／控制規則；真實 controller seam 未證前不執行相應操作。 |
| I03 | 使用共用 evaluator、baseline、gate 與負結果分類，收集每個 verified Skill 的完整結果。 | S02-A、S02-B；S02-R04、S02-R05。 | 已採納 SP-02 Provider、FIFO、null／負結果規則；Provider 版本與 sandbox 證據未備前不交付結果。 |
| I04 | 使用非零 checkpoint 與隔離 sandbox；不得自行實作或假定 SP-01 的 clone／runner 能力。 | S02-A；S02-R04。 | checkpoint／隔離 seam 未證前，不執行 sandbox evaluation 或宣稱 baseline 驗收。 |
| I05 | 對既有 evaluation 的 request identity、timeout、取消與 recovery 只依採納 checkpoint 規則操作。 | S02-A、S02-B、S02-C；S02-R06、S02-R08、S02-R10。 | 真實 recovery seam 未證前，不提供 retry、取消或重送副作用操作。 |
| I06 | 不提供 promotion input、不呼叫 register；僅確保 S02 的全敗交接不越過 SP-03 直接到 SP-04。 | S02-A；S02-R05。 | 不適用於 SP-02 的實作交付；不擴張本子 PRD 去處理登錄。 |
| I07 | 向 SP-03 提供完整既有 Skill 結果與全敗判定的可追溯交接。 | S02-A；S02-R05。 | 已採納完整性／identity／all-failed 語意；真實 Provider 未交付前不交付 Candidate 流程可用結果。 |
| I08 | 在既有三 tabs 的插入點顯示 SP-02 evidence 與 backend 決定的安全操作；UI 不自行作安全判斷。 | S02-C；S02-R09、S02-R10。 | envelope、插入點與錯誤 action seam 未證前，不交付真實 UI evidence。 |
| I09 | 與 Hybrid fixture 的 gate／register 順序沒有直接交付責任；SP-02 不新增 Hybrid、gate 或 promotion 行為。 | 完整 SP-02 聯合驗收的外部前提；S02-R11。 | 只待真實來源與 SP-01 seam 證據，不能以固定 passed 結果替代。 |

正式交付的解除門檻是：採納內容已回寫適當權威文件、受影響 Provider／Consumer 確認真實 seam、以及表列真實驗收案例可執行。核可與證據可再記入[接口討論表](../docs/product/interface-discussion-board.md)，但該表不取代權威規格。這些是既有[凍結檢查](../docs/contracts/adaptation-contract.md)的 SP-02 套用，不是新 schema 或額外核可流程。

### 已採納方案：trigger、比較集合與全敗判定（I02–I04、I07）

下列規則已由 2026-09-12 本次對話使用者採納，須同步回寫 PRD 與適用 contract。SP-01 seam 的實作邊界、真實版本及驗證仍未提供；在這些證據就緒前，S02-A／B 不得把相關真實操作或驗收標為通過：

- 觀測使用連續的五個模擬秒非重疊 window；某 window 有至少一筆新 `expired` Job 時形成 trigger。window 不重疊，避免同一 expiry 重複觸發。
- baseline Policy 是 FIFO。每個既有 Skill 與 FIFO 比較時，使用同一 checkpoint、seed、workload 與 evaluation window。
- checkpoint 固定後，評分集合只包含當時的非終態 Jobs，包含 `running` 與 `scheduled`；該 checkpoint 前已完成或已逾期的歷史終態 Jobs 不計入評分。
- evaluation 從 pause 當下的 `now` 延續到這個評分集合中已知 deadline 的最大值。若集合沒有任何可評分的 remaining Job，不得呼叫 Planner 或建立 Candidate；應以已核准的完成／停止結果結束此 adaptation。
- 任一評分所需的 P95 或其他可比較數值為 null，該 Skill 是「完整、不可比較的負結果」，不能通過 gate；它不等同 infrastructure failure。timeout、transport／runtime infrastructure error、遺失結果、未知／重複 identity 或契約欄位缺失則是 incomplete，不能作為 all-skills-failed 的證據。

本方案不新增公開 schema、不改寫 SP-01 排程責任，也不授權將 `running` Job 重派或改寫 live state。SP-01 所需 seam 未確認前，S02-A 僅可做 A／B 的結果收集、完整性檢查及隔離組裝；所有依賴該 seam 的真實 trigger、比較、全敗交接和後續 Candidate 路徑保持停止。

## 必要行為

- trigger 未成立時不得開始 evaluation 或啟用 Policy。
- trigger 成立時立即暫停 simulation clock；同一 run／window 的重複 trigger 只回傳現有 `adaptation_id` 與進度，不重跑 evaluation。
- 評估範圍只含已驗證 Skills，且每項使用相同 baseline 條件。
- 若目前 Policy 通過，維持目前 Policy；若多個通過，依 expired 最低、completed 最高、P95 最低、目前 Policy、`skill_id` 選擇。
- 有既有 Skill 通過時必須記錄 `existing_skill_reused`。目前 Policy 通過時維持原 Policy，不建立 `policy_activated` 或新 segment；選到不同 Skill 時才啟用並記錄 `policy_activated`。
- 啟用只影響下一次 dispatch；running Job 保留。sandbox 不得修改 Live Run。
- 既有 Skill 成功重用或啟用後設回播放；不得要求使用者手動調參或接受結果。
- Demo mode 只呈現自動結果；Developer mode 的手動 Skill 測試不得偽裝成這條路徑的 Agent 決策。

## 驗收與證據

| 案例 | 固定輸入／操作 | 預期可觀察結果 | 交接與狀態門檻 |
| --- | --- | --- | --- |
| S02-R01 未觸發 | 未形成已採納 trigger 的 Snapshot。 | 不開始 evaluation、不暫停、不啟用、沒有 Candidate 路徑。 | I02 controller seam 可用時執行；否則僅能測組內不啟動邏輯。 |
| S02-R02 重複 trigger 與 reset | 同一已接受 run／window 重複偵測，再 reset 後以相同時間區間偵測。 | 前者回同一 window／adaptation ID，沒有額外 evaluator 呼叫或 event；後者是新 run。 | I01、I02 的 accepted identity 已凍結。 |
| S02-R03 目前 Policy 重用 | 目前 Policy 的完整既有結果通過。 | 記錄 `existing_skill_reused`，不新增 activation event／segment、不建 Candidate，安全恢復。 | I02、I03、I05；真實控制／gate 已核准。 |
| S02-R04 相同 baseline 與隔離 | 每個 verified Skill 在同一已核准 workload、seed、checkpoint、window 與 baseline 下評估。 | 所有結果可對照同一條件，sandbox 不改 Live Run 排程投影。 | I03、I04；真實 evaluator／sandbox Provider 可用。 |
| S02-R05 多通過與完整全敗 | 分別提供多個完整通過結果，以及每個 verified Skill 都有一個完整有效未通過結果。 | 前者依 PRD 固定排序；後者只交出 H4 全敗交接，不建立 Candidate 或呼叫 Planner。缺項、未知或外部未完成結果不得算全敗。 | I03、I07；全敗語意與 H4 已核准。 |
| S02-R06 評估失敗與恢復 | 已核准的 timeout、契約錯誤與 state-uncertain 結果。 | 保持安全停止、保留可讀錯誤；只提供 backend 判定且核准的 retry／resync／reset，絕不重送成功副作用。 | I05；checkpoint recovery 已核准。 |
| S02-R07 不同 Skill 啟用 | 非目前 Skill 依固定排序獲選，且有 running Job。 | `policy_activated` 只對不同 Skill 記錄；running Job 不重派，新 Policy 從下一次 dispatch 生效。 | I02、I03；真實 activation seam 可用。 |
| S02-R08 成功恢復與新 window | 成功重用或啟用後繼續同一 run，再進入新 workload window。 | simulation clock 恢復，沒有手動調參／接受；可形成下一個 adaptation。 | I02、I05；恢復操作與窗口語意已核准。 |
| S02-R09 同版本 UI evidence | 已接受 Snapshot 與其比較、選擇、event evidence。 | 三 tabs 顯示同一版本的 degradation、baseline／受測 metrics、選擇原因與資料來源；live／sandbox 不混稱改善。 | I01、I08；SP-01 shell 插入點及 envelope 已核准。 |
| S02-R10 UI 錯誤與安全 action | 已核准的 S02-A／B 錯誤、read failure 或 state-uncertain。 | 保留最後有效 evidence，顯示錯誤與唯一後端允許的 action；UI 不自行判斷 retry 安全。 | I05、I08；錯誤／recovery 契約已核准。 |
| S02-R11 Hybrid fixture 邊界 | 若聯合驗收採用既有 Hybrid fixture，追溯其 candidate、gate、register 證據。 | 僅使用已證明的真實來源；SP-02 不製造固定 passed、人工 accept 或 promotion。 | I09 解除且 SP-01／main 所需確認完成；否則此聯合案例不執行。 |
| S02-R12 已採納比較規則 | 連續五秒非重疊 window 內新增至少一筆 `expired` Job，並固定 FIFO／同一 checkpoint 比較。 | trigger 只形成一次；評分僅涵蓋 checkpoint 的 `running`、`scheduled` 與其他非終態 Jobs，至其最大已知 deadline；歷史終態不計。 | I02～I04、I07 的真實 seam 與驗證證據可用；否則本案例不得執行。 |
| S02-R13 已採納空集合、null 與 incomplete | 分別使用沒有 remaining Job、null 可比較數值、timeout、遺失結果與未知／重複 identity。 | 空集合不呼叫 Planner／不建 Candidate；null 是完整負結果；其餘均為 incomplete，不能當 all-skills-failed。 | I03、I05、I07 的真實 seam 與驗證證據可用；否則本案例不得執行。 |

S02-R01～S02-R10 以可重現輸入驅動真實 team adapter 重跑；正式整合等待 S01-FULL 在 main 驗證，不以替身代替上游。S02-R11 是跨子 PRD 的聯合驗收前提，不是 SP-02 新增的獨立交付。S02-R12～S02-R13 驗證已採納方案，仍須真實 seam 與版本證據才可執行。

## Ticket 設計與數量閘門

預估 Ticket 數：3 張。以下為已採納的真實切片設計，不代表已建立 GitHub Ticket；交付對照見下節：

1. **從 degradation 到全部既有 Skills 比較。** trigger 成立後，以相同 baseline 評估每個 verified Skill，並讓使用者看見比較結果；未成立則不執行。此片承接既有評估逾時／錯誤／狀態不明的完整安全恢復，細部 checkpoint 依已採納 D5，UI 由第三片呈現。
2. **從固定選擇到恢復與下一次 dispatch。** 選出通過者，保留 running Job，產生 reuse／activation evidence，恢復 simulation clock；整條路徑不建立 Candidate。
3. **完成 Adaptation evidence UI。** 同一 Snapshot 顯示 degradation、baseline／受測 metrics、選擇原因與 events，並驗證真實 team 來源標示；呈現 S02-A／B 的錯誤及安全恢復操作。

## 已核定產品行為

指標惡化即暫停 simulation clock；同一 run、同一 workload window 只有一個 active `adaptation_id`。重複 trigger 沿用現有進度，不排隊、不重開；成功重用後自動恢復。

## 真實切片交付與開始條件

採 [workflow](../workflow.md) 的 SP-02～04 切片模式；以下 ID 是規格交付識別，不是已發佈 Ticket。每張 Ticket 自己的 branch／PR 經人類授權 merge、main 驗證後才結案；整份功能仍須全部驗收。相關契約見 [H1～H8](../docs/contracts/adaptation-contract.md)，未決內容見 [D1～D9](../docs/product/adaptation-decisions.md)。

| 交付 ID | 提供的真實結果 | 正式整合所需上游 | 使用者 | 待決 blocker | 驗證方式 |
| --- | --- | --- | --- | --- | --- |
| S02-A | 從 degradation 到完整既有 Skill 比較（H2、H3、H4、H7） | S01-FULL；H3 的 SP-02 共用評估 Provider | SP-03 消費 H4；SP-02 後續切片 | controller／checkpoint／sandbox seam 證據 | 真實 trigger、相同 baseline、完整比較／全敗與錯誤證據，包含安全停止與評估逾時／錯誤回應／狀態不明後的手動 retry／resync／reset：安全 retry 沿用 ID、不重做成功副作用，狀態不明只 resync／reset；依已採納 D5 checkpoint 驗證，seam 未備不可交付。 |
| S02-B | 固定選擇、重用／啟用及恢復（H2、H7） | S01-FULL、S02-A | UI 與完整 SP-02 驗收 | D1～D5、D7、D8 | 目前 Policy 無新增 activation；其他通過者固定排序；成功恢復、不重派 running Job；失敗保持暫停，依 H7／D5 驗證本片控制操作的安全恢復。 |
| S02-C | 完整 Adaptation evidence UI（H8） | S01-FULL、S02-A、S02-B | 使用者與完整功能驗收 | D4～D6、D8、D9 | 同一已接受版本呈現比較、選擇與條件式 event；真實來源可追溯；呈現 S02-A／B 錯誤、可用恢復操作及狀態不明限制，不由 UI 自行判斷安全。 |

- 原型開工依上述 A／B／C 分類；表列 D 項阻擋的是依賴答案的部分及正式交付，不是整組停工。未定語意／責任不自行補值；未接真實上游不宣稱相應結果通過。
- 正式整合時，表列上游均需 merge 並在 main 驗證；S01-FULL 指 SP-01 整份完成，不要求其提前拆分。
- S02-A 承接既有評估的完整安全恢復；S02-B 承接自身控制錯誤恢復；S02-C 呈現兩者。沿用三張 Ticket，沒有未列出的「後續恢復切片」，也不等待 SP-04。各片須具安全停止及副作用保護；恢復細節依已採納 D5／H7 實作驗證。
- 本次不降低原驗收。D4 責任與 D6 Snapshot 隔離範圍已採納；SP-01 或其他 Provider 未提供真實 seam 時，只停止相應交付，不自行推定能力已存在。
- 完整子 PRD 結案仍需所有直接 Provider 的完整所需成果與全流程驗收；切片提早交付不代表略過其他路徑。
