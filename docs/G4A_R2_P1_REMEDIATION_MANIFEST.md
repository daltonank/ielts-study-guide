# G4-A R2 P1 remediation manifest

Review-only plan, built from exact accepted base `cbadd2a4eda8cc5012313b0888f85d42f3edcd83`. It does not apply any
proposal or change the learner bank. Gate remains G4 technical PASS · G4-A
CHANGES REQUESTED · G5 BLOCKED.

## Population and partition

| Measure | Count |
|---|---:|
| Residual inventory | 1,007 |
| P1 manifest rows | 265 |
| Part-1 floor P1 | 63 |
| R2 reconciliation P1 | 202 |
| Existing accepted proposals | 234 |
| Accepted supplemental proposals | 31 |
| Stage A | 250 |
| Stage B | 15 |

The P1 IDs are sorted lexically. Stage A is the first 250 (`SB-0009` through
`SB-1707`); Stage B is the final 15:

SB-1709, SB-1721, SB-1723, SB-1724, SB-1731, SB-1733, SB-1735, SB-1738, SB-1747, SB-1750, SB-1752, SB-1753, SB-1759, SB-1760, SB-1769.

## Proposal interpretation

`proposal_fields` lists every field represented in the accepted proposal.
`effective_fields` lists only represented fields whose value differs from the
current learner bank. Order is always `ua|definitionUa`.

| Field | Proposed | Effective |
|---|---:|---:|
| `ua` | 40 | 39 |
| `definitionUa` | 261 | 261 |

The only no-op proposal field is `SB-1469.ua`: its accepted `ua` is
`зареєстрований`, identical to the learner value, while its `definitionUa`
correction remains effective.

`source_proposed_target` and `source_proposed_value` retain legacy floor and
reconciliation proposal text, including strict `both` strings. They are blank
for the 31 supplemental rows because that accepted source already has separate
`proposed_ua` and `proposed_definitionUa` columns. `proposal_source` gives the
exact source CSV path. `finding_evidence` comes from floor intake evidence or
the reconciliation evidence quote. `finding_rationale` retains the distinct
reconciliation rationale; it is blank for floor findings. `proposal_rationale`
contains the accepted supplemental rationale; it is blank when the legacy
source has no distinct proposal rationale. `confidence` is the proposal-source
confidence. `finding_confidence` preserves final-inventory finding confidence.
These differ for 11 supplemental rows; both are retained.
`proposal_evidence_quote` preserves the accepted supplemental quote and is blank
for legacy rows that have no separate proposal quote.

Each `current_pair_sha256` is SHA-256 over UTF-8 bytes of
`id + NUL + current_ua + NUL + current_definitionUa`. This fingerprints the
current learner pair for later review, without predicting any remediation output.

## Integrity

- Manifest SHA-256: `99aeb25b16e697fd3cbe42349a09d7bda80e50079ac5e6c5507f960f4b2c187a`
- Learner vocabulary git blob: `1c184e84e5c63e3a9f8e386af13787664a23bd66` (unchanged)
- Accepted reconciliation checkpoint: `39d6f918c7087d3616acc9654eecfaf5219aefc4` (byte-frozen inputs)
- Supplemental and inventory source base: `cbadd2a4eda8cc5012313b0888f85d42f3edcd83` (byte-frozen inputs)
- Generated artifacts: deterministic UTF-8 with LF line endings
- Next action: ChatGPT G4A-RT-06 review. No Stage A work is authorized here.
