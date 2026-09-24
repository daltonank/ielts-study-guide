#!/usr/bin/env python3
"""Independent guard and seeded negatives for the review-only P1 manifest."""

from __future__ import annotations

import collections
import copy
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "cbadd2a4eda8cc5012313b0888f85d42f3edcd83"
CHECKPOINT = "39d6f918c7087d3616acc9654eecfaf5219aefc4"
VOCAB_BLOB = "1c184e84e5c63e3a9f8e386af13787664a23bd66"
INVENTORY = "docs/G4A_R2_FINAL_INVENTORY.csv"
INTAKE = "docs/G4A_RESIDUAL_AUDIT_R2_INTAKE.csv"
SUPPLEMENTAL = "docs/G4A_R2_SUPPLEMENTAL_PROPOSALS.csv"
GAPS = "docs/G4A_R2_PROPOSAL_GAP_INVENTORY.csv"
VOCAB = "web/vocabulary.js"
RECON = [f"docs/G4A_R2_RECON_CHUNK{i}.csv" for i in (1, 2, 3)]
CSV_OUT = ROOT / "docs/G4A_R2_P1_REMEDIATION_MANIFEST.csv"
MD_OUT = ROOT / "docs/G4A_R2_P1_REMEDIATION_MANIFEST.md"
STAGE_B = ["SB-1709", "SB-1721", "SB-1723", "SB-1724", "SB-1731",
           "SB-1733", "SB-1735", "SB-1738", "SB-1747", "SB-1750",
           "SB-1752", "SB-1753", "SB-1759", "SB-1760", "SB-1769"]
COLS = ["id", "stage", "source_stage", "proposal_source", "word", "pos",
        "category", "confidence", "provenance", "finding_evidence",
        "proposal_rationale", "current_ua", "current_definitionUa",
        "source_proposed_target", "source_proposed_value", "proposed_ua",
        "proposed_definitionUa", "proposal_fields", "effective_fields",
        "current_pair_sha256", "finding_rationale", "finding_confidence",
        "proposal_evidence_quote"]
FIELDS = ("ua", "definitionUa")


def check(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def csv_rows(payload: bytes, label: str) -> tuple[list[str], list[dict[str, str]]]:
    if b"\r" in payload or not payload.endswith(b"\n"):
        raise ValueError(f"{label}: not UTF-8/LF CSV")
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8"), newline=""))
    header = reader.fieldnames
    if not header or len(header) != len(set(header)):
        raise ValueError(f"{label}: missing or duplicate CSV header")
    rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError(f"{label}: malformed CSV row")
    return header, rows


def read(name: str) -> list[dict[str, str]]:
    return csv_rows((ROOT / name).read_bytes(), name)[1]


def keyed(rows: list[dict[str, str]], name: str) -> dict[str, dict[str, str]]:
    ids = [r["id"] for r in rows]
    if not all(ids) or len(ids) != len(set(ids)):
        raise ValueError(f"{name}: missing or duplicate IDs")
    return {r["id"]: r for r in rows}


def git_bytes(rev: str, name: str) -> bytes:
    return subprocess.run(["git", "show", f"{rev}:{name}"], cwd=ROOT,
                          check=True, capture_output=True).stdout


def check_sources_frozen() -> None:
    at_checkpoint = [INTAKE, *RECON, VOCAB,
                     "docs/G4A_R2_RECON_CONSENSUS_CLEAN.csv",
                     "docs/G4A_R2_RECON_ROSTER.csv",
                     "docs/G4A_R2_RECON_SUMMARY.md",
                     "docs/G4A_R2_SEED_20260914_REVIEW.csv"]
    at_base = [INVENTORY, SUPPLEMENTAL, GAPS,
               "docs/batches/G4A_R2_PROPOSAL_BATCH1.csv",
               "docs/batches/G4A_R2_PROPOSAL_BATCH2.csv",
               "docs/batches/G4A_R2_PROPOSAL_BATCH3.csv"]
    for name in at_checkpoint:
        if (ROOT / name).read_bytes() != git_bytes(CHECKPOINT, name):
            raise ValueError(f"{name}: accepted checkpoint bytes changed")
    for name in at_base:
        if (ROOT / name).read_bytes() != git_bytes(BASE, name):
            raise ValueError(f"{name}: accepted execution-base bytes changed")
    raw = (ROOT / VOCAB).read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if blob != VOCAB_BLOB:
        raise ValueError(f"learner vocabulary blob changed: {blob}")


def parse_bank() -> dict[str, dict]:
    data = (ROOT / VOCAB).read_text(encoding="utf-8")
    match = re.fullmatch(r"window\.VOCABULARY_META=(.*?);\s*\nwindow\.VOCABULARY=(\[.*\]);\s*", data, re.S)
    if match is None:
        raise ValueError("learner vocabulary wrapper changed")
    rows = json.loads(match.group(2))
    ids = [r["id"] for r in rows]
    if len(rows) != 1784 or len(ids) != len(set(ids)):
        raise ValueError("learner vocabulary row/ID count changed")
    return {r["id"]: r for r in rows}


def parse_legacy(sid: str, target: str, value: str) -> tuple[str, str]:
    if target == "ua" and value.strip():
        return value, ""
    if target == "definitionUa" and value.strip():
        return "", value
    if target == "both":
        parts = value.split(" | ")
        if len(parts) != 2 or not parts[0].startswith("ua: ") or not parts[1].startswith("definitionUa: "):
            raise ValueError(f"{sid}: malformed legacy both")
        ua, definition = parts[0][4:], parts[1][14:]
        if (not ua or not definition or ua.strip() != ua or
                definition.strip() != definition or
                any(char in ua + definition for char in "|\r\n")):
            raise ValueError(f"{sid}: malformed legacy both")
        return ua, definition
    raise ValueError(f"{sid}: invalid/empty legacy proposal")


def load_context() -> dict:
    inventory_rows = read(INVENTORY)
    inventory = keyed(inventory_rows, INVENTORY)
    intake = keyed(read(INTAKE), INTAKE)
    recon: dict[str, tuple[str, dict[str, str]]] = {}
    for name in RECON:
        for sid, row in keyed(read(name), name).items():
            if sid in recon:
                raise ValueError(f"{sid}: duplicate reconciliation ID")
            recon[sid] = name, row
    supplemental = keyed(read(SUPPLEMENTAL), SUPPLEMENTAL)
    gaps = keyed(read(GAPS), GAPS)
    bank = parse_bank()
    p1 = sorted((r for r in inventory_rows if r["final_disposition"] == "P1"),
                key=lambda r: r["id"])
    return {"inventory_rows": inventory_rows, "inventory": inventory,
            "intake": intake, "recon": recon, "supplemental": supplemental,
            "gaps": gaps, "bank": bank, "p1": p1}


def inspect(rows: list[dict[str, str]], context: dict) -> list[str]:
    errors: list[str] = []
    inv_rows = context["inventory_rows"]
    p1 = context["p1"]
    check(len(inv_rows) == 1007 and len(context["inventory"]) == 1007,
          "final inventory is not 1,007 unique rows", errors)
    dispositions = collections.Counter(r["final_disposition"] for r in inv_rows)
    check(dispositions["P1"] == 265 and dispositions["P2"] == 149 and
          dispositions["consensus-clean-candidate"] + dispositions["clean-candidate"] == 593,
          "P1/P2/clean disposition counts differ from 265/149/593", errors)
    check(collections.Counter(r["source_stage"] for r in p1) ==
          {"part1-floor": 63, "r2-reconciliation": 202},
          "P1 source split differs from 63/202", errors)
    check(collections.Counter(r["proposal_state"] for r in p1) ==
          {"present": 234, "absent": 31},
          "P1 proposal split differs from 234/31", errors)
    gap_ids = {r["id"] for r in p1 if r["proposal_state"] == "absent"}
    existing_ids = {r["id"] for r in p1 if r["proposal_state"] == "present"}
    check(len(context["supplemental"]) == 31 and
          set(context["supplemental"]) == gap_ids == set(context["gaps"]) and
          not existing_ids & set(context["supplemental"]),
          "supplemental IDs differ from the former 31 gaps", errors)
    ids = [r["id"] for r in rows]
    expected_ids = [r["id"] for r in p1]
    check(len(rows) == 265 and len(ids) == len(set(ids)),
          "manifest is not 265 unique rows", errors)
    check(set(ids) == set(expected_ids), "manifest P1 ID set mismatch (P2/clean/missing row)", errors)
    check(ids == expected_ids, "manifest is not in stable-ID order", errors)
    check([r["id"] for r in rows if r["stage"] == "B"] == STAGE_B,
          "Stage B roster differs from exact accepted 15 IDs", errors)
    check(collections.Counter(r["stage"] for r in rows) == {"A": 250, "B": 15},
          "Stage A/B count differs from 250/15", errors)
    if len(rows) >= 265:
        check((rows[0]["id"], rows[249]["id"], rows[250]["id"], rows[-1]["id"]) ==
              ("SB-0009", "SB-1707", "SB-1709", "SB-1769"),
              "Stage boundaries differ", errors)
    source_counts = collections.Counter()
    noops: list[str] = []
    for index, row in enumerate(rows):
        sid = row["id"]
        inv = context["inventory"].get(sid)
        if inv is None or inv["final_disposition"] != "P1":
            errors.append(f"{sid}: P2/clean/unknown row in manifest")
            continue
        expected_stage = "A" if expected_ids.index(sid) < 250 else "B"
        check(row["stage"] == expected_stage, f"{sid}: wrong stage", errors)
        check(row["source_stage"] == inv["source_stage"], f"{sid}: source stage changed", errors)
        for field in ("word", "pos", "category", "provenance"):
            check(row[field] == inv[field], f"{sid}: {field} differs from inventory", errors)
        if inv["source_stage"] == "part1-floor":
            source_name, source = INTAKE, context["intake"].get(sid)
            finding_evidence = source["evidence"] if source else ""
            finding_rationale = ""
        elif inv["source_stage"] == "r2-reconciliation":
            source_name, source = context["recon"].get(sid, ("", None))
            finding_evidence = source["evidence_quote"] if source else ""
            finding_rationale = source["rationale"] if source else ""
        else:
            errors.append(f"{sid}: invalid P1 source stage")
            continue
        if source is None:
            errors.append(f"{sid}: accepted finding source missing")
            continue
        for field in ("word", "pos", "ua", "definitionUa", "category", "confidence"):
            check(source[field] == inv[field], f"{sid}: source {field} differs from inventory", errors)
        check(bool(finding_evidence.strip()) and
              (inv["source_stage"] == "part1-floor" or bool(finding_rationale.strip())),
              f"{sid}: accepted finding evidence/rationale missing", errors)
        check(row["finding_evidence"] == finding_evidence and
              row["finding_rationale"] == finding_rationale,
              f"{sid}: accepted finding evidence/rationale changed", errors)
        check(row["finding_confidence"] == inv["confidence"],
              f"{sid}: finding confidence changed", errors)
        learner = context["bank"].get(sid)
        if learner is None or not learner["ua"] or not learner["definitionUa"]:
            errors.append(f"{sid}: missing/blank learner values")
            continue
        for field in ("word", "pos", "ua", "definitionUa"):
            check(inv[field] == learner[field], f"{sid}: inventory/learner {field} mismatch", errors)
        current = {"ua": row["current_ua"], "definitionUa": row["current_definitionUa"]}
        check(current == {name: learner[name] for name in FIELDS},
              f"{sid}: current learner value changed", errors)
        digest = hashlib.sha256((sid + "\0" + current["ua"] + "\0" +
                                 current["definitionUa"]).encode("utf-8")).hexdigest()
        check(row["current_pair_sha256"] == digest,
              f"{sid}: current pair fingerprint changed", errors)
        if inv["proposal_state"] == "present":
            source_counts["existing"] += 1
            check(row["proposal_source"] == source_name, f"{sid}: proposal source changed", errors)
            check((source["proposed_target"], source["proposed_value"]) ==
                  (inv["proposed_target"], inv["proposed_value"]),
                  f"{sid}: accepted proposal differs from inventory", errors)
            check((row["source_proposed_target"], row["source_proposed_value"]) ==
                  (source["proposed_target"], source["proposed_value"]),
                  f"{sid}: original proposal representation changed", errors)
            try:
                accepted = parse_legacy(sid, source["proposed_target"], source["proposed_value"])
                represented = parse_legacy(sid, row["source_proposed_target"],
                                           row["source_proposed_value"])
                check(accepted == represented, f"{sid}: legacy normalization changed", errors)
            except ValueError as exc:
                errors.append(str(exc))
                continue
            expected_rationale, expected_confidence, expected_quote = "", inv["confidence"], ""
        elif inv["proposal_state"] == "absent":
            source_counts["supplemental"] += 1
            proposal = context["supplemental"].get(sid)
            if proposal is None:
                errors.append(f"{sid}: supplemental proposal missing")
                continue
            check(row["proposal_source"] == SUPPLEMENTAL,
                  f"{sid}: supplemental proposal source changed", errors)
            check(not row["source_proposed_target"] and not row["source_proposed_value"] and
                  not inv["proposed_target"] and not inv["proposed_value"],
                  f"{sid}: supplemental row has a legacy proposal", errors)
            for field in ("word", "pos", "ua", "definitionUa", "category"):
                check(proposal[field] == inv[field], f"{sid}: supplemental {field} changed", errors)
            check(proposal["existing_rationale"] == finding_evidence and
                  proposal["answer_kind"] == "correction",
                  f"{sid}: supplemental finding/answer kind changed", errors)
            check(bool(proposal["evidence_quote"].strip()) and
                  (proposal["evidence_quote"] in inv["ua"] or
                   proposal["evidence_quote"] in inv["definitionUa"]),
                  f"{sid}: supplemental evidence quote not grounded", errors)
            accepted = (proposal["proposed_ua"], proposal["proposed_definitionUa"])
            expected_rationale, expected_confidence, expected_quote = (
                proposal["rationale"], proposal["confidence"], proposal["evidence_quote"])
        else:
            errors.append(f"{sid}: invalid proposal state")
            continue
        check((row["proposed_ua"], row["proposed_definitionUa"]) == accepted,
              f"{sid}: accepted proposal changed during normalization", errors)
        check(row["proposal_rationale"] == expected_rationale,
              f"{sid}: accepted proposal rationale changed", errors)
        check(row["proposal_evidence_quote"] == expected_quote,
              f"{sid}: accepted proposal evidence quote changed", errors)
        check(row["confidence"] == expected_confidence,
              f"{sid}: proposal confidence changed", errors)
        proposals = {"ua": row["proposed_ua"], "definitionUa": row["proposed_definitionUa"]}
        fields = "|".join(name for name in FIELDS if proposals[name])
        effective = "|".join(name for name in FIELDS if proposals[name] and
                             proposals[name] != learner[name])
        check(row["proposal_fields"] == fields, f"{sid}: proposal_fields hides/changes a field", errors)
        check(row["effective_fields"] == effective, f"{sid}: effective_fields changed", errors)
        check(bool(effective), f"{sid}: no effective correction", errors)
        noops.extend(f"{sid}.{name}" for name in FIELDS
                     if proposals[name] and proposals[name] == learner[name])
    check(source_counts == {"existing": 234, "supplemental": 31},
          "proposal-source split differs from 234/31", errors)
    check(noops == ["SB-1469.ua"], f"no-op proposal fields differ: {noops}", errors)
    return errors


def negative_tests(rows: list[dict[str, str]], context: dict,
                   original_csv: bytes, original_md: bytes) -> None:
    def row(items: list[dict[str, str]], sid: str) -> dict[str, str]:
        return next(r for r in items if r["id"] == sid)

    def drop(items: list[dict[str, str]]) -> None:
        items.pop(0)

    def inject_p2(items: list[dict[str, str]]) -> None:
        p2 = next(r for r in context["inventory_rows"] if r["final_disposition"] == "P2")
        items[0]["id"] = p2["id"]

    def move_b(items: list[dict[str, str]]) -> None:
        row(items, "SB-1709")["stage"] = "A"

    def change_current(items: list[dict[str, str]]) -> None:
        items[0]["current_ua"] += "-seed"

    def change_proposal(items: list[dict[str, str]]) -> None:
        row(items, "SB-0009")["proposed_definitionUa"] += " seed"

    def malformed_both(items: list[dict[str, str]]) -> None:
        row(items, "SB-1469")["source_proposed_value"] = "ua: broken | definitionUa"

    def hide_noop(items: list[dict[str, str]]) -> None:
        target = row(items, "SB-1469")
        target["proposed_ua"] = ""
        target["proposal_fields"] = "definitionUa"

    def second_noop(items: list[dict[str, str]]) -> None:
        row(items, "SB-1590")["proposed_ua"] = row(items, "SB-1590")["current_ua"]

    seeds = [("drop one P1", drop, "265 unique"),
             ("inject P2", inject_p2, "P2/clean"),
             ("move Stage B ID to A", move_b, "wrong stage"),
             ("change learner value", change_current, "current learner value"),
             ("change normalized proposal", change_proposal, "accepted proposal changed"),
             ("malform legacy both", malformed_both, "malformed legacy both"),
             ("hide SB-1469.ua no-op", hide_noop, "no-op proposal fields differ"),
             ("add second no-op", second_noop, "no-op proposal fields differ")]
    for label, mutate, signature in seeds:
        candidate = copy.deepcopy(rows)
        mutate(candidate)
        violations = inspect(candidate, context)
        if not any(signature in violation for violation in violations):
            raise ValueError(f"seeded negative {label!r} was not detected: {violations[:3]}")
        if CSV_OUT.read_bytes() != original_csv or MD_OUT.read_bytes() != original_md:
            raise ValueError(f"seeded negative {label!r} did not restore exact artifact bytes")
        print(f"PASS seeded negative: {label}; artifacts byte-identical")


def main() -> int:
    try:
        check_sources_frozen()
        if not CSV_OUT.exists() or not MD_OUT.exists():
            raise ValueError("manifest/summary missing; run the builder")
        original_csv, original_md = CSV_OUT.read_bytes(), MD_OUT.read_bytes()
        header, rows = csv_rows(original_csv, str(CSV_OUT))
        if header != COLS:
            raise ValueError("manifest header differs from the documented schema")
        if b"\r" in original_md or not original_md.endswith(b"\n"):
            raise ValueError("summary is not UTF-8/LF")
        summary = original_md.decode("utf-8")
        digest = hashlib.sha256(original_csv).hexdigest()
        if f"Manifest SHA-256: `{digest}`" not in summary:
            raise ValueError("summary does not name the exact manifest SHA-256")
        for fact in ("| P1 manifest rows | 265 |", "| Part-1 floor P1 | 63 |",
                     "| R2 reconciliation P1 | 202 |", "| Existing accepted proposals | 234 |",
                     "| Accepted supplemental proposals | 31 |", "| Stage A | 250 |",
                     "| Stage B | 15 |", "| `ua` | 40 | 39 |",
                     "| `definitionUa` | 261 | 261 |", "SB-1469.ua"):
            if fact not in summary:
                raise ValueError(f"summary missing accepted fact: {fact}")
        context = load_context()
        errors = inspect(rows, context)
        if errors:
            raise ValueError("; ".join(errors[:12]))
        negative_tests(rows, context, original_csv, original_md)
        for attempt in (1, 2):
            proc = subprocess.run([sys.executable, "scripts/qa/r2_p1_remediation_manifest.py"],
                                  cwd=ROOT, text=True, capture_output=True)
            if proc.returncode:
                raise ValueError(f"builder attempt {attempt} failed: {(proc.stderr or proc.stdout).strip()}")
            if CSV_OUT.read_bytes() != original_csv or MD_OUT.read_bytes() != original_md:
                raise ValueError(f"builder attempt {attempt} changed generated artifact bytes")
        diff = subprocess.run(["git", "diff", "--check"], cwd=ROOT,
                              text=True, capture_output=True)
        if diff.returncode:
            raise ValueError(f"git diff --check failed: {diff.stdout}{diff.stderr}")
    except (ValueError, OSError, UnicodeError, KeyError, IndexError,
            subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    proposal_counts = collections.Counter(name for row in rows for name in row["proposal_fields"].split("|"))
    effective_counts = collections.Counter(name for row in rows for name in row["effective_fields"].split("|"))
    print("PASS: 265/265 P1; floor/reconciliation 63/202; proposals 234/31; stages 250/15")
    print(f"proposal fields: {dict(proposal_counts)}; effective fields: {dict(effective_counts)}")
    print("PASS: only no-op SB-1469.ua; learner/evidence frozen; UTF-8/LF; two byte-identical rebuilds; diff check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
