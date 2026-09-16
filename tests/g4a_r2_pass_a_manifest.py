#!/usr/bin/env python3
"""Guard the pre-inspection R2 Pass-A stable-ID chunk manifest."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "qa" / "r2_pass_a_manifest.py"
MANIFEST = ROOT / "docs" / "G4A_R2_PASS_A_CHUNK_MANIFEST.json"
LEARNER_BLOB = "1c184e84e5c63e3a9f8e386af13787664a23bd66"


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def load_script():
    spec = importlib.util.spec_from_file_location("r2_pass_a_manifest", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_script()
    pending = module.load_pending_ids()
    expected = module.render(module.build_manifest(pending))
    actual = MANIFEST.read_bytes()
    assert actual == expected, "manifest is not a deterministic regeneration"
    assert b"\r\n" not in actual and actual.endswith(b"\n")

    data = json.loads(actual)
    chunks = data["chunks"]
    assert [chunk["count"] for chunk in chunks] == [230, 230, 230, 229]
    flattened = [stable_id for chunk in chunks for stable_id in chunk["ids"]]
    assert flattened == pending
    assert len(flattened) == len(set(flattened)) == 919
    for chunk in chunks:
        assert chunk["count"] == len(chunk["ids"])
        assert chunk["first_id"] == chunk["ids"][0]
        assert chunk["last_id"] == chunk["ids"][-1]
        assert chunk["ids"] == sorted(chunk["ids"])

    assert git("rev-parse", "HEAD:web/vocabulary.js") == LEARNER_BLOB
    print("G4-A R2 PASS-A MANIFEST PASS")
    print("chunks=230/230/230/229 coverage=919/919 duplicates=0 omissions=0")
    print("sha256=" + hashlib.sha256(actual).hexdigest())
    print("learner blob unchanged=" + LEARNER_BLOB)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
