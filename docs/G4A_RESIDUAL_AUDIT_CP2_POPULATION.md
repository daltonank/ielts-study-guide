# G4-A Residual-Population Audit — CP2: Population + Mechanical Scans

**Audit branch:** `claude-code/4-g4a-residual-audit`  
**Baseline:** `f34f109ae5b8564e7fa10317c167a6ca728c52fd`  
**web/vocabulary.js blob:** `1c184e84e5c63e3a9f8e386af13787664a23bd66` (unchanged)  
**Gate language (unchanged):** `G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`

## Deterministic bucket partition of all 1,784 IDs

Each ID is assigned to exactly one bucket (no double counting). SB-1015 physically appears in the supplemental register but is re-opened by the PR #7 review, so it is assigned to bucket (c), not (b).

| Bucket | Definition | Count |
|---|---|---|
| (a) historical-register findings | `docs/G4A_UKRAINIAN_QA_FINDINGS.csv` | 702 |
| (b) supplemental corrected/benign (excl. SB-1015) | `docs/G4A_T5B_SUPPLEMENTAL_FINDINGS.csv` | 75 |
| (c) known-open residual (24) | SB-1015 + 23 seed-20260913 | 24 |
| (d) never-flagged clean pool | remainder | 983 |
| **TOTAL** | | **1784** |

**Residual population to audit = (c) + (d) = 1007.**

Cross-check: the PR #7 review's seed-20260913 selector reported an eligible pool of **1,006** = all IDs absent from *both* registers (historical ∪ supplemental = 778). The residual-to-audit adds SB-1015 (re-opened) to that 1,006, giving 1,007.

## The 24 known-open residual (independently listed here; re-derived in CP3)

- **SB-1015** — `retrieve`; `ua` too generic, omits back/recover sense (in supplemental register, re-opened).
- **Grammar/calque fragments (7):** SB-0009, SB-0191, SB-0295, SB-0363, SB-0371, SB-0467, SB-0724
- **POS/morphology mismatch (10):** SB-0058, SB-0306, SB-0498, SB-0749, SB-0797, SB-1635, SB-1695, SB-1707, SB-1731, SB-1735
- **Semantic/pedagogical error (6):** SB-0142, SB-0571, SB-0647, SB-0840, SB-1211, SB-1464

## Exhaustive mechanical detectors over the residual population

Detectors are conservative *candidate* signals — CP3 adjudicates each. They are deterministic and defined in `scripts/qa/residual_audit_lib.py`.

| Detector | Residual IDs hit |
|---|---|
| adjacent_repeat | 0 |
| connector_repeat | 0 |
| placeholder | 0 |
| calque_marker | 1 |
| empty_or_noncyrillic | 0 |
| pos_morphology | 0 |
| **residual IDs with ≥1 mechanical hit** | **1** |

`translationQa` still carrying the migration default "Draft — verify in context": **1006/1007** residual IDs. This is the unreviewed-stamp default, reported for transparency, **not** counted as a learner-facing defect (it is not shown to the learner as a translation).

## Interpretation

The mechanical layer is intentionally low-yield: adjacent/connector repeats are already fully remediated bank-wide (T5-B), and empty/placeholder/non-Cyrillic fields are already blocked by the deterministic gate. The substantive residual risk is **semantic/POS/calque meaning errors that are well-formed Ukrainian** — invisible to mechanical detectors — which is why CP3 applies the full linguistic rubric to every residual entry.

Artifacts: `G4A_RESIDUAL_AUDIT_CP2_ROSTER.csv` (one row per residual ID), `G4A_RESIDUAL_AUDIT_CP2_MECHANICAL.csv` (one row per mechanical hit).
