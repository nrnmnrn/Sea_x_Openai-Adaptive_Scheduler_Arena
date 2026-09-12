# SP-04：Skill Promotion and Recovery

## 基本資料

- 狀態：`Unclaimed`
- 核可狀態：2026-09-12 本次對話使用者已採納四組規格方案；本草案可作權威同步基準。真實 SP-01／SP-03 Provider seam、版本與整合證據尚未確認，只阻擋受影響操作、正式交付與完整驗收。
- 版本：`0.4-draft`
- Owner：待比賽當日認領
- GitHub parent issue：待比賽當日認領後建立
- 核可紀錄：本次對話使用者，2026-09-12；使用者兼任 SP-01 接口確認人與開發版 integrator，姓名與實際版本／證據待 Ticket 據實記錄
- 交付模式：SP-04 真實切片；整份功能尚未核可
- 局部核可範圍：僅 [工作分類表](../docs/product/prototype-work-plan.md) 所列 A／B 內部工作；實際範圍、相關 I 編號、排除範圍與未驗證項仍須在已核可 Ticket 據實記錄

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

## 原型開發分類

依[工作分類表](../docs/product/prototype-work-plan.md)在原 Ticket 內先做 A 獨立或 B 邊做邊談的內部部分，開始前記錄範圍、接口 ID 及未驗證項，不等待整份契約凍結。C 僅停止依賴未決答案的部分。接口討論與決策紀錄集中於[共用表單](../docs/product/interface-discussion-board.md)。開發版試接可使用可辨識的真實未合併版本，條件依 [workflow](../workflow.md)；下表整合條件均指正式交付，並非開發版試接門檻。

| 交付 | A：可獨立工作 | B：可先做的內部邊界 | C：核可前不得執行的操作 | 相關 interface issues／未驗證項 |
| --- | --- | --- | --- | --- |
| S04-A | 以既有 Candidate／Skill 最小欄位準備 code、來源與結果呈現。 | 合格結果的檢查流程與 Library 接點，外部資料停在局部 boundary。 | 讀取或登錄真實 Candidate、建立可信關聯、修改 Library。 | I01、I06～I08；真實 passed、版本關聯與同版本 evidence 未驗證。 |
| S04-B | 啟用原因、segment 與錯誤證據的組內呈現。 | 接既有 activation／resume／reset 入口並規劃正常與失敗案例。 | 真實 activate、resume 或改寫 live state。 | I02、I05、I08；控制責任、部分成功與讀取回復未驗證。 |
| S04-C | 安全動作與最後有效畫面的呈現結構。 | 受控故障案例的接線邊界。 | 依未定 checkpoint 判定 retry，或重送 register／activate。 | I01、I05、I08；state-uncertain 分類與安全 recovery 未驗證。 |

下節的已採納方案不擴張 A／B 的範圍，也不建立新的公開 schema；資料形狀、責任與回傳規則以已同步的[後端契約](../docs/contracts/backend-contract.md)與[交接契約](../docs/contracts/adaptation-contract.md)為準。

## 介面與直接依賴

| 方向（Consumer depends on Provider） | 類型 | 需要的輸出或 contract | 可開始條件 | 整合條件 | 理由 |
| --- | --- | --- | --- | --- | --- |
| SP-04 depends on SP-03 | Contract | gate-passed Candidate、EvaluationResult、Candidate lineage | A／B 依原型分類先行；C 的受影響操作先決定，真實試接依 workflow | S03-A merge 並在 main 驗證；真實 gate 輸出驅動 register | 僅合格 Candidate 可 promotion。 |
| SP-04 depends on SP-01 | Contract | Skill Library、dispatch attribution、Snapshot、events、segments、pause／resume、reset、UI shell | A／B 依原型分類先行；C 的受影響操作先決定，真實試接依 workflow | SP-01 的 dispatch、pause／resume、reset、三 tabs 聯合驗收 | promotion 必須進入 live scheduler。 |
| SP-04 depends on SP-01、SP-03 | Integration | passed Candidate、registration、activation、resume、dispatch attribution、retry／reset evidence | A／B 依原型分類先行；C 的受影響操作先決定，真實試接依 workflow | team mode 完成完整路徑 | 驗證真實 promotion 整合。 |


## 必要行為

- `register_skill` 只接受 gate-passed Candidate；重複、未通過或狀態不明 input 必須拒絕且不改變 Skill Library。
- 註冊成功後 Skill Library 可查到 ID、規則、code、來源、驗證狀態與使用記錄；Demo mode 不提供人工 accept。
- 本版只保存後端契約列出的最小 Skill 欄位，不增加建立者、模型、成本或分類 metadata。
- `activate_skill` 記錄原因與生效時點，開新 segment；running Job 保留，下一次 dispatch 才用新 Policy。
- 成功啟用後設回播放。Live Run、policy segment、Candidate evaluation metrics 分開保存與呈現；已 dispatch Job 依 dispatch segment 歸屬，未 dispatch 即 expired 者歸 expiry 時 segment。不可用混合 live metrics 證明 Candidate 在 sandbox 外的普遍優勢。
- Adapter 操作或同步失敗時，controller 保持暫停、保留最後有效 Snapshot、顯示錯誤；安全狀態可手動 retry，狀態不明時只可 resync／reset，且不能默默切 Mock 或重送有副作用呼叫。
- reset 一律回到初始四個 Skills，不保留 Candidate、promotion 或使用歷史。

## 驗收與證據

| 案例 | 真實輸入與可觀察結果 | 必要證據 |
| --- | --- | --- |
| 合格登錄 | 真實上游 passed Candidate 的 ID、版本、code 與結果為同一已接受紀錄時才可登錄；Library 可讀到既有最小 Skill 欄位。 | S03-A 版本、H6 凍結版本、register 結果與讀取證據。 |
| 拒絕且無副作用 | 未通過、缺結果、版本或 code 不符、重複登錄、不可判定的結果全部被拒絕；Skill Library 與 Live Policy 不變。 | 拒絕原因、操作前後防禦性 Snapshot／Library 比對。 |
| 啟用與歸屬 | 已登錄 Skill 建立 `policy_activated` 和新 segment；running Job 保留，下一次 dispatch 才使用新 Policy；跨切換完成和未 dispatch expiry 依 PRD 歸屬。 | event、segment、Job attribution 與 resume 後 dispatch 的真實 scheduler 證據。 |
| 三 tab 證據 | Arena、Metrics & Code、Skill Library 顯示同一已接受 Snapshot 的註冊、gate、live／sandbox 分隔、來源與啟用原因。 | 兩 session、過時回應與 1280×720／1440×900 瀏覽器案例。 |
| 受控失敗與恢復 | register、activate 或後續讀取失敗時保持暫停和最後有效畫面；只有已核准為安全的 stage 可手動 retry，未知狀態只 resync／reset。 | 每個失敗 stage 的錯誤分類、唯一安全動作、retry identity 與「未重送已完成 mutation」證據。 |
| reset | reset 後只剩 FIFO、SJF、Priority、EDF，並清除 Candidate Skills、segments、usage 與 adaptation 狀態；舊 run 回應不得套用。 | reset 後 Snapshot／Library、generation／run 拒收案例。 |
| Hybrid fixture 前置 | 固定 Hybrid fixture 僅在真實 Candidate gate 與 register 證據存在時使用；其結果不得冒充 Planner 來源或完整流程。 | exact Candidate/version/code → gate → register → fixture 的鏈結與反例拒絕。 |

正式驗收另需與 SP-01、SP-03 的 team mode 真實整合；固定資料、Mock、或未合併 prototype 均不能取代上述上游與 `main` 證據。

## 已採納介面決策與真實 seam 門檻

下列是本功能依 I01–I09 的已採納規則，已同步至 PRD／contract，不改變 SP-01 責任。I03、I04 與 I07 的 gate／sandbox／全敗集合由上游提供；SP-04 只消費其已凍結、可追溯的結果，不能自行實作或放寬它們。真實 Provider seam、版本與驗證證據未備時，只停止相應操作與正式交付。

| I 項 | SP-04 的已採納交付或驗收規則 | seam 未證時停止的範圍 |
| --- | --- | --- |
| I01 | controller 只接受同一已接受 Snapshot 版本的 Library 與 evidence；讀取失敗且狀態不明時不重送先前 mutation。驗收兩 session、過時 generation／run 與 read failure。 | 真實讀取接線、同版本三-tab 證據與讀取後 recovery。 |
| I02 | 只有成功 activation 才恢復播放；啟用不搶占，下一次 dispatch 才生效。active adaptation 期間拒絕指定 live 操作，control-plane 依既有 contract 分工。 | 真實 activate／resume 與暫停中的控制聯測。 |
| I03 | promotion 只接受同一凍結 gate 的完整 passed 結果；不以單一 `passed` 布林或 live metrics 取代 baseline、sandbox 與負結果證據。 | 對 gate 語意、baseline、null 或 timeout 分類有依賴的登錄。 |
| I04 | promotion 不得把 sandbox 的 clone、例外或惡意 code 寫回 Live Run；需由 Provider 證明非零 checkpoint 隔離。 | 任何將 sandbox 安全或重放結果當成登錄前置的驗收。 |
| I05 | request／response 與 recovery 必須能辨識同一 adaptation、Candidate 版本及 operation；已成功 register／activate 先查詢再續行，絕不自動重送。timeout、取消與安全 retry checkpoint 依既有 contract。 | 真實 retry、部分成功、timeout／遲回與取消處理。 |
| I06 | SP-03 提供不可變的已接受 Candidate／EvaluationResult 關聯；SP-04 以受信任查詢取得它，拒絕 caller 重傳或不符的 code、版本、結果，成功 register 仍只回既有最小 Skill 欄位。 | 真實 register、duplicate recovery 與其公開查詢／回傳接縫。 |
| I07 | 上游 Candidate 必須可追溯至完整既有 Skill 比較；缺失、重複、未知 ID、incomplete/error 或任一 pass 都不得被 SP-04 解讀為可 promotion。 | 對全敗鏈與 context identity 有依賴的 promotion 驗收。 |
| I08 | 三 tabs 以同一接受版本呈現 registration、gate、live／sandbox 分隔與錯誤；最後有效整套畫面只加 backend 決定的安全動作，UI 不自行判斷 retry。 | evidence envelope、UI 插入點、read-failure 畫面與 responsive 聯測。 |
| I09 | Hybrid 固定 fixture 是驗證消費者：先有真實 gate→register 鏈才可執行，不能固定 passed、人工 accept 或以 fixture 取代完整 Planner 路徑。 | Hybrid fixture 的真實來源證據與其前置交付順序。 |

解除每一列的門檻為：受影響 Provider／Consumer（涉及 SP-01 時含其 Owner）提供真實 seam、版本與驗證證據，以及上述正常、拒絕、錯誤、state-uncertain 案例均可驗收。未同時滿足時，僅可做前節列出的 A／B 內部工作，不能結案相應正式 Ticket。

## Ticket 設計與數量閘門

預估 Ticket 數：3 張。以下為已採納的真實切片設計，不代表已建立 GitHub Ticket；交付對照見下節：

1. **S04-A：從已接受 gate 結果到 verified Skill。** 真實 immutable Candidate／結果鏈驅動登錄；拒絕未通過、缺結果、錯版本／code 與重複輸入，並在 Skill Library 顯示既有最小欄位與 gate 證據。I06、I07、I08 及 H6 凍結前，只限 A／B 內部範圍。
2. **S04-B：從 Skill activation 到恢復與下一次 dispatch。** 保留 running Job，成功後恢復 simulation clock；下一次 dispatch 使用新 Skill，並顯示原因、時間、segment、attribution 與 event。I01、I02、I05、I08 及 H2／H6～H8 凍結前，不修改正式 live state。
3. **S04-C：從 promotion failure 到可恢復狀態。** 失敗時保持暫停並保留最後有效 Snapshot；僅已核准安全的 stage 可 retry，狀態不明則 resync 或 reset。I01、I05、I08 及 H7／H8 凍結前，不發出或重送 mutation。

## 已核定產品行為

已 dispatch Job 的 segment metrics 依 dispatch 時的 Policy／segment 歸屬，跨切換後才結束亦不改歸屬；未 dispatch 即 expired 者歸 expiry 時 segment。本版 Skill 僅使用後端契約列出的最小欄位，不增加 metadata；segment metrics 不取代 sandbox gate。

## 真實切片交付與開始條件

採 [workflow](../workflow.md) 的 SP-02～04 切片模式；以下 ID 是規格交付識別，不是已發佈 Ticket。每張 Ticket 自己的 branch／PR 經人類授權 merge、main 驗證後才結案；整份功能仍須全部驗收。相關契約見 [H1～H8](../docs/contracts/adaptation-contract.md)與已採納的 [D1～D9](../docs/product/adaptation-decisions.md)。

| 交付 ID | 提供的真實結果 | 正式整合所需上游 | 使用者 | 待決 blocker | 驗證方式 |
| --- | --- | --- | --- | --- | --- |
| S04-A | 真實 gate-passed 到 verified Skill（H6、H8） | S01-FULL、S03-A 的 H6；底層 register Provider | Skill Library、S04-B | register/storage/UI seam 證據 | 真實接受的 candidate/version/code/result 對應、拒絕與重複登錄；含部分失敗安全停止。 |
| S04-B | 啟用、恢復與下次 dispatch（H2、H6～H8） | S01-FULL、S03-A、S04-A | Live Run、完整功能驗收 | activation/controller/UI seam 證據 | 真實啟用與 resume、segment、attribution、running Job；同步失敗不盲目重送。 |
| S04-C | promotion failure 到可恢復狀態（H7、H8） | S01-FULL、S03-A、S04-A、S04-B | 完整 SP-04 與產品驗收 | recovery/UI seam 證據 | 真實 register/activate/snapshot 受控失敗、安全 retry、未知狀態 resync/reset；最後有效畫面。 |

- 原型開工依上述 A／B／C 分類；已採納方案不取代真實 Provider seam，未接真實上游不宣稱相應結果通過。
- 正式整合時，表列上游均需 merge 並在 main 驗證；S01-FULL 指 SP-01 整份完成，不要求其提前拆分。
- 每個早期切片都要包含安全停止與自身副作用保護；後續恢復切片補完整手動恢復，不是允許前段省略錯誤處理。
- 本次不降低原驗收。D4／D6 的採納責任與隔離範圍已同步；SP-01 或其他 Provider 未提供真實 seam 時，僅停止相應交付。
- 完整子 PRD 結案仍需所有直接 Provider 的完整所需成果與全流程驗收；切片提早交付不代表略過其他路徑。
