# PROJECT_CHARTER.md

## IELTS Academic C1 • UA+EN Adaptive Study Webapp

**Project owner:** Dalton  
**Primary learner:** Lesia / Olesia  
**Exam:** IELTS Academic  
**Target:** Band 7.0–8.0, operating target around 7.5  
**Language model:** English-first with strategic Ukrainian support  
**Runtime direction:** local-first static HTML/CSS/JavaScript during the build  
**Current canonical gate:** G3 Reading Complete — PASS  
**Next gate:** G4 Writing Task 1  
**Public deployment:** deferred until the local build reaches release readiness

---

## 1. Mission

Build one integrated, rigorous, bilingual IELTS Academic preparation system that converts a strong general-English learner into a reliable Band 7–8 test performer through explicit exam instruction, targeted practice, evidence-based mastery, error-driven review, and increasingly realistic timed simulation.

The product is not a vocabulary page, a static study guide, a content demo, or a generic English-learning website. It is a durable learner-facing training system.

---

## 2. Learner

The primary learner is an advanced Ukrainian-speaking English learner whose vocabulary breadth is already substantial. The system should therefore prioritize exam application rather than elementary language exposure.

The product should help the learner:

- understand the structure and expectations of IELTS Academic;
- identify what each task is actually testing;
- apply existing English knowledge under exam conditions;
- improve comprehension, analysis, grammar, sentence control, and precision;
- learn to select relevant evidence and information;
- recognize paraphrases and distractors;
- produce organized, accurate written and spoken responses;
- convert passive vocabulary into natural productive vocabulary;
- identify recurring errors;
- review weaknesses on a schedule;
- build timed performance gradually;
- know what to study next without navigating a giant undifferentiated content catalog.

The learner prefers a low-friction, scrollable format. Mobile use is a first-class use case.

---

## 3. Product Objective

The final application must integrate:

1. IELTS Academic orientation and diagnostics.
2. Reading Academy.
3. Writing Task 1 Academy.
4. Writing Task 2 Academy.
5. Ukrainian–English Grammar Clinic.
6. Paraphrasing Academy.
7. Pronunciation training.
8. Speaking Academy.
9. Listening Academy.
10. C1 vocabulary and selected C2 extension content.
11. Error Log.
12. Review Queue / Review Today.
13. evidence-based mastery tracking.
14. timed practice.
15. adaptive study recommendations with visible reasons.
16. study history and progress reporting.
17. mock-test progression.
18. local persistence and data backup/export/import.
19. global search.
20. accessibility and responsive behavior.

The build should preserve useful legacy content while improving structure and learner effectiveness.

---

## 4. Product Principles

### 4.1 IELTS authenticity

Training must transfer to real IELTS Academic performance. Content volume does not compensate for weak task authenticity.

### 4.2 English-first bilingual support

English is the exam language and should dominate authentic task content. Ukrainian should clarify difficult concepts, strategy, transfer errors, vocabulary meaning, instructions, and corrective feedback when it materially improves learning.

Do not mirror every English sentence into Ukrainian.

### 4.3 Advanced-learner calibration

Avoid excessive beginner material. Focus increasingly on:

- inference;
- evidence;
- paraphrase;
- lexical precision;
- grammatical control;
- organization;
- data interpretation;
- argument development;
- timing;
- distractor resistance;
- editing and self-correction.

### 4.4 Mobile-first continuous study

The experience must remain comfortable at phone widths, especially 320–430 px, and should support natural continuous scrolling.

### 4.5 Evidence-based mastery

Opening content does not create mastery.

The learner progression model is:

- L0 — Not Assessed
- L1 — Introduced
- L2 — Guided
- L3 — Independent
- L4 — Timed
- L5 — Mastered

Evidence thresholds may vary by skill but must remain performance-based.

### 4.6 Error-driven improvement

Incorrect responses should produce actionable learning evidence when possible. Errors should support classification, review, recommendation, and later retesting.

### 4.7 Local-first ownership

Learner data remains local unless explicitly exported. The application must not require an account or backend during the current build.

### 4.8 Copyright discipline

Do not reproduce commercial IELTS passages, paid preparation books, unauthorized audio, or copyrighted answer banks. Prefer original training material, official links, and clearly licensed/open resources.

### 4.9 Honest scoring

Practice guidance or estimated performance must never be presented as an official IELTS examiner score.

---

## 5. Scope

### In scope

- one learner-focused static application;
- HTML/CSS/JavaScript;
- LocalStorage learner state;
- JSON export/import;
- original practice content;
- curriculum generation scripts;
- automated validation scripts;
- responsive testing;
- accessibility checks;
- data migration from the vocabulary workbook;
- phase-gate documentation.

### Out of scope unless explicitly approved later

- user accounts;
- authentication;
- payments;
- analytics trackers;
- advertising;
- remote multi-user databases;
- public social features;
- teacher administration portals;
- framework migration for its own sake;
- public deployment before the release decision.

---

## 6. Information Architecture Commitments

The approved primary navigation contains exactly five controls:

1. Today
2. Skills
3. Practice
4. Words
5. Progress

The broader application architecture supports:

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

Major changes require a documented product decision supported by a concrete usability or architectural need.

---

## 7. Learning Loop

The learner experience should converge on:

**Diagnose → Train → Practice → Capture error → Explain → Review → Retest → Update mastery → Adapt next session**

The build process should converge on:

**Requirements → Implement → Static validation → Functional test → Responsive test → Accessibility check → Content QA → Data QA → Regression → Ledger reconciliation → Defect repair → Gate decision**

---

## 8. Canonical Phase Roadmap

- **G0:** Audit & Requirements Lock — PASS
- **G1:** Foundation & Design System — PASS
- **G2:** Legacy Integration & Vocabulary Migration — PASS
- **G3:** Reading Academy — PASS
- **G4:** Writing Task 1 — NEXT
- **G5:** Writing Task 2
- **G6:** Grammar, Paraphrasing & Pronunciation
- **G7:** Speaking & Practice Together
- **G8:** Listening
- **G9:** Adaptive Engine, Review & Mock Center
- **G10:** Final QA & Release

No phase advances merely because implementation exists. A gate requires evidence.

---

## 9. Standing Quantitative Benchmarks

### G3 Reading
Completed:
- 8/8 foundation strategies
- 15 question families
- 60 original texts/extracts
- 240 scored questions
- 100% answer-explanation coverage

### G4 Writing Task 1
Minimum:
- 7 visual families
- at least 60 micro-exercises
- at least 20 full prompts

### G5 Writing Task 2
Minimum:
- at least 60 full prompts
- at least 100 micro-drills
- at least 15 annotated model responses
- at least 10 Band 6/7/8 comparison sets
- at least 12 timed simulations

### G6 Grammar / Paraphrasing / Pronunciation
Minimum:
- at least 20 grammar modules
- at least 250 grammar items
- at least 100 paraphrase exercises
- complete pronunciation curriculum

### G7 Speaking
Minimum:
- at least 120 Part 1 questions
- at least 75 Part 2 cue cards
- at least 150 Part 3 questions

### G10 Release
Minimum:
- 100% requirements traceability
- 0 open P0 defects
- 0 open P1 defects
- accessibility automated target at least 95
- performance target at least 90
- export/import integrity
- final regression pass
- user acceptance flows complete

---

## 10. Source-of-Truth Policy

Canonical project intent is represented by the root specification set, but actual implementation state must be reconciled against the newest passed release and gate evidence.

Use this authority model:

1. `PROJECT_CHARTER.md`
2. `PRODUCT_SPEC.md`
3. `CURRICULUM_SPEC.md`
4. `UX_DESIGN_SPEC.md`
5. `VALIDATION_SPEC.md`
6. approved entries in `DECISIONS.md`
7. `CURRENT_STATE.md`
8. requirements ledger and newest passed phase report
9. current implementation
10. historical notes and archived prompts

A newer approved decision may explicitly supersede an older requirement. When that occurs, document the supersession.

Historical reports remain evidence, not perpetual current status.

---

## 11. Definition of Success

The product succeeds when the learner can use one coherent system to understand IELTS Academic, train weak skills, practice with realistic tasks, receive useful feedback, revisit recurring errors, build timed competence, see evidence of progress, and receive increasingly relevant recommendations without losing prior work or being overwhelmed by the interface.

The final product should feel calm and personal while remaining technically rigorous and educationally demanding.
