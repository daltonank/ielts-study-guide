# Live Build Benchmark Dashboard

**Updated:** 2026-09-04 (G4 complete)

| Metric | Current | Approved benchmark | Status |
|---|---:|---:|---|
| Requirements ledger rows | 131 | complete traceability | Active |
| Legacy vocabulary loaded | 1,784 | 1,784 | **Pass** |
| Legacy vocabulary source records reconciled | 1,784 / 1,784 | 1,784 / 1,784 | **Pass** |
| Reading foundation modules | 8 / 8 | all required foundations | **Pass** |
| Reading question-family modules | 15 | all major families | **Pass** |
| Reading passages/extracts | 60 | ≥50 | **Pass** |
| Reading questions | 240 | ≥200 | **Pass** |
| Reading answer explanations | 240 / 240 | 100% | **Pass** |
| Task 1 visual families | 7 / 7 | 7 | **Pass** |
| Task 1 original visuals | 21 | 3 per family | **Pass** |
| Task 1 micro-exercises | 70 | ≥60 | **Pass** |
| Task 1 micro-exercise types per family | 10 / 10 | all 10 in every family | **Pass** |
| Task 1 full timed prompts | 21 | ≥20 | **Pass** |
| Task 1 foundation modules | 4 | — | Complete |
| Task 1 error taxonomy categories | 12 | ≥10 | **Pass** |
| Task 1 data-grounding validation | 70 exercises + 21 model responses | every figure derivable from its own visual | **Pass** |
| Task 1 prose-claim QA | 115 claims re-derived, 0 failed | all quantified prose claims true | **Pass** |
| Task 1 UI | delivered | learner-facing delivery | **Pass** |
| Task 2 prompts | 0 | ≥60 | Not started |
| Task 2 drills | 0 | ≥100 | Not started |
| Grammar items | 0 | ≥250 | Not started |
| Paraphrase items | 0 | ≥100 | Not started |
| Speaking Part 1 | 0 | ≥120 | Not started |
| Speaking Part 2 | 0 | ≥75 | Not started |
| Speaking Part 3 | 0 | ≥150 | Not started |
| P0 defects | 0 | 0 | **Pass** |
| P1 defects | 0 | 0 at release | **Pass** |
| P2 defects | 0 open (2 fixed: D4-001, D4-002) | resolve before gate | **Pass** |
| P3 defects | 0 open (5 fixed) | should not accumulate | **Pass** |
| Responsive target widths | 6 / 6 passed | 6 / 6 | **Pass** |
| Reading responsive target widths | 6 / 6 passed | 6 / 6 | **Pass** |
| Task 1 responsive target widths | 6 / 6 passed, all 7 families | 6 / 6 | **Pass** |
| Task 1 accessibility, all families | 7 / 7 passed | text equivalents + labelled controls | **Pass** |
| Task 1 functional flow | passed | scoring, mastery, timing, autosave, error/review, reload | **Pass** |
| Accessibility automated score | not fully measurable in current harness | ≥95 at G10 | Deferred to G10 |

Phase gates passed: **G0, G1, G2, G3, G4**.
Next gate: **G5 — Writing Task 2.**

## How the Task 1 rows were verified

Every figure above came from running the script, not from reading a report:

- `python scripts/build_writing1_curriculum.py` → `web/writing1_data.js`
- `python tests/g4_writing1_validation.py` → PASS (re-parses the artifact and re-derives every check independently of the generator)
- `python tests/g4_writing1_content_qa.py` → 115 claims checked, 0 failed
- `python tests/g4_writing1_functional.py` → PASS
- `python tests/g4_writing1_responsive.py` → PASS at all six widths, all seven families
- `python tests/g4_writing1_accessibility.py` → PASS
- `python scripts/build_benchmark.py` → regenerated `docs/benchmark_dashboard.json`

The validator was itself checked against ten seeded defects (fabricated figure, substituted family, tampered fact, missing distractor reasoning, missing overview, missing micro-type, pie not summing to 100, band claim, dangling module reference, stripped Ukrainian note). All ten were caught and the clean artifact still passed.
