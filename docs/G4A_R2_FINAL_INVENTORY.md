# G4-A residual audit R2 — final inventory + proposal-gap roster (Phase 1)

Deterministic unification of the three accepted R2 evidence populations into a
single 1,007-row inventory, plus the mechanically derived roster of Part-1-floor
P1 findings that carry no correction proposal.

**Inventory only. No proposal authoring, no remediation, no correction manifest,
no learner-facing mutation, no PR #7 movement, no merge, no gate change, no G5.**
Gate remains `G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`.

## Canonical baseline

- Branch cut from exact `39d6f918c7087d3616acc9654eecfaf5219aefc4`
  (*G4-A R2 reconciliation: final 1,007-row accounting + summary*)
- Learner `web/vocabulary.js` blob (unchanged): `1c184e84e5c63e3a9f8e386af13787664a23bd66`
- Part-1 floor `docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv` (unchanged): blob `7f34785e379ac76ee5341d4f65f33b123d57bc43`
- Accepted reconciliation evidence byte-frozen: `G4A_R2_RECON_CHUNK{1,2,3}.csv`,
  `G4A_R2_RECON_ROSTER.csv`, `G4A_R2_RECON_CONSENSUS_CLEAN.csv`, `G4A_R2_RECON.md`

Pass A, Pass B and the A/B reconciliation are accepted and closed. This phase
reads them and writes none of them.

## Inventory

`docs/G4A_R2_FINAL_INVENTORY.csv` — SHA-256
`47db204722bba924d240ab6ad4f0f90495a97378baa51d61cd66e4ff940faa33`

| source_stage | rows | meaning |
|---|---:|---|
| `part1-floor` | 88 | accepted Part-1 evidence floor (63 P1 / 25 P2) |
| `r2-reconciliation` | 327 | adjudicated union-defect roster (202 P1 / 124 P2 / 1 clean-candidate) |
| `consensus-clean` | 592 | Pass A/B consensus-clean-candidates, awaiting the fresh acceptance sample |
| **total** | **1,007** | every residual id exactly once |

**P1 population = 265** (63 floor + 202 reconciled). This is the scope the
complete Stage A/B remediation manifest will consume.

## Proposal-gap roster

`docs/G4A_R2_PROPOSAL_GAP_INVENTORY.csv` — SHA-256
`765093f483d7e737d5621d8ed90d5c685b74caf2d2f24db8e5cb316dd21621d9`

**31 rows**, derived — never hand-listed — as exactly:

```
source_stage == part1-floor  AND  final_disposition == P1  AND  proposal absent
```

### Why these 31 and no others

The 88-row floor decomposes as:

| provenance | disposition | rows | proposals |
|---|---|---:|---|
| R1-listed defect, severity normalized to P1 | P1 | 32 | **all present** |
| Codex seed-20260914 blinded acceptance challenge | P1 | **31** | **all absent** |
| Codex seed-20260914 blinded acceptance challenge | P2 | 25 | all absent |

`docs/G4A_R2_SEED_20260914_REVIEW.csv` carries only
`id, disposition, category, rationale` — it has **no proposal column at all**.
That is the structural origin of the gap: seed-derived findings entered the
intake with empty `proposed_target`/`proposed_value`, while the 32 R1-listed
floor P1s arrived with proposals (eight of them rewritten via
`scripts/qa/r2_revised_corrections.json` after independent review).

These rows sit **outside** `tests/g4a_r2_reconciliation.py`'s proposal
requirement, which governs only the 327-row union-defect roster. The guard was
never red; it simply never covered this population. The 25 seed P2 rows are
likewise proposal-less and are **out of scope** for this ticket.

### Gap composition

| category | rows |
|---|---:|
| `pos-morphology` | 9 |
| `semantic-pedagogical` | 8 |
| `grammar-syntax` | 5 |
| `grammar-calque` | 4 |
| `grammar-semantic` | 2 |
| `russianism-calque` | 2 |
| `ua-definition-consistency` | 1 |

POS: 9 word family · 8 n. · 7 adj. · 5 v. · 2 adv.

## Artifacts

- `scripts/qa/r2_final_inventory.py` — deterministic generator (both outputs)
- `docs/G4A_R2_FINAL_INVENTORY.csv` — 1,007 rows
- `docs/G4A_R2_PROPOSAL_GAP_INVENTORY.csv` — 31 rows
- `tests/g4a_r2_final_inventory.py` — guard

## Validation

| check | result |
|---|---|
| `tests/g4a_r2_final_inventory.py` | **PASS** (exit 0) |
| `tests/g4a_r2_reconciliation.py` (accepted, unmodified) | **PASS** (exit 0, 327/327) |
| Seeded negative — drop a gap row | **caught** (not byte-reproducible) |
| Seeded negative — mutate frozen reconciliation evidence | **caught** (recon holds 328, expected 327) |
| `git diff 39d6f918 -- docs/ web/ scripts/ tests/` | no content change to accepted evidence |
| Generated artifacts CRLF-free | yes (`write_bytes`, explicit LF) |

### Environment note (pre-existing, not introduced here)

This checkout has `core.autocrlf=true`, and the repository pins raw-byte blob
hashes throughout. Git reports LF working-copy files as modified and warns it
will convert them to CRLF on next touch; if that conversion ever materializes,
every raw-byte guard in the project breaks — the same failure class fixed for
the migration generator in `b2cf9ef5`. Separately, the accepted reconciliation
guard exits non-zero on a Windows console without UTF-8 because its child
generator crashes printing Ukrainian text under cp1252; it passes cleanly with
`PYTHONUTF8=1`. Both are environment findings for Dalton, not code defects
introduced by this phase.

## Boundary

This phase makes no G4-A PASS claim and authorizes no correction. The next step
is a calibration fixture, then authoring the 31 proposals in 10/10/11 reviewed
batches into a **separate supplemental artifact**, leaving the accepted
reconciliation byte-frozen. The complete 265-row Stage A/B remediation manifest
is generated only afterward.
