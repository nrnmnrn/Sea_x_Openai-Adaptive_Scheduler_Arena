# SP-01：Scheduling Arena

## 基本資料

- 狀態：`Unclaimed`
- 核可狀態：待人類核可；未核可前不可開始實作
- 版本：`0.1-draft`
- Owner：待比賽當日認領
- GitHub parent issue：待比賽當日認領後建立
- 核可紀錄：待填核可者、日期與連結

## 交付結果

交付一個不依賴 Agent adaptation 也能完整展示與驗收的排程 Arena：使用者控制可重現的單 worker 模擬、注入 workload，並在三個 Gradio tabs 看見同一 Snapshot 的排程過程、metrics、實際 policy code 與初始 Skill Library。

## 範圍

- 實作 Job 驗證、五種 Policy 定義（Hybrid 只能作未登錄的可驗證候選規則）、生命週期、deadline、事件順序、單 worker、不可搶占、reset、seed、20 筆名額與 deterministic `advance`。
- 產生契約要求的 Snapshot、排程 events、整局 metrics、series、初始 Skills 與 developer-mode 的已驗證 Skill 套用入口。
- 實作 Gradio 共用 shell 與資料來源標示；Scheduling Arena 的播放、暫停、單步、倍速、reset、inject 與 SVG 狀態呈現。
- 提供 adaptation 使用的自動 pause／resume seam：暫停時 simulation clock、Job 進度、arrival、deadline 與 dispatch 均不前進；成功訊號後設回播放。
- 實作 Metrics & Code 的整局 cards、趨勢、實際排序 code、Policy diff；實作 Skill Library 的初始 Skill 閱讀、預覽與來源／使用記錄呈現。
- 以 1440×900、1280×720 做可讀性與操作驗收；動畫只能插補 Snapshot，不可成為狀態來源。

## 不在範圍

不負責 trigger、既有 Skill evaluator、Candidate 生成／評估／晉升。不得預先建立 Hybrid Skill、Candidate 或 adaptation UI state。不得把 local 結果冒充 team backend。

## PRD requirement coverage

| PRD 要求 | 本子 PRD 如何覆蓋 | 驗收證據 |
| --- | --- | --- |
| `PRD.md`「名詞與產品邊界」 | 僅恢復 FIFO、SJF、Priority、EDF；Hybrid 不作初始 Skill；排除未核定 scope。 | R02、R20；初始 Skill、reset 與範圍審查。 |
| `PRD.md`「排程與模擬規則」 | 覆蓋 Job、狀態、worker、deadline、Policy、event、`advance`、seed、inject、20 筆上限與 reset。 | R01–R03；共同 fixtures A–D 及排程契約測試。 |
| `PRD.md`「Metrics、Snapshot 與 Adapter」 | 提供可序列化 Snapshot、events、metrics、series、revision 與 scheduler adapter。 | R04、R06、R17–R18；contract、session 與 revision 測試。 |
| `PRD.md`「Demo 與 Developer mode」 | 提供共用 UI shell、控制、來源標示、SVG、Metrics & Code、Skill Library 及尺寸驗收。 | R04–R06、R20；瀏覽器與 backend source 證據。 |
| `PRD.md`「90 秒短展示與 progression run」 | 支援短展示及多輪 progression 的 clock pause／resume、同 Snapshot、timeline 與 live／sandbox 來源標示。 | R19–R20；team mode 短展示與 progression 紀錄。 |

## 介面與直接依賴

| 方向（Consumer depends on Provider） | 類型 | 需要的輸出或 contract | 可開始條件 | 整合條件 | 理由 |
| --- | --- | --- | --- | --- | --- |
| `None` | None | 無上游子 PRD | 本子 PRD 核可後可開始 | 下游依共同 contract 整合 | SP-01 是基礎 Provider。 |

本子 PRD提供[後端契約](../docs/contracts/backend-contract.md)所定義的 SchedulerBackendAdapter、Snapshot、Job、Skill、Event、metrics、segments、pause／resume seam 與 UI shell。下游 SP-02 以 **Contract** 依賴上述輸出；契約凍結後可用 deterministic adapter／fixture 平行工作。與實際 Arena 的聯合驗收另為 **Integration** 依賴，須等本子 PRD 完成。

## 必要行為

- 預設 `seed=42`、八筆可重現 Jobs、初始 FIFO；reset 新建 run 並恢復四個初始 Skills。
- 同時刻事件順序及全部 Policy tie-break 必須符合總 PRD。不同 `advance` 切分不可影響結果。
- `inject` 必須整批原子；無效資料、過去 arrival、ID 衝突、超過名額不可留下部分資料或消耗 RNG。
- pending／running／scheduled／completed／expired 的顯示與後端 Snapshot 一致。worker 閒置原因須可讀。
- Arena、Metrics & Code、Skill Library 同一 UI 更新中使用同一 `run_id` 與 `snapshot_version`；切 tab 不得新增 timer 或推進狀態。
- Demo mode 隱藏手動 Policy 切換與套用；Developer mode 才可測試已驗證 Skill。資料來源與 Mock 標籤始終可見。
- 初始為暫停、1×。單步固定推進一模擬秒、不乘倍速，且停止連續播放；reset 後仍保留使用者選定倍速。
- 使用約 200 ms 的單一更新來源；播放每次推進 `0.2 × speed` 模擬秒。暫停停止推進與插值；切 tab 不新增 timer，也不自動暫停。
- adaptation pause 必須鎖定播放與單步推進，但仍允許 reset、查看三個 tabs 及 adaptation 證據；成功後設回播放，失敗時保持暫停。
- active Job 依 running、pending、scheduled，再依 arrival、ID 排列。約 420 px 的 Job 區獨立垂直捲動，顯示全部未結束 Jobs，更新時保留捲動位置。
- scheduled 以灰色與抵達倒數呈現；pending 以綠色與可行性文案呈現；running 以黃色沿處理路徑呈現；completed／expired 移至保留結束時間的歷史。worker idle 須區分尚未到達、全部不可行或工作皆結束。
- 等待位置為 `clamp((now-arrival)/(deadline-arrival), 0, 1)`；處理進度為 `clamp((now-started_at)/processing_time, 0, 1)`。priority 不得改變等待位置。
- Metrics & Code 依序顯示 cards、三層趨勢、實際執行 code 與最近一次不同 Policy 的 diff；趨勢顯示最近 60 個事件取樣及目前點。Skill 下拉只改預覽，Developer mode 的套用才可切換；uses 只計實際 dispatch。
- UI 只在已接受 Snapshot 間插補動畫，不向未知未來外推，亦不以動畫判定完成。全局結束後不自動 reset；尚有名額時仍可 inject。

## 驗收與證據

- 使用後端契約的共同 deterministic fixtures A–D 驗證 FIFO、SJF、Priority、EDF、通過 gate 後的 Hybrid、deadline、同時刻事件順序、metrics 與不搶占。
- 比較大步與小數分段 `advance` 的 Job、events、metrics；驗證 P95、throughput、名額、reset、RNG 與輸入拒絕。
- 以兩個 factory 實例驗證 session 隔離、防禦性 Snapshot、JSON 可序列化與舊 revision 拒收。
- 瀏覽器驗證控制項、20 筆捲動、tab 切換、動畫、畫面尺寸及同 Snapshot 顯示。
- 驗證 adaptation 前後 simulation time 與 running Job 進度在暫停期間不變，成功 resume 後由同一 Snapshot 後續推進；progression run 的多輪 pause／resume 不建立額外 timer。
- team 模式必須實際呼叫指定 factory；載入失敗明確錯誤、不 fallback。local 僅可作明確開發／備援模式。

## Ticket 設計與數量閘門

預估 Ticket 數：3 張。以下是賽前 vertical-slice 設計，不是已建立的 GitHub Ticket：

1. **完成可重現的 Scheduler Run。** 使用者以固定 Jobs 執行一局，從 Arena 看見 Job 狀態、dispatch、events 與 metrics；共同 fixtures 驗證 Policy、deadline、`advance`、reset、seed 與 inject。
2. **完成 workload 控制與排程證據。** 使用者可播放、暫停、單步、調速、加入單筆或 Flash Sale；adaptation 可自動暫停並在成功後恢復，同一畫面可核對容量、worker、Policy code 與拒絕原因。
3. **完成 team/local 的三-tab 展示。** 依明確 CLI 啟動指定 backend；三個 tabs 顯示同一 Snapshot、來源、Skill 與 metrics，並通過 session、捲動、動畫及兩種尺寸驗收。

## 已核定產品行為

已 dispatch Job 的 segment metrics 依 dispatch 時寫入的 Policy／segment 歸屬；跨越 Policy 切換才結束仍計入原 dispatch segment。從未 dispatch 就 expired 的 Job 歸於 expiry 時生效的 segment，且 `dispatched_policy_id` 保持 null。此子 PRD 必須保留欄位與可驗證的 attribution 證據。
