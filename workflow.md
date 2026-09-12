# 子 PRD 工作流程

本流程用於官方 coding window 已開始的實作 repository。產品、完整功能、介面與執行紀錄的權威依 [ADR 0001](docs/adr/0001-document-authority.md) 分工。

## 1. 交付模式與認領

- 每份子 PRD 保留唯一 Owner 與 parent issue，負責完整功能。認領、核可者、日期、規格版本與連結須據實記錄，不由 AI 補造。
- **承接入口**：SP-02～04 的執行者先到被指派子 PRD 的 parent issue 確認 Owner、整體狀態與 Ticket 索引，再進入被指派且已核可的 active Ticket。parent issue 用於整體追蹤，不直接授權整份實作；active Ticket 才記錄本次實際範圍、branch／PR、待決事項與驗證證據。不得自行挑選或開始尚未建立、未被指派或未核可的下一張 Ticket。
- **SP-01 保留完整交付模式**：已在執行，沿用既有單一 branch／Draft PR、Ticket 結構與整份合併流程，不要求提前交付切片。使用者確認正在開發，不代表缺少的核可或執行連結可視為已有證據。
- **SP-02～04 採真實切片模式**：每張核可 Ticket 交付可獨立驗證的真實功能切片，由最新 `main` 建立自己的短期 branch／Draft PR；一條切片 branch 只對應一張 Ticket。parent issue 索引全部 branch／PR。詳見 [ADR 0003](docs/adr/0003-real-slice-delivery.md)。
- Owner 依核可子 PRD 草擬 Ticket（可用 `$to-tickets`），遵循 [模板](templates/ticket.md)。2–3 張為標準；4–5 張須 main branch 負責人特別核可；超過 5 張先拆分或縮減子 PRD。切片分支不能繞過數量閘門。
- 一般草稿經人類核可後才可發佈正式 Ticket／實作；原型 A／B 的明列內部範圍適用第 2.1 節。未決事項只阻擋受影響範圍；可開始範圍必須在子 PRD 與 Ticket 明列並經人類核可，不得把局部核可寫成整份已核可。
- 不代改 SP-01 現有 branch、PR 或工作單。涉及其責任、介面或驗收的實質變更，先由 SP-01 負責人確認影響，再由 main branch 負責人核可權威文件。

## 2. 開工、開發版試接、正式交付與完整結案

依賴方向固定為「Consumer depends on Provider」。[依賴索引](sub-PRDs/DEPENDENCIES.md) 指向子 PRD 的交付成果；[交接契約](docs/contracts/adaptation-contract.md) 列出必要交接、驗證要求與未決缺口。

| 門檻 | 必要條件 |
| --- | --- |
| 開工 | 範圍、輸入與驗收已核准，且影響本工作的待決事項已解除。一般工作所需的真實 Provider 必須可用；第 2.1 節的核可 prototype 例外另行適用。 |
| 開發版試接 | 僅可依第 2.2 節，以真實指定版本（可尚未 merge）進行受控試接；試接證據不是正式交付、`main` 證據或 Ticket closeout。 |
| 正式交付 | 本切片實際需要的全部上游交付已 merge 並在 `main` 驗證；以真實依賴通過全部 Ticket 驗收、完整測試及審查。SP-02～04 本切片亦需人類授權 merge 並在 `main` 驗證才可結案。SP-01 內部 Ticket 保留第 3 節的整份合併前結案方式。 |
| 完整結案 | 全部 Ticket 完成、直接依賴全部交付、完整功能與 `main` 聯合驗收、Owner 自查、另一位成員確認及人類整合核可均完成。 |

本次不使用 deterministic adapter、Mock 或固定 passed／all-failed 回應替代上游作為 readiness 或整合證據。固定 Jobs、邊界值、可重現測試資料及真實 adapter 的受控故障測試仍須保留；不是刪除測試，也不取消產品明示的 local／Mock 模式。

SP-01 對下游的正式交付只有「整份完成、merge 並在 `main` 驗證」的交付點，不能假定提前 merge。SP-02～04 可按已核准交付逐片整合，不必等上游子 PRD 的無關切片。不得縮小依賴清單來隱藏實際呼叫、共享狀態或必要恢復能力。

### 2.1 Prototype-first 開工例外

本次使用者已核准工作分類表所列 A／B 內部範圍採以下例外；在表列限制內記錄後即可開始，不另等整份切片契約核准。超出表列範圍須另取得人類核可。

已核可為 **A（獨立）**或 **B（可平行的內部邏輯）** 的有限範圍，可在完整 contract 尚未凍結、上游尚未交付或尚未有 `main` 證據時開工。子 PRD 引用工作分類；Owner 必須在開始前於 Ticket 據實記錄，parent issue 索引該紀錄：範圍類別、相關 interface issue ID、排除範圍，以及尚未驗證項；不必等待所有 **D（待決）** 項目解除。

此例外不授權補造預設值、新資料 schema 或責任轉移。**C（受影響）** 類若涉及未決行為、控制或安全，僅停止受影響的操作，不擴大為無關工作停擺。分類與 interface issue 的協調格式以 [prototype work plan](docs/product/prototype-work-plan.md) 及 [interface discussion board](docs/product/interface-discussion-board.md) 為準；它們不是規格權威，決定必須先寫入並核可對應的 PRD、子 PRD 或 contract 後才能使用。

名稱或格式的安全在地調整，只要語意維持，可在本地完成並留下對照證據；語意衝突則只停止該介面接縫，依第 4 節處理。

### 2.2 開發版試接

開發版試接僅為驗證 prototype 的整合假設。指定的人類 integrator 取得各 Owner 允許後，於隔離 integration branch／worktree 使用已識別的真實指定版本（可尚未 merge）與實際輸入；記錄版本、保護措施、結果及錯誤證據。試接前先確認所執行路徑的產品語意、控制歸屬與安全條件；未決 C 操作仍不得執行。優先適配 SP-01 已有介面，不改其原分支或增加提前交付責任。不得自行補上 integrator 人名。試接不構成正式交付、`main` 驗證、Ticket closeout 或合併授權，仍不得以假 upstream 取代真實輸入。

## 3. 執行與切片合併

1. 由被指派的 parent issue 進入被指派且已核可的 active Ticket；讀完整子 PRD、Ticket、parent issue、本流程、最新 `main` 與直接交付證據，核對契約版本、未決事項及既有變動。frontier 是開始條件已滿足的工作，不由 Ticket 編號或執行者自行選擇決定。
2. 一次只主動實作一張 Ticket，同一檔案集只有一位寫入者。滿足第 2 節才執行 `$implement`；prototype 依第 2.1 節可做有界內部工作，尚無真實依賴的驗證標為待整合，不宣告完成。
3. 完成 Ticket 驗收、相關檢查、完整 repository 測試套件與 AI `/code-review`，處理必要發現。程式變更依 AGENTS 執行 lint／format 與適用型別檢查；純文件變更只做文件檢查及 `git diff --check`，不執行程式測試。AI review 不取代人類核可。
4. 經允許建立可辨識 Ticket commit。**SP-02～04**：另一位成員確認切片與真實依賴證據，main branch 負責人審查契約相容性、範圍及整合條件；取得人類授權後 merge，再在 `main` 驗證切片。切片須不破壞既有功能，不將尚未完成路徑暴露為正式可用功能。
5. **SP-01**：內部 Ticket 驗收、完整檢查、AI review 及 commit 完成可結案；仍在原分支，內部結案不構成對下游交付。其 PR 等整份功能依第 5 節驗收後才 merge。
6. 滿足相應結案門檻才執行 `$task-closeout`，核對 tracker、commit、PR、測試、`main` 證據與限制；不另建重複 commit。再以 `$handoff` 指向下一張可開始 Ticket 或整體驗收。prototype milestone 只代表其已核可子集，不代表產品完成。

若使用者要求不 commit，保留變動與檢查結果，不宣告 Ticket closeout 或交付可用。工具／skill 不可用時，按相同文件步驟留下證據，不因工具名稱省略關卡。

## 4. 阻塞、切換與變更

同一技術問題超過 15 分鐘，或兩次有證據的嘗試仍無法前進，標記受影響 Ticket `Blocked` 且保持 Open，記錄症狀、嘗試、證據、所需決定及恢復條件，通知 main branch 負責人。parent issue 列明受阻範圍；無關且已核准的工作可繼續。

文件矛盾、題意不清或介面不一致，立即停止受影響工作，不等待時間門檻；介面衝突只停止受影響接縫與操作：

```text
BLOCKED
子 PRD／Ticket：<連結>
文件與段落：<路徑／段落>
解讀 A／B 或缺少資訊：<內容>
影響：<停止的工作、交付、驗收>
需要決定：<問題與人類決策者>
恢復條件：<權威文件核准與必要證據>
```

main branch 負責人依證據作人類決定，並與 Owner 在現場檢查相關狀態。先更新並核可權威文件，再更新紀錄、重驗開始條件；若決定不改規格，至少把決定記入 parent issue。產品規則、責任與驗收變更不能只寫在 Ticket。

受阻後可轉做另一張已核准且可開始的 Ticket：先留下可恢復交接（branch、變動、已驗證／未驗證項、blocker、下一步），原 Ticket 保持 Open，不執行 closeout。SP-02～04 隔離切片工作樹／分支，避免攜帶未提交變動；SP-01 仍在原分支，只有能安全隔離且不打亂既有責任時才切換。每位執行者同時只主動處理一張，不自動擴大工作量；交接列出所有受阻工作，不能遺忘舊 Ticket。

新增 Ticket 仍遵守數量閘門與核可。改動已交付契約前分析所有使用者，取得受影響 Owner 確認與人類核可，更新契約、子 PRD、索引及驗證案例。

## 5. 子 PRD 與產品完成

1. 全部 Ticket 完成後，Owner 驗收完整功能、完整相關測試、最後 AI review 與自查，不只檢查工作單數量。
2. 另一位成員確認完整功能、全部直接交付與聯合證據；main branch 負責人確認範圍、架構及依賴。
3. SP-01 經人類授權將整份 Draft PR 正式 merge，再於 `main` 整合驗收。SP-02～04 核對所有切片已 merge；若整體驗收需修正，依核可工作單流程交付，不以驗收名義加入未審查程式。
4. 在同一 `main` 驗證完整子 PRD，記錄版本與證據後才關閉 parent issue。分段 merge 不代替完整驗收。
5. 產品完成仍須全部 [ACCEPTANCE.md](ACCEPTANCE.md) 項目、90 秒短展示與 progression run 通過；未決契約與已知失敗不能標為通過。
