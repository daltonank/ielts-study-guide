# IELTS Academic C1 • UA+EN Adaptive Study Webapp

This package is the gated production rebuild started from the approved master implementation specification.

## Open the app
Open `web/index.html` in a browser, or serve the `web` directory with any static HTTP server.

## Current gate status
- G0 Scope Locked: **PASS**
- G1 Platform Stable: **PASS**
- G2 Legacy Fully Integrated: **PASS**
- G3 Reading Complete: **PASS**
- G4–G10: **not yet gate-complete**

The package does **not** pretend that later phases are complete. G3 now passes with 60 original Reading texts, 240 scored questions, 15 Reading families, timed/mastery evidence, error integration and responsive validation. G4 and later remain unclaimed.

## Run validation
```bash
python scripts/validate_build.py
python tests/accessibility_static.py
python tests/responsive_check.py
python tests/g2_vocabulary_validation.py
python tests/ui_vocabulary_static.py
python tests/g3_reading_validation.py
python tests/g3_reading_functional.py
python tests/g3_reading_responsive.py
python tests/g3_reading_accessibility.py
```

## Vocabulary migration
`scripts/migrate_vocabulary.py` processes the exact legacy workbook and refuses to emit a “complete” vocabulary payload unless it finds exactly **1,784** normalized, unique Study Bank records with Ukrainian equivalents.

## Build philosophy
Learner loop:
Diagnose → Train → Practice → Capture error → Explain → Review → Retest → Update mastery → Adapt next session.

Build loop:
Requirements → Implement → Static validation → Functional test → Responsive test → Accessibility check → Content QA → Data QA → Regression → Ledger reconciliation → Defect repair → Gate decision.
