# ADR 0002：一份子 PRD 一條 branch

> Status: accepted

## 決策

一份已核可子 PRD 對應一條從最新 `main` 建立的 branch 與一個 Draft Pull Request。該子 PRD 的所有 Ticket 都在這條 branch 依真實依賴順序完成；每張真正完成的 Ticket 各有一個可辨識的 commit。非 `main` branch 必須能連回唯一子 PRD 與其 GitHub parent issue。

比賽當日認領者是 Owner，建立 parent issue、branch、Draft PR 和依核可子 PRD 拆出的 Ticket。branch 表示工作歸屬；認領、進度、證據與核可狀態仍以 parent issue 為準。

## 取捨與界線

這樣可把完整功能以一個可審查變更集交付，減少每張小工作反覆開 branch、PR、merge 與 rebase 的成本。代價是 Owner 必須維持 Ticket 順序與同檔協調，並在每張 Ticket 後留下可驗證證據。

若工作量估計超過可控範圍，先依 [子 PRD 撰寫規則](../../sub-prd-authoring.md) 拆分或縮減子 PRD；不得改成多條 branch 來避開 2 至 3 張 Ticket 的標準或超過 5 張不得核可的上限。

子 PRD 完成後，仍須經完整測試、AI review、Owner 自查、另一位成員確認、人類授權的正式 PR merge 及 `main` 整合驗收，才可關閉 parent issue。
