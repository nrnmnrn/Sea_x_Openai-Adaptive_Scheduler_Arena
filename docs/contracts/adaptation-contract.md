# Adaptation 交接契約與凍結門檻

## 狀態與權威

2026-09-12 使用者已採納 trigger／baseline／負結果、責任與重放安全、request／recovery／evidence，以及 Hybrid 真實來源四組方案。產品選擇與公開 identity/query 以 [PRD](../../PRD.md) 及 [backend-contract](backend-contract.md) 為唯一來源，本文件不另造第二套型別。尚未提供真實實作證據的 SP-01 controller、checkpoint、storage、UI shell seam，仍是交付凍結與整合 blocker，不能把方案採納寫成 seam 已完成。

使用者兼任 SP-01 接口確認者與開發版 integrator；其具體 seam、版本與真實驗證證據仍須在 Ticket／交付紀錄據實填寫。流程核准與產品核准分開；見 [待決清單](../product/adaptation-decisions.md)。

接口協調使用[討論表](../product/interface-discussion-board.md)，表單決定須回寫權威後生效。真實開發版試接不等於本文件交付凍結或 main 驗收。

## 必要交接目錄

H 編號是文件追蹤 ID，不是 API 名稱，也不是新建 Ticket。表中功能層級提供者依既有子 PRD；內部實作責任有缺口時明列待決，不能由下游自行補實作或形成反向依賴。

| ID | 提供者 → 使用者 | 交付資料與操作／契約位置 | 真實驗證方式 | 凍結缺口 |
| --- | --- | --- | --- | --- |
| H1 | SP-01 → SP-02、03、04 | backend 的 Job、Skill、Snapshot、metrics、segments、read／revision；accepted Snapshot 與 evidence identity。 | 兩 session、防禦副本、舊 generation/run/revision 拒收。 | SP-01 read/controller seam 的真實證據待填。 |
| H2 | SP-01 scheduler seam、SP-02 trigger flow → SP-02；後續 SP-03／04 使用共同控制 | 五秒 non-overlap trigger、同一序列化 pause/checkpoint、active adaptation 拒絕 live mutations；成功 reuse/activate 才 resume。 | 跨界 trigger 即停、重複不重跑、四個拒絕操作、reset 舊結果拒收。 | SP-01 pause/checkpoint/control seam 待真實證據。 |
| H3 | SP-01 checkpoint seam → SP-02 共用 evaluator → SP-03 | FIFO baseline、非零 checkpoint、同 context gate、sandbox isolation；SP-02 是 evaluator Provider，SP-03 重用。 | 改善／持平／退步、null、policy error、infra timeout，及 running/scheduled/RNG 重放。 | SP-01 clone/isolated runner seam 與安全執行能力待證。 |
| H4 | SP-02 → SP-03 | immutable complete comparison：預期 verified IDs/code versions、observation/evaluation windows、context、baseline、每項 EvaluationResult/outcome/reason。僅 expected 非空、每項完整負結果才 all-failed。 | pass、缺失、重複、未知、baseline/window mismatch、incomplete/error 均不得啟 Planner。 | SP-02 真實 Provider 版本待交付。 |
| H5 | SP-03 Planner／Critic loop → SP-04 | identity、60/60/10 秒 timeout、取消與安全 stage retry；SP-03 只在 H4 all-failed 後建 Candidate。 | 拒絕→feedback→下一版、五版停止、schema/timeout/遲回拒收。 | 真實 adapter 與 controller seam 待驗證。 |
| H6 | SP-03 accepted Candidate → SP-04 promotion → storage/activation Provider | trusted query 以 `(run_id, adaptation_id, candidate_id, version)` 取得 exact Candidate、EvaluationResult、context identity；`register_skill` 不信 caller 重傳 code/passed，成功仍只回最小 Skill。 | 未通過、缺 result、錯 version/code、duplicate 均拒絕；已完成 register 先 query 再恢復。 | SP-01 storage/activate seam 的真實能力待證。 |
| H7 | SP-01 controller/reset seam；SP-02、03、04 各自流程錯誤處理 → 各階段與 UI | backend「Session 與錯誤」的已採納 identity、timeout、取消、retry/resync/reset 規則；SP-02 負責 evaluator、SP-03 planner/critic、SP-04 promotion 的流程恢復。 | 真實操作受控失敗；保留最後有效畫面、保持暫停；安全手動 retry 沿用 ID、不重做成功登錄／啟用；狀態不明 resync/reset；reset 拒收舊結果。 | 各 Provider checkpoint、controller/reset seam 與實測證據待具備；不可令 SP-02／03 的安全恢復等待 SP-04。 |
| H8 | SP-01 UI shell；SP-02 比較、SP-03 候選、SP-04 登錄 evidence → 同一 UI | backend Snapshot/Event、已採納的 UI envelope identity 與同版本 evidence 綁定；不另造 schema。 | 真實各階段 evidence 同一已接受 run/version；兩 session、過時回應、錯誤最後有效畫面；三 tabs、來源、live/sandbox 區分。 | SP-01 shell/read seam、各 evidence Provider 版本與瀏覽器整合證據待具備。 |

## 已有行為邊界

- 既有 Skill 與 Candidate 使用同一產品 gate；不能各寫不同通過條件。目前 Policy 通過只重用，不新增 activation／segment；全敗才進 Planner。
- Candidate 最多五版；只有 gate-passed 才 register。外部錯誤停止 adaptation、保持暫停、不自動 retry 或切 Mock；安全手動 retry 沿用 adaptation ID，不重做已完成副作用；狀態不明只 resync/reset。
- Sandbox 與 Live metrics 分開；Skill 不增加契約外 metadata；新 Policy 只在下一次 dispatch 生效。
- 已採納的選擇不免除 H 的 Provider 真實版本、main 整合與驗收；尤其 SP-01 seam 未有能力證據前，受影響操作仍不可宣稱可交付。

## 凍結檢查

每個 H 交付凍結前，提供者與使用者共同確認以下項目並由人類核可：

1. 資料：必填／可空、型別／enum、ID 與版本、完整性、序列化、不可變範圍；已有型別留在 backend，不複製另一套。
2. 操作：呼叫者與實作者、參數、回傳、前置 stage、成功／拒絕後狀態、副作用、Snapshot 取得及 UI 接納規則。
3. 失敗：validation、policy 負結果、外部錯誤、部分成功、狀態不明的分類；timeout 責任；手動 retry/resync/reset checkpoint；取消與過時結果。
4. 驗證：真實輸入來源、正常與拒絕預期、錯誤案例、Provider 合併版本、main 驗證命令／畫面。固定測試資料不能代替真實 Provider。
5. 核可：所有影響本交付的 D 項已決定並更新權威文件；SP-01 邊界變更有其負責人確認。記錄契約版本及提供／使用雙方確認；未完成則仍是 blocker。

## 切片交付對照

S01-FULL、S02-A～C、S03-A～C、S04-A～C 的範圍與直接依賴以各[子 PRD](../../sub-PRDs/DEPENDENCIES.md)為準。H1～H8 不代表全部由 SP-01 提供；未定責任不可因方法列在 BackendAdapter 就推定由 SP-01 實作。
