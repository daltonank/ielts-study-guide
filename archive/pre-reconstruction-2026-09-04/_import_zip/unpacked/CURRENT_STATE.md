# CURRENT_STATE.md

**Updated:** 2026-09-04  
**Current canonical gate:** G3 Reading Complete — PASS  
**Next gate:** G4 Writing Task 1  
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

### G4 — Writing Task 1

Minimum gate:

- 7 visual families
- ≥60 micro-exercises
- ≥20 full prompts

Required integrations:

- mastery
- errors
- review
- autosave
- local persistence
- timers
- responsive visual rendering
- accessibility
- content QA
- prior-phase regression

---

## Current Source Tree

Primary implementation:

- `web/index.html`
- `web/styles.css`
- `web/app.js`
- `web/data.js`
- `web/vocabulary.js`
- `web/reading_data.js`

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
