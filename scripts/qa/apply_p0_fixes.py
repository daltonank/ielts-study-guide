#!/usr/bin/env python3
"""
Apply the G4-A Ukrainian linguistic QA "P0" corrections to web/vocabulary.js.

Background: an audit of the 1,784-entry vocabulary bank
(docs/G4A_UKRAINIAN_QA_FINDINGS.md, DECISIONS.md D-026) found 675 defects
in Ukrainian translations/definitions, of which 142 were classified P0
(highest severity: false friends, wrong-sense translations, POS/register
mismatches, grammatical-case leakage from source extraction). This script
applies concrete, editorially-reviewed corrections for those 142 entries.

Usage (run from the repository root):
    python3 scripts/qa/apply_p0_fixes.py

It rewrites web/vocabulary.js in place. Run the project's validation
suite afterwards:
    python3 tests/g4a_ukrainian_deterministic.py
    python3 tests/g2_vocabulary_validation.py
    python3 tests/ui_vocabulary_static.py
    python3 scripts/validate_build.py

Expected result (already verified locally against this exact input):
  - record count stays at 1784, no duplicate IDs, no blank ua/definitionUa
  - resulting web/vocabulary.js has git blob sha
    e054ad8d2164b94fd78df8e77caf9f22ac29b04d
    when applied on top of commit 52d12ddd2c52f9d822a5677b98ee30649ccd61a6
    (main, as of 2026-09-06)
"""
import json
import os
import re
import sys
from datetime import date

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VOCAB_PATH = os.path.join(REPO_ROOT, 'web', 'vocabulary.js')
CORR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'p0_corrections.json')


def main():
    with open(VOCAB_PATH, encoding='utf-8') as f:
        content = f.read()

    m = re.match(r'window\.VOCABULARY_META=(.*?);\s*\nwindow\.VOCABULARY=(.*);\s*$', content, re.DOTALL)
    if not m:
        print("PARSE FAILED: web/vocabulary.js did not match the expected "
              "'window.VOCABULARY_META=...;\\nwindow.VOCABULARY=...;' format.")
        sys.exit(1)

    meta_raw = m.group(1)
    vocab = json.loads(m.group(2))

    with open(CORR_PATH, encoding='utf-8') as f:
        corrections = json.load(f)

    by_id = {e['id']: e for e in vocab}

    missing = [cid for cid in corrections if cid not in by_id]
    if missing:
        print("MISSING IDS (vocabulary.js does not match expected base state):", missing)
        sys.exit(1)

    today = date.today().isoformat()
    qa_note = f"Reviewed — G4-A P0 correction applied ({today})"

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

    # sanity checks
    assert len(vocab) == 1784, f"record count changed: {len(vocab)}"
    ids = [e['id'] for e in vocab]
    assert len(ids) == len(set(ids)), "duplicate IDs introduced"
    for e in vocab:
        assert e.get('ua'), f"blank ua for {e['id']}"
        assert e.get('definitionUa'), f"blank definitionUa for {e['id']}"

    new_vocab_json = json.dumps(vocab, ensure_ascii=False)
    new_content = f"window.VOCABULARY_META={meta_raw};\nwindow.VOCABULARY={new_vocab_json};\n"

    with open(VOCAB_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Applied {len(applied)} corrections to {VOCAB_PATH}.")
    print("Sample:", applied[:5])


if __name__ == '__main__':
    main()
