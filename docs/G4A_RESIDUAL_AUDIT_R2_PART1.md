# G4-A residual audit R2: part 1 intake

Branch: `codex/4-g4a-residual-audit-r2`

Exact parent: `d98f3f46cb6d0cce5e5d2a32c42b1eaa16305537`

Learner baseline: `f34f109ae5b8564e7fa10317c167a6ca728c52fd`

Learner vocabulary blob: `1c184e84e5c63e3a9f8e386af13787664a23bd66`

Gate remains `G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`.

## Purpose

Part 1 establishes an honest R2 intake. It removes every inherited R1 clean
judgment from consideration and records the accepted evidence floor before the
fresh 1,007-row audit continues.

The intake contains:

- 63 known P1 IDs: all 32 R1-listed defects normalized to P1 plus the 31
  seed-20260914 P1 findings;
- 25 known P2 IDs from seed-20260914;
- 919 `needs-human` rows pending fresh R2 adjudication;
- zero rows labeled clean;
- eight rewritten proposal-only corrections for the R1 proposals rejected by
  independent review.

The 88 known findings are pairwise disjoint. The complete intake contains each
of the 1,007 residual IDs exactly once in stable-ID order.

## Artifacts

- `docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv`
- `docs/G4A_R2_SEED_20260914_REVIEW.csv`
- `scripts/qa/r2_revised_corrections.json`
- `scripts/qa/r2_intake.py`
- `tests/g4a_r2_intake.py`

## Boundary

This checkpoint is not a completed R2 audit and makes no G4-A PASS claim. A
`needs-human` intake row means only that R1's inherited clean judgment was
discarded and a fresh row-level adjudication is still required. No correction
has been applied to `web/vocabulary.js` or any learner-facing artifact.
