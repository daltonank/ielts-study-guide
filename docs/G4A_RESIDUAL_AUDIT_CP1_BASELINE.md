# G4-A Residual-Population Audit — CP1: Baseline & Integrity

**Audit branch:** `claude-code/4-g4a-residual-audit`
**Reviewed baseline (PR #7 head):** `f34f109ae5b8564e7fa10317c167a6ca728c52fd`
**`web/vocabulary.js` git blob:** `1c184e84e5c63e3a9f8e386af13787664a23bd66` (unchanged — verified at HEAD)
**Gate language (unchanged):** `G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`
**Disposition constraint:** this is an AUDIT. It mutates no learner-facing data and claims no G4-A PASS.

This audit is a **read-and-inventory** pass over the residual vocabulary population. It adds
only audit artifacts (docs/, scripts/, tests/). It does not edit `web/vocabulary.js`, does not
move PR #7, and does not change D-027/D-028 or any G5 state.

## Canonical-checkpoint provenance

A repository + issue #4 + docs search (`DECISIONS.md`, `CURRENT_STATE.md`, `docs/phase_4a*`,
the T5-B docs, `docs/G4A_UKRAINIAN_QA_AUDIT_PLAN.md`) found **no pre-existing canonical
definition of "the four deterministic audit checkpoints."** The only `checkpoint` hits are the
per-phase report titles (`phase_N_report.md`). This audit therefore **adopts and documents** the
four checkpoints (CP1–CP4) specified in the issue #4 residual-audit handoff, and persists each as
a distinct commit pushed to `origin`.

## Register integrity (frozen — confirmed, not modified)

| Register | File | Rows | Split |
|---|---|---|---|
| Historical | `docs/G4A_UKRAINIAN_QA_FINDINGS.csv` | 702 | **142 P0 / 314 P1 / 246 P2** |
| Supplemental | `docs/G4A_T5B_SUPPLEMENTAL_FINDINGS.csv` | 116 | **114 corrected (1 P0 + 113 P1) + 2 benign; 0 open / 0 needs-human** |

Both registers are confirmed at the frozen values the handoff specifies. Neither file is touched
by this audit.

## Deterministic gate + guards (run this session, PYTHONUTF8=1)

| Command | Exit | Result | Non-vacuity evidence |
|---|---|---|---|
| `python3 tests/g4a_ukrainian_deterministic.py` | 0 | PASS | ratchet self-check flags a seeded equal-count collision and ignores a legit shrink |
| `python3 tests/g4a_t5b_repeat_guard.py` | 0 | PASS | seeded synthetic adjacent + connector repeats caught |
| `python3 tests/g4a_t5b_supplemental_accounting.py` | 0 | PASS | reconciles register ↔ shipped bytes ↔ guarded payloads |

The deterministic gate reports 1784/1784 vocabulary entries, no missing/non-Cyrillic/copied
`ua`/`definitionUa`, no placeholder/markup/encoding corruption, no new collision groups vs
baseline, and the historical register reconciling at 142/314/246. It explicitly proves only
**structural** well-formedness — it says nothing about meaning. That semantic gap is exactly what
CP3 of this audit addresses over the residual population.

## What CP1 establishes

The baseline is green and non-vacuous. The residual audit (CP2–CP4) proceeds from an intact,
verified baseline with the canonical `web/vocabulary.js` blob unchanged.

See `docs/G4A_RESIDUAL_AUDIT_CP1_BASELINE.json` for the machine-readable record.
