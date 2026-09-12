# Adaptive Scheduler Arena：SP-01 Scheduling Arena

本 repository 目前只實作 `sub-PRDs/scheduling-arena.md`。Agent adaptation、Candidate、Evaluator 與 Skill promotion 等其他 sub-PRD 功能等待隊友完成後再整合。

## 比賽環境與啟動

比賽時使用 Anaconda `scheduler-ui` 環境：

```powershell
conda activate scheduler-ui
python app.py --backend local
python app.py --backend local --mode developer
```

team backend 到位後，使用指定 factory：

```powershell
python app.py --backend team --factory team_backend:create_backend
```

team factory 載入失敗會明確報錯，不會自動切換到 local。頁面會持續顯示資料來源與 `MOCK 示範` 標籤。

## 驗證

```powershell
conda activate scheduler-ui
pytest -q --backend local
ruff check .
ruff format --check .
```

以下內容是交接包原文，保留作為規格與流程參考。

本 repository（程式庫）是 Sea × OpenAI Hackathon 的正式實作與驗收空間。

產品展示 workload 改變時，Agent（自動執行與判斷的程式）如何先重用已驗證的 Skill，必要時再產生、隔離評估及採用新策略。完整產品行為以 [PRD](PRD.md) 為準。

## 開始工作

1. 先讀 [AGENTS.md](AGENTS.md)，確認工作規則與安全界線。
2. 再讀 [INDEXER.md](INDEXER.md)，依目前工作選取必讀文件。
3. 依 [workflow.md](workflow.md) 認領工作、建立證據、審查、整合及結案。

能清楚回答此次工作的範圍、開始條件、驗收證據與下一步後，才開始修改。

## 文件入口

- 產品範圍與行為：[PRD.md](PRD.md)
- 功能範圍、依賴與驗收：[`sub-PRDs/`](sub-PRDs/)
- 跨功能介面：[`docs/contracts/`](docs/contracts/)
- 總體驗收證據：[ACCEPTANCE.md](ACCEPTANCE.md)
- 工作流程：[workflow.md](workflow.md)
- 比賽規則與開發時點：[COMPETITION.md](COMPETITION.md)
- 文件權威與衝突處理：[ADR 0001](docs/adr/0001-document-authority.md)

GitHub parent issue 與 Ticket 僅記錄執行狀態及證據；產品需求與介面仍以上述文件為準。

目前採[原型優先異步開發](docs/adr/0004-prototype-parallel-development.md)：SP-01 保留原完整開發；SP-02～04 按[三類工作表](docs/product/prototype-work-plan.md)先做可獨立部分，用[接口討論表](docs/product/interface-discussion-board.md)同步決策。可用真實開發版本持續試接；正式交付仍須 main 證據。未決產品規則不自行補值，原型接通不等於完整驗收。

## 環境、啟動與測試

依[後端契約的環境與啟動章節](docs/contracts/backend-contract.md#環境與啟動契約)建立環境、啟動 UI、選擇 backend（後端執行方式）及執行測試。依賴版本以 [pyproject.toml](pyproject.toml) 為準。

# 連結
https://github.com/nrnmnrn/Sea_x_Openai-Adaptive_Scheduler_Arena/tree/main