# G4-A R2 Phase-1 — P1 proposal-completeness gap artifact

**Derivation.** This list and count are computed solely from the current,
published 265-P1 manifest source (`docs/G4A_R2_P1_MANIFEST.csv`, itself built
from the committed `docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv` floor and
`docs/G4A_R2_RECON_CHUNK{1,2,3}.csv`). A P1 row is a gap iff, after
whitespace normalization, its `proposed_target` or `proposed_value` is empty
or a placeholder token (`n/a`, `na`, `none`, `null`, `tbd`, `-`). Only rows
with a final P1 disposition are considered; P2 rows and non-P1 floor rows
(`needs-human`) are excluded. No preselected numeric count is asserted
anywhere — this is the data's answer, not an input.

**Superseded figures.** The earlier unverified "31" figure came from a
noncanonical, local-only attempt and is **not** used as evidence here.
Separately, `docs/G4A_RESIDUAL_AUDIT_R2_PART1.md` also contains the numeral
"31" in an unrelated context (a provenance sub-count: 31 of the 63 floor-P1
IDs originate from the "seed-20260914" P1 findings) — that is a different
quantity and is not evidence for this gap count either. The earlier "56
blank floor defect rows" figure is also not substituted here; it was not
computed as a P1-only quantity and this artifact does not rely on it.

**Computed gap count: 31** out of 265 final-disposition P1 rows.

All 31 gap rows originate from the accepted floor
(`docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv`, disposition `P1`); none originate
from the 327-row A/B reconciliation chunks, which is expected because the
reconciliation adjudication guard (`tests/g4a_r2_reconciliation.py`) already
requires every P0/P1/P2 chunk row to carry a non-empty `proposed_target` and
`proposed_value` before it can be committed, while the floor's already-final
P1 rows predate that guard and were carried forward unedited.

## Sorted gap ID list (31)

- `SB-0043`
- `SB-0061`
- `SB-0073`
- `SB-0328`
- `SB-0428`
- `SB-0516`
- `SB-0556`
- `SB-0651`
- `SB-0652`
- `SB-0710`
- `SB-0885`
- `SB-0899`
- `SB-0907`
- `SB-1003`
- `SB-1048`
- `SB-1111`
- `SB-1149`
- `SB-1168`
- `SB-1171`
- `SB-1247`
- `SB-1270`
- `SB-1275`
- `SB-1335`
- `SB-1495`
- `SB-1523`
- `SB-1570`
- `SB-1585`
- `SB-1590`
- `SB-1630`
- `SB-1668`
- `SB-1747`

## Reproduce

```
python3 scripts/qa/r2_p1_phase1_build.py
```

regenerates `docs/G4A_R2_P1_MANIFEST.csv`, `docs/G4A_R2_P2_BACKLOG.csv`,
`docs/G4A_R2_P1_PROPOSAL_GAPS.csv` and this file byte-identically.
