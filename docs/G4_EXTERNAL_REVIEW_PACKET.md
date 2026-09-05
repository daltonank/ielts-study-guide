# G4 External Review Packet — Writing Task 1

**Gate status: `G4 INTERNAL PASS — EXTERNAL RE-REVIEW PENDING`.**

**Two external reviews happened and both returned CHANGES REQUESTED.** Candidate
`fe720d5` produced the round-1 repairs in **g4-candidate-2**. Re-review of candidate 2
found one P1, two P2 and one P3 gap outside the assertions. All four are fixed in
candidate 3. §12 preserves the first review and §14 answers the re-review findings
one by one.

This packet is the durable handoff: everything a reviewer needs is in this
repository, not in Slack.

---

## 1. Candidate release

The candidate is identified by a **git tag**, not by a hash written into the
commit it describes. That is what went wrong last cycle: the packet at the first
candidate named a SHA that never existed in the repository, because the hash was
stamped by a later commit and the commit was then rewritten. A tag is created
after the commit exists, so it always resolves, and `tests/release_integrity.py`
now fails the build if it does not.

| | |
|---|---|
| Repository | `github.com/daltonank/ielts-study-guide` |
| Branch | `codex/g4-external-re-review-round-2` |
| Candidate | the commit tagged `g4-candidate-3` |
| Resolve it with | `git rev-parse g4-candidate-3` |
| Verify the packet | `python tests/release_integrity.py` |
| Superseded candidates | `f2b3157` (did not satisfy REQ-019), `fe720d5` (round 1), **g4-candidate-2** / `d5eae47929ace2a47eaa507235d438aa66b15063` (external re-review changes requested) |
| Toolchain | Python 3.13.15 with `jsonschema`, `playwright`; Microsoft Edge (Chromium) resolved by `tests/browser_env.py`; Node 24 only for design mockups |
| Application runtime | dependency-free static HTML/CSS/JS, local only (D-014) |

Reproduce everything with:

```bash
python scripts/build_writing1_curriculum.py && python tests/g4_writing1_inventory.py
```

---

## 2. Changed-file inventory

### External re-review repair
| File | Change |
|---|---|
| `scripts/build_writing1_curriculum.py` | Reconciled five Band 6 annotation sets; validates diagnostic evidence and rejects canonical `respectively` |
| `web/writing1_data.js` | Regenerated with executable `diagnosticChecks` and safe ordered comparisons |
| `web/app.js` | Bounded target-sample wording tied to the annotated criteria |
| `web/styles.css` | Long notice text wraps safely at mobile widths |
| `tests/g4_writing1_claims.py` | Independent canonical `respectively` ban |
| `tests/g4_writing1_validation.py` | Independent annotation/prose consistency and bounded-copy checks |
| `tests/g4_writing1_negative.py` | Two new seeded defects; 8 of 8 required to be caught |
| `tests/responsive_check.py` | Document and body overflow checked after every primary-route navigation |
| `DECISIONS.md`, `VALIDATION_SPEC.md`, `CURRENT_STATE.md`, `CHANGELOG.md`, `docs/phase_4_report.md`, `docs/requirements_ledger.csv` | Canonical state and traceability for the re-review repairs |

### Added in review round 2
| File | Lines | Purpose |
|---|---:|---|
| `tests/g4_writing1_negative.py` | 197 | Eight seeded defects, each required to fail its own guard; restores every file it touches |
| `tests/release_integrity.py` | 109 | The packet must name a release that resolves and describes itself |

### Modified in review round 2
| File | Change |
|---|---|
| `scripts/build_writing1_curriculum.py` | Sentence-scoped claim engine (D-021); band samples extended to 150+ words and refused below it; `styleLabel`, `aspectCriteria`, `descriptorReference`, `wordMinimum`; `underlength_response` error category; mastery rules carry the length floor |
| `web/writing1_data.js` | Regenerated: per-sentence claim tuples, band sample lengths and labels, 13-category taxonomy |
| `web/app.js` | Mastery length floor in `w1UpdateMastery` and `w1SubmitPrompt`; underlength error logging; KPI operands named; module duration rendered only where it exists; band card shows the illustrative label, word count and criterion column |
| `web/styles.css` | D4-008: grid children span the full row below 760px |
| `tests/g4_writing1_claims.py` | Independent re-implementation of the sentence-scoped binder, cross-checked against the stored manifest; band length, labelling and criterion checks |
| `tests/g4_writing1_validation.py` | 150-word floor, illustrative labelling, criterion mapping, mastery length rules |
| `tests/g4_writing1_functional.py` | 20-word and 149-word negative submissions; full-length positive case |
| `tests/g4_writing1_responsive.py` | Walks the band lab at all six widths; sliver and scroll-container checks |
| `tests/g4_writing1_inventory.py` | Band samples at 150+ words as a hard row |
| `tests/responsive_check.py` | Measures every grid child on all five primary routes |

### Added in the closure audit cycle
| File | Lines | Purpose |
|---|---:|---|
| `tests/g4_writing1_inventory.py` | 174 | Machine-derived counts; fails if any benchmark regresses |
| `tests/g4_writing1_claims.py` | 472 | Exhaustive canonical-claim validation over every scored item |
| `tests/g4_writing1_persistence.py` | 277 | Real HTTP server: genuine reload, export/import round-trip, keyboard-only |
| `tests/g4_writing1_obstruction.py` | 239 | Real viewport states, sticky-overlap and skip-link verification |
| `docs/G4_EXTERNAL_REVIEW_PACKET.md` | this file | Review handoff |

### Modified this audit cycle
| File | Change |
|---|---|
| `scripts/build_writing1_curriculum.py` | Band comparison lab (7 sets, 21 samples); canonical-claim model; build now refuses to emit if any figure, year or unit is unauthorised |
| `web/writing1_data.js` | Regenerated: adds `bandComparisons`, `bandLevels`, `bandAspects`, and a `claim` manifest on every exercise, prompt and band set |
| `web/app.js` | Band comparison lab view, routing, state and bindings |
| `web/styles.css` | `.w1-bandcard`; removed the negative margin that caused D4-007 |
| `tests/g4_writing1_validation.py` | Band lab structural validation; band records join the honest-scoring grep |

### Added in the G4 build (commits `b18cbc2`, `c2e19c8`, `f2b3157`)
`scripts/build_writing1_curriculum.py`, `web/writing1_data.js`, `tests/browser_env.py`,
`tests/g4_writing1_validation.py`, `tests/g4_writing1_content_qa.py`,
`tests/g4_writing1_functional.py`, `tests/g4_writing1_responsive.py`,
`tests/g4_writing1_accessibility.py`, `docs/writing1_content_qa.md`,
`docs/phase_4_report.md`, `docs/qa_w1_*.png`.

Modified: `web/app.js`, `web/styles.css`, `web/index.html`,
`scripts/build_benchmark.py`, the four pre-existing Playwright suites,
`docs/requirements_ledger.csv`, `CURRENT_STATE.md`, `DECISIONS.md`,
`CHANGELOG.md`, `UX_DESIGN_SPEC.md`, `PROJECT_CHARTER.md`, `VALIDATION_SPEC.md`,
`PRODUCT_SPEC.md`, `CURRICULUM_SPEC.md`, `docs/benchmark_dashboard.{json,md}`.

---

## 3. Machine-derived content counts

All counted from `web/writing1_data.js`, generated by
`scripts/build_writing1_curriculum.py`. Run `python tests/g4_writing1_inventory.py`
to reproduce; it exits non-zero if any row regresses.

| Metric | Actual | Required | Source identifiers |
|---|---:|---:|---|
| Visual families | 7 | 7 | `visuals[].family` |
| Original visuals | 21 | 21 | `visuals[]`, ids `W1V-*` |
| Micro-exercises | **70** | ≥60 | `exercises[]`, ids `W1X-*` |
| Full timed prompts | **21** | ≥20 | `prompts[]`, ids `W1P-*` |
| Band comparison sets | **7** | ≥7 (one per family) | `bandComparisons[]`, ids `W1B-*` |
| Band sample responses | **21** | 21 | `bandComparisons[].responses[]` |
| Band samples at 150+ words | **21** | 21 | `bandComparisons[].responses[].text` — 158 to 202 words |
| Worked examples | 11 | 11 | `modules[].workedExamples[]` |
| Annotated model responses | 21 | ≥20 | `prompts[]` with `modelResponse` and `modelNotes` |
| Foundation modules | 4 | 4 | `modules[]` where `kind=foundation`, ids `W1F-*` |
| Visual-family modules | 7 | 7 | `modules[]` where `kind=visual_family`, ids `W1M-*` |
| Error taxonomy categories | 13 | ≥10 | `errorTaxonomy[].id` — `underlength_response` added (D-022) |
| Timed activities — exercises | 21 | ≥14 | `exercises[]` where `mode ∈ {timed, mastery}` |
| Timed activities — prompts | 21 | ≥20 | `prompts[].estimatedMinutes` |
| **Timed activities — total** | **42** | ≥34 | the two rows above |

### Exercises by interaction type
| Type | Count | Identifier |
|---|---:|---|
| `select` | 49 | `exercises[] where type=select` |
| `cloze` | 14 | `exercises[] where type=cloze` |
| `order` | 7 | `exercises[] where type=order` |

### Exercises by visual family
Every family carries exactly 10 exercises — one of each of the ten micro-types —
plus 3 prompts and 1 band set. Interaction split is identical in every family:
7 select, 2 cloze, 1 order.

| Family | Exercises | Micro-types | Prompts | Band sets | Visuals |
|---|---:|---:|---:|---:|---:|
| line_graph | 10 | 10 | 3 | 1 | 3 |
| bar_chart | 10 | 10 | 3 | 1 | 3 |
| pie_chart | 10 | 10 | 3 | 1 | 3 |
| table | 10 | 10 | 3 | 1 | 3 |
| process_diagram | 10 | 10 | 3 | 1 | 3 |
| map_plan | 10 | 10 | 3 | 1 | 3 |
| mixed_visual | 10 | 10 | 3 | 1 | 3 |

### Bilingual coverage
| Coverage | Actual | Required | Identifier |
|---|---:|---:|---|
| Ukrainian support on exercises | 70/70 | all | `exercises[].uaSupport` containing Cyrillic |
| Ukrainian support on prompts | 21/21 | all | `prompts[].uaSupport` |
| Ukrainian support on band sets | 7/7 | all | `bandComparisons[].uaSupport` |
| Ukrainian support on modules | 11/11 | all | `modules[].uaSupport` |
| Ukrainian transfer notes | 7/7 | all family modules | `modules[].uaTransferNote` |
| Ukrainian error taxonomy | 13/13 | all | `errorTaxonomy[].ua`, `.uaCorrection` |
| English instruction on exercises | 70/70 | all | `exercises[].prompt`, `.explanation` |
| English lesson content on modules | 11/11 | all | `modules[].lesson[]` |

Ukrainian is strategy and transfer support only; English carries all authentic
task content, per `PROJECT_CHARTER.md` §4.2. No content is mirrored.

---

## 4. Requirement-to-evidence matrix

All 26 phase-4 requirements. "Result" is what the named check actually printed.

| ID | Requirement | Implementation | Verification | Result | Status | Limitation |
|---|---|---|---|---|---|---|
| REQ-017 | Writing Task 1 academy | `web/app.js` `renderWriting1`, `renderW1Family`, `renderW1Exercise`, `renderW1Prompt`, `renderW1Band`; `web/writing1_data.js` | full suite | 7 families, 70 exercises, 21 prompts, 7 band sets, 11 modules, all reachable in the UI | PASS | — |
| REQ-018 | Task 1 exercise types | `build_exercise`, `MICRO_TYPES`; UI `select`/`cloze`/`order` renderers | `g4_writing1_inventory.py`, `g4_writing1_functional.py` | 10 types × 7 families; all three interactions scored in-browser | PASS | — |
| REQ-019 | Task 1 band comparison lab | `BAND_SETS`, `build_band_sets`, `renderW1Band` | `g4_writing1_validation.py` §6b, `g4_writing1_claims.py` | 7 sets, 21 samples of 158–202 words, per-aspect comparison mapped to the four public IELTS criteria | PASS | Mis-recorded once (§7.2); samples were underlength until round 1 (§12.1) |
| REQ-019B | Band samples meet the 150-word Task 1 minimum | `build_band_sets` refuses a shorter sample | `g4_writing1_validation.py`, `g4_writing1_inventory.py`, `g4_writing1_negative.py` | 21/21 at 158–202 words; cutting one below 150 fails the validator | PASS | — |
| REQ-019C | Illustrative labelling and criterion mapping | `styleLabel`, `aspectCriteria`, `descriptorReference`; `renderW1Band` | `g4_writing1_validation.py`, `g4_writing1_claims.py` | every sample labelled "Illustrative Band N-style sample"; every aspect mapped to one of the four public criteria | PASS | Criterion names only; no descriptor text reproduced |
| REQ-020 | Task 1 quality gate | whole G4 build | all 21 scripts + the seeded-defect proof | 21/21 pass; 8/8 seeded defects caught | PASS | — |
| REQ-053 | Phase 4 Writing Task 1 | — | `docs/phase_4_report.md` | Internal pass; external re-review of candidate 2 returned CHANGES REQUESTED, all findings addressed in candidate 3 | **PENDING** | Awaiting another independent review |
| REQ-017A | Seven families with instructional depth | `FAMILY_META` (whatItTests, howIeltsConstructs, 6-step strategy, trap, 3–4 common errors, worked example, language bank, tense rule, UA transfer note) | `g4_writing1_validation.py` module checks | every field present and non-blank on all 7 | PASS | — |
| REQ-017B | ≥60 micro-exercises | `exercises[]` | `g4_writing1_inventory.py` | 70 | PASS | — |
| REQ-017C | ≥20 full prompts | `prompts[]` | `g4_writing1_inventory.py` | 21 | PASS | — |
| REQ-017D | Key-feature and overview training | `feature_selection`, `overview_selection` micro-types; module `W1F-02` | `g4_writing1_inventory.py` | present in all 7 families | PASS | — |
| REQ-017E | Data-language precision | `trend_language`, `data_to_sentence`; module `W1F-03` | `g4_writing1_content_qa.py` | percentage-points vs per-cent and share-vs-quantity re-derived | PASS | — |
| REQ-017F | Grouping and comparison | `grouping`, `comparison_building`; `list_like_description` taxonomy entry | `g4_writing1_inventory.py` | present in all 7 families | PASS | — |
| REQ-017G | Plan → timed draft → self-review | `renderW1Prompt`, `w1StartPromptTimer`, `w1SubmitPrompt` | `g4_writing1_functional.py`, `g4_writing1_persistence.py` | stepper, plan autosave, 20-min timer, word count, 13-item checklist, model comparison all driven in-browser | PASS | — |
| REQ-017H | Four progression modes per family | `MICRO_TYPES[].mode` | `g4_writing1_inventory.py` | set equality per family | PASS | — |
| REQ-017I | Ukrainian transfer support | `article_preposition_transfer`; `uaTransferNote`; per-item `uaSupport` | `g4_writing1_inventory.py` | 70/70 exercises, 7/7 transfer notes, Cyrillic asserted | PASS | — |
| REQ-018A | Ten micro-types in every family | `build()` loop over `MICRO_TYPE_IDS` | `g4_writing1_inventory.py`, `g4_writing1_validation.py` | set equality, not a count | PASS | — |
| REQ-018B | Explanation, error category, wrong-option reasoning | `distractorReasoning`, `errorCategory` | `g4_writing1_claims.py` | every wrong option has ≥30 chars of reasoning | PASS | Reasons are prose, not coded per option |
| REQ-018C | Answers and model responses grounded | canonical claim model (D-020) + sentence-scoped binding of canonical prose (D-021) | `g4_writing1_claims.py`, `g4_writing1_negative.py` | 531 text blocks; 368 figures bound to named entities; swapped series values are caught | PASS | — |
| REQ-018D | Ordered multi-entity values are safe | D-024 canonical `respectively` ban | `g4_writing1_claims.py`, `g4_writing1_negative.py` | actual blind-spot sentence shape is rejected | PASS | Ordered-pair parsing may replace the ban later |
| REQ-019D | Band diagnostics match their prose | `diagnosticChecks` on affected samples (D-025) | `g4_writing1_validation.py`, `g4_writing1_negative.py` | five annotation sets carry required/forbidden phrase evidence; a contradictory edit fails | PASS | Evidence rules cover concrete wording claims, not subjective band calibration |
| REQ-019A | Self-review checklist, not official scoring | `BASE_CHECKLIST` + per-family extras; `SCORING_NOTE`, `BAND_SCORING_NOTE` | `g4_writing1_validation.py`, `g4_writing1_accessibility.py` | disclaimer asserted on every prompt, band set and meta; band-claim grep clean | PASS | — |
| REQ-020A | Original visuals and datasets | `VISUALS` | `g4_writing1_validation.py` | `originality == "original"` on all visuals, exercises, prompts | PASS | — |
| REQ-020B | Mastery only on demonstrated performance | `w1UpdateMastery` (D-015 as amended by D-022) | `g4_writing1_functional.py`, `g4_writing1_negative.py` | opening grants nothing; timed exercises alone stay L3; 20-word and 149-word submissions stay L3; 150+ words with the checklist reaches L4; removing the floor fails the suite | PASS | — |
| REQ-020C | Errors feed error log and review queue | `w1SubmitExercise`, `w1SubmitPrompt` | `g4_writing1_functional.py`, `g4_writing1_persistence.py` | error record with all fields; review item; both re-render after reload | PASS | — |
| REQ-020D | Autosave and persistence across reload | `w1SaveDraft`, `saveState`, `loadState` | `g4_writing1_persistence.py` | genuine `page.reload()` over HTTP; results, mastery, drafts, timer, errors, reviews all survive | PASS | — |
| REQ-020E | Responsive at six widths | `.w1-visual`, `.w1-chart` | `g4_writing1_responsive.py`, `g4_writing1_obstruction.py` | 7 families × 6 widths; no overflow, no label under 9px, no sticky overlap | PASS | — |
| REQ-020F | Text equivalents for every visual | `w1VisualPanel` `.w1-alt` | `g4_writing1_accessibility.py` | all 7 families: labelled section, `role="img"` + name, >80-char equivalent, data table | PASS | — |
| REQ-020G | G0–G3 regression preserved | — | 9 pre-existing scripts | all pass after G4 integration | PASS | Round 1 found two visible platform defects the scripts did not assert (`undefined min`, slivered vocabulary filters); both fixed and now measured — §12.5, §12.6 |
| REQ-020H | The packet identifies a release that resolves | tag `g4-candidate-3`; `tests/release_integrity.py` | `release_integrity.py`, `g4_writing1_negative.py` | tag resolves, packet inside the tag names the same tag, and every cited hash/path exists | PASS | D-023 |
| REQ-020I | Whole-page overflow is checked on every route | safe notice wrapping; route-level document/body measurements | `responsive_check.py` | Today, Skills, Practice, Words and Progress pass at all six widths | PASS | — |
| REQ-048B | Portable Chromium resolution | `tests/browser_env.py` | all 8 browser suites | resolves Edge on Windows; all launch | PASS | — |

---

## 5. Test commands and results

Run in this order. Every line below was produced by running the command.

```bash
python scripts/validate_build.py                 # PASS: G0–G3 static artifact validation
python scripts/build_writing1_curriculum.py      # 7 families, 70 exercises, 21 prompts, 7 band sets
python tests/g2_vocabulary_validation.py         # PASS: 1784 records, uniqueness, Ukrainian fields
python tests/ui_vocabulary_static.py             # UI VOCAB STATIC PASS
python tests/accessibility_static.py             # A11Y STATIC PASS
python tests/g3_reading_validation.py            # PASS: 60 passages / 240 questions / 15 families
python tests/g3_reading_functional.py            # G3 READING FUNCTIONAL PASS
python tests/g3_reading_responsive.py            # G3 READING RESPONSIVE PASS: 320…1440
python tests/g3_reading_accessibility.py         # G3 READING A11Y PASS
python tests/g4_writing1_inventory.py            # PASS: every approved G4 benchmark met or exceeded
python tests/g4_writing1_validation.py           # PASS: inventory, coverage, IDs, references, grounding, honest scoring
python tests/g4_writing1_claims.py               # PASS: 531 text blocks; 368 figures bound to an entity
python tests/g4_writing1_content_qa.py           # 115 prose claims checked, 0 failed
python tests/g4_writing1_functional.py           # G4 WRITING TASK 1 FUNCTIONAL PASS
python tests/g4_writing1_persistence.py          # PASS (real HTTP, genuine reload, export/import, keyboard-only)
python tests/g4_writing1_responsive.py           # PASS: 320, 375, 430, 768, 1024, 1440
python tests/g4_writing1_accessibility.py        # G4 WRITING TASK 1 A11Y PASS
python tests/g4_writing1_obstruction.py          # PASS: 320…1440, no sticky overlap, skip link hidden until focused
python tests/responsive_check.py                 # RESPONSIVE PASS: 320, 375, 430, 768, 1024, 1440
python tests/g4_writing1_negative.py             # PASS: 8 of 8 seeded defects caught, artifact restored
python tests/release_integrity.py                # PASS: the packet names a release that exists
```

**21 of 21 pass. 0 failing.**

### Preserved-platform regression, itemised

| Behaviour | Evidence |
|---|---|
| G0–G3 gates | the nine pre-G4 scripts above, all passing after integration |
| Five-item primary navigation | asserted in `validate_build.py`, `g4_writing1_functional.py`, `g4_writing1_accessibility.py` |
| Reading behaviour | `g3_reading_functional.py` (scoring, L2→L4 mastery, timing, error/review) |
| Local-state loading | `g4_writing1_persistence.py` — app boots from a pre-seeded store |
| Actual browser reload persistence | `g4_writing1_persistence.py` — real `page.reload()` over HTTP |
| Export/import round-trip of G4 state | `g4_writing1_persistence.py` — results, mastery, drafts, errors all restored |
| Malformed-import rejection | `g4_writing1_persistence.py` — existing state undamaged |
| Backup snapshot retention | `g4_writing1_persistence.py` — `backups[]` non-empty after a valid import |
| Error log / review queue restoration | `g4_writing1_persistence.py` — both re-render after reload |
| Mastery restoration | `g4_writing1_persistence.py` |
| Timers and autosaved drafts | `g4_writing1_persistence.py` — running timer and draft survive reload |
| Search behaviour | `g4_writing1_persistence.py` — reaches Writing Task 1 content and still serves prior queries |
| 1,784-word vocabulary bank | `g2_vocabulary_validation.py`; also asserted live in `g4_writing1_persistence.py` |
| Keyboard-only operation | `g4_writing1_persistence.py` — skip link → drawer → family → exercise → answer → submit, Tab/Enter/Space only |
| No public deployment | `g4_writing1_persistence.py` asserts zero off-origin requests; D-014 unchanged; no hosting config added |

### Validator self-tests (proof the suites are not vacuous)

**Structural validator** — 10 seeded defects, 10 caught, clean artifact still passes:
fabricated figure, substituted family, tampered stored fact, missing distractor
reasoning, missing overview, missing micro-type, pie not summing to 100, band
claim, dangling module reference, stripped Ukrainian note.

**Canonical-claim validator** — 8 seeded defects, 8 caught, clean artifact still
passes:

| Mutation | Caught as |
|---|---|
| Column total smuggled into an explanation | `cites 77, not authorised for W1V-LINE-01` |
| Pairwise slice sum smuggled in | `cites 66, not authorised for W1V-PIE-02` |
| A year the visual never plots | `cites 2017, not authorised for W1V-LINE-02` |
| A unit the visual does not measure in | `uses unit 'tonne', which W1V-PIE-01 does not measure in` |
| A declared derivation deleted | `manifest authorisedFigures do not match the declared derivation` |
| Manifest figure list widened by hand | same |
| Band sample citing an invented figure | `cites 16, not authorised for W1V-LINE-01` |
| Distractor stripped of its reason | `distractor has no substantive reason it is wrong` |

**`tests/g4_writing1_negative.py`** — eight defects, each required to fail the
guard that should catch it, every file restored afterwards. 8 of 8 caught:

| Seeded defect | Guard | Caught as |
|---|---|---|
| Band sample cut under 150 words | `g4_writing1_validation.py` | `W1B-LINE-01/Band 8: sample response is 95 words, under the 150-word Academic Task 1 minimum` |
| Sample labelled as an awarded band | `g4_writing1_validation.py` | `sample is not labelled as an illustrative Band-style sample` |
| One series given another's real value | `g4_writing1_claims.py` | `W1P-LINE-01.model.p2.s1: 31 is not bound to an entity named in its clause -- "oslo's 31 per cent"` |
| Undeclared column total in a model response | `g4_writing1_claims.py` | `cites 77, not authorised for W1V-LINE-01` |
| Mastery word floor removed from `web/app.js` | `g4_writing1_functional.py` | mastery reached L4 on a 20-word response |
| Packet naming a release that does not exist | `release_integrity.py` | `candidate tag 'g4-candidate-does-not-exist' does not resolve` |
| Canonical non-interleaved multi-entity `respectively` sentence | `g4_writing1_claims.py` | canonical prose uses banned ordered-pair word `respectively` |
| Band prose changed to contradict its diagnostic | `g4_writing1_validation.py` | diagnostic contradicts prose containing `crossed` |

The seventh and eighth rows are the external re-review regressions: both defects
passed the prior candidate's assertions and both now fail independently.

---

## 6. Defect ledger

| ID | Sev | Status | Description | Resolution |
|---|---|---|---|---|
| D4-001 | P2 | Fixed | Four Playwright tests hard-coded `/usr/bin/chromium`; browser-driven gate evidence was not reproducible off Linux | `tests/browser_env.py` |
| D4-002 | P2 | Fixed | Exercise controls stayed disabled after an attempt, so "Try again" was impossible | Controls stay live, matching Reading |
| D4-003 | P3 | Fixed | `.field textarea` out-specified `.w1-draft`; drafting box was 73px tall | `.field .w1-draft` |
| D4-004 | P3 | Fixed | `.question-card label{display:grid}` out-specified `.w1-opt`; radios stacked above their text | `.question-card label.w1-opt` |
| D4-005 | P3 | Fixed | Chart axis caption collided with the top tick label | Caption given its own band |
| **D4-006** | **P2** | **Fixed** | Grounding authorised any arithmetically derivable figure, including column totals and pairwise sums, so an item could be "supported" without being correct | Canonical claim manifest: exercises may cite only the values of their declared fact keys; `total`/`sum` require explicit authorisation; verified by `tests/g4_writing1_claims.py` over all 531 text blocks |
| **D4-007** | **P3** | **Fixed** | `.w1-chart{margin:0 -2px}` made every chart 4px wider than its parent's content box, so ancestors reported horizontal overflow | Negative margin removed |
| QA-G4-001 | P3 | Fixed | Fact engine could not derive pairwise differences, rejecting genuinely grounded claims | Pairwise differences computed in generator and validator independently |
| QA-G4-002 | P3 | Fixed | The literal string "Task 1" was read as the figure 1 | Exam labels stripped before figure extraction |
| **R1-001** | **P1** | **Fixed** | 18 of 21 band samples were under the 150-word Academic Task 1 minimum, four of them labelled Strong, so length was an uncontrolled variable between the levels *(external review)* | All 21 rewritten to 158–202 words in their own voice; `build_band_sets` refuses a shorter one; validator and inventory both check it (D-022) |
| **R1-002** | **P1** | **Fixed** | L4 and L5 could be reached with a 20-word response *(external review)* | Both now require `words >= wordMinimum`; underlength submissions log the new `underlength_response` category; browser tests at 20 and 149 words (D-022) |
| **R1-003** | **P2** | **Fixed** | Report-level grounding authorised an unbound set of figures, so two real values could be swapped between two series *(external review)* | Sentence-scoped binding of canonical prose, recorded per sentence and re-derived independently (D-021) |
| **R1-004** | **P2** | **Fixed** | The packet named candidate SHA `53e986d1…`, which does not exist; the hash was stamped by a later commit and then rewritten *(external review)* | The candidate is a tag; `tests/release_integrity.py` fails if it does not resolve, if the tagged commit's packet names a different release, or if any cited hash or path is missing (D-023) |
| **R1-005** | **P3** | **Fixed** | `Completed 0+0` named neither operand; Reading foundation modules printed `foundation • undefined min` *(external review)* | `Exercises done 0 / 70` and `Prompts answered 0 / 21`; the duration is shown only where the module has one |
| **D4-008** | **P2** | **Fixed** | `.half`, `.third`, `.twoThird` received a column span only at ≥760px. `.card` carries its own span, so cards were fine and the bug was invisible — every other grid child collapsed to one twelfth of the row on a phone: 28px slivers in the band lab, 14px slivers for the four vocabulary filters on Words. Present since G1 | Mobile-first default added in `web/styles.css`; `tests/responsive_check.py` now measures every grid child on all five primary routes at all six widths, and `g4_writing1_responsive.py` walks the band lab |
| **R2-001** | **P1** | **Fixed** | Five Band 6 annotations contradicted the final extended prose *(external re-review)* | Reconciled annotations plus executable evidence rules (D-025) |
| **R2-002** | **P2** | **Fixed** | Canonical `respectively` allowed a silent ordered value swap *(external re-review)* | Construction banned until ordered-pair parsing exists; actual shape seeded as a negative (D-024) |
| **R2-003** | **P2** | **Fixed** | Words had whole-page overflow at 320px and 375px; document overflow was checked only on Today *(external re-review)* | Notices wrap; document and body measured after every route navigation |
| **R2-004** | **P3** | **Fixed** | `Nothing holding it back` was an absolute claim *(external re-review)* | Bounded criteria-specific and non-official wording |
| **D4-009** | **P2** | **Fixed** | Chromium exposed a 3px overflow on the 320px Task 1 family list during the full packet run | Mobile `.module-item` uses two shrinkable columns and a full-row action button |

Open **P0: 0 · P1: 0 · P2: 0 · P3: 0**.

D4-008 is the one to weigh when judging the suite. It was found by looking at a
screenshot, exactly as D4-004 was. Both times the assertions were green on a
broken layout, which is why the responsive checks now measure rendered geometry
rather than only overflow.

---

## 7. Known limitations and honest caveats

1. **Two reviews happened; the next independent review has not.** Both returned
   CHANGES REQUESTED, and their findings are addressed in §12 and §14. Gate status is
   `INTERNAL PASS — EXTERNAL RE-REVIEW PENDING`, not `PASS`.

2. **REQ-019 was previously mis-recorded.** In commit `f2b3157` the band
   comparison lab was marked Passed with the note "Band comparison sets are a G5
   Task 2 requirement, not a Task 1 one". That was a requirement being
   reinterpreted to match what had been built, which `CLAUDE.md` §10 forbids.
   REQ-019 is a phase-4 row in the ledger. The lab now exists: 7 sets, 21 sample
   responses. **A reviewer should treat this as the reason to distrust any other
   "Passed" row that was justified by argument rather than by a check**, which is
   why §4 now names a specific verification for every row.

3. **Band sample responses keep all figures accurate and all lengths legal.**
   The three levels differ structurally and linguistically; every sample is now at
   least 150 words, so length is held constant rather than varying invisibly. Data
   errors are not used to distinguish the levels, because band differences in Task 1
   rarely come from wrong numbers and inventing wrong ones would defeat the
   grounding model. Underlength writing is taught as a fault in its own right — it
   is an error category and it blocks mastery — rather than being modelled.

4. **Distractor reasoning is prose, not a coded taxonomy.** Every wrong option
   carries an authored reason, and each item carries one taxonomy error category.
   Per-option fault codes were not added.

5. **Written responses are not scored.** They are self-assessed against a 13-item
   checklist. Deliberate under `PROJECT_CHARTER.md` §4.9.

6. **Label figures are typed and scoped, not whitelisted.** A figure printed on
   the visual — an axis band, a column heading, an index base of 100, a stage
   number — is authorised only inside a clause that names the label it belongs to.
   "was under the index base of 100" is authorised; a bare "100" is not. This
   replaces the flat numeric whitelist round 1 objected to.

7. **`tests/g4_writing1_content_qa.py` is a fixed list of 115 claims.** It checks
   linguistic assertions ("less than a third", "the only mode to fall") that no
   mechanical rule can derive. It is not exhaustive and is not intended to be;
   `g4_writing1_claims.py` is the exhaustive layer.

8. **The known ordered-pair blind spot is closed by an authoring ban.** Until the
   binder can parse entity/value order, canonical model responses and band samples
   may not use `respectively` (D-024). The actual multi-entity sentence shape is a
   seeded negative case. Interleaved forms remain individually bound.

9. **Exercise stems, model notes and target-feature lists keep the D-020
   declared-key set check** rather than sentence binding. That prose is commentary
   about language ("'Until' would turn 22.1 million into a point in time"), where
   a rule written for reports misreads the sentence. Exercises remain the strictest
   layer: they may cite only the values of the fact keys they declare.

10. **`total` and `sum` remain excluded** from report authorisation and must be
    declared per item.

---

## 8. Screenshot index

Real viewport captures (not stitched full-page), produced by
`tests/g4_writing1_obstruction.py`:

| File | What it shows |
|---|---|
| `docs/qa_w1_skiplink_375.png`, `_1440.png` | The skip link in its keyboard-focused state, above the study content |
| `docs/qa_w1_viewport_list_375.png`, `_1440.png` | Initial viewport, family list |
| `docs/qa_w1_viewport_line_graph_375.png`, `_1440.png` | Scrolled to a chart visual |
| `docs/qa_w1_viewport_map_plan_375.png`, `_1440.png` | Scrolled to a map visual |
| `docs/qa_w1_viewport_writing_375.png`, `_1440.png` | Scrolled to the drafting textarea |

Round 2 captures, real viewports, smooth scrolling pinned off:

| File | What it shows |
|---|---|
| `docs/qa_w1r2_home_desktop.png`, `_mobile.png`, `_narrow.png` | Task 1 inventory with the renamed KPIs (`Exercises done 0 / 70`) |
| `docs/qa_w1r2_band_desktop.png`, `_mobile.png`, `_narrow.png` | A band sample with its illustrative label and word count |
| `docs/qa_w1r2_bandtable_desktop.png`, `_mobile.png`, `_narrow.png` | The comparison table with its IELTS-criterion column and the descriptor pointer |
| `docs/qa_w1r2_skills_desktop.png`, `_mobile.png`, `_narrow.png` | Skills, with Reading foundation modules no longer printing `undefined min` |
| `docs/qa_w1r2_words_mobile.png` | The Words filters at 375px, full width after D4-008 |

Full-page captures from the build cycle (retained; note they render sticky and
fixed elements at scroll position, which is what created the apparent
obstruction the audit asked about):
`docs/qa_w1_list_mobile.png`, `qa_w1_exercise_mobile.png`,
`qa_w1_exercise_desktop.png`, `qa_w1_writing_mobile.png`, `qa_w1_320.png`, and
one per visual family.

---

## 9. Manual inspection checklist for the reviewer

Serve the app and work through this by hand:

```bash
python -m http.server 8000 --directory web
```

- [ ] Skills → Writing Task 1 lists seven families with progress and mastery.
- [ ] Open a family: strategy, worked example, trap, common errors, language bank and mastery rule all read as real teaching, not filler.
- [ ] Open one exercise per family. Is the correct answer the **only** defensible one?
- [ ] Read three distractors. Is each wrong for a **different, nameable** reason?
- [ ] Check a chart against its data table. Do they agree?
- [ ] Open "Describe this visual in words". Could you answer the task from the text alone?
- [ ] Answer wrongly. Is the feedback specific and criteria-relevant, and never presented as a band?
- [ ] Open the band comparison lab. Do the three samples genuinely differ in the ways the comparison table claims — now that all three are the same length?
- [ ] Check a band sample's word count against the stated Task 1 minimum, and read the label: does it read as an illustration rather than as an awarded band?
- [ ] Submit a 20-word response to a prompt. Does mastery refuse to move, and is the reason clear?
- [ ] At 375px, open Words and check the four filter selects are usable (D4-008).
- [ ] Do a full prompt end to end under the 20-minute timer. Does the plan and draft survive a reload?
- [ ] Export, clear site data, import. Is everything back?
- [ ] Read five Ukrainian notes. Natural? Genuinely helpful rather than mirrored?
- [ ] Tab through one exercise without a mouse.
- [ ] Resize to 320px. Is anything illegible or unreachable?

---

## 10. Questions for the next re-review

Round 1's answers are recorded in §12 next to the finding each one settled. What
is genuinely open now:

1. **Is sentence-scoped binding the right strictness for canonical prose?** It
   forced four sentences to name their subject explicitly. Does that constrain the
   writing in ways that hurt the model responses as teaching material?
2. **Is the D-024 authoring ban sufficient for this gate**, with ordered-pair
   parsing deferred until canonical prose needs `respectively`?
3. **Is keeping the D-020 set check for exercise stems and model notes right**, or
   should commentary carry declared keys too?
4. **Do the extended band samples still read as their level?** Each was lengthened
   in its own voice; a Band 6 sample that is now 188 words should still read as
   Band 6 work, not as padded Band 7 work. This is a human judgement.
5. **Is "Illustrative Band N-style sample" plus a criterion mapping the right
   calibration**, or does naming bands at all still imply more than the evidence
   supports?
6. **Should underlength writing be modelled as well as taught?** Currently no
   sample is underlength, and underlength is an error category. The alternative —
   one deliberately underlength sample, labelled as a fault — was not taken.
7. **Are the visuals authentic enough to IELTS?** Unchanged from round 1 and
   answered yes; re-ask only if the extended samples changed your view.
8. **Is the Ukrainian support still right** after the samples grew? A native
   editorial spot-check remains outstanding and automation cannot substitute for it.
9. **Is any row in §4 still satisfied by argument rather than by a check?** Round 1
   found REQ-020B was; §4 now names a specific verification and a seeded-defect
   proof for every row that moved.

---

## 11. What happens after review

- Any defect the reviewer raises is logged in §6 and fixed before the gate moves.
- Round 1's findings are answered in §12 and the external re-review findings in §14;
  the next reviewer should start at §13.
- When the reviewer approves, `CURRENT_STATE.md`, `PROJECT_CHARTER.md` §8,
  `VALIDATION_SPEC.md` §11 and `docs/phase_4_report.md` move to `G4 PASS`.
- **G5 does not start until then.** When it does, it must follow its own
  benchmarks — all major essay families, ≥60 prompts, ≥100 micro-drills, ≥15
  annotated models, ≥10 Band 6/7/8 comparison sets, ≥12 timed simulations — with
  Task 2-specific pedagogy and validation. The G4 technical framework (generator →
  independent validator → claim manifest → functional/responsive/accessibility/
  obstruction suites) is reusable; the curriculum is not a mechanical conversion
  of Task 1, and `.w1-visual` does not apply because Task 2 has no graphic.


---

## 12. External review round 1 — findings and responses

Reviewer verdict on candidate `fe720d5`: **CHANGES REQUESTED**. The suite was
independently rerun and passed; every finding below is something a green suite
did not see.

### 12.1 P1 — Band samples violated the Task 1 minimum
**Finding.** 18 of 21 samples under 150 words; four labelled Band 8 / Strong at
133, 137, 143 and 146 words. The validator accepted samples from 90 words. The
packet's claim that samples differ "only structurally and linguistically" was
therefore untrue: length was another variable.

**Accepted in full.** All 21 samples were extended in their own voice and are now
158–202 words. `build_band_sets` raises if a sample falls under
`TASK1_WORD_MINIMUM`; `g4_writing1_validation.py` fails on one; the inventory
reports the count; the seeded-defect proof cuts a sample and requires the failure.
The line-graph takeaway, which claimed the figures were identical across the three
responses, was corrected to what is actually true — every figure is accurate and
all three are at least 150 words.

### 12.2 P1 — REQ-020B was not satisfied by demonstrated performance
**Finding.** `w1SubmitPrompt` accepted any response of 20+ words, and
`w1UpdateMastery` granted L4 from `withinLimit` plus checked boxes, L5 from any
within-limit submission. A learner could reach timed/mastered status with 20 words.

**Accepted in full.** Submissions record `wordMinimum` and `meetsLength`; L4 and
L5 both require a full-length response as well as their existing conditions; an
underlength submission logs the new `underlength_response` error category and
tells the learner why it does not count. `g4_writing1_functional.py` submits 20
words and 149 words in the browser and requires mastery to stay at L3, then a
150+ word response and requires L4. Removing the floor fails that suite.

### 12.3 P2 — Report-level grounding was too loose
**Finding.** The validator authorised a set of numbers derivable anywhere in the
visual without binding each to its series or category, so two real values could be
swapped between entities and still pass. Broad permission is reasonable for
learner free text, not for canonical teaching content.

**Accepted for canonical content; scoped deliberately.** Model responses and band
samples are now bound sentence by sentence (D-021): a figure may cite only a fact
whose subjects are named in its own clause, whose context does not contradict a
year or category named there. The manifest stores the entity/value/operation
tuples per sentence, and `g4_writing1_claims.py` re-derives them by resolving fact
keys against the visual's label vocabulary — the opposite direction from the
generator — and requires both to agree, figure by figure. `In 2005 Oslo recorded
31 per cent` (Bergen's value) now fails.

Exercise stems, model notes and target lists keep the D-020 declared-key check.
That prose is commentary about language rather than a report of the data, and a
report rule misreads it. Exercises were already the strictest layer. §7.8 states
the one construction the binder still cannot separate.

### 12.4 P2 — The durable handoff named a nonexistent candidate
**Finding.** At `fe720d5`, §1 named the SHA 53e986d12d8942defcc90e19b4cb33c267e418c3
(written here without backticks precisely because it is not a citation), which GitHub
cannot resolve. It exists in the local object store as an orphan left by an amended
commit, which is why a local check that only asked "does this object exist" would have
passed it.

**Accepted in full.** The candidate is now identified by a tag, and
`tests/release_integrity.py` checks that the tag resolves, that the packet inside
the tagged commit names the same tag, and that every hash and path the packet
cites exists. The seeded-defect proof points the packet at a nonexistent tag and
requires the failure.

### 12.5 P3 — Manual UI cleanup
**Finding.** `Completed 0+0` without naming its operands; `foundation ·
undefined min` on the Skills screen for Reading foundation modules.

**Accepted in full.** The inventory card now reads `Exercises done 0 / 70` and
`Prompts answered 0 / 21`. Reading foundation modules carry no duration, so the
duration is now rendered only when there is one. Screenshots in §8.

### 12.6 Found while verifying the above — D4-008
The `undefined min` fix meant looking at the Skills screen at 375px. That is when
the band lab's annotation blocks turned out to be 28px slivers of vertical text,
and the four vocabulary filters on the Words screen 14px slivers. The cause was in
the stylesheet from G1: `.half`, `.third` and `.twoThird` only receive a column
span at 760px and above, and `.card` carries its own span, so every card looked
right and nothing else did. Fixed, and now measured on all five primary routes at
all six widths.

### 12.7 Reviewer answers adopted
- Aspects are mapped to the four public IELTS Writing criteria, with a pointer to
  the published descriptors and no descriptor text reproduced.
- Samples are labelled "Illustrative Band N-style sample" rather than as bands.
- Label figures are typed and scoped to their context rather than whitelisted.
- The completed-checklist requirement for L4 is kept, with the length floor added.
- The Ukrainian editorial spot-check by a native speaker remains outstanding and
  is recorded as such; automation proves presence, not naturalness.
- Volume was not increased: 70 / 21 / 7 stands.

---

## 13. What a re-review should check first

1. Run `python tests/g4_writing1_negative.py`. If a guard stops failing on its own
   defect, nothing else in this packet is worth reading.
2. Read three band samples end to end and judge whether the extended text still
   reads as its level.
3. Insert the original multi-entity `respectively` sentence shape and confirm
   `tests/g4_writing1_claims.py` rejects it.
4. Add an explicit crossover statement to the Band 6 line sample without changing
   its diagnostic and confirm `tests/g4_writing1_validation.py` rejects the drift.
5. Open Words at 320px and 375px and inspect both document width and the workbook
   filename notice rather than trusting this document.
6. Submit a 149-word response in the browser and confirm mastery does not move.

---

## 14. External re-review — findings and responses

Reviewer verdict on `g4-candidate-2` / `d5eae47929ace2a47eaa507235d438aa66b15063`:
**CHANGES REQUESTED**. The reviewer independently reran all 21 commands and the six
seeded negatives before identifying four gaps outside those assertions.

### 14.1 P1 — Five Band 6 annotation sets contradicted their samples
**Accepted in full.** The line, bar, table, process and map annotations now describe
the final prose: isolated comparisons are not called absent; the table's exceptions,
the process cycle/stage count and the map's late compass directions are acknowledged.
Each concrete presence/absence diagnosis carries `diagnosticChecks` evidence enforced
both by the generator and the independent validator (D-025). A seeded edit that adds an
explicit crossover against the displayed diagnostic now fails.

### 14.2 P2 — The canonical `respectively` blind spot was active
**Accepted in full.** The Band 8 line sample now names each city beside its end value.
Canonical model responses and band samples reject `respectively` until ordered-pair
parsing is implemented (D-024). The negative suite uses the actual two-entity/two-value
sentence shape with the values swapped; the claims validator rejects it independently.

### 14.3 P2 — Words overflowed the whole page at 320px and 375px
**Accepted in full.** `.notice` permits emergency wrapping for long filenames.
`tests/responsive_check.py` now measures both `documentElement` and `body` widths after
navigating to Today, Skills, Practice, Words and Progress at every target width. Words
passes at 320px and 375px with the canonical workbook filename rendered.

### 14.4 P3 — Band 8 wording was overconfident
**Accepted in full.** `Nothing holding it back` and `This response models the target`
were removed. The card now says `Annotated criteria demonstrated` and states that no
major weakness is identified *within the criteria annotated here*, while retaining the
illustrative, non-official qualification. Static validation rejects the old wording.

### 14.5 Still open
The native-Ukrainian editorial spot-check remains a human gate and is not represented as
an automation PASS. G4 and G5 status are unchanged until candidate 3 is independently
reviewed.
