# SP-02：Existing Skill Adaptation

## 基本資料

- 狀態：`Unclaimed`
- 核可狀態：原型 A／B 開工依 workflow 與工作分類；產品／契約待決事項及整份驗收未核准，不推定完整交付
- 版本：`0.3-draft`
- Owner：待比賽當日認領
- GitHub parent issue：待比賽當日認領後建立
- 核可紀錄：待填核可者、日期與連結

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
| `PRD.md`「自動 adaptation」之 trigger、baseline 與固定選擇 | trigger 成立即暫停並依 run／window 去重；以相同 workload、seed、state、window 評估全部 verified Skills，依固定順序選擇。 | R07–R08；pause、去重、baseline 與 tie-break 測試。 |
| `PRD.md`「自動 adaptation」之啟用時點 | 一律記錄 `existing_skill_reused`；目前 Policy 通過時不重建 activation，不同 Skill 通過才記錄 `policy_activated`；成功後恢復。 | R08–R09；條件式 event、resume、running Job 與 next-dispatch 測試。 |
| `PRD.md`「Metrics、Snapshot 與 Adapter」 | 分開 sandbox／live metrics，保留同一 Snapshot 與 adaptation context。 | R07、R09、R17–R18；contract 與 Snapshot 證據。 |
| `PRD.md`「Demo 與 Developer mode」 | 顯示 degradation、比較、選擇原因與 events；手動操作不冒充 Agent 決策。 | R09、R20；瀏覽器及來源標示證據。 |
| `PRD.md`「90 秒短展示與 progression run」 | 提供可重複的 trigger、既有 Skill evaluation、重用及 resume 路徑。 | R19–R20；team mode 短展示與 progression 紀錄。 |

## 原型開發分類

依[工作分類表](../docs/product/prototype-work-plan.md)在原 Ticket 內先做 A 獨立或 B 邊做邊談的內部部分，開始前記錄範圍、接口 ID 及未驗證項，不等待整份契約凍結。C 僅停止依賴未決答案的部分。接口討論與決策紀錄集中於[共用表單](../docs/product/interface-discussion-board.md)。開發版試接可使用可辨識的真實未合併版本，條件依 [workflow](../workflow.md)；下表整合條件均指正式交付，並非開發版試接門檻。

## 介面與直接依賴

| 方向（Consumer depends on Provider） | 類型 | 需要的輸出或 contract | 可開始條件 | 整合條件 | 理由 |
| --- | --- | --- | --- | --- | --- |
| SP-02 depends on SP-01 | Contract | SchedulerBackendAdapter、Snapshot、metrics、events、verified Skills、activation、pause／resume seam、UI 插入點 | A／B 依原型分類先行；C 的受影響操作先決定，真實試接依 workflow | S01-FULL merge 並在 main 驗證，使用真實 Arena | 評估與展示必須使用同一 scheduling evidence。 |
| SP-02 depends on SP-01 | Integration | 實際 Snapshot、pause／resume 與 UI shell | A／B 依原型分類先行；C 的受影響操作先決定，真實試接依 workflow | team mode 中以同一 Snapshot 聯合驗收 | 驗證真實 Arena 整合。 |

本子 PRD 向 SP-03 提供含 run／window 唯一鍵的 `TriggerResult`、完整既有 Skill `EvaluationResult[]`、all-skills-failed 判定、active `adaptation_id` 與可追溯 adaptation context。

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

- trigger 未成立、目前 Policy 通過、多個通過的 tie-break、所有失敗各有 deterministic 測試；目前 Policy 通過不得新增 activation event／segment。
- 驗證有效 trigger 立即暫停且 clock／Job 不前進；同一 Snapshot 重複偵測取得相同 window／adaptation ID，且不增加 evaluator 呼叫或 event；reset 後相同時間區間屬新 run。
- 所有 sandbox evaluation 都證明 baseline 條件相同且不改 Live Run Snapshot。
- 有 Skill 通過時，測試證明無 Candidate、無 Planner 呼叫、無新 Skill；下次 dispatch 才採新 Policy。
- 驗證成功重用後由同一 Snapshot 恢復，未重派 running Job，且 progression run 可再次進入新的 workload window。
- UI／event／metrics 用同一 Snapshot 顯示 degradation、比較、選擇與啟用原因。
- 以上以可重現輸入驅動真實 team adapter 重跑；正式整合等待 S01-FULL 在 main 驗證，不以替身代替上游。

## Ticket 設計與數量閘門

預估 Ticket 數：3 張。以下為待核可的真實切片設計，不代表已建立 GitHub Ticket；交付對照見下節：

1. **從 degradation 到全部既有 Skills 比較。** trigger 成立後，以相同 baseline 評估每個 verified Skill，並讓使用者看見比較結果；未成立則不執行。此片承接既有評估逾時／錯誤／狀態不明的完整安全恢復，細部 checkpoint 待 D5，UI 由第三片呈現。
2. **從固定選擇到恢復與下一次 dispatch。** 選出通過者，保留 running Job，產生 reuse／activation evidence，恢復 simulation clock；整條路徑不建立 Candidate。
3. **完成 Adaptation evidence UI。** 同一 Snapshot 顯示 degradation、baseline／受測 metrics、選擇原因與 events，並驗證真實 team 來源標示；呈現 S02-A／B 的錯誤及安全恢復操作。

## 已核定產品行為

指標惡化即暫停 simulation clock；同一 run、同一 workload window 只有一個 active `adaptation_id`。重複 trigger 沿用現有進度，不排隊、不重開；成功重用後自動恢復。

## 真實切片交付與開始條件

採 [workflow](../workflow.md) 的 SP-02～04 切片模式；以下 ID 是規格交付識別，不是已發佈 Ticket。每張 Ticket 自己的 branch／PR 經人類授權 merge、main 驗證後才結案；整份功能仍須全部驗收。相關契約見 [H1～H8](../docs/contracts/adaptation-contract.md)，未決內容見 [D1～D9](../docs/product/adaptation-decisions.md)。

| 交付 ID | 提供的真實結果 | 正式整合所需上游 | 使用者 | 待決 blocker | 驗證方式 |
| --- | --- | --- | --- | --- | --- |
| S02-A | 從 degradation 到完整既有 Skill 比較（H2、H3、H4、H7） | S01-FULL；H3 共用評估 Provider 待 D4 | SP-03 消費 H4；SP-02 後續切片 | D1～D9 | 真實 trigger、相同 baseline、完整比較／全敗與錯誤證據，包含安全停止與評估逾時／錯誤回應／狀態不明後的手動 retry／resync／reset：安全 retry 沿用 ID、不重做成功副作用，狀態不明只 resync／reset；依 D5 核准 checkpoint 驗證，未解決不可交付。 |
| S02-B | 固定選擇、重用／啟用及恢復（H2、H7） | S01-FULL、S02-A | UI 與完整 SP-02 驗收 | D1～D5、D7、D8 | 目前 Policy 無新增 activation；其他通過者固定排序；成功恢復、不重派 running Job；失敗保持暫停，依 H7／D5 驗證本片控制操作的安全恢復。 |
| S02-C | 完整 Adaptation evidence UI（H8） | S01-FULL、S02-A、S02-B | 使用者與完整功能驗收 | D4～D6、D8、D9 | 同一已接受版本呈現比較、選擇與條件式 event；真實來源可追溯；呈現 S02-A／B 錯誤、可用恢復操作及狀態不明限制，不由 UI 自行判斷安全。 |

- 原型開工依上述 A／B／C 分類；表列 D 項阻擋的是依賴答案的部分及正式交付，不是整組停工。未定語意／責任不自行補值；未接真實上游不宣稱相應結果通過。
- 正式整合時，表列上游均需 merge 並在 main 驗證；S01-FULL 指 SP-01 整份完成，不要求其提前拆分。
- S02-A 承接既有評估的完整安全恢復；S02-B 承接自身控制錯誤恢復；S02-C 呈現兩者。沿用三張 Ticket，沒有未列出的「後續恢復切片」，也不等待 SP-04。各片須具安全停止及副作用保護；恢復細節由 D5／H7 核准後實作驗證。
- 本次不調整原有產品責任或降低原驗收。D4 責任配置、D6 Snapshot 不變範圍等尚未解決時，停止相應交付，不自行推定 SP-01 或其他 Provider 已承諾。
- 完整子 PRD 結案仍需所有直接 Provider 的完整所需成果與全流程驗收；切片提早交付不代表略過其他路徑。
