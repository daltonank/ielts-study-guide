# G4-A residual audit R2 — A/B reconciliation summary (v2)

Evidence-first reconciliation of Pass A (Codex) vs Pass B (Claude Code) over the
327 union-defect rows, restarted cleanly from canonical GitHub evidence. The
earlier unpublished commits `ad70bfa` / `a1eb6e7` are noncanonical/lost and are
neither referenced as evidence nor recreated.

**Reconciliation evidence only.** No learner-facing mutation, no remediation, no
PR #7 movement, no merge, no gate change, no G5. Gate remains
`G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`.

## Frozen inputs (verified by exact SHA)

- Baseline (merge-base of A and B): `5a5fd7d7ce8cc4e7c3f8a2b2a0253269ed803ac0`
- Pass A: `codex/4-g4a-residual-audit-r2` @ `f7ddf7b1dadfd91a8126b15c0977873be02f883c`
- Pass B: `claude/recent-slack-handoff-a0fx3d` @ `2b90574e3dafb88313ac6563ec094577fb7a95a2`
- PR #7: open / draft / unmerged @ `f34f109ae5b8564e7fa10317c167a6ca728c52fd`
- Learner `web/vocabulary.js` blob (unchanged): `1c184e84e5c63e3a9f8e386af13787664a23bd66`
- Accepted 88-row Part-1 floor `docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv` (unchanged): blob `7f34785e379ac76ee5341d4f65f33b123d57bc43`

## A/B matrix (mechanically reproduced, 919/919, same ID set)

| Pass A | Pass B | count |
|---|---|---:|
| P1 | clean-candidate | 188 |
| P2 | clean-candidate | 113 |
| P1 | P2 | 18 |
| P2 | P2 | 6 |
| clean-candidate | P2 | 2 |
| clean-candidate | clean-candidate | 592 |

A-defect = 325 · B-defect = 26 · overlap = 24 · **union-defect roster = 327** · consensus-clean = 592.
Roster: `docs/G4A_R2_RECON_ROSTER.csv`, SHA-256 `eb3a88dd9284dd5237bbbfa0953fe8fcc9d133828c14a8b9c745ce406bd001e6`; seed `20260919`, split 109/109/109.

## Reconciled dispositions (327 union-defect rows)

| final | count |
|---|---:|
| P1 | 202 |
| P2 | 124 |
| clean-candidate | 1 |
| P0 | 0 |
| needs-human | 0 |

Per chunk: c1 66 P1 / 43 P2; c2 65 P1 / 43 P2 / 1 clean; c3 71 P1 / 38 P2.
Confidence: 321 high, 6 medium (the 6 divergences below).

### Method and severity standard

Each row was re-adjudicated against the **actual frozen Ukrainian text** with an
exact-substring evidence quote, carrying both the Pass-A and Pass-B disposition
and rationale. The final disposition defaults to Pass A's where the text
confirms the defect — which it did on essentially every row, because Pass B's
clean calls on these rows were too lenient (e.g. SB-0015, SB-0039, SB-0047,
SB-0048, SB-0060, all confirmed defects here). Severity follows the project's
established register standard: non-idiomatic/Russian-influenced calques,
grammatical agreement errors, POS/coverage gaps on multi-POS headwords, false
friends, broken/unintelligible syntax and truncation are **P1**; purely cosmetic
issues (missing terminal period, lowercase start, trailing semicolon), mild
circular restatements where the cognate fully conveys, and gloss citation-form
issues where the definition is correct are **P2**. A final clean verdict must
explicitly rebut every prior defect claim (guard-enforced); generic "sense is
accurate" rationales are rejected.

### Divergences from Pass A (6, all evidence-based)

| ID | Pass A | Pass B | final | reason |
|---|---|---|---|---|
| SB-0537 gambling | P1 | clean | **clean-candidate** | definition does state «із ставкою на результат» and names skill/chance, so it captures wagering — Pass A's "does not explain wagering" does not hold |
| SB-1124 stir | clean | P2 | **P2** | gloss «ворушити» is imprecise for stirring a liquid («помішувати/розмішувати») — Pass B upheld |
| SB-0882 portfolio | clean | P2 | **P2** | investment definition under the creative-works gloss «портфоліо» (finance = «портфель») — Pass B upheld |
| SB-1521 parallel | P1 | clean | **P2** | telegraphic but valid description of parallelism; «віддалені» agrees with the implied points — minor, not a material grammar defect |
| SB-1771 encountered | P1 | P2 | **P2** | gloss «зіткнувся» is a finite-past citation but the definition is correct — citation-form only |
| SB-1640 decades | P1 | P2 | **P2** | ua «десятиліть» is a genitive citation where nominative «десятиліття» is expected; the definition is correct — citation-form only |

The 592 A/B consensus-clean rows are carried forward as **consensus-clean-candidates**
only (`docs/G4A_R2_RECON_CONSENSUS_CLEAN.csv`), not final clean — they await the
later fresh unseen acceptance sample and are not re-reviewed in this pass.

## Final 1,007-row accounting

`88` accepted Part-1 floor (untouched) `+` `327` reconciled union-defect `+` `592`
consensus-clean-candidates `=` **1,007** residual IDs, each accounted for exactly
once. The 88-row floor artifact is byte-identical to baseline.

## Artifacts

- `docs/G4A_R2_RECON_ROSTER.csv` — 327-ID roster (chunk/seq/id + A/B dispositions)
- `docs/G4A_R2_RECON_CONSENSUS_CLEAN.csv` — 592 consensus-clean IDs
- `docs/G4A_R2_RECON_CHUNK{1,2,3}.csv` — per-row reconciliation with 9-axis-derived
  evidence, both passes' dispositions/rationales, final disposition, confidence,
  category, rationale, and proposal for defects
- `scripts/qa/r2_reconciliation_roster.py` — deterministic roster generator
- `scripts/qa/r2_recon_build_chunk.py` — chunk assembler
- `scripts/qa/recon_judgments/chunk{1,2,3}.py` — authored per-row verdicts
- `tests/g4a_r2_reconciliation.py` — guard/validator

This reconciliation proposes no remediation. ChatGPT independently reviews the
adjudication before any correction manifest is authorized.
