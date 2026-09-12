# UI、Scheduler 與 Agent Adapter 契約

本契約定義 implementation repository 中 UI、scheduler、sandbox 與 Agent adapter 的共同邊界。若與 [總 PRD](../../PRD.md) 衝突，以總 PRD 為準；若子 PRD 對自己的直接依賴提出更嚴格要求，以子 PRD 為準。本文件不決定 LLM 供應商、部署方式或實作類別。

## 契約修訂與交接狀態

本次採納 2026-09-12 使用者的產品、責任、payload 與 Hybrid 方案。跨功能交付、提供／使用者、驗證方式與凍結檢查集中於 [adaptation-contract](adaptation-contract.md)。BackendAdapter 方法集合不等於全部由 SP-01 實作：SP-02 提供共用 evaluator／全敗比較，SP-03 重用 gate 並提供 accepted Candidate，SP-04 promotion；controller、checkpoint、storage 與 UI shell 的既有 seam 仍待同一位使用者兼任的 SP-01 接口確認者提供真實能力證據。

修改操作維持其既定逐方法回傳；controller 在成功 mutation 後以 `snapshot()` 取得序列化接受的 Snapshot，UI envelope 的 `playing` 不寫入 Snapshot。下列 identity、query、timeout 與 evidence 規則已核可；尚未有 seam 的實作能力不可宣稱完成。

共同 deterministic fixtures 是固定測試資料，繼續保留；不等於以替身取代未完成 Provider。正式整合依 workflow 使用真實上游。案例 A 的 Hybrid 真實通過來源依 D6 確認，不憑本次流程修改移除其 gate 前提。

## 環境與啟動契約

- 使用 Python 3.11 與 uv；支援範圍為 `>=3.11,<3.12`。`pyproject.toml` 固定包含 `gradio==6.26.0`、`plotly==7.0.0`，以及 dev dependency group 的 `pytest==9.1.1`、`ruff==0.16.6`。
- 以 `uv sync` 建立環境；命令不得寫死個人帳號或絕對路徑。
- `--backend` 必填。team mode 必須提供 `--factory module:function`；缺少、無法 import 或 factory 建立失敗時須明確退出，不得 fallback 到 local。
- local mode 只供明確選擇的開發或備援。正式串接與本機啟動入口如下：

```text
uv run python app.py --backend team --factory team_backend:create_backend
uv run python app.py --backend local
uv run python app.py --backend local --mode developer
```

Demo mode 是預設；`--mode developer` 才顯示手動套用已驗證 Skill 等測試控制，且不放寬 `--backend` 要求。

- 預設只綁定 `127.0.0.1:7860`，不建立公開分享連結；可用 `--port` 改埠。
- 每頁持續顯示 `資料來源：隊友後端` 或 `資料來源：本機備援`；外部 Planner／Evaluator／Critic 使用 Mock 時亦須持續顯示 `MOCK 示範`。
- 共用測試入口須接受相同的 `--backend`、`--factory`：

```text
uv run pytest -q --backend local
uv run pytest -q --backend team --factory team_backend:create_backend
```

缺少 team backend 時，team 驗收必須失敗，不得以 skip 或 local 結果宣稱 team mode 通過。

## 共同規則

- 同程序 Python factory：`create_backend(seed: int = 42, initial_jobs: list[dict] | None = None) -> BackendAdapter`。每個瀏覽器 session 呼叫一次；不得回傳共享的可變 singleton。
- `initial_jobs=None` 建立預設八筆 Job；`[]` 建立空場景。factory 完成 `t=0` 的到達與 dispatch 處理後才回傳。
- 公開 API 的 number 只接受內建 `int` 或 `float`，排除 `bool`、字串與 Decimal；輸出僅含 JSON 可序列化、有限的數值。內部可採 Decimal 保護邊界。
- 每個成功操作依方法表的既定回傳型別回傳：排程／控制 mutation 回傳新的防禦性 Snapshot，`register_skill` 回傳 Skill，查詢回傳其查詢結果。controller 在 mutation 後以 `snapshot()` 取得序列化接受的 Snapshot；讀取不可改變狀態。
- UI controller 對同一 session 的操作序列化；三個 tabs 不可各自推進或讀取不同狀態。
- controller 只從已接受且 `playing=true` 的 Snapshot 建立有效 degradation trigger，於同一序列化區段設 `playing=false` 並捕捉 checkpoint。每個 window 是已完成、不重疊的 `(t-5,t]`；新增 `expired >= 1` 才 trigger，跨界 `advance` 在第一個有效邊界停止。adaptation 期間 simulation clock、Job 進度、arrival、deadline 與 dispatch 不前進；`advance`、`inject`、`generate` 與 developer `set_policy` 必須拒絕且不變更 scheduler state。Planner／Evaluator／Critic 依 wall-clock time 自動執行。

## BackendAdapter 方法

| 方法 | 回傳 | 契約 |
| --- | --- | --- |
| `reset(seed=42)` | Snapshot | 新 run；時間 0、FIFO、八筆初始 Job、四個初始 Skills；清除 events、series、後續 Skills、Candidate 與 usage。 |
| `advance(dt)` | Snapshot | `dt` 為有限非負數；處理區間內全部事件；零不推進時間。active adaptation 期間必須拒絕且不改變 Snapshot。 |
| `inject(jobs)` | Snapshot | 驗證整批後原子加入；arrival 不早於現在；累計不超過 20。 |
| `generate(count)` | Snapshot | 僅接受整數 1 或 4；使用本 run 的 RNG 在現在時間產生並 inject。 |
| `set_policy(id, reason)` | Snapshot | 僅 developer mode；Skill 必須已驗證；不搶占；同 Policy 無狀態變更。 |
| `snapshot()` | Snapshot | 無副作用。 |
| `list_skills()` | `list[Skill]` | 回傳本 run 所有可用 Skills 與使用記錄；讀取不改變狀態。 |
| `detect_adaptation_trigger(snapshot)` | TriggerResult | 回傳是否觸發、可見原因、`workload_window` 與 `adaptation_id`；同 run／window 重複呼叫沿用 active adaptation，不產生第二輪。 |
| `evaluate_existing_skills(context)` | `list[EvaluationResult]` | SP-02 Provider 用同一已凍結 context、FIFO baseline、checkpoint、seed、workload 與 evaluation window 評估每個已驗證 Skill。 |
| `clone_for_evaluation(context_id)` | `BackendAdapter` | 回傳供受信任 builtin Policy replay 的獨立非零 backend clone；保留完整 scheduler state、RNG、Skills 與 adaptation evidence 的深拷貝，任何 clone mutation 不得回寫 Live Run。此方法不是任意 policy code 的安全執行器。 |
| `select_existing_skill(results)` | Skill 或 null | 僅在至少一個通過時依總 PRD 的固定順序選擇。 |
| `propose_candidate(context, feedback)` | Candidate | 僅在既有 Skills 全部失敗且未達五版時建立。 |
| `evaluate_candidate(candidate_id, baseline_run)` | EvaluationResult | 僅在 sandbox 執行；不得修改 live Run。 |
| `register_skill(candidate_id)` | Skill | 僅接受通過 gate 的 Candidate。 |
| `activate_skill(skill_id)` | Snapshot | 建立新 segment 與 `policy_activated`；下一次 dispatch 才使用。 |
| `get_accepted_candidate(run_id, adaptation_id, candidate_id, version)` | `{candidate: Candidate, evaluation_result: EvaluationResult, context_id: str}` | 僅回傳可信 accepted record 的精確版本；任何缺失、非 accepted、或 run/adaptation/candidate/version 不符皆以 `AdapterValidationError` 拒絕且不改變狀態，不接受 caller 重傳 code／passed 結果。 |

team mode 的 factory 載入失敗必須明確失敗，不得 fallback 到 local。local 或 Mock 僅能以明確 mode 選擇，且 UI 必須標示來源。

`TriggerResult` 至少有 `triggered`、`reason`、`run_id`、`workload_window`、`adaptation_id`。`workload_window` 是不可變物件 `{id, start, end}`：`start`、`end` 為已完成觀測區間的模擬時間，`id` 為同一 run 唯一的非空字串。同一 `run_id`、相同 `start`／`end` 必須回傳同一 window ID；simulation clock 恢復並進入新的觀測區間後才可產生新 ID。reset 清除全部 window／adaptation identity，故即使時間值相同亦屬新 run。`(run_id, workload_window.id)` 是 adaptation 唯一鍵；同鍵在 `evaluating_existing` 或 `evaluating_candidate` 時只回傳既有 ID 與目前進度，不排隊、不重跑 evaluator，也不建立新 Candidate。

Evaluation context 是不可變 checkpoint handle `context_id`，綁定 checkpoint、seed、非終態評分集合、FIFO baseline exact code、observation/evaluation windows。checkpoint 複本保留 `now`、Jobs（含 running/scheduled/terminal）、worker、policy／segment attribution、RNG／seed、Skills 與 code，且不得共享可變引用；sandbox 只產生 evaluation 結果，絕不回寫 Live Run。Live Snapshot 在 adaptation 期間只可變更 `adaptation`、對應 adaptation events、`snapshot_version` 與 controller/evidence revision；Job、worker、time、RNG、policy、Skills、segments、metrics、series、capacity 與既有 events 不得因 evaluation 改變。任意 policy code 必須在可終止且限制檔案、網路、資源及 wall-clock 的隔離執行環境執行；具體 SP-01 seam 仍待真實能力證據。

## 排程資料

### JobInput 與 Job

JobInput 為 `id`、`arrival`、`processing_time`、`priority`、`deadline`。ID 非空且同 run 唯一；arrival 非負；processing time 正；deadline 大於 arrival；所有數值有限。無效整批必須拒絕，不消耗 RNG，不留部分資料。

Job Snapshot 另含：`status`、`started_at`、`completed_at`、`dropped_at`、`feasible`、`dispatched_policy_id`、`segment_id`。`feasible` 僅對 pending／running 有值；終態與 scheduled 為 null。dispatch 同時寫入後兩個歸屬欄位；從未 dispatch 就 expired 時，`dispatched_policy_id` 保持 null，`segment_id` 於 expiry 寫入當時生效 segment。

狀態與同時刻事件順序、Policy 排序、deadline 邊界、單 worker、不搶占，均依總 PRD。事件序號 `seq` 在同一 run 遞增。

### Skill、Candidate、EvaluationResult

Skill 至少有 `id`、`name`、`description`、`code`、`source`、`verified`、`uses`、`last_applied_at`。`source` 為 `base`、`candidate` 或明確的 `mock`。`uses` 只計實際 dispatch，不計預覽或按鈕點擊。

Candidate 至少有 `candidate_id`、`parent_candidate_id`、`version`、`reason`、`policy_code`、`workload_scope`、`status`、`critic_feedback`、`evaluation_result`。狀態可為 `proposed`、`evaluating`、`failed`、`passed`、`registered`；ID 不可重複。

EvaluationResult 至少有 `subject_id`、`subject_kind`、`baseline_metrics`、`evaluated_metrics`、`evaluation_window`、`gate_passed`、`outcome`、`regressions`、`contract_validation`、`sandbox_status`、`failure_reason`、`critic_feedback`。`sandbox_status` 必須是 `passed`、`failed` 或 `incomplete`；只有 `passed` 才可進入 gate 判斷。`contract_validation` 是布林值，只有 `true` 可通過 gate。`outcome` 為 `passed`、`failed` 或 `incomplete`：只有 `sandbox_status == "passed"`、`contract_validation == true` 且 `gate_passed == true` 時為 `passed`；完整執行但 P95 不可比較、可歸因於 policy code 的例外或契約違反為 `failed`；baseline failure、無法歸因的 scheduler／runner／trace 故障、infrastructure／未能判明 timeout、缺失或 identity 不符為 `incomplete`。只有完整 `failed` 可計入 all-failed；`passed` 與 `incomplete` 均不得計入。它必須明示 sandbox 結果，不能混入 Live Run metrics。

本版 Skill 只保存上述最小欄位，不增加建立者、模型、成本、分類標籤或其他 metadata；實作者不得令額外欄位成為 UI、排序或 gate 的必要條件。

## Snapshot 與 Event

Snapshot 至少包含：

```text
run_id, snapshot_version, time, jobs, worker, policy, metrics,
segments, events, series, adaptation, capacity
```

- `run_id`：每次 reset 改變。
- `snapshot_version`：同一 run 單調遞增；供 UI 拒收過時回應。
- `worker`：`job_id`、`state`（`idle`／`running`）、`reason`。
- `policy`：`id`、`name`、`code`、`previous_code`、`reason`。
- `metrics`：`completed`、`expired`、`throughput`、`p95_latency`；無定義值用 null。
- `segments`：已啟用 Policy 的時間範圍與 segment metrics；不得與整局或 sandbox 指標混淆。
- `series`：按事件時間排序的整局 metrics 歷史；同時刻可合併。
- `adaptation`：`stage`、`message`、`adaptation_id`、`workload_window`、`candidate_id`。
- `capacity`：`total`、固定 `limit=20`、`remaining`。

`adaptation.stage` 至少支援 `idle`、`evaluating_existing`、`existing_skill_reused`、`evaluating_candidate`、`registered`、`failed`。stage 只描述已發生或正在執行的流程；UI 不可自行推測下一狀態。

Event 至少有 `seq`、`time`、`type`、`job_id`、`policy_id`、`adaptation_id`、`candidate_id`、`message`。必要類型為排程事件 `arrived`、`started`、`completed`、`expired`，以及 `adaptation_triggered`、`existing_skill_reused`、`candidate_proposed`、`candidate_evaluated`、`skill_registered`、`policy_activated`、`adaptation_failed`、`adaptation_error`。無關 ID 用 null。

每個 adaptation Event 必須以 `adaptation_id` 串成可追溯 progression。外部 adapter 失敗統一記錄 `adaptation_error` 與失敗 stage／原因，不為每個 provider 建立不同 Event 類型。錯誤後保持暫停並顯示手動 retry；不得自動 retry 或自動切換 Mock。

## Metrics

- Live Run：整局 `completed`、`expired`、`throughput`、P95 completion latency。
- Policy segment：已 dispatch Job 的完成、expired 與 latency 全部歸於 dispatch 時寫入的 `segment_id`；跨越 Policy 切換才結束仍屬原 dispatch segment。從未 dispatch 就 expired 的 Job 歸於 expiry 時生效的 segment，不產生 latency。
- Existing Skill evaluation：相同 baseline 下各既有 Skill 的 sandbox 結果。
- Candidate evaluation：各 Candidate 版本的 sandbox 結果。

Live Run 的 throughput 為 `completed / (time / 60)`；Live Run 時間為零時為 null。Sandbox evaluation 僅在正長 evaluation window 定義 throughput，公式為本輪評分集合的 `completed / ((evaluation.end - evaluation.start) / 60)`；評分集合不包含 checkpoint 前的歷史終態 Jobs，window 非正長時為 null。P95 只用 completed Jobs 的 `completed_at - arrival`，空集合為 null，採線性插值。卡片可四捨五入顯示，測試比較原始值。

### 共同 deterministic fixtures

local 與 team adapter 必須以 factory 的 `initial_jobs` 建立下列獨立場景並得到相同預期；不得依賴預設隨機 Jobs。

**案例 A：基本 Policy。** 四筆 Job 均在 `t=1` 到達；於 `t=0` 選定已驗證 Policy，再推進至 `t=1`。

| ID | arrival | processing_time | priority | deadline |
| --- | --- | --- | --- | --- |
| A | 1 | 6 | 2 | 25 |
| B | 1 | 2 | 1 | 12 |
| C | 1 | 4 | 5 | 18 |
| D | 1 | 3 | 3 | 9 |

預期首筆為 FIFO=A、SJF=B、Priority=C、EDF=D、Hybrid=C。Hybrid 測試使用已通過 gate 並依契約註冊的固定 Candidate；不得加入 Demo mode 的人工 accept。

**案例 B：deadline 與同時刻順序。** A=`(arrival=0, processing_time=2, priority=1, deadline=2)`；B=`(0,3,1,2)`；C=`(2,1,1,4)`。`t=0` 派 A；`t=2` 依序完成 A、丟棄 B、納入 C、派 C。B 不得開始；C 於 `t=3` 完成。

**案例 C：metrics。** FIFO；A=`(arrival=0, processing_time=2, priority=1, deadline=10)`；B=`(0,4,1,10)`，欄位順序同 A。A 於 `t=2`、B 於 `t=6` 完成。`t=6` 時 completed=2、expired=0、throughput=20、P95=5.8；不新增 Job 而推進至 `t=12` 時 throughput=10、P95 仍為 5.8。

**案例 D：不搶占。** A 於 `t=0` 開始，processing time=5、deadline=20；B、C 於 `t=1` 到達，processing time 分別為 4、1，priority 均為 1、deadline 均為 20。`t=1` 切至 SJF；A 仍於 `t=5` 完成，下一筆選 C。

## Session 與錯誤

UI envelope 另持有 `session_generation`、`revision`、`backend_source`、`playing`、`speed`、`error`。長操作 request／response 必須原樣帶回 `(session_generation, run_id, adaptation_id, context_id, request_id, operation)`；`operation` 為 `evaluate_existing`、`propose_candidate`、`evaluate_candidate`、`critic_feedback`、`register_skill` 或 `activate_skill`。Candidate operation 再核對 `candidate_id` 與正整數 `version`；Planner 的新 ID/version 是 response 結果，非 request identity。evidence 與 accepted Snapshot 同綁 session_generation、run_id、adaptation_id、context_id、snapshot_version、evidence_revision，三 tabs 只呈現同一組已接受版本。有效 trigger 把 `playing` 設為 false；成功 `existing_skill_reused` 或 `policy_activated` 後設回 true。reset 增加 generation 並換 run ID；過時 generation、run ID、request 或 revision 的結果不得套用到任何 tab，UI refresh 不得使合法 pending response 失效。

輸入錯誤以 `AdapterValidationError(ValueError)` 回報，並保證 Job、RNG、events、時間不變。操作或讀取失敗以 `AdapterOperationError(RuntimeError)` 回報，含 `state_uncertain: bool`；無法證明未修改時預設為 true。controller 必須保持暫停、保留最後有效 Snapshot、記錄 `adaptation_error`，並顯示失敗 stage、可讀原因及唯一安全動作。`state_uncertain=false` 時，使用者可手動從最後完成的 adaptation stage 重試；`state_uncertain=true` 時只提供重新取得狀態或 reset。任何情況皆不得自動重送修改操作。不得把 stack trace 當使用者文案。

外部 Planner／Critic timeout 為 60 秒 wall-clock，Evaluator 為 10 秒；timeout、schema 或服務錯誤時 adaptation 進入失敗狀態並保持暫停。取消只使本地 request 無效，遲到 response 丟棄。手動 retry 沿用原 `adaptation_id` 與 context；只可重試未完成 stage，不得重複已完成且有副作用的 stage。register／activate 已完成後須先以 query 證明再繼續；五版失敗不能新增版本預算，只能 resync/reset。成功完成後才恢復播放。不得默默改用 Mock。
