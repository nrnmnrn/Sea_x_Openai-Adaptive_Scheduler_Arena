# 實作交接包（候選版）

`build-handoff_final/` 是準備帶入未來比賽實作 repository 的單一文件包。它目前等待獨立驗收；通過前是候選交接包，不宣稱已取代其他交接包。驗收通過後，複製整個資料夾到實作 repository 使用；閱讀與執行不應需要規劃 repository 的其他檔案。

團隊提出的題目更換已獲主辦方核准；本包因此以 [Adaptive Scheduler Arena 總 PRD](PRD.md) 為現行題目。此項核准不等於本候選交接包已通過獨立驗收。

本包只保存可執行的產品規格、介面約定、驗收基準及協作治理。不保存研究原文、會議紀錄、個人資料、憑證或被淘汰方案。

## 先讀什麼

先讀 [AGENTS.md](AGENTS.md)，再依 [INDEXER.md](INDEXER.md) 選讀。它會依目前工作指出唯一需要的文件，避免把規格、執行狀態與歷史資料混在一起。

文件職責如下：

| 文件 | 回答的問題 |
| --- | --- |
| [PRD.md](PRD.md) | 產品必須做什麼？ |
| `sub-PRDs/*.md` | 一項完整功能的範圍、直接依賴與驗收是什麼？ |
| `docs/contracts/*.md` | 跨功能使用的介面如何交換資料或呼叫？ |
| [ACCEPTANCE.md](ACCEPTANCE.md) | 總 PRD 的每項要求由哪個功能負責、用何證據驗收？ |
| [workflow.md](workflow.md) | 比賽當日如何認領、執行、審查、整合與結案？ |

權威關係與衝突處理見 [文件權威 ADR](docs/adr/0001-document-authority.md)。GitHub parent issue 與 Ticket 只記錄執行中的狀態和證據，不能改寫上述規格。

從空白 implementation repository 建立 Python／uv 環境、實作啟動入口或選擇 team/local backend 時，以[後端契約的環境與啟動章節](docs/contracts/backend-contract.md#環境與啟動契約)為唯一技術基準。

## 比賽前與比賽當日

賽前只準備並驗收本文件包：不預先指定 Owner（負責該功能的人）、不建立 GitHub issue，也不建立正式 Ticket。官方 coding window 開始後，第一位認領已核可子 PRD 的人即為該子 PRD Owner；他建立 parent issue 與 Ticket，並依 [workflow.md](workflow.md) 開始工作。

本包不包含競賽程式碼。程式、測試執行結果、commit、Pull Request（PR，供審查與合併的變更單）及 GitHub issue 都只在比賽當日的實作 repository 產生。

## 安全與使用界線

- 每位參與者使用自己的憑證；共享運算資源不等於共享帳號。
- 不把 API key、token、密碼、私鑰或私人通信寫入 repository、issue、Ticket 或 prompt。
- 只有取得人類授權的角色可以 merge、push 或 deploy；AI 可協助檢查，不能核准或執行這些動作。
- 產品範圍、介面或驗收有矛盾時，停止相關工作並依 [文件權威 ADR](docs/adr/0001-document-authority.md) 處理，不自行猜測。
