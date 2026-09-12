# GitHub Ticket 模板

> 僅於比賽期間，由子 PRD Owner 依明確核可的完整或局部範圍建立。Ticket 只記一次工作與執行證據，不改寫產品或功能規格；局部核可須有證據，不推定整份核可。

## 基本資料

- 所屬 parent issue：[連結]
- 所屬子 PRD：[相對路徑與版本]
- 交付模式／交付 ID：[SP-01 整份內部 Ticket，或 SP-02～04 真實切片及核可 ID]
- Branch／Draft PR：[SP-01 沿用原 branch／PR；其他填本 Ticket 專屬 branch／PR]
- 核可範圍與契約版本：[人類核可連結，不從流程核准推定產品核准]
- Prototype 類別／interface issue：[A 獨立／B 內部邏輯／C 受影響，或 `Not applicable`；I01–I09 或已登錄 ID；討論狀態與相關 H 交接／D 決策 ID]
- 排除範圍與未驗證項：[prototype 開工前必填；否則 `Not applicable`]

## 開始條件與依賴 frontier

- 工作順序與開始條件：[直接依賴／前一張 Ticket 證據／最新 `main` 證據]
- 直接依賴：[Consumer depends on Provider；子 PRD 指定的理由]
- Provider readiness 證據：[實際需要的交付 ID、契約位置、真實成果；尚無法執行或驗證的部分明列，不以替身補足]
- 正式整合與 `$task-closeout` 條件：[所需上游交付已 merge 並在 `main` 驗證；SP-01 上游指整份交付。SP-02～04 本切片亦需人類授權 merge 及 main 驗證；SP-01 內部 Ticket 依 workflow 保留模式]
- 未決事項：[決策 ID、受阻範圍、解除條件；未決不得自行補預設值]
- 開發版試接（如適用）：[指定人類 integrator、Owner 許可、隔離 branch／worktree、真實未 merge Provider 版本、實際輸入、保護措施、版本／錯誤證據；不是正式交付或 closeout]

## 這次工作

[一個 vertical slice：描述本次從輸入到可觀察結果要完成什麼。]

## 不做事項

[明確列出不在本 Ticket 的工作。]

## 驗收與完整驗證

- [ ] [可觀察的驗收條件]
- [ ] 程式變更執行完整 repository 測試套件 `uv run pytest` 及適用 lint／format／型別檢查；純文件變更記錄 `git diff --check`，不執行程式測試。
- [ ] [其他相關測試、人工檢查或驗證方式與通過證據]
- [ ] AI `/code-review` 已完成；必要發現已處理，並記錄連結或摘要。

## 完成紀錄

- 實作 commit：[連結]
- 驗收證據：[連結或摘要]
- 完整驗證證據：[`uv run pytest` 結果、其他命令／人工檢查及連結或摘要]
- AI review 證據：[連結或摘要；必要發現的處理結果]
- 切片合併證據：[SP-02～04：另一位成員確認、人類授權、PR merge、main 版本及驗證；SP-01：內部 Ticket，尚非對下游交付]
- Provider／試接與正式證據：[真實 Provider 版本與試接結果；另列正式 `main` 版本與驗收證據。未試接則寫 `Not applicable`]
- `$task-closeout` 結果：[`Not run — remains Open/Blocked`，直到真正完成；完成後填入完成確認、狀態／證據一致性檢查及下一步]
- Tracker 狀態：[`Open`／`Closed`；`Blocked` 時必為 `Open`；若 `Closed`，填入關閉時間或連結]
- blocker／限制／handoff：[症狀、已嘗試事項、證據、所需決定與交接資訊；無則 `None`]
- 下一步：[下一張可開始的 Ticket、待解除 blocker，或交由 parent issue 的整體完成關卡]

只有 [workflow.md](../workflow.md) 的正式交付門檻所需驗收、完整驗證、AI review、commit、合併／main 證據與 `$task-closeout` 完成且一致時，才可設為 `Closed`。試接或 prototype milestone 不可作為 closeout 證據。受阻切換須留下可恢復交接，原 Ticket 保持 Open。Ticket 關閉不表示完整子 PRD 已完成。
