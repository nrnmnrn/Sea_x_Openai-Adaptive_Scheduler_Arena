# SP-03：Candidate Evaluation Loop

## 基本資料

- 狀態：`Unclaimed`
- 核可狀態：2026-09-12 本次對話使用者已採納四組規格方案；本草案可作權威同步基準。真實 SP-01／SP-02 Provider seam、版本與整合證據尚未確認，只阻擋受影響操作、正式交付與完整驗收。
- 版本：`0.4-draft`
- Owner：待比賽當日認領
- GitHub parent issue：待比賽當日認領後建立
- 核可紀錄：本次對話使用者，2026-09-12；使用者兼任 SP-01 接口確認人與開發版 integrator，姓名與實際版本／證據待 Ticket 據實記錄

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

## 原型開發分類

依[工作分類表](../docs/product/prototype-work-plan.md)在原 Ticket 內先做 A 獨立或 B 邊做邊談的內部部分，開始前記錄範圍、接口 ID 及未驗證項，不等待整份契約凍結。C 僅停止依賴未決答案的部分。接口討論與決策紀錄集中於[共用表單](../docs/product/interface-discussion-board.md)。開發版試接可使用可辨識的真實未合併版本，條件依 [workflow](../workflow.md)；下表整合條件均指正式交付，並非開發版試接門檻。

## 介面與直接依賴

| 方向（Consumer depends on Provider） | 類型 | 需要的輸出或 contract | 可開始條件 | 整合條件 | 理由 |
| --- | --- | --- | --- | --- | --- |
| SP-03 depends on SP-02 | Contract | run／window 唯一 TriggerResult、既有 Skill EvaluationResult、all-failed 判定、active adaptation context | A／B 依原型分類先行；C 的受影響操作先決定，真實試接依 workflow | S02-A merge 並在 main 驗證；真實完整全敗輸出驅動 loop | Candidate 只能在全部既有 Skills 失敗後建立。 |
| SP-03 depends on SP-01 | Contract | sandbox、baseline Snapshot、metrics、events、pause／resume、手動恢復 UI 插入點 | A／B 依原型分類先行；C 的受影響操作先決定，真實試接依 workflow | S01-FULL main 證據及核准的真實 sandbox／pause 能力 | Candidate 必須在 scheduler contract 上安全評估。 |
| SP-03 depends on SP-01、SP-02 | Integration | 真實 trigger、all-failed context、pause／resume、retry、sandbox／live 比較 | A／B 依原型分類先行；C 的受影響操作先決定，真實試接依 workflow | team mode 完成聯合驗收 | 驗證真實 all-failed 串接。 |

本子 PRD 向 SP-04 提供 gate-passed Candidate、完整 EvaluationResult 與不可變 promotion input。

## I01–I09 介面交付對照與核可門檻

本表只將本功能必須消費或提供的交接，對照至 [交接契約](../docs/contracts/adaptation-contract.md)、[待決清單](../docs/product/adaptation-decisions.md) 與 [接口討論表](../docs/product/interface-discussion-board.md)。資料型別、方法與公開 schema 仍只由 [後端契約](../docs/contracts/backend-contract.md) 定義；下表不新增欄位，也不把討論提案當成已核可規則。

| 接口問題 | SP-03 交付／消費邊界 | 對應交接與切片 | 正式交付前的最低門檻 |
| --- | --- | --- | --- |
| I01 | 消費同一 session／run 的已接受 Snapshot、revision 與錯誤狀態；不持有或改寫 controller。 | H1；S03-A～C | D6、D8 已依權威文件核可；SP-01 確認所需 read/controller seam，並有兩 session、舊 generation／run 拒收的真實證據。 |
| I02 | 只在已暫停且唯一的 adaptation context 中工作；SP-03 不決定 trigger 或 live 操作控制。 | H2、H7；S03-A、S03-C | D1、D4、D7、D8 對受影響操作已決；真實 trigger 的 pause、去重與 reset 舊結果拒收已驗證。 |
| I03 | 對 Candidate 使用與既有 Skill 相同的已核可 baseline 與 gate；不自行指定 evaluator Provider。 | H3、H5；S03-A、S03-B | D2～D4、D6、D7 已決，且 Provider／Consumer 確認同一 context、baseline、window、負結果分類與隔離驗證。 |
| I04 | 消費真實可重放 checkpoint，於 sandbox 評估並限制 evidence 變更；不改變 SP-01 的 sandbox 責任。 | H3、H8；S03-A | D2、D4、D6、D7 已決；SP-01 確認 checkpoint seam，真實 running／scheduled state、RNG 與 live-before/after 證據通過。 |
| I05 | 驅動 Planner／Evaluator／Critic stage，安全停止及手動恢復只依已核可 checkpoint。 | H5、H7；S03-B、S03-C | D4、D5、D7、D8 已決；每個 stage 的 timeout、取消、遲到回應、部分成功與 state-uncertain 行為有真實證據。 |
| I06 | 提供給 SP-04 的僅是通過 gate 的 Candidate、EvaluationResult 與既有契約所需的不可變對應；不登錄或啟用。 | H6；S03-A、S03-B | D4、D8、D9 已決；SP-03／04 確認 exact candidate/version/code/result 的可信交接及錯版本拒絕案例。 |
| I07 | 只消費 SP-02 的完整 all-failed 集合；不以單一布林值或 incomplete/error 開啟 Planner。 | H4；S03-A | D2～D4、D9 已決；真實集合含預期 ID、每項結果、baseline/window 關聯，並驗證缺失、重複、pass、timeout 均不得啟動 Planner。 |
| I08 | 提供 Candidate、gate、feedback 與錯誤 evidence 給既有三-tab UI；不建立第二個 UI envelope。 | H8；S03-A～C | D4、D6、D8、D9 已決；同一已接受版本的三-tab evidence、source/Mock 標示與最後有效畫面有真實證據。 |
| I09 | 只使用通過真實 gate 的 Candidate 作為 promotion 前交接；不將 Hybrid fixture 或固定 passed 結果當成 Candidate loop 證據。 | H3、H6；S03-A | D2～D4、D6 已決，且 SP-01 Owner 確認 fixture 影響；真實 gate→H6 交接版本可追溯。 |

每一 I 列未滿足時，只停止該列所對應的 C 操作、驗收案例與正式交付；不依賴該答案的 A／B 內部工作及其他已滿足門檻的交付可依[工作分類](../docs/product/prototype-work-plan.md)繼續。接口討論表中的提案必須先回寫並核可 PRD、子 PRD 或 contract，才可移除相應門檻。

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

正式交付必須再具備下列可觀察案例；它們引用既有 contract，並非新 schema 或數值規則：

| 案例 | 輸入與預期結果 | 所屬交付 |
| --- | --- | --- |
| 完整失敗才建立 | H4 的完整既有 Skill 負結果集合使 Planner 僅建立一版 Candidate；任一 pass、缺項、重複、未知 ID、incomplete 或外部錯誤均不建立 Candidate。 | S03-A |
| 同 context 的隔離評估 | 同一已核可 baseline、seed、checkpoint 與 window 評估 Candidate；保留 gate 原因，且 live scheduler state 不因 sandbox 改變。 | S03-A |
| passed 的可追溯交接 | 通過 gate 的 exact Candidate 版本、code、EvaluationResult 與 context 關聯可交給 SP-04；錯版本、缺結果或未通過均拒絕交接且不改 Live Run。 | S03-A |
| 拒絕至上限 | Candidate 被拒或契約違反時留下可讀 feedback 並進入下一版；第五版後記錄 `adaptation_failed`、維持暫停與原 Policy。 | S03-B |
| 受控外部故障 | timeout、schema、服務錯誤、取消後遲到回應與部分成功皆記 `adaptation_error`、保留最後有效畫面且不自動 retry／Mock；僅 contract 可證明安全時可用原 adaptation ID 手動 retry。 | S03-C |
| 同版本呈現與重置 | 三 tabs 顯示相同已接受版本的 Candidate evidence；過時 generation/run 回應被拒絕，`state_uncertain=true` 僅顯示 resync 或 reset。 | S03-C |

## Ticket 設計與數量閘門

預估 Ticket 數：3 張。以下為已採納的真實切片設計，不代表已建立 GitHub Ticket；交付對照見下節：

1. **從 all-skills-failed 到單版 Candidate 結果。** 消費失敗 context，產生唯一 Candidate，在隔離 sandbox 執行 gate，並顯示 lineage 與比較證據。
2. **從 Candidate 拒絕到 Critic loop 結束。** 保存 feedback、產生後續版本，於通過或第五版失敗時留下完整可見結果，且不修改 Live Run。
3. **從外部錯誤到安全手動恢復。** timeout、schema 或服務錯誤時保持暫停、保留最後有效 Snapshot 並顯示來源與錯誤；安全狀態可手動 retry，狀態不明只可 resync 或 reset。

## 已核定產品行為

外部 adapter 錯誤統一記錄 `adaptation_error`，UI 顯示失敗 stage 與原因。系統不得自動 retry；僅在狀態可證明安全時提供手動 retry，狀態不明時只提供 resync 或 reset，且不得自動切換 Mock。

## 真實切片交付與開始條件

採 [workflow](../workflow.md) 的 SP-02～04 切片模式；以下 ID 是規格交付識別，不是已發佈 Ticket。每張 Ticket 自己的 branch／PR 經人類授權 merge、main 驗證後才結案；整份功能仍須全部驗收。相關契約見 [H1～H8](../docs/contracts/adaptation-contract.md)與已採納的 [D1～D9](../docs/product/adaptation-decisions.md)。

| 交付 ID | 提供的真實結果 | 正式整合所需上游 | 使用者 | 待決 blocker | 驗證方式 |
| --- | --- | --- | --- | --- | --- |
| S03-A | 真實全敗到單版 Candidate 與 passed 交接（H3～H6、H8） | S01-FULL、S02-A 的 H4；SP-02 共用評估 Provider | SP-04 使用 H6 | checkpoint／evaluator／storage seam 證據 | 真實全敗才呼叫 Planner；sandbox gate、lineage、不可變結果；外部錯誤至少安全停止，不將未完成視為 passed。 |
| S03-B | 拒絕到 Critic loop 結束（H5、H6） | S01-FULL、S02-A、S03-A | SP-04 與完整 SP-03 驗收 | adapter／controller seam 證據 | 真實 feedback／後續版本、通過或第五版失敗，保持 Live Policy；含各 stage 安全停止。 |
| S03-C | 外部錯誤到安全手動恢復（H7、H8） | S01-FULL、S02-A、S03-A、S03-B | 各候選 stage 與完整功能驗收 | adapter／recovery／UI seam 證據 | 真實 adapter 受控 timeout/schema 故障，安全 retry、不重做成功副作用、resync/reset；不能靠 Mock fallback。 |

- 原型開工依上述 A／B／C 分類；已採納方案不取代真實 Provider seam，未接真實上游不宣稱相應結果通過。
- 正式整合時，表列上游均需 merge 並在 main 驗證；S01-FULL 指 SP-01 整份完成，不要求其提前拆分。
- 每個早期切片都要包含安全停止與自身副作用保護；後續恢復切片補完整手動恢復，不是允許前段省略錯誤處理。
- 本次不降低原驗收。D4／D6 的採納責任與隔離範圍已同步；SP-01 或其他 Provider 未提供真實 seam 時，僅停止相應交付。
- 完整子 PRD 結案仍需所有直接 Provider 的完整所需成果與全流程驗收；切片提早交付不代表略過其他路徑。

## 已採納交接方案與真實 seam 門檻

下列方案已由 2026-09-12 本次對話使用者採納並同步至 PRD／contract；[接口討論表](../docs/product/interface-discussion-board.md)只記協調與證據。它們可作實作基準，但沒有真實 Provider seam、版本或驗證證據時，只能停止受影響操作與正式交付。

| 範圍 | 已採納方向 | 尚待真實證據 |
| --- | --- | --- |
| I01／I02 | controller 以同一 session、run、adaptation 與 context 關聯接受背景 stage 結果；UI refresh 不得使合法 pending 結果失效，reset 必須令舊 run 結果失效。有效 trigger 在取得 paused checkpoint 的同一序列化控制區段內停鐘；active adaptation 期間拒絕指定 live 操作。 | SP-01 controller/read seam；兩 session、重複 trigger、refresh 後合法結果與 reset 後舊結果拒收。 |
| I03／I07 | SP-02 提供共用 evaluator 與完整 immutable all-failed comparison，SP-03 重用同一 gate；FIFO 作固定 reference baseline，P95 不可比較視為不通過，incomplete/error 不得視為全敗。 | SP-02 Provider 版本、全敗交接與 gate 實測。 |
| I04 | 以非零 checkpoint clone 重放，保留 running／scheduled state 與 RNG；Live Run／Snapshot 只允許 adaptation evidence 變化，sandbox 隔離執行可產生評估結果但不得回寫 live。任意 policy code 由獨立可終止執行環境隔離。 | SP-01 clone／runner seam 與安全實作證據。 |
| I05 | 每個外部 stage 綁定既有身分關聯並用 request identity 拒絕取消後遲到結果；未完成 stage 可安全 retry，已完成副作用先查詢再繼續。Planner／Critic timeout 為 60 秒、Evaluator 為 10 秒 wall-clock。 | adapter、controller 與 recovery 實測；identity／timeout 已在 backend 定義。 |
| I06／I08／I09 | SP-03 保存 accepted Candidate 與 evaluation 的可信不可變關聯，SP-04 依此登錄；既有三 tabs 以同版本 evidence 顯示。Hybrid fixture 仍須真實 gate/register 來源，不可固定 passed。 | storage/UI/fixture seam、SP-03→04 交接與瀏覽器證據。 |

真實 seam 未備時的停止點：S03-A 不得宣稱真實 all-failed→passed 或交付 H6；S03-B 不得宣稱完整 loop；S03-C 不得執行未證明安全的 timeout、取消或 retry 操作。A／B 內部原型範圍仍可依上方分類進行，並在 Ticket 留下排除範圍與未驗證項。
