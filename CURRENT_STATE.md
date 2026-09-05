# CURRENT_STATE.md

**Updated:** 2026-09-04  
**Last passed gate:** G3 Reading Complete — PASS  
**Candidate gate:** G4 INTERNAL PASS — EXTERNAL REVIEW PENDING — see `docs/G4_EXTERNAL_REVIEW_PACKET.md`  
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
**INTERNAL PASS — EXTERNAL REVIEW PENDING.** Every internal requirement passes with
reproducible evidence, but the planned cross-provider review has not happened, so this
is a candidate release rather than a closed gate. Review packet:
`docs/G4_EXTERNAL_REVIEW_PACKET.md`.

| Benchmark | Required | Actual |
|---|---:|---:|
| Visual families | 7 | 7 |
| Micro-exercises | ≥60 | 70 |
| Full timed prompts | ≥20 | 21 |
| Band comparison sets | 1 per family | 7 |

Also delivered: 21 original visuals, all 10 micro-exercise types in every family,
guided/independent/timed/mastery progression per family, 4 foundation modules, 7 family
modules, a 12-category error taxonomy, and the learner-facing UI under
Skills → Writing Task 1.

Current Writing Task 1 evidence:

- `tests/g4_writing1_inventory.py` — every benchmark met, fails automatically if coverage drops
- `tests/g4_writing1_validation.py` — PASS
- `tests/g4_writing1_claims.py` — 529 text blocks, every figure traced to a declared derivation
- `tests/g4_writing1_content_qa.py` — 115 prose claims re-derived, 0 failed
- `tests/g4_writing1_functional.py` — PASS (scoring, mastery, timing, autosave, error/review, reload)
- `tests/g4_writing1_responsive.py` — PASS at 320/375/430/768/1024/1440 across all 7 families
- `tests/g4_writing1_accessibility.py` — PASS across all 7 families
- `tests/g4_writing1_persistence.py` — real HTTP, genuine reload, export/import, keyboard-only
- `tests/g4_writing1_obstruction.py` — real viewport states at all six widths
- G0–G3 regression re-run and passing
- `docs/phase_4_report.md`, `docs/writing1_content_qa.md`

Decisions: D-015 mastery thresholds, D-016 error taxonomy, D-017 grounding by re-derived
facts, D-018 toolchain, D-019 the visual panel as the only new component.

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
