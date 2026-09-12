# 實作 repository 的工作指引

本資料夾複製到未來比賽實作 repository 後才用於開發。開始任何工作先讀 [INDEXER.md](INDEXER.md)，只載入該情境指定的文件。

## 權威與邊界

- [PRD.md](PRD.md) 是產品需求權威。
- 已核可且完整的 `sub-PRDs/*.md` 是該完整功能的範圍與驗收權威。
- `docs/contracts/*.md` 是跨功能介面權威。
- GitHub parent issue 與 Ticket 只記錄認領、進度、連結、測試證據、blocker 與核可；它們不取代規格。
- 規格衝突或缺少足以開始的資訊時，停止受影響工作，依 [workflow.md](workflow.md) 記錄並請 main branch 負責人處理。

此交接包仍待獨立驗收。賽前不指定 Owner、不建立 GitHub issue 或 Ticket，也不在此資料夾建立競賽程式碼。官方 coding window 開始後，認領已核可子 PRD 的人即為 Owner，並建立該功能唯一的 parent issue、branch、Draft PR 與必要 Ticket。

## 執行原則

- 開始工作前，先理解使用者的目標、範圍、限制與完成標準；再檢查並選用與任務直接相關的 skill。依所選 skill 決定須讀取的文件、執行步驟與驗證方式。僅使用必要 skill，不得以 skill 取代或擴張使用者需求；若無合適 skill，依本文件及 repository 既有模式執行。
- 目前 branch 非 `main`，或本次已認領／承接任何子 PRD 或 Ticket 時，開始前必須完整讀 [workflow.md](workflow.md)。僅管理 `main` 且未承接子 PRD／Ticket 者不強制。
- 每次子 PRD／Ticket session 只完成一張已準備好的 Ticket；開始檢查包含完整子 PRD、目前 Ticket、[workflow.md](workflow.md)、[依賴索引](sub-PRDs/DEPENDENCIES.md)的開始條件、直接 Provider 證據與最新 `main`。
- 依賴方向固定寫為「Consumer depends on Provider」：使用成果的一方依賴提供成果的一方。Contract 已核定時，下游可用子 PRD 指定的 deterministic adapter／fixture 平行準備；正式整合與 closeout 一律等 Provider 成果已 merge 並在 `main` 驗證。
- 一份子 PRD 對應一條 branch 和一個 Draft PR；每張完成的 Ticket 留下清楚 commit、測試與 AI review 證據。
- 子 PRD 全部 Ticket 完成後，還要做整體功能驗收、完整測試、Owner 自查、另一位成員確認、正式 PR merge 與 `main` 整合驗收，才能關閉 parent issue。
- 同一 blocker 超過 15 分鐘，或完成兩次有證據的嘗試仍無法前進時，標示 Blocked 並回報；不要自行改寫需求或介面。

完整步驟與結案條件在 [workflow.md](workflow.md)。子 PRD 的撰寫與拆分規則在 [sub-prd-authoring.md](sub-prd-authoring.md)。

## 安全

使用個人憑證；不得把 API key、token、密碼、私鑰或私人通信放入 repository、issue、Ticket 或 prompt。新增依賴、資料 schema、CI/CD、authentication 或 authorization 變更前須取得人類核可；不得降低驗證或授權來通過測試。
