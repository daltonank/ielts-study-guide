# G4-A P1 Remediation Batch Manifest

**Generated:** 2026-09-08 · **Ticket:** T1 · **Status:** manifest only — no bulk P1 corrections applied in T1.

**Batch application status (updated 2026-09-09):**

| Batch | Size | Status |
|---|---:|---|
| T2 | 104 | **APPLIED** (2026-09-09) — `scripts/qa/apply_p1_t2_fixes.py` + `scripts/qa/p1_t2_corrections.json`; input blob `414fbeac`, output blob `fe46b30a`; see `docs/G4A_P1_BATCH_STATUS.md`. |
| T3 | 104 | **APPLIED** (2026-09-09) — **102** byte corrections via `scripts/qa/apply_p1_t3_fixes.py` + `scripts/qa/p1_t3_corrections.json`; input blob `fe46b30a`, output blob `5cda209d`. SB-0425 (efficiency) excluded as copy-through (resolved via SB-0424); SB-0773 (minute2) deferred word-field fix (blocked by g2 casefold word-uniqueness) — still unresolved P1. See `docs/G4A_P1_BATCH_STATUS.md`. |
| T4 | 103 | Pending (plus deferred SB-0773 word-field fix). |

## Purpose

This manifest defines three bounded, deterministic remediation batches — **T2**, **T3**, and **T4** — that partition the outstanding P1 Ukrainian-QA findings for the vocabulary bank. Each batch is intended to be executed as its own bounded ticket so that P1 corrections land in reviewable, evenly-sized units rather than as a single unbounded bulk edit. **Ticket T1 does not apply any of these corrections to `web/vocabulary.js`;** it only produces the manifest and the machine-readable id lists. The actual `ua`/`definitionUa` corrections are deferred to tickets T2–T4.

## Derivation of the 311-id set

- The findings register (`docs/G4A_UKRAINIAN_QA_FINDINGS.csv`) records **314** findings at severity **P1**.
- **3** of those P1 items were already remediated and landed in `web/vocabulary.js` via **PR #3**: `SB-0208`, `SB-1728`, `SB-1160`.
- The unresolved P1 working set is therefore **314 − 3 = 311** findings.

## Sort and partition rule

The 311 unresolved P1 findings are sorted by the exact key **`(category ASC, id ASC)`** (category ascending, then id ascending as a tie-breaker), then partitioned **contiguously** into three batches. Because the partition is contiguous over the sorted sequence, each batch's "first id" and "last id" below are the first and last elements of that batch **in sorted order** (not lexicographic id order across the whole set).

## Batches

| Batch | Size | First id (sorted) | Last id (sorted) | Per-category counts |
|---|---|---|---|---|
| T2 | 104 | SB-0004 | SB-0463 | circular-definition 26, grammar 60, other 18 |
| T3 | 104 | SB-0530 | SB-0235 | other 31, pedagogical-accuracy 50, register 7, russianism-calque 8, semantic-fidelity 8 |
| T4 | 103 | SB-0237 | SB-1781 | semantic-fidelity 103 |

Batch totals: **104 + 104 + 103 = 311**.

## Guarantees

- The three id sets are **pairwise-disjoint** (T2 ∩ T3 = T2 ∩ T4 = T3 ∩ T4 = ∅).
- Their **union is exactly the 311 unresolved P1 ids** — no id is dropped, duplicated, or introduced.
- The partition reproduces exactly the sorted `(category, id)` sequence of the 311 unresolved P1 findings.

## Machine-readable source

The complete id arrays for each batch (not reproduced here) live in **`docs/g4a_p1_batches.json`**, alongside the `generated`, `ticket`, `note`, and `sort_key` metadata. Consumers should read that JSON rather than parsing this table.
