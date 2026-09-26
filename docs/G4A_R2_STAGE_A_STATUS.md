# G4A-CX-07 Stage A execution status

Stage A is a guarded post-migration correction layer under D-028. The gate remains
G4 technical PASS · G4-A CHANGES REQUESTED · G5 BLOCKED. This ticket makes no
semantic acceptance claim and does not start Stage B.

## Exact inputs and output

| Item | Pinned value |
|---|---|
| Execution base and merge base | `54daff49e05452eac3fef54e58a42c8719c673e5` |
| Accepted reconciliation checkpoint | `39d6f918c7087d3616acc9654eecfaf5219aefc4` |
| Accepted manifest SHA-256 | `99aeb25b16e697fd3cbe42349a09d7bda80e50079ac5e6c5507f960f4b2c187a` |
| Input learner Git blob | `1c184e84e5c63e3a9f8e386af13787664a23bd66` |
| Stage A payload SHA-256 | `cd3e9ff04734c51537e367fa9453e3b426812bcd9b0a2dae2252454df44be922` |
| Pinned output learner Git blob | `d3153cdb71f4768a04bed883953ea788a38e0aaf` |

The payload was built mechanically from the accepted manifest in stable-ID
order. It contains 250 rows, from `SB-0009` through `SB-1707`, with exactly
38 effective `ua` and 246 effective `definitionUa` replacements. Row shapes
are 4 `ua` only, 212 `definitionUa` only, and 34 with both fields. The accepted
`SB-1469.ua` proposal equals the input value, so the payload carries only its
effective `definitionUa` replacement.

## Validation evidence

Before learner mutation, all six accepted guards passed with `PYTHONUTF8=1`:
`g4a_r2_final_inventory.py`, `g4a_r2_supplemental_proposals.py`,
`g4a_r2_schema_compatibility.py`, `g4a_r2_reconciliation.py`,
`g4a_r2_batch3_packet.py`, and `g4a_r2_p1_remediation_manifest.py`.
These guards retain their pre-remediation learner-blob expectation and are
pre-apply checks; their historical pins were not changed.

The applicator computed the candidate entirely in memory, pinned its Git blob,
then recomputed byte-identical output twice from the untouched input. It read
the input again before its sole write and verified the written blob against
the pin. A CLI rerun rejected the Stage A output at the input-blob guard.

After application, `tests/g4a_r2_stage_a.py` passed. It independently checked
1,784 records and stable ID order; exactly 250 changed IDs and 284 changed
learner fields; accepted proposal equality; no other record or field changes;
unchanged wrapper metadata and `translationQa`; no blank Ukrainian fields;
UTF-8/LF output; and the pinned output blob. It compared all 301 prior tracked
files other than the learner bank to their exact accepted-base Git blobs, and
confirmed the reconciliation checkpoint remains available.

The validator proved all 15 Stage B full records and learner pairs unchanged:
`SB-1709`, `SB-1721`, `SB-1723`, `SB-1724`, `SB-1731`, `SB-1733`, `SB-1735`,
`SB-1738`, `SB-1747`, `SB-1750`, `SB-1752`, `SB-1753`, `SB-1759`, `SB-1760`,
`SB-1769`. It also confirmed `SB-1469.ua` unchanged and its `definitionUa`
changed as accepted.

Nine isolated negative cases passed without changing the canonical learner
file: wrong input blob, missing Stage A ID, injected Stage B ID, altered
replacement, altered current-pair fingerprint, inserted no-op correction,
unsupported field, wrong expected-output blob, and rerun against the applied
output.

Compatible general checks passed: `g2_vocabulary_validation.py`,
`ui_vocabulary_static.py`, `validate_build.py`, and
`g4a_migration_portability.py`. `git diff --check` passed. No browser suite
was needed because runtime code did not change.

GitHub CI/status is reported separately by the executor after push. PR #7,
issue #4 gate language, G5, the source workbook, and all accepted evidence
were untouched. Next reviewer action: G4A-RT-08. Stop before Stage B.
