# GitHub Ticket 模板

> 僅於比賽當日，由已認領子 PRD 的 Owner 依核可子 PRD 建立。Ticket 只記一次工作與執行證據，不改寫產品或功能規格。

## 基本資料

- 所屬 parent issue：[連結]
- 所屬子 PRD：[相對路徑與版本]
- 順序與開始條件：[直接依賴／前一張 Ticket 證據／`main` 證據]

## 這次工作

[一個 vertical slice：描述本次從輸入到可觀察結果要完成什麼。]

## 不做事項

[明確列出不在本 Ticket 的工作。]

## 驗收與測試

- [ ] [可觀察的驗收條件]
- [ ] [相關測試或驗證方式]
- [ ] AI `/code-review` 已完成並處理必要發現。

## 完成紀錄

- commit：[連結]
- 自驗與測試證據：[連結或摘要]
- 限制／blocker：[內容或 `None`]
- 下一張可開始的 Ticket：[連結或條件]

完成後更新 parent issue 並執行 closeout。Ticket 完成不表示子 PRD 已可 merge；完整關卡以 parent issue 與 [workflow.md](../workflow.md) 為準。
