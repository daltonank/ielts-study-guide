# Live Build Benchmark Dashboard

**Updated:** 2026-09-05 (G4 candidate 3 — internal pass, external re-review pending)

| Metric | Current | Approved benchmark | Status |
|---|---:|---:|---|
| Requirements ledger rows | 137 | complete traceability | Active |
| Legacy vocabulary loaded | 1,784 | 1,784 | **Pass** |
| Legacy vocabulary source records reconciled | 1,784 / 1,784 | 1,784 / 1,784 | **Pass** |
| Reading foundation modules | 8 / 8 | all required foundations | **Pass** |
| Reading question-family modules | 15 | all major families | **Pass** |
| Reading passages/extracts | 60 | ≥50 | **Pass** |
| Reading questions | 240 | ≥200 | **Pass** |
| Reading answer explanations | 240 / 240 | 100% | **Pass** |
| Task 1 visual families | 7 / 7 | 7 | **Pass** |
| Task 1 original visuals | 21 | 3 per family | **Pass** |
| Task 1 micro-exercises | 70 | ≥60 | **Pass** |
| Task 1 micro-exercise types per family | 10 / 10 | all 10 in every family | **Pass** |
| Task 1 full timed prompts | 21 | ≥20 | **Pass** |
| Task 1 band comparison sets (REQ-019) | 7 | 1 per family | **Pass** |
| Task 1 band sample responses | 21 | 3 per set | **Pass** |
| Task 1 foundation modules | 4 | — | Complete |
| Task 1 error taxonomy categories | 13 | ≥10 | **Pass** |
| Task 1 canonical claim manifest | 531 text blocks | every figure traces to a declared derivation | **Pass** |
| Task 1 band diagnostic evidence | 5 affected Band 6 samples | displayed annotations match adjacent prose | **Pass** |
| Task 1 ordered-pair safety | canonical `respectively` rejected | no known silent ordered swap path | **Pass** |
| Task 1 prose-claim QA | 115 claims re-derived, 0 failed | all quantified prose claims true | **Pass** |
| Task 1 UI | delivered | learner-facing delivery | **Pass** |
| Task 2 prompts | 0 | ≥60 | Not started |
| Task 2 drills | 0 | ≥100 | Not started |
| Grammar items | 0 | ≥250 | Not started |
| Paraphrase items | 0 | ≥100 | Not started |
| Speaking Part 1 | 0 | ≥120 | Not started |
| Speaking Part 2 | 0 | ≥75 | Not started |
| Speaking Part 3 | 0 | ≥150 | Not started |
| P0 defects | 0 | 0 | **Pass** |
| P1 defects | 0 | 0 at release | **Pass** |
| P2 defects | 0 open (3 fixed: D4-001, D4-002, D4-006) | resolve before gate | **Pass** |
| P3 defects | 0 open (6 fixed) | should not accumulate | **Pass** |
| Responsive target widths | 6 / 6 passed | 6 / 6 | **Pass** |
| Reading responsive target widths | 6 / 6 passed | 6 / 6 | **Pass** |
| Task 1 responsive target widths | 6 / 6 passed, all 7 families | 6 / 6 | **Pass** |
| Task 1 accessibility, all families | 7 / 7 passed | text equivalents + labelled controls | **Pass** |
| Task 1 functional flow | passed | scoring, mastery, timing, autosave, error/review, reload | **Pass** |
| Task 1 persistence over real HTTP | passed | genuine reload, export/import, keyboard-only | **Pass** |
| Task 1 obstruction, real viewports | 6 / 6 widths | no sticky overlap, skip link hidden until focused | **Pass** |
| Accessibility automated score | not fully measurable in current harness | ≥95 at G10 | Deferred to G10 |

Phase gates passed: **G0, G1, G2, G3**.
Candidate gate: **G4 — INTERNAL PASS, EXTERNAL RE-REVIEW PENDING** (`docs/G4_EXTERNAL_REVIEW_PACKET.md`).
Next gate: **G5 — Writing Task 2**, blocked until G4 is independently reviewed.

**G4-A T5-B promotion attempt (2026-09-10): CHANGES REQUESTED.** 28/28 fresh validation commands
PASS and the P1 closeout accounting reports 314/314 registered P1 resolved · 0 unresolved · 246 P2
remaining, but the T5-B blind stratified sample of never-flagged entries surfaced a NEW P1-class
defect — adjacent identical-word repetition in `definitionUa` (~21 clean entries, e.g. `SB-0013,
SB-0357, SB-0484, SB-0576, SB-0577, SB-0759, SB-1230, SB-1259, SB-1486`), the same "Word repeated"
class the register rates P1 but outside the register and the P2 backlog. Gate stays
`G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`. The "P0/P1 defects = 0" rows above track
the *register* backlog; this newly-surfaced P1-class finding is untracked and pending a remediation
sweep. Evidence: `docs/phase_4a_t5b_promotion_report.md`.

**G4-A T5-B repeat remediation (2026-09-10, issue #4, branch `claude/slack-session-62m83z`): still
CHANGES REQUESTED.** The "~21" estimate was resolved to exact numbers by a deterministic full-bank
scan: **37 candidates → 35 confirmed P1 corrected + 2 benign allowlisted (`SB-0660`, `SB-1197`)**, 0
needing human adjudication. Corrections landed as a guarded post-migration stage (input blob
`9282d201` → new pinned output `bb173f36`; workbook untouched, base blob `4ed00c96` not repinned).
New full-bank repeat guard (`tests/g4a_t5b_repeat_guard.py`, non-vacuous) + supplemental register
(`docs/G4A_T5B_SUPPLEMENTAL_FINDINGS.csv`). Fresh blind sample (seed `20260910`, n=40 by POS over
1,683 unflagged entries): 0/40 repeat-class defects; 35 corrected re-review clean. 20 non-browser +
11 browser (six widths) all PASS. **Disposition stays CHANGES REQUESTED** because a NEW distinct
class — connector-separated repeats ("X або X", 64 entries) — remains open (registered
open-deferred; D-027 requires zero unresolved P0/P1). See D-028 and
`docs/phase_4a_t5b_promotion_report.md` §9–15.

**G4-A T5-B connector-separated remediation (2026-09-10, issue #4 follow-up, branch
`claude/slack-session-0iypwo`): zero unresolved P0/P1 — `G4-A PASS CANDIDATE` proposed (proposal
only).** The 64 connector-separated candidates were each individually adjudicated with Ukrainian
linguistic judgement: **64 confirmed P1, 0 benign, 0 needs-human** — every one a generation artifact
(an English near-synonym/doubled pair collapsed to a single Ukrainian lexeme: "X або X", "X чи X",
"X і X"), none a legitimate homograph/idiom/binomial. Corrections landed as a guarded post-migration
stage (input blob `bb173f36` → new pinned output `7520f722`; workbook untouched, base blob `4ed00c96`
and earlier pins not repinned). The full-bank repeat guard now fails closed on connector-separated
repeats too (seeded synthetic connector defect: exit 1 with defect, exit 0 restored). Supplemental
register: **99 corrected (35 adjacent + 64 connector) + 2 benign; 0 open, 0 needs-human**; historical
register (142/314/246) untouched; the dashboard's `p1_accounting` block splits historical (314, frozen)
from supplemental so 0 can never read as globally zero. **29/29 commands PASS** (18 non-browser + 11
browser at 320/375/430/768/1024/1440). Fresh T5-B review: 64 corrected items re-review clean; fresh
blind stratified sample **n=48, NEW seed `913377`, POS-stratified over 1,683 clean entries → 0 new
P0/P1**; seeded-defect meta-validation **6/6**. Canonical gate language unchanged pending sign-off:
`G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`; PR #7 unmerged; issue #4 not closed; G5 not
started; no canonical G4-A PASS recorded.

## How the Task 1 rows were verified

Every figure above came from running the script, not from reading a report:

- `python scripts/build_writing1_curriculum.py` → `web/writing1_data.js`
- `python tests/g4_writing1_validation.py` → PASS (re-parses the artifact and re-derives every check independently of the generator)
- `python tests/g4_writing1_content_qa.py` → 115 claims checked, 0 failed
- `python tests/g4_writing1_inventory.py` → every benchmark met
- `python tests/g4_writing1_claims.py` → 531 text blocks, all traced; canonical `respectively` rejected
- `python tests/g4_writing1_functional.py` → PASS
- `python tests/g4_writing1_persistence.py` → PASS
- `python tests/g4_writing1_obstruction.py` → PASS at all six widths
- `python tests/g4_writing1_responsive.py` → PASS at all six widths, all seven families
- `python tests/g4_writing1_accessibility.py` → PASS
- `python scripts/build_benchmark.py` → regenerated `docs/benchmark_dashboard.json`

Two validators were checked against seeded defects. The structural validator caught ten of ten (fabricated figure, substituted family, tampered fact, missing distractor reasoning, missing overview, missing micro-type, pie not summing to 100, band claim, dangling module reference, stripped Ukrainian note). The canonical-claim validator caught eight of eight, including a column total and a pairwise slice sum smuggled into an explanation. The cross-suite negative packet caught eight of eight, including the actual `respectively` blind spot and annotation/prose drift. Every clean artifact still passed.
