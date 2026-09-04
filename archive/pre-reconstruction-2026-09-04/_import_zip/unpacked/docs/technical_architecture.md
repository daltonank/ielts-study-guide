# Technical Architecture

## Runtime
Static, mobile-first HTML/CSS/JavaScript application. No login or backend is required for Phase 1. LocalStorage is used for the compact learner state; the schema leaves room to move high-volume records to IndexedDB after G2 without changing the learner-facing contract.

## Core state
`ieltsC1UAEN.state.v1`

The learner state includes settings, diagnostic data, mastery, vocabulary learner state, errors, reviews, saved responses, practice/mock results, study history, recommendation state, and backups.

## Language modes
- `en`
- `uaen`
- `uahelp`

The mode is presentation support, not a second curriculum. English remains primary for exam content.

## Mastery
0 Not Assessed
1 Introduced
2 Guided
3 Independent
4 Timed
5 Mastered

Opening a module does not advance mastery.

## Content model
Curriculum modules and exercises are validated against JSON Schema. Later phases populate data only after preceding gates pass.

## Backup
Export uses a documented JSON learner-state file. Import performs top-level schema checks, preserves the current state as a backup snapshot, then replaces state only when validation passes.

## Vocabulary migration
`scripts/migrate_vocabulary.py` processes the exact legacy workbook and refuses to emit a “complete” vocabulary payload unless it finds exactly 1,784 normalized, unique Study Bank records with Ukrainian equivalents.

## Security / privacy
No external analytics, accounts, trackers or ad dependencies are included in the foundation build. Learner work stays in the local browser unless the learner explicitly exports it.


## Phase 3 Reading architecture
`reading_data.js` is generated from `scripts/build_reading_curriculum.py` and contains structured modules, family metadata, original passages and scored questions. The learner state stores active Reading navigation, answers, results and timer evidence. Incorrect results flow into the shared error log/review queue; results flow into shared practice history/mastery.
