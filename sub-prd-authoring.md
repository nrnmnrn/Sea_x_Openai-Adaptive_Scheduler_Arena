# 子 PRD 撰寫與核可

子 PRD 是一項可獨立展示、測試及驗收的完整功能規格，不是單一技術元件或水平切割的待辦清單。使用 [模板](templates/sub-prd.md) 撰寫。產品行為以 [PRD.md](PRD.md) 為權威；子 PRD 只把其中一項完整功能具體化；跨功能介面以 `docs/contracts/` 為權威。

## 撰寫前的完整性檢查

一份可核可的子 PRD 必須明確寫出：交付結果、範圍與不做範圍、PRD requirement coverage、直接依賴及理由、Consumer／Provider 方向、驗收方式、未解問題與 Ticket 數量閘門。若交付結果、驗收、直接依賴或其開始條件未知，該子 PRD 是 blocker，不能核可或開始實作。

直接依賴固定寫為「Consumer depends on Provider」；Consumer 是使用成果的一方，Provider 是提供成果的一方。子 PRD 是自身直接依賴和理由的權威；`sub-PRDs/DEPENDENCIES.md` 只作跨子 PRD 的靜態索引。

## Ticket 數量閘門

- **2 至 3 張：標準。** Ticket 必須是 vertical slice（能從輸入到可觀察結果的一小段完整功能），共同覆蓋子 PRD 的交付結果與驗收。
- **4 至 5 張：特別核准。** 撰寫者必須填寫模板中的「不拆分理由」與「main branch 負責人特別核准」欄位。未取得 main branch 負責人核准前不可開始或建立正式 Ticket。
- **超過 5 張：不得核准。** 必須把子 PRD 拆成更小的完整功能，或正式縮減其範圍後重新估算；不得用額外 branch、更多 Ticket 或口頭例外繞過上限。

## 賽前與比賽當日的狀態

賽前模板中的 Owner 是 `Unclaimed`，GitHub parent issue 是「待比賽當日建立」，不可預先指定人或建立正式 Ticket。比賽當日第一位認領已核可子 PRD 的人就是 Owner；他建立 parent issue 和 Ticket，並依 [工作流程](workflow.md) 把易變的執行狀態、branch、PR、測試證據及 blocker 記在 issue。

修正文句、相對連結或不改變已核可內容的說明可直接維護。凡改變交付結果、範圍、驗收、直接依賴或已核可 Ticket 數量的提案，須由 main branch 負責人核可後才成為新的執行基準。衝突處理依 [文件權威 ADR](docs/adr/0001-document-authority.md)。
