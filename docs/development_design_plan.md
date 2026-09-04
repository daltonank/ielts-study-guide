# Development & Design Plan — Claude Code + Claude Design

**Established:** 2026-09-04
**Precedence:** Same as the rest of `docs/` — this is process/execution guidance, subordinate to `PROJECT_CHARTER.md` through `DECISIONS.md`. It exists to make the next six gates (G4–G9) as mechanical to execute as G3 was, by generalizing the pattern G3 already proved.

---

## 1. How every Claude Code session should start

This is the Startup Protocol from the repo's own project instructions, made concrete:

1. `PROJECT_CHARTER.md` — mission, scope, the canonical phase roadmap, standing quantitative benchmarks (§9).
2. `CURRENT_STATE.md` — what's actually passed, what's active.
3. `DECISIONS.md` — approved exceptions/changes; nothing here should be treated as optional.
4. The specific curriculum section in `CURRICULUM_SPEC.md` for the active gate.
5. The matching gate definition in `VALIDATION_SPEC.md` §11.
6. `docs/requirements_ledger.csv` — find the requirement IDs for the active gate.
7. The existing implementation (`web/app.js`, and the most recently completed academy's data file, e.g. `web/reading_data.js`, as the pattern to extend).

Only after all seven should implementation begin. This isn't bureaucracy for its own sake — it's what caught, in this same session, a set of validation scripts that referenced files that didn't exist yet, and a "canonical precedence" note that would have caused a future session to accept unverified claims.

## 2. Repository layout (established 2026-09-04)

```
PROJECT_CHARTER.md, PRODUCT_SPEC.md, CURRICULUM_SPEC.md,
UX_DESIGN_SPEC.md, VALIDATION_SPEC.md, CURRENT_STATE.md,
DECISIONS.md, CHANGELOG.md, README.md, CLAUDE.md, CONTEXT.md
web/            → index.html, styles.css, app.js, data.js,
                  vocabulary.js, reading_data.js (one *_data.js per academy)
schemas/        → learner_state.schema.json, module.schema.json, exercise.schema.json
scripts/        → migrate_vocabulary.py, build_<academy>_curriculum.py, validate_build.py
tests/          → static/functional/responsive/accessibility validation per gate
docs/           → requirements_ledger.csv, benchmark_dashboard.{md,json}, phase_N_report.md,
                  regression_checklist.md, risk_register.csv, technical_architecture.md
source/         → canonical source data (the vocabulary workbook)
releases/       → point-in-time monolithic HTML snapshots (historical, not the working source)
legacy/         → the original v2 study guide, preserved not edited
archive/        → superseded material, never deleted
```

`web/` is the actual application. `releases/*.html` are frozen snapshots for reference only — never edit them as if they were the source; edit `web/` and, if a new release snapshot is wanted, generate it from `web/` deliberately.

## 3. The proven content pipeline (from G3, generalize for G4–G9)

G3 Reading was built with a specific, replicable pattern:

**Structured Python data → build script → generated `web/<academy>_data.js` → structural validation script → functional/responsive/accessibility validation → gate report.**

Concretely, `scripts/build_reading_curriculum.py` defines, in Python dictionaries: `FAMILY_META` (one entry per question family: display name, skill focus, a named common error, the Ukrainian label), `MODES` (progression stages: guided/independent/timed/mastery, each with a target difficulty), `FAMILY_GUIDANCE` (per-family teaching steps, a worked example, a challenge prompt), and `TOPICS` (the actual passage content, grouped by family). The script assembles these into `window.READING_DATA` in `web/reading_data.js`. `tests/g3_reading_validation.py` then re-parses that same file and checks it against every quantitative and structural requirement from `CURRICULUM_SPEC.md` and `VALIDATION_SPEC.md` — counts, family coverage, unique IDs, required fields, answer grounding in passage text, distractor reasoning, progression-mode coverage.

This pattern should repeat for every remaining academy: **write the generator in Python with the content as structured, human-readable data (not hand-written JS, not a giant prose blob) → run it to produce the data file → write a validator that reproves every quantitative benchmark independently of the generator.** The validator must not simply check "does the generator's output look like what the generator intended" — it must check the output against the specification, the same way `g3_reading_validation.py` checks passage/question counts against `CURRICULUM_SPEC.md` §5, not against whatever the generator happened to produce.

## 4. Curriculum Generation Schema (applies to every new gate)

Any content-generation task — whether run by Claude Code directly, or drafted by ChatGPT and implemented by Claude Code — should be specified in this shape before a line of generator code is written. This is the "prompt schema" requested: it's the contract a content-generation task must satisfy, independent of which tool executes it.

```json
{
  "gate": "G4",
  "skill": "Writing Task 1",
  "family_dimension": "visual family (line graph, bar chart, pie chart, table, process diagram, map/plan, mixed)",
  "quantitative_targets": {
    "families_or_categories": 7,
    "primary_items_min": 20,
    "micro_exercises_min": 60
  },
  "required_item_fields": [
    "id", "type", "skill", "questionFamily|visualFamily", "difficulty",
    "prompt", "correctAnswer|modelResponse", "explanation",
    "errorCategory", "estimatedMinutes", "originality"
  ],
  "grounding_rule": "every claim/answer must be traceable to the item's own visual/data, not external knowledge",
  "distractor_or_common_error_requirement": true,
  "originality_requirement": "original | official-link | licensed — never unlicensed commercial IELTS material",
  "progression_modes": ["guided", "independent", "timed", "mastery"],
  "error_taxonomy_required": true,
  "output_file": "web/<academy>_data.js",
  "generator_script": "scripts/build_<academy>_curriculum.py",
  "validation_script": "tests/g<gate>_<academy>_validation.py",
  "regression_scripts_that_must_still_pass": [
    "scripts/validate_build.py",
    "tests/g2_vocabulary_validation.py",
    "tests/g3_reading_validation.py",
    "tests/responsive_check.py"
  ]
}
```

This mirrors and extends `schemas/exercise.schema.json` and `schemas/module.schema.json`, which already define the item- and module-level JSON Schema every generated exercise/module must validate against (both live in `schemas/` and should be reused, not redefined, for every new academy — add fields only through a documented `DECISIONS.md` entry if a new academy genuinely needs one exercise.schema.json doesn't have).

### Per-gate fill-in, taken directly from `PROJECT_CHARTER.md` §9 and `CURRICULUM_SPEC.md` (not invented — this is the existing approved spec, organized for direct use):

| Gate | Skill | Dimension | Quantitative minimum |
|---|---|---|---|
| G4 | Writing Task 1 | 7 visual families (line, bar, pie, table, process, map/plan, mixed) | ≥60 micro-exercises, ≥20 full prompts |
| G5 | Writing Task 2 | Essay families (opinion, discussion, adv/disadv, problem/solution, two-part, mixed) | ≥60 prompts, ≥100 micro-drills, ≥15 annotated models, ≥10 Band 6/7/8 comparison sets, ≥12 timed simulations |
| G6 | Grammar / Paraphrasing / Pronunciation | Grammar modules; paraphrase techniques; pronunciation features | ≥20 grammar modules, ≥250 grammar items, ≥100 paraphrase exercises, complete pronunciation curriculum |
| G7 | Speaking | Parts 1/2/3 | ≥120 Part 1, ≥75 Part 2 cue cards, ≥150 Part 3 |
| G8 | Listening | Section types / task types | Complete strategy curriculum + full error taxonomy (no fixed count specified yet — propose one via `DECISIONS.md` before building) |
| G9 | Adaptive Engine, Review, Mock Center | N/A — behavioral, not content-count | Seeded-profile recommendation tests, review scheduling tests, mock-driven priority tests (see §7 below) |

## 5. The validation loop, operationalized

`VALIDATION_SPEC.md` §1 defines a 15-step loop in the abstract. For every gate G4–G8, that loop becomes this concrete command sequence, to be run in order, with every step's real output read (not assumed):

1. Confirm requirement IDs exist in `docs/requirements_ledger.csv` for the gate (add if missing, never renumber existing IDs).
2. Write/extend `scripts/build_<academy>_curriculum.py` against the schema in §4.
3. `python scripts/build_<academy>_curriculum.py` → produces `web/<academy>_data.js`.
4. `python scripts/validate_build.py` → structural regression across the whole app.
5. `python tests/g<gate>_<academy>_validation.py` (new, written per §3/§4) → content/schema/grounding validation specific to this gate.
6. `python tests/responsive_check.py` → regression at 320/375/430/768/1024/1440px, must still pass.
7. `python tests/accessibility_static.py` (+ a gate-specific accessibility test if the new UI introduces new interaction patterns, e.g. chart rendering for G4).
8. Manual content QA: sample at least one item per family/category, checked against `VALIDATION_SPEC.md` §8 (answer correctness, ambiguity, distractor defensibility, explanation quality, natural English/Ukrainian, copyright status) — record the sample and findings in a `docs/<academy>_content_qa.md`, following the pattern of `docs/reading_content_qa.md`.
9. Re-run every regression script from earlier gates (§4's `regression_scripts_that_must_still_pass` list, extended with each new gate's own validator once it exists).
10. Log any defect found, by severity (`VALIDATION_SPEC.md` §3), in the requirements ledger or a defect note.
11. Fix defects, rerun 3–9.
12. Write `docs/phase_<N>_report.md` following the template in `VALIDATION_SPEC.md` §12 — decision must be PASS or BLOCKED, never implied.
13. Update `CURRENT_STATE.md`, `DECISIONS.md` (if a real decision was made), `CHANGELOG.md`, and `docs/benchmark_dashboard.json`.
14. Commit.
15. Only then does `PROJECT_CHARTER.md` §8's roadmap advance.

### Validation script template (what every new `tests/g<gate>_<academy>_validation.py` should do, modeled on `tests/g3_reading_validation.py`)

- Parse the generated data file directly (regex out the `window.<NAME>=` assignment, `json.loads` it) — never trust the generator's own internal state, re-derive from the artifact.
- Assert every quantitative target from §4's table.
- Assert required-family/category coverage as a set equality, not just a count (a set equality catches silently-substituted categories that a count alone would miss).
- Assert unique IDs across passages/items/modules.
- Assert every module's `prerequisites` and `masteryCheck` reference IDs that actually exist.
- Assert every item has every required field non-blank.
- Assert answer/claim grounding where the item type makes that checkable (e.g., completion-type answers must appear in the source text/data, mirroring G3's `norm(q['correctAnswer']) not in norm(full)` check).
- Assert distractor reasoning exists for every wrong option where the item is multiple-choice/select.
- Print a human-readable report and exit non-zero on any failure — the exit code is what a future verification pass (by Cowork or anyone else) should actually check, not the printed text alone.

## 6. Claude Design's role

Claude Design should be used **before** Claude Code builds a new academy's UI, not after — per `UX_DESIGN_SPEC.md` §20 ("Design Change Rule"), the design system shouldn't be extended casually mid-implementation. Concretely, for G4 (the next gate, which introduces genuinely new UI surface — chart/visual rendering that Reading never needed):

1. Claude Design produces a mockup canvas covering: the Writing Task 1 module list view (reusing the existing Skills-page card pattern from `web/app.js`'s `renderSkills`), one worked example of each of the 7 visual families rendered at the mobile widths in `UX_DESIGN_SPEC.md` §2, the planning/drafting/review writing flow (extending the existing autosave textarea pattern from `renderPractice`), and the responsive behavior required by §18 (no illegible shrunk data labels; contained scrolling for visuals that can't compress).
2. You review and approve or redirect the mockup.
3. Claude Code implements against the approved mockup, reusing `web/styles.css` component classes wherever an equivalent already exists (card, badge, progress, session-item, notice) and extending the component set only where G4 genuinely needs something Reading didn't — documenting any new component addition in `UX_DESIGN_SPEC.md` §8's component list.
4. Any visual/data source for the 7 chart families must be original or clearly-licensed per `CURRICULUM_SPEC.md` §6's sourcing rule — Claude Design mockups should use placeholder data clearly, and the real dataset gets built the same way G3's passages were: original content authored for this product.

## 7. G9 is different — behavioral, not content-volume

G9 (Adaptive Engine, Review, Mock Center) has no quantitative content target; `VALIDATION_SPEC.md` §11's G9 requirements are behavioral: seeded learner profiles must produce predictable, explainable recommendations. When G9 is reached, the validation script for it should construct several synthetic `state` objects (a learner with no diagnostic data, one with a specific repeated error category, one with a low baseline in one skill) and assert that `recommendation()` in `web/app.js` returns the expected `top`/`reason` for each — i.e. unit tests against the actual recommendation function, not content counts. Flag this now so a future session doesn't try to force G9 into the same "N items generated" pattern as G4–G8.

## 8. Immediate next action: starting G4

1. Read `CURRICULUM_SPEC.md` §6 and `PROJECT_CHARTER.md` §9's G4 benchmarks (already summarized in §4's table above).
2. Add G4 requirement IDs to `docs/requirements_ledger.csv`.
3. Get a Claude Design mockup approved for the 7 visual families and the writing flow (§6).
4. Write `scripts/build_writing1_curriculum.py` following the schema in §4 and the pipeline in §3.
5. Write `tests/g4_writing1_validation.py` following the template in §5.
6. Run the full loop in §5, produce `docs/phase_4_report.md`, update `CURRENT_STATE.md`.
