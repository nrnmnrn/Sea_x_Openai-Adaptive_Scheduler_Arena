# 原型異步開發修改結果與審查交接

## 結果

已依使用者授權，將「先凍結整份相關契約再開工」調整為三類原型工作：A 可獨立、B 內部先做並同步討論接口、C 僅受影響部分先決定。新增真實開發版試接，保留正式 main 交付與完整驗收。SP-01 原完整開發安排、產品行為、Ticket 數量與合併授權未改。

入口：[各組工作分類](prototype-work-plan.md)、[團隊可填寫接口討論表](interface-discussion-board.md)、[正式流程](../../workflow.md)。使用 writing-for-agents 將流程集中於 workflow，其他文件引用；cavecrew 用於唯讀定位、分工修改與獨立審查。

## 本輪修改檔案

- 流程／模板：[workflow](../../workflow.md)、[authoring](../../sub-prd-authoring.md)、[Ticket](../../templates/ticket.md)、[parent issue](../../templates/parent-issue.md)、[子 PRD 模板](../../templates/sub-prd.md)。
- 入口／權威：[AGENTS](../../AGENTS.md)、[INDEXER](../../INDEXER.md)、[README](../../README.md)、[PRD 文件定位](../../PRD.md)、[ACCEPTANCE 證據規則](../../ACCEPTANCE.md)、[ADR 0001](../adr/0001-document-authority.md)、[ADR 0003](../adr/0003-real-slice-delivery.md)。
- 交付：[依賴索引](../../sub-PRDs/DEPENDENCIES.md)、[SP-01 交接說明](../../sub-PRDs/scheduling-arena.md)、[SP-02](../../sub-PRDs/existing-skill-adaptation.md)、[SP-03](../../sub-PRDs/candidate-evaluation-loop.md)、[SP-04](../../sub-PRDs/skill-promotion-and-recovery.md)。
- 協調／歷史：[adaptation 契約狀態](../contracts/adaptation-contract.md)、[待決清單](adaptation-decisions.md)、[歷史調查標示](sub-prd-contract-review.md)、[上一輪交接標示](real-slice-change-handoff.md)。
- 新增：[ADR 0004](../adr/0004-prototype-parallel-development.md)、[工作分類](prototype-work-plan.md)、[接口討論表](interface-discussion-board.md)、本交接文件。

共 25 份本輪觸及文件；開始時已有 19 份 tracked 修改、4 份 untracked，全部保留，不能把 git 相對 HEAD 的全部差異視為本輪新增。本輪未修改 backend 的公開方法／型別，亦未修改 ADR 0002。

上一輪驗證兩項發現已處理：SP-02 的 S02-A 明確承接既有評估完整恢復、S02-B 承接控制恢復、S02-C 呈現操作，同步 D5／H7 及索引，維持三張 Ticket；依賴箭頭改稱成果交付順序，保留 SP-03／04 直接依賴 SP-01。

## 檢查與限制

- `git diff --check`：通過。純文件修改，未執行 Pytest、Ruff、型別檢查或 build。
- 檔案／連結掃描：33 份 Markdown、286 個本機連結目標均存在；未驗證外部連結或 Markdown 錨點語意。
- 獨立唯讀審查指出部分切片漏列共同契約 D 項，已補齊。對「每份子 PRD 重複分類矩陣」的建議，採集中工作表＋子 PRD 引用及 Ticket 記錄，以避免兩套範圍；每列已對應交付 ID、A／B／C、接口及驗證。受影響 D 項包含上游條件，不要求下游重做上游功能。
- 未找到根目錄 pre-commit 設定，未執行 pre-commit。
- 沒有 commit、staging、push、merge、建立工作單或實作程式；沒有驗證外部服務、組員分支或真實接通。
- D1～D9 仍待決；I01～I09 全為待討論，人名、時限、版本與核可證據待團隊填寫。工作表分類不是實作已完成的證據。
- 本輪依目前文件作分類，不假定第一組已實作哪些未展示能力。若實際 A／B 需要待決答案，只將受影響部分改列 C。

## 下一步，白話說明

這次把工作分成「現在能做」「一邊做、一邊確認接法」「沒有答案就不能安全做」三類，並給大家一張共用討論表。它像四個人一起組裝攤位：可以同時做桌面與燈箱，但要先確認供電由誰負責；插頭形狀不同可以轉接，電壓不明不能直接插。

這避免大家為了等待所有細節而停工，也避免各自猜一套答案，最後接不起來。第一組繼續原安排，其他組按表先做內部部分；拿到真實開發版本就可依流程試接，但試接成功不是正式驗收完成。

目前還不知道共用評估由誰提供、Hybrid 真實驗收材料從哪裡來，以及部分錯誤恢復與資料關聯規則。因此不能自行執行依賴這些答案的操作，也不能宣告完整功能通過。

接下來請使用者指定整合協調人；各組 Owner 填接口表的實作位置、參與者及最晚需要答案時間。優先討論 I03／I09，再處理即將執行的控制與安全接點。Owner 選工作表 A／B 的限定範圍記入工作單即可開始，不用等整張討論表填完；超出範圍或產品答案仍需人類核准。

## 下一 session 唯讀審查 prompt

```text
請先遵循 AGENTS.md、INDEXER.md 與適用 skills，唯讀審查目前原型異步開發文件修改，不修改、不 commit、不核准產品規則。

先讀 docs/product/prototype-change-handoff.md、workflow.md、docs/adr/0004-prototype-parallel-development.md、docs/product/prototype-work-plan.md、docs/product/interface-discussion-board.md，再依索引核對子 PRD、契約、待決清單及模板。

目前未提交內容包含前一輪真實切片修訂與本輪原型例外；先核對 git status 與差異，不把所有內容當成本輪。檢查：
1. A／B 明列內部工作是否能不等整份契約凍結開始；C 是否只停受影響部分，沒有自訂產品預設。
2. SP-01 原功能、責任及驗收是否保留；開發版試接是否不要求其提前切片／merge。
3. 真實開發版本試接、正式 main 交付與完整結案是否分開，安全與合併授權是否完整。
4. 四組分類與 I01～I09 表單是否涵蓋 H1～H8、D1～D9；提供／使用者、待決責任與驗證是否清楚，表單不冒充契約。
5. SP-02 S02-A／B／C 的完整恢復、D5／H7 及索引是否一致；是否保留三張 Ticket。
6. 入口、ADR、模板、歷史標示是否仍有舊門檻衝突。

純文件執行 git diff --check，不跑 Pytest／Ruff／build。以嚴重度、檔案行號、原因與最小修法報告；另用白話列出現在能開始、仍需人類決定與仍未實際驗證的事情。不要把原型流程核准誤認成產品或各功能全部通過。
```
