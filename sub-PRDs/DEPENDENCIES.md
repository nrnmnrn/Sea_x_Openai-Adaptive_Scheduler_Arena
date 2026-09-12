# 子 PRD 開發與整合順序索引

本文件只回答「何時可開始」與「何時可正式整合」。子 PRD 是其直接依賴與理由的權威；跨功能 contract 以 `docs/contracts/*.md` 為權威；產品整體 closeout 以 [ACCEPTANCE.md](../ACCEPTANCE.md) 為準。衝突時停止受影響工作，交由 main branch 負責人處理。

方向固定為「Consumer depends on Provider」。

## 兩種門檻

- **Contract 開始**：Provider 的 contract 已核定，Consumer 可依子 PRD 的 deterministic adapter／fixture 平行開發與驗證。這不是正式整合，也不可宣稱已使用 Provider 實際成果。
- **正式整合**：所有直接 Provider 已 merge 並在 `main` 驗證，再以實際成果做 team mode 整合。不得例外；未完成前不得宣稱正式整合或 closeout。

Contract 開始使工作可平行，不表示四份子 PRD 必須單純線性開發；下表的正式整合順序才受 Provider `main` 證據限制。

## 開發開始順序

| 子 PRD | Contract 核定後可開始 | 此時可做的範圍 |
| --- | --- | --- |
| [SP-01 Scheduling Arena](scheduling-arena.md) | 無上游子 PRD；本子 PRD 核可後。 | 基礎 Provider。 |
| [SP-02 Existing Skill Adaptation](existing-skill-adaptation.md) | SP-01 contract。 | SP-02 指定的 fixture／adapter 路徑。 |
| [SP-03 Candidate Evaluation Loop](candidate-evaluation-loop.md) | SP-01、SP-02 contract。 | SP-03 指定的 baseline 與 all-failed fixture 路徑。 |
| [SP-04 Skill Promotion and Recovery](skill-promotion-and-recovery.md) | SP-01、SP-03 contract。 | SP-04 指定的 scheduler adapter 與 passed-result fixture 路徑。 |

## 正式整合順序

| 次序 | Consumer 正式整合前，必須已有 `main` 驗證的 Provider |
| --- | --- |
| 1 | SP-01：無上游子 PRD。 |
| 2 | SP-02：SP-01。 |
| 3 | SP-03：SP-01、SP-02。 |
| 4 | SP-04：SP-01、SP-03。 |

Provider 證據與實際整合驗收依 [workflow.md](../workflow.md) 及各子 PRD 記錄；fixture 證據不能替代 `main` 驗證。
