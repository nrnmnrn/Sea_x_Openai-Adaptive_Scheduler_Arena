# 實作 repository 的工作指引

本 repository 已進入比賽實作期間。開始任何工作先讀 [INDEXER.md](INDEXER.md)，只載入該情境指定的文件。

## 權威與邊界

- [PRD.md](PRD.md) 是產品需求權威。
- 已核可且完整的 `sub-PRDs/*.md` 是該完整功能的範圍與驗收權威。
- `docs/contracts/*.md` 是跨功能介面權威。
- GitHub parent issue 與 Ticket 只記錄認領、進度、連結、測試證據、blocker 與核可；它們不取代規格。
- 規格衝突或缺少足以開始的資訊時，停止受影響工作，依 [workflow.md](workflow.md) 記錄並請 main branch 負責人處理。

認領已核可範圍的人即為 Owner，每份子 PRD 保留唯一 parent issue。SP-01 已在執行，維持原單一 branch／Draft PR 完整交付；SP-02～04 依 [workflow.md](workflow.md) 採每張 Ticket 的真實切片 branch／PR。流程核准不等於產品、契約或整份規格已驗收。

## 執行原則

- 開始工作前，先理解使用者的目標、範圍、限制與完成標準；再檢查並選用與任務直接相關的 skill。依所選 skill 決定須讀取的文件、執行步驟與驗證方式。僅使用必要 skill，不得以 skill 取代或擴張使用者需求；若無合適 skill，依本文件及 repository 既有模式執行。
- 目前 branch 非 `main`，或本次已認領／承接任何子 PRD 或 Ticket 時，開始前必須完整讀 [workflow.md](workflow.md)。僅管理 `main` 且未承接子 PRD／Ticket 者不強制。
- 每次只主動處理一張已準備好的 Ticket；開始前讀完整子 PRD、Ticket、[workflow.md](workflow.md)、[依賴索引](sub-PRDs/DEPENDENCIES.md)、必要交付證據與最新 `main`。受阻後切換須先依 workflow 留下可恢復交接，原工作保持 Open。
- 依賴方向固定為「Consumer depends on Provider」。原型工作先讀[工作分類](docs/product/prototype-work-plan.md)與[接口討論表](docs/product/interface-discussion-board.md)，依 workflow 區分 A 獨立、B 邊做邊談、C 受影響部分先決定；開發版試接不等於正式交付，不以替身證明接通。
- SP-01 維持完整交付，不要求提前切片；任何涉及其責任、介面或驗收的實質變更，先取得該負責人確認及人類核可。
- 每項完成交付留下 commit、測試、AI review 與所需人類／`main` 證據；所有切片完成仍須完整子 PRD 驗收，才能關閉 parent issue。
- 同一 blocker 超過 15 分鐘，或完成兩次有證據的嘗試仍無法前進時，標示 Blocked 並回報；不要自行改寫需求或介面。

完整步驟與結案條件在 [workflow.md](workflow.md)。子 PRD 的撰寫與拆分規則在 [sub-prd-authoring.md](sub-prd-authoring.md)。

## 安全

使用個人憑證；不得把 API key、token、密碼、私鑰或私人通信放入 repository、issue、Ticket 或 prompt。新增依賴、資料 schema、CI/CD、authentication 或 authorization 變更前須取得人類核可；不得降低驗證或授權來通過測試。
