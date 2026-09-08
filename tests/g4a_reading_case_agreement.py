#!/usr/bin/env python3
"""G4-A regression: Reading module uaSupport case agreement (G4A-R-001..003).

The Reading question-family modules carry a Ukrainian scaffolding line of the
form:

    "Цей тип завдань перевіряє <X>. Не обирайте відповідь лише через знайоме слово."

The verb `перевіряє` ("tests / checks") governs the ACCUSATIVE case (знахідний
відмінок), so <X> must be in the accusative. The generator originally
interpolated `FAMILY_META[fam][3]` — labels written in the nominative — directly
into that slot (scripts/build_reading_curriculum.py). Twelve labels are syncretic
(neuter -ння nouns, masculine inanimates: nom == acc) and read correctly by
coincidence; three feminine-headed labels do not and produced learner-visible
grammatical errors:

    G4A-R-001  READ-MULTIPLE-CHOICE  "…головна думка"          -> "…головну думку"
    G4A-R-002  READ-YNNG             "перевіряє позиція…"       -> "перевіряє позицію…"
    G4A-R-003  READ-SHORT-ANSWER     "коротка точна відповідь…" -> "коротку точну відповідь…"

This test re-parses the GENERATED web/reading_data.js independently (it does not
import the generator) and enforces two things as hard failures:

  1. the exact nominative-only fragments that defined the bug are absent after
     `перевіряє` — the specific accusative-case failure mode; and
  2. every one of the 15 family modules carries the exact expected accusative
     scaffolding string.

Because it checks all 15 families against an independent expected table, a future
feminine-headed family that regressed to the nominative slot would fail here even
though the three original defects are fixed.

Exit code 0 only if every family label sits in the correct case.
"""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
READING = ROOT / 'web' / 'reading_data.js'

# The verb that governs the accusative in the scaffolding sentence.
GOVERNING_VERB = 'перевіряє'

# Nominative-only fragments that MUST NOT appear after `перевіряє`. Each is a
# feminine head noun/phrase whose accusative form is distinct; their presence is
# exactly the G4A-R-001..003 case-agreement defect.
FORBIDDEN_NOMINATIVE_FRAGMENTS = {
    'G4A-R-001': 'перевіряє детальне розуміння та головна думка',
    'G4A-R-002': 'перевіряє позиція та твердження автора',
    'G4A-R-003': 'перевіряє коротка точна відповідь',
}

# Independent expected accusative scaffolding, keyed by module id. Written here
# from the grammar of the sentence, NOT copied from the generator, so the two can
# be cross-checked. All 15 families are covered.
SENTENCE = 'Цей тип завдань перевіряє {}. Не обирайте відповідь лише через знайоме слово.'
EXPECTED_ACCUSATIVE = {
    'READ-MULTIPLE-CHOICE': 'детальне розуміння та головну думку',
    'READ-TFNG': 'розрізнення підтвердженої, суперечної та відсутньої інформації',
    'READ-YNNG': 'позицію та твердження автора',
    'READ-MATCHING-INFORMATION': 'пошук конкретної інформації у параграфах',
    'READ-MATCHING-HEADINGS': 'визначення головної ідеї абзацу',
    'READ-MATCHING-FEATURES': 'зіставлення тверджень з людьми, місцями або категоріями',
    'READ-MATCHING-SENTENCE-ENDINGS': 'поєднання частин речення за змістом',
    'READ-SENTENCE-COMPLETION': 'точне відтворення інформації з тексту',
    'READ-SUMMARY-COMPLETION': 'розпізнавання перефразування та узагальнення',
    'READ-NOTE-COMPLETION': 'вибір конкретних деталей',
    'READ-TABLE-COMPLETION': 'порівняння структурованої інформації',
    'READ-FLOW-CHART-COMPLETION': 'відстеження послідовності процесу та перефразування',
    'READ-DIAGRAM-LABEL': 'зіставлення тексту з етапами або частинами схеми',
    'READ-SHORT-ANSWER': 'коротку точну відповідь на основі тексту',
    'READ-INFERENCE-AUTHOR': 'висновки, підтекст і ставлення автора',
}


def load_reading():
    src = READING.read_text(encoding='utf-8')
    m = re.search(r'window\.READING_DATA\s*=\s*', src)
    if not m:
        raise SystemExit('FAIL: could not find window.READING_DATA in web/reading_data.js')
    text = src[m.end():].rstrip()
    if text.endswith(';'):
        text = text[:-1]
    return json.loads(text)


def main():
    data = load_reading()
    modules = {m['id']: m for m in data['modules']}
    family_modules = {mid: m for mid, m in modules.items()
                      if m.get('kind') == 'question_family'}

    errors = []

    # Structural: the family set the test knows about must match the data exactly.
    if set(family_modules) != set(EXPECTED_ACCUSATIVE):
        missing = sorted(set(EXPECTED_ACCUSATIVE) - set(family_modules))
        extra = sorted(set(family_modules) - set(EXPECTED_ACCUSATIVE))
        errors.append(
            f'question-family module set drift: missing {missing}, unexpected {extra}. '
            f'A new family must be added to EXPECTED_ACCUSATIVE with a correctly '
            f'declined (accusative) label, or the case-agreement bug can hide in it.'
        )

    # Each family carries the governing verb exactly once in its uaSupport.
    for mid, mod in sorted(family_modules.items()):
        ua = mod.get('uaSupport', '') or ''
        if GOVERNING_VERB not in ua:
            errors.append(f'{mid}: uaSupport does not contain the governing verb '
                          f'{GOVERNING_VERB!r}: {ua!r}')

    # Failure-mode assertion: none of the known nominative-only fragments survive.
    for rid, fragment in FORBIDDEN_NOMINATIVE_FRAGMENTS.items():
        hits = sorted(mid for mid, mod in family_modules.items()
                      if fragment in (mod.get('uaSupport', '') or ''))
        if hits:
            errors.append(
                f'{rid}: nominative-case fragment {fragment!r} still present after '
                f'{GOVERNING_VERB!r} in {hits} — the accusative-case defect is live.'
            )

    # Positive assertion: every family carries the exact expected accusative sentence.
    for mid, label in sorted(EXPECTED_ACCUSATIVE.items()):
        if mid not in family_modules:
            continue
        expected = SENTENCE.format(label)
        actual = family_modules[mid].get('uaSupport', '') or ''
        if actual != expected:
            errors.append(f'{mid}: uaSupport case/text mismatch.\n'
                          f'    expected: {expected!r}\n'
                          f'    actual:   {actual!r}')

    print('G4-A READING uaSupport CASE-AGREEMENT REGRESSION (G4A-R-001..003)')
    print('=================================================================')
    print(f'  question-family modules checked: {len(family_modules)}')
    print(f'  governing verb: {GOVERNING_VERB!r} (accusative)')
    print()
    if errors:
        for e in errors:
            print('FAIL:', e)
        print()
        print(f'FAIL: {len(errors)} case-agreement assertion(s) failed.')
        sys.exit(1)
    print('PASS: all 15 family uaSupport labels sit in the accusative after '
          f'{GOVERNING_VERB!r}; none of the nominative-only fragments (G4A-R-001..003) remain.')


if __name__ == '__main__':
    main()
