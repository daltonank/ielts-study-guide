#!/usr/bin/env python3
"""Deterministic source->final reproduction guard for the SB-0773 repair.

The G4-A P1 closeout repaired the malformed ``minute2`` headword at the canonical
source (``Study Bank!A777`` and ``Oxford C1 Bank!B774`` are both ``minute``). This
test proves, from a clean checkout, that:

  1. ``scripts/migrate_vocabulary.py`` re-migrates the workbook to the exact base
     blob the guarded P0 step expects, and that SB-0773 retains its Oxford
     provenance (oxfordId / topicTags / sourceUrls / pos) after the join.
  2. The full guarded pipeline (P0 -> T2 -> T3 -> T4 -> SB-0773 structural stamp)
     deterministically reaches the reviewed final ``web/vocabulary.js`` blob.

It runs the real generators against the real workbook, verifying every pinned
input/output git-blob in the chain, then restores the on-disk artifact.
"""

import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
VOCAB = ROOT / "web" / "vocabulary.js"
WORKBOOK = ROOT / "source" / "IELTS_Academic_C1_Ukrainian_Vocabulary_Bank.xlsx"
FINAL_BLOB = "9282d2013dcf382bbb439384247a0be0be0dede2"  # SB-0773 stage output (intermediate)
# T5-B appends TWO guarded post-migration stages (definitionUa repeat remediation, issue #4)
# on top of the SB-0773 final: first the adjacent/punctuation-separated stage (bb173f36),
# then the connector-separated stage (7520f722). Earlier historical stages are NOT repinned;
# the chain simply grows by two stages ending at the new pinned final blob.
T5B_FINAL_BLOB = "bb173f3614dbf35558d96a17b7f692d28f82f303"  # adjacent stage output (intermediate)
T5B_CONNECTOR_FINAL_BLOB = "7520f7220a64df20240523cf12fcd08a70734bc0"  # connector stage output (final)
# Reviewed learner-facing SB-0773 fields (web/vocabulary.js at the PR #5 head). Pinned as
# literals so any drift in stable identity or the Ukrainian fields fails the test closed —
# the source-chain guard alone proves provenance, not Ukrainian-field preservation.
SB0773_ID = "SB-0773"
SB0773_UA = "крихітний; надзвичайно малий"
SB0773_DEFINITION_UA = "Надзвичайно малий за розміром або незначний за кількістю."


def blob(data: bytes) -> str:
    h = hashlib.sha1()
    h.update(b"blob " + str(len(data)).encode() + b"\0")
    h.update(data)
    return h.hexdigest()


def disk_blob() -> str:
    return blob(VOCAB.read_bytes())


def sb0773() -> dict:
    text = VOCAB.read_text(encoding="utf-8")
    vocab = json.loads(re.search(r"window\.VOCABULARY=(\[.*\]);", text, re.DOTALL).group(1))
    return {e["id"]: e for e in vocab}["SB-0773"]


def run(*args) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def payload_meta(name: str) -> dict:
    return json.loads((ROOT / "scripts" / "qa" / name).read_text(encoding="utf-8"))["_meta"]


def sb_step_pins() -> tuple:
    src = (ROOT / "scripts" / "qa" / "apply_sb0773_headword_fix.py").read_text(encoding="utf-8")
    exp_in = re.search(r'EXPECTED_INPUT = "([0-9a-f]{40})"', src).group(1)
    exp_out = re.search(r'EXPECTED_OUTPUT = "([0-9a-f]{40})"', src).group(1)
    return exp_in, exp_out


def main() -> int:
    p0 = payload_meta("p0_corrections.json")
    t2 = payload_meta("p1_t2_corrections.json")
    t3 = payload_meta("p1_t3_corrections.json")
    t4 = payload_meta("p1_t4_corrections.json")
    sb_in, sb_out = sb_step_pins()

    # Chain must be internally consistent: each output feeds the next input.
    assert p0["expected_output_blob_sha1"] == t2["expected_input_blob_sha1"], "P0->T2 chain broken"
    assert t2["expected_output_blob_sha1"] == t3["expected_input_blob_sha1"], "T2->T3 chain broken"
    assert t3["expected_output_blob_sha1"] == t4["expected_input_blob_sha1"], "T3->T4 chain broken"
    assert t4["expected_output_blob_sha1"] == sb_in, "T4->SB-0773 chain broken"
    assert sb_out == FINAL_BLOB, "SB-0773 step does not target the reviewed final blob"
    t5b = payload_meta("t5b_repeat_corrections.json")
    assert t5b["expected_input_blob_sha1"] == FINAL_BLOB, "SB-0773->T5-B chain broken"
    assert t5b["expected_output_blob_sha1"] == T5B_FINAL_BLOB, "T5-B adjacent step does not target its pinned blob"
    t5bc = payload_meta("t5b_connector_corrections.json")
    assert t5bc["expected_input_blob_sha1"] == T5B_FINAL_BLOB, "T5-B adjacent->connector chain broken"
    assert t5bc["expected_output_blob_sha1"] == T5B_CONNECTOR_FINAL_BLOB, "T5-B connector step does not target the new final blob"

    backup = pathlib.Path(tempfile.mkdtemp()) / "vocabulary.js"
    shutil.copy2(VOCAB, backup)
    try:
        # 1. Clean migration reproduces the guarded base and retains provenance.
        run("scripts/migrate_vocabulary.py", str(WORKBOOK))
        assert disk_blob() == p0["expected_input_blob_sha1"], (
            f"migration base {disk_blob()} != P0 expected_input {p0['expected_input_blob_sha1']}")
        base = sb0773()
        assert base["word"] == "minute" and base["pos"] == "adj.", base
        assert base["sourceRefs"]["oxfordId"] == 773, "SB-0773 lost Oxford provenance in migration"
        assert base["topicTags"] == ["General"], base["topicTags"]
        assert base["sourceUrls"] and "oxford" in base["sourceUrls"][0].lower(), base["sourceUrls"]

        # 2. Guarded pipeline reproduces every pinned stage and the reviewed final.
        run("scripts/qa/apply_p0_fixes.py")
        assert disk_blob() == p0["expected_output_blob_sha1"], "P0 output blob drift"
        run("scripts/qa/apply_p1_t2_fixes.py")
        assert disk_blob() == t2["expected_output_blob_sha1"], "T2 output blob drift"
        run("scripts/qa/apply_p1_batch_fixes.py", "scripts/qa/p1_t3_corrections.json")
        assert disk_blob() == t3["expected_output_blob_sha1"], "T3 output blob drift"
        run("scripts/qa/apply_p1_batch_fixes.py", "scripts/qa/p1_t4_corrections.json")
        assert disk_blob() == t4["expected_output_blob_sha1"], "T4 output blob drift"
        run("scripts/qa/apply_sb0773_headword_fix.py")
        assert disk_blob() == FINAL_BLOB, f"final blob {disk_blob()} != reviewed {FINAL_BLOB}"

        final = sb0773()
        assert final["word"] == "minute" and final["pos"] == "adj.", final
        assert final["sourceRefs"]["oxfordId"] == 773, final
        assert final["topicTags"] == ["General"], final
        assert final["sourceUrls"], final
        assert final["translationQa"].startswith("Reviewed — G4-A P1"), final["translationQa"]
        # Stable identity and Ukrainian fields must survive the clean-migration pipeline
        # exactly as reviewed — a provenance-only guard could pass while these drifted.
        assert final["id"] == SB0773_ID, final["id"]
        assert final["ua"] == SB0773_UA, final["ua"]
        assert final["definitionUa"] == SB0773_DEFINITION_UA, final["definitionUa"]

        # 3. T5-B adjacent guarded stage reproduces its pinned blob and lands the
        # adjacent/punctuation-separated definitionUa repeat corrections. SB-0773 untouched.
        run("scripts/qa/apply_t5b_repeat_fixes.py")
        assert disk_blob() == T5B_FINAL_BLOB, (
            f"T5-B adjacent blob {disk_blob()} != reviewed {T5B_FINAL_BLOB}")
        t5b_payload = json.loads(
            (ROOT / "scripts" / "qa" / "t5b_repeat_corrections.json").read_text(encoding="utf-8"))
        after = {e["id"]: e for e in json.loads(
            re.search(r"window\.VOCABULARY=(\[.*\]);", VOCAB.read_text(encoding="utf-8"),
                      re.DOTALL).group(1))}
        for cid, corr in t5b_payload["corrections"].items():
            assert after[cid]["definitionUa"] == corr["definitionUa"], (
                f"T5-B adjacent correction for {cid} did not land")

        # 4. T5-B connector guarded stage reproduces the new final blob and lands the 64
        # connector-separated definitionUa repeat corrections. SB-0773 still untouched.
        run("scripts/qa/apply_t5b_connector_fixes.py")
        assert disk_blob() == T5B_CONNECTOR_FINAL_BLOB, (
            f"T5-B connector final blob {disk_blob()} != reviewed {T5B_CONNECTOR_FINAL_BLOB}")
        t5bc_payload = json.loads(
            (ROOT / "scripts" / "qa" / "t5b_connector_corrections.json").read_text(encoding="utf-8"))
        after = {e["id"]: e for e in json.loads(
            re.search(r"window\.VOCABULARY=(\[.*\]);", VOCAB.read_text(encoding="utf-8"),
                      re.DOTALL).group(1))}
        for cid, corr in t5bc_payload["corrections"].items():
            assert after[cid]["definitionUa"] == corr["definitionUa"], (
                f"T5-B connector correction for {cid} did not land")
        assert after["SB-0773"]["definitionUa"] == SB0773_DEFINITION_UA, "T5-B disturbed SB-0773"
    finally:
        shutil.copy2(backup, VOCAB)

    assert disk_blob() == T5B_CONNECTOR_FINAL_BLOB, "restore failed"
    print("G4-A SB-0773 SOURCE-CHAIN PASS: workbook -> base -> P0 -> T2 -> T3 -> T4 -> "
          f"SB-0773 {FINAL_BLOB} -> T5-B adjacent {T5B_FINAL_BLOB} -> T5-B connector "
          f"{T5B_CONNECTOR_FINAL_BLOB} reproduced; SB-0773 provenance + stable id + Ukrainian "
          "fields retained; 35 adjacent + 64 connector T5-B repeat corrections landed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
