# 交接包索引

每次先讀 [AGENTS.md](AGENTS.md) 與本檔，再依情境讀下表。`parent issue` 指一份子 PRD 的 GitHub 上層工作單；Ticket 是它底下可獨立驗證的一次工作。

| 情境 | 必讀文件 | 讀完必須回答 |
| --- | --- | --- |
| 判斷產品行為、範圍或總驗收 | [PRD.md](PRD.md)、[ACCEPTANCE.md](ACCEPTANCE.md) | 要交付什麼、由誰覆蓋、如何證明完成？ |
| 建立、修改或核可子 PRD | [sub-prd-authoring.md](sub-prd-authoring.md)、[模板](templates/sub-prd.md)、[文件權威 ADR](docs/adr/0001-document-authority.md)、[交付模式 ADR](docs/adr/0003-real-slice-delivery.md)、[依賴索引](sub-PRDs/DEPENDENCIES.md) | 完整功能、切片交付、直接依賴、核可範圍與 Ticket 數量是否明確？ |
| 比賽當日認領子 PRD、建立工作單 | [workflow.md](workflow.md)、已核可子 PRD、[parent issue 模板](templates/parent-issue.md)、[Ticket 模板](templates/ticket.md) | SP-01 保留模式或 SP-02～04 切片模式、Owner、parent issue、branch／PR 如何記錄？ |
| 比賽規則或簡報準備 | [COMPETITION.md](COMPETITION.md) | Coding 窗口、限制與當日待更新事項是什麼？ |
| 開始、續做或受阻後切換 Ticket | [workflow.md](workflow.md)、完整子 PRD、目前 Ticket、parent issue、直接交付證據 | 本次主動工作、未完成工作交接、開工／試接／正式交付／完整結案與下一步是什麼？ |
| 修改或使用跨功能介面 | 對應的 `docs/contracts/*.md`、相關子 PRD、[PRD.md](PRD.md) | 介面約定、相容範圍與整合證據是什麼？ |
| 從零建立環境、啟動 UI 或選擇 team/local backend | [後端契約](docs/contracts/backend-contract.md)、[Scheduling Arena 子 PRD](sub-PRDs/scheduling-arena.md) | Python／uv 版本、啟動參數、factory、來源標示及失敗規則是什麼？ |
| 準備子 PRD 審查、merge 或結案 | [workflow.md](workflow.md)、完整子 PRD、parent issue、[ACCEPTANCE.md](ACCEPTANCE.md) | 哪些測試、人工確認、合併授權與 `main` 證據仍缺少？ |
| 修改治理文件或模板 | 本檔、[workflow.md](workflow.md)、[ADR](docs/adr/) 中 0001～0004 | 是否維持單一權威、相對連結與 SP-01 保留邊界？ |
| 原型異步開發、接口討論或開發版試接 | [workflow](workflow.md)、[ADR 0004](docs/adr/0004-prototype-parallel-development.md)、[工作分類](docs/product/prototype-work-plan.md)、[接口討論表](docs/product/interface-discussion-board.md)、相關子 PRD | 哪部分 A／B 可先做、哪部分 C 需決策；真實試接與正式交付證據是否分開？ |
| 核對 adaptation 交接或解除開工 blocker | [交接契約](docs/contracts/adaptation-contract.md)、[待決清單](docs/product/adaptation-decisions.md)、相關子 PRD | 哪個交付、誰提供／使用、哪些決策與真實驗證尚缺？ |

若檔案不存在或文件之間衝突，不以 issue 或 Ticket 補寫規格；停止受影響工作，依 [文件權威 ADR](docs/adr/0001-document-authority.md) 處理。
