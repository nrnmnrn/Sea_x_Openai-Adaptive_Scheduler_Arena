# Adaptation 交接契約與凍結門檻

## 狀態與權威

本次先集中既有交接責任與契約缺口，**不是已凍結的完整 API schema**。標為待決的介面不是可執行的已核准契約；不依賴該答案的 A／B 內部工作可依 [workflow](../../workflow.md) 先行，不能自行補值。產品以 [PRD](../../PRD.md) 為準；現有資料型別、方法與錯誤以 [backend-contract](backend-contract.md) 為唯一來源，本文件不另造第二套型別。調查中的 EvaluationContext、ExistingEvaluationSummary、PromotionInput 是提案名稱，尚非公開介面。

流程核准與產品核准分開；見 [待決清單](../product/adaptation-decisions.md)。新增 schema、責任轉移及 SP-01 介面改動仍須人類核可與該負責人確認。

接口協調使用[討論表](../product/interface-discussion-board.md)，表單決定須回寫權威後生效。真實開發版試接不等於本文件交付凍結或 main 驗收。

## 必要交接目錄

H 編號是文件追蹤 ID，不是 API 名稱，也不是新建 Ticket。表中功能層級提供者依既有子 PRD；內部實作責任有缺口時明列待決，不能由下游自行補實作或形成反向依賴。

| ID | 提供者 → 使用者 | 交付資料與操作／契約位置 | 真實驗證方式 | 凍結缺口 |
| --- | --- | --- | --- | --- |
| H1 | SP-01 → SP-02、03、04 | backend「排程資料」「Snapshot 與 Event」「Metrics」「Session 與錯誤」：Job、Skill、Snapshot、metrics、segments、讀取／revision；本文件「凍結檢查」補齊時引用同一型別。 | 真實 factory；兩個 session；舊 run/revision 拒收；JSON、防禦副本、attribution；固定 Jobs 跑真實 scheduler。 | D6、D8：Snapshot 不變範圍／回傳矛盾；細部 shape 由 SP-01 確認。 |
| H2 | SP-01 pause/resume 與 scheduler seam、SP-02 trigger 流程 → SP-02；後續 SP-03／04 使用共同控制 | backend「BackendAdapter 方法」「共同規則」「Session 與錯誤」；trigger 既有 identity 與 pause 原則不變，精確控制方法／底層 activation 責任待 D4。 | 真實 trigger 即停鐘；重複 run/window 不重開；成功重用無新 segment；不同 Skill 下次 dispatch 才生效；reset 舊回應拒收。 | D1、D4、D7、D8。 |
| H3 | SP-01 被要求的 sandbox 基礎、共用評估 Provider 待 D4 → SP-02、03 | backend「EvaluationResult」「Metrics」，PRD「自動 adaptation」同一 gate；完整 context／baseline 重放、呼叫方式待決。 | 同一 workload/seed/state/window/baseline 真實重放；嚴格改善、持平、退步、null、契約違反；驗證隔離。 | D2～D4、D6、D7；不推定 SP-01 已承諾新 sandbox API。 |
| H4 | SP-02 → SP-03 | backend 的 TriggerResult、EvaluationResult；本節凍結時須補全 context 與全敗交接 schema。包括預期 verified Skill 集合、每項結果與原因、選擇結果、run/window/adaptation 關聯。 | 真實比較結果驅動；任一通過不得呼叫 Planner；全敗有完整證據；缺失／重複／未知結果、外部中斷不能冒充已完成。負結果分類依 D3。 | D2～D4、D9。 |
| H5 | SP-03 Planner／Critic 與 Candidate loop；Evaluator Provider 待 D4 → SP-03，結果續交 SP-04 | backend Candidate、EvaluationResult 與錯誤原則；Planner/Evaluator/Critic 請求、結果、timeout、版本／identity、取消方式尚待凍結。 | 真實外部 adapter；未全敗不啟動；拒絕→feedback→下一版；五版停止；timeout/schema 錯誤不自動 retry／Mock；過時结果拒收。 | D2～D5。 |
| H6 | SP-03 合格候選 → SP-04 promotion → backend 儲存／啟用（底層 Provider 待 D4） | backend register_skill、activate_skill、Candidate、Skill；需凍結 candidate ID/version/code/context/result 不可變對應及可信已接受結果查詢，不增加 Skill metadata。 | 真實 passed 結果登錄；未通過、缺結果、錯版本、重複登錄拒絕且不改庫；啟用後新 segment、running Job 不重派、下次 dispatch 生效。 | D4、D8、D9；不能以固定 passed 回應驗收。 |
| H7 | SP-01 既有 controller/reset；SP-02、03、04 各自流程錯誤處理（共用 checkpoint 責任待 D4） → 各階段與 UI | backend「Session 與錯誤」；每操作的前置狀態、成功 checkpoint、副作用與部分失敗需逐項凍結。 | 真實操作受控失敗；保留最後有效畫面、保持暫停；安全手動 retry 沿用 ID、不重做成功登錄／啟用；狀態不明 resync/reset；reset 拒收舊結果。 | D4、D5、D7、D8。不可令 SP-02／03 的安全恢復等待 SP-04 完成才存在。 |
| H8 | SP-01 UI shell；SP-02 比較、SP-03 候選、SP-04 登錄證據 → 同一 UI | backend Snapshot/Event、UI envelope；完整 evidence 查詢、插入點、同版本綁定待凍結。 | 真實各階段 evidence 同一已接受 run/version；兩 session、過時回應、錯誤最後有效畫面；三 tabs、來源、live/sandbox 區分。 | D4、D6、D8、D9。 |

## 已有行為邊界

- 既有 Skill 與 Candidate 使用同一產品 gate；不能各寫不同通過條件。目前 Policy 通過只重用，不新增 activation／segment；全敗才進 Planner。
- Candidate 最多五版；只有 gate-passed 才 register。外部錯誤停止 adaptation、保持暫停、不自動 retry 或切 Mock；安全手動 retry 沿用 adaptation ID，不重做已完成副作用；狀態不明只 resync/reset。
- Sandbox 與 Live metrics 分開；Skill 不增加契約外 metadata；新 Policy 只在下一次 dispatch 生效。
- 本文件不解決 D2/D3 的數值語意、不定新方法名稱或 timeout 值，也不放寬現有 Snapshot 隔離驗收。遇到矛盾停止受影響驗證，依待決清單處理。

## 凍結檢查

每個 H 交付凍結前，提供者與使用者共同確認以下項目並由人類核可：

1. 資料：必填／可空、型別／enum、ID 與版本、完整性、序列化、不可變範圍；已有型別留在 backend，不複製另一套。
2. 操作：呼叫者與實作者、參數、回傳、前置 stage、成功／拒絕後狀態、副作用、Snapshot 取得及 UI 接納規則。
3. 失敗：validation、policy 負結果、外部錯誤、部分成功、狀態不明的分類；timeout 責任；手動 retry/resync/reset checkpoint；取消與過時結果。
4. 驗證：真實輸入來源、正常與拒絕預期、錯誤案例、Provider 合併版本、main 驗證命令／畫面。固定測試資料不能代替真實 Provider。
5. 核可：所有影響本交付的 D 項已決定並更新權威文件；SP-01 邊界變更有其負責人確認。記錄契約版本及提供／使用雙方確認；未完成則仍是 blocker。

## 切片交付對照

S01-FULL、S02-A～C、S03-A～C、S04-A～C 的範圍與直接依賴以各[子 PRD](../../sub-PRDs/DEPENDENCIES.md)為準。H1～H8 不代表全部由 SP-01 提供；未定責任不可因方法列在 BackendAdapter 就推定由 SP-01 實作。
