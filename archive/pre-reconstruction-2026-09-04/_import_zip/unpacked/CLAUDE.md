# CLAUDE.md

## Claude Code Operating Instructions

This repository contains the active **IELTS Academic C1 UA+EN Adaptive Study Webapp**.

The repository is an existing product. Do not restart it as a new prototype.

---

## 1. Startup Protocol

Before substantial implementation:

1. read `PROJECT_CHARTER.md`;
2. read `CURRENT_STATE.md`;
3. read `DECISIONS.md`;
4. read the specification relevant to the active task;
5. inspect `docs/requirements_ledger.csv`;
6. inspect the newest passed phase report;
7. inspect the current source implementation;
8. establish baseline test status;
9. identify the exact active requirement;
10. then implement.

Do not ask the user to restate context that is discoverable in these files.

---

## 2. Current State

Current passed gates:

- G0 PASS
- G1 PASS
- G2 PASS
- G3 PASS

Next approved gate:

**G4 Writing Task 1**

Current deployment constraint:

**Local HTML only. Do not deploy or reconcile with the public site yet.**

---

## 3. Authority Order

Use:

1. `PROJECT_CHARTER.md`
2. `PRODUCT_SPEC.md`
3. `CURRICULUM_SPEC.md`
4. `UX_DESIGN_SPEC.md`
5. `VALIDATION_SPEC.md`
6. approved `DECISIONS.md`
7. `CURRENT_STATE.md`
8. requirements ledger / newest passed phase report
9. implementation
10. historical/archive material

A newer approved decision may explicitly supersede earlier material.

Do not silently choose a convenient interpretation when sources conflict.

---

## 4. Canonical Implementation

Primary source:

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

Migration/build scripts live under `scripts/`.

Validation lives under `tests/`.

The large single-file releases under `releases/` are release/reference artifacts, not a reason to discard the structured source tree.

---

## 5. Do Not Regress

Preserve:

- five-item primary navigation;
- EN / UA+EN / UA Help;
- local learner state;
- export/import;
- 1,784-word vocabulary source reconciliation;
- G3 Reading content and mastery behavior;
- Error Log / Review foundations;
- search;
- timers;
- autosave foundations;
- responsive behavior;
- accessibility primitives.

---

## 6. Do Not Silently Redefine

Require a documented decision before changing:

- target IELTS band;
- bilingual philosophy;
- pedagogy;
- mastery model;
- information architecture;
- phase definitions;
- quantitative gates;
- scoring philosophy;
- local-first architecture;
- deployment timing.

You may recommend changes. Separate recommendations from approved requirements.

---

## 7. Implementation Discipline

For substantial work:

1. identify requirement IDs;
2. identify affected files;
3. state acceptance criteria;
4. inspect dependencies;
5. implement coherently;
6. avoid unrelated refactors;
7. test actual behavior;
8. run responsive/accessibility checks where relevant;
9. run regression;
10. update requirement evidence;
11. update `CURRENT_STATE.md`;
12. update `CHANGELOG.md`;
13. update `DECISIONS.md` only for meaningful approved decisions;
14. produce/update the phase report.

Do not equate code presence with completion.

---

## 8. Current G4 Mandate

Continue into Writing Task 1.

Minimums:

- 7 visual families;
- ≥60 micro-exercises;
- ≥20 full prompts.

Integrate with:

- mastery;
- errors;
- review;
- persistence;
- autosave;
- timers;
- Today/recommendation foundation;
- responsive visual handling;
- accessibility;
- content QA.

Preserve G0–G3 regressions.

Do not deploy publicly.

---

## 9. End-of-Work Report

After substantial work report:

### Implemented
Concrete changes.

### Validated
Tests actually run and results.

### Remaining
Incomplete current-gate work.

### Files Changed
Meaningful files.

### Decisions
Only new approved/significant decisions.

### Known Issues
Unresolved defects or risks.

### Next Task
The next dependency-appropriate requirement.

Leave repository state more understandable than you found it.
