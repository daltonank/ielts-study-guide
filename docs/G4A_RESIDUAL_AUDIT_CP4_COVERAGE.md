# G4-A Residual-Population Audit — CP4: Coverage, Manifests, Meta-Validation

**Audit branch:** `claude-code/4-g4a-residual-audit`  
**Baseline:** `f34f109ae5b8564e7fa10317c167a6ca728c52fd`  
**web/vocabulary.js blob:** `1c184e84e5c63e3a9f8e386af13787664a23bd66` (unchanged)  
**Gate language (unchanged):** `G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED`

## Coverage proof

`tests/g4a_residual_audit_coverage.py` proves every residual ID (1,007) appears exactly once in the CP3 inventory with a valid disposition — none skipped. Coverage = examined / residual-total = **1007 / 1007 = 100%**.

## Remediation manifests (PROPOSALS ONLY — not applied)

Partition rule: **category then stable ID ascending**; each defect ID appears in exactly one manifest (non-overlapping). Manifests edit no data; `applied` is `false` for every entry and `web/vocabulary.js` is untouched.

| Manifest | Entries | Bytes |
|---|---|---|
| `scripts/qa/cp4_manifest_grammar_calque_fragment.json` | 10 | 8369 |
| `scripts/qa/cp4_manifest_pos_morphology_mismatch.json` | 11 | 8123 |
| `scripts/qa/cp4_manifest_semantic_pedagogical_error.json` | 9 | 7312 |
| `scripts/qa/cp4_manifest_other.json` | 2 | 1952 |
| **total** | **32** | |

Total defects manifested: **32** (25 P1 + 7 P2). Manifest ID set == inventory defect ID set (verified in-script). These are non-binding proposals for a follow-up remediation ticket; this audit applies none of them.

## Meta-validation (non-vacuity)

`scripts/qa/cp4_meta_validation.py` plants one synthetic defect of each audited class into an in-memory COPY of the bank (never `web/vocabulary.js`) and confirms the CP2 detectors catch each. See its recorded output for planted/detected counts. The deterministic G4-A gate and the T5-B repeat guard additionally carry their own seeded-negative self-checks (CP1).

