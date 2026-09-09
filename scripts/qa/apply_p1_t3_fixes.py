#!/usr/bin/env python3
"""
Apply the G4-A Ukrainian linguistic QA "P1 batch T3" corrections to
web/vocabulary.js.

Background: the G4-A Ukrainian QA audit (docs/G4A_UKRAINIAN_QA_FINDINGS.md,
DECISIONS.md D-026, PR #2) classified 702 defects. The P0 tranche (145
corrections) was applied by scripts/qa/apply_p0_fixes.py; the first P1 batch
(T2, 104 corrections) by scripts/qa/apply_p1_t2_fixes.py. This script applies
the second P1 batch (T3): 102 corrections (sorted by (category, id) —
pedagogical-accuracy 49 / other 30 / russianism-calque 8 / semantic-fidelity 8
/ register 7). All 102 corrections are AI linguistic QA drafts accepted for this
batch; provenance is stamped P1.

Two T3 draft records are intentionally NOT in this batch:
  - SB-0425 (efficiency): a copy-through — its finding is resolved by sibling
    SB-0424 (effectiveness->результативність); efficiency correctly stays
    "ефективність". No field changes, so it is excluded rather than applied.
  - SB-0773 (minute2): a word-field defect (word should read "minute"). Its
    ua/definitionUa are already correct. Renaming the `word` field is blocked
    here because tests/g2_vocabulary_validation.py asserts globally-unique
    casefolded headwords; the fix is deferred and remains an unresolved P1.

This mirrors scripts/qa/apply_p1_t2_fixes.py precisely:

  1. INPUT GUARD. Before mutating anything, the git blob SHA-1 of the on-disk
     web/vocabulary.js must equal _meta.expected_input_blob_sha1. This pins the
     exact base state and makes a second run on an already-patched file fail
     loudly (fail-closed) instead of double-applying.
  2. FIXED REVIEW DATE. translationQa is stamped with _meta.review_date, never
     date.today(), so output is byte-identical on any run date.
  3. ONLY ua/definitionUa/pos/register are mutated (plus the translationQa
     provenance stamp on each changed entry). Nothing else is touched. The
     `word` field is NOT in the allowed-mutation set for this batch.
  4. OUTPUT GUARD. After building the new file content, its git blob SHA-1 must
     equal _meta.expected_output_blob_sha1 before it is written to disk.

Compute-only bootstrap:
    python3 scripts/qa/apply_p1_t3_fixes.py --compute-only
  computes and prints the resulting blob SHA-1 WITHOUT writing, so the value can
  be pinned into _meta.expected_output_blob_sha1. The real guarded run then
  enforces it.

Usage (from a clean checkout, repository root):
    python3 scripts/qa/apply_p1_t3_fixes.py

Run the validation suite afterwards:
    python3 tests/g4a_ukrainian_deterministic.py
    python3 tests/g2_vocabulary_validation.py
    python3 tests/ui_vocabulary_static.py
    python3 scripts/validate_build.py
"""
import hashlib
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VOCAB_PATH = os.path.join(REPO_ROOT, 'web', 'vocabulary.js')
CORR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'p1_t3_corrections.json')


def git_blob_sha1(data: bytes) -> str:
    """Git blob object SHA-1: sha1(b'blob <len>\\0' + data). Matches `git hash-object`."""
    h = hashlib.sha1()
    h.update(b'blob ' + str(len(data)).encode() + b'\0')
    h.update(data)
    return h.hexdigest()


def fail(msg: str):
    print('FAIL:', msg)
    sys.exit(1)


def main():
    compute_only = '--compute-only' in sys.argv[1:]

    with open(CORR_PATH, encoding='utf-8') as f:
        payload = json.load(f)
    meta = payload['_meta']
    corrections = payload['corrections']
    review_date = meta['review_date']
    severity = meta.get('severity', 'P1')
    expected_in = meta['expected_input_blob_sha1']
    expected_out = meta['expected_output_blob_sha1']

    # Read the input file as raw bytes so the hash matches git exactly.
    with open(VOCAB_PATH, 'rb') as f:
        raw = f.read()

    # --- INPUT GUARD (executable assertion) -------------------------------
    actual_in = git_blob_sha1(raw)
    if actual_in != expected_in:
        fail(f'web/vocabulary.js input blob SHA-1 {actual_in} != expected {expected_in}. '
             f'Refusing to mutate: the base file is not the clean state this patch was '
             f'built against (main @ {meta["base_commit"]}), or the patch was already applied.')

    content = raw.decode('utf-8')
    m = re.match(r'window\.VOCABULARY_META=(.*?);\s*\nwindow\.VOCABULARY=(.*);\s*$', content, re.DOTALL)
    if not m:
        fail("web/vocabulary.js did not match the expected "
             "'window.VOCABULARY_META=...;\\nwindow.VOCABULARY=...;' format.")

    meta_raw = m.group(1)
    vocab = json.loads(m.group(2))
    by_id = {e['id']: e for e in vocab}

    missing = [cid for cid in corrections if cid not in by_id]
    if missing:
        fail(f'correction ids not found in vocabulary.js: {missing}')

    p1_ids = set(meta.get('p1_ids', []))

    applied = []
    for cid, fix in corrections.items():
        entry = by_id[cid]
        changed_fields = []
        for field in ('ua', 'definitionUa', 'pos', 'register'):
            if field in fix and fix[field] != entry.get(field):
                entry[field] = fix[field]
                changed_fields.append(field)
        if not changed_fields:
            fail(f'correction {cid} changed no field (already matches current). Aborting.')
        entry_severity = 'P1' if cid in p1_ids else severity
        entry['translationQa'] = f"Reviewed — G4-A {entry_severity} correction applied ({review_date})"
        applied.append((cid, changed_fields))

    # structural sanity checks
    assert len(vocab) == 1784, f"record count changed: {len(vocab)}"
    ids = [e['id'] for e in vocab]
    assert len(ids) == len(set(ids)), "duplicate IDs introduced"
    assert len(applied) == 102, f"expected 102 corrections applied, got {len(applied)}"
    for cid in corrections:
        assert cid in by_id, f"missing {cid}"
    for e in vocab:
        assert e.get('ua'), f"blank ua for {e['id']}"
        assert e.get('definitionUa'), f"blank definitionUa for {e['id']}"

    new_vocab_json = json.dumps(vocab, ensure_ascii=False)
    new_content = f"window.VOCABULARY_META={meta_raw};\nwindow.VOCABULARY={new_vocab_json};\n"
    new_bytes = new_content.encode('utf-8')
    actual_out = git_blob_sha1(new_bytes)

    if compute_only:
        print(f'[compute-only] would apply {len(applied)} corrections; NOTHING written.')
        print(f'  input  blob SHA-1: {actual_in}')
        print(f'  output blob SHA-1: {actual_out}')
        return

    # --- OUTPUT GUARD (executable assertion) ------------------------------
    if not expected_out or expected_out == 'TBD':
        fail('_meta.expected_output_blob_sha1 is unset/TBD. Run with --compute-only '
             'to obtain the value, pin it into the payload, then re-run.')
    if actual_out != expected_out:
        fail(f'computed output blob SHA-1 {actual_out} != expected {expected_out}. '
             f'Refusing to write: the corrections would not reproduce the pinned, '
             f'reviewed result. Nothing was changed on disk.')

    with open(VOCAB_PATH, 'wb') as f:
        f.write(new_bytes)

    print(f'Applied {len(applied)} corrections to {VOCAB_PATH}.')
    print(f'  review_date (fixed): {review_date}')
    print(f'  input  blob SHA-1: {actual_in}')
    print(f'  output blob SHA-1: {actual_out}')
    print('  sample:', applied[:5])


if __name__ == '__main__':
    main()
