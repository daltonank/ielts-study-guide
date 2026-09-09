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
    'app_ua_strings': 61,     # 53 baseline + 8 from the T5-A learner flag/correction loop UI copy (D-027)
}

# --- The per-entry findings register. These are the numbers every G4-A document
# --- states; asserting them here is what stops a document and the data drifting
# --- apart, which is the defect that produced the Phase 1 remediation.
FINDINGS_CSV = 'docs/G4A_UKRAINIAN_QA_FINDINGS.csv'
EXPECTED_FINDINGS = {
    'rows': 702,
    'severity': {'P0': 142, 'P1': 314, 'P2': 246},
    'source': {'main-pass': 675, 'spot-check': 27},
    # Published per-category counts. Two breakdowns, both stated in the register:
    # 'category' is across both passes (n=702, FINDINGS.md §1a), parallel to the
    # severity/source totals above; 'category_main_pass' is the first pass only
    # (n=675, FINDINGS.md §1a and §6). Both are read from the CSV, not guessed.
    'category': {
        'semantic-fidelity': 216, 'grammar': 145, 'pedagogical-accuracy': 133,
        'other': 100, 'circular-definition': 67, 'russianism-calque': 26,
        'register': 15,
    },
    'category_main_pass': {
        'semantic-fidelity': 212, 'grammar': 144, 'pedagogical-accuracy': 121,
        'other': 98, 'circular-definition': 61, 'russianism-calque': 24,
        'register': 15,
    },
}

# --- Collision policy (see docs/G4A_UKRAINIAN_QA_AUDIT_PLAN.md §3, Phase 0).
# A gloss shared by three or more distinct headwords is not a definition of any
# of them, so it fails. A `ua` value shared by five or more entries indicates a
# generic filler translation, so it fails. Below those thresholds, collisions are
# ratcheted by *identity*, not by count: the baseline records the exact set of
# entry ids that share each colliding value. A post-change group is allowed only
# when it is a subset of some baseline group — i.e. a known collision that has been
# partly or fully repaired. Any group containing a pair of ids that did not already
# collide in the baseline fails, even when the total number of colliding groups is
# unchanged. This is what a plain count baseline could not do: it let a correction
# pass remove one duplicate pair and introduce a different one in the same change
# and stay green because the count matched.
MAX_ENTRIES_SHARING_DEFINITION = 2
MAX_ENTRIES_SHARING_UA = 4
BASELINE_COLLISION_GROUPS = {
    'definitionUa': frozenset({
        frozenset({'SB-0175', 'SB-1726'}),
        frozenset({'SB-0208', 'SB-0432', 'SB-1728'}),
        frozenset({'SB-0224', 'SB-1767'}),
        frozenset({'SB-0262', 'SB-1435'}),
        frozenset({'SB-0460', 'SB-1552'}),
        frozenset({'SB-0665', 'SB-1775'}),
        frozenset({'SB-0845', 'SB-1522'}),
        frozenset({'SB-0886', 'SB-1706'}),
        frozenset({'SB-1012', 'SB-1753'}),
    }),
    'ua': frozenset({
        frozenset({'SB-0013', 'SB-0227', 'SB-1683'}),
        frozenset({'SB-0014', 'SB-1010'}),
        frozenset({'SB-0019', 'SB-0613'}),
        frozenset({'SB-0028', 'SB-0229'}),
        frozenset({'SB-0038', 'SB-0098', 'SB-1090'}),
        frozenset({'SB-0051', 'SB-0092'}),
        frozenset({'SB-0052', 'SB-0091'}),
        frozenset({'SB-0053', 'SB-0997', 'SB-1162'}),
        frozenset({'SB-0057', 'SB-1631'}),
        frozenset({'SB-0064', 'SB-0764'}),
        frozenset({'SB-0074', 'SB-0899'}),
        frozenset({'SB-0086', 'SB-1133'}),
        frozenset({'SB-0094', 'SB-0974'}),
        frozenset({'SB-0096', 'SB-1373'}),
        frozenset({'SB-0110', 'SB-0875'}),
        frozenset({'SB-0111', 'SB-0798'}),
        frozenset({'SB-0124', 'SB-0682'}),
        frozenset({'SB-0144', 'SB-0394', 'SB-1281'}),
        frozenset({'SB-0170', 'SB-0379'}),
        frozenset({'SB-0175', 'SB-1189'}),
        frozenset({'SB-0188', 'SB-1490'}),
        frozenset({'SB-0190', 'SB-0204'}),
        frozenset({'SB-0201', 'SB-0278'}),
        frozenset({'SB-0230', 'SB-1288'}),
        frozenset({'SB-0238', 'SB-0276', 'SB-0344'}),
        frozenset({'SB-0252', 'SB-1148'}),
        frozenset({'SB-0262', 'SB-1435', 'SB-1753'}),
        frozenset({'SB-0269', 'SB-0392', 'SB-1732'}),
        frozenset({'SB-0275', 'SB-1226'}),
        frozenset({'SB-0292', 'SB-1009', 'SB-1376'}),
        frozenset({'SB-0296', 'SB-0298'}),
        frozenset({'SB-0305', 'SB-0309'}),
        frozenset({'SB-0308', 'SB-1027'}),
        frozenset({'SB-0336', 'SB-0511'}),
        frozenset({'SB-0343', 'SB-0815'}),
        frozenset({'SB-0348', 'SB-0883'}),
        frozenset({'SB-0383', 'SB-1253'}),
        frozenset({'SB-0388', 'SB-0704'}),
        frozenset({'SB-0393', 'SB-1280'}),
        frozenset({'SB-0424', 'SB-0425'}),
        frozenset({'SB-0448', 'SB-1213'}),
        frozenset({'SB-0450', 'SB-0480'}),
        frozenset({'SB-0457', 'SB-1267'}),
        frozenset({'SB-0470', 'SB-0665'}),
        frozenset({'SB-0474', 'SB-0477'}),
        frozenset({'SB-0475', 'SB-1167'}),
        frozenset({'SB-0478', 'SB-1089'}),
        frozenset({'SB-0483', 'SB-1519'}),
        frozenset({'SB-0493', 'SB-1528'}),
        frozenset({'SB-0496', 'SB-1263'}),
        frozenset({'SB-0507', 'SB-1295'}),
        frozenset({'SB-0517', 'SB-1206'}),
        frozenset({'SB-0525', 'SB-1254'}),
        frozenset({'SB-0531', 'SB-0532'}),
        frozenset({'SB-0539', 'SB-0543'}),
        frozenset({'SB-0549', 'SB-1084'}),
        frozenset({'SB-0569', 'SB-0933'}),
        frozenset({'SB-0570', 'SB-1645'}),
        frozenset({'SB-0575', 'SB-0932', 'SB-1574'}),
        frozenset({'SB-0599', 'SB-1561'}),
        frozenset({'SB-0600', 'SB-1233', 'SB-1772'}),
        frozenset({'SB-0630', 'SB-1656'}),
        frozenset({'SB-0656', 'SB-1762'}),
        frozenset({'SB-0666', 'SB-1406'}),
        frozenset({'SB-0706', 'SB-1562'}),
        frozenset({'SB-0719', 'SB-0720'}),
        frozenset({'SB-0740', 'SB-0793'}),
        frozenset({'SB-0758', 'SB-1572'}),
        frozenset({'SB-0797', 'SB-1065'}),
        frozenset({'SB-0819', 'SB-1708'}),
        frozenset({'SB-0822', 'SB-0931'}),
        frozenset({'SB-0860', 'SB-1279'}),
        frozenset({'SB-0863', 'SB-1578'}),
        frozenset({'SB-0879', 'SB-1425'}),
        frozenset({'SB-0895', 'SB-1410', 'SB-1525', 'SB-1623'}),
        frozenset({'SB-0946', 'SB-1113'}),
        frozenset({'SB-0975', 'SB-0983'}),
        frozenset({'SB-0976', 'SB-0993', 'SB-1710'}),
        frozenset({'SB-0978', 'SB-1659'}),
        frozenset({'SB-0987', 'SB-1006'}),
        frozenset({'SB-0996', 'SB-1144'}),
        frozenset({'SB-1013', 'SB-1537'}),
        frozenset({'SB-1043', 'SB-1482'}),
        frozenset({'SB-1063', 'SB-1083'}),
        frozenset({'SB-1121', 'SB-1648'}),
        frozenset({'SB-1123', 'SB-1608'}),
        frozenset({'SB-1155', 'SB-1191'}),
        frozenset({'SB-1156', 'SB-1164'}),
        frozenset({'SB-1173', 'SB-1256'}),
        frozenset({'SB-1188', 'SB-1647'}),
        frozenset({'SB-1228', 'SB-1428'}),
        frozenset({'SB-1231', 'SB-1399'}),
        frozenset({'SB-1259', 'SB-1301'}),
        frozenset({'SB-1343', 'SB-1576'}),
        frozenset({'SB-1364', 'SB-1380'}),
        frozenset({'SB-1385', 'SB-1654'}),
        frozenset({'SB-1387', 'SB-1509'}),
        frozenset({'SB-1419', 'SB-1731'}),
        frozenset({'SB-1486', 'SB-1516'}),
        frozenset({'SB-1511', 'SB-1774'}),
        frozenset({'SB-1517', 'SB-1526'}),
        frozenset({'SB-1527', 'SB-1549'}),
        frozenset({'SB-1544', 'SB-1704'}),
        frozenset({'SB-1570', 'SB-1707'}),
        frozenset({'SB-1571', 'SB-1586'}),
        frozenset({'SB-1599', 'SB-1709'}),
        frozenset({'SB-1626', 'SB-1688'}),
        frozenset({'SB-1671', 'SB-1715'}),
        frozenset({'SB-1672', 'SB-1692'}),
    }),
}

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


def new_collision_groups(current_groups, baseline_groups):
    """Groups present after a change whose collision was not already in the baseline.

    A current group is exempt only if it is a subset of some baseline group — that is,
    every pair of ids in it was already colliding, so it can only be a shrunk remnant
    of a known collision (a partial or in-progress repair), never a newly-introduced
    duplicate. Anything else — a brand-new pair, or a new id joining an existing
    value — is flagged, regardless of the total group count.
    """
    return [g for g in current_groups
            if not any(g <= b for b in baseline_groups)]


def check_collisions(field, value_to_ids):
    limit = MAX_ENTRIES_SHARING_DEFINITION if field == 'definitionUa' else MAX_ENTRIES_SHARING_UA
    over = {v: ids for v, ids in value_to_ids.items() if len(ids) > limit}
    if over:
        for value, ids in sorted(over.items(), key=lambda kv: -len(kv[1]))[:5]:
            errors.append(
                f'vocabulary.js: {field} shared by {len(ids)} entries (policy allows at most '
                f'{limit}): {value[:70]!r}'
            )
    current_groups = {frozenset(ids) for ids in value_to_ids.values() if len(ids) >= 2}
    baseline = BASELINE_COLLISION_GROUPS[field]
    introduced = new_collision_groups(current_groups, baseline)
    report.append(
        f'{field} colliding groups (>=2 entries): {len(current_groups)} '
        f'(ratchet baseline {len(baseline)} identities); new groups vs baseline: {len(introduced)}'
    )
    for g in sorted(introduced, key=lambda s: sorted(s))[:5]:
        errors.append(
            f'vocabulary.js: {field} has a new colliding group {sorted(g)} whose collision was '
            f'not present in the ratchet baseline. A correction pass introduced a duplicate value '
            f'shared by entries that did not previously collide (fails even at equal group count).'
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

def value_to_ids(field):
    m = collections.defaultdict(list)
    for e in vocab:
        v = (e.get(field) or '').strip()
        if v:
            m[v].append(e['id'])
    return m


def _selfcheck_ratchet():
    """Prove the identity ratchet is non-vacuous before trusting it on real data.

    A plain count baseline passes an equal-count swap; the identity comparison must
    not. Assert that a synthetic swap (one baseline pair removed, a brand-new pair
    added, group count unchanged) is flagged, and that a legitimate shrink of a
    baseline group is not.
    """
    baseline = {frozenset({'A', 'B', 'C'}), frozenset({'D', 'E'})}
    swapped = {frozenset({'A', 'B', 'C'}), frozenset({'F', 'G'})}  # same count, new pair F/G
    assert len(swapped) == len(baseline), 'self-check setup: group counts must match'
    assert new_collision_groups(swapped, baseline) == [frozenset({'F', 'G'})], \
        'ratchet self-check: a new equal-count collision pair was not flagged'
    shrunk = {frozenset({'A', 'B'}), frozenset({'D', 'E'})}  # {A,B} ⊂ {A,B,C}
    assert new_collision_groups(shrunk, baseline) == [], \
        'ratchet self-check: a legitimate group shrink was wrongly flagged'
    report.append('ratchet self-check: identity comparison flags a new equal-count '
                  'collision pair and ignores a legitimate group shrink (non-vacuous)')


_selfcheck_ratchet()
check_collisions('ua', value_to_ids('ua'))
check_collisions('definitionUa', value_to_ids('definitionUa'))

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
                            ('source', EXPECTED_FINDINGS['source']),
                            ('category', EXPECTED_FINDINGS['category'])):
        actual = dict(collections.Counter(r[field] for r in findings))
        report.append(f'findings register {field}: {actual}')
        if actual != expected:
            errors.append(
                f'{FINDINGS_CSV}: {field} counts are {actual}, expected {expected}. '
                f'Either the register changed or a document is now quoting stale numbers.'
            )

    # Every first-pass finding must carry a category, and the first-pass category
    # breakdown must match the register's published attribution (FINDINGS.md §1a, §6).
    main_pass = [r for r in findings if r['source'] == 'main-pass']
    blank_category = [r['id'] for r in main_pass if not (r.get('category') or '').strip()]
    if blank_category:
        errors.append(
            f'{FINDINGS_CSV}: {len(blank_category)} first-pass findings have a blank '
            f'category: {blank_category[:10]}. Every first-pass finding is categorised in '
            f'the published attribution, so a blank category means the register drifted.'
        )
    main_category = dict(collections.Counter(r['category'] for r in main_pass))
    report.append(f'findings register category (main-pass): {main_category}')
    if main_category != EXPECTED_FINDINGS['category_main_pass']:
        errors.append(
            f'{FINDINGS_CSV}: main-pass category counts are {main_category}, expected '
            f'{EXPECTED_FINDINGS["category_main_pass"]}. Either the register changed or a '
            f'document is now quoting stale numbers.'
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
    if open_spot:
        errors.append(f'{FINDINGS_CSV}: {open_spot} spot-check findings carry no proposed correction (expected 0 after T1 triage)')

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
