#!/usr/bin/env python3
"""Byte-determinism / portability guard for scripts/migrate_vocabulary.py.

The Phase 2 migration must emit the same reviewed bytes on Windows, Linux and
macOS. ``Path.write_text()`` opens in text mode (newline=None), which translates
``\\n`` -> ``os.linesep`` and therefore emits CRLF on Windows, changing the raw
git blob away from the reviewed LF artifact and breaking every downstream
raw-byte blob guard (P0 -> T2 -> T3 -> T4 -> SB-0773 chain). This test fails
closed if that regression is reintroduced.

It has two independent halves:

  1. Static source guard (no third-party deps): the generator must write both
     artifacts with ``write_bytes(...)`` and must not use ``write_text`` for
     them. This catches a reintroduced ``write_text`` even where openpyxl is
     unavailable.
  2. Dynamic regeneration guard (requires openpyxl + the workbook): re-run the
     real migration and assert the regenerated ``web/vocabulary.js`` and
     ``docs/vocabulary_migration_manifest.json`` contain zero CRLF bytes and
     reproduce their pinned reviewed blobs exactly. On-disk artifacts are
     backed up and restored.
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
MIGRATE = ROOT / "scripts" / "migrate_vocabulary.py"
VOCAB = ROOT / "web" / "vocabulary.js"
MANIFEST = ROOT / "docs" / "vocabulary_migration_manifest.json"
WORKBOOK = ROOT / "source" / "IELTS_Academic_C1_Ukrainian_Vocabulary_Bank.xlsx"

# Pinned reviewed migration outputs (LF bytes). The vocabulary base blob is the
# same value the P0 step pins as its expected input; keeping them in sync is
# asserted below so this guard can never silently drift from the source chain.
VOCAB_BASE_BLOB = "4ed00c96e8a5fc72b2074b37980c40fbb6541b18"
MANIFEST_BLOB = "2a01f3819a61fee10de3d64e873d414b4f9f9e0e"


def blob(data: bytes) -> str:
    h = hashlib.sha1()
    h.update(b"blob " + str(len(data)).encode() + b"\0")
    h.update(data)
    return h.hexdigest()


def static_source_guard() -> None:
    src = MIGRATE.read_text(encoding="utf-8")
    # Both generated artifacts must be written via write_bytes.
    assert "out.write_bytes(" in src, "migrate_vocabulary.py must write web/vocabulary.js via write_bytes()"
    assert "manifest.write_bytes(" in src, "migrate_vocabulary.py must write the manifest via write_bytes()"
    # No write_text on the generated artifacts (text mode => platform CRLF).
    assert "out.write_text(" not in src, "web/vocabulary.js must not be written via write_text() (CRLF risk)"
    assert "manifest.write_text(" not in src, "manifest must not be written via write_text() (CRLF risk)"
    # Payloads must use explicit LF, never a CRLF literal.
    assert "\\r\\n" not in src, "migrate_vocabulary.py must not emit explicit CRLF"


def pin_consistency_guard() -> None:
    p0 = json.loads((ROOT / "scripts" / "qa" / "p0_corrections.json").read_text(encoding="utf-8"))["_meta"]
    assert p0["expected_input_blob_sha1"] == VOCAB_BASE_BLOB, (
        f"pinned base blob {VOCAB_BASE_BLOB} != P0 expected_input {p0['expected_input_blob_sha1']}")


def dynamic_regeneration_guard() -> None:
    try:
        import openpyxl  # noqa: F401
    except ModuleNotFoundError:
        print("G4-A MIGRATION PORTABILITY: openpyxl unavailable; static guard only (dynamic skipped)")
        return
    if not WORKBOOK.exists():
        print("G4-A MIGRATION PORTABILITY: workbook absent; static guard only (dynamic skipped)")
        return

    tmp = pathlib.Path(tempfile.mkdtemp())
    vocab_bak = tmp / "vocabulary.js"
    manifest_bak = tmp / "manifest.json"
    shutil.copy2(VOCAB, vocab_bak)
    shutil.copy2(MANIFEST, manifest_bak)
    try:
        subprocess.run([sys.executable, str(MIGRATE), str(WORKBOOK)], cwd=ROOT, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        vocab_bytes = VOCAB.read_bytes()
        manifest_bytes = MANIFEST.read_bytes()
        assert b"\r\n" not in vocab_bytes, "regenerated web/vocabulary.js contains CRLF"
        assert b"\r\n" not in manifest_bytes, "regenerated manifest contains CRLF"
        assert blob(vocab_bytes) == VOCAB_BASE_BLOB, (
            f"regenerated vocabulary.js blob {blob(vocab_bytes)} != pinned base {VOCAB_BASE_BLOB}")
        assert blob(manifest_bytes) == MANIFEST_BLOB, (
            f"regenerated manifest blob {blob(manifest_bytes)} != pinned {MANIFEST_BLOB}")
    finally:
        shutil.copy2(vocab_bak, VOCAB)
        shutil.copy2(manifest_bak, MANIFEST)
    print("G4-A MIGRATION PORTABILITY: regenerated LF artifacts reproduce pinned base "
          f"{VOCAB_BASE_BLOB} + manifest {MANIFEST_BLOB}; no CRLF")


def main() -> int:
    static_source_guard()
    pin_consistency_guard()
    dynamic_regeneration_guard()
    print("G4-A MIGRATION PORTABILITY PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
