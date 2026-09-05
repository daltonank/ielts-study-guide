# Phase 4 Checkpoint Report

**Phase:** 4 — Writing Task 1
**Gate:** G4 Writing Task 1
**Date:** 2026-09-04
**Decision:** **PASS**

---

## Requirements

| Benchmark (`PROJECT_CHARTER.md` §9, `CURRICULUM_SPEC.md` §6) | Required | Delivered |
|---|---:|---:|
| Visual families | 7 | **7** |
| Micro-exercises | ≥60 | **70** |
| Full timed prompts | ≥20 | **21** |

Also delivered: 21 original visuals (3 per family), all 10 micro-exercise types in every
family, guided/independent/timed/mastery progression in every family, 4 foundation
modules, 7 family modules, and a 12-category Writing Task 1 error taxonomy.

## Curriculum coverage

Visual families: line graphs · bar charts · pie charts · tables · process diagrams ·
maps and plans · mixed and multiple visuals.

Every family carries what the visual tests, how IELTS constructs it, a six-step strategy,
a named trap, three to four documented common errors with symptom and repair, a worked
example, a language bank, a tense rule, and a Ukrainian transfer note.

Micro-exercise types, one of each in every family: feature selection · overview selection ·
grouping · trend-language choice · comparison building · data-to-sentence transformation ·
paraphrase without numerical distortion · sentence correction · grammar correction ·
paragraph ordering.

Foundation modules: what Task 1 actually asks for · building the overview · the language of
data · planning, timing and self-review.

Each full prompt carries a planning stage, a 13-item self-review checklist mapped to the
criteria IELTS Writing rewards, and an annotated model response.

## Mastery behaviour (D-015)

- **L1** requires an explicit "mark introduced" action. Opening or scrolling a lesson never
  advances mastery — asserted by `g4_writing1_functional.py`.
- **L2** ≥50% across the family's four guided exercises.
- **L3** ≥75% across the family's three independent exercises.
- **L4** ≥75% across the timed exercises **and** one full prompt submitted inside its
  20-minute limit with the checklist completed. The functional test explicitly asserts that
  finishing the timed exercises alone leaves the learner at L3.
- **L5** ≥85% across ≥3 distinct exercises on ≥2 dates, including the mastery exercise,
  plus a timed full response.

## Error and review integration

An incorrect answer persists skill, module, exercise ID, learner answer, correct answer,
error category, explanation, correction direction, repeated flag, review date and resolved
status, and creates a review item unless that exercise is already queued. Submitting a full
response over the 20-minute limit logs a `timing_failure`, and unticked checklist items are
queued for review.

## Tests — every one run this session, none inferred

| Script | Result | What it covers |
|---|---|---|
| `scripts/validate_build.py` | **PASS** | Static artifacts, ledger IDs, nav count, language modes, vocabulary count |
| `tests/g2_vocabulary_validation.py` | **PASS** | 1,784 / 1,784 records |
| `tests/ui_vocabulary_static.py` | **PASS** | Vocabulary UI tokens |
| `tests/accessibility_static.py` | **PASS** | Landmarks, skip link, focus, reduced motion |
| `tests/g3_reading_validation.py` | **PASS** | 60 passages / 240 questions / 15 families |
| `tests/g3_reading_functional.py` | **PASS** | Reading flow after G4 integration |
| `tests/g3_reading_responsive.py` | **PASS** | 320/375/430/768/1024/1440 |
| `tests/g3_reading_accessibility.py` | **PASS** | Reading a11y after G4 integration |
| `tests/g4_writing1_validation.py` | **PASS** | Counts, family and micro-type coverage as set equality, unique IDs, reference integrity, `schemas/` conformance, wrong-option reasoning, bilingual coverage, honest scoring, data grounding |
| `tests/g4_writing1_content_qa.py` | **PASS** | 115 quantified prose claims re-derived from the data, 0 failed |
| `tests/g4_writing1_functional.py` | **PASS** | Navigation, all three interaction types, mastery transitions, timing evidence, autosave, error/review integration, persistence across reload |
| `tests/g4_writing1_responsive.py` | **PASS** | All 7 families × 6 widths |
| `tests/g4_writing1_accessibility.py` | **PASS** | All 7 families: text equivalents, SVG naming, labelled controls, non-colour-only feedback, keyboard operability |
| `tests/responsive_check.py` | **PASS** | Whole-app regression at 6 widths |

Browser used: Microsoft Edge (Chromium), resolved by `tests/browser_env.py`.

### The validator was itself tested

Ten defects were seeded into `web/writing1_data.js` — fabricated figure in a model
response, silently substituted visual family, tampered stored fact, wrong option with no
reasoning, model response with no overview, family missing a micro-type, pie not summing to
100, text awarding the learner a band, module pointing at a module that does not exist, and
an exercise stripped of its Ukrainian note. **All ten were caught**, and the clean artifact
still passed. The G4 validator is not passing vacuously.

## Content QA

Three layers, recorded in `docs/writing1_content_qa.md`:

1. **Structural** — every figure in an answer or model response must be derivable from that
   item's own visual, checked by a fact engine the validator re-implements independently of
   the generator.
2. **Prose claims** — 115 linguistic claims ("less than a third", "the only mode to fall",
   "more steeply in proportional terms") re-derived from the data. 0 failed.
3. **Editorial** — answer correctness and uniqueness, distractor defensibility, explanation
   quality, level calibration, natural English and Ukrainian, copyright status, honest
   scoring.

All 21 visuals and datasets are original to this product. No commercial IELTS graphic,
passage or answer key is reproduced.

## Responsive evidence

All seven visual families were opened at 320 / 375 / 430 / 768 / 1024 / 1440 px and checked
for horizontal overflow, collapsed visuals, data labels shrunk below ~9px, content spilling
its panel without a scroll container, and answer controls under practical touch size. The
writing flow was additionally checked with a long draft in the textarea.

Per `UX_DESIGN_SPEC.md` §18, a graphic that cannot compress scrolls inside its own
container rather than shrinking its labels or clipping.

Screenshots: `docs/qa_w1_list_mobile.png`, `qa_w1_exercise_mobile.png`,
`qa_w1_exercise_desktop.png`, `qa_w1_writing_mobile.png`, `qa_w1_320.png`, and one per
visual family.

## Accessibility evidence

Checked across all seven families: the visual is a labelled `<section>`; every SVG carries
`role="img"` and an accessible name; every chart also ships a data table so identity is
never colour-alone; map statuses carry text badges as well as colour; options are grouped
in a `<fieldset>` with a `<legend>`; every input is labelled; feedback states are conveyed
in text as well as colour; the error category is exposed to the learner; radio groups are
keyboard operable and keep focus; the time-used progress bar has an accessible name; the
scoring disclaimer is visible; UA Help switches `documentElement.lang` to `uk`.

## Design

The UI was built against an approved mockup (`CLAUDE.md` §29). One new component was added,
`.w1-visual`, documented in `UX_DESIGN_SPEC.md` §8 and recorded as D-019. Everything else
reuses the existing component vocabulary. Primary navigation remains exactly five controls.

## Defects

| ID | Severity | Status | Note |
|---|---|---|---|
| D4-001 | P2 | Fixed | Four Playwright tests hard-coded `/usr/bin/chromium`, so browser-driven gate evidence was not reproducible off Linux. `tests/browser_env.py` resolves a browser portably. |
| D4-002 | P2 | Fixed | Exercise controls stayed disabled after an attempt, so "Try again" was impossible. Controls now stay live, matching Reading. |
| D4-003 | P3 | Fixed | `.field textarea` out-specified `.w1-draft`, leaving the drafting box 73px tall at every width. Caught by `g4_writing1_responsive.py`. |
| D4-004 | P3 | Fixed | `.question-card label{display:grid}` out-specified `.w1-opt`, stacking each radio above its option text. Caught by visual inspection, not by the assertions. |
| D4-005 | P3 | Fixed | The chart axis caption collided with the top tick label; the caption now has its own band. |
| QA-G4-001 | P3 | Fixed | The fact engine could not derive differences between two readings of a series or two columns of a row, rejecting genuinely grounded claims. |
| QA-G4-002 | P3 | Fixed | The literal string "Task 1" was read as the figure 1 during grounding checks. |

Open P0: **0** · Open P1: **0** · Open P2: **0** · Open P3: **0**

## Risks carried forward

- Grounding proves a figure is *derivable* from the data, not that it is the *intended*
  figure, because the support set legitimately includes column totals and pairwise sums.
  `tests/g4_writing1_content_qa.py` closes that gap for the claims that matter, but it is a
  fixed list rather than an exhaustive check.
- Full written responses cannot be auto-scored and are self-assessed against a checklist.
  This is deliberate (`PROJECT_CHARTER.md` §4.9) and is not a defect to fix later.
- The 21 prompts are single-task timed responses, not multi-task exam simulations. Full
  Writing-paper realism belongs to the Mock Center in G9.

## Gate

**PASS — G4 Writing Task 1 Complete.**

All quantitative benchmarks exceeded, all fourteen validation scripts passing, content QA
recorded, responsive and accessibility evidence generated at the six approved widths across
all seven families, and G0–G3 regression re-run and passing after integration.
