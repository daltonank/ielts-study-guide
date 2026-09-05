# CURRENT_STATE.md

**Updated:** 2026-09-04  
**Last passed gate:** G3 Reading Complete — PASS  
**Active gate:** G4 Writing Task 1 — content layer complete and validated; UI not built, gate **not** passed  
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

## Active Work

### G4 — Writing Task 1 — IN PROGRESS, not passed

**Content layer: complete and validated. Learner-facing UI: not built.**

Quantitative benchmarks, all met and verified by running the validators:

| Benchmark | Required | Actual | Status |
|---|---:|---:|---|
| Visual families | 7 | 7 | Met |
| Micro-exercises | ≥60 | 70 | Met |
| Full timed prompts | ≥20 | 21 | Met |

Also delivered: 21 original visuals (3 per family), all 10 micro-exercise types in every
family, guided/independent/timed/mastery coverage in every family, 4 foundation modules,
7 family modules, and a 12-category error taxonomy.

Artifacts:

- `scripts/build_writing1_curriculum.py` → `web/writing1_data.js`
- `tests/g4_writing1_validation.py` — PASS
- `tests/g4_writing1_content_qa.py` — 115 prose claims re-derived, 0 failed
- `docs/writing1_content_qa.md`

Decisions logged: D-015 (mastery thresholds), D-016 (error taxonomy), D-017 (grounding
by re-derived facts), D-018 (toolchain).

**Outstanding for the G4 gate:**

- the Writing Task 1 UI (`web/app.js` route `task1` is still the `genericLab` placeholder)
- planning → timed drafting → self-review flow
- autosave and persistence across reload
- mastery enforcement against D-015
- error-log and review-queue integration
- responsive validation at 320/375/430/768/1024/1440
- accessibility validation of the new visual panel
- `docs/phase_4_report.md` and the gate decision

A UI mockup covering all of the above is published and awaiting design approval per
`CLAUDE.md` §29; the request is in the `#proj-ielts` thread dated 2026-09-04.

---

## Defects

| ID | Severity | Status | Note |
|---|---|---|---|
| D4-001 | P2 | **Fixed** | Four Playwright tests hard-coded `/usr/bin/chromium` and could not launch off Linux, so the browser-driven gate evidence was not reproducible on the development machine. `tests/browser_env.py` resolves a Chromium binary portably; all four now pass. |

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

Existing automated validation includes G2/G3, responsive, and accessibility tests.

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
