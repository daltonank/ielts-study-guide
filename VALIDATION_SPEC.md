# VALIDATION_SPEC.md

## IELTS Academic C1 • UA+EN Validation and Gate Specification

The project uses evidence-based phase closure.

**Implemented is not equivalent to complete.**

---

## 1. Validation Loop

For every phase:

1. define requirements and success criteria;
2. implement only against the approved requirement set;
3. run structural/static validation;
4. run functional validation;
5. run responsive validation;
6. run accessibility checks;
7. run content QA;
8. run data QA where applicable;
9. run regression against completed phases;
10. reconcile the requirements ledger;
11. record defects;
12. repair defects;
13. rerun failed validation;
14. produce/update the gate report;
15. advance only when the gate passes.

---

## 2. Traceability

Every major requirement should map to:

**Requirement → implementation artifact → validation evidence → status**

The canonical ledger is:

`docs/requirements_ledger.csv`

Stable IDs must be preserved.

Do not renumber existing requirements simply for stylistic consistency.

---

## 3. Defect Severity

### P0
Catastrophic or release-blocking:
- data loss;
- app unusable;
- severe corruption;
- fundamental security/privacy defect.

### P1
Gate-blocking:
- core required functionality broken;
- major learner workflow unavailable;
- significant regression;
- required accessibility or responsive failure.

### P2
Material quality defect:
- requirement partially works;
- significant content or UX deficiency;
- should be resolved before the relevant gate unless explicitly accepted.

### P3
Minor:
- cosmetic or low-impact issue.

P3 defects should not silently accumulate.

G10 requires 0 open P0 and P1 defects.

---

## 4. Static / Structural Validation

Check as appropriate:

- expected files;
- required data fields;
- unique IDs;
- module references;
- schema validity;
- navigation counts;
- source counts;
- explanation coverage;
- required curriculum-family coverage;
- stale placeholders;
- duplicate records.

Existing utility:

`scripts/validate_build.py`

---

## 5. Functional Validation

Exercise the actual learner flow.

Check as appropriate:

- navigation;
- scoring;
- answer persistence;
- state reload;
- mastery transitions;
- timing evidence;
- error creation;
- review creation;
- language-mode state preservation;
- export/import;
- malformed-import rejection;
- autosave;
- search;
- filters.

Automated browser tests should be used where available.

---

## 6. Responsive Validation

Required widths:

320 / 375 / 430 / 768 / 1024 / 1440 px.

Validate:

- no unintended horizontal overflow;
- primary navigation;
- drawers;
- passages;
- question forms;
- writing inputs;
- vocabulary;
- feedback;
- charts/visuals;
- timers;
- language modes.

Permanent baseline test:

`tests/responsive_check.py`

---

## 7. Accessibility Validation

Validate:

- semantic elements;
- form labels;
- keyboard focus;
- control roles;
- status messages;
- reduced-motion behavior;
- readable structure;
- accessible feedback;
- chart/visual alternatives where appropriate.

Existing tests include:

- `tests/accessibility_static.py`
- `tests/g3_reading_accessibility.py`

Each new academy should add skill-specific accessibility checks where needed.

---

## 8. Content QA

Every curriculum family requires representative manual review.

Check:

- answer correctness;
- ambiguity;
- distractor defensibility;
- explanation quality;
- level appropriateness;
- natural English;
- Ukrainian quality where present;
- copyright/source status;
- task authenticity;
- internal consistency;
- unsupported scoring claims.

For generated practice, passing structural tests does not replace manual content review.

---

## 9. Data QA

For migrated/generated data:

- source counts reconcile;
- IDs are unique;
- required fields are present;
- encoding is valid;
- Ukrainian text is preserved;
- duplicates are detected;
- generation is deterministic where practical;
- source lineage is documented.

Vocabulary gate requires exact reconciliation of 1,784 normalized Study Bank entries.

---

## 10. Regression

Every later phase must rerun the relevant permanent checks for earlier completed phases.

A new academy cannot pass by breaking:

- navigation;
- language support;
- persistence;
- vocabulary;
- Reading;
- backup;
- responsive behavior;
- accessibility.

Regression evidence should appear in the gate report.

---

## 11. Gate Definitions

### G0 — Scope Locked
Requires:
- requirements ledger;
- legacy inventory;
- risk register;
- baseline regression checklist;
- stable IDs;
- known legacy dispositions.

Current status: PASS.

### G1 — Platform Stable
Requires:
- responsive foundation;
- design tokens/components;
- five-item navigation;
- language modes;
- state schema;
- persistence;
- backup;
- mastery foundation;
- Today/review/error shells;
- responsive/accessibility pass.

Current status: PASS.

### G2 — Legacy Fully Integrated
Requires:
- source vocabulary migration;
- exact 1,784 reconciliation;
- duplicate/blank/encoding checks;
- search/filter behavior;
- persistence compatibility;
- regression.

Current status: PASS.

### G3 — Reading Complete
Requires:
- 8 foundation strategies;
- 15 major question families;
- at least 50 original texts;
- at least 200 scored questions;
- 100% answer explanations;
- meaningful progression modes;
- timed evidence;
- error/review integration;
- mastery evidence;
- responsive/accessibility/regression pass.

Actual result:
- 60 texts
- 240 questions
- 100% explanations

Current status: PASS.

### G4 — Writing Task 1
Requires at minimum:
- 7 visual families;
- ≥60 micro-exercises;
- ≥20 full prompts;
- key-feature and overview training;
- data-language precision;
- grouping/comparison;
- planning/drafting/review;
- original/legal visuals;
- autosave/persistence;
- error/mastery/review integration;
- responsive chart/visual validation;
- accessibility;
- content QA;
- G0–G3 regression.

Actual result:
- 7 visual families
- 70 micro-exercises
- 21 full timed prompts
- 7 band comparison sets, one per visual family
- responsive and accessibility evidence for all seven families at the six required widths
- obstruction, persistence, export/import and keyboard-only evidence

Current status: **G4 INTERNAL PASS — EXTERNAL REVIEW PENDING**. All internal requirements pass; see
`docs/G4_EXTERNAL_REVIEW_PACKET.md`. A gate is not recorded as PASS until the planned
cross-provider review has actually occurred.

### G5 — Writing Task 2
Requires at minimum:
- ≥60 prompts;
- ≥100 micro-drills;
- ≥15 annotated models;
- ≥10 Band 6/7/8 comparisons;
- ≥12 timed simulations;
- major essay families;
- autosave;
- criteria-aligned feedback;
- error/mastery/review;
- regression.

### G6 — Grammar, Paraphrasing, Pronunciation
Requires:
- ≥20 grammar modules;
- ≥250 grammar items;
- ≥100 paraphrase exercises;
- pronunciation curriculum;
- Ukrainian transfer notes;
- error/review integration;
- regression.

### G7 — Speaking & Practice Together
Requires:
- ≥120 Part 1 questions;
- ≥75 Part 2 cue cards;
- ≥150 Part 3 questions;
- timers;
- randomization;
- persistent history;
- Practice Together;
- feedback;
- mastery;
- regression.

### G8 — Listening
Requires:
- complete strategy curriculum;
- complete Listening error taxonomy;
- legal/original/official audio/resource flow;
- practice/review integration;
- regression.

### G9 — Adaptive Engine, Review & Mock Center
Requires evidence that:
- seeded profiles produce expected recommendations;
- recommendation reasons are visible;
- review scheduling works;
- mock results change priorities;
- weak areas influence Today;
- state is retained;
- Error Log, Review, Today, Progress, and history behave coherently.

### G10 — Final QA & Release
Requires:
- 100% requirements traceability;
- 0 P0;
- 0 P1;
- accessibility automated target ≥95;
- performance target ≥90;
- export/import integrity;
- final regression;
- user acceptance flows;
- release definition of done.

---

## 12. Gate Report Template

Each phase report should record:

- phase and gate;
- decision;
- requirements;
- delivered artifacts;
- quantitative counts;
- tests run;
- content QA;
- data QA;
- responsive evidence;
- accessibility evidence;
- regression;
- defects by severity;
- risks;
- explicit PASS/BLOCKED decision.

---

## 13. Truthfulness Rule

Never claim:

- fully tested if only static inspection occurred;
- mobile validated without target-width testing;
- accessible based only on visual appearance;
- adaptive when recommendations are static;
- persistent when state resets;
- complete when only placeholders exist;
- official IELTS scoring when feedback is an estimate.

Validation language must match evidence.
