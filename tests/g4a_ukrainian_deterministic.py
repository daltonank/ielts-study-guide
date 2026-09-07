#!/usr/bin/env python3
"""G4-A deterministic Ukrainian-content gate.

Mechanical, 100%-coverage checks over every learner-facing Ukrainian string in
the app: web/vocabulary.js, web/reading_data.js, web/writing1_data.js, and the
inline UI copy in web/app.js.

WHAT THIS GATE PROVES
    Only that the Ukrainian content is *structurally* well-formed and that no
    inventory has silently shrunk: fields are present, contain Cyrillic, are not
    the English headword copied verbatim, carry no placeholder/markup/encoding
    corruption, and do not reuse one gloss across more entries than policy
    allows.

WHAT THIS GATE DOES NOT PROVE
    Anything about meaning. It cannot tell a correct translation from a
    confident wrong one: a false friend, a wrong-sense definition, a
    part-of-speech mismatch and a grammatical-case error are all well-formed
    Ukrainian and all pass every assertion below. This is NOT semantic review,
    NOT native-speaker review, and passing it is NOT evidence of translation
    quality. See docs/G4A_UKRAINIAN_QA_FINDINGS.md for the linguistic review,
    which is an AI pass and is separately labelled as such.

Run before and after any change to learner-facing Ukrainian content, and as the
first step of every G4-A session — it catches drift such as main having moved
since the last session, the way release_integrity.py does for release tags.

Exit code 0 only if every assertion below holds. Counts and collision policy are
enforced, not reported: a drifted inventory or a new collision fails the run.
"""
from pathlib import Path
import csv, json, re, sys, collections

ROOT = Path(__file__).resolve().parents[1]
HAS_CYRILLIC = re.compile(r'[а-яіїєґА-ЯІЇЄҐ]')
CORRUPTION = re.compile(r'\{\{|undefined|\[object Object\]|\bTODO\b|<script|<div|<span')
APP_UA_STRING = re.compile(r"[а-яіїєґА-ЯІЇЄҐ][а-яіїєґА-ЯІЇЄҐ '\-]{5,}")

# --- Enforced inventory. A drop means content was lost; a rise means new content
# --- entered without going through a G4-A review. Either way, look before editing.
EXPECTED = {
    'vocabulary_entries': 1784,   # locked by D-014 standing constraint (G2: 1,784 records)
    'reading_ua_strings': 38,     # 15 family + 23 module uaSupport
    'writing1_ua_strings': 268,
    'app_ua_strings': 53,
}

# --- The per-entry findings register. These are the numbers every G4-A document
# --- states; asserting them here is what stops a document and the data drifting
# --- apart, which is the defect that produced the Phase 1 remediation.
FINDINGS_CSV = 'docs/G4A_UKRAINIAN_QA_FINDINGS.csv'
EXPECTED_FINDINGS = {
    'rows': 702,
    'severity': {'P0': 142, 'P1': 314, 'P2': 246},
    'source': {'main-pass': 675, 'spot-check': 27},
}

# --- Collision policy (see docs/G4A_UKRAINIAN_QA_AUDIT_PLAN.md §3, Phase 0).
# A gloss shared by three or more distinct headwords is not a definition of any
# of them, so it fails. A `ua` value shared by five or more entries indicates a
# generic filler translation, so it fails. Below those thresholds, collisions are
# ratcheted: the number of colliding groups may fall but never rise, so a
# correction pass cannot quietly introduce new duplicates while fixing old ones,
# and cannot escape the hard thresholds by splitting one group into two pairs.
MAX_ENTRIES_SHARING_DEFINITION = 2
MAX_ENTRIES_SHARING_UA = 4
BASELINE_COLLIDING_GROUPS = {'definitionUa': 9, 'ua': 109}

# --- Named open defects from the G4-A register that a threshold alone cannot hold.
# Thresholds are gameable by partial repair: fixing one member of a three-way
# collision drops it to a pair and slips under MAX_ENTRIES_SHARING_DEFINITION while
# the defect is still live. Each group below must be fully resolved — no two of its
# members may share a definitionUa — before this gate goes green. Remove a group only
# when it is actually fixed, never to make the run pass.
#
# G4A-V-001: SB-0208 (commence), SB-0432 (embark), SB-1728 (commenced) all carry the
# circular gloss "Щоб почати, почніть." ("To begin, begin."). As of the P0 correction
# payload on claude-code/g4a-vocab-p0-fixes, only SB-0432 is corrected; SB-0208 and
# SB-1728 are absent from it and would still share the gloss.
NO_SHARED_DEFINITION_GROUPS = {
    'G4A-V-001': ['SB-0208', 'SB-0432', 'SB-1728'],
}

errors = []
report = []


def load_js_object(path, varname):
    src = (ROOT / path).read_text(encoding='utf-8')
    m = re.search(r'window\.' + varname + r'\s*=\s*', src)
    if not m:
        raise SystemExit(f'FAIL: {path}: could not find window.{varname}')
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


def check_count(label, actual, expected):
    report.append(f'{label}: {actual} (expected {expected})')
    if actual != expected:
        errors.append(
            f'{label}: expected {expected}, found {actual}. Content was added or lost '
            f'without a corresponding G4-A review; update EXPECTED deliberately if intended.'
        )


def check_collisions(field, counts):
    limit = MAX_ENTRIES_SHARING_DEFINITION if field == 'definitionUa' else MAX_ENTRIES_SHARING_UA
    over = {k: n for k, n in counts.items() if n > limit}
    if over:
        for value, n in sorted(over.items(), key=lambda kv: -kv[1])[:5]:
            errors.append(
                f'vocabulary.js: {field} shared by {n} entries (policy allows at most '
                f'{limit}): {value[:70]!r}'
            )
    groups = sum(1 for n in counts.values() if n >= 2)
    baseline = BASELINE_COLLIDING_GROUPS[field]
    report.append(f'{field} colliding groups (>=2 entries): {groups} (ratchet baseline {baseline})')
    if groups > baseline:
        errors.append(
            f'vocabulary.js: {field} now has {groups} colliding groups, above the ratchet '
            f'baseline of {baseline}. A correction pass introduced new duplicate values.'
        )


# --- vocabulary.js -----------------------------------------------------------
vocab = load_js_object('web/vocabulary.js', 'VOCABULARY')
check_count('vocabulary.js entries', len(vocab), EXPECTED['vocabulary_entries'])

no_ua = [e['id'] for e in vocab if not (e.get('ua') or '').strip()]
ua_no_cyr = [e['id'] for e in vocab if (e.get('ua') or '').strip() and not HAS_CYRILLIC.search(e['ua'])]
ua_eq_word = [e['id'] for e in vocab if (e.get('ua') or '').strip().lower() == (e.get('word') or '').strip().lower()]
no_def = [e['id'] for e in vocab if not (e.get('definitionUa') or '').strip()]
def_no_cyr = [e['id'] for e in vocab if (e.get('definitionUa') or '').strip() and not HAS_CYRILLIC.search(e['definitionUa'])]
placeholder = [e['id'] for e in vocab if CORRUPTION.search(e.get('ua', '')) or CORRUPTION.search(e.get('definitionUa', ''))]

if no_ua: errors.append(f'vocabulary.js: {len(no_ua)} entries missing ua: {no_ua[:10]}')
if ua_no_cyr: errors.append(f'vocabulary.js: {len(ua_no_cyr)} ua fields contain no Cyrillic: {ua_no_cyr[:10]}')
if ua_eq_word: errors.append(f'vocabulary.js: {len(ua_eq_word)} ua fields equal the English word verbatim: {ua_eq_word[:10]}')
if no_def: errors.append(f'vocabulary.js: {len(no_def)} entries missing definitionUa: {no_def[:10]}')
if def_no_cyr: errors.append(f'vocabulary.js: {len(def_no_cyr)} definitionUa fields contain no Cyrillic: {def_no_cyr[:10]}')
if placeholder: errors.append(f'vocabulary.js: {len(placeholder)} entries with placeholder/HTML corruption: {placeholder[:10]}')

check_collisions('ua', collections.Counter(
    (e.get('ua') or '').strip() for e in vocab if (e.get('ua') or '').strip()))
check_collisions('definitionUa', collections.Counter(
    (e.get('definitionUa') or '').strip() for e in vocab if (e.get('definitionUa') or '').strip()))

by_id = {e['id']: e for e in vocab}
for group_id, ids in NO_SHARED_DEFINITION_GROUPS.items():
    missing = [i for i in ids if i not in by_id]
    if missing:
        errors.append(f'{group_id}: entry ids not found in vocabulary.js: {missing}')
        continue
    seen = collections.defaultdict(list)
    for i in ids:
        seen[(by_id[i].get('definitionUa') or '').strip()].append(i)
    still_shared = {d: members for d, members in seen.items() if len(members) > 1}
    report.append(f'{group_id}: {len(still_shared)} unresolved shared gloss(es) among {len(ids)} entries')
    for definition, members in still_shared.items():
        errors.append(
            f'{group_id}: {members} still share definitionUa {definition[:60]!r} — the named '
            f'defect is not fully resolved (partial repair does not clear this assertion).'
        )

draft_qa = [e['id'] for e in vocab if str(e.get('translationQa', '')).lower().startswith('draft')]
report.append(f'entries still carrying translationQa="Draft": {len(draft_qa)}/{len(vocab)}')

# --- reading_data.js ---------------------------------------------------------
reading = load_js_object('web/reading_data.js', 'READING_DATA')
reading_ua = [(p, s) for p, s in walk_strings(reading) if HAS_CYRILLIC.search(s)]
reading_corrupt = [(p, s) for p, s in walk_strings(reading) if CORRUPTION.search(s)]
if reading_corrupt: errors.append(f'reading_data.js: placeholder/corruption hits: {reading_corrupt[:10]}')
check_count('reading_data.js UA strings', len(reading_ua), EXPECTED['reading_ua_strings'])

# --- writing1_data.js --------------------------------------------------------
writing = load_js_object('web/writing1_data.js', 'WRITING1_DATA')
writing_ua = [(p, s) for p, s in walk_strings(writing) if HAS_CYRILLIC.search(s)]
writing_corrupt = [(p, s) for p, s in walk_strings(writing) if CORRUPTION.search(s)]
if writing_corrupt: errors.append(f'writing1_data.js: placeholder/corruption hits: {writing_corrupt[:10]}')
check_count('writing1_data.js UA strings', len(writing_ua), EXPECTED['writing1_ua_strings'])

# --- app.js UI copy ----------------------------------------------------------
app_src = (ROOT / 'web/app.js').read_text(encoding='utf-8')
app_ua = APP_UA_STRING.findall(app_src)
app_corrupt = [s for s in app_ua if CORRUPTION.search(s)]
if app_corrupt: errors.append(f'app.js: placeholder/corruption in UA UI copy: {app_corrupt[:10]}')
check_count('app.js UA UI substrings', len(app_ua), EXPECTED['app_ua_strings'])

# --- findings register -------------------------------------------------------
# Landed 2026-09-06. Before this, the register existed only outside the repository
# and its counts could not be checked from a clone.
csv_path = ROOT / FINDINGS_CSV
if not csv_path.exists():
    errors.append(
        f'{FINDINGS_CSV}: missing. The per-entry findings register is what makes the '
        f'G4-A audit reproducible from the repository alone; without it the counts in '
        f'CURRENT_STATE.md, D-026 and the register narrative cannot be verified.'
    )
else:
    with csv_path.open(encoding='utf-8-sig', newline='') as fh:
        findings = list(csv.DictReader(fh))
    check_count('findings register rows', len(findings), EXPECTED_FINDINGS['rows'])

    ids = [r['id'] for r in findings]
    if len(set(ids)) != len(ids):
        dupes = [i for i, n in collections.Counter(ids).items() if n > 1]
        errors.append(
            f'{FINDINGS_CSV}: {len(ids) - len(set(ids))} duplicate entry ids '
            f'({dupes[:5]}). The count reconciliation assumes one finding per entry.'
        )
    unknown = sorted(set(ids) - {e['id'] for e in vocab})
    if unknown:
        errors.append(
            f'{FINDINGS_CSV}: {len(unknown)} finding ids do not resolve in '
            f'vocabulary.js: {unknown[:10]}'
        )

    for field, expected in (('severity', EXPECTED_FINDINGS['severity']),
                            ('source', EXPECTED_FINDINGS['source'])):
        actual = dict(collections.Counter(r[field] for r in findings))
        report.append(f'findings register {field}: {actual}')
        if actual != expected:
            errors.append(
                f'{FINDINGS_CSV}: {field} counts are {actual}, expected {expected}. '
                f'Either the register changed or a document is now quoting stale numbers.'
            )

    # The spot-check sampled only entries the first pass judged clean. If the two
    # sets ever overlap, the disjointness the totals rest on is false and the
    # 702-distinct-entry figure is wrong.
    main_ids = {r['id'] for r in findings if r['source'] == 'main-pass'}
    spot_ids = {r['id'] for r in findings if r['source'] == 'spot-check'}
    overlap = sorted(main_ids & spot_ids)
    report.append(f'findings register: main-pass {len(main_ids)}, spot-check '
                  f'{len(spot_ids)}, overlap {len(overlap)}')
    if overlap:
        errors.append(
            f'{FINDINGS_CSV}: {len(overlap)} entries appear in both the main pass and '
            f'the spot-check ({overlap[:5]}). The two sets are documented as disjoint '
            f'by construction, and the 702 distinct-entry total depends on it.'
        )

    missing_fix = [r['id'] for r in findings
                   if r['source'] == 'main-pass' and not r['proposed_correction'].strip()]
    if missing_fix:
        errors.append(
            f'{FINDINGS_CSV}: {len(missing_fix)} first-pass findings carry no proposed '
            f'correction: {missing_fix[:10]}'
        )
    open_spot = sum(1 for r in findings
                    if r['source'] == 'spot-check' and not r['proposed_correction'].strip())
    report.append(f'spot-check findings still without a proposed correction: {open_spot}/27')

# --- result ------------------------------------------------------------------
print('G4-A DETERMINISTIC UKRAINIAN-CONTENT GATE')
print('=========================================')
for line in report:
    print('  ', line)
print()
if errors:
    for e in errors:
        print('FAIL:', e)
    print()
    print(f'FAIL: {len(errors)} structural assertion(s) failed.')
    sys.exit(1)
print('PASS: across vocabulary.js, reading_data.js, writing1_data.js and app.js —')
print('  - every expected UA inventory count matches exactly;')
print('  - no missing, non-Cyrillic, or copied-from-English ua/definitionUa fields;')
print('  - no placeholder, markup or encoding corruption;')
print('  - no gloss or translation shared beyond the collision policy, and no new')
print('    colliding groups above the recorded baseline;')
print('  - the per-entry findings register reconciles: row count, severity and source')
print('    splits, one finding per entry, every id resolving in vocabulary.js, and the')
print('    main-pass and spot-check sets disjoint.')
print('This is a STRUCTURAL result only. It says nothing about whether any translation')
print('is correct, idiomatic, or the right sense — see docs/G4A_UKRAINIAN_QA_FINDINGS.md.')
