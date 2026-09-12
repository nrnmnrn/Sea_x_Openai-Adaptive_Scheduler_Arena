# 真實切片流程修改交接與下一輪審查

> 歷史交接：以下記錄上一輪真實切片修訂。後續原型開工／試接已由 [ADR 0004](../adr/0004-prototype-parallel-development.md) 調整；本輪結果及審查入口見[原型修改交接](prototype-change-handoff.md)。下方「本次」「開始時」及檔案清單只描述上一輪，不代表目前工作樹來源。

## 本次結果與狀態

已落實使用者核准的流程方向：SP-01 保留完整開發與單一分支／合併請求；SP-02～04 可用真實功能切片各自交付。開工、切片正式整合／結案、整份子 PRD 結案分開；受阻後可留下可恢復交接再換已準備好的工作。不以測試替身作本次開工或整合證據。

**完成的是流程與交付文件修改，不是產品實作、全部契約凍結或全面開工核准。** 本次沒有 commit、建立 issue／Ticket、合併、推送或寫實作程式。下一 session 仍須獨立審查。

基準 HEAD：`7c47381614c5b829e7eb02abfb6a9e1385a78a60`。開始時 `git status --short` 為空；本次列出的文件變動均由此 session 建立。下一輪仍須檢查最新 HEAD 與實際差異；若之後有其他人的修改，不得全部歸給本次或覆蓋它們。

## 修改檔案與目的

| 檔案 | 修改內容 |
| --- | --- |
| [workflow](../../workflow.md)、[AGENTS](../../AGENTS.md) | 真實切片、SP-01 保留模式、三個門檻、受阻切換、人類 merge 與 main 證據。 |
| [INDEXER](../../INDEXER.md)、[README](../../README.md) | 新交付模式、契約／待決入口與必讀路由。 |
| [ADR 0001](../adr/0001-document-authority.md) | 更新實作時點描述，保留原主題權威。 |
| [ADR 0002](../adr/0002-one-branch-per-sub-prd.md)、[新增 ADR 0003](../adr/0003-real-slice-delivery.md) | 原決策對 SP-01 保留；SP-02～04 多切片分支規則及取捨。 |
| [撰寫規則](../../sub-prd-authoring.md)、[子 PRD 模板](../../templates/sub-prd.md)、[Ticket 模板](../../templates/ticket.md)、[parent 模板](../../templates/parent-issue.md) | 局部核可範圍、交付 ID、上游證據、分支／PR、結案記錄；保留 Ticket 數量閘門。 |
| [依賴索引](../../sub-PRDs/DEPENDENCIES.md) | S01-FULL 與 SP-02～04 切片依賴、真實驗證門檻。 |
| [SP-01](../../sub-PRDs/scheduling-arena.md) | 僅補執行狀態提示、S01-FULL 交接及待確認邊界；不改功能範圍與驗收、不重建認領。 |
| [SP-02](../../sub-PRDs/existing-skill-adaptation.md)、[SP-03](../../sub-PRDs/candidate-evaluation-loop.md)、[SP-04](../../sub-PRDs/skill-promotion-and-recovery.md) | 0.2-draft、真實上游 readiness、3 個切片的提供／使用者、契約與 blocker；保留完整產品要求。 |
| [backend 契約](../contracts/backend-contract.md) | 增加交接／缺口入口，保留既有公開方法與資料，不擅改 SP-01 介面。 |
| [新增 adaptation 契約](../contracts/adaptation-contract.md) | H1～H8 交接目錄、既有規則與凍結檢查；明示尚非完整已凍結 schema。 |
| [新增待決清單](adaptation-decisions.md) | D1～D9 精確缺口、選項、影響、受阻工作與人類核可方式。 |
| [PRD](../../PRD.md)、[ACCEPTANCE](../../ACCEPTANCE.md) | 實作時點／流程引用、切片與完整验收證據分層；未改 gate、數值、產品責任或降低驗收。 |
| [原調查報告](sub-prd-contract-review.md) | 加歷史狀態提示；修正本 repo 對應來源連結；未隨附舊文件保留文字路徑，不冒稱現行來源。原設計建議仍未核准。 |
| 本檔 | 修改說明、檢查結果、已知限制及下輪可複製 prompt。 |

## 已核准與仍待決

已核准：交付流程方向及 SP-01 保留邊界。沒有藉此核准調查報告所有提案。

待人類決定：D1 trigger、D2 baseline／重放、D3 null／失敗分類、D4 共用能力責任、D5 外部 adapter／retry checkpoint、D6 Snapshot 不變範圍與 Hybrid 真實驗收前提、D7 暫停時 workload 操作、D8 修改回傳／playing 邊界、D9 evidence／promotion schema。

尤其 D4 未定，所以共同評估與部分底層控制的提供者尚不能唯一確定。契約表刻意標明缺口，不自行把新責任交給正在開發 SP-01 的組員。這些未解事項阻擋相應切片的核准與真實驗證，詳見各子 PRD 表格；不是宣稱四份已可獨立完成。

SP-01 的實際 Owner／parent issue／核可版本連結需現有負責人提供。本次只採信使用者「已有人完整開發」的事實，不存取外部 tracker、不猜人名或核可證據。

## 本次基本檢查

- `git status --short`：開始為乾淨工作目錄；最後僅文件變動。
- `git diff --check`：通過。
- 變動 Markdown 本機連結存在性掃描：最終 23 份文件、209 個本機連結，無不存在目標、無尾端空白，只有 Markdown 變動；HEAD 未變。此掃描不證明每個段落語意或瀏覽器渲染正確。
- 跨文件搜尋：舊單分支／fixture 開始／受阻只能續同 Ticket 規則已在執行文件遷移；ADR 0002 與原調查以保留／歷史狀態說明。
- 產品與 SP-01 範圍檢查：PRD 僅修改文件定位；SP-01 僅修改基本資料說明與介面／直接依賴章節，保留必要行為、驗收及 Ticket 設計。
- 使用 cavecrew 精簡唯讀調查與差異檢查；writing-for-agents 使流程集中 workflow、入口文件引用；context-mode 用於跨文件分析。這些基本檢查不代替下輪獨立審查。
- 本輪 cavecrew 唯讀差異檢查提出 ADR 0002 兩處泛稱單分支可能誤讀；已將正文明確限縮為 SP-01，保留 SP-02～04 指向 ADR 0003。其機械檢查未發現斷鏈或交付／決策 ID 不一致；不代表已獨立核准產品決策。
- 未執行 pytest、Ruff、型別檢查、build；本次無程式修改。未發現 repository pre-commit 設定，因此未執行 pre-commit。

## 初學者說明

這次改的是團隊交作業的方式，不是把產品做完。正在製作排程基礎的組員照原計畫完成整份；其他組員把自己的功能分成能真正操作、能檢查的小段，完成一段就能交給下一位接續。

這像餐廳先把能使用的料理台交付，再逐道完成餐點；不必等全部菜色研究完才讓下一位工作，但也不能用一張餐點照片當成真正出餐。現在規則已分清「可以開始寫」與「真正接好、驗收完成」，避免把尚不能執行的程式誤報為完成。

仍不知道的是部分比較標準、出錯後如何接續，以及共用能力由誰提供。這些須由使用者決定，涉及排程基礎的改動也須和正在開發的組員確認。下一輪先檢查本次文件是否一致，再整理必要決策；在那之前，不能安全宣稱所有功能都已具備完整平行開發條件。

## 下一個 session 的 prompt

```text
請獨立、唯讀審查上一個 session 的規格與流程修改。先不改檔案、不寫程式、不 commit。

先遵循適用 AGENTS.md、INDEXER.md 與必讀文件，再讀 docs/product/real-slice-change-handoff.md。
基準 HEAD 為 7c47381614c5b829e7eb02abfb6a9e1385a78a60，但以目前工作目錄為準。
先看 git status、最新 HEAD、未提交差異及交接清單；若已有人 commit 或新增變動，分清來源，不只看 git diff 或相信交接描述。

已核准方向：SP-01 已有人完整開發，保留原 branch／PR、責任與完整驗收；SP-02～04 可用真實功能切片各自 branch／PR 交付。不用測試替身作 readiness 證據。正式整合等待所需上游交付 merge 並在 main 驗證；切片自身也須人類授權 merge／main 驗證才能結案；完整子 PRD 驗收保留。受阻可交接後切換，但原 Ticket 保持 Open。
未核准：D1～D9 的產品數值、schema、責任轉移與驗收變動。不要替使用者決定。

檢查：
1. AGENTS、workflow、ADR、撰寫規則、模板、依賴索引、四份子 PRD 是否一致；三個門檻是否可操作。
2. SP-01 責任／介面／驗收有無擅改，所有需要其負責人確認的地方是否明確。
3. 每項必要交接是否有提供者、使用者、契約位置、版本、驗證方式；未定提供者是否準確標為 blocker，而非假裝已完成。
4. S01-FULL 與 S02～04 切片依賴是否完整，有無循環、隱藏依賴或不安全的早期切片；後續恢復工作是否被用來省略早期必要錯誤處理。
5. 是否把歷史調查提案當現行規格、把流程核准当全部產品核准，或自行填入預設值。
6. 是否降低原驗收；尤其 gate、五版上限、錯誤恢復、Snapshot 隔離、Hybrid 真實通過前提與完整展示。
7. 所有變動與新增文件的相對連結、引用、交付 ID、待決 ID 是否正確。保留固定測試資料不等於允許替身整合。

執行 git diff --check；本次文件審查不執行程式測試、lint 或 build。
按嚴重程度列問題，附精確檔案／行號、依據、影響與最小修正建議；沒有發現就明說。
分別判定四份子 PRD 哪些工作可開始、哪些受阻；列使用者決策與 SP-01 負責人確認事項。
給「通過／附條件通過／不通過」結論及未驗證範圍，用初學者能理解的話說明現況。不要為提出建議擴大修改。
```
