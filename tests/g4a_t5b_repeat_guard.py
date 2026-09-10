#!/usr/bin/env python3
"""Full-bank definitionUa identical-word repeat guard (G4-A T5-B, issue #4).

Scope (matches the T5-B ticket definition exactly): flags ADJACENT and
PUNCTUATION-SEPARATED identical-word repetition inside ``definitionUa`` across all
1,784 vocabulary records — i.e. two consecutive word tokens that are equal
case-insensitively (only whitespace/punctuation between them). Case-insensitive on
Ukrainian; exact text preserved.

This FAILS closed on any such duplication except a small, explicitly documented
allowlist of genuinely legitimate repetitions that survived individual adjudication.
There is NO broad normalisation that could hide a real defect: the check compares raw
consecutive tokens.

Two honesty properties, both enforced here rather than assumed:
  1. Non-vacuity: a seeded synthetic repetition ("слово слово") must be caught.
  2. No dead allowlist: every allowlisted id must STILL carry a repeat, so an entry
     cannot sit on the allowlist after its repeat is gone.

The distinct CONNECTOR-SEPARATED repeat class ("X або X", "X чи X" — a word between
the duplicates) is OUT of this guard's scope by ticket definition; it is a separate,
still-open finding tracked in docs/G4A_T5B_SUPPLEMENTAL_FINDINGS.csv. This guard
reports its count and cross-checks it against the register so the open finding stays
visible and cannot silently drift — it does not fail on it.
"""

import csv
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
VOCAB = ROOT / "web" / "vocabulary.js"
REGISTER = ROOT / "docs" / "G4A_T5B_SUPPLEMENTAL_FINDINGS.csv"

WORD = re.compile(r"[A-Za-zА-Яа-яІіЇїЄєҐґ’']+(?:[-’'][A-Za-zА-Яа-яІіЇїЄєҐґ]+)*")
CONNECTORS = {"або", "чи", "та", "й", "і"}

# Genuinely legitimate repetitions, individually adjudicated (T5-B). Keep this list
# minimal and documented; never add an id merely to make the run pass.
ALLOWLIST = {
    "SB-0660": "Two distinct semicolon glosses ('Дія втручання' vs 'втручання в якийсь "
               "хід подій'); the second instance heads a separate descriptive phrase.",
    "SB-1197": "Theological distinction 'Бога' (God) vs 'бога' (a god); the case "
               "difference is meaningful and correct Ukrainian.",
}


def adjacent_repeats(text):
    """Repeated tokens where two consecutive word tokens are case-insensitively equal
    (adjacent or separated only by whitespace/punctuation)."""
    toks = list(WORD.finditer(text or ""))
    return [toks[i].group() for i in range(len(toks) - 1)
            if toks[i].group().casefold() == toks[i + 1].group().casefold()]


def connector_separated_ids(vocab):
    ids = []
    for e in vocab:
        s = e.get("definitionUa") or ""
        toks = list(WORD.finditer(s))
        for i in range(len(toks) - 2):
            if (toks[i].group().casefold() == toks[i + 2].group().casefold()
                    and toks[i + 1].group().casefold() in CONNECTORS
                    and s[toks[i].end():toks[i + 1].start()].strip() == ""
                    and s[toks[i + 1].end():toks[i + 2].start()].strip() == ""):
                ids.append(e["id"])
                break
    return ids


def selfcheck():
    """Prove the detector is non-vacuous before trusting it on real data."""
    assert adjacent_repeats("слово слово") == ["слово"], "seeded adjacent repeat not caught"
    assert adjacent_repeats("текст; текст.") == ["текст"], "seeded punctuation-separated repeat not caught"
    assert adjacent_repeats("Прозорий; має властивість") == [], "clean text wrongly flagged"
    # A connector-separated pair must NOT be caught by the adjacent detector (scope proof).
    assert adjacent_repeats("стан або стан") == [], "connector-separated wrongly treated as adjacent"


def main():
    selfcheck()
    text = VOCAB.read_text(encoding="utf-8")
    vocab = json.loads(re.search(r"window\.VOCABULARY=(\[.*\]);", text, re.DOTALL).group(1))
    assert len(vocab) == 1784, f"expected 1784 records, found {len(vocab)}"

    flagged = {e["id"]: adjacent_repeats(e.get("definitionUa") or "")
               for e in vocab if adjacent_repeats(e.get("definitionUa") or "")}

    errors = []
    unexpected = sorted(set(flagged) - set(ALLOWLIST))
    for cid in unexpected:
        errors.append(f"{cid}: unremediated definitionUa repeat {flagged[cid]}")

    # No dead allowlist entries: each allowlisted id must still carry a repeat.
    dead = sorted(cid for cid in ALLOWLIST if cid not in flagged)
    for cid in dead:
        errors.append(f"{cid}: allowlisted but carries no repeat anymore — remove from ALLOWLIST")

    by_id = {e["id"]: e for e in vocab}
    missing_allow = sorted(cid for cid in ALLOWLIST if cid not in by_id)
    for cid in missing_allow:
        errors.append(f"{cid}: allowlisted id not present in vocabulary.js")

    # Cross-check the still-open connector-separated class against the register so the
    # deferred finding cannot silently drift. Informational for scope, asserted for count.
    conn_ids = set(connector_separated_ids(vocab))
    reg_open = set()
    if REGISTER.exists():
        with REGISTER.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                if row["disposition"] == "open-deferred-followup":
                    reg_open.add(row["stable_id"])
        if conn_ids != reg_open:
            errors.append(
                f"connector-separated set {len(conn_ids)} != register open-deferred "
                f"{len(reg_open)}; missing_from_register={sorted(conn_ids - reg_open)[:5]}, "
                f"stale_in_register={sorted(reg_open - conn_ids)[:5]}"
            )
    else:
        errors.append(f"{REGISTER} missing; the open connector-separated finding is untracked")

    print("G4-A T5-B FULL-BANK definitionUa REPEAT GUARD")
    print("=============================================")
    print(f"  records scanned: {len(vocab)}")
    print(f"  adjacent/punctuation-separated repeats flagged: {len(flagged)} "
          f"(allowlisted benign: {sorted(ALLOWLIST)})")
    print(f"  connector-separated (OUT OF SCOPE, open follow-up): {len(conn_ids)} entries "
          f"— tracked in {REGISTER.name}")
    print("  seeded synthetic repeat caught (non-vacuous): yes")
    print()
    if errors:
        for e in errors:
            print("FAIL:", e)
        print(f"\nFAIL: {len(errors)} repeat-guard assertion(s) failed.")
        return 1
    print("PASS: no unremediated adjacent/punctuation-separated definitionUa repeats "
          "outside the adjudicated benign allowlist; connector-separated class reconciles "
          "with the supplemental register.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
