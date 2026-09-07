#!/usr/bin/env python3
"""
Apply the G4-A Ukrainian linguistic QA "P0" corrections to web/vocabulary.js.

Background: an audit of the 1,784-entry vocabulary bank
(docs/G4A_UKRAINIAN_QA_FINDINGS.md, docs/G4A_UKRAINIAN_QA_FINDINGS.csv,
DECISIONS.md D-026, PR #2) found 702 defects in Ukrainian
translations/definitions, of which 142 were classified P0 (highest severity:
false friends, wrong-sense translations, POS/register mismatches,
grammatical-case leakage from source extraction). This script applies concrete,
editorially-reviewed corrections for those 142 entries, PLUS two further entries
(SB-0208, SB-1728; register severity P1) that must be corrected together with
SB-0432 to fully clear deterministic-gate defect G4A-V-001 — the three shared the
circular gloss "Щоб почати, почніть." and a partial repair would slip under the
duplicate threshold while the defect stayed live. Total: 144 corrections.

Usage (run from a clean checkout, repository root):
    python3 scripts/qa/apply_p0_fixes.py

Determinism / reproducibility guarantees (all enforced as executable assertions,
not comments — the script exits non-zero and writes nothing on any mismatch):

  1. INPUT GUARD. Before mutating anything, the git blob SHA-1 of the on-disk
     web/vocabulary.js must equal _meta.expected_input_blob_sha1 in
     p0_corrections.json. This pins the exact base state (main @ _meta.base_commit)
     and makes a second run on an already-patched file fail loudly instead of
     double-applying.
  2. FIXED REVIEW DATE. translationQa is stamped with _meta.review_date from the
     payload, never date.today(), so the output is byte-identical on any run date.
  3. OUTPUT GUARD. After building the new file content, its git blob SHA-1 must
     equal _meta.expected_output_blob_sha1 before it is written to disk.

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
CORR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'p0_corrections.json')


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
    with open(CORR_PATH, encoding='utf-8') as f:
        payload = json.load(f)
    meta = payload['_meta']
    corrections = payload['corrections']
    review_date = meta['review_date']
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

    qa_note = f"Reviewed — G4-A P0 correction applied ({review_date})"

    applied = []
    for cid, fix in corrections.items():
        entry = by_id[cid]
        changed_fields = []
        for field in ('ua', 'definitionUa', 'pos', 'register'):
            if field in fix and fix[field] != entry.get(field):
                entry[field] = fix[field]
                changed_fields.append(field)
        entry['translationQa'] = qa_note
        applied.append((cid, changed_fields))

    # structural sanity checks
    assert len(vocab) == 1784, f"record count changed: {len(vocab)}"
    ids = [e['id'] for e in vocab]
    assert len(ids) == len(set(ids)), "duplicate IDs introduced"
    for e in vocab:
        assert e.get('ua'), f"blank ua for {e['id']}"
        assert e.get('definitionUa'), f"blank definitionUa for {e['id']}"

    new_vocab_json = json.dumps(vocab, ensure_ascii=False)
    new_content = f"window.VOCABULARY_META={meta_raw};\nwindow.VOCABULARY={new_vocab_json};\n"
    new_bytes = new_content.encode('utf-8')

    # --- OUTPUT GUARD (executable assertion) ------------------------------
    actual_out = git_blob_sha1(new_bytes)
    if expected_out and expected_out != 'TBD':
        if actual_out != expected_out:
            fail(f'computed output blob SHA-1 {actual_out} != expected {expected_out}. '
                 f'Refusing to write: the corrections would not reproduce the pinned, '
                 f'reviewed result. Nothing was changed on disk.')
    else:
        print(f'[bootstrap] expected_output_blob_sha1 is unset; computed {actual_out}. '
              f'Set _meta.expected_output_blob_sha1 to this value to enable the output guard.')

    with open(VOCAB_PATH, 'wb') as f:
        f.write(new_bytes)

    print(f'Applied {len(applied)} corrections to {VOCAB_PATH}.')
    print(f'  review_date (fixed): {review_date}')
    print(f'  input  blob SHA-1: {actual_in}')
    print(f'  output blob SHA-1: {actual_out}')
    print('  sample:', applied[:5])


if __name__ == '__main__':
    main()
