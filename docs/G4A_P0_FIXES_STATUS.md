# G4-A P0 Corrections — Status

**Date:** 2026-09-06
**Scope:** the 142 P0-severity findings from the G4-A Ukrainian linguistic QA
audit (see `docs/G4A_UKRAINIAN_QA_FINDINGS.md`, `DECISIONS.md` D-026 on the
`claude-code/g4a-ukrainian-qa-audit` branch / PR #2).
**Authorization:** executed under Dalton's explicit instruction "batch-fix
the 142 P0 entries first."

## What was done

Each of the 142 P0 findings was individually reviewed and given a concrete,
editorially-final correction (not the audit's original vague
`proposed_correction` text) for `ua` and/or `definitionUa`, plus `pos`
and/or `register` for 4 entries whose part-of-speech or register tag was
itself wrong. All 142 entries' `translationQa` field was updated from
`"Draft — verify in context"` to `"Reviewed — G4-A P0 correction applied
(2026-09-06)"` to record the sign-off.

This is captured as a small, self-contained patch:

- `scripts/qa/p0_corrections.json` — the 142 corrections, keyed by
  vocabulary entry ID.
- `scripts/qa/apply_p0_fixes.py` — applies them to `web/vocabulary.js` in
  place, with built-in sanity checks (record count stays 1784, no
  duplicate IDs, no blank `ua`/`definitionUa`).

## Verification already performed

The script was run against a clean checkout of `web/vocabulary.js` from
`main` (`52d12ddd2c52f9d822a5677b98ee30649ccd61a6`) in this session's local
clone, and validated:

- `tests/g4a_ukrainian_deterministic.py` — PASS (Draft count drops from
  1784/1784 to 1642/1784, confirming exactly 142 entries newly reviewed;
  no missing/corrupted/placeholder content introduced).
- `tests/g2_vocabulary_validation.py` — PASS (1784 records, unique IDs,
  Ukrainian fields present).
- `tests/ui_vocabulary_static.py` — PASS.
- `scripts/validate_build.py` — PASS.

The resulting `web/vocabulary.js` is byte-identical every time the script
is run against that base commit — confirmed via git blob hash
`e054ad8d2164b94fd78df8e77caf9f22ac29b04d` (sha256
`07751146e33998c08ee980679f82d1aa25e45f2ceda89ef6b30797c90b7d77eb`).

## Why `web/vocabulary.js` itself is not included in this PR

`web/vocabulary.js` is single-line-minified JSON, ~1.5 MB, ~1.52M
characters. The only tools available to this session for writing to
GitHub require the complete new file content to be transmitted inline in
one call; a file this size exceeds what can be reliably transmitted that
way (as with the 702-row findings CSV noted in PR #2, but at roughly 15×
the size — large enough here that attempting it risks a truncated,
corrupted push rather than just an inconvenience). This is a tool/session
limitation, not an authorization or correctness issue — the fix itself is
fully specified, deterministic, and already verified above.

**To land the actual data change**, from a clone with normal `git` access
(e.g. Dalton's own machine — outside this session's git-proxy
restrictions):

```bash
git fetch origin claude-code/g4a-vocab-p0-fixes
git checkout claude-code/g4a-vocab-p0-fixes
python3 scripts/qa/apply_p0_fixes.py
git add web/vocabulary.js
git commit -m "Apply 142 P0 Ukrainian translation corrections to vocabulary.js"
git push
```

The byte-identical corrected `web/vocabulary.js` has also been delivered
directly to Dalton in this session as a ready-to-use file, if simply
replacing the file is preferred over running the script.

## What's left

- Apply this patch to `web/vocabulary.js` on this branch (above), then
  this PR is ready to merge.
- 533 lower-severity findings (305 P1 + 228 P2) from the same audit remain
  open, tracked in `docs/G4A_UKRAINIAN_QA_FINDINGS.md`.
- `CURRENT_STATE.md` / `DECISIONS.md` should record this P0-fix pass once
  it lands — deferred here to avoid conflicting with the still-open
  `claude-code/g4a-ukrainian-qa-audit` PR (#2), which is already editing
  both files.
