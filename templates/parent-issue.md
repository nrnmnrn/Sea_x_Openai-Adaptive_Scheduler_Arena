# GitHub parent issue 模板

> 僅於比賽當日、已核可子 PRD 被認領後建立。不要在賽前建立實例；本 issue 記執行狀態，不複製規格。

## 基本資料

- 子 PRD：[相對路徑與版本]
- Owner：[認領者]
- Branch：[唯一 branch 名稱]
- Draft PR：[連結]
- 直接依賴 readiness：[Provider 已在 `main` 驗證的證據，或 main branch 負責人例外核可]

## Ticket 清單

| Ticket | 狀態 | commit／PR 證據 | 測試與驗收證據 | blocker／下一步 |
| --- | --- | --- | --- | --- |
| [連結] | [未開始／進行中／完成／Blocked] | [連結] | [連結或摘要] | [內容] |

## 子 PRD 完成關卡

- [ ] 全部 Ticket 完成，且整體功能驗收通過。
- [ ] 完整相關測試、最後 AI review 與 Owner 自查完成。
- [ ] 另一位成員已確認功能、證據與整合結果。
- [ ] main branch 負責人完成範圍、架構、依賴與整合檢查。
- [ ] 取得人類授權後，正式 PR 已 merge。
- [ ] 已在 `main` 完成整合驗收並留下證據。

## Blocker 與核可紀錄

[記錄症狀、已嘗試事項、證據、所需決定及核可連結。]
