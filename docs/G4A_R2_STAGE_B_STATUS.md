# G4A-CX-09 Stage B execution status

Stage B is a separate D-028 guarded post-migration correction layer on the exact
Stage A output. The gate remains G4 technical PASS · G4-A CHANGES REQUESTED ·
G5 BLOCKED. This stage makes no new Ukrainian linguistic judgment.

## Pinned inputs and output

| Item | Value |
|---|---|
| Exact Stage A base and required ancestor | `db65e13ce66190b48ae6c1039dd93930b2798b25` |
| Accepted manifest source | `54daff49e05452eac3fef54e58a42c8719c673e5` |
| Accepted manifest SHA-256 | `99aeb25b16e697fd3cbe42349a09d7bda80e50079ac5e6c5507f960f4b2c187a` |
| Stage A input learner Git blob | `d3153cdb71f4768a04bed883953ea788a38e0aaf` |
| Stage B payload SHA-256 | `4364894c28811db4a3581c05dbe4cd9f112af1cea3d0dbfc93a4cc004e20207a` |
| Stage B output learner Git blob | `e0e81c69084853f3e0db1ca35335e0c4dcb5007e` |

The payload was generated mechanically from the 15 accepted Stage B manifest
rows in stable-ID order. Each row carries the accepted current-pair SHA-256 and
only effective replacement fields. It has 1 `ua` and 15 `definitionUa`
replacements: 14 definition-only rows and `SB-1760` with both fields. There are
no blank or no-op replacements.

## Validation evidence

Before application, `tests/g4a_r2_stage_a.py` passed against the exact Stage A
learner blob. `tests/g2_vocabulary_validation.py`,
`tests/ui_vocabulary_static.py`, `scripts/validate_build.py`, and
`tests/g4a_migration_portability.py` also passed. Windows checkout line-ending
conversion was cleared by restoring tracked files from their exact Git blobs;
no accepted file's Git content changed.

The applicator computed the candidate in memory, pinned its Git blob, and
recomputed byte-identical output from the untouched Stage A input. It checked
the input again before its sole write. A CLI rerun failed at the input-blob
guard, as required.

The independent `tests/g4a_r2_stage_b.py` validator passed. It checked 1,784
records before and after, stable ID order, exactly 15 changed Stage B IDs, 16
changed fields, the 14/1 row shapes, every final value against the accepted
proposal, and all other target fields against Stage A. Every non-Stage-B
record is identical to Stage A, including all 250 Stage A records. Wrapper
metadata, `translationQa`, and all other fields are unchanged. No Ukrainian
field is blank. An independent manifest projection reproduced the exact output
bytes and pinned Git blob. All 305 tracked Stage A base/history files other
than the learner bank match their exact Git blobs.

Nine isolated negatives rejected without mutating the learner bank: wrong
input blob, missing Stage B ID, injected non-Stage-B ID, altered proposal,
altered current-pair fingerprint, no-op insertion, unsupported field, wrong
output pin, and rerun against Stage B output.

After application, the four compatible vocabulary/build checks above passed
again. `git diff --check` passed. No Stage A artifact or prior accepted evidence
was rewritten. PR #7, issue #4 gate language, G5, and fresh corrected-bank
acceptance sampling were untouched. GitHub CI/status is reported separately
after branch publication. Next reviewer action: G4A-RT-10.
