#!/usr/bin/env python3
"""Full-bank definitionUa identical-word repeat guard (G4-A T5-B, issue #4).

Scope (both repeat classes surfaced by the T5-B work are now IN scope and fail closed):

  1. ADJACENT / PUNCTUATION-SEPARATED repetition — two consecutive word tokens equal
     case-insensitively, with only whitespace/punctuation between them ("слово слово",
     "текст; текст"). Remediated by the adjacent T5-B stage (blob bb173f36).
  2. CONNECTOR-SEPARATED repetition — the same lexeme on both sides of a single Ukrainian
     connector ("X або X", "X чи X", "X та X", "X і X", "X й X"). Remediated by the
     connector T5-B stage (blob 7520f722). Originally deferred; adjudicated (64 confirmed
     P1, 0 benign, 0 needs-human) and corrected, so it is now a hard failure condition too.

Case-insensitive on Ukrainian; exact text preserved. There is NO broad normalisation that
could hide a real defect: both checks compare raw tokens with only whitespace/punctuation (or
a single connector) between them.

This FAILS closed on any such duplication except a small, explicitly documented allowlist of
genuinely legitimate repetitions that survived individual adjudication.

Honesty properties, enforced rather than assumed:
  1. Non-vacuity: seeded synthetic repetitions (adjacent AND connector) must be caught.
  2. No dead allowlist: every allowlisted id must STILL carry the repeat it is allowlisted
     for, so an entry cannot sit on an allowlist after its repeat is gone.
  3. The connector-separated finding class is fully resolved: no register row may remain
     ``open-deferred-followup`` while this guard claims a clean bank.
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

# Genuinely legitimate ADJACENT/punctuation-separated repetitions, individually adjudicated
# (T5-B). Keep minimal and documented; never add an id merely to make the run pass.
ADJACENT_ALLOWLIST = {
    "SB-0660": "Two distinct semicolon glosses ('Дія втручання' vs 'втручання в якийсь "
               "хід подій'); the second instance heads a separate descriptive phrase.",
    "SB-1197": "Theological distinction 'Бога' (God) vs 'бога' (a god); the case "
               "difference is meaningful and correct Ukrainian.",
}

# Genuinely legitimate CONNECTOR-SEPARATED repetitions. All 64 connector-separated candidates
# were adjudicated as confirmed P1 generation artifacts and corrected, so none is benign: this
# allowlist is intentionally empty. It exists so a future, individually-justified exception has
# a documented home — never populate it to silence an unadjudicated defect.
CONNECTOR_ALLOWLIST = {}


def adjacent_repeats(text):
    """Repeated tokens where two consecutive word tokens are case-insensitively equal
    (adjacent or separated only by whitespace/punctuation)."""
    toks = list(WORD.finditer(text or ""))
    return [toks[i].group() for i in range(len(toks) - 1)
            if toks[i].group().casefold() == toks[i + 1].group().casefold()]


def connector_repeats(text):
    """Repeated tokens separated by exactly one connector word ("X або X" etc.), with only
    whitespace/punctuation between each token and the connector."""
    s = text or ""
    toks = list(WORD.finditer(s))
    out = []
    for i in range(len(toks) - 2):
        if (toks[i].group().casefold() == toks[i + 2].group().casefold()
                and toks[i + 1].group().casefold() in CONNECTORS
                and s[toks[i].end():toks[i + 1].start()].strip() == ""
                and s[toks[i + 1].end():toks[i + 2].start()].strip() == ""):
            out.append(f"{toks[i].group()} {toks[i + 1].group()} {toks[i + 2].group()}")
    return out


def selfcheck():
    """Prove both detectors are non-vacuous before trusting them on real data."""
    assert adjacent_repeats("слово слово") == ["слово"], "seeded adjacent repeat not caught"
    assert adjacent_repeats("текст; текст.") == ["текст"], "seeded punctuation-separated repeat not caught"
    assert adjacent_repeats("Прозорий; має властивість") == [], "clean text wrongly flagged"
    # A connector-separated pair must NOT be caught by the adjacent detector (class separation).
    assert adjacent_repeats("стан або стан") == [], "connector-separated wrongly treated as adjacent"
    assert connector_repeats("стан або стан") == ["стан або стан"], "seeded connector repeat not caught"
    assert connector_repeats("думка чи думка") == ["думка чи думка"], "seeded connector repeat not caught"
    assert connector_repeats("Штатів і Канади") == [], "distinct words wrongly flagged as connector repeat"
    assert connector_repeats("слово слово") == [], "adjacent repeat wrongly treated as connector"


def main():
    selfcheck()
    text = VOCAB.read_text(encoding="utf-8")
    vocab = json.loads(re.search(r"window\.VOCABULARY=(\[.*\]);", text, re.DOTALL).group(1))
    assert len(vocab) == 1784, f"expected 1784 records, found {len(vocab)}"

    adj_flagged = {e["id"]: adjacent_repeats(e.get("definitionUa") or "")
                   for e in vocab if adjacent_repeats(e.get("definitionUa") or "")}
    conn_flagged = {e["id"]: connector_repeats(e.get("definitionUa") or "")
                    for e in vocab if connector_repeats(e.get("definitionUa") or "")}
    by_id = {e["id"]: e for e in vocab}

    errors = []
    for cid in sorted(set(adj_flagged) - set(ADJACENT_ALLOWLIST)):
        errors.append(f"{cid}: unremediated ADJACENT definitionUa repeat {adj_flagged[cid]}")
    for cid in sorted(set(conn_flagged) - set(CONNECTOR_ALLOWLIST)):
        errors.append(f"{cid}: unremediated CONNECTOR-separated definitionUa repeat {conn_flagged[cid]}")

    # No dead allowlist entries: each allowlisted id must still carry the relevant repeat.
    for cid in sorted(cid for cid in ADJACENT_ALLOWLIST if cid not in adj_flagged):
        errors.append(f"{cid}: adjacent-allowlisted but carries no adjacent repeat — remove from ALLOWLIST")
    for cid in sorted(cid for cid in CONNECTOR_ALLOWLIST if cid not in conn_flagged):
        errors.append(f"{cid}: connector-allowlisted but carries no connector repeat — remove from ALLOWLIST")
    for cid in sorted(cid for cid in {**ADJACENT_ALLOWLIST, **CONNECTOR_ALLOWLIST} if cid not in by_id):
        errors.append(f"{cid}: allowlisted id not present in vocabulary.js")

    # The connector-separated class is now fully adjudicated and remediated: no register row
    # may remain open-deferred-followup. This keeps the resolved class from silently reopening.
    if REGISTER.exists():
        with REGISTER.open(encoding="utf-8", newline="") as fh:
            still_open = [row["stable_id"] for row in csv.DictReader(fh)
                          if row["disposition"] == "open-deferred-followup"]
        if still_open:
            errors.append(f"register still has {len(still_open)} open-deferred-followup rows: "
                          f"{still_open[:5]} — connector class must be fully resolved")
    else:
        errors.append(f"{REGISTER} missing; the connector-separated finding class is untracked")

    print("G4-A T5-B FULL-BANK definitionUa REPEAT GUARD")
    print("=============================================")
    print(f"  records scanned: {len(vocab)}")
    print(f"  adjacent/punctuation-separated repeats flagged: {len(adj_flagged)} "
          f"(allowlisted benign: {sorted(ADJACENT_ALLOWLIST)})")
    print(f"  connector-separated repeats flagged: {len(conn_flagged)} "
          f"(allowlisted benign: {sorted(CONNECTOR_ALLOWLIST)})")
    print("  seeded synthetic repeats caught (adjacent + connector, non-vacuous): yes")
    print()
    if errors:
        for e in errors:
            print("FAIL:", e)
        print(f"\nFAIL: {len(errors)} repeat-guard assertion(s) failed.")
        return 1
    print("PASS: no unremediated adjacent/punctuation-separated OR connector-separated "
          "definitionUa repeats outside the adjudicated benign allowlists; the connector "
          "class is fully resolved in the supplemental register.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
