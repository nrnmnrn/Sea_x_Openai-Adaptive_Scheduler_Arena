# 子 PRD 真實交付與整合索引

本檔只作索引：子 PRD 是交付範圍與直接依賴的權威，共同契約是介面權威，開工、開發版試接、正式交付與完整結案以 [workflow](../workflow.md) 為準。方向固定「Consumer depends on Provider」。

## 開發與正式交付

原型可依[工作分類](../docs/product/prototype-work-plan.md)先做 A／B，接口問題集中於[討論表](../docs/product/interface-discussion-board.md)；C 只停受影響部分。可依 workflow 使用可辨識的真實未合併版本試接；沒有真實上游就不能完成相應驗證。本次不以測試替身作 readiness 證據。正式整合要求所需交付已 merge 並在 main 驗證。SP-01 保留整份交付；SP-02～04 自身切片也須人類授權 merge 及 main 驗證才能結案。

| 子 PRD | 功能層直接依賴 | 交付／正式整合門檻 | 未決與限制 |
| --- | --- | --- | --- |
| [SP-01](scheduling-arena.md) | None | S01-FULL：整份驗收、merge、main 證據；不要求提前切片。 | 執行／核可連結需負責人提供；D6 Hybrid 證據及其他介面改動先確認，不重分派責任。 |
| [SP-02](existing-skill-adaptation.md) | SP-02 depends on SP-01 | S02-A 依 S01-FULL；S02-B 再依 S02-A；S02-C 再依 S02-A/B。 | 2026-09-12 使用者已採納四組方案；SP-01 controller、checkpoint、activation 與 UI seam 的真實版本／驗證仍只阻擋受影響操作。 |
| [SP-03](candidate-evaluation-loop.md) | SP-03 depends on SP-01、SP-02 | S03-A 依 S01-FULL、S02-A 的真實全敗交付；S03-B 再依 S03-A；S03-C 再依 S03-A/B。 | 已採納方案不取代真實全敗、checkpoint、adapter 與 evidence seam；S03-A 仍需可安全交付的真實單版結果，不能把替身 passed 當成果。 |
| [SP-04](skill-promotion-and-recovery.md) | SP-04 depends on SP-01、SP-03 | S04-A 依 S01-FULL、S03-A 真實 passed 結果；S04-B 再依 S04-A；S04-C 再依 S04-A/B。 | 已採納方案不取代 H6 的真實 passed／可信交接與 register seam；SP-02 是經 SP-03 的傳遞依賴，不能跳過真實全敗證據。 |

## 必要交接位置

| 交付 | 提供／使用與契約、驗證索引 |
| --- | --- |
| S01-FULL | SP-01 → SP-02／03／04；[交接契約 H1、H2、H3、H7、H8](../docs/contracts/adaptation-contract.md)，其中未定能力不自動歸 SP-01。 |
| S02-A | SP-02 → SP-03；H4 完整既有結果／全敗證據；H7 自身評估錯誤恢復，UI 由 S02-C 承接；採納的共用評估責任仍須以真實 Provider seam 證明。 |
| S03-A／B | SP-03 → SP-04；H5／H6 真實 Candidate、gate、不可變 promotion 證據。 |
| S02-B／C、S03-C、S04-A～C | 各功能 → UI／完整產品；H2、H6～H8 的控制、恢復、登錄與同版本證據。 |

已採納方案與尚待真實驗證的 seam 詳見各子 PRD及[交接契約](../docs/contracts/adaptation-contract.md)。上述切片規格不代表已建立 Ticket；實際範圍、branch、PR 與證據仍須在已核可 active Ticket 據實記錄。不得一邊開發一邊猜測未提供的 Provider seam。

## 整體完成

成果交付順序概述為 SP-01 → SP-02 → SP-03 → SP-04；不是 Consumer depends on Provider 的箭頭方向，SP-03／04 仍直接依賴 SP-01。不同子 PRD 的完整結案不必被當成下一個切片的開工門檻，但每條正式交付依賴都要有 main 證據；開發版試接依 workflow 另記。

例如 S02-A 真實全敗交付後，SP-03 可接入，而 SP-02 繼續其餘已核准切片；S03-A 真實合格候選交付後，SP-04 可接入，而 SP-03 繼續迭代／恢復。這些例子以切片包含必要安全處理、契約已凍結為前提，不保證任一 workload 必然全敗或通過。

整份子 PRD 結案仍須自己的全部切片、完整直接依賴與聯合驗收；產品完成須同一 main 通過 [ACCEPTANCE](../ACCEPTANCE.md)，不能只展示最短成功路徑。
