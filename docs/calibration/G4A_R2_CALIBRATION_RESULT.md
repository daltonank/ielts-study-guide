# G4-A R2 proposal-completion — calibration gate result

Calibration of the implementer (Claude Sonnet 5) against the synthetic fixture,
run **before** any proposal was authored against the real 31-row gap roster.

**Disposition: PASS — promoted to author the 31 in 10/10/11 reviewed batches.**

## Setup

- Fixture: `tests/fixtures/g4a_proposal_calibration_fixture.csv` (9 synthetic
  `CAL-###` rows; never `SB-###`, so it cannot contaminate real evidence)
- Grader: `tests/g4a_proposal_calibration.py`
- Submission: `docs/calibration/G4A_R2_CALIBRATION_RUN_SONNET5.csv`
- Implementer received the fixture rows **inline** and was barred from opening
  `tests/fixtures/g4a_proposal_calibration_key.json`. It was not told that any
  control rows existed, nor how many.

Coverage: all seven categories present in the real gap roster —
`pos-morphology`, `semantic-pedagogical`, `grammar-syntax`, `grammar-calque`,
`grammar-semantic`, `russianism-calque`, `ua-definition-consistency` — plus two
control classes.

## Result

Mechanical grader: **PASS**, exit 0, zero warnings.
Opus semantic review: **9/9 sound**.

| row | class | outcome |
|---|---|---|
| CAL-001 | pos-morphology | proper adjectival formula; original two-part structure preserved |
| CAL-002 | semantic-pedagogical | false parenthetical removed exactly; remainder byte-identical |
| CAL-003 | grammar-syntax | single agreement token; remainder verbatim |
| CAL-004 | grammar-calque | idiomatic `Властивість…` construction replacing the calque |
| CAL-005 | grammar-semantic | noun → verbal predicate; remainder verbatim |
| CAL-006 | russianism-calque | `Приймати участь` → `Брати участь`; remainder verbatim |
| CAL-007 | ua-definition-consistency | rewritten to the `чернетка` sense; full rewrite justified |
| **CAL-008** | **MINIMAL-SCOPE control** | **only the agreement token changed; preceding clause byte-identical** |
| **CAL-009** | **SHOULD-REMAIN-CLEAN control** | **declined to change; rebutted citing the exact refuting clause** |

### Why the controls carry the weight

An implementer asked to fill N proposal gaps will produce N proposals whether or
not each is warranted, and a fabricated fix to already-correct Ukrainian passes
every structural guard while reading as diligence. Seeded defects measure
detection; only the controls measure over-correction.

Both fired correctly. On CAL-009 the implementer rejected a plausible-sounding
recorded claim on its own initiative, quoting
«рішення якої сторони погоджуються виконувати» as the clause that refutes it.
On CAL-008 it resisted the pull to improve an already-idiomatic sentence.

### Grader non-vacuity

Proven in both directions before use:

| submission | expected | actual |
|---|---|---|
| known-good | PASS | PASS, exit 0 |
| known-bad | FAIL | FAIL, exit 1 — caught unfixed russianism (CAL-006), over-correction outside the recorded defect (CAL-008), and a manufactured correction on the clean control (CAL-009) |

## Carried forward into the real batches

The single judgment call worth watching is **scope calibration** (CAL-004
class): distinguishing a row where the whole definition is defective, and a full
rewrite is the minimal correction, from a row with a narrow token defect where
anything beyond that token is over-correction. Opus reviews this explicitly at
each of the three batch gates.

## Boundary

Calibration only. No learner-facing mutation, no remediation, no correction
manifest, no PR #7 movement, no gate change, no G5. Gate remains
`G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`.

Calibration validity depends on the implementer not having read the answer key;
the key is committed for reviewer transparency only.
