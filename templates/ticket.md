# GitHub Ticket 模板

> 僅於比賽當日，由已認領子 PRD 的 Owner 依核可子 PRD 建立。Ticket 只記一次工作與執行證據，不改寫產品或功能規格。

## 基本資料

- 所屬 parent issue：[連結]
- 所屬子 PRD：[相對路徑與版本]

## 開始條件與依賴 frontier

- 工作順序與開始條件：[直接依賴／前一張 Ticket 證據／最新 `main` 證據]
- 直接依賴：[Consumer depends on Provider；子 PRD 指定的理由]
- Provider readiness 證據：[Provider 已 merge 並在 `main` 驗證，或已核定 contract 與子 PRD 指定的 deterministic adapter／fixture]
- 正式整合與 `$task-closeout` 條件：[所有直接 Provider 已 merge 並在 `main` 驗證；未滿足時不得正式整合或 closeout。已核定 contract 與子 PRD 指定的 deterministic adapter／fixture 仍可用於平行準備。]

## 這次工作

[一個 vertical slice：描述本次從輸入到可觀察結果要完成什麼。]

## 不做事項

[明確列出不在本 Ticket 的工作。]

## 驗收與完整驗證

- [ ] [可觀察的驗收條件]
- [ ] 完整 repository 測試套件：`uv run pytest`，並記錄通過結果。
- [ ] [其他相關測試、人工檢查或驗證方式與通過證據]
- [ ] AI `/code-review` 已完成；必要發現已處理，並記錄連結或摘要。

## 完成紀錄

- 實作 commit：[連結]
- 驗收證據：[連結或摘要]
- 完整驗證證據：[`uv run pytest` 結果、其他命令／人工檢查及連結或摘要]
- AI review 證據：[連結或摘要；必要發現的處理結果]
- `$task-closeout` 結果：[`Not run — remains Open/Blocked`，直到真正完成；完成後填入完成確認、狀態／證據一致性檢查及下一步]
- Tracker 狀態：[`Open`／`Closed`；`Blocked` 時必為 `Open`；若 `Closed`，填入關閉時間或連結]
- blocker／限制／handoff：[症狀、已嘗試事項、證據、所需決定與交接資訊；無則 `None`]
- 下一步：[下一張可開始的 Ticket、待解除 blocker，或交由 parent issue 的整體完成關卡]

只有驗收條件、完整驗證、AI review、實作 commit 與 `$task-closeout` 都完成且證據一致時，才可將 Tracker 狀態設為 `Closed`。完成後更新 parent issue。Ticket 關閉不表示子 PRD 已可 merge；完整關卡以 parent issue 與 [workflow.md](../workflow.md) 為準。
