# GitHub parent issue 模板

> 僅於比賽當日、已核可子 PRD 被認領後建立。不要在賽前建立實例；本 issue 記執行狀態，不複製規格。

## 基本資料

- 子 PRD：[相對路徑與版本]
- Owner：[認領者]
- Branch：[唯一 branch 名稱]
- Draft PR：[連結]
- 直接依賴 frontier：[Consumer depends on Provider、Provider readiness 與最新 `main` 證據]
- 平行準備範圍：[僅已核定 contract 與子 PRD 指定的 deterministic adapter／fixture；正式整合與 closeout 一律等所有直接 Provider 已 merge 並在 `main` 驗證]

此 issue 僅記錄執行狀態與證據；需求、驗收、範圍與直接依賴仍以已核可子 PRD、PRD 與 contract 為準。一份子 PRD 只使用此唯一 branch 與一個 Draft PR。

## Ticket 清單

| Ticket | Tracker 狀態 | 工作狀態 | readiness／frontier 證據 | 完成證據 | closeout 結果 | blocker／限制 | 下一步 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [連結] | [`Open`／`Closed`] | [未開始／進行中／Blocked／完成] | [依賴、前一張 Ticket 與 `main` 證據] | [commit、驗收、完整驗證、AI review] | [`Not run — remains Open/Blocked`，或 `$task-closeout` 摘要] | [內容或 `None`] | [內容] |

`Blocked` Ticket 的 Tracker 狀態必為 `Open`。所有 Ticket 都是 `Closed` 只表示可以進入下列子 PRD 完成關卡，不能單獨關閉 parent issue。

## 子 PRD 完成關卡

- [ ] 全部 Ticket 完成，且整體功能驗收通過。
- [ ] 完整相關測試、最後 AI review 與 Owner 自查完成。
- [ ] 另一位成員已確認功能、證據與整合結果。
- [ ] main branch 負責人完成範圍、架構、依賴與整合檢查。
- [ ] 取得人類授權後，正式 PR 已 merge。
- [ ] 已在 `main` 完成整合驗收並留下證據。
- [ ] 子 PRD closeout 已確認 parent tracker、所有證據與下一步一致。

## Blocker 與核可紀錄

[記錄症狀、已嘗試事項、證據、所需決定及核可連結。文件矛盾、題意不清或介面不一致時，依 [workflow.md](../workflow.md) 停止受影響工作並記錄 `BLOCKED` 區塊。]

## Parent closeout 與下一步

- closeout 結果：[子 PRD 完成確認、tracker／證據一致性與 `main` 整合驗收證據]
- Parent 工作／label 狀態：[進行中／`Blocked`／完成；`Blocked` 時 Parent tracker 必為 `Open`]
- Parent tracker 狀態：[`Open`／`Closed`；只有所有完成關卡與 parent closeout 完成後才可設為 `Closed`]
- 下一步：[可開始的 Ticket、待處理 blocker，或整體 `main` 驗收／展示]
