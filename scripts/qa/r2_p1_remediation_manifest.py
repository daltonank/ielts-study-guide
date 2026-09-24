#!/usr/bin/env python3
"""Build the review-only 265-row G4-A R2 P1 remediation manifest.

Reads accepted evidence and learner vocabulary. Writes only the CSV manifest and
its Markdown summary. No learner correction or application payload is produced.
"""

from __future__ import annotations

import collections
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
BASE = "cbadd2a4eda8cc5012313b0888f85d42f3edcd83"
CHECKPOINT = "39d6f918c7087d3616acc9654eecfaf5219aefc4"
VOCAB_BLOB = "1c184e84e5c63e3a9f8e386af13787664a23bd66"
INVENTORY = "docs/G4A_R2_FINAL_INVENTORY.csv"
INTAKE = "docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv"
SUPPLEMENTAL = "docs/G4A_R2_SUPPLEMENTAL_PROPOSALS.csv"
VOCAB = "web/vocabulary.js"
RECON = [f"docs/G4A_R2_RECON_CHUNK{i}.csv" for i in (1, 2, 3)]
CSV_OUT = DOCS / "G4A_R2_P1_REMEDIATION_MANIFEST.csv"
MD_OUT = DOCS / "G4A_R2_P1_REMEDIATION_MANIFEST.md"
STAGE_B = ["SB-1709", "SB-1721", "SB-1723", "SB-1724", "SB-1731",
           "SB-1733", "SB-1735", "SB-1738", "SB-1747", "SB-1750",
           "SB-1752", "SB-1753", "SB-1759", "SB-1760", "SB-1769"]
COLS = [
    "id", "stage", "source_stage", "proposal_source", "word", "pos",
    "category", "confidence", "provenance", "finding_evidence",
    "proposal_rationale", "current_ua", "current_definitionUa",
    "source_proposed_target", "source_proposed_value", "proposed_ua",
    "proposed_definitionUa", "proposal_fields", "effective_fields",
    "current_pair_sha256", "finding_rationale", "finding_confidence",
    "proposal_evidence_quote",
]
BOTH = re.compile(r"ua: ([^|\r\n]+) \| definitionUa: ([^|\r\n]+)")
FIELDS = ("ua", "definitionUa")


def fail(message: str) -> None:
    raise ValueError(message)


def read_csv(name: str, required: set[str]) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames
        if not header or len(header) != len(set(header)) or not required <= set(header):
            fail(f"{name}: missing or duplicate required CSV column")
        rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        fail(f"{name}: malformed CSV row")
    return rows


def by_id(rows: list[dict[str, str]], label: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        sid = row["id"]
        if not sid or sid in out:
            fail(f"{label}: missing or duplicate ID {sid!r}")
        out[sid] = row
    return out


def at_commit(rev: str, name: str) -> bytes:
    return subprocess.run(["git", "show", f"{rev}:{name}"], cwd=ROOT,
                          capture_output=True, check=True).stdout


def check_frozen() -> None:
    for name in (INTAKE, *RECON, VOCAB):
        if (ROOT / name).read_bytes() != at_commit(CHECKPOINT, name):
            fail(f"{name}: differs from accepted reconciliation checkpoint")
    for name in (INVENTORY, SUPPLEMENTAL):
        if (ROOT / name).read_bytes() != at_commit(BASE, name):
            fail(f"{name}: differs from exact execution base")
    data = (ROOT / VOCAB).read_bytes()
    raw_blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if raw_blob != VOCAB_BLOB:
        fail(f"learner vocabulary blob {raw_blob} differs from {VOCAB_BLOB}")


def learner_bank() -> dict[str, dict]:
    text = (ROOT / VOCAB).read_text(encoding="utf-8")
    match = re.fullmatch(r"window\.VOCABULARY_META=(.*?);\s*\nwindow\.VOCABULARY=(\[.*\]);\s*", text, re.S)
    if not match:
        fail("web/vocabulary.js has an unexpected wrapper")
    values = json.loads(match.group(2))
    if len(values) != 1784 or len({row["id"] for row in values}) != len(values):
        fail("learner vocabulary IDs are missing or duplicated")
    return {row["id"]: row for row in values}


def normalize_legacy(sid: str, target: str, value: str) -> tuple[str, str]:
    if not target or not value.strip():
        fail(f"{sid}: accepted legacy proposal is empty")
    if target == "ua":
        return value, ""
    if target == "definitionUa":
        return "", value
    if target == "both":
        match = BOTH.fullmatch(value)
        if not match or not all(part.strip() == part and part for part in match.groups()):
            fail(f"{sid}: malformed legacy both proposal")
        return match.group(1), match.group(2)
    fail(f"{sid}: invalid legacy proposal target {target!r}")


def field_names(values: dict[str, str], current: dict[str, str] | None = None) -> str:
    selected = [name for name in FIELDS if values[name] and
                (current is None or values[name] != current[name])]
    return "|".join(selected)


def pair_hash(sid: str, ua: str, definition: str) -> str:
    return hashlib.sha256((sid + "\0" + ua + "\0" + definition).encode("utf-8")).hexdigest()


def build_rows() -> list[dict[str, str]]:
    check_frozen()
    inventory = by_id(read_csv(INVENTORY, {"id", "final_disposition", "source_stage",
                                           "proposal_state", "proposed_target", "proposed_value"}), INVENTORY)
    if len(inventory) != 1007:
        fail(f"inventory has {len(inventory)} rows, expected 1007")
    dispositions = collections.Counter(row["final_disposition"] for row in inventory.values())
    if (dispositions["P1"], dispositions["P2"],
        dispositions["consensus-clean-candidate"] + dispositions["clean-candidate"]) != (265, 149, 593):
        fail(f"inventory disposition counts differ: {dispositions}")
    p1 = sorted((row for row in inventory.values() if row["final_disposition"] == "P1"),
                key=lambda row: row["id"])
    if collections.Counter(row["source_stage"] for row in p1) != {"part1-floor": 63, "r2-reconciliation": 202}:
        fail("P1 source split differs from 63 floor / 202 reconciliation")
    if collections.Counter(row["proposal_state"] for row in p1) != {"present": 234, "absent": 31}:
        fail("P1 proposal split differs from 234 existing / 31 supplemental")
    if (p1[0]["id"], p1[249]["id"], [r["id"] for r in p1[250:]]) != ("SB-0009", "SB-1707", STAGE_B):
        fail("Stage A/B stable-ID boundaries differ from accepted ticket")

    intake = by_id(read_csv(INTAKE, {"id", "evidence", "proposed_target", "proposed_value"}), INTAKE)
    recon: dict[str, tuple[str, dict[str, str]]] = {}
    for name in RECON:
        for sid, row in by_id(read_csv(name, {"id", "evidence_quote", "rationale",
                                                 "proposed_target", "proposed_value"}), name).items():
            if sid in recon:
                fail(f"{sid}: duplicated across reconciliation chunks")
            recon[sid] = (name, row)
    supplemental = by_id(read_csv(SUPPLEMENTAL, {"id", "batch", "proposed_ua",
                                                   "proposed_definitionUa", "rationale",
                                                   "confidence", "answer_kind",
                                                   "evidence_quote"}), SUPPLEMENTAL)
    gaps = {r["id"] for r in p1 if r["proposal_state"] == "absent"}
    existing = {r["id"] for r in p1 if r["proposal_state"] == "present"}
    if len(supplemental) != 31 or set(supplemental) != gaps or existing & set(supplemental):
        fail("supplemental IDs differ from the 31 accepted P1 gaps")
    bank = learner_bank()
    out: list[dict[str, str]] = []
    noops: list[str] = []
    for index, inv in enumerate(p1):
        sid = inv["id"]
        learner = bank.get(sid)
        if learner is None or not learner["ua"] or not learner["definitionUa"]:
            fail(f"{sid}: learner row or Ukrainian field missing")
        for field in ("word", "pos", "ua", "definitionUa"):
            if inv[field] != learner[field]:
                fail(f"{sid}: inventory {field} differs from learner bank")
        if inv["source_stage"] == "part1-floor":
            source_name, source = INTAKE, intake[sid]
            finding_evidence, finding_rationale = source["evidence"], ""
        else:
            source_name, source = recon[sid]
            finding_evidence = source["evidence_quote"]
            finding_rationale = source["rationale"]
        for field in ("word", "pos", "ua", "definitionUa", "category", "confidence"):
            if inv[field] != source[field]:
                fail(f"{sid}: accepted source {field} differs from final inventory")
        if not finding_evidence.strip() or (inv["source_stage"] == "r2-reconciliation"
                                             and not finding_rationale.strip()):
            fail(f"{sid}: finding evidence/rationale missing")
        if inv["proposal_state"] == "present":
            if (source["proposed_target"], source["proposed_value"]) != (inv["proposed_target"], inv["proposed_value"]):
                fail(f"{sid}: existing proposal differs from final inventory")
            proposed_ua, proposed_definition = normalize_legacy(
                sid, source["proposed_target"], source["proposed_value"])
            target, value = source["proposed_target"], source["proposed_value"]
            proposal_rationale, confidence, proposal_quote = "", inv["confidence"], ""
        else:
            if inv["proposed_target"] or inv["proposed_value"] or source["proposed_target"] or source["proposed_value"]:
                fail(f"{sid}: absent proposal already has a legacy value")
            supplement = supplemental[sid]
            for field in ("word", "pos", "ua", "definitionUa", "category"):
                if supplement[field] != inv[field]:
                    fail(f"{sid}: supplemental {field} differs from inventory")
            if supplement["existing_rationale"] != finding_evidence or supplement["answer_kind"] != "correction":
                fail(f"{sid}: supplemental finding or answer kind differs")
            if (not supplement["evidence_quote"].strip() or
                    (supplement["evidence_quote"] not in inv["ua"] and
                     supplement["evidence_quote"] not in inv["definitionUa"])):
                fail(f"{sid}: supplemental evidence quote is not in the frozen learner text")
            if supplement["batch"] not in ("1", "2", "3"):
                fail(f"{sid}: supplemental batch invalid")
            proposed_ua = supplement["proposed_ua"]
            proposed_definition = supplement["proposed_definitionUa"]
            proposal_rationale, confidence, proposal_quote = (
                supplement["rationale"], supplement["confidence"], supplement["evidence_quote"])
            source_name = SUPPLEMENTAL
            target = value = ""  # Native source uses the two explicit proposal columns.
        proposals = {"ua": proposed_ua, "definitionUa": proposed_definition}
        current = {"ua": learner["ua"], "definitionUa": learner["definitionUa"]}
        proposal_fields = field_names(proposals)
        effective_fields = field_names(proposals, current)
        if not proposal_fields or not effective_fields:
            fail(f"{sid}: no effective correction")
        noops.extend(f"{sid}.{field}" for field in FIELDS
                     if proposals[field] and proposals[field] == current[field])
        out.append({
            "id": sid, "stage": "A" if index < 250 else "B",
            "source_stage": inv["source_stage"], "proposal_source": source_name,
            "word": inv["word"], "pos": inv["pos"], "category": inv["category"],
            "confidence": confidence, "provenance": inv["provenance"],
            "finding_evidence": finding_evidence, "proposal_rationale": proposal_rationale,
            "current_ua": current["ua"], "current_definitionUa": current["definitionUa"],
            "source_proposed_target": target, "source_proposed_value": value,
            "proposed_ua": proposed_ua, "proposed_definitionUa": proposed_definition,
            "proposal_fields": proposal_fields, "effective_fields": effective_fields,
            "current_pair_sha256": pair_hash(sid, current["ua"], current["definitionUa"]),
            "finding_rationale": finding_rationale, "finding_confidence": inv["confidence"],
            "proposal_evidence_quote": proposal_quote,
        })
    if noops != ["SB-1469.ua"]:
        fail(f"unexpected no-op proposal fields: {noops}")
    return out


def render_csv(rows: list[dict[str, str]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=COLS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def render_summary(rows: list[dict[str, str]], digest: str) -> bytes:
    proposal_counts = collections.Counter(field for row in rows for field in row["proposal_fields"].split("|"))
    effective_counts = collections.Counter(field for row in rows for field in row["effective_fields"].split("|"))
    text = f"""# G4-A R2 P1 remediation manifest

Review-only plan, built from exact accepted base `{BASE}`. It does not apply any
proposal or change the learner bank. Gate remains G4 technical PASS · G4-A
CHANGES REQUESTED · G5 BLOCKED.

## Population and partition

| Measure | Count |
|---|---:|
| Residual inventory | 1,007 |
| P1 manifest rows | 265 |
| Part-1 floor P1 | 63 |
| R2 reconciliation P1 | 202 |
| Existing accepted proposals | 234 |
| Accepted supplemental proposals | 31 |
| Stage A | 250 |
| Stage B | 15 |

The P1 IDs are sorted lexically. Stage A is the first 250 (`SB-0009` through
`SB-1707`); Stage B is the final 15:

{', '.join(STAGE_B)}.

## Proposal interpretation

`proposal_fields` lists every field represented in the accepted proposal.
`effective_fields` lists only represented fields whose value differs from the
current learner bank. Order is always `ua|definitionUa`.

| Field | Proposed | Effective |
|---|---:|---:|
| `ua` | {proposal_counts['ua']} | {effective_counts['ua']} |
| `definitionUa` | {proposal_counts['definitionUa']} | {effective_counts['definitionUa']} |

The only no-op proposal field is `SB-1469.ua`: its accepted `ua` is
`зареєстрований`, identical to the learner value, while its `definitionUa`
correction remains effective.

`source_proposed_target` and `source_proposed_value` retain legacy floor and
reconciliation proposal text, including strict `both` strings. They are blank
for the 31 supplemental rows because that accepted source already has separate
`proposed_ua` and `proposed_definitionUa` columns. `proposal_source` gives the
exact source CSV path. `finding_evidence` comes from floor intake evidence or
the reconciliation evidence quote. `finding_rationale` retains the distinct
reconciliation rationale; it is blank for floor findings. `proposal_rationale`
contains the accepted supplemental rationale; it is blank when the legacy
source has no distinct proposal rationale. `confidence` is the proposal-source
confidence. `finding_confidence` preserves final-inventory finding confidence.
These differ for 11 supplemental rows; both are retained.
`proposal_evidence_quote` preserves the accepted supplemental quote and is blank
for legacy rows that have no separate proposal quote.

Each `current_pair_sha256` is SHA-256 over UTF-8 bytes of
`id + NUL + current_ua + NUL + current_definitionUa`. This fingerprints the
current learner pair for later review, without predicting any remediation output.

## Integrity

- Manifest SHA-256: `{digest}`
- Learner vocabulary git blob: `{VOCAB_BLOB}` (unchanged)
- Accepted reconciliation checkpoint: `{CHECKPOINT}` (byte-frozen inputs)
- Supplemental and inventory source base: `{BASE}` (byte-frozen inputs)
- Generated artifacts: deterministic UTF-8 with LF line endings
- Next action: ChatGPT G4A-RT-06 review. No Stage A work is authorized here.
"""
    return text.encode("utf-8")


def main() -> int:
    try:
        rows = build_rows()
        payload = render_csv(rows)
        digest = hashlib.sha256(payload).hexdigest()
        summary = render_summary(rows, digest)
        CSV_OUT.write_bytes(payload)
        MD_OUT.write_bytes(summary)
    except (ValueError, OSError, UnicodeError, KeyError, IndexError,
            subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: 265 P1 rows; Stage A/B 250/15; proposals 234/31; no-op SB-1469.ua")
    print(f"manifest SHA-256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
