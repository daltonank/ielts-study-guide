#!/usr/bin/env python3
"""Apply the G4-A T5-B follow-up definitionUa batch (PR #7 blocking-review remediation, issue #4).

This is the THIRD guarded post-migration stage in the deterministic correction chain, layered on
top of the connector-separated stage output blob ``7520f722`` (this stage's input guard). It
applies the corrections that the PR #7 review required and that a fresh full-rubric pass surfaced:

  1. Two punctuation-separated connector repeats the whitespace-only connector detector missed
     (``SB-0364`` "міста, або міста", ``SB-0818`` "занепокоєність, або занепокоєність").
  2. Reviewer-identified blind-review defects, including one P0 (``SB-1698`` "Принесено; спричинений
     трапитися.").
  3. Eight of the 64 connector-corrected entries that carried a further semantic/grammar P1 beyond
     the removed repeat, re-adjudicated under the full Ukrainian rubric.
  4. Eight P1 defects surfaced by the durable seed-20260912 n=48 blind sample.

It edits ``definitionUa`` only (plus a reviewed ``translationQa`` stamp — any existing ``Reviewed``
stamp is APPENDED to, never overwritten, so the P1-closeout and connector history are preserved).

The workbook is NOT edited (D-028): ``definitionUa`` flows from Study Bank column D into the pinned
migration base blob ``4ed00c96``; every Ukrainian correction is layered post-migration so the frozen
base blob and downstream pins (``9282d201``, ``bb173f36``, ``7520f722``) are never repinned.

Guards (fail-closed, deterministic, non-repeatable):
  * input git-blob must equal the pinned connector-stage output blob ``7520f722``;
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
PAYLOAD_PATH = ROOT / "scripts" / "qa" / "t5b_followup_corrections.json"
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
        # Append to any existing 'Reviewed' stamp so the P1-closeout (startswith 'Reviewed — G4-A P1')
        # and the connector-stage history are preserved; otherwise record a fresh follow-up stamp.
        existing = entry.get("translationQa", "")
        if existing.startswith("Reviewed"):
            entry["translationQa"] = existing + f"; T5-B follow-up re-adjudication ({meta['review_date']})"
        else:
            entry["translationQa"] = (
                f"Reviewed — G4-A T5-B follow-up full-rubric re-adjudication applied "
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
