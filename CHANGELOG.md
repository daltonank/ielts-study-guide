# CHANGELOG.md

All notable product/gate changes are recorded here. Historical phase reports remain the detailed evidence.

## 2026-09-09 — G4-A P1 closeout: T3, T4, and SB-0773

**Gate:** unchanged — `G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`.
No G4-A PASS is claimed because T5 remains outstanding.

### Changed
- T3 resolved 103 of its 104 findings through 102 learner-facing edits and one
  resolved-via-sibling disposition. It deferred malformed headword `SB-0773`.
- T4 applied all 103 semantic-fidelity corrections, including the approved `SB-1519`
  production sense.
- `SB-0773` now uses `minute` in both the source workbook and `web/vocabulary.js`.
  A dedicated regression enforces normalized-headword uniqueness.

### Verified
- Guarded vocabulary blobs: `fe46b30a` → `3427a6a5` → `0d144c70` → `9282d201`.
- `tests/g4a_p1_closeout_accounting.py` reconciles all 314 registered P1 findings:
  3 earlier fixes plus the 311 canonical T2-T4 IDs. Remaining backlog is **0 P1 +
  246 P2**.

## 2026-09-09 — G4-A T2: first P1 vocabulary batch applied (104 corrections)

**Gate:** unchanged — `G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`. No G4-A PASS claimed.
`web/vocabulary.js` is the only learner-facing `web/*` file changed.

### Changed
- Applied the **104-correction T2 P1 batch** (circular-definition 26 / grammar 60 / other 18)
  to `web/vocabulary.js` via a guarded, reproducible pipeline (`scripts/qa/apply_p1_t2_fixes.py`
  reading `scripts/qa/p1_t2_corrections.json`): fixed review date 2026-09-09, input/output
  git-blob guards (`414fbeac` → `fe46b30a`), idempotent fail-closed — mirroring the P0 mechanism.
- Reviewer overrides: **SB-1629 (transport)** carries both noun and verb senses; **SB-1378
  (assistance)** and **SB-1393 (elements)** disambiguated to resolve deterministic-gate `ua`
  collisions.

### Verified
- `tests/g4a_ukrainian_deterministic.py` EXIT 0 (no new collisions; both prior collisions resolved);
  record count 1,784 unchanged; all 104 ids changed. Full regression packet re-run green
  (`release_integrity.py` fails only on a missing local git tag — environmental).

### Remaining
- **207 P1** (311 − 104) + **246 P2** open; batches **T3/T4** pending. AI linguistic QA, honestly
  labelled. Evidence: `docs/G4A_P1_BATCH_STATUS.md`, `docs/G4A_P1_BATCH_MANIFEST.md`.

## 2026-09-08 — D-027 approved: G4-A acceptance standard reconciled

- D-027 approved by Dalton (AI linguistic QA + learner flag loop replaces the mandatory native-Ukrainian editorial gate as the G4-A acceptance standard); G4-A remains CHANGES REQUESTED pending P1 remediation and the T5 flag loop.

## 2026-09-08 — G4-A T1: spot-check triage, P1 batch manifests, acceptance-policy reconciliation

**Gate:** unchanged — `G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`. No G4-A PASS claimed.
No learner-facing `web/*` files changed (docs/CSV/tests only).

### Added
- Triaged the **27 spot-check findings** (9 P1 + 18 P2) in `docs/G4A_UKRAINIAN_QA_FINDINGS.csv`
  that previously lacked a `proposed_correction`/`confidence`; severity re-confirmed with no
  reclassification. AI linguistic QA, honestly labelled. Evidence: `docs/G4A_SPOTCHECK_TRIAGE.md`.
- Deterministic P1 remediation batch manifests **T2/T3/T4** — 311 unresolved P1 findings (314 P1
  minus the 3 applied in PR #3), sorted `(category ASC, id ASC)`, partitioned contiguously into
  104/104/103, pairwise-disjoint, union-complete: `docs/g4a_p1_batches.json`,
  `docs/G4A_P1_BATCH_MANIFEST.md`.
- Decision **D-027 (Proposed)**: AI linguistic QA + a learner-facing flagging loop proposed to
  replace the mandatory pre-release native-Ukrainian editorial gate; awaits Dalton's approval.

### Changed
- Reconciled `CURRENT_STATE.md`, `docs/G4A_UKRAINIAN_QA_AUDIT_PLAN.md`,
  `docs/G4A_P0_FIXES_STATUS.md` and `docs/G4A_UKRAINIAN_QA_FINDINGS.md` to the merged
  **PR #2 + PR #3** state (current `main` HEAD `6d3bb41`). Corrected the stale
  "deterministic gate fails by design (exit 1) / `G4A-V-001`" note — that gate now **PASSES**
  on current `main` (`SB-0208`/`SB-0432`/`SB-1728` no longer share the circular gloss).

### Not changed
- No learner-facing vocabulary corrections applied; the spot-check corrections are recorded in
  the register only and deferred to batch tickets T2–T4.

## 2026-09-05 — G4 external re-review: four findings addressed

**Gate:** G4 Writing Task 1 — **INTERNAL PASS, EXTERNAL RE-REVIEW PENDING.**
Candidate `g4-candidate-3`. The next independent review must approve it before G4 PASS;
G5 remains blocked.

### Fixed
- **R2-001 (P1)** reconciled five Band 6 annotation sets with their final extended
  responses. Diagnostics now acknowledge the comparisons, exceptions, cycle language and
  compass directions actually present while explaining why they remain weakly organised.
- **R2-002 (P2)** removed the canonical Band 8 `respectively` construction. Canonical
  model responses and band samples now reject `respectively` until ordered entity/value
  binding exists (D-024).
- **R2-003 (P2)** made long notice text, including
  `IELTS_Academic_C1_Ukrainian_Vocabulary_Bank.xlsx`, wrap safely. The whole-app responsive
  test now measures document and body overflow after navigating to every primary route.
- **R2-004 (P3)** replaced `Nothing holding it back` with bounded, criteria-specific copy:
  `Annotated criteria demonstrated` and an explicit non-official-sample qualification.
- **D4-009 (P2, found during full-suite verification)** fixed a 3px overflow on the
  320px Task 1 family list. Mobile foundation module cards now use two shrinkable columns
  and place their action button across the full row.

### Added
- Machine-readable `diagnosticChecks` linking displayed Band 6 annotations to required or
  forbidden phrases in the adjacent response (D-025).
- Two seeded negative cases: the actual non-interleaved multi-entity `respectively` shape,
  and a prose edit that contradicts its teaching diagnostic. The negative suite now catches
  **8 of 8** defects independently and restores the artifact.
- Requirements `REQ-018D`, `REQ-019D` and `REQ-020I` for ordered value safety,
  annotation/prose consistency and per-route whole-document overflow.

### Verified
All 21 packet commands pass after the changes. Browser checks ran against Chromium at
320/375/430/768/1024/1440; the Words route has no document or body overflow at 320px or
375px. The gate remains pending external re-review rather than being promoted from an
executor completion statement.

---

## 2026-09-05 — G4 external review round 1: changes requested and made

**Gate:** G4 Writing Task 1 — **INTERNAL PASS, EXTERNAL RE-REVIEW PENDING.**
Candidate `g4-candidate-2`. See `docs/G4_EXTERNAL_REVIEW_PACKET.md` §12 for the
finding-by-finding response.

An external reviewer independently reran the whole suite against candidate `fe720d5`,
found it green, and still returned **CHANGES REQUESTED** on five findings the suite could
not see. All five are fixed here, and checking the fixes on a real 375px viewport turned
up a sixth defect that had been in the stylesheet since G1.

### Fixed
- **R1-001 (P1)** eighteen of 21 band samples were under the 150-word Academic Task 1
  minimum, four of them in the "Strong" position, so length was an uncontrolled variable
  between the three levels. Every sample is now 158-202 words, written in its own voice,
  and the generator refuses to emit a shorter one (D-022).
- **R1-002 (P1)** mastery L4 and L5 could be reached with a 20-word response. Both now
  require a response of at least 150 words as well as the timing and checklist conditions.
  An underlength submission logs the new `underlength_response` error category instead
  (D-022, amending D-015 and D-016).
- **R1-003 (P2)** report-level grounding authorised a set of figures with no opinion about
  which entity each belonged to, so two real values could be swapped between two series and
  still pass. Canonical prose is now bound sentence by sentence: a figure may cite only a
  fact whose subjects are named in its own clause (D-021).
- **R1-004 (P2)** the packet named a candidate SHA that no commit in the repository has.
  The candidate is now a git tag, and `tests/release_integrity.py` fails if it does not
  resolve, if the packet inside the tagged commit names a different release, or if any
  hash or path the packet cites does not exist (D-023).
- **R1-005 (P3)** the Task 1 inventory printed `Completed 0+0`; it now reads
  `Exercises done 0 / 70` and `Prompts answered 0 / 21`. Reading foundation modules printed
  `foundation • undefined min`; the duration is now shown only where there is one.
- **D4-008 (P2, found while verifying the above)** `.half`, `.third` and `.twoThird` only
  received a column span at 760px and above. `.card` carries its own span, so cards were
  fine and the bug stayed invisible — but every other grid child collapsed to one twelfth
  of the row on a phone: the band-lab annotation blocks rendered as 28px slivers of
  vertical text, and the four vocabulary filters on the Words screen as 14px slivers.

### Added
- `tests/g4_writing1_negative.py` — six seeded defects, each required to fail the guard
  that should catch it, every file restored afterwards.
- `tests/release_integrity.py` — the review packet must identify a release that resolves.
- Sentence-level claim tuples in `web/writing1_data.js`, and an independent
  re-implementation of the binder in `tests/g4_writing1_claims.py` that resolves fact keys
  against the visual's label vocabulary rather than building them structurally.
- Band samples carry `styleLabel` ("Illustrative Band N-style sample"), `wordMinimum` and
  `meetsMinimum`; each set maps its compared aspects to the four public IELTS Writing
  criteria and points at the published descriptors without reproducing them.
- `tests/g4_writing1_responsive.py` now walks the band lab at all six widths;
  `tests/responsive_check.py` measures every grid child on all five primary routes.
- Screenshots `docs/qa_w1r2_*.png` at 1440, 375 and 320.
- `DECISIONS.md` D-021, D-022, D-023.

### Verified
All 21 scripts pass, plus the seeded-defect proof: 6 of 6 defects caught and the restored
artifact still passes.

---
## 2026-09-04 — G4 closure audit

**Gate:** G4 Writing Task 1 — **INTERNAL PASS, EXTERNAL REVIEW PENDING.**
See `docs/G4_EXTERNAL_REVIEW_PACKET.md`.

### Corrected
- **REQ-019, the Task 1 band comparison lab, had been recorded as satisfied by argument** rather than by implementation: the ledger note claimed band comparison was a G5 concern. REQ-019 is a phase-4 row. The lab now exists — 7 sets (one per visual family), 21 sample responses, a per-aspect comparison table, and labels disclaimed as describing the samples rather than the learner.
- Gate status corrected from `PASS` to `INTERNAL PASS — EXTERNAL REVIEW PENDING` in `CURRENT_STATE.md`, `PROJECT_CHARTER.md`, `VALIDATION_SPEC.md`, `PRODUCT_SPEC.md`, `CURRICULUM_SPEC.md`, `docs/phase_4_report.md` and the dashboards, because the planned cross-provider review did not occur.

### Added
- `tests/g4_writing1_inventory.py` — machine-derived counts with every benchmark as a hard failure.
- `tests/g4_writing1_claims.py` — exhaustive canonical-claim validation across all 529 text blocks.
- `tests/g4_writing1_persistence.py` — real HTTP server: genuine browser reload, export/import round-trip, malformed-import rejection, backup retention, search, keyboard-only operation.
- `tests/g4_writing1_obstruction.py` — real viewport states at six widths: sticky overlap, skip-link focus state, contained scrolling.
- `docs/G4_EXTERNAL_REVIEW_PACKET.md`; `DECISIONS.md` D-020.
- Real-viewport screenshots `docs/qa_w1_viewport_*.png`, `docs/qa_w1_skiplink_*.png`.

### Fixed
- **D4-006 (P2)** grounding authorised any arithmetically derivable figure, including column totals and pairwise sums, so an item could look supported without being the intended claim. Replaced by the canonical claim manifest.
- **D4-007 (P3)** `.w1-chart{margin:0 -2px}` made every chart 4px wider than its parent's content box.

### Resolved as not-a-defect
The apparent header obstruction in the earlier full-page screenshots was a capture artifact: full-page screenshots render sticky and fixed elements at scroll position. Real viewport captures confirm nothing sticky covers content at any of the six widths, and that the skip link is hidden until focused.

---

## 2026-09-04 — G4 Writing Task 1: learner-facing UI

**Gate:** G4 Writing Task 1 — UI delivered (gate decision superseded by the audit above).

### Added
- Writing Task 1 academy in `web/app.js`, reached from Skills → Writing Task 1 and the drawer. Family list, family module page, micro-exercise workspace and the plan → timed draft → self-review flow.
- The `.w1-visual` component (`web/styles.css`, documented in `UX_DESIGN_SPEC.md` §8, recorded as D-019): inline SVG rendering for line, bar and pie charts, real tables, numbered stage lists for processes and status-coded feature lists for maps, each with a legend, a data table and a text equivalent.
- Three interaction types: single-select with per-option reasoning, cloze with accepted variants, and keyboard-operable paragraph ordering.
- `tests/g4_writing1_functional.py`, `tests/g4_writing1_responsive.py`, `tests/g4_writing1_accessibility.py`.
- QA screenshots `docs/qa_w1_*.png`, one per visual family plus mobile, desktop and 320px surfaces.
- `docs/phase_4_report.md`. `DECISIONS.md` D-019.

### Changed
- `web/index.html` loads `writing1_data.js`.
- `renderSkills` links into Reading and Writing Task 1 and caps the module preview at six.
- Global search covers Writing Task 1 visuals and exercises.
- `.reading-family-grid` / `.reading-family-card` generalised to also match `.family-grid` / `.family-card` rather than duplicating the rules.
- The four existing browser tests now inline `writing1_data.js`, so they exercise the real page.

### Fixed
- **D4-002 (P2)** exercise controls stayed disabled after an attempt, making "Try again" impossible.
- **D4-003 (P3)** `.field textarea` out-specified `.w1-draft`, leaving the drafting box 73px tall at every width.
- **D4-004 (P3)** `.question-card label{display:grid}` out-specified `.w1-opt`, stacking each radio above its option text.
- **D4-005 (P3)** the chart axis caption collided with the top tick label.

### Verified
All fourteen scripts pass, Edge as the Chromium binary. Responsive and accessibility evidence generated for all seven visual families at 320/375/430/768/1024/1440.

---

## 2026-09-04 — G4 Writing Task 1: content layer

**Gate:** G4 — content layer complete and validated (the UI followed in the entry above).

### Added
- `scripts/build_writing1_curriculum.py` — the G4 generator, following the G3 pipeline shape.
- `web/writing1_data.js` — `window.WRITING1_DATA`: 7 visual families, 21 original visuals, 70 micro-exercises (benchmark 60), 21 full timed prompts (benchmark 20), 4 foundation modules, 7 family modules, a 12-category error taxonomy and the mastery rules from D-015.
- `tests/g4_writing1_validation.py` — re-parses the artifact and re-derives every check from the specification, including an independent re-implementation of the fact engine.
- `tests/g4_writing1_content_qa.py` — re-derives 115 quantified prose claims from the underlying data.
- `tests/browser_env.py` — portable Chromium resolution for the Playwright suites.
- `docs/writing1_content_qa.md` — the three-layer content QA record.
- `DECISIONS.md` D-015 (Task 1 mastery thresholds), D-016 (12-category error taxonomy), D-017 (grounding by re-derived facts), D-018 (local toolchain requirements).
- 21 new G4 requirement IDs in `docs/requirements_ledger.csv` (REQ-017A–I, REQ-018A–C, REQ-019A, REQ-020A–G, REQ-048B). No existing ID was renumbered.

### Fixed
- **Defect D4-001 (P2).** `tests/responsive_check.py`, `tests/g3_reading_responsive.py`, `tests/g3_reading_functional.py` and `tests/g3_reading_accessibility.py` hard-coded `executable_path="/usr/bin/chromium"`, so every browser-driven gate check failed to launch outside the Linux environment G3 was authored in. The checks themselves were correct; only the browser lookup was not portable. All four now pass again.

### Changed
- `scripts/build_benchmark.py` now reads the Task 1 counts from `web/writing1_data.js` instead of hard-coding zeros.
- `docs/benchmark_dashboard.{json,md}` regenerated.

### Verified this session (by running the scripts, not by reading reports)
`scripts/validate_build.py`, `tests/g2_vocabulary_validation.py`, `tests/g3_reading_validation.py`, `tests/responsive_check.py`, `tests/g3_reading_responsive.py`, `tests/g3_reading_functional.py`, `tests/g3_reading_accessibility.py`, `tests/accessibility_static.py`, `tests/ui_vocabulary_static.py`, `tests/g4_writing1_validation.py`, `tests/g4_writing1_content_qa.py` — all pass. Browser used: Microsoft Edge (Chromium).

The G4 validator was itself tested against ten seeded defects; all ten were caught and the clean artifact still passed.

### Not done
The Writing Task 1 UI. The `task1` route still renders the `genericLab` placeholder, so no G4 requirement that depends on delivery — autosave, responsive rendering, accessibility of the visuals, mastery enforcement, error/review integration — can be assessed yet.

---

## 2026-09-04 — Project documentation reconstruction

### Added
- `PROJECT_CHARTER.md`
- `PRODUCT_SPEC.md`
- `CURRICULUM_SPEC.md`
- `UX_DESIGN_SPEC.md`
- `VALIDATION_SPEC.md`
- `CLAUDE.md`
- `CONTEXT.md`
- canonical `CURRENT_STATE.md`
- canonical `DECISIONS.md`
- recovery manifest

### Recovered
The earlier G0–G3 build archive was recovered and shown to contain the structured `web/`, `schemas/`, `scripts/`, `tests/`, and validation-document artifacts cited by the gate reports.

No implementation artifacts were recreated when an original recoverable copy existed.

---

## 2026-09-04 — G3 Reading Academy

**Gate:** G3 Reading Complete — PASS

### Added
- 8 Reading foundation strategy modules
- 15 major Reading question-family modules
- 60 original practice texts/extracts
- 240 scored questions
- 240 answer explanations
- Reading timed/mastery evidence
- automatic Reading error logging
- review-item creation
- responsive/accessibility validation

### Regression
G0–G2 platform and vocabulary behavior passed regression.

---

## 2026-09-04 — G2 Legacy/Vocabulary Integration

**Gate:** G2 Legacy Fully Integrated — PASS

### Added
- deterministic vocabulary migration
- 1,784-record reconciled `web/vocabulary.js`
- vocabulary migration manifest
- vocabulary filters/search metadata
- vocabulary source-data validation

### Source reconciliation
- Oxford C1: 1,315
- AWL: 570
- normalized Study Bank: 1,784
- overlaps: 100
- Starter 100: 100

An earlier blocked G2 report caused by unavailable workbook bytes is historical and superseded by the later reconciled release.

---

## 2026-09-04 — G1 Foundation & Design System

**Gate:** G1 Platform Stable — PASS

### Added
- mobile-first continuous-scroll shell
- five-item primary navigation
- EN / UA+EN / UA Help
- design tokens/components
- learner/module/exercise schemas
- LocalStorage state
- JSON export/import protection
- mastery model
- Today recommendation shell
- Review Today shell
- error schema
- writing autosave field
- timer
- global search shell
- vocabulary preview behavior
- accessibility primitives
- responsive coverage at 320/375/430/768/1024/1440

---

## 2026-09-04 — G0 Audit & Requirements Lock

**Gate:** G0 Scope Locked — PASS

### Added
- stable requirement IDs
- legacy inventory
- risk register
- regression checklist
- requirements ledger
- phase-gate framework

### Established
The legacy study guide and vocabulary workbook were classified for preservation/migration rather than discarded.
