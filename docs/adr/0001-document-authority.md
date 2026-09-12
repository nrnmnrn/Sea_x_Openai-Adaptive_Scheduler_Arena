# ADR 0001：文件權威

> Status: accepted

## 決策

交接包內的權威依序按主題分工，而不是讓任何單一工作單同時承擔規格與進度：

| 主題 | 唯一權威 |
| --- | --- |
| 產品需求、行為、範圍與總體完成條件 | `PRD.md` |
| 一項完整功能的範圍、直接依賴、驗收與 Ticket 結構 | 已核可且完整的 `sub-PRDs/*.md` |
| 跨功能輸入、輸出與呼叫約定 | `docs/contracts/*.md` |
| 總 PRD requirement coverage 與驗收證據對照 | `ACCEPTANCE.md` |
| 認領、Owner、branch、PR、Ticket 狀態、測試證據、blocker 與核可連結 | GitHub parent issue 與 Ticket |

GitHub issue 與 Ticket 是易變執行紀錄，不能複製、放寬或覆蓋完整規格。依賴方向使用「Consumer depends on Provider」；子 PRD 記自身理由，集中依賴檔只作索引。

## 衝突處理

文件衝突、缺少規格或 interface contract 不一致時，停止依賴該答案的實作與操作；無關 A／B 原型工作依 [workflow](../../workflow.md) 繼續。單純名稱／包裝且語意不變的局部適配依 workflow 記錄，不視為整組 blocker。先依上表找對應權威；若仍無法唯一判斷，由 main branch 負責人作人類決定並更新權威文件，之後再更新 issue 的執行狀態。不得以 Ticket 的文字自行創造產品決策。

## 後果

規格可完整帶入實作 repository，而進度資訊留在 GitHub。目前 repository 已進入比賽實作；開始開發不等於規格已獨立驗收，未核准內容仍不能作為執行基準。交付模式由 [ADR 0003](0003-real-slice-delivery.md) 及原型開工／試接例外 [ADR 0004](0004-prototype-parallel-development.md) 調整，不改變本文件的主題權威。
