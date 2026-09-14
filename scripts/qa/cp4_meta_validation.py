#!/usr/bin/env python3
"""CP4 — meta-validation (non-vacuity) for the residual-audit detectors. READ-ONLY.

Plants one synthetic defect of each audited class into an in-memory COPY of the bank
(NEVER web/vocabulary.js) and proves the CP2 mechanical detectors catch each. Exits 0
only if every planted defect is detected (planted == detected). This is what makes the
'0 mechanical hits over the residual population' result trustworthy rather than vacuous.
"""
from pathlib import Path
import copy, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import residual_audit_lib as lib


def base_entry(**kw):
    e = {"id": "TEST-0000", "word": "test", "pos": "n.", "ua": "тест",
         "definitionUa": "Проста коректна дефініція без дефектів.", "translationQa": "ok"}
    e.update(kw)
    return e


def main():
    planted = []  # (label, entry, detector_key)

    planted.append(("adjacent_repeat",
                    base_entry(id="TEST-ADJ", definitionUa="Це стан стан речей."),
                    "adjacent_repeat"))
    planted.append(("connector_repeat",
                    base_entry(id="TEST-CON", definitionUa="Це мета або мета проєкту."),
                    "connector_repeat"))
    planted.append(("placeholder",
                    base_entry(id="TEST-PH", definitionUa="Draft — verify in context"),
                    "placeholder"))
    planted.append(("empty_ua",
                    base_entry(id="TEST-EMPTY", ua="", definitionUa="Порожнє ua поле."),
                    "placeholder"))  # empty ua caught by placeholder+empty detectors
    planted.append(("non_cyrillic",
                    base_entry(id="TEST-LAT", ua="boundary", definitionUa="Латиниця в ua."),
                    "empty_or_noncyrillic"))
    planted.append(("calque_marker",
                    base_entry(id="TEST-CAL", definitionUa="Він приймати участь у зустрічі."),
                    "calque_marker"))
    planted.append(("pos_noun_infinitive",
                    base_entry(id="TEST-POSN", pos="n.", ua="малювати"),
                    "pos_morphology"))
    planted.append(("pos_verb_not_infinitive",
                    base_entry(id="TEST-POSV", pos="v.", ua="малюнок"),
                    "pos_morphology"))

    results = []
    detected = 0
    for label, entry, expected_key in planted:
        hits = lib.run_all_detectors(entry)
        ok = expected_key in hits
        detected += 1 if ok else 0
        results.append((label, expected_key, ok, {k: v for k, v in hits.items()}))

    # negative control: a clean entry must produce no hits
    clean_hits = lib.run_all_detectors(base_entry(id="TEST-CLEAN", pos="adj.",
                                                  ua="великий",
                                                  definitionUa="Значний за розміром або обсягом."))
    negative_ok = (len(clean_hits) == 0)

    print("CP4 META-VALIDATION (non-vacuity)")
    print("=================================")
    for label, key, ok, hits in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] planted {label:24s} expect {key:20s} hits={list(hits)}")
    print(f"  [{'PASS' if negative_ok else 'FAIL'}] negative control (clean entry) -> no hits: {list(clean_hits)}")
    print(f"planted={len(planted)} detected={detected} negative_control={'ok' if negative_ok else 'FAILED'}")

    if detected == len(planted) and negative_ok:
        print("PASS: every planted defect class detected; clean entry yields no hits (non-vacuous).")
        return 0
    print("FAIL: a planted defect was missed or the negative control fired.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
