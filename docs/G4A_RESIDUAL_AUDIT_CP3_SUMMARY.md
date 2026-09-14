# G4-A Residual-Population Audit — CP3: Full-Rubric Findings Inventory

**Audit branch:** `claude-code/4-g4a-residual-audit`  
**Baseline:** `f34f109ae5b8564e7fa10317c167a6ca728c52fd`  
**web/vocabulary.js blob:** `1c184e84e5c63e3a9f8e386af13787664a23bd66` (unchanged)  
**Gate language (unchanged):** `G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`

Complete inventory: **1007** residual IDs, each dispositioned exactly once (coverage proven mechanically by `tests/g4a_residual_audit_coverage.py`).

## Method and depth (honest)

AI full-rubric linguistic read (grammar/calque, POS/morphology, semantic/pedagogical fidelity, repeats). NOT native-speaker review; labelled as an AI pass, consistent with docs/G4A_UKRAINIAN_QA_FINDINGS.md.

> Exhaustive full-rubric AI read at careful screening depth. Reliably catches grammatical breakage, structural/fragment defects, calque markers, POS word-class mismatches, and salient semantic/sense errors. It is an AI pass, NOT native-speaker review. Observed clean-pool defect density (1 new P1 + 7 P2 in 983) is far below the PR#7 n=48 sample rate (23 P1 / 48 = 48%). This divergence is reconciled two ways and flagged for human adjudication: (a) a consistent principled POS bar treats predicate/relative adjective glosses (e.g. fragile->'легко ламається') as CLEAN, whereas several PR#7 POS 'P1's are, under that bar, borderline/P2; (b) residual risk that AI screening depth misses some subtle sense errors of the boundary->'розташування' class. Consequently the clean pool is NOT asserted defect-free; deeper/native semantic review remains advisable and G4-A is NOT a PASS.

**Principled POS bar (applied consistently):** P1 POS mismatch = gloss states a standalone WRONG-word-class sense (e.g. adj 'net' -> noun 'Залишок'). Predicate/relative descriptive glosses for adjectives (e.g. 'fragile'->'легко ламається') are standard lexicography and dispositioned CLEAN. This bar is applied consistently across the whole residual pool and explains the density divergence from the PR#7 n=48 sample (48% P1).

## Disposition counts (whole residual population)

| Disposition | Count |
|---|---|
| clean | 975 |
| P0 | 0 |
| P1 | 25 |
| P2 | 7 |
| needs-human | 0 |
| **total** | **1007** |

## The 24 known-open residual — independently re-derived

All 24 were verified against each entry's own fields. **All 24 are genuine defects.** Agreement with the PR #7 review: **18 full agreement**; **6 genuine-defect-but-milder-severity** (under the principled POS/number bar they are P2 rather than P1): SB-0058, SB-0306, SB-1695, SB-1707, SB-1731, SB-1635. See the inventory rows (source=known-open-confirmation) for per-ID rationale and `independent_severity_note` in `scripts/qa/cp3_judgments.json`.

## NEW findings from the exhaustive clean-pool read

- **New P1: 1** — SB-0067
- **New P2: 7** — SB-0014, SB-0024, SB-0070, SB-0474, SB-0493, SB-0659, SB-1081
- **New P0: 0**, **needs-human: 0**

Non-clean categories: grammar-calque-fragment=10, other=2, pos-morphology-mismatch=11, semantic-pedagogical-error=9

## Divergence from the PR #7 sample density — flagged for reviewer

The PR #7 seed-20260913 sample found 23 P1 in 48 (~48%). This exhaustive pass finds a far lower clean-pool defect density (1 new P1 + 7 P2 in 983). The two documented reasons are in the depth caveat above. This is surfaced explicitly rather than reconciled away: it means either the reviewer's bar is stricter (borderline POS/number cases counted P1) and/or AI screening depth under-detects some subtle sense errors. **Either way the clean pool is NOT asserted defect-free and G4-A is NOT a PASS.** A deeper or native-Ukrainian semantic pass over the clean pool is the recommended follow-up.

Artifacts: `G4A_RESIDUAL_AUDIT_CP3_INVENTORY.csv` (per-entry inventory), `scripts/qa/cp3_judgments.json` (judgment source).
