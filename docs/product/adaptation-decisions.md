# Adaptation 待決事項與受影響工作

2026-09-12 本次對話中，使用者已採納下表 D1～D9 的產品選擇與公開契約方向，並同步至 PRD 與 contracts。這不等於各 Provider seam 已實作、驗證或可正式整合；SP-01 interface confirmation/integrator 角色由同一位使用者兼任，但仍須以真實版本與證據完成各交付凍結。

原型依 [workflow](../../workflow.md) 與[工作分類](prototype-work-plan.md)開發；下表阻擋的是依賴答案的部分及相應正式交付，不是阻擋整組 A／B 工作。用[接口討論表](interface-discussion-board.md)收集問題、參與者與證據，不能把建議當結論。

## 決策清單

| ID | 已採納選擇 | 影響 | 受影響交付／工作 | 尚待完成的 Provider／seam 證據 |
| --- | --- | --- | --- | --- |
| D1 | 五秒非重疊 `(t-5,t]` window；新增 `expired >= 1` trigger。 | 跨界逐邊界檢查並立即 pause。 | H2、S02-A。 | SP-01 control seam、fixture 驗證。 |
| D2 | FIFO baseline；同一非零 checkpoint、seed、workload/window；只評 checkpoint 非終態集合。 | 空集合不啟 Planner。 | H3～H5、S02/S03。 | SP-01 clone seam、SP-02 evaluator Provider。 |
| D3 | P95 不可比較、policy error、契約違反為完整負結果；baseline failure、infra/未知 timeout、缺失或 identity 不符為 incomplete/error。 | incomplete/error 不得 all-failed。 | H3～H5。 | 真實 gate 案例。 |
| D4 | SP-02 提供共用 evaluator/all-failed comparison；SP-03 reuse gate/accepted Candidate；SP-04 promotion。 | 不將 controller/checkpoint/storage/UI 自動歸 SP-01。 | H2～H8。 | Owner 接受與 SP-01 seam 證據。 |
| D5 | Planner/Critic 60 秒、Evaluator 10 秒；取消失效、遲回丟棄；只 retry 未完成 stage，副作用先 query。 | 五版失敗只 resync/reset。 | H5、H7。 | 真實 adapter/recovery 測試。 |
| D6 | evaluation 不改 scheduler state；Live Snapshot 僅 adaptation/evidence、對應 event、version/revision 可變；Hybrid 要真實 gate→register。 | 保留隔離與 fixture gate。 | H1、H3、H8。 | SP-01 evidence/fixture seam。 |
| D7 | active adaptation 拒絕 advance/inject/generate/developer set_policy；reset 作廢舊結果。 | 保護 checkpoint 一致性。 | H2、H3、H7。 | SP-01 control seam、聯測。 |
| D8 | mutation 保持既定回傳；controller 後續讀 accepted Snapshot；playing 屬 UI envelope。 | 防止回傳矛盾與重送。 | H1、H2、H6～H8。 | SP-01 controller/read seam。 |
| D9 | accepted Candidate 以 run/adaptation/candidate/version 精確 query；evidence 與 accepted Snapshot 同版本。 | 不憑 bool promotion、不加 Skill metadata。 | H4、H6、H8。 | storage/UI seam、Provider 版本與整合證據。 |

## 解除方式

每項決策記錄：選擇、理由、核可者／日期／證據、受影響 Owner 確認、權威文件章節與版本、驗證案例、解除的交付／Ticket。更新相關正式規格後再重驗開工條件；只回覆「同意流程」或只關閉工作單都不能解除。

已核准的是 [ADR 0003](../adr/0003-real-slice-delivery.md) 的正式交付方式、[ADR 0004](../adr/0004-prototype-parallel-development.md) 的原型開工／試接流程，以及本表 2026-09-12 採納的產品／契約選擇。各子 PRD 的完整交付仍待獨立驗收；使用者兼任 SP-01 interface confirmation/integrator，不取代真實 seam、版本與 main 證據。
