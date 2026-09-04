# RECOVERY_MANIFEST.md

## Purpose

This manifest records which Claude-requested files were recovered from existing ChatGPT Library artifacts and which genuinely did not exist as standalone project files and were therefore authored during reconstruction.

Reconstruction date: **2026-09-04**

---

## A. Canonical files Claude reported missing

| File | Status | Action |
|---|---|---|
| `PROJECT_CHARTER.md` | Not found as standalone prior artifact | Authored from approved master context, requirement ledger, and gate reports |
| `PRODUCT_SPEC.md` | Not found as standalone prior artifact | Authored |
| `CURRICULUM_SPEC.md` | Not found as standalone prior artifact | Authored |
| `UX_DESIGN_SPEC.md` | Not found as standalone prior artifact | Authored |
| `VALIDATION_SPEC.md` | Not found as standalone prior artifact | Authored |
| `README.md` | Found in existing G0–G3 source ZIP | Recovered unchanged |
| `CLAUDE.md` | Not found as standalone prior artifact | Authored |
| `CONTEXT.md` | Exact filename absent; detailed `LESIA_IELTS_CLAUDE_CONTEXT.md` existed | Authored concise canonical entry point; preserved detailed source |
| `CHANGELOG.md` | Not found as standalone prior artifact | Authored from gate reports |

---

## B. Implementation artifacts Claude reported missing

All of the following were found inside the previously generated:

`IELTS_C1_UAEN_Adaptive_Webapp_G0-G3.zip`

They were recovered rather than recreated.

### Web
- `web/index.html`
- `web/app.js`
- `web/styles.css`

Also recovered:
- `web/data.js`
- `web/vocabulary.js`
- `web/reading_data.js`

### Schemas
- `schemas/learner_state.schema.json`
- `schemas/module.schema.json`
- `schemas/exercise.schema.json`

### Scripts
- `scripts/migrate_vocabulary.py`

Also recovered:
- `scripts/build_benchmark.py`
- `scripts/build_reading_curriculum.py`
- `scripts/validate_build.py`

### Tests
- `tests/responsive_check.py`
- `tests/g3_reading_validation.py`
- `tests/g3_reading_functional.py`
- `tests/g3_reading_responsive.py`
- `tests/g3_reading_accessibility.py`

Also recovered:
- `tests/accessibility_static.py`
- `tests/g2_vocabulary_validation.py`
- `tests/ui_vocabulary_static.py`

### Docs
- `docs/legacy_content_inventory.csv`
- `docs/regression_checklist.md`
- `docs/risk_register.csv`

---

## C. Other existing artifacts recovered

- `requirements_ledger.csv` (archive copy is under `docs/`)
- `benchmark_dashboard.md`
- `phase_0_report.md`
- `phase_1_report.md`
- `phase_2_gate_report.md`
- `phase_3_report.md`
- `reading_content_qa.md`
- `reading_inventory.json`
- `technical_architecture.md`
- `vocabulary_migration_manifest.json`
- `LESIA_IELTS_CLAUDE_CONTEXT.md`
- `IELTS_Academic_C1_Ukrainian_Vocabulary_Bank.xlsx`
- `IELTS_C1_UAEN_G1_Platform_Release.html`
- `IELTS_C1_UAEN_G3_Reading_Complete_Release.html`
- `legacy/ielts_c1_ukrainian_study_guide_v2.html`

---

## D. Claude-local files not available to ChatGPT for byte-for-byte recovery

Claude reported these local files, but their exact local copies were not available through ChatGPT Library:

- `claude-dev/CURRENT_STATE.md` — reported as placeholder only
- `claude-dev/DECISIONS.md` — reported to contain D-014
- `claude-dev/INBOX.md`
- `claude-dev/REQUIREMENT_IDS.md`
- Claude-local copy of `claude-dev/CLAUDE_WORKSPACE_SCOPE.md`

Actions taken:

- a canonical `CURRENT_STATE.md` was authored because the reported local version was an empty template;
- `DECISIONS.md` was reconstructed with the known D-014 decision and no invented product decisions;
- `CLAUDE_WORKSPACE_SCOPE.md` was recovered from ChatGPT Library;
- `INBOX.md` was not overwritten because its exact Claude-local content is unknown and it is not required to reconstruct the current passed gates;
- `REQUIREMENT_IDS.md` was not overwritten because the authoritative stable IDs already exist in `docs/requirements_ledger.csv`.

---

## E. Important status correction

Claude's local-folder inspection concluded that the cited source/test artifacts did not exist in that folder.

That was true of the folder Claude inspected, but **not true of the project artifact history**.

The prior G0–G3 build ZIP contains those structured files. The correct action is therefore to import/reconcile this recovered structured workspace into Claude rather than recreate the app from the standalone release HTML.
