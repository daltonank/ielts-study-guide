# Lesia IELTS Academic C1 UA+EN Study Webapp
## Claude Project Context and Continuation Handoff

**Project owner:** Dalton  
**Primary learner:** Lesia / Olesia, advanced Ukrainian-speaking English learner  
**Target:** IELTS Academic, Band 7.0–8.0, with an operating target around Band 7.5  
**Current canonical build state:** G3 Reading Complete — PASS  
**Next implementation gate:** G4 Writing Task 1  
**Deployment rule:** Keep development as a local HTML build for now. Do **not** reconcile with or deploy over the public site until the local build is complete and passes the later release gates.

---

# 1. Purpose of This File

This document is the continuity layer for moving the IELTS Academic C1 UA+EN adaptive study webapp from ChatGPT/GPT-side development into Claude without losing product intent, learner context, technical decisions, curriculum architecture, validation rules, or build status.

Claude should treat this document as the project-level source of truth **only when it agrees with newer canonical release artifacts and gate reports**. Where older documents conflict with later reports, the newest passed gate/release wins.

The immediate objective is **not** to redesign the product from scratch. The immediate objective is to continue the approved build from the current G3 release, preserve all completed behavior, and implement the next approved phase under the existing validation framework.

---

# 2. Canonical Source Precedence

When files disagree, use this precedence order:

1. **Newest passed phase/gate report**
2. **Newest complete release HTML**
3. **Current source workbook / data source**
4. **Requirements ledger**
5. **Phase-specific QA notes**
6. **Earlier passed release HTML**
7. **Legacy site HTML**
8. **Historical benchmark snapshots / blocked gate reports**
9. **Old public deployed site**

Important consequence:

- `phase_2_gate_report.md` records an earlier G2 **BLOCKED** state caused by lack of raw workbook bytes. This is historical.
- The later G3 release contains a fully reconciled 1,784-record vocabulary payload and the G3 regression suite reports G2 vocabulary migration passing.
- Therefore, the **current truth is G2 PASS and G3 PASS**.
- `benchmark_dashboard.md` is also an older snapshot if it still says G2 blocked or Reading = 0. Treat its benchmark targets as useful, but not its old current-value column.

---

# 3. Learner and Product Context

This is a personal preparation system for Lesia/Olesia, an advanced Ukrainian-speaking learner preparing for IELTS Academic at approximately C1 level.

The system should help her move from strong general English to **exam-effective Band 7.0–8.0 performance**, particularly by converting passive knowledge into reliable timed output.

Core learner assumptions:

- Native / primary language support: Ukrainian.
- Exam language: English.
- English should dominate authentic exam-facing content.
- Ukrainian support should clarify difficult concepts, transfer errors, grammar differences, strategy, and vocabulary meaning without turning the interface into a full mirrored translation.
- The learner benefits from a low-friction, scrollable study experience rather than a dense LMS portal.
- Progress should feel practical and personal: diagnose weakness → train it → receive feedback → review errors → retest → advance mastery.
- Vocabulary breadth is already large; the system should prioritize **active use, collocations, paraphrasing, accuracy, and recall**, not rare-word accumulation.
- The website should make it obvious what to study next instead of forcing the learner to decide from a giant content catalog.

The product is personal and local-first. It is not currently intended to require account creation, a server database, payment infrastructure, or a public multi-user backend.

---

# 4. Primary Product Objective

Build one integrated **IELTS Academic C1 / Band 7.0–8.0 UA+EN adaptive study webapp** that:

- preserves the useful original Ukrainian/English study guide and vocabulary bank;
- provides diagnostic and baseline assessment;
- teaches every major IELTS Academic skill;
- contains substantial original practice banks;
- tracks mastery, errors, review debt, timing, and repeated weaknesses;
- recommends what the learner should study next and explains why;
- supports spaced review;
- supports full mock-test progression later in the build;
- remains calm, usable, mobile-first, and continuously scrollable;
- retains learner progress locally and allows export/import backup;
- uses British English conventions where appropriate;
- avoids copyrighted commercial IELTS passage reproduction;
- distinguishes training estimates from official IELTS band scoring.

The philosophy is **complete training system, not visual demo**.

---

# 5. Core Product Principles

## 5.1 Experience

Preserve the approved experience:

- calm academic presentation;
- mobile-first;
- continuous-scroll reading/study flow;
- low-friction interactions;
- compact navigation;
- clear visual hierarchy;
- useful cards and sections without dashboard clutter;
- strong phone usability at 320–430 px widths;
- responsive through tablet and desktop;
- accessibility as a first-class requirement.

## 5.2 Language Modes

Three modes are already part of the platform:

- `EN`
- `UA + EN`
- `UA Help`

Changing the language-support mode must **not destroy learner state**.

Use Ukrainian strategically for:

- strategy explanations;
- contrastive grammar;
- common Ukrainian → English transfer errors;
- vocabulary definitions/equivalents;
- difficult instructions;
- corrective feedback where it genuinely improves comprehension.

Do not translate every English sentence merely because a Ukrainian mode exists.

## 5.3 Local-first Data

Current state architecture is local-first.

Preserve:

- LocalStorage persistence;
- JSON export;
- JSON import;
- malformed-import rejection;
- pre-import backup snapshot;
- autosave where long responses are entered;
- persistent mastery;
- persistent error records;
- persistent review queue;
- practice and mock history as later phases expand.

Do not introduce a remote backend unless Dalton explicitly changes the architecture.

---

# 6. Existing Information Architecture

## Primary mobile navigation

Exactly five primary controls are part of the approved foundation:

1. Today
2. Skills
3. Practice
4. Words
5. Progress

## Secondary / drawer navigation

Existing platform architecture includes:

- Start Here
- Reading Lab
- Listening Lab
- Writing Task 1
- Writing Task 2
- Speaking Lab
- Grammar Clinic
- Paraphrasing
- Pronunciation
- Error Log
- Review Queue / Review Today
- Global Search
- Settings / Backup
- Component Lab

Do not replace this with a radically different information architecture unless there is a concrete usability defect.

---

# 7. Learning Architecture

The product should behave as an adaptive training loop:

**Diagnostic → targeted instruction → guided practice → independent practice → timed performance → feedback → error capture → review → mastery check → recommendation**

The learner should never receive mastery credit merely for opening or scrolling through a lesson.

The platform mastery scale is:

- **L0 — Not Assessed**
- **L1 — Introduced**
- **L2 — Guided**
- **L3 — Independent**
- **L4 — Timed**
- **L5 — Mastered**

The Reading phase established an important precedent that should be reused where appropriate:

- L1 requires explicit introduced/completed evidence.
- L2 is earned from guided work, not passive viewing.
- L3 requires unseen independent performance.
- L4 requires timed evidence.
- L5 requires repeated high performance across multiple sets/dates.

Exact thresholds may be skill-specific, but progression must remain evidence-based.

---

# 8. Vocabulary Source and Study Philosophy

Canonical vocabulary source:

`IELTS_Academic_C1_Ukrainian_Vocabulary_Bank.xlsx`

Workbook facts:

- 1,784 normalized / deduplicated study-bank entries.
- 1,315 Oxford C1 entries.
- 570 Academic Word List entries/families represented in the source workbook.
- 100 Oxford/AWL overlaps.
- Starter 100 active-use set.
- Ukrainian equivalents and definitions.
- Source metadata.
- IELTS priority.
- study status;
- confidence;
- review fields;
- collocation/original-use fields.

The original study workflow is:

**Study Bank → High priority → active use → review**

The workbook’s mastery concept should continue to influence the site:

A word is not truly mastered because its definition was seen. Mastery requires the learner to:

1. recognize the meaning;
2. recall the English word from Ukrainian;
3. select/use a natural collocation;
4. use it correctly in at least two separate IELTS-style responses.

The vocabulary bank is a **reference and prioritization system**, not a mandate to force every C1 word into active vocabulary.

High-value vocabulary use should emphasize:

- AWL sublists 1–3 first;
- high-priority rows;
- words emerging from Reading/Writing/Speaking errors;
- collocations;
- paraphrase families;
- register;
- productive use.

Avoid rare-word stuffing and pseudo-academic vocabulary inflation.

The G3 release embeds the reconciled vocabulary data and reports:

- `expectedCount: 1784`
- `sourceCount: 1784`
- `gate: G2 SOURCE RECONCILED`

This supersedes the earlier blocked G2 snapshot.

---

# 9. Completed Build Status

## G0 — Audit & Requirements Lock
**PASS**

Completed:

- stable requirements IDs;
- legacy inventory;
- risk register;
- initial regression framework;
- preservation rules for legacy functionality/content.

## G1 — Foundation & Design System
**PASS**

Delivered:

- responsive design tokens;
- continuous-scroll mobile-first shell;
- five-control primary navigation;
- secondary navigation drawer;
- EN / UA+EN / UA Help;
- reusable component primitives;
- Component Lab;
- learner-state, module, and exercise schemas;
- LocalStorage persistence shell;
- JSON export/import protections;
- mastery model 0–5;
- Today recommendation shell with visible reason;
- Review Today shell;
- error schema;
- writing autosave field;
- reusable timer;
- global search shell;
- vocabulary preview/search/state behavior;
- focus/accessibility primitives;
- reduced-motion behavior.

Target responsive widths already used:

- 320
- 375
- 430
- 768
- 1024
- 1440 px

## G2 — Legacy Integration & Vocabulary Migration
**CURRENT STATUS: PASS**

Historical note:
An earlier `phase_2_gate_report.md` says BLOCKED because raw `.xlsx` bytes were unavailable in that build runtime.

That block was later resolved by providing the source workbook. The release was reconciled at:

**1,784 / 1,784 records**

Current G3 regression evidence says:

**G2 vocabulary migration regression: PASS**

Claude must not reopen G2 unless an actual data-integrity defect is found.

## G3 — Reading Academy
**PASS**

Canonical release:

`IELTS_C1_UAEN_G3_Reading_Complete_Release.html`

Quantitative result:

- 8 / 8 Reading foundation strategies;
- 15 major question-family modules;
- 60 original practice texts/extracts;
- 240 scored Reading questions;
- 240 / 240 answer explanations;
- distractor rejection reasoning where relevant;
- responsive/accessibility regression passed;
- G2 vocabulary regression passed;
- zero open P0/P1/P2/P3 defects at gate.

### Reading foundation topics

1. IELTS Academic Reading structure
2. skimming
3. scanning
4. paraphrase recognition
5. reference words
6. vocabulary from context
7. evidence location
8. inference boundaries

### Reading question families

- Multiple Choice
- True / False / Not Given
- Yes / No / Not Given
- Matching Information
- Matching Headings
- Matching Features
- Matching Sentence Endings
- Sentence Completion
- Summary Completion
- Note Completion
- Table Completion
- Flow-chart Completion
- Diagram Label Completion
- Short Answer
- Inference & Author Position

### Reading module learning sequence

The established module pattern is:

**Learn → See → Think → Guided Practice → Independent Practice → Challenge → Timed Round → Review → Error Diagnosis → Mastery Check**

This is a strong pattern for future academies when pedagogically appropriate.

### Reading mastery thresholds

G3 uses:

- L1: explicit introduced action;
- L2: guided set accuracy ≥50%;
- L3: independent unseen-set accuracy ≥75%;
- L4: timed + mastery sets both inside target time and average ≥75%;
- L5: ≥85% across at least three distinct sets on at least two dates, including the mastery set.

### Reading error persistence

Wrong answers can persist:

- skill;
- module;
- question ID;
- learner answer;
- correct answer;
- error category;
- explanation;
- correction direction;
- repeated flag;
- review date;
- resolved status.

An incorrect Reading response also creates a review item unless that question is already queued.

### Reading content rule

The Reading bank uses **original synthetic training texts**, not copied commercial IELTS passages.

Focused extracts intentionally isolate mechanics. Full three-section realism belongs in the later Mock Center phase.

---

# 10. Current Next Step: G4 Writing Task 1

Claude should continue from the G3 canonical release into **Phase 4 / G4 — Writing Task 1**.

Do not rebuild Reading. Do not deploy publicly yet.

Approved G4 quantitative minimums:

- **7 visual families**
- **≥60 Task 1 micro-exercises**
- **≥20 full Task 1 prompts**

Writing Task 1 should cover the full Academic visual-analysis skill set. The seven-family benchmark should be implemented as a complete practical curriculum rather than a checkbox inventory.

Expected families include the normal Academic Task 1 visual forms, such as:

- line graphs;
- bar charts;
- pie charts;
- tables;
- process diagrams;
- maps/plans;
- mixed/multiple visuals.

The curriculum should train more than vocabulary. It should explicitly teach:

- understanding the task;
- selecting key features;
- identifying overview-worthy patterns;
- grouping information logically;
- comparing rather than listing;
- data-language precision;
- change/trend language;
- quantity/proportion language;
- approximate values;
- tense selection;
- sentence control;
- avoiding unsupported causal claims;
- avoiding personal opinions;
- overview construction;
- paragraph organization;
- lexical variation without distortion;
- grammar and article/preposition errors common for Ukrainian speakers;
- timed response planning and drafting;
- self-review.

Preserve autosave and local state.

Use original visuals/data created for the product unless official/open material is legally safe to use.

Do not present automated feedback as an official IELTS examiner score. If score-like feedback is used, clearly label it as practice guidance / estimate.

---

# 11. Approved Downstream Gates and Benchmarks

These targets are part of the approved master build direction and should remain intact unless Dalton explicitly revises them.

## G5 — Writing Task 2

Minimum content:

- **≥60 full Task 2 prompts**
- **≥100 micro-drills**
- **≥15 annotated model responses**
- **≥10 Band 6 / 7 / 8 comparison sets**
- **≥12 full timed simulations**

Must cover all major essay/task families, autosave, feedback framework, error capture, and regression.

Training should include:

- prompt interpretation;
- position/thesis;
- idea development;
- paragraph logic;
- evidence/examples;
- qualification;
- cohesion;
- coherence;
- grammar;
- vocabulary;
- conclusion control;
- timing;
- editing.

## G6 — Grammar, Paraphrasing, Pronunciation

Minimums:

- **≥20 grammar modules**
- **≥250 grammar items**
- **≥100 paraphrase exercises**
- pronunciation curriculum complete;
- Ukrainian → English transfer notes;
- error-log integration;
- regression pass.

Grammar should be contrastive and practical, especially where Ukrainian structures produce predictable English errors.

## G7 — Speaking + Practice Together

Minimum banks:

- **≥120 Part 1 questions**
- **≥75 Part 2 cue cards**
- **≥150 Part 3 questions**

Must include:

- timers;
- randomization;
- persistent feedback/history;
- Together Mode;
- progressive practice;
- useful self/partner practice flows;
- evidence-based mastery rather than mere completion.

## G8 — Listening

Gate requires:

- complete strategy curriculum;
- full Listening error taxonomy;
- legal/original/official resource flow;
- adaptive/review integration;
- regression.

Do not embed unauthorized copyrighted audio.

## G9 — Adaptive Engine, Review, Mock Center

Gate requires functional evidence that:

- seeded learner profiles produce expected recommendations;
- review scheduling works;
- recommendation reasons are visible;
- mock results change priorities;
- weak areas influence study selection;
- no learner-state loss occurs;
- Error Log, Review Queue, Today, Progress, and mock history operate as one system.

Mock Center should finally combine skills into realistic exam simulations rather than using the short focused extracts from earlier academies.

## G10 — Final QA and Release

Minimum release conditions include:

- **100% requirements traceability**
- **0 P0 defects**
- **0 P1 defects**
- accessibility automated target **≥95**
- performance target **≥90**
- export/import integrity
- final regression suite
- user acceptance flows
- release definition of done

No phase is complete merely because content exists. A phase closes only when its gate passes.

---

# 12. Validation System

The project operates under a repeat-until-complete validation loop:

**Plan → Build → Test → Review → Refine → repeat until gate passes**

For every phase:

1. Define requirements and success criteria.
2. Build only against the approved requirement set.
3. Run automated inventory/structural tests.
4. Run functional tests.
5. Run responsive tests.
6. Run accessibility checks.
7. Manually inspect representative content.
8. Run regression against all completed prior phases.
9. Log defects.
10. Fix defects.
11. Re-run tests.
12. Produce a phase checkpoint/gate report.
13. Do not advance if gate criteria fail.

## Defect discipline

Release philosophy:

- P0: release-blocking
- P1: gate/release-blocking
- P2: must be resolved at relevant gate unless explicitly accepted
- P3: minor; should not silently accumulate

Final G10 requires 0 P0/P1.

Claude should never write “implemented” as a synonym for “complete.”

---

# 13. Required QA Behavior

## Content QA

For every curriculum bank:

- verify answer correctness;
- verify distractors are defensible;
- verify explanations teach the reason, not merely state the answer;
- verify unique IDs;
- verify required fields;
- verify module references;
- verify scoring consistency;
- verify original/licensed source status;
- manually inspect samples from every family/type;
- inspect timed/mastery examples;
- check Ukrainian wording where used;
- ensure advanced but natural English.

## Accessibility

Maintain:

- semantic controls;
- visible keyboard focus;
- reasonable touch targets;
- no unintended horizontal overflow;
- reduced-motion support;
- readable contrast;
- appropriate form labeling;
- screen-reader-friendly state/status feedback.

## Responsive widths

Keep regression coverage at:

320 / 375 / 430 / 768 / 1024 / 1440 px

---

# 14. Copyright and Source Rules

Do not reproduce copyrighted commercial IELTS passages, audio, answer banks, or paid test-prep books.

Preferred content order:

1. original content written for this product;
2. official IELTS resources used as links/reference;
3. open/licensed material with clear rights;
4. short factual/descriptive references where legally appropriate.

For Reading and future mock banks, original synthetic content is acceptable and already established.

For official test format/scoring descriptors, link to the official authority rather than copying large protected sections.

---

# 15. Public Site and Deployment Rule

Known existing public/legacy site:

https://ielts-academic-study-guide.daltonankenbrand811.chatgpt.site/

This is **not** the current development authority.

Current instruction from Dalton:

> Keep the build local HTML for now. We will reconcile and deploy to the public site once the local build is complete.

Therefore:

- do not overwrite the public site;
- do not simplify the local build merely to match the older deployed site;
- do not treat the deployed site as canonical when it conflicts with G3;
- later reconciliation should be a deliberate release activity.

---

# 16. Official / Supporting Links Already Used

These links are safe reference points for test format and preparation context:

## IELTS official
https://ielts.org/

Academic sample questions:
https://www.ielts.org/take-a-test/preparation-resources/sample-test-questions/academic-test

Academic Writing format:
https://ielts.org/take-a-test/test-types/ielts-academic-test/ielts-academic-format-writing

Academic Speaking format:
https://ielts.org/take-a-test/test-types/ielts-academic-test/ielts-academic-format-speaking

## British Council Ukraine
https://www.britishcouncil.org.ua/en/exam/ielts

Preparation:
https://www.britishcouncil.org.ua/exam/ielts/prepare

## IDP IELTS
https://ielts.idp.com/prepare

Academic preparation:
https://ielts.idp.com/about/academic-preparation

Claude should verify current official URLs if external browsing is available before adding new links.

---

# 17. Files Claude Should Receive

## Tier A — Required to continue correctly

### 1. This context file
`LESIA_IELTS_CLAUDE_CONTEXT.md`

Purpose:
Project memory, precedence rules, current status, product direction, learner context, benchmarks, and continuation instructions.

### 2. Latest canonical application release
`IELTS_C1_UAEN_G3_Reading_Complete_Release.html`

Purpose:
This is the current working application state and should be the implementation baseline for G4.

### 3. Canonical vocabulary workbook
`IELTS_Academic_C1_Ukrainian_Vocabulary_Bank.xlsx`

Purpose:
Raw source of the 1,784-record vocabulary bank and original study model.

### 4. Requirements ledger
`requirements_ledger.csv`

Purpose:
Stable requirement IDs and traceability framework.

### 5. Current phase report
`phase_3_report.md`

Purpose:
Authoritative evidence that G3 passed and exact Reading benchmarks/behavior.

### 6. Reading QA note
`reading_content_qa.md`

Purpose:
Defines the manual content-quality precedent and clarifies focused practice vs full mocks.

## Tier B — Strongly recommended for full historical/technical coverage

### 7. G1 platform release
`IELTS_C1_UAEN_G1_Platform_Release.html`

Purpose:
Useful regression/reference point for the platform foundation.

### 8. Legacy v2 study guide
`ielts_c1_ukrainian_study_guide_v2.html`

Purpose:
Preserves the pre-master-build product concept, original Today/error/practice behavior, and the old public-bank linkage.

### 9. Phase 0 report
`phase_0_report.md`

Purpose:
Initial audit, scope lock, legacy facts, and early risks.

### 10. Phase 1 report
`phase_1_report.md`

Purpose:
Foundation/design-system gate evidence.

### 11. Historical Phase 2 blocked report
`phase_2_gate_report.md`

Purpose:
Useful audit trail showing why G2 was originally blocked.

**Warning to Claude:** historical only; G2 was later resolved.

### 12. Historical benchmark dashboard
`benchmark_dashboard.md`

Purpose:
Contains approved quantitative benchmarks.

**Warning to Claude:** current-value/status cells may be stale. Use later gate reports for actual status.

### 13. Build-cycle infographic
`International Education Webapp Plan Infographic.png`

Purpose:
Visual overview of Plan → Build → Test → Review → Refine and phase progression.

## Tier C — Include if available from the local build workspace

The requirements ledger indicates that earlier implementation work also used a structured workspace. If these files/directories still exist locally, provide them to Claude, preferably as one zip archive:

`IELTS_C1_UAEN_BUILD_WORKSPACE.zip`

The archive should include, where available:

### Web source
- `web/index.html`
- `web/styles.css`
- `web/app.js`

### Schemas
- `schemas/learner_state.schema.json`
- `schemas/module.schema.json`
- `schemas/exercise.schema.json`

### Docs
- `docs/requirements_ledger.csv`
- `docs/legacy_content_inventory.csv`
- `docs/regression_checklist.md`
- `docs/risk_register.csv`

### Migration / build scripts
- `scripts/migrate_vocabulary.py`
- any script that produced the reconciled G2 payload
- any release/build script

### G3 tests
- `g3_reading_validation.py`
- `g3_reading_functional.py`
- `g3_reading_responsive.py`
- `g3_reading_accessibility.py`

### Permanent tests
- responsive regression test/suite
- static accessibility suite
- build static validator
- vocabulary migration regression test

### Generated data, if separate from the release
- reconciled vocabulary JSON/JS payload
- Reading module bank/data
- Reading passage/question bank
- migration manifest

If these source/test artifacts are unavailable, Claude can still proceed from the canonical G3 single-file HTML, but complete workspace transfer is preferable because it preserves automated validation infrastructure.

---

# 18. Links Dalton Should Give Claude

Submit these alongside the file bundle:

## Required project reference
**Legacy/public site**
https://ielts-academic-study-guide.daltonankenbrand811.chatgpt.site/

Tell Claude explicitly:
“This URL is a legacy/public reference only. The local G3 release is canonical.”

## Official exam references
- https://ielts.org/
- https://www.ielts.org/take-a-test/preparation-resources/sample-test-questions/academic-test
- https://ielts.org/take-a-test/test-types/ielts-academic-test/ielts-academic-format-writing
- https://ielts.org/take-a-test/test-types/ielts-academic-test/ielts-academic-format-speaking
- https://www.britishcouncil.org.ua/en/exam/ielts
- https://www.britishcouncil.org.ua/exam/ielts/prepare
- https://ielts.idp.com/prepare
- https://ielts.idp.com/about/academic-preparation

If a GitHub repository is later created for this specific IELTS build, add that repository URL to this section and make it the implementation workspace. At present, the project direction is local HTML first.

---

# 19. Claude Startup Instructions

Use the following operating protocol when beginning work:

1. Read `LESIA_IELTS_CLAUDE_CONTEXT.md`.
2. Inspect `phase_3_report.md`.
3. Inspect `IELTS_C1_UAEN_G3_Reading_Complete_Release.html`.
4. Inspect `requirements_ledger.csv`.
5. Inspect the workbook structure and vocabulary fields.
6. Read `reading_content_qa.md`.
7. Read earlier reports only for historical decisions and regressions.
8. Confirm internally that current gates are:
   - G0 PASS
   - G1 PASS
   - G2 PASS
   - G3 PASS
   - G4 NEXT
9. Do not reopen completed gates absent an actual regression.
10. Build G4 Task 1 against the approved benchmarks.
11. Preserve all completed G1–G3 functionality.
12. Extend the existing state/error/review/mastery architecture instead of creating a parallel system.
13. Add automated G4 inventory, functional, responsive, accessibility, and regression tests.
14. Produce a G4 gate report after validation.
15. Do not deploy publicly.

---

# 20. Suggested First Claude Task

Use this as the first execution request after the files are attached:

> Read the supplied `LESIA_IELTS_CLAUDE_CONTEXT.md` first, then inspect the G3 canonical release, Phase 3 report, requirements ledger, Reading QA note, and vocabulary workbook. Treat G0–G3 as passed, with the later G3 artifacts superseding stale G2-blocked and Reading-zero snapshots. Continue the existing local-first single-page UA+EN application into **G4 Writing Task 1**. Preserve every completed regression behavior, build the complete Task 1 curriculum to the approved benchmark of seven visual families, at least 60 micro-exercises, and at least 20 full prompts, integrate mastery/error/review/local-state behavior, create original practice visuals/data, and run the project validation loop until the G4 gate passes. Do not deploy or reconcile with the public site yet. Produce a phase checkpoint report and updated benchmark/requirements evidence at completion.

---

# 21. Anti-Regression Rules

Claude should not:

- replace the current application with a superficial new prototype;
- remove the 1,784-word vocabulary bank;
- discard local learner state;
- change the five-item primary navigation without a demonstrated defect;
- translate everything into Ukrainian;
- reduce the project to static study notes;
- remove timers, review, errors, mastery, search, backup, or adaptive foundations;
- grant mastery from page views;
- copy commercial IELTS content;
- call practice estimates “official IELTS scores”;
- mark phases complete without passing their gates;
- trust stale historical “current status” fields over newer gate evidence;
- deploy to the public site before the local build is complete.

---

# 22. Product Direction in One Sentence

Build a calm, rigorous, bilingual IELTS Academic training system that turns Lesia’s strong English into repeatable Band 7–8 exam performance through targeted practice, evidence-based mastery, error-driven review, and increasingly realistic timed simulation.

---

# 23. Current Handoff Snapshot

**As of 2026-09-04:**

- Product direction: locked.
- Local-first architecture: locked.
- Public deployment: deferred.
- Vocabulary: 1,784 / 1,784 reconciled.
- G0: PASS.
- G1: PASS.
- G2: PASS.
- G3 Reading: PASS.
- Reading inventory: 60 texts / 240 scored questions / 100% explanations.
- Next gate: G4 Writing Task 1.
- G4 minimums: 7 visual families / ≥60 micro-exercises / ≥20 full prompts.
- Future quantitative gates: retained as listed above.
- Highest priority: advance the local application without regressing completed work.

