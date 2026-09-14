#!/usr/bin/env python3
"""Shared, deterministic helpers for the G4-A residual-population audit (issue #4).

READ-ONLY over learner data. Nothing here mutates web/vocabulary.js or any register.
Every function is deterministic and depends only on repository files, so any resumed
session (or reviewer) reproduces identical buckets, detectors and rosters.

Bucket model (partition of all 1,784 IDs), documented in
docs/G4A_RESIDUAL_AUDIT_CP2_POPULATION.md:

  (a) historical-register finding IDs          -> docs/G4A_UKRAINIAN_QA_FINDINGS.csv
  (b) supplemental corrected/benign IDs        -> docs/G4A_T5B_SUPPLEMENTAL_FINDINGS.csv
      (excluding SB-1015, which is re-opened by the PR #7 review and lives in bucket c)
  (c) known-open residual (24: SB-1015 + 23 seed-20260913 findings from the PR #7 review)
  (d) never-flagged clean pool

  residual-to-audit = (c) + (d)
"""
from pathlib import Path
import csv, json, re

ROOT = Path(__file__).resolve().parents[2]
VOCAB_JS = ROOT / "web" / "vocabulary.js"
HISTORICAL_CSV = ROOT / "docs" / "G4A_UKRAINIAN_QA_FINDINGS.csv"
SUPPLEMENTAL_CSV = ROOT / "docs" / "G4A_T5B_SUPPLEMENTAL_FINDINGS.csv"

# Canonical 24 known-open residual P1s, from the PR #7 review comment
# (https://github.com/daltonank/ielts-study-guide/pull/7#issuecomment-5659705649).
KNOWN_OPEN_SB1015 = "SB-1015"  # 'retrieve' — ua too generic vs definitionUa (re-opened)
SEED_20260913_GRAMMAR_CALQUE = [
    "SB-0009", "SB-0191", "SB-0295", "SB-0363", "SB-0371", "SB-0467", "SB-0724",
]
SEED_20260913_POS_MORPH = [
    "SB-0058", "SB-0306", "SB-0498", "SB-0749", "SB-0797",
    "SB-1635", "SB-1695", "SB-1707", "SB-1731", "SB-1735",
]
SEED_20260913_SEMANTIC = [
    "SB-0142", "SB-0571", "SB-0647", "SB-0840", "SB-1211", "SB-1464",
]
SEED_20260913_ALL = sorted(
    SEED_20260913_GRAMMAR_CALQUE + SEED_20260913_POS_MORPH + SEED_20260913_SEMANTIC
)
KNOWN_OPEN_24 = sorted([KNOWN_OPEN_SB1015] + SEED_20260913_ALL)

# Per-ID category for the 23 seed findings (SB-1015 handled separately).
SEED_20260913_CATEGORY = {}
for _id in SEED_20260913_GRAMMAR_CALQUE:
    SEED_20260913_CATEGORY[_id] = "grammar-calque-fragment"
for _id in SEED_20260913_POS_MORPH:
    SEED_20260913_CATEGORY[_id] = "pos-morphology-mismatch"
for _id in SEED_20260913_SEMANTIC:
    SEED_20260913_CATEGORY[_id] = "semantic-pedagogical-error"

CYRILLIC = re.compile(r"[а-яіїєґА-ЯІЇЄҐ']")
WORD_RE = re.compile(r"[а-яіїєґА-ЯІЇЄҐ'\-]+", re.UNICODE)
PLACEHOLDER_RE = re.compile(r"\bDraft\b|\bTODO\b|\bFIXME\b|\{\{|undefined|\[object Object\]|верифікуй|verify in context", re.IGNORECASE)

# Mechanical calque / russianism surface markers (conservative; each is a *candidate*,
# not a conviction — CP3 adjudicates). Lower-cased WHOLE-WORD/phrase match on
# ua/definitionUa. Markers are chosen to be genuine russianisms that are unlikely to be
# a legitimate-substring false positive (e.g. bare "нада" was removed because it is a
# substring of the legitimate надавати/надання).
CALQUE_MARKERS = [
    "получити", "получати", "получив",
    "слідуючий", "наступаючий",
    "по крайній мірі", "на протязі", "в залежності від", "у залежності від",
    "співпадати", "співпадіння", "співпадає",
    "приймати участь", "приймає участь",
    "у якості", "в якості",
    "більш краще", "самий кращий", "все рівно", "на рахунок того",
    "любий випадок", "слідувати", "по відношенню до",
]


def load_vocab():
    """Return the parsed window.VOCABULARY list (deterministic order)."""
    src = VOCAB_JS.read_text(encoding="utf-8")
    m = re.search(r"window\.VOCABULARY\s*=\s*(\[.*\]);", src, re.S)
    if not m:
        raise SystemExit("could not locate window.VOCABULARY array in vocabulary.js")
    return json.loads(m.group(1))


def all_ids(vocab=None):
    vocab = vocab if vocab is not None else load_vocab()
    return sorted(e["id"] for e in vocab)


def historical_ids():
    with HISTORICAL_CSV.open(encoding="utf-8") as fh:
        return set(r["id"] for r in csv.DictReader(fh))


def supplemental_ids():
    with SUPPLEMENTAL_CSV.open(encoding="utf-8") as fh:
        return set(r["stable_id"] for r in csv.DictReader(fh))


def buckets(vocab=None):
    """Deterministic partition of every ID into a, b, c, d (no double counting)."""
    vocab = vocab if vocab is not None else load_vocab()
    ids = set(e["id"] for e in vocab)
    hist = historical_ids()
    supp = supplemental_ids()
    known = set(KNOWN_OPEN_24)
    a = ids & hist
    # supplemental-only, minus any also-historical, minus SB-1015 (moved to bucket c)
    b = (ids & supp) - a - known
    c = ids & known
    d = ids - a - b - c
    return {"a_historical": a, "b_supplemental": b, "c_known_open": c, "d_clean": d}


def residual_ids(vocab=None):
    """residual-to-audit = clean pool (d) + known-open (c), deterministic sorted."""
    bk = buckets(vocab)
    return sorted(bk["c_known_open"] | bk["d_clean"])


# ----------------------------- mechanical detectors -----------------------------

def _words(text):
    return WORD_RE.findall((text or "").lower())


def detect_adjacent_repeat(text):
    """Adjacent identical-word repeat (case-insensitive), e.g. 'стан стан'."""
    ws = _words(text)
    hits = []
    for i in range(len(ws) - 1):
        if ws[i] == ws[i + 1] and len(ws[i]) > 1:
            hits.append(ws[i])
    return hits


def detect_connector_repeat(text):
    """Connector/punctuation-separated identical-word repeat, e.g. 'стан або стан',
    'мета, або мета'. Two identical content words separated only by a connector
    and/or punctuation."""
    raw = (text or "").lower()
    tokens = re.findall(r"[а-яіїєґ'\-]+|[,;:]|\bабо\b|\bчи\b|\bта\b|\bі\b", raw)
    connectors = {"або", "чи", "та", "і", ",", ";", ":"}
    content = [t for t in re.findall(r"[а-яіїєґ'\-]+", raw)]
    hits = []
    # sliding window: word, (connector/punct)+, same word
    idx_words = [(m.group(0), m.start()) for m in re.finditer(r"[а-яіїєґ'\-]+", raw)]
    for i in range(len(idx_words) - 1):
        w1, s1 = idx_words[i]
        w2, s2 = idx_words[i + 1]
        if len(w1) <= 1:
            continue
        between = raw[s1 + len(w1):s2].strip()
        if w1 == w2 and between and all(
            (b in connectors or b in {",", ";", ":", " "}) for b in re.split(r"\s+", between) if b
        ):
            hits.append(f"{w1}{'/'+between if between else ''}/{w2}")
    return hits


def detect_placeholder(entry):
    """Placeholder/Draft/null in learner-facing ua/definitionUa (translationQa Draft is
    the migration default and is reported separately, not as a defect)."""
    hits = []
    for field in ("ua", "definitionUa"):
        val = entry.get(field)
        if val is None or (isinstance(val, str) and not val.strip()):
            hits.append(f"{field}:empty/null")
        elif isinstance(val, str) and PLACEHOLDER_RE.search(val):
            hits.append(f"{field}:placeholder")
    return hits


def detect_calque(entry):
    hits = []
    for field in ("ua", "definitionUa"):
        val = (entry.get(field) or "").lower()
        for marker in CALQUE_MARKERS:
            # whole-word/phrase boundary so we do not match inside a longer legit word
            if re.search(r"(?<![а-яіїєґ'])" + re.escape(marker) + r"(?![а-яіїєґ'])", val):
                hits.append(f"{field}:{marker}")
    return hits


def detect_empty_ua(entry):
    hits = []
    for field in ("ua", "definitionUa"):
        val = entry.get(field)
        if val is None or (isinstance(val, str) and not val.strip()):
            hits.append(field)
        elif isinstance(val, str) and not CYRILLIC.search(val):
            hits.append(f"{field}:no-cyrillic")
    return hits


# POS morphology heuristics: mechanical, conservative. Ukrainian verb infinitives
# typically end in -ти/-ть; adjectives commonly in -ий/-ій/-а/-е (m/f/n); adverbs -о/-е.
def detect_pos_morphology(entry):
    """Mechanical POS vs ua-morphology mismatch signal. Conservative and precise so it
    is a low-noise *candidate* detector (CP3 adjudicates each hit).

    Precision choices, informed by CP2 calibration:
      * Ukrainian verb infinitives end in -ти/-тися/-тись (NOT bare -ть, which is also
        the ending of many feminine abstract nouns: відсутність, залежність, ...).
      * For a multi-word gloss the HEAD is the first token (verb phrases like
        "кинути виклик", "знизати плечима" are headed by the verb), so single-POS
        judgements use the head token, not the last token.
      * Entries with a dual/compound pos (e.g. "v., n.") are not flagged: either
        morphology is legitimate for one of the tags.
    """
    pos = (entry.get("pos") or "").strip().lower()
    ua = (entry.get("ua") or "").strip().lower()
    if not ua:
        return []
    # dual/compound POS -> skip (ambiguous by construction)
    tags = [t for t in re.split(r"[.,/ ]+", pos) if t]
    canonical = {"v": "v", "n": "n", "adj": "adj", "adv": "adv"}
    kinds = set()
    for t in tags:
        for pref, k in (("adj", "adj"), ("adv", "adv"), ("v", "v"), ("n", "n")):
            if t.startswith(pref):
                kinds.add(k)
                break
    if len(kinds) != 1:
        return []
    kind = next(iter(kinds))
    first_seg = ua.split(",")[0].split(";")[0].split("(")[0].strip()
    toks = first_seg.split()
    if not toks:
        return []
    head = toks[0]
    infinitive = head.endswith(("ти", "тися", "тись"))
    hits = []
    if kind == "v" and len(toks) == 1 and not infinitive and len(head) > 3 and not head.endswith("ся"):
        hits.append(f"verb-gloss-not-infinitive-head:{head}")
    if kind == "n" and infinitive and len(toks) == 1:
        hits.append(f"noun-gloss-is-infinitive-head:{head}")
    return hits


BENIGN_REPEAT_ALLOWLIST = {"SB-0660", "SB-1197"}  # from the T5-B repeat guard


def run_all_detectors(entry):
    """Return dict detector_name -> list of evidence strings for one entry."""
    out = {}
    adj = detect_adjacent_repeat(entry.get("definitionUa"))
    con = detect_connector_repeat(entry.get("definitionUa"))
    if entry["id"] in BENIGN_REPEAT_ALLOWLIST:
        adj, con = [], []
    if adj:
        out["adjacent_repeat"] = adj
    if con:
        out["connector_repeat"] = con
    ph = detect_placeholder(entry)
    if ph:
        out["placeholder"] = ph
    ca = detect_calque(entry)
    if ca:
        out["calque_marker"] = ca
    eu = detect_empty_ua(entry)
    if eu:
        out["empty_or_noncyrillic"] = eu
    pm = detect_pos_morphology(entry)
    if pm:
        out["pos_morphology"] = pm
    return out


if __name__ == "__main__":
    vocab = load_vocab()
    bk = buckets(vocab)
    print("total ids:", len(all_ids(vocab)))
    for k in ("a_historical", "b_supplemental", "c_known_open", "d_clean"):
        print(f"  {k}: {len(bk[k])}")
    print("residual-to-audit:", len(residual_ids(vocab)))
    print("reconcile a+b+c+d:",
          sum(len(bk[k]) for k in bk))
