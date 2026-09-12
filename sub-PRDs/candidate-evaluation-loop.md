# SP-03：Candidate Evaluation Loop

## 基本資料

- 狀態：`Unclaimed`
- 核可狀態：待人類核可；未核可前不可開始實作
- 版本：`0.1-draft`
- Owner：待比賽當日認領
- GitHub parent issue：待比賽當日認領後建立
- 核可紀錄：待填核可者、日期與連結

## 交付結果

交付「全部既有 Skills 失敗後，安全評估新策略」的完整路徑：Planner 提出唯一版本的 Candidate，Evaluator 在隔離 sandbox 套用 gate，Critic 將可讀失敗原因回饋 Planner，最多五版；失敗、契約違反與外部錯誤均留下可見證據，且從不修改 Live Run。

## 範圍

- 消費 all-skills-failed context 後才呼叫 provider-neutral Planner，產生唯一 `candidate_id`、父版本、原因、policy code 與 workload scope。
- 在 sandbox 使用與 baseline 相同 workload、seed、初始 state、evaluation window 執行 Candidate；驗證 Job、deadline、單 worker、不搶占、event 順序、有效 Snapshot 與可序列化 metrics。
- 實作 expired／completed／P95 evaluator gate、退化說明、Critic feedback、最多五版迭代及五版失敗結束。
- 在 adaptation UI 插入點顯示 Candidate 版本、sandbox 結果、gate、feedback 與停止原因；清楚區分 sandbox 與 Live Run。
- AI 在 simulation clock 暫停期間自動完成 Planner、Evaluator 與 Critic 迭代，不需使用者調參或接受 Candidate。
- 外部 Planner、Evaluator、Critic 或 LLM timeout、schema、服務錯誤時停止目前 loop、保持暫停、保留最後有效 Snapshot、記錄 `adaptation_error` 並提供安全的手動 retry。

## 不在範圍

不將 Candidate 寫入 Skill Library，不啟用 Candidate，不改變 live Policy 或 segment；這些由 SP-04 負責。不得以 Mock 取代失效外部服務，除非明確啟用離線 Mock mode 並標示來源。

## PRD requirement coverage

| PRD 要求 | 本子 PRD 如何覆蓋 | 驗收證據 |
| --- | --- | --- |
| `PRD.md`「自動 adaptation」之 Candidate gate 與 lineage | 只在 all-skills-failed 後建立唯一 Candidate；保存 parent、原因、code、workload 與 feedback。 | R10；all-failed gate、ID 與 lineage 測試。 |
| `PRD.md`「自動 adaptation」之 evaluator、Critic 與五版上限 | 以相同 baseline 執行 gate；拒絕後回饋；最多五版；全敗留下 `adaptation_failed`。 | R11–R12；gate、版本上限及失敗證據。 |
| `PRD.md`「Metrics、Snapshot 與 Adapter」 | sandbox 不回寫 Live Run；保留 Snapshot、metrics、events；外部錯誤保持暫停並提供安全手動 retry。 | R11、R13、R16–R18；before／after、adapter error 與 retry 測試。 |
| `PRD.md`「Demo 與 Developer mode」 | Demo 不提供人工 accept；外部錯誤不 fallback Mock；明確顯示來源。 | R13、R20；錯誤與瀏覽器證據。 |
| `PRD.md`「90 秒短展示與 progression run」 | 顯示 AI 自動 Planner、Candidate、Critic、gate 與 promotion 前 sandbox 證據。 | R19–R20；team mode 短展示與 progression 紀錄。 |

## 介面與直接依賴

| 方向（Consumer depends on Provider） | 類型 | 需要的輸出或 contract | 可開始條件 | 整合條件 | 理由 |
| --- | --- | --- | --- | --- | --- |
| SP-03 depends on SP-02 | Contract | run／window 唯一 TriggerResult、既有 Skill EvaluationResult、all-failed 判定、active adaptation context | 契約已核定；使用 deterministic all-failed fixture | SP-02 實際輸出驅動 loop | Candidate 只能在全部既有 Skills 失敗後建立。 |
| SP-03 depends on SP-01 | Contract | sandbox、baseline Snapshot、metrics、events、pause／resume、手動恢復 UI 插入點 | 契約已核定；使用 baseline fixture | SP-01 證明 sandbox／live 隔離與 clock pause | Candidate 必須在 scheduler contract 上安全評估。 |
| SP-03 depends on SP-01、SP-02 | Integration | 真實 trigger、all-failed context、pause／resume、retry、sandbox／live 比較 | Contract fixtures 可先行 | team mode 完成聯合驗收 | 驗證真實 all-failed 串接。 |

本子 PRD 向 SP-04 提供 gate-passed Candidate、完整 EvaluationResult 與不可變 promotion input。

## 必要行為

- 全部既有 Skills 失敗前不得建立 Candidate；有任一通過時本 loop 不得執行。
- 每版 Candidate ID 唯一，並保存 parent、原因、code、workload、evaluation、feedback 與失敗理由。
- Gate 條件：expired 下降；或相同時 completed 增加且 P95 不惡化；completed 不得下降；P95 不得惡化；全部契約檢查與 sandbox 執行成功。
- 不通過、執行錯誤或契約違反時回饋 Planner；第五版仍失敗時停止並建立 `adaptation_failed` evidence，維持 Live Policy。
- 五版失敗或外部錯誤後 simulation clock 保持暫停。`state_uncertain=false` 時只由使用者手動從最後完成的 stage retry；狀態不明時只可 resync 或 reset。
- sandbox 的 Job、events、metrics、Skills 與 Candidate 變化不得回寫到 Live Run。
- UI 明確標示資料來源與 Mock 狀態；sandbox metrics 不得作為 live 改善宣稱。

## 驗收與證據

- 對 all-skills-failed 前、單版拒絕、Critic 後續版本、第五版失敗、gate 通過、契約違反與 adapter timeout 寫 deterministic 測試。
- 每項評估可對照相同 baseline inputs，並證明 Live Run Snapshot 在 loop 前後不變。
- 驗證 Candidate ID／parent chain、最多五版、feedback、gate 原因、`adaptation_failed` 與 UI 證據完整。
- 驗證 Demo mode 不顯示人工 accept，外部錯誤不 fallback Mock，最後有效 Snapshot 可讀。
- 驗證外部錯誤記錄 `adaptation_error`、不自動 retry；安全手動 retry 沿用 `adaptation_id` 且不重複已完成的副作用，成功後交由 SP-04 恢復。

## Ticket 設計與數量閘門

預估 Ticket 數：3 張。以下是賽前 vertical-slice 設計，不是已建立的 GitHub Ticket：

1. **從 all-skills-failed 到單版 Candidate 結果。** 消費失敗 context，產生唯一 Candidate，在隔離 sandbox 執行 gate，並顯示 lineage 與比較證據。
2. **從 Candidate 拒絕到 Critic loop 結束。** 保存 feedback、產生後續版本，於通過或第五版失敗時留下完整可見結果，且不修改 Live Run。
3. **從外部錯誤到安全手動恢復。** timeout、schema 或服務錯誤時保持暫停、保留最後有效 Snapshot 並顯示來源與錯誤；安全狀態可手動 retry，狀態不明只可 resync 或 reset。

## 已核定產品行為

外部 adapter 錯誤統一記錄 `adaptation_error`，UI 顯示失敗 stage 與原因。系統不得自動 retry；僅在狀態可證明安全時提供手動 retry，狀態不明時只提供 resync 或 reset，且不得自動切換 Mock。
