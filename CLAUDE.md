# CLAUDE CODE MASTER STARTUP PROMPT
## IELTS Academic C1 UA+EN Adaptive Study Webapp

You are taking over active development of an existing long-term educational software project. This is not a new project, not a prototype, and not an invitation to redesign the product from scratch.

Your task is to confirm the current state of the repository and continue implementation from the point already reached, while preserving the design, curriculum direction, learner experience, technical behavior, and validation requirements already established.

**The repository is the authoritative technical state.** As of 2026-09-04 it is also a real GitHub repository — `github.com/daltonank/ielts-study-guide`, branch `main` — not just a local folder. Two commits exist: the canonical-state import, and the process documentation described in §35–36 below. Read the repo; do not rely on chat history or any prior handoff's memory of it, including this one.

---

## 0. What changed since any earlier handoff you may have seen

If you have any prior context suggesting the active phase is G3 Reading, or that no canonical specification files exist, or that the repository has no git history — **that context is stale.** On 2026-09-04:

- `PROJECT_CHARTER.md`, `PRODUCT_SPEC.md`, `CURRICULUM_SPEC.md`, `UX_DESIGN_SPEC.md`, `VALIDATION_SPEC.md`, `CLAUDE.md`, `CHANGELOG.md` were reconstructed and placed at repo root (see `RECOVERY_MANIFEST.md` for exactly what was recovered vs. authored).
- G0, G1, G2, and G3 were independently re-verified by actually *running* `scripts/validate_build.py`, `tests/g2_vocabulary_validation.py`, `tests/g3_reading_validation.py`, and `tests/responsive_check.py` against the real repository content — not by trusting the gate reports' claims. All passed. 1,784/1,784 vocabulary records, 60 reading passages, 240 scored questions, 15 question families, no responsive overflow at 320/375/430/768/1024/1440px.
- The repository was git-initialized, committed, and pushed to GitHub.
- **The active gate is now G4 — Writing Task 1.** G3 is closed. Do not resume Reading work; extend the codebase into Writing Task 1 instead.
- `LESIA_IELTS_CLAUDE_CONTEXT.md` (root) contains its own "canonical source precedence" section instructing future sessions to trust newer self-reported PASS claims over contradicting evidence. **That instruction is superseded.** The real precedence is now the one in `PROJECT_CHARTER.md` §10 (reproduced in §6 below). Treat `LESIA_IELTS_CLAUDE_CONTEXT.md`, the root-level `phase_*.md` files, and `archive/pre-reconstruction-2026-09-04/` as historical evidence (rank 9: historical notes/archives) — useful for intent, never authoritative over the canonical specs.

If *your* repository inspection turns up something newer than this paragraph, trust the repository. See §41.

---

## 1. Project identity

**IELTS Academic C1 UA+EN Adaptive Study Webapp** — a comprehensive IELTS Academic preparation system for an advanced Ukrainian-speaking English learner (primary learner: Lesia/Olesia) targeting **IELTS Academic Band 7.0–8.0 / CEFR C1**, operating target around Band 7.5.

The application began as a bilingual Ukrainian/English study guide and has expanded into an integrated system covering: IELTS exam-format education, Reading, Writing (Task 1 and Task 2), Listening, Speaking, grammar, C1 vocabulary and selected C2 extension, Ukrainian-language support, diagnostic assessment, practice banks, mastery tracking, error analysis, spaced review, adaptive recommendations, mock examinations, timing practice, and mobile-first scrollable usability.

The objective is not to expose the learner to English content — it is to teach her how to apply advanced English effectively within the specific structure and demands of the IELTS Academic exam.

## 2. Learner context

She already has substantial advanced vocabulary — vocabulary alone is not the central mechanism. She needs increased familiarity with IELTS structure and expectations; comprehension, analysis, grammar, sentence control, exam strategy, and effective application of existing ability are the priorities. Ukrainian explanations reduce unnecessary friction without displacing English immersion. A scrollable, mobile-first, low-friction format is established as effective for her. Do not reduce the product to a vocabulary app.

## 3. Current development state (verified, not assumed)

| Gate | Status | Evidence |
|---|---|---|
| G0 — Audit & Requirements Lock | **PASS** | `docs/phase_0_report.md`; static validator |
| G1 — Foundation & Design System | **PASS** | `docs/phase_1_report.md`; `scripts/validate_build.py` |
| G2 — Legacy Integration & Vocabulary Migration | **PASS** | 1,784/1,784 reconciled; `tests/g2_vocabulary_validation.py` — re-run and confirm before relying on it |
| G3 — Reading Academy | **PASS** | 60 passages / 240 questions / 15 families / 100% explanations; `tests/g3_reading_validation.py`, `tests/responsive_check.py` — re-run and confirm before relying on it |
| **G4 — Writing Task 1** | **ACTIVE — this is your work** | Not started. See §12–16. |
| G5–G10 | Not started | See `PROJECT_CHARTER.md` §8 |

The application is a **local-first static HTML/CSS/JS build** (`web/`), with GitHub now the durable canonical repository per D-014 in `DECISIONS.md`. Do not deploy, migrate hosting, or reconcile with any public/older version. Treat D-014 as binding unless the user explicitly changes it.

## 4. Your first responsibility: confirm real project state

Do not immediately begin writing code. Perform a full orientation pass:

- `git status`, current branch, `git log`, `git remote -v` (should show `origin` → the GitHub URL above).
- Repository root file tree — root-level canonical specs, `web/`, `schemas/`, `scripts/`, `tests/`, `docs/`, `source/`, `releases/`, `legacy/`, `archive/`.
- `web/index.html`, `web/app.js`, `web/styles.css`, `web/data.js`, `web/vocabulary.js`, `web/reading_data.js` — read `app.js` in full; it is ~350 lines and is the entire application logic (routing, state, mastery, recommendation engine).
- `docs/requirements_ledger.csv`, `docs/benchmark_dashboard.json`, `docs/technical_architecture.md`.
- `schemas/learner_state.schema.json`, `schemas/module.schema.json`, `schemas/exercise.schema.json`.

Do not assume file paths beyond what's listed above — this list reflects the actual repository as of 2026-09-04, but confirm it rather than trusting this document blindly (§41).

## 5. Vocabulary source data

Canonical source: `source/IELTS_Academic_C1_Ukrainian_Vocabulary_Bank.xlsx`. It has already been migrated into `web/vocabulary.js` (`window.VOCABULARY`, 1,784 records) by `scripts/migrate_vocabulary.py`, and independently re-verified passing on 2026-09-04. Treat the workbook as source/editorial data. **Do not regenerate or overwrite `web/vocabulary.js` casually** — if you touch vocabulary behavior, re-run `tests/g2_vocabulary_validation.py` afterward and confirm it still passes before considering the change done.

## 6. Source-of-truth model

Repository-centered continuity, now literally true (GitHub is live). Authority order, from `PROJECT_CHARTER.md` §10:

1. `PROJECT_CHARTER.md`
2. `PRODUCT_SPEC.md`
3. `CURRICULUM_SPEC.md`
4. `UX_DESIGN_SPEC.md`
5. `VALIDATION_SPEC.md`
6. approved entries in `DECISIONS.md`
7. `CURRENT_STATE.md`
8. `docs/requirements_ledger.csv` and the newest passed phase report
9. current implementation
10. historical notes and archived prompts (`LESIA_IELTS_CLAUDE_CONTEXT.md`, root `phase_*.md`, everything under `archive/`)

A newer approved `DECISIONS.md` entry may supersede an older requirement; document the supersession when it happens. Historical reports are evidence of past state, not perpetual current status — this is exactly the mistake this project already made once (see §0, §23).

## 7. Conflict resolution

When documentation conflicts: identify the sources, determine which has higher authority per §6, check whether a `DECISIONS.md` entry supersedes the older one, inspect git history if needed, preserve the higher-level product intent, and document any unresolved contradiction rather than silently picking the convenient reading.

## 8. Role of Claude Code

Senior product engineer, front-end engineer, learning-platform engineer, curriculum implementation engineer, QA engineer, accessibility reviewer, state-management reviewer, content-generation pipeline engineer, and technical documentation maintainer. You may analyze requirements and recommend changes; you do not silently redefine pedagogy, curriculum architecture, or product scope.

## 9. Primary technical responsibilities

HTML/CSS/JS implementation, component behavior, responsive/mobile layouts, application state (`localStorage`, namespace `ieltsC1UAEN.state.v1`), navigation, curriculum rendering, exercise systems, the content-generation scripts in `scripts/` and their paired validators in `tests/`, diagnostics, mastery/progress/review behavior, accessibility, regression testing, and documentation. Use the existing architecture (vanilla JS, no framework, no build step) unless there is a compelling technical reason to change it — not because another stack would be more fashionable.

## 10. Areas you may not silently redefine

Target band/CEFR level, bilingual strategy, pedagogical strategy, project scope, curriculum architecture, mastery model, scoring model, phase-gate structure, acceptance benchmarks, primary navigation (exactly five controls: Today/Skills/Practice/Words/Progress), or core UX principles. Recommend; don't quietly implement as if approved. A real change goes into `DECISIONS.md` first.

## 11. Core product principles (from `PROJECT_CHARTER.md` §4)

**11.1 IELTS authenticity** — exercises must transfer to real IELTS performance; volume never substitutes for authenticity.
**11.2 English-first bilingual support** — English dominates authentic task content; Ukrainian clarifies strategy, transfer errors, vocabulary, grammar contrast, and feedback. Do not mirror every sentence into Ukrainian.
**11.3 Advanced-learner calibration** — minimize elementary material; focus on inference, evidence, paraphrase, lexical precision, grammatical control, organization, timing, distractor resistance.
**11.4 Mobile-first continuous study** — validated at 320/375/430/768/1024/1440px; no unintended horizontal overflow.
**11.5 Evidence-based mastery** — L0 Not Assessed → L1 Introduced → L2 Guided → L3 Independent → L4 Timed → L5 Mastered. Opening content never advances mastery.
**11.6 Error-driven improvement, local-first ownership, copyright discipline (no commercial IELTS reproduction), honest scoring (never present practice guidance as an official band).**

## 12. Current priority: G4 — Writing Task 1

This is confirmed active by `PROJECT_CHARTER.md` §8, `CURRENT_STATE.md`, and `docs/benchmark_dashboard.json` (`task1_micro_exercises: 0`, `task1_full_prompts: 0`). Do not skip ahead to G5+ or backfill G3 further — G3 is closed with evidence.

## 13. G4 objective (from `CURRICULUM_SPEC.md` §6)

Build the Writing Task 1 academy: 7 visual families (line graphs, bar charts, pie charts, tables, process diagrams, maps/plans, mixed/multiple visuals). Train task interpretation, key-feature identification, overview construction, grouping, comparison (not list-like description), trend language, quantity/proportion language, approximation, tense selection, sentence control, lexical variation without data distortion, data precision, paragraph organization, avoiding unsupported causal claims, avoiding personal opinion, planning, timed drafting, self-review, and common Ukrainian-speaker grammar/article/preposition issues.

## 14. Quantitative minimum (from `PROJECT_CHARTER.md` §9)

- 7 visual families, all represented.
- ≥60 micro-exercises (feature selection, overview selection, comparison building, data-to-sentence transformation, sentence correction, grouping, paragraph ordering, trend-language choice, grammar correction, paraphrase without numerical distortion).
- ≥20 full timed-writing prompts (planning + full timed response).
- Visual/data sourcing must be original-to-product or clearly safe/open — never reproduce commercial IELTS visuals.

For each visual family, the same instructional depth G3 required per question family applies here: what the visual tests, how IELTS constructs it, a strategy, common errors, worked examples, guided practice, independent practice, feedback, error interpretation. A family that technically has one trivial exercise is not complete.

## 15. Feedback and error taxonomy for Writing Task 1

Feedback must be criteria-relevant and specific — not "Incorrect, try again" — but must never imply official examiner authority (§23; `PROJECT_CHARTER.md` §4.9). Reasonable Writing Task 1 error categories to formalize (check `docs/requirements_ledger.csv` / prior `DECISIONS.md` for an existing taxonomy before inventing one): data misreading, invalid/unsupported comparison, missing overview, list-like description without synthesis, tense misuse, unsupported causal claim, inclusion of personal opinion, imprecise quantity language, poor paragraph organization, timing failure.

## 16. Progress and mastery — inspect before changing

Read `web/app.js`'s `state` shape, `masteryBadge`, `recommendation()`, and the Reading precedent in `PRODUCT_SPEC.md` §4 (L2 ≥50% guided, L3 ≥75% independent, L4 timed + ≥75%, L5 ≥85% across ≥3 sets on ≥2 dates) before defining G4's own thresholds. Preserve all working G0–G3 state behavior while adding G4.

## 17. Validation philosophy — the rule this project already learned the hard way

**Implemented does not mean complete, and a report claiming PASS is not evidence of PASS — running the script is evidence.** Before implementing a G4 requirement: identify the requirement ID, identify acceptance criteria (§13–14 plus `VALIDATION_SPEC.md` §11's G4 gate definition), inspect current behavior, implement, test, validate, check regression, document evidence. Never mark a requirement complete on file presence or code volume alone.

## 18. Validation dimensions

Functional, curriculum (does it teach the intended skill), content (complete and appropriately advanced), bilingual, interaction, feedback, state, responsive, accessibility, regression — same nine dimensions established for G3, unchanged for G4.

## 19. Never fake validation

Never report "fully tested" from static inspection only, "mobile validated" without running the actual widths, "complete" without a requirement→evidence map, "no regressions" without running the regression scripts, "adaptive" for static behavior, or "persistent" when state actually resets. This project has a documented instance of a prior session's own precedence note trying to make exactly this mistake acceptable (§0) — it isn't. Report only what you actually verified.

## 20. Code-change discipline

Understand existing implementation, dependencies, state coupling, shared styles, and naming conventions before major changes. Make coherent, related changes; avoid unrelated refactors; use existing component patterns (`card`, `badge`, `progress`, `session-item`, `notice` in `web/styles.css`) before inventing new ones; extend the design system deliberately (§25/`UX_DESIGN_SPEC.md` §20), not incidentally.

## 21. Local HTML constraint

Per D-014: no deployment, no hosting migration, no reconciliation with any public/older site. GitHub being live now is about durable history, not deployment — it changes nothing about this constraint.

## 22. Preserve existing content

Everything from before the 2026-09-04 reconstruction is preserved under `archive/pre-reconstruction-2026-09-04/` — nothing was deleted. Keep that practice: never delete, always archive, when reorganizing.

## 23. Content and Ukrainian quality

Generated content is not valid merely because it's grammatically correct or fluent-sounding. For every Writing Task 1 item: verify the correct/model answer is actually supported by its visual/data, check distractor/common-error plausibility, natural English and Ukrainian, appropriate academic tone, and realistic task construction — same rigor `tests/g3_reading_validation.py` applied to Reading (answer grounding, distractor reasoning, uniqueness).

## 24. Information architecture

Primary nav is locked at five items (§10). New G4 surfaces live under Skills → Writing Task 1 and Practice, following existing secondary-navigation patterns in `UX_DESIGN_SPEC.md` §4 (Writing Task 1 is already a named secondary destination). Do not add primary nav items for G4.

## 25. Adaptive system and mock exam principles

Full adaptivity is G9's job — don't build a parallel recommendation engine now, but don't make architectural choices in G4 that would make G9's later integration harder (keep error/mastery/review data shapes consistent with what `recommendation()` already reads). Similarly, full mock-exam realism is G9/Mock Center's job; G4 should produce properly-scoped focused exercises and full timed prompts, not a premature mock system, while avoiding choices that would make later timed-simulation integration unnecessarily difficult.

## 26. Repository documentation to keep current

`CURRENT_STATE.md`, `DECISIONS.md`, `CHANGELOG.md`, `docs/requirements_ledger.csv`, `docs/benchmark_dashboard.json`/`.md`. After substantial work, another engineer (human or AI) should be able to reconstruct what changed, why, what's tested, what remains, and what's next from the repo alone — never from this chat's history.

## 27. Decision logging and requirement traceability

Log real architecture/curriculum/data/scope decisions in `DECISIONS.md`; skip routine implementation details. Preserve existing requirement IDs in `docs/requirements_ledger.csv`; add new G4 IDs rather than renumbering. Maintain requirement → implementation artifact → validation evidence → status for every G4 requirement, same shape the ledger already uses for G0–G3.

## 28. The proven content-generation pipeline (use this pattern for G4)

G3 was built as: structured Python data (`scripts/build_reading_curriculum.py` — `FAMILY_META`, `MODES`, `FAMILY_GUIDANCE`, `TOPICS` dictionaries) → a build step that assembles `window.READING_DATA` into `web/reading_data.js` → `tests/g3_reading_validation.py`, which **re-parses the generated file independently** and checks every quantitative/structural/grounding requirement against the spec, not against the generator's own intent.

Repeat this shape for G4: write `scripts/build_writing1_curriculum.py` (structured Python data covering the 7 visual families, each exercise/prompt type, common-error guidance, worked examples), have it emit `web/writing1_data.js`, and write `tests/g4_writing1_validation.py` that independently re-parses that file and asserts every target in §14 as a hard failure condition, plus family-set equality (not just counts), unique IDs, required-field presence, and answer/model-response grounding in the item's own visual/data. The full generalized schema and a step-by-step validation loop (mirroring `VALIDATION_SPEC.md` §1's 15 steps, made concrete) are in `docs/development_design_plan.md` §4–5 — read that file before writing the generator or validator.

## 29. Claude Design handoff

G4 introduces real new UI surface (chart/visual rendering) that Reading never needed. Per `docs/development_design_plan.md` §6: get a Claude Design mockup approved for the 7 visual families at target widths and the planning/drafting/timed-writing flow **before** building the UI, reusing existing component classes wherever they already fit. Don't build G4's chart UI from a blank page without that mockup step.

## 30. Git and GitHub discipline

The repo is live at `github.com/daltonank/ielts-study-guide` (branch `main`). Commit at the end of every session that changes files, with a message describing what changed and why (not just "update"). If you have push access in your environment, push after committing so GitHub stays current; if you don't, leave a clean commit for the user to push themselves — never leave uncommitted work as the only record of a session's changes.

## 31. Startup execution sequence

**Step A — Repository orientation.** `git status`, branch, recent log, file tree (§4).
**Step B — Documentation reconstruction.** Read files in the order in §6, focused on G4's sections specifically (`CURRICULUM_SPEC.md` §6, `VALIDATION_SPEC.md` §11's G4 definition, `PROJECT_CHARTER.md` §9's G4 row) plus `docs/development_design_plan.md` in full.
**Step C — Implementation reconstruction.** Read `web/app.js` in full, `web/reading_data.js`'s structure (even briefly) as the pattern to follow, `web/styles.css` for the existing component vocabulary.
**Step D — Baseline integrity check.** Run `python scripts/validate_build.py`, `python tests/g2_vocabulary_validation.py`, `python tests/g3_reading_validation.py`, `python tests/responsive_check.py` (needs a Chromium binary — locate one; do not skip this check by assuming it would pass). All four must actually pass before you touch G4. If any fails, that is a pre-existing defect — separate it from new G4 work, and report it rather than silently fixing it as if it were expected.
**Step E — G4 gap analysis.** Confirm `web/writing1_data.js` / `scripts/build_writing1_curriculum.py` / `tests/g4_writing1_validation.py` do not yet exist (they shouldn't — G4 is unstarted), and confirm this against `docs/requirements_ledger.csv`.
**Step F — Resume/begin G4.** Once B–E are done, start on the highest-priority G4 requirement per §28's pipeline. Don't stop at an audit — continue into implementation in the same session unless a genuine blocking contradiction (§7) prevents safe progress.

## 32. Do not ask what's already answered here

Use the repository and this document first. Do not ask what phase we're on, whether the build stays local, whether the learner is Ukrainian, whether the vocabulary workbook matters, or whether you should inspect the repo — all answered above. Only surface a question when a decision genuinely can't be resolved from repository evidence and would materially change the implementation (e.g., a genuinely ambiguous choice between two valid G4 exercise-type interpretations, or a real contradiction between two canonical documents).

## 33. Do not stop at analysis

This prompt authorizes inspection followed by real G4 implementation in the same session. Don't end a session with only an inventory, a proposal, or questions answerable from the repo.

## 34. When the repository differs from this handoff

This document reflects repository state as of 2026-09-04. If your own inspection shows newer commits, a further-advanced G4, or updated specs — trust the repository. Use this document for intent and standing decisions, not as a literal freeze of implementation state. Do not regress newer valid work to match this document.

## 35. Expected initial status report

After orientation (before implementation), report: **Repository state** (branch, cleanliness, structure, most recent relevant commit). **Product state** (implemented/partial/missing major systems). **Phase state** (G0–G3 re-verification results — pass/fail per script actually run — and the exact G4 workstream you're starting). **Validation state** (which scripts exist, which you ran, pass/fail, gaps). **Immediate implementation target** (the specific next G4 task and why). Then proceed with implementation.

## 36. End-of-work reporting

At the end of a substantial work cycle: **Implemented** (concrete functionality/content added). **Validated** (what was actually tested, how, and the real output). **Remaining** (what's left in G4). **Files changed.** **Decisions** (any new `DECISIONS.md` entries). **Known issues.** **Next recommended task.** Update `CURRENT_STATE.md`, `docs/requirements_ledger.csv`, `docs/benchmark_dashboard.json`, and `CHANGELOG.md` before ending the session.

## 37. Definition of done

Not done because code was written. Done when: implementation and content exist, behavior works, correct answers/model responses are actually correct, feedback is useful and honestly labeled, bilingual behavior is intact, state behaves correctly across reload, responsive behavior is verified at all six widths, accessibility has been checked, regressions across G0–G3 have been re-run and pass, acceptance criteria in `VALIDATION_SPEC.md` §11 (G4) are met, and documentation reflects reality. A phase is not complete until its gate benchmarks are supported by evidence you generated this session, not evidence you read about.

## 38. Current mandate

1. Confirm repository state (§4, §31 Step A).
2. Re-verify G0–G3 by actually running their validation scripts (§31 Step D) — do not assume the table in §3 is still accurate without checking.
3. Read `docs/development_design_plan.md` in full for the G4 content-generation schema and validation loop.
4. Get a Claude Design mockup approved for G4's new UI before building it (§29).
5. Build `scripts/build_writing1_curriculum.py` → `web/writing1_data.js` → `tests/g4_writing1_validation.py`, following §28's pipeline, against the benchmarks in §14.
6. Validate what you built — don't just implement it (§17–19).
7. Update `CURRENT_STATE.md`, `docs/requirements_ledger.csv`, `docs/benchmark_dashboard.json`, `CHANGELOG.md`, and `DECISIONS.md` (if a real decision was made).
8. Commit, and push if you can (§30).
9. Report per §36.

Do not restart the project. Do not redesign it from first principles. Do not deploy it. Pick up the verified G0–G3 baseline and build G4 forward from there.
