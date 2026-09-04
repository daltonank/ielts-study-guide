# PRODUCT_SPEC.md

## IELTS Academic C1 • UA+EN Adaptive Study Webapp Product Specification

This specification defines the product behavior required by the Project Charter. Requirement identifiers reference `docs/requirements_ledger.csv` where applicable.

---

## 1. Product Summary

The application is a local-first, mobile-first IELTS Academic training platform for an advanced Ukrainian-speaking learner targeting Band 7.0–8.0.

It must combine instruction, practice, error analysis, mastery, review, progress, and later mock examinations into one coherent learner loop.

---

## 2. Functional Product Areas

### 2.1 Today

Purpose: make the learner's next action obvious.

The Today experience should surface:

- a recommended study target;
- a visible explanation of why it is recommended;
- review debt;
- unfinished or weak skills;
- an appropriate session length;
- quick access to resume recent work.

Supported study-time presets:

- 10 minutes
- 20 minutes
- 30 minutes
- 45 minutes
- 60 minutes
- 90 minutes

Recommendations must eventually respond to learner evidence rather than remain permanently static.

Relevant requirements: REQ-002D, REQ-035, REQ-036, REQ-036A.

---

### 2.2 Skills

Skills is the structured curriculum entry point.

It must accommodate:

- Reading;
- Writing Task 1;
- Writing Task 2;
- Listening;
- Speaking;
- Grammar;
- Paraphrasing;
- Pronunciation.

Each academy may use a skill-specific learning sequence, but progression should normally include instruction, guided practice, independent practice, timed evidence, feedback, review, and mastery checks.

---

### 2.3 Practice

Practice should allow focused work independent of long lessons.

It should eventually support:

- question-type drills;
- mixed practice;
- timed practice;
- error-driven practice;
- mastery checks;
- randomized speaking practice;
- later mock simulations.

Practice results should feed shared learner state.

---

### 2.4 Words

The vocabulary system uses the canonical workbook:

`source/IELTS_Academic_C1_Ukrainian_Vocabulary_Bank.xlsx`

Required source reconciliation:

- Oxford C1: 1,315
- Academic Word List: 570
- normalized Study Bank: 1,784
- Oxford/AWL overlaps: 100
- Starter 100: 100

Vocabulary behavior should include:

- search;
- filtering;
- source metadata;
- topic;
- priority;
- study status;
- confidence;
- Ukrainian equivalent/definition;
- collocation or word-family information where present;
- review fields;
- productive-use evidence.

Vocabulary should prioritize active use rather than rare-word accumulation.

Relevant requirements: REQ-011, REQ-012, REQ-011A, REQ-012A.

---

### 2.5 Progress

Progress should eventually synthesize:

- mastery by skill/module;
- recent practice;
- repeated errors;
- review debt;
- vocabulary progress;
- study history;
- timing trends;
- mock performance;
- recommended priorities.

Progress must distinguish exposure from demonstrated mastery.

Relevant requirements: REQ-014, REQ-039, REQ-040.

---

## 3. Diagnostic System

The diagnostic system must establish a useful baseline rather than merely produce a decorative score.

It should eventually identify:

- skill strengths/weaknesses;
- question-type weaknesses;
- grammar patterns;
- vocabulary limitations;
- timing problems;
- error categories.

Diagnostic results should become inputs to the adaptive recommendation model.

Relevant requirement: REQ-013.

---

## 4. Mastery Model

Global scale:

- L0 — Not Assessed
- L1 — Introduced
- L2 — Guided
- L3 — Independent
- L4 — Timed
- L5 — Mastered

Rules:

- opening or scrolling content never grants mastery;
- advancement requires skill-appropriate evidence;
- timed mastery requires timing evidence;
- L5 should require repeated high-quality performance rather than a single lucky set;
- mastery evidence must survive reload.

Reading precedent:

- L2: guided accuracy ≥50%;
- L3: independent unseen-set accuracy ≥75%;
- L4: timed + mastery sets inside target time with average ≥75%;
- L5: ≥85% across at least three distinct sets on at least two dates, including mastery evidence.

Other academies may define equivalent skill-specific thresholds.

Relevant requirement: REQ-014 / REQ-014A.

---

## 5. Error Log

Error records should support:

- skill;
- module;
- item/question ID;
- learner answer;
- correct or target answer;
- error category;
- explanation;
- correction direction;
- repeated flag;
- review date;
- resolution state.

Errors should be available to the review/recommendation system.

Relevant requirements: REQ-033, REQ-033A.

---

## 6. Review Queue

Review should surface work that needs deliberate re-exposure.

The system should support:

- queued incorrect items;
- recurring error patterns;
- due vocabulary;
- later spaced skill review;
- resolution or successful retest.

Duplicate review items should be avoided where reasonable.

Relevant requirements: REQ-034, REQ-034A.

---

## 7. Adaptive Recommendation Engine

The later adaptive engine should use real evidence, including:

- diagnostics;
- mastery state;
- recent accuracy;
- repeated errors;
- review due dates;
- time-on-task/timing evidence;
- mock performance;
- skill recency.

A recommendation must expose a human-readable reason.

Seeded learner profiles must produce predictable, testable recommendations.

Relevant requirements: REQ-035, REQ-036, REQ-037.

---

## 8. Mock Test Center

The Mock Center is a later-phase system for increasingly realistic test simulation.

It should support:

- skill-level timed simulations;
- later multi-section realistic flows;
- persistent results;
- error capture;
- history;
- priority updates.

Earlier academies may use focused extracts or partial tasks. These must not be mislabeled as full exam realism.

Relevant requirement: REQ-038.

---

## 9. Search

Global search should eventually cover supported curriculum and learner-facing data such as:

- lessons;
- vocabulary;
- practice;
- resource references;
- relevant saved/review items where appropriate.

Existing search behavior must not be regressed as later phases are added.

Relevant requirements: REQ-041, REQ-041A.

---

## 10. Backup and Persistence

Current state namespace:

`ieltsC1UAEN.state.v1`

Required behavior:

- LocalStorage persistence;
- state survives reload;
- JSON export;
- JSON import;
- malformed import rejection;
- current-state backup snapshot before valid replacement;
- autosave for long learner responses;
- compatibility with future larger-record storage if needed.

No remote backend is required during the current build.

Relevant requirements: REQ-008, REQ-009, REQ-009A/B/C.

---

## 11. Language Support

Modes:

- `en`
- `uaen`
- `uahelp`

Changing modes must not erase learner state.

English remains primary for authentic exam content.

Ukrainian should be used strategically for:

- difficult strategy;
- grammar contrast;
- transfer errors;
- vocabulary meaning;
- instructions;
- corrective explanation.

Relevant requirements: REQ-002C.

---

## 12. Primary Navigation

Mobile primary navigation contains exactly:

1. Today
2. Skills
3. Practice
4. Words
5. Progress

Additional functions belong in secondary navigation.

Relevant requirements: REQ-004, REQ-004A.

---

## 13. Content Quality

Every scored item should be checked for:

- unique ID;
- valid module reference;
- answer correctness;
- required fields;
- scoring consistency;
- plausible distractors;
- explanation quality;
- originality/licensing status.

For text-grounded Reading items, answer reasoning should identify the evidence or relationship in the text.

Writing and Speaking feedback must not pretend to be official examiner scoring.

Relevant requirements: REQ-043, REQ-044.

---

## 14. Nonfunctional Requirements

### Mobile/responsive
Target widths:
320 / 375 / 430 / 768 / 1024 / 1440 px.

No unintended horizontal overflow.

### Accessibility
Maintain:
- semantic controls;
- keyboard accessibility;
- visible focus;
- reasonable touch targets;
- readable contrast;
- labeled forms;
- status feedback;
- reduced-motion behavior.

### Privacy
No required analytics, trackers, accounts, or remote learner-data collection.

### Maintainability
Prefer structured data and reusable patterns over duplicated hard-coded curriculum.

### Integrity
Do not silently discard learner data or source vocabulary records.

---

## 15. Current Product State

Passed:

- G0 Audit & Requirements Lock
- G1 Foundation & Design System
- G2 Vocabulary/Legacy Integration
- G3 Reading Academy

Current implementation baseline:

- `web/index.html`
- `web/styles.css`
- `web/app.js`
- `web/data.js`
- `web/vocabulary.js`
- `web/reading_data.js`

Next product target:

**G4 Writing Task 1**

The product remains local HTML during active development.
