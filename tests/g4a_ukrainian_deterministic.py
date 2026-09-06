#!/usr/bin/env python3
"""G4-A deterministic Ukrainian-content gate.

Mechanical, 100%-coverage checks over every learner-facing Ukrainian string in
the app: web/vocabulary.js, web/reading_data.js, web/writing1_data.js, and the
inline UI copy in web/app.js. This is NOT a substitute for the semantic /
idiomatic / grammatical linguistic review — it only catches missing,
untranslated, corrupted, or suspiciously duplicated content. See
docs/G4A_UKRAINIAN_QA_FINDINGS.md for the manual review results.

Run before and after any change to learner-facing Ukrainian content, and as
the first step of every G4-A audit session (catches drift such as main having
moved since the last session, the same way `release_integrity.py` does for
release tags).
"""
from pathlib import Path
import json, re, sys, collections

ROOT = Path(__file__).resolve().parents[1]
HAS_CYRILLIC = re.compile(r'[а-яіїєґА-ЯІЇЄҐ]')
CORRUPTION = re.compile(r'\{\{|undefined|\[object Object\]|\bTODO\b|<script|<div|<span')

errors = []
notes = []


def load_js_object(path, varname):
    src = (ROOT / path).read_text(encoding='utf-8')
    m = re.search(r'window\.' + varname + r'\s*=\s*', src)
    text = src[m.end():].rstrip()
    if text.endswith(';'):
        text = text[:-1]
    return json.loads(text)


def walk_strings(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_strings(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_strings(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield (path, obj)


# --- vocabulary.js ---
vocab = load_js_object('web/vocabulary.js', 'VOCABULARY')
no_ua = [e['id'] for e in vocab if not (e.get('ua') or '').strip()]
ua_no_cyr = [e['id'] for e in vocab if (e.get('ua') or '').strip() and not HAS_CYRILLIC.search(e['ua'])]
ua_eq_word = [e['id'] for e in vocab if (e.get('ua') or '').strip().lower() == (e.get('word') or '').strip().lower()]
def_no_cyr = [e['id'] for e in vocab if (e.get('definitionUa') or '').strip() and not HAS_CYRILLIC.search(e['definitionUa'])]
placeholder = [e['id'] for e in vocab if CORRUPTION.search(e.get('ua', '')) or CORRUPTION.search(e.get('definitionUa', ''))]

ua_counts = collections.Counter((e.get('ua') or '').strip() for e in vocab if (e.get('ua') or '').strip())
dup_ua = {k: v for k, v in ua_counts.items() if v >= 5}
def_counts = collections.Counter((e.get('definitionUa') or '').strip() for e in vocab if (e.get('definitionUa') or '').strip())
dup_def = {k: v for k, v in def_counts.items() if v >= 3}

if no_ua: errors.append(f'vocabulary.js: {len(no_ua)} entries missing ua: {no_ua[:10]}')
if ua_no_cyr: errors.append(f'vocabulary.js: {len(ua_no_cyr)} ua fields contain no Cyrillic: {ua_no_cyr[:10]}')
if ua_eq_word: errors.append(f'vocabulary.js: {len(ua_eq_word)} ua fields equal the English word verbatim: {ua_eq_word[:10]}')
if def_no_cyr: errors.append(f'vocabulary.js: {len(def_no_cyr)} definitionUa fields contain no Cyrillic: {def_no_cyr[:10]}')
if placeholder: errors.append(f'vocabulary.js: {len(placeholder)} entries with placeholder/HTML corruption: {placeholder[:10]}')
if dup_ua: notes.append(f'vocabulary.js: {len(dup_ua)} ua values reused >=5x (review for over-generic translation): {list(dup_ua.items())[:10]}')
if dup_def: notes.append(f'vocabulary.js: {len(dup_def)} definitionUa values reused >=3x (review for copy-paste glosses): {list(dup_def.items())[:10]}')

draft_qa = [e['id'] for e in vocab if str(e.get('translationQa', '')).lower().startswith('draft')]
notes.append(f'vocabulary.js: {len(draft_qa)}/{len(vocab)} entries still carry translationQa="Draft" (no prior per-item sign-off recorded)')

# --- reading_data.js ---
reading = load_js_object('web/reading_data.js', 'READING_DATA')
reading_ua_hits = [(p, s) for p, s in walk_strings(reading) if HAS_CYRILLIC.search(s)]
reading_corrupt = [(p, s) for p, s in walk_strings(reading) if CORRUPTION.search(s)]
if reading_corrupt: errors.append(f'reading_data.js: placeholder/corruption hits: {reading_corrupt[:10]}')
notes.append(f'reading_data.js: {len(reading_ua_hits)} Cyrillic-bearing strings found (expected ~38: 15 family + 23 module uaSupport)')

# --- writing1_data.js ---
writing = load_js_object('web/writing1_data.js', 'WRITING1_DATA')
writing_ua_hits = [(p, s) for p, s in walk_strings(writing) if HAS_CYRILLIC.search(s)]
writing_corrupt = [(p, s) for p, s in walk_strings(writing) if CORRUPTION.search(s)]
if writing_corrupt: errors.append(f'writing1_data.js: placeholder/corruption hits: {writing_corrupt[:10]}')
notes.append(f'writing1_data.js: {len(writing_ua_hits)} Cyrillic-bearing strings found (expected ~268)')

# --- app.js UI copy (spot check for corruption only; not a JSON object) ---
app_src = (ROOT / 'web/app.js').read_text(encoding='utf-8')
app_ua_strings = re.findall(r'[а-яіїєґА-ЯІЇЄҐ][а-яіїєґА-ЯІЇЄҐ \'\-]{5,}', app_src)
app_corrupt = [s for s in app_ua_strings if CORRUPTION.search(s)]
if app_corrupt: errors.append(f'app.js: placeholder/corruption in UA UI copy: {app_corrupt[:10]}')
notes.append(f'app.js: {len(app_ua_strings)} Cyrillic-bearing UI substrings found (expected ~53)')

print('G4-A DETERMINISTIC UKRAINIAN-CONTENT GATE')
print('==========================================')
for n in notes:
    print('NOTE:', n)
if errors:
    for e in errors:
        print('FAIL:', e)
    sys.exit(1)
print('PASS: no missing/untranslated fields, no placeholder/HTML/encoding corruption, '
      'no suspicious duplicate translations across vocabulary.js, reading_data.js, writing1_data.js, app.js')
