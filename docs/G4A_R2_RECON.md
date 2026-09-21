# G4-A residual audit R2 — A/B reconciliation (v2)

Evidence-first reconciliation of the Pass A vs Pass B dispositions, restarted
cleanly from canonical GitHub evidence. The earlier unpublished commits
`ad70bfa` / `a1eb6e7` are treated as noncanonical/lost and are neither
referenced as evidence nor recreated.

## Frozen inputs (by exact SHA)

- Baseline (merge-base of A and B): `5a5fd7d7ce8cc4e7c3f8a2b2a0253269ed803ac0`
- Pass A: `codex/4-g4a-residual-audit-r2` @ `f7ddf7b1dadfd91a8126b15c0977873be02f883c`
- Pass B: `claude/recent-slack-handoff-a0fx3d` @ `2b90574e3dafb88313ac6563ec094577fb7a95a2`
- PR #7: open / draft / unmerged @ `f34f109…`
- Learner `web/vocabulary.js` blob (must remain): `1c184e84e5c63e3a9f8e386af13787664a23bd66`
- Accepted 88-row Part-1 floor `docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv`: unchanged (blob `7f34785e379ac76ee5341d4f65f33b123d57bc43`).

## Mechanically reproduced A/B matrix (919/919, same ID set)

| Pass A | Pass B | count |
|---|---|---:|
| P1 | clean-candidate | 188 |
| P2 | clean-candidate | 113 |
| P1 | P2 | 18 |
| P2 | P2 | 6 |
| clean-candidate | P2 | 2 |
| clean-candidate | clean-candidate | 592 |

A-defect set = 325 · B-defect set = 26 · overlap = 24 · **union-defect roster = 327** · consensus-clean = 592.

## Deterministic roster (committed before adjudication)

Union-defect IDs sorted ascending, then `random.Random(20260919).shuffle`, then
split 109 / 109 / 109: chunk 1 = 109, chunk 2 = 109, chunk 3 = 109.

- Roster: `docs/G4A_R2_RECON_ROSTER.csv` — SHA-256 `eb3a88dd9284dd5237bbbfa0953fe8fcc9d133828c14a8b9c745ce406bd001e6`
- Consensus-clean carry-forward: `docs/G4A_R2_RECON_CONSENSUS_CLEAN.csv` — SHA-256 `1f92840c0d881e8d37203669e5d5bcfde1cb51ea513bc04cf80f9c4088e99cc2`

Reproduce: `python3 scripts/qa/r2_reconciliation_roster.py` regenerates both
files byte-identically and prints the same SHA-256 values.

## Adjudication (chunks 1-3, evidence-first)

Each of the 327 rows is re-adjudicated against the **actual frozen Ukrainian
text** (exact `ua` / `definitionUa` substring evidence), carrying both the
Pass-A and Pass-B disposition + rationale, and a final disposition
(`P0`/`P1`/`P2`/`clean-candidate`/`needs-human`) with confidence, category,
rationale, and a proposal for defects. A final clean verdict must explicitly
rebut every prior defect claim; a generic "sense is accurate" is not accepted.
Output: `docs/G4A_R2_RECON_CHUNK{1,2,3}.csv`. Guard: `tests/g4a_r2_reconciliation.py`.

No learner-facing mutation, no remediation, no PR #7 movement, no merge, no
gate change, no G5. Gate remains `G4 technical PASS · G4-A CHANGES REQUESTED ·
G5 BLOCKED`.
