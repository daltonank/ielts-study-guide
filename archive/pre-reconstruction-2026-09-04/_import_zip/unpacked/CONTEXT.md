# CONTEXT.md

## Active Project Context

This repository is the local-first build of the **IELTS Academic C1 UA+EN Adaptive Study Webapp** for an advanced Ukrainian-speaking learner targeting IELTS Academic Band 7.0–8.0.

### Current truth

- G0 Audit & Requirements Lock: PASS
- G1 Foundation & Design System: PASS
- G2 Legacy/Vocabulary Integration: PASS
- G3 Reading Academy: PASS
- G4 Writing Task 1: NEXT
- public deployment: deferred
- canonical vocabulary count: 1,784 normalized Study Bank records
- canonical Reading inventory: 60 original texts / 240 scored questions / 100% explanations

### Development model

Use the structured source tree under `web/`, not only the release HTML.

Current runtime is static HTML/CSS/JavaScript with local learner state.

### Canonical project documents

Read in this order:

1. `PROJECT_CHARTER.md`
2. `PRODUCT_SPEC.md`
3. `CURRICULUM_SPEC.md`
4. `UX_DESIGN_SPEC.md`
5. `VALIDATION_SPEC.md`
6. `DECISIONS.md`
7. `CURRENT_STATE.md`
8. `docs/requirements_ledger.csv`
9. newest passed phase report

### Detailed historical handoff

`LESIA_IELTS_CLAUDE_CONTEXT.md` contains the detailed pre-repository continuity package, learner context, phase benchmarks, official reference links, and historical source-precedence notes.

Treat it as supporting context. Where it conflicts with the newer canonical specification set, use the canonical root specifications unless an approved decision says otherwise.

### Key implementation paths

- app: `web/`
- schemas: `schemas/`
- build/migration scripts: `scripts/`
- tests: `tests/`
- evidence/reports: `docs/`
- vocabulary source: `source/IELTS_Academic_C1_Ukrainian_Vocabulary_Bank.xlsx`
- release snapshots: `releases/`
- legacy app: `legacy/`

### Immediate implementation target

Proceed with **G4 Writing Task 1** against the approved gate:

- 7 visual families;
- ≥60 micro-exercises;
- ≥20 full prompts;
- mastery/error/review integration;
- original/legal visual data;
- autosave and persistence;
- responsive and accessible visual rendering;
- G0–G3 regression.

Do not redeploy the public site.
