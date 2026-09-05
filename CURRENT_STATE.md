# CURRENT_STATE.md

**Updated:** 2026-09-05
**Last passed gate:** G3 Reading Complete — PASS  
**Candidate gate:** G4 INTERNAL PASS — EXTERNAL RE-REVIEW PENDING — external re-review returned CHANGES REQUESTED; all four findings are addressed in candidate 3 — see `docs/G4_EXTERNAL_REVIEW_PACKET.md`
**Next gate:** G5 Writing Task 2, blocked until G4 is independently reviewed  
**Deployment:** local HTML only; public reconciliation deferred

---

## Passed Gates

### G0 — Audit & Requirements Lock
PASS.

### G1 — Foundation & Design System
PASS.

### G2 — Legacy Integration & Vocabulary Migration
PASS.

The source workbook is reconciled at 1,784 / 1,784 normalized Study Bank records.

### G3 — Reading Academy
PASS.

Current Reading evidence:

- 8 / 8 foundation strategies
- 15 question families
- 60 original texts/extracts
- 240 scored questions
- 240 / 240 explanations
- timed/mastery evidence
- error/review integration
- responsive pass at 320/375/430/768/1024/1440
- accessibility/regression pass

---

### G4 — Writing Task 1
**INTERNAL PASS — EXTERNAL RE-REVIEW PENDING.** External review of the first
candidate (`fe720d5`) returned **CHANGES REQUESTED** and produced candidate 2.
External re-review of `g4-candidate-2` returned **CHANGES REQUESTED** with one P1,
two P2 and one P3 finding. All four are fixed in candidate 3. The gate stays open
until the next independent re-review succeeds.
Review packet: `docs/G4_EXTERNAL_REVIEW_PACKET.md`.

| Benchmark | Required | Actual |
|---|---:|---:|
| Visual families | 7 | 7 |
| Micro-exercises | ≥60 | 70 |
| Full timed prompts | ≥20 | 21 |
| Band comparison sets | 1 per family | 7 |
| Band samples at 150+ words | 21 | 21 |

Also delivered: 21 original visuals, all 10 micro-exercise types in every family,
guided/independent/timed/mastery progression per family, 4 foundation modules, 7 family
modules, a 13-category error taxonomy, and the learner-facing UI under
Skills → Writing Task 1.

Current Writing Task 1 evidence:

- `tests/g4_writing1_inventory.py` — every benchmark met, fails automatically if coverage drops
- `tests/g4_writing1_validation.py` — PASS
- `tests/g4_writing1_claims.py` — 531 text blocks, every figure traced to a declared derivation; canonical `respectively` constructions rejected
- `tests/g4_writing1_content_qa.py` — 115 prose claims re-derived, 0 failed
- `tests/g4_writing1_functional.py` — PASS (scoring, mastery, timing, autosave, error/review, reload)
- `tests/g4_writing1_responsive.py` — PASS at 320/375/430/768/1024/1440 across all 7 families
- `tests/g4_writing1_accessibility.py` — PASS across all 7 families
- `tests/g4_writing1_persistence.py` — real HTTP, genuine reload, export/import, keyboard-only
- `tests/g4_writing1_obstruction.py` — real viewport states at all six widths
- `tests/g4_writing1_negative.py` — eight seeded defects, all caught, including the ordered-pair blind spot and annotation/prose drift
- `tests/release_integrity.py` — the packet names a release that resolves
- G0–G3 regression re-run and passing
- `docs/phase_4_report.md`, `docs/writing1_content_qa.md`

Decisions: D-015 mastery thresholds (amended by D-022), D-016 error taxonomy (13
categories after D-022), D-017 grounding by re-derived facts, D-018 toolchain, D-019 the
visual panel as the only new component, D-020 canonical claim manifest, D-021
sentence-scoped binding of canonical prose, D-022 the 150-word Task 1 minimum enforced,
D-023 release identity by tag, D-024 canonical `respectively` ban, D-025 executable
band-diagnostic evidence.

---

## Active Work

### G5 — Writing Task 2 — BLOCKED

Do not begin G5 until the G4 candidate release is independently reviewed and
approved. Minimum gate (`PROJECT_CHARTER.md` §9):

- ≥60 full prompts
- ≥100 micro-drills
- ≥15 annotated model responses
- ≥10 Band 6/7/8 comparison sets
- ≥12 timed simulations

Reuse the G4 shape: a Python generator producing `web/writing2_data.js`, an independent
validator that re-derives every check from the specification, a prose-claim QA pass, and
functional/responsive/accessibility suites covering every essay family rather than a
sample. The `.w1-visual` panel does not apply; Task 2 has no graphic.

---

## Defects

| ID | Severity | Status | Note |
|---|---|---|---|
| D4-001 | P2 | **Fixed** | Four Playwright tests hard-coded `/usr/bin/chromium` and could not launch off Linux, so the browser-driven gate evidence was not reproducible on the development machine. `tests/browser_env.py` resolves a Chromium binary portably; all four now pass. |
| D4-002 | P2 | **Fixed** | Task 1 exercise controls stayed disabled after an attempt, so "Try again" was impossible. |
| D4-003 | P3 | **Fixed** | `.field textarea` out-specified `.w1-draft`, leaving the drafting box 73px tall. |
| D4-004 | P3 | **Fixed** | `.question-card label{display:grid}` out-specified `.w1-opt`, stacking each radio above its option text. |
| D4-005 | P3 | **Fixed** | The chart axis caption collided with the top tick label. |
| QA-G4-001 | P3 | **Fixed** | The fact engine could not derive pairwise differences, rejecting genuinely grounded claims. |
| QA-G4-002 | P3 | **Fixed** | The literal string "Task 1" was read as the figure 1 during grounding checks. |
| D4-006 | P2 | **Fixed** | Grounding authorised any arithmetically derivable figure, including column totals and pairwise sums, so an item could look supported without being correct. Replaced by the canonical claim manifest (D-020). |
| D4-007 | P3 | **Fixed** | `.w1-chart{margin:0 -2px}` made every chart 4px wider than its parent's content box, so ancestors reported horizontal overflow. |
| D4-008 | P2 | **Fixed** | `.half`, `.third` and `.twoThird` only received a column span at 760px and above, so any non-`.card` grid child collapsed to one twelfth of the row on a phone: the band-lab annotation blocks became 28px slivers and the four vocabulary filters on Words became 14px slivers. Found by looking at a 375px screenshot, not by an assertion. Fixed in `web/styles.css`; `tests/responsive_check.py` now measures every grid child on all five primary routes at all six widths. |
| R1-001 | P1 | **Fixed** | Eighteen of 21 band samples were under the 150-word Academic Task 1 minimum, four of them labelled Strong (external review). All 21 are now 158-202 words. |
| R1-002 | P1 | **Fixed** | Mastery L4 and L5 could be reached with a 20-word response (external review). Both now require a response of at least `wordMinimum` words; underlength submissions log an error instead. |
| R1-003 | P2 | **Fixed** | Report-level grounding authorised a set of figures unbound to any entity, so two real values could be swapped between two series (external review). Replaced by sentence-scoped binding (D-021). |
| R1-004 | P2 | **Fixed** | The review packet named a candidate SHA that does not exist (external review). The candidate is now a tag, checked by `tests/release_integrity.py` (D-023). |
| R1-005 | P3 | **Fixed** | The Task 1 inventory printed `Completed 0+0` without naming its operands, and Reading foundation modules printed `foundation • undefined min` (external review). |
| R2-001 | P1 | **Fixed** | Five Band 6 teaching annotations contradicted the extended prose. The annotations now describe the final samples and carry executable presence/absence evidence rules (D-025). |
| R2-002 | P2 | **Fixed** | The canonical Band 8 line sample used a non-interleaved multi-entity `respectively` construction that allowed an ordered value swap. Canonical prose now bans the construction until ordered-pair parsing exists (D-024). |
| R2-003 | P2 | **Fixed** | Words overflowed the whole page at 320px and 375px because the migration filename could not wrap and the regression test measured document overflow only on Today. Notices now wrap; document and body widths are asserted after every route navigation. |
| R2-004 | P3 | **Fixed** | `Nothing holding it back` made an absolute claim stronger than the annotated evidence. The UI now says `Annotated criteria demonstrated` and explicitly bounds the statement to the criteria shown. |
| D4-009 | P2 | **Fixed** | Chromium exposed a 3px overflow on the 320px Task 1 family list: the three-column foundation `.module-item` could not shrink around its action button. Mobile module items now use two columns and place the action across the full row. |

Open P0: 0 · Open P1: 0 · Open P2: 0 · Open P3: 0

---

## Toolchain

Running the validation suite requires (see D-018):

- Python 3 with `jsonschema` and `playwright`
- any Chromium-family browser (override with `$IELTS_CHROMIUM`)

The application itself remains dependency-free static HTML/CSS/JS per D-014. Node is
needed only to assemble Claude Design mockups, not to run the app or its tests.

---

## Current Source Tree

Primary implementation:

- `web/index.html`
- `web/styles.css`
- `web/app.js`
- `web/data.js`
- `web/vocabulary.js`
- `web/reading_data.js`
- `web/writing1_data.js`

Schemas:

- `schemas/learner_state.schema.json`
- `schemas/module.schema.json`
- `schemas/exercise.schema.json`

Automated validation covers G2, G3 and G4 content, plus functional, responsive and
accessibility suites for Reading and Writing Task 1, and a whole-app responsive check.

---

## Known Constraints

- Do not deploy publicly yet.
- Do not reopen G0–G3 without an actual regression.
- Do not discard structured source in favor of editing only the monolithic release HTML.
- Do not remove the 1,784-word vocabulary bank.
- Do not grant mastery from page views.
- Do not use copyrighted commercial IELTS content.
- Practice guidance must not be labeled official scoring.

---

## Known Documentation Recovery

The earlier G0–G3 ZIP contains the source/test artifacts that were previously reported as missing from the local Claude folder.

The root canonical project documents were not present in that archive and have now been reconstructed from the approved context, ledger, and phase evidence.
