# G4-A R2 Phase-1 — P1 inventory, Stage A/B partition, and P2 backlog

**Phase-1 inventory only.** No proposals are drafted or applied, no Stage is
executed, no learner-facing file is touched, no gate changes, no G5, no
Priority 2 work. Gate remains `G4 technical PASS · G4-A CHANGES REQUESTED ·
G5 BLOCKED`.

## Provenance of the 265-P1 remediation set

The R2 reconciliation universe is exactly 1,007 residual IDs, each accounted
for exactly once (`docs/G4A_R2_RECON_SUMMARY.md`):

| Component | Rows | Source |
|---|---:|---|
| Accepted Part-1 floor (already final, not routed to A/B) | 88 | `docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv`, `disposition` != `needs-human` |
| — of which `disposition == P1` | **63** | same file |
| — of which `disposition == P2` | 25 | same file |
| Routed to A/B reconciliation (`disposition == needs-human`) | 919 | same file |
| — reconciled `final_disposition == P1` | **202** | `docs/G4A_R2_RECON_CHUNK{1,2,3}.csv` |
| — reconciled `final_disposition == P2` | 124 | same |
| — reconciled `final_disposition == clean-candidate` | 1 | same (`SB-0537`) |
| — consensus-clean-candidates (A/B agreed clean, not re-adjudicated) | 592 | `docs/G4A_R2_RECON_CONSENSUS_CLEAN.csv` |

Cross-consistency mechanically verified (see `scripts/qa/r2_p1_phase1_build.py`
and `tests/g4a_r2_p1_phase1_validator.py`): the 919 `needs-human` floor IDs
are exactly the union of the 327 chunk IDs and the 592 consensus-clean IDs,
with zero overlap; all 1,007 intake IDs are unique; no floor disposition
falls outside `{P1, P2, needs-human}`.

**P1 total = 63 (floor) + 202 (reconciled) = 265.** This matches the
265-P1 figure named in the governing handoff — that figure was verified
against the committed CSVs here, not assumed. Had the computed total not
equalled 265, this document would report the actual computed number instead.

**P2 total (backlog, tracked separately, not part of the P1 manifest or the
gap count) = 25 (floor) + 124 (reconciled) = 149.** See
`docs/G4A_R2_P2_BACKLOG.csv`.

P0 = 0, needs-human = 0 in the final accounting (all 919 non-floor IDs
resolved to P1/P2/clean-candidate across the reconciliation + consensus-clean
sets).

## Stage partition (deterministic, seedless)

Governing rule (verbatim from the handoff): sort the complete 265-P1 set by
stable ID in ascending lexical order. Stage A is the first 250 IDs; Stage B
is the remaining 15. This is the sole partition rule — there is no
dependency-based exception, no per-category grouping, and no reordering by
source (floor vs. reconciled).

All 265 P1 stable IDs use the uniform `SB-####` (4-digit, zero-padded)
format, so ascending lexical order coincides with ascending numeric order
here; the rule is applied lexically as specified, not renegotiated to a
numeric sort.

| Stage | Size | First id | Last id |
|---|---:|---|---|
| A | 250 | `SB-0009` | `SB-1707` |
| B | 15 | `SB-1709` | `SB-1769` |

Full sorted ID list with Stage tags: `docs/G4A_R2_P1_MANIFEST.csv`
(`id, word, pos, source, stage, proposed_target, proposed_value, gap`,
`source` is `floor` or `reconciled`).

Stage A and Stage B are **recorded only**, not applied. No P1 row's
`proposed_target`/`proposed_value` is drafted, edited, or applied by this
document, the manifest, or the builder script.

## P2 backlog

`docs/G4A_R2_P2_BACKLOG.csv` carries the 149 P2-disposition rows (25 floor +
124 reconciled) from the same universe, with the same `id, word, pos,
source, proposed_target, proposed_value` shape as the P1 manifest minus the
Stage/gap columns (P2 is not staged under this handoff). It is tracked
separately from the P1 manifest and is excluded from the proposal-
completeness gap count.

## Proposal-completeness gap

See `docs/G4A_R2_P1_PROPOSAL_GAPS.md` / `.csv` for the full derivation,
superseded-figures note, and the sorted list of the **31** P1 IDs whose
`proposed_target` or `proposed_value` is empty after normalization — all 31
originate from the accepted floor, none from the reconciled chunks. This
number is computed, not asserted; see that document for why the two
different pre-existing "31" mentions in the repo are not evidence for it.

## Methodology / determinism

- Builder: `scripts/qa/r2_p1_phase1_build.py`. Re-running it regenerates
  `docs/G4A_R2_P1_MANIFEST.csv`, `docs/G4A_R2_P2_BACKLOG.csv`,
  `docs/G4A_R2_P1_PROPOSAL_GAPS.csv` and `docs/G4A_R2_P1_PROPOSAL_GAPS.md`
  byte-identically from the two committed source artifact sets — no
  randomness, no seed, no manual editing of the generated files.
- Validator: `tests/g4a_r2_p1_phase1_validator.py`. Independently re-derives
  the P1/P2 sets and the Stage A/B split from the same committed sources and
  asserts the committed manifest/backlog/gap files match that recomputation
  exactly; fails closed (hard assertions, non-zero exit) on any missing ID,
  duplicate ID, incomplete P1 row, P2-row miscounted as P1, or wrong Stage
  split. It does not assert a preselected gap count.

## Explicitly out of scope here

No proposal drafting for any P1 row (gap or non-gap). No Stage A or Stage B
application. No learner-facing mutation (`web/vocabulary.js` is unchanged;
verified by blob SHA against the PR #8 base branch). No movement or merge of
PR #7. No gate-status or `DECISIONS.md` change. No G5 work. No Priority 2
(fresh promotion packet) work.
