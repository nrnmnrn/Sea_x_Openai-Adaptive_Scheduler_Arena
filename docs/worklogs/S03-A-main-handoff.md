# S03-A 原型移交 main

## 本次核可與交付邊界

2026-09-12，使用者明確指示依「先 merge 原型；必須等接口才能宣告接通」執行，並指定剩餘未完成工作交由 main 接手。本次以此指示作為提前合併原型的個案核可；不改變產品、契約及完整 S03-A 驗收條件，也不將此例外擴大至其他切片。

- Parent：[SP-03 #3](https://github.com/nrnmnrn/Sea_x_Openai-Adaptive_Scheduler_Arena/issues/3)。
- Active Ticket：[S03-A #6](https://github.com/nrnmnrn/Sea_x_Openai-Adaptive_Scheduler_Arena/issues/6)，保持 Open。
- 原型：[PR #12](https://github.com/nrnmnrn/Sea_x_Openai-Adaptive_Scheduler_Arena/pull/12)，原版本 `088c4beae2f07894606b9cf336f2b9b38ff5a4fd`。
- 本次相容性基準：main `f2cd6b0`，包含 S02 結果組裝模組；不代表 S02 真實評估／全敗接口已交付。
- main 承接後续整合；不補造人類 integrator 姓名，不將 AI review 寫成人類成員驗收。

## 已接收與必要補強

保留 Candidate 唯一 ID、連續版本／父鏈、五版上限、防禦副本及未驗證結果呈現。正式 runtime 仍明確拒絕執行。獨立生成實驗只提供語法／函式形狀檢查後的未驗證草稿，不執行生成程式、不啟用策略。

本次只補命令列入口的準備模式與失敗退出測試，不修改 production 邏輯、不新增依賴，也不讀取金鑰檔或呼叫外部生成服務。與最新 main 整合不修改 S02 模組，避免干擾正在開發的接口。

## 待接口完成後的恢復條件

1. main 與相關 Owner 核定觀測／評估時間窗、baseline、共同起始狀態、缺值與未完成結果分類；不得將現有 S02 時間窗相等限制視為既定契約。
2. 指定並提供共同 evaluator 的真實實作與契約版本，讓既有策略和 Candidate 使用一致規則與隔離起點。
3. 取得真實完整全敗輸入；任一策略通過不得呼叫 Planner，缺失或中斷不能當成全敗。
4. 接通單版生成、隔離評估與不可變結果交接，驗證未通過／外部錯誤安全停止、不修改 Live Policy、未驗證結果不得供 SP-04 晉升。
5. 完成切片驗收、人類確認及 main 整合證據後，才可關閉 #6；Parent #3 仍須全部切片與完整驗收。S03-B／C 不因本次移交自動開始。

## 狀態

此文件記錄原型移交決定與可恢復工作，不宣告正式流程接通。驗證命令與最終合併版本記錄於 PR 及本次完成報告；歷史工作紀錄保留原時點狀態。

## 合併前驗證

- `uv sync --frozen`：通過，沿用既有 lockfile。
- `uv run pytest -q`：87 passed；預設 backend 為 local。
- `uv run ruff check .`：通過。
- `uv run ruff format --check .`：通過，52 files already formatted。
- `git diff --check`：通過。
- 獨立 cavecrew review：原型邊界、與 main 相容性及新增入口測試均無待修正發現。
- 未找到型別檢查與 pre-commit 設定。
- `uv build`：失敗，setuptools 多頂層目錄自動探索；在 main `f2cd6b0` 隔離版本同樣重現。此為既有打包限制，未在本次改動打包設定，不宣稱可發佈安裝套件。
- 未執行外部生成服務、team backend、瀏覽器聯測或真實 S02→S03 交接。
