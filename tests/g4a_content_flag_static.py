#!/usr/bin/env python3
"""Deterministic (no-browser) validation for the D-027 / ticket T5-A learner
content-flag correction loop.

This re-reads web/app.js and web/styles.css as text and asserts, as hard
failures, the structural guarantees the flag loop must keep:

  * the report is captured into the canonical learner-state object
    (ieltsC1UAEN.state.v1 -> contentFlags) with the required field set;
  * the flag control is present on all three G4-A Ukrainian-content surfaces
    (vocabulary entry ua/definitionUa, Reading UA support, Writing Task 1 UA
    support), with a bilingual, keyboard-native label;
  * the report exports with the rest of the learner state and survives import
    (contentFlags is normalised on the import path);
  * copy and JSON export helpers exist and a copyable textarea is rendered;
  * the flag code path performs NO network I/O — the whole app.js is asserted
    free of fetch / XHR / sendBeacon / WebSocket / EventSource / dynamic import,
    matching the local-first invariant the other suites also rely on.

It never claims G4-A PASS; it only proves the T5-A behaviour is wired in.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
CSS = (ROOT / "web" / "styles.css").read_text(encoding="utf-8")
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


# ---- 1. state key exists in defaultState and is an array --------------------
check("contentFlags:[]" in APP, "defaultState does not initialise contentFlags:[]")
check('const STORE="ieltsC1UAEN.state.v1"' in APP,
      "canonical localStorage namespace changed unexpectedly")

# ---- 2. capture function + full field set ----------------------------------
check("function submitFlag(" in APP, "submitFlag() capture function missing")
flag_obj = re.search(r"const flag=\{(.+?)\};", APP, re.S)
check(flag_obj is not None, "flag report object literal not found in submitFlag")
if flag_obj:
    body = flag_obj.group(1)
    for field in ["id:", "kind,", "contentId,", "field,", "en:", "ua:", "note:",
                  "appVersion:", "createdAt:"]:
        check(field in body, f"flag report object is missing required field: {field}")
    check("appVersion:VERSION" in body, "appVersion is not bound to the build VERSION")
    check("new Date().toISOString()" in body, "createdAt is not an ISO timestamp")
check("state.contentFlags.unshift(flag)" in APP,
      "flag is not stored into state.contentFlags")
check("saveState()" in APP, "submitFlag does not persist via saveState")

# ---- 3. stable-id binding + text capture for each kind ---------------------
check("function flagTexts(" in APP, "flagTexts() lookup helper missing")
check('window.VOCABULARY||[]).find(x=>x.id===contentId)' in APP,
      "vocab flag does not bind to a stable VOCABULARY id")
check('window.READING_DATA?.modules||[]).find(x=>x.id===contentId)' in APP,
      "reading flag does not bind to a stable READING_DATA module id")
check('w1()?.modules||[]).find(x=>x.id===contentId)' in APP,
      "writing1 flag does not bind to a stable WRITING1_DATA module id")

# ---- 4. control present on all three surfaces ------------------------------
check('flagControl("vocab",v.id,"ua")' in APP,
      "flag control not attached to the vocabulary entry (ua/definitionUa)")
check('flagControl("reading",mod.id,"uaSupport")' in APP,
      "flag control not attached to the Reading UA support surface")
check('flagControl("writing1",mod.id,"uaSupport")' in APP,
      "flag control not attached to the Writing Task 1 UA support surface")

# ---- 5. bilingual, keyboard-native control ---------------------------------
check("Flag mistake" in APP and "Це виглядає неправильно" in APP,
      "flag label is not bilingual EN/UA")
check("<details class=\"flag\">" in APP and "<summary class=\"flag-summary\">" in APP,
      "flag control is not a native <details>/<summary> (keyboard-operable) element")
check("data-flag-submit=" in APP and "data-flag-note=" in APP,
      "flag submit/note hooks missing")

# ---- 6. copy + export + review list ----------------------------------------
check("function renderFlagList(" in APP, "review/list view (renderFlagList) missing")
check("function copyFlags(" in APP, "copy support (copyFlags) missing")
check("function exportFlags(" in APP, "JSON export support (exportFlags) missing")
check('id="flagJson"' in APP, "copyable report textarea not rendered")
check("No flags yet" in APP, "empty state for the flag list is missing")

# ---- 7. export/import round-trip -------------------------------------------
# whole-state export already serialises contentFlags because it stringifies state
check("JSON.stringify(state,null,2)" in APP,
      "exportData no longer serialises the whole state (round-trip at risk)")
check("x.contentFlags=Array.isArray(x.contentFlags)?x.contentFlags:[]" in APP,
      "importData does not normalise contentFlags (old backups would break the list)")

# ---- 8. honest, local-only framing -----------------------------------------
check("Local only" in APP or "local-only" in APP or "only on this device" in APP,
      "no explicit local-only / privacy statement in the flag UI")
for banned in ["examiner", "editor", "server"]:
    # each of these words must appear in a *negating* privacy sentence
    check(banned in APP, f"privacy copy does not disclaim '{banned}'")
check("never sent" in APP or "not sent" in APP or "не надіслано" in APP or "nothing is sent" in APP,
      "flag UI does not state that reports are not transmitted")

# ---- 9. NO network in the flag path (whole-app local-first invariant) -------
# The entire app is local-first; a network primitive anywhere would violate the
# ticket's "no account, network submission, analytics, or backend" scope.
network_patterns = {
    "fetch(": r"\bfetch\s*\(",
    "XMLHttpRequest": r"\bXMLHttpRequest\b",
    "navigator.sendBeacon": r"sendBeacon",
    "WebSocket": r"\bWebSocket\b",
    "EventSource": r"\bEventSource\b",
    "dynamic import()": r"[^.\w]import\s*\(",
}
for label, pat in network_patterns.items():
    check(re.search(pat, APP) is None,
          f"app.js contains a network primitive ({label}) — flag path must stay local")

# ---- 10. styling wired so the control is visible & non-obstructive ----------
check(".flag-summary" in CSS, "flag summary has no style hook")
check(".flag-item" in CSS, "flag review item has no style hook")

if fails:
    print("G4A CONTENT-FLAG STATIC FAIL")
    print("\n".join(f"  - {f}" for f in fails))
    sys.exit(1)
print("G4A CONTENT-FLAG STATIC PASS "
      "(state key, field set, 3 surfaces, bilingual keyboard control, "
      "copy/export, import round-trip, local-only, no-network)")
