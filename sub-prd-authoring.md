# 子 PRD 撰寫與核可

子 PRD 是一項可獨立展示、測試及驗收的完整功能規格，不是單一技術元件或水平切割的待辦清單。使用 [模板](templates/sub-prd.md) 撰寫。產品行為以 [PRD.md](PRD.md) 為權威；子 PRD 只把其中一項完整功能具體化；跨功能介面以 `docs/contracts/` 為權威。

## 撰寫前的完整性檢查

一份可完整核可的子 PRD 必須明確寫出：交付結果、範圍與不做範圍、PRD coverage、直接依賴及理由、Consumer／Provider 方向、驗收方式、未解問題與 Ticket 數量閘門。交付、驗收、依賴或開始條件未知時，受影響範圍不能核可或實作。一般局部開工須由人類明確核可該切片範圍、契約與驗收；原型工作另依 workflow 第 2.1 節的已核准 A／B 例外，並保留整份子 PRD 的未決狀態，不能自動視為完整核可。

直接依賴固定寫為「Consumer depends on Provider」；Consumer 是使用成果的一方，Provider 是提供成果的一方。子 PRD 是自身直接依賴和理由的權威；`sub-PRDs/DEPENDENCIES.md` 只作跨子 PRD 的靜態索引。

## 真實交付切片與 prototype 分類

SP-01 維持既有整份交付；SP-02～04 依 [workflow](workflow.md) 與 [ADR 0003](docs/adr/0003-real-slice-delivery.md)、[ADR 0004](docs/adr/0004-prototype-parallel-development.md) 設計切片與原型工作。每個交付需寫提供者、使用者、契約章節／版本、輸入到可觀察結果、驗證方式及上游交付 ID。開始、正式整合、Ticket 結案與完整功能結案分別描述；沒有真實依賴時，明列只能寫而尚不能驗證的部分，不以測試替身補足。

切片不得改變原完整功能責任。基礎能力／錯誤恢復若跨子 PRD 歸屬未定，先記入[待決清單](docs/product/adaptation-decisions.md)，取得核可後才調整契約及範圍。SP-01 相關實質變更須取得其負責人確認。切片應包含完成自身驗收所必需的安全錯誤處理，不能把不安全的半成品交給下游。

若採 prototype-first，為每個範圍標記 [prototype work plan](docs/product/prototype-work-plan.md) 的 A／B／C 與相關 interface issue ID（I01–I09 或後續已登錄 ID）。A／B 僅限已核可且有界的內部工作；開始前列出排除範圍與未驗證項。C 的未決行為、控制或安全僅阻擋受影響操作。discussion board 是協調紀錄，任何決定先更新並核可 PRD、子 PRD 或 contract 才能成為執行基準；安全的名稱／格式轉換可在語意不變時局部處理。

開發版試接與正式交付必須分列：前者記指定人類 integrator、Owner 許可、隔離 branch／worktree、真實未 merge 版本、實際輸入、保護措施與版本／錯誤證據；後者仍依 [workflow](workflow.md) 要求 `main`、正式驗收與 closeout。prototype milestone 只能聲明已完成的子集，不能聲明完整功能或產品完成。

## Ticket 數量閘門

- **2 至 3 張：標準。** Ticket 必須是 vertical slice（能從輸入到可觀察結果的一小段完整功能），共同覆蓋子 PRD 的交付結果與驗收。
- **4 至 5 張：特別核准。** 撰寫者必須填寫模板中的「不拆分理由」與「main branch 負責人特別核准」欄位。未取得 main branch 負責人核准前不可開始或建立正式 Ticket。
- **超過 5 張：不得核准。** 必須把子 PRD 拆成更小的完整功能，或正式縮減其範圍後重新估算；不得用額外 branch、更多 Ticket 或口頭例外繞過上限。

## 賽前與比賽當日的狀態

賽前模板中的 Owner 是 `Unclaimed`，GitHub parent issue 是「待比賽當日建立」，不可預先指定人或建立正式 Ticket。比賽當日第一位認領已核可子 PRD 的人就是 Owner；他建立 parent issue 和 Ticket，並依 [工作流程](workflow.md) 把易變的執行狀態、branch、PR、測試證據及 blocker 記在 issue。

修正文句、相對連結或不改變已核可內容的說明可直接維護。凡改變交付結果、範圍、驗收、直接依賴或已核可 Ticket 數量的提案，須由 main branch 負責人核可後才成為新的執行基準。衝突處理依 [文件權威 ADR](docs/adr/0001-document-authority.md)。
