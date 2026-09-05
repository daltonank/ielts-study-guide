# Phase 4 Checkpoint Report

**Phase:** 4 — Writing Task 1
**Gate:** G4 Writing Task 1
**Date:** 2026-09-04, revised 2026-09-05 after external re-review
**Decision:** **G4 INTERNAL PASS — EXTERNAL RE-REVIEW PENDING**

> External review of candidate `fe720d5` produced candidate 2. External re-review of
> `g4-candidate-2` independently reran all 21 commands and returned **CHANGES REQUESTED**
> on four remaining gaps: five Band 6 annotation/prose contradictions, the active
> `respectively` ordered-pair blind spot, whole-page overflow on Words, and overconfident
> Band 8 UI copy. All four are fixed in `g4-candidate-3`; G4 remains pending another
> independent review. See `docs/G4_EXTERNAL_REVIEW_PACKET.md` §14.

---

## Requirements

| Benchmark (`PROJECT_CHARTER.md` §9, `CURRICULUM_SPEC.md` §6) | Required | Delivered |
|---|---:|---:|
| Visual families | 7 | **7** |
| Micro-exercises | ≥60 | **70** |
| Full timed prompts | ≥20 | **21** |
| Band comparison sets (REQ-019) | 1 per family | **7** |

Also delivered: 21 original visuals (3 per family), all 10 micro-exercise types in every
family, guided/independent/timed/mastery progression in every family, 4 foundation
modules, 7 family modules, and a 13-category Writing Task 1 error taxonomy.

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
  20-minute limit, **at least 150 words long**, with the checklist completed. The functional
  test asserts that finishing the timed exercises alone leaves the learner at L3, and that a
  20-word and a 149-word submission also leave the learner at L3 (D-022).
- **L5** ≥85% across ≥3 distinct exercises on ≥2 dates, including the mastery exercise,
  plus a timed full response of at least 150 words.

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
| `tests/g4_writing1_inventory.py` | **PASS** | Machine-derived counts; every benchmark, fails automatically if coverage drops |
| `tests/g4_writing1_claims.py` | **PASS** | Canonical claim manifest over all 531 text blocks, plus sentence-scoped binding of every figure in the 21 model responses and 21 band samples to an entity named in its clause (D-021), re-derived independently |
| `tests/g4_writing1_persistence.py` | **PASS** | Real HTTP server: genuine reload, export/import round-trip, malformed rejection, backup retention, search, keyboard-only |
| `tests/g4_writing1_obstruction.py` | **PASS** | Real viewport states at six widths: sticky overlap, skip-link focus state, contained scrolling |
| `tests/g4_writing1_validation.py` | **PASS** | Counts, family and micro-type coverage as set equality, unique IDs, reference integrity, `schemas/` conformance, wrong-option reasoning, bilingual coverage, honest scoring, data grounding |
| `tests/g4_writing1_content_qa.py` | **PASS** | 115 quantified prose claims re-derived from the data, 0 failed |
| `tests/g4_writing1_functional.py` | **PASS** | Navigation, all three interaction types, mastery transitions, timing evidence, autosave, error/review integration, persistence across reload |
| `tests/g4_writing1_responsive.py` | **PASS** | All 7 families × 6 widths |
| `tests/g4_writing1_accessibility.py` | **PASS** | All 7 families: text equivalents, SVG naming, labelled controls, non-colour-only feedback, keyboard operability |
| `tests/responsive_check.py` | **PASS** | Whole-app regression at 6 widths, now measuring every grid child on all five primary routes (D4-008) |
| `tests/g4_writing1_negative.py` | **PASS** | Eight seeded defects, including the actual `respectively` blind spot and annotation/prose drift; each required to fail its own guard; 8 of 8 caught |
| `tests/release_integrity.py` | **PASS** | The review packet names a candidate tag that resolves, describes itself, and cites only hashes and paths that exist |

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
| D4-006 | P2 | Fixed | Grounding authorised any arithmetically derivable figure, including column totals and pairwise sums, so an item could look supported without being the intended claim. Replaced by the canonical claim manifest (D-020), verified exhaustively by `tests/g4_writing1_claims.py`. |
| D4-007 | P3 | Fixed | `.w1-chart{margin:0 -2px}` made every chart 4px wider than its parent's content box, so ancestors reported horizontal overflow. Found by `tests/g4_writing1_obstruction.py`. |
| QA-G4-001 | P3 | Fixed | The fact engine could not derive differences between two readings of a series or two columns of a row, rejecting genuinely grounded claims. |
| QA-G4-002 | P3 | Fixed | The literal string "Task 1" was read as the figure 1 during grounding checks. |
| D4-008 | P2 | Fixed | `.half`, `.third` and `.twoThird` received a column span only at 760px and above, so every non-`.card` grid child collapsed to one twelfth of the row on a phone — 28px slivers in the band lab, 14px slivers for the vocabulary filters on Words. In the stylesheet since G1 and invisible to the assertions; found by looking at a 375px screenshot. `tests/responsive_check.py` now measures every grid child on all five primary routes at all six widths. |
| R1-001 | P1 | Fixed | 18 of 21 band samples were under the 150-word Task 1 minimum, four of them labelled Strong (external review). All 21 are now 158-202 words; the generator refuses to emit a shorter one. |
| R1-002 | P1 | Fixed | L4 and L5 could be reached with a 20-word response (external review). Both now require at least 150 words; underlength submissions log an error. |
| R1-003 | P2 | Fixed | Report-level grounding authorised an unbound set of figures, so two real values could be swapped between two series (external review). Replaced by sentence-scoped binding (D-021). |
| R1-004 | P2 | Fixed | The packet named a candidate SHA that does not exist (external review). The candidate is now a tag, checked by `tests/release_integrity.py` (D-023). |
| R1-005 | P3 | Fixed | `Completed 0+0` and `foundation • undefined min` (external review). Both strings now name what they show. |
| R2-001 | P1 | Fixed | Five Band 6 teaching annotations contradicted the extended samples. Annotations were reconciled and now carry executable prose-evidence rules (D-025). |
| R2-002 | P2 | Fixed | A non-interleaved `respectively` construction allowed a silent ordered value swap in canonical content. The construction is banned in canonical prose until ordered-pair parsing exists (D-024). |
| R2-003 | P2 | Fixed | The Words route overflowed at 320px and 375px because the workbook filename could not wrap and document overflow was checked only on Today. Notices now wrap; document and body widths are measured on every primary route. |
| R2-004 | P3 | Fixed | `Nothing holding it back` was stronger than the annotated evidence. The target card now uses bounded criteria-specific and explicitly non-official language. |
| D4-009 | P2 | Fixed | Full-suite verification exposed a 3px overflow on the 320px Task 1 family list: the three-column foundation `.module-item` could not shrink around its action button. At ≤430px it now uses two columns and the action spans the full row. |

Open P0: **0** · Open P1: **0** · Open P2: **0** · Open P3: **0**

## Closure audit

A closure audit after the first candidate (`f2b3157`) found:

- **REQ-019, the band comparison lab, had been recorded as satisfied by argument** — the
  note claimed band comparison was a G5 concern — rather than by implementation. It is a
  phase-4 ledger row. The lab now exists: 7 sets, 21 sample responses, per-aspect
  comparison, disclaimed labels.
- **D4-006** and **D4-007** above.
- The apparent header obstruction in the earlier screenshots was an artifact of full-page
  capture rendering sticky and fixed elements at scroll position.
  `tests/g4_writing1_obstruction.py` settles it with real viewport states and confirms
  nothing sticky covers content at any of the six widths, and that the skip link is hidden
  until focused.

## Risks carried forward

- Sentence-scoped binding (D-021) ties each figure in canonical prose to an entity named
  in its clause. Until ordered-pair parsing exists, canonical model responses and band
  samples reject `respectively` (D-024), closing the known non-interleaved value-swap path.
- Exercise stems, model notes and target-feature lists keep the declared-key set check of
  D-020 rather than sentence binding, because that prose is commentary about language.
- Full written responses cannot be auto-scored and are self-assessed against a checklist.
  This is deliberate (`PROJECT_CHARTER.md` §4.9) and is not a defect to fix later.
- The 21 prompts are single-task timed responses, not multi-task exam simulations. Full
  Writing-paper realism belongs to the Mock Center in G9.

## Gate

**G4 INTERNAL PASS — EXTERNAL RE-REVIEW PENDING.**

All quantitative benchmarks exceeded and all twenty-one validation commands passing, with
content QA recorded and responsive, accessibility, obstruction, persistence and keyboard
evidence generated across all seven families at the six approved widths. G0–G3 regression
re-run and passing after integration. `tests/g4_writing1_negative.py` seeds eight real
defects and requires each guard to fail on its own: 8 of 8 caught.

The gate is **not** recorded as PASS. External re-review of candidate 2 returned CHANGES
REQUESTED; every finding is addressed in candidate 3, and the next independent review has
not happened yet. A green suite was not enough last time, which is the reason the
seeded-defect proof now ships with it.
REQ-019, the band comparison lab, was previously recorded as satisfied by argument
rather than by implementation; it now exists and is verified.
