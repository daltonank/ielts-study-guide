# CHANGELOG.md

All notable product/gate changes are recorded here. Historical phase reports remain the detailed evidence.

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
