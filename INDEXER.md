# 交接包索引

每次先讀 [AGENTS.md](AGENTS.md) 與本檔，再依情境讀下表。`parent issue` 指一份子 PRD 的 GitHub 上層工作單；Ticket 是它底下可獨立驗證的一次工作。

| 情境 | 必讀文件 | 讀完必須回答 |
| --- | --- | --- |
| 判斷產品行為、範圍或總驗收 | [PRD.md](PRD.md)、[ACCEPTANCE.md](ACCEPTANCE.md) | 要交付什麼、由誰覆蓋、如何證明完成？ |
| 建立、修改或核可子 PRD | [sub-prd-authoring.md](sub-prd-authoring.md)、[模板](templates/sub-prd.md)、[文件權威 ADR](docs/adr/0001-document-authority.md)、[一子 PRD 一 branch ADR](docs/adr/0002-one-branch-per-sub-prd.md)、[依賴索引](sub-PRDs/DEPENDENCIES.md) | 這是完整功能嗎、直接依賴是什麼、Ticket 數量可核可嗎？ |
| 比賽當日認領子 PRD、建立工作單 | [workflow.md](workflow.md)、已核可子 PRD、[parent issue 模板](templates/parent-issue.md)、[Ticket 模板](templates/ticket.md) | 認領人、唯一 branch／Draft PR、parent issue 與 Ticket 如何建立？ |
| 比賽規則或簡報準備 | [COMPETITION.md](COMPETITION.md) | Coding 窗口、限制與當日待更新事項是什麼？ |
| 開始或續做一張 Ticket | [workflow.md](workflow.md)、完整子 PRD、目前 Ticket、parent issue、直接依賴的 `main` 證據 | 此次唯一工作、開始條件、驗收與下一步是什麼？ |
| 修改或使用跨功能介面 | 對應的 `docs/contracts/*.md`、相關子 PRD、[PRD.md](PRD.md) | 介面約定、相容範圍與整合證據是什麼？ |
| 從零建立環境、啟動 UI 或選擇 team/local backend | [後端契約](docs/contracts/backend-contract.md)、[Scheduling Arena 子 PRD](sub-PRDs/scheduling-arena.md) | Python／uv 版本、啟動參數、factory、來源標示及失敗規則是什麼？ |
| 準備子 PRD 審查、merge 或結案 | [workflow.md](workflow.md)、完整子 PRD、parent issue、[ACCEPTANCE.md](ACCEPTANCE.md) | 哪些測試、人工確認、合併授權與 `main` 證據仍缺少？ |
| 修改本包的治理文件或模板 | 本檔、[workflow.md](workflow.md)、兩份 [ADR](docs/adr/) | 是否維持單一權威、相對連結及賽前／比賽當日邊界？ |

若檔案不存在或文件之間衝突，不以 issue 或 Ticket 補寫規格；停止受影響工作，依 [文件權威 ADR](docs/adr/0001-document-authority.md) 處理。
