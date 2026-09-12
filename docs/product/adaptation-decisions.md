# Adaptation 待決事項與受影響工作

本文件記錄尚缺的人類決策，不是新的產品規則。原始[調查報告](sub-prd-contract-review.md)仍是未核准建議；流程改採真實切片不等於核准其 schema、責任或產品選项。各項目前均為 **待決**；未提供核可者、日期與正式權威修改前，不能標為解除。

原型依 [workflow](../../workflow.md) 與[工作分類](prototype-work-plan.md)開發；下表阻擋的是依賴答案的部分及相應正式交付，不是阻擋整組 A／B 工作。用[接口討論表](interface-discussion-board.md)收集問題、參與者與證據，不能把建議當結論。

## 決策清單

| ID | 精確缺口／建議選項 | 理由與影響 | 阻擋交付／工作 | 核可與落點 |
| --- | --- | --- | --- | --- |
| D1 | trigger 指標、門檻、觀測 window 長度／形成方式未定。選固定核准設定，或另定可設定規則；數值由人類決定。 | 不同設定會改變何時暫停及展示是否觸發。 | H2、S02-A；真實 trigger 驗證。 | main 負責人決定，寫 PRD、backend 契約。 |
| D2 | baseline Policy、workload、seed、完整非零 checkpoint、evaluation window 未定。可採明確參考基準；若改採目前 Policy 作基準，需解決嚴格改善 gate 令「目前 Policy 通過」不可達的矛盾。 | 不指定 FIFO 或其他預設；比較基準影響改善宣稱。factory 的 t=0 初始化不等於非零狀態重放。 | H3、H4、H5；S02-A/B、S03-A/B、後续 promotion 真實結果。 | 產品決策寫 PRD；重放介面需 SP-01 確認並寫契約。 |
| D3 | P95 null 與 null／數值如何比較；完整負結果、policy runtime／契約違反與外部 timeout／缺結果的分類未定。可定明確不可比較結果，或核准另一比較規則。 | 不能默認 null=0／通過；不能把評估未完成當作全部失敗。 | H3～H5；全敗、gate 與候選建立驗證。 | main 負責人決定，寫 PRD／契約與案例。 |
| D4 | SP-02 需要共用 gate，但 SP-03 寫實作 gate；sandbox、activation、register、controller seam 的底層與流程責任未完整分開。建議共用評估由 SP-02 先交付、SP-03 重用；或由其他明確 Provider 交付。 | 建議未核准。若仍由 SP-03 提供，須設計不依賴 SP-02 全敗結果的先行交付，重新核可依賴，避免循環等待。不能把新增能力直接塞給 SP-01。 | H2、H3、H5～H8；所有涉跨功能操作切片。 | 受影響 Owner（尤其 SP-01）確認，main 核可 PRD 責任／子 PRD／契約。 |
| D5 | Planner／Evaluator／Critic 輸入輸出、同步／非同步、timeout 所有權、取消、stage checkpoint 與版本 retry 未定。可重試未完成外部 stage，但不得自行把五版已失敗重設為新預算。 | 現有禁止自動 retry、沿用 adaptation ID 與禁止重做成功副作用不變；五版後可做何種手動操作需決定。 | H5、H7；S02-A 評估恢復、S02-B 控制恢復、S02-C 恢復 UI、S03 全部及 S04-C。 | main 核可契約；改五版／retry 行為需改 PRD。 |
| D6 | 子 PRD 要求整份 Live Snapshot before/after 不變，卻同時要求 adaptation stage/events 更新。可明確區分 scheduler 狀態不變與允許的控制證據變化；不可直接刪測試。另 SP-01 fixture A 的已通過 Hybrid 前提需真實來源或另行核准驗證分層。 | Snapshot 不變範圍與 Hybrid 驗收調整都需人類決定；本次保留 SP-01 原驗收，不能宣稱此缺口已解。 | H1、H3、H8；S02/S03 隔離驗證；SP-01 Hybrid 驗收證據確認。 | SP-01 負責人確認，main 核可契約／子 PRD／ACCEPTANCE。 |
| D7 | adaptation 暫停期間 inject／generate 是否拒絕，或允許但使評估失效重算，未定。 | 影響狀態一致性與使用者操作；不能擅自排隊、拒絕或重啟。 | H2、H3、H7；暫停時 workload 操作與恢復聯測。 | main 產品決策、SP-01 確認；PRD／backend。 |
| D8 | 「每個修改回傳 Snapshot」與 register 回 Skill 等逐方法回傳矛盾；playing 在 UI envelope 與 Snapshot 文句不一致。可保留逐方法結果並定義序列化讀 Snapshot，或核准統一 envelope。 | 不自行改公開回傳；需逐項定義部分成功後讀取失敗與安全恢復。 | H1、H2、H6～H8；修改操作整合。 | SP-01 確認，main 核可 backend／新操作契約。 |
| D9 | 完整比較、Candidate、feedback、promotion 的查詢／UI 插入介面及與 Snapshot 同版本關聯未定。可採 controller 同版本 evidence，或擴充 Snapshot；promotion 不可變資料與 accepted-result 查詢 schema 也待核准。 | 不增加 Skill metadata；不得僅憑 passed 布林登錄未知 code／版本。 | H4、H6、H8；S02-C、S03-A/B、S04-A/B。 | SP-01 UI／資料邊界確認，main 核可契約及相關子 PRD。 |

## 解除方式

每項決策記錄：選擇、理由、核可者／日期／證據、受影響 Owner 確認、權威文件章節與版本、驗證案例、解除的交付／Ticket。更新相關正式規格後再重驗開工條件；只回覆「同意流程」或只關閉工作單都不能解除。

已核准的是 [ADR 0003](../adr/0003-real-slice-delivery.md) 的正式交付方式與 [ADR 0004](../adr/0004-prototype-parallel-development.md) 的原型開工／試接流程。各子 PRD 的本次版本仍待獨立審查／人類內容核可，SP-01 執行連結需由現有負責人提供，不由本文件捏造。
