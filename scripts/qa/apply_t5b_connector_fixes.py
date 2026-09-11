#!/usr/bin/env python3
"""Apply the adjudicated G4-A T5-B connector-separated definitionUa repeat batch (issue #4).

This is the post-migration guarded stage that follows the adjacent/punctuation-separated
T5-B stage (input blob ``bb173f36``) in the deterministic correction chain. It removes the
64 confirmed connector-separated identical-word duplications in ``definitionUa`` ("X або X",
"X чи X", "X і X") that the connector-separated diagnostic scan surfaced and that were
registered as ``open-deferred-followup`` in ``docs/G4A_T5B_SUPPLEMENTAL_FINDINGS.csv``. Each
candidate was individually adjudicated (64 confirmed P1, 0 benign, 0 needs-human). It edits
``definitionUa`` only (plus the reviewed ``translationQa`` stamp).

The workbook is NOT edited: ``definitionUa`` flows from Study Bank column D through
``scripts/migrate_vocabulary.py`` into the pinned migration base blob ``4ed00c96``, and every
Ukrainian correction in this project (P0/T2/T3/T4/SB-0773/T5-B adjacent) is layered as a
post-migration guarded patch rather than at source, precisely so the frozen base blob and its
downstream pins are never repinned. This stage keeps that invariant (D-028).

Guards (fail-closed, deterministic, non-repeatable):
  * input git-blob must equal the pinned T5-B adjacent-stage output blob (this stage's input);
  * corrections apply in sorted id order and touch ``definitionUa`` only;
  * record count / unique ids / non-blank ua+definitionUa are re-checked;
  * output git-blob must equal the pinned new final blob, or nothing is written.
"""

import argparse
import hashlib
import json
import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parents[2]
VOCAB_PATH = ROOT / "web" / "vocabulary.js"
PAYLOAD_PATH = ROOT / "scripts" / "qa" / "t5b_connector_corrections.json"
MUTABLE_FIELDS = ("definitionUa",)


def git_blob_sha1(data: bytes) -> str:
    digest = hashlib.sha1()
    digest.update(b"blob " + str(len(data)).encode() + b"\0")
    digest.update(data)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compute-only", action="store_true")
    args = parser.parse_args()

    payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))
    meta = payload["_meta"]
    corrections = payload["corrections"]
    if len(corrections) != meta["apply_count"]:
        fail("apply_count does not match correction payload")

    raw_on_disk = VOCAB_PATH.read_bytes()
    if b"\r\n" in raw_on_disk and b"\n" in raw_on_disk.replace(b"\r\n", b""):
        fail("vocabulary.js contains mixed line endings")
    raw = raw_on_disk.replace(b"\r\n", b"\n")
    actual_in = git_blob_sha1(raw)
    if actual_in != meta["expected_input_blob_sha1"]:
        fail(
            f"input blob {actual_in} != expected {meta['expected_input_blob_sha1']}; "
            "refusing to mutate"
        )

    match = re.fullmatch(
        r"window\.VOCABULARY_META=(.*?);\s*\nwindow\.VOCABULARY=(.*);\s*",
        raw.decode("utf-8"),
        re.DOTALL,
    )
    if not match:
        fail("vocabulary.js does not match the expected format")
    meta_raw = match.group(1)
    vocab = json.loads(match.group(2))
    by_id = {entry["id"]: entry for entry in vocab}

    missing_ids = sorted(set(corrections) - set(by_id))
    if missing_ids:
        fail(f"vocabulary records missing: {missing_ids}")

    applied = []
    for item_id in sorted(corrections):  # deterministic ordering
        correction = corrections[item_id]
        unsupported = sorted(set(correction) - set(MUTABLE_FIELDS))
        if unsupported:
            fail(f"{item_id} attempts unsupported fields: {unsupported}")
        entry = by_id[item_id]
        changed = []
        for field in MUTABLE_FIELDS:
            if field in correction and correction[field] != entry.get(field):
                entry[field] = correction[field]
                changed.append(field)
        if not changed:
            fail(f"{item_id} changes no field")
        # Preserve an existing P1 review stamp (append) so the P1 closeout guard's
        # startswith("Reviewed — G4-A P1") assertion still holds for entries a prior
        # P1 batch already reviewed; otherwise record a fresh T5-B connector stamp.
        existing = entry.get("translationQa", "")
        if existing.startswith("Reviewed — G4-A P1"):
            entry["translationQa"] = existing + f"; T5-B connector fix ({meta['review_date']})"
        else:
            entry["translationQa"] = (
                f"Reviewed — G4-A T5-B connector-separated repeat remediation applied "
                f"({meta['review_date']})"
            )
        applied.append((item_id, changed))

    if len(vocab) != 1784:
        fail(f"record count changed: {len(vocab)}")
    ids = [entry["id"] for entry in vocab]
    if len(ids) != len(set(ids)):
        fail("duplicate IDs introduced")
    if any(not entry.get("ua") or not entry.get("definitionUa") for entry in vocab):
        fail("blank ua or definitionUa introduced")

    new_content = (
        f"window.VOCABULARY_META={meta_raw};\n"
        f"window.VOCABULARY={json.dumps(vocab, ensure_ascii=False)};\n"
    ).encode("utf-8")
    actual_out = git_blob_sha1(new_content)

    print(f"batch={meta['batch']} applied={len(applied)}")
    print(f"input={actual_in} output={actual_out}")
    if args.compute_only:
        print("compute-only: nothing written")
        return 0
    expected_out = meta["expected_output_blob_sha1"]
    if not expected_out or expected_out == "TBD":
        fail("expected_output_blob_sha1 is unset; run --compute-only and pin it")
    if actual_out != expected_out:
        fail(f"output blob {actual_out} != expected {expected_out}; nothing written")
    VOCAB_PATH.write_bytes(new_content)
    print(f"wrote {VOCAB_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
