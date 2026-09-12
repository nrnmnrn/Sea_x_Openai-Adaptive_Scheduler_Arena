# S03-A：隔離的 OpenAI 生成實驗

## 本次授權與邊界

使用者於本次對話要求先實作外部 OpenAI 候選生成並測試生成能力，後續選擇「給我指令，我在自己的終端執行真實測試」。此為獨立實驗的明確授權，超出先前只做 A／B 內部紀錄的範圍；不將 D2～D9 標示已核定，不接入正式 Candidate loop，亦不宣稱 S03-A 已完成。

- 分支沿用 `codex/s03-a-candidate-internals`；GitHub 依先前要求只保留本地紀錄。
- 程式限 `experiments/openai_candidate_generation.py` 及必要套件標記；測試限 `tests/test_openai_candidate_generation.py`。
- 固定模型 `gpt-6-astra`、`reasoning.effort=low`，使用 OpenAI Responses API。
- 一次請求、最多 4096 輸出 tokens、逾時 60 秒、不自動重試或更換模型；`store=false`。
- 只送程式內明列的合成工作樣本與排程限制，不讀取 repository、Live Run 或上游全敗資料。使用者明確指定 `--env-file .env` 時，只在執行期間讀取其中的 OpenAI key。
- 輸出的策略程式碼只是未驗證草稿。只分析 Python 語法與實驗函式形狀，不執行生成程式，不宣告隔離評估／gate 通過，也不登錄或啟用 Skill。
- 本次輸出格式與函式簽名只屬於這個實驗，不定義跨組資料契約。

## 官方 API 依據

- [GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)：模型 ID 與 low reasoning 支援。
- [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)：Responses 的 `text.format` JSON Schema 設定。
- [Responses API](https://developers.openai.com/api/reference/cli/resources/responses/methods/create)：單次生成、status、output 與 store 設定。

## 實作與執行方式

- `experiments/openai_candidate_generation.py`：建立固定 Responses API 請求、處理回應、做不執行程式碼的 AST 語法／函式形狀檢查並寫出未驗證產物。
- `tests/test_openai_candidate_generation.py`：以本地 transport 驗證一次請求、無 retry／redirect fallback、拒絕／錯誤回應、安全金鑰讀取與不執行生成程式碼。
- `.env` 僅由命令執行時的 parser 讀取指定鍵，支援 `OPENAI_API_KEY` 或 `openai_api_key`；不執行 shell 展開、不修改環境、不輸出或保存金鑰。

```bash
.venv/bin/python -m experiments.openai_candidate_generation --env-file .env
```

## 驗證與真實生成結果

- `uv run pytest`：首次實驗版本加總 23 項通過；加入 `.env` parser 與 AST 邊界測試後，改以已建立的 Python 3.11 環境執行 `.venv/bin/pytest`，最終 **25 項全部通過**。
- `.venv/bin/ruff check .`、`.venv/bin/ruff format --check .`、`git diff --check`：全部通過。直接使用 `.venv` 是因 sandbox 內 `uv run` 無法初始化使用者 cache；沒有跳過相同測試工具。
- `--prepare-only`：成功產生不含金鑰的請求預覽；未發出網路請求。
- 真實生成：使用者告知 `.env` 已有 OpenAI key 後，依其「先做並測試」指示執行一次。HTTP 請求成功完成，模型 `gpt-6-astra`、effort `low`，輸入 290 tokens、輸出 289 tokens、總計 579 tokens。
- 產物：`artifacts/planner-experiment/candidate-20260912T071545Z-14095cb97b3e4eb09e70b57271147ba5.json`。不含 API key；保存合成輸入、response ID、usage、草稿、語法／形狀結果及 `evaluation_status=unverified`。
- 草稿定義唯一 `choose_job(jobs, now)`，先過濾到達、pending、可在 deadline 完成的工作，再依 priority 降序、deadline、processing time、arrival、ID 排序；對合成案例的文字理由選擇 `urgent`。AST 語法／函式形狀檢查通過。
- 獨立 Standards 與 Spec 複查各為 0 項待修正發現；Spec 複查促成 AST 檢查收緊為最外層只能有唯一、無 decorator 的 `choose_job(jobs, now)`，測試已覆蓋額外最外層程式碼的拒絕。

以上證明 OpenAI API 可用且能生成符合本實驗格式的候選草稿。生成程式碼沒有被執行，亦未經真實 scheduler sandbox、契約驗證、metrics gate 或安全審查，因此不能宣稱策略正確、改善排程、通過 evaluator 或可供 SP-04 使用。正式接入仍等待 H4、D2～D9 及團隊核定介面。
