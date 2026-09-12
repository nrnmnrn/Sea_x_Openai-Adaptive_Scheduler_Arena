# GitHub parent issue 模板

> 僅於比賽期間、子 PRD 的明確核可範圍被認領後建立；局部核可不可宣稱整份核可。SP-01 沿用現有 issue，不重建。本 issue 記執行狀態，不複製規格。

## 基本資料

- 子 PRD：[相對路徑與版本]
- Owner：[認領者]
- 交付模式：[SP-01 保留完整交付／SP-02～04 真實切片]
- Branch／Draft PR：[SP-01 原唯一 branch／PR；SP-02～04 各 Ticket 的 branch／PR 對照]
- 直接依賴 frontier：[Consumer depends on Provider、Provider readiness 與最新 `main` 證據]
- 平行開發範圍：[已核准範圍與契約；哪些可寫、哪些需等真實上游才能驗證；不能用替身當 readiness 證據]
- Prototype 分類與 interface issue：[每個範圍的 A／B／C、I01–I09 或已登錄 ID、discussion 狀態 H／D、排除範圍與未驗證項；無則 `Not applicable`]
- 開發版試接紀錄：[指定人類 integrator、Owner 許可、隔離位置、真實未 merge 版本、實際輸入、保護措施、版本／錯誤證據；無則 `Not applicable`]

此 issue 僅記錄執行狀態與證據；需求、驗收、範圍與直接依賴仍以核可子 PRD、PRD 與 contract 為準。interface discussion board 只作協調，決定須先反映到權威文件。交付模式及開工、開發版試接、正式交付與完整結案依 [workflow](../workflow.md)。

## Ticket 清單

| Ticket | 類別／interface ID | Tracker 狀態 | 工作狀態 | readiness／試接與正式證據 | 完成證據 | closeout 結果 | blocker／限制 | 下一步 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [連結] | [A／B／C／N/A；Ixx；H／D] | [`Open`／`Closed`] | [未開始／進行中／Blocked／完成] | [依賴、真實 Provider 版本、試接證據與正式 `main` 證據分列] | [commit、驗收、完整驗證、AI review] | [`Not run — remains Open/Blocked`，或 `$task-closeout` 摘要] | [內容或 `None`] | [內容] |

`Blocked` Ticket 的 Tracker 狀態必為 `Open`。所有 Ticket 都是 `Closed` 只表示可以進入下列子 PRD 完成關卡，不能單獨關閉 parent issue。

## 子 PRD 完成關卡

- [ ] 全部 Ticket 完成，且整體功能驗收通過。
- [ ] 完整相關測試、最後 AI review 與 Owner 自查完成。
- [ ] 另一位成員已確認功能、證據與整合結果。
- [ ] main branch 負責人完成範圍、架構、依賴與整合檢查。
- [ ] SP-01 整份 PR，或 SP-02～04 全部切片 PR，均已取得人類授權並 merge。
- [ ] 已在 `main` 完成整合驗收並留下證據。
- [ ] 子 PRD closeout 已確認 parent tracker、所有證據與下一步一致。

## Blocker 與核可紀錄

[記錄症狀、已嘗試事項、證據、所需決定及核可連結。文件矛盾、題意不清或介面不一致時，依 [workflow.md](../workflow.md) 停止受影響工作並記錄 `BLOCKED` 區塊。]

## Parent closeout 與下一步

- closeout 結果：[子 PRD 完成確認、tracker／證據一致性與 `main` 整合驗收證據]
- Parent 工作／label 狀態：[進行中／`Blocked`／完成；`Blocked` 時 Parent tracker 必為 `Open`]
- Parent tracker 狀態：[`Open`／`Closed`；只有所有完成關卡與 parent closeout 完成後才可設為 `Closed`]
- 下一步：[可開始的 Ticket、待處理 blocker，或整體 `main` 驗收／展示]
