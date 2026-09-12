# SP-04：Skill Promotion and Recovery

## 基本資料

- 狀態：`Unclaimed`
- 核可狀態：待人類核可；未核可前不可開始實作
- 版本：`0.1-draft`
- Owner：待比賽當日認領
- GitHub parent issue：待比賽當日認領後建立
- 核可紀錄：待填核可者、日期與連結

## 交付結果

交付「只有合格 Candidate 進入正式執行」的完整路徑：接收已通過 gate 的 Candidate，自動註冊為 Skill、顯示於 Skill Library、建立 policy segment 與 `policy_activated` event，於下一次 dispatch 啟用；註冊／啟用失敗時維持最後有效狀態，reset 回復初始 Skills。

## 範圍

- 驗證 promotion input 的 Candidate gate-passed EvaluationResult，再註冊成 `verified=true`、`source=candidate` 的 Skill。
- 自動啟用已註冊 Skill，建立新的 Policy segment 與 `policy_activated` evidence；running Job 不被中斷，新 Skill 從下一次 dispatch 生效，成功後設回播放。
- 在 Skill Library 與 adaptation UI 呈現註冊來源、code、使用記錄、gate 依據、啟用原因與生效時點。
- 實作註冊、啟用、後續 Snapshot 讀取失敗的錯誤處理：保持暫停、保留最後有效 Snapshot、顯示錯誤；安全狀態可手動 retry，狀態不明時先重新同步或 reset，不自動重送修改。
- reset 清除後續 Candidate Skills、segments、usage 與 adaptation 狀態，恢復 FIFO、SJF、Priority、EDF。

## 不在範圍

不決定 trigger、既有 Skill 選擇、Planner、Candidate 版本迭代或 evaluator gate。本子 PRD 不得接受未通過、缺少或狀態不明的 EvaluationResult，也不得改寫 sandbox 結果。

## PRD requirement coverage

| PRD 要求 | 本子 PRD 如何覆蓋 | 驗收證據 |
| --- | --- | --- |
| `PRD.md`「名詞與產品邊界」 | 只接受 verified Candidate；reset 恢復 FIFO、SJF、Priority、EDF；不接受未驗證 code。 | R16、R20；拒絕輸入、reset 與範圍審查。 |
| `PRD.md`「自動 adaptation」之 register、activation 與 segment | gate-passed Candidate 才 register；建立 `policy_activated` 與新 segment；恢復 simulation clock，並於下次 dispatch 生效。 | R14–R15；register、event、resume、running Job 與 dispatch 測試。 |
| `PRD.md`「Metrics、Snapshot 與 Adapter」 | 分開 Live、segment、Candidate evaluation metrics；同步錯誤保留最後有效 Snapshot。 | R16–R18；contract、錯誤與資料分離證據。 |
| `PRD.md`「Demo 與 Developer mode」 | Demo 無人工 accept；失敗不 fallback Mock；顯示錯誤與來源。 | R16、R20；瀏覽器及錯誤證據。 |
| `PRD.md`「90 秒短展示與 progression run」 | 顯示 Skill Library、registration、activation、resume、next dispatch 與逐輪 live／sandbox 差異。 | R19–R20；team mode 短展示與 progression 紀錄。 |

## 介面與直接依賴

| 方向（Consumer depends on Provider） | 類型 | 需要的輸出或 contract | 可開始條件 | 整合條件 | 理由 |
| --- | --- | --- | --- | --- | --- |
| SP-04 depends on SP-03 | Contract | gate-passed Candidate、EvaluationResult、Candidate lineage | 契約已核定；使用 fixed passed result | SP-03 實際 gate 輸出驅動 register | 僅合格 Candidate 可 promotion。 |
| SP-04 depends on SP-01 | Contract | Skill Library、dispatch attribution、Snapshot、events、segments、pause／resume、reset、UI shell | 契約已核定；使用 deterministic adapter | SP-01 的 dispatch、pause／resume、reset、三 tabs 聯合驗收 | promotion 必須進入 live scheduler。 |
| SP-04 depends on SP-01、SP-03 | Integration | passed Candidate、registration、activation、resume、dispatch attribution、retry／reset evidence | Contract fixtures 可先行 | team mode 完成完整路徑 | 驗證真實 promotion 整合。 |


## 必要行為

- `register_skill` 只接受 gate-passed Candidate；重複、未通過或狀態不明 input 必須拒絕且不改變 Skill Library。
- 註冊成功後 Skill Library 可查到 ID、規則、code、來源、驗證狀態與使用記錄；Demo mode 不提供人工 accept。
- 本版只保存後端契約列出的最小 Skill 欄位，不增加建立者、模型、成本或分類 metadata。
- `activate_skill` 記錄原因與生效時點，開新 segment；running Job 保留，下一次 dispatch 才用新 Policy。
- 成功啟用後設回播放。Live Run、policy segment、Candidate evaluation metrics 分開保存與呈現；已 dispatch Job 依 dispatch segment 歸屬，未 dispatch 即 expired 者歸 expiry 時 segment。不可用混合 live metrics 證明 Candidate 在 sandbox 外的普遍優勢。
- Adapter 操作或同步失敗時，controller 保持暫停、保留最後有效 Snapshot、顯示錯誤；安全狀態可手動 retry，狀態不明時只可 resync／reset，且不能默默切 Mock 或重送有副作用呼叫。
- reset 一律回到初始四個 Skills，不保留 Candidate、promotion 或使用歷史。

## 驗收與證據

- 測試未通過 Candidate 被拒絕且 Skill Library／Live Policy 不變；通過 Candidate 被登錄後可查詢。
- 測試 registration 與 activation events、成功 resume、Policy／segment 記錄、running Job 保留、跨切換完成與未 dispatch expiry 的 attribution，以及下一次 dispatch 生效。
- 測試 reset 清除新增 Skill、segments、usage 與 adaptation state。
- 模擬 register、activate、snapshot 失敗，驗證最後有效畫面、保持暫停、安全手動 retry、重新同步／reset 與禁止盲目重送。
- 瀏覽器驗證 Skill Library、Arena 與 Metrics 同一 Snapshot 的註冊與啟用證據，並完成與 SP-01、SP-03 的 team mode 整合。

## Ticket 設計與數量閘門

預估 Ticket 數：3 張。以下是賽前 vertical-slice 設計，不是已建立的 GitHub Ticket：

1. **從 gate-passed Candidate 到 verified Skill。** 拒絕未通過、重複或狀態不明 input；通過 input 登錄後可在 Skill Library 查到來源與 gate 證據。
2. **從 Skill activation 到恢復與下一次 dispatch。** 保留 running Job，成功後恢復 simulation clock；下一次 dispatch 使用新 Skill，並顯示原因、時間、segment、attribution 與 event。
3. **從 promotion failure 到可恢復狀態。** 失敗時保持暫停並保留最後有效 Snapshot；安全狀態可手動 retry，狀態不明則 resync 或 reset。

## 已核定產品行為

已 dispatch Job 的 segment metrics 依 dispatch 時的 Policy／segment 歸屬，跨切換後才結束亦不改歸屬；未 dispatch 即 expired 者歸 expiry 時 segment。本版 Skill 僅使用後端契約列出的最小欄位，不增加 metadata；segment metrics 不取代 sandbox gate。
