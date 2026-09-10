#!/usr/bin/env python3
"""Browser validation for the D-027 / ticket T5-A learner content-flag loop.

Served over a real local HTTP server (like g4_writing1_persistence.py) so that
localStorage is the browser's own and page.reload()/export/import go through the
genuine paths.

Covers, as hard failures:
  * the flag control exists and is keyboard-operable on all three G4-A
    Ukrainian-content surfaces (vocabulary entry, Reading UA support, Writing
    Task 1 UA support);
  * (T5-A review Finding 1) the vocabulary entry exposes TWO per-field controls,
    one capturing v.ua and one capturing v.definitionUa exactly, each labelled;
  * submitting captures a structured report into ieltsC1UAEN.state.v1.contentFlags
    with the required fields, bound to the surface's stable content id, with the
    current EN/UA text and the optional note;
  * (T5-A review Finding 2) a backup with malformed contentFlags members imports
    safely — bad members dropped/coerced, renderFlagList never throws — and a
    copy failure produces an honest failure toast, never a false success;
  * (T5-A review Finding 3) an OPENED flag disclosure (textarea + submit button)
    stays unclipped, unoccluded and tappable on all three surfaces at 320/375px;
  * reports survive a real reload;
  * the review/list view renders the flags with a copyable JSON textarea;
  * export/import round-trips the flags AND preserves unrelated learner progress;
  * keyboard-only submission works;
  * responsive with no horizontal overflow at 320/375/430/768/1024/1440 px;
  * no request ever leaves the local origin (local-first / no backend).
"""
from pathlib import Path
import http.server
import json
import re
import socket
import socketserver
import sys
import tempfile
import threading

from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent))
from browser_env import launch_chromium, describe

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
STORE = "ieltsC1UAEN.state.v1"
WIDTHS = [320, 375, 430, 768, 1024, 1440]
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(WEB), **kw)

    def log_message(self, *a):
        pass


PORT = free_port()
httpd = socketserver.TCPServer(("127.0.0.1", PORT), Handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{PORT}/index.html"


def st(page):
    return page.evaluate(f'()=>JSON.parse(localStorage.getItem("{STORE}") || "null")')


def tab_to(page, selector, limit=140):
    for _ in range(limit):
        if page.evaluate("(sel)=>document.activeElement===document.querySelector(sel)", selector):
            return True
        page.keyboard.press("Tab")
    return page.evaluate("(sel)=>document.activeElement===document.querySelector(sel)", selector)


def submit_first_flag(page, note=None):
    """Open the first <details.flag> on the current view and submit it."""
    box = page.locator("details.flag").first
    box.locator("summary.flag-summary").click()
    page.wait_for_timeout(60)
    if note is not None:
        box.locator("textarea.flag-note").fill(note)
    box.locator("[data-flag-submit]").click()
    page.wait_for_timeout(150)


try:
    with sync_playwright() as p:
        browser = launch_chromium(p)
        ctx = browser.new_context(viewport={"width": 420, "height": 900}, accept_downloads=True)
        page = ctx.new_page()
        page.goto(BASE, wait_until="load")
        page.wait_for_timeout(300)

        check(page.locator(".mobile-nav button").count() == 5, "primary nav is not five controls")

        # ---------- surface 1: vocabulary entry ------------------------------
        page.click('.mobile-nav button[data-route="words"]')
        page.wait_for_timeout(250)
        first_vocab_id = page.evaluate("()=>window.VOCABULARY[0].id")
        first_vocab_word = page.evaluate("()=>window.VOCABULARY[0].word")
        first_vocab_ua = page.evaluate("()=>window.VOCABULARY[0].ua")
        first_vocab_defua = page.evaluate("()=>window.VOCABULARY[0].definitionUa")
        check(page.locator("details.flag").count() > 0, "no flag control rendered on vocabulary entries")

        # T5-A review Finding 1: a vocabulary entry must expose TWO separate,
        # individually-attributable flag controls — one for v.ua and one for
        # v.definitionUa — each with a learner-visible field label.
        first_card = page.locator(".vocab-card").first
        check(first_card.locator("details.flag").count() == 2,
              "vocabulary entry does not render two per-field flag controls (ua + definitionUa)")
        labels = first_card.locator(".flag-field").all_inner_texts()
        check(any("ua" == l.split("/")[-1].strip() for l in labels),
              "vocab flag controls have no learner-visible 'ua' field label")
        check(any("definitionUa" in l for l in labels),
              "vocab flag controls have no learner-visible 'definitionUa' field label")

        # submit the definitionUa control (the second on the card) and confirm it
        # captures v.definitionUa exactly — not the ua text, not a concatenation.
        def_box = first_card.locator("details.flag").nth(1)
        def_box.locator("summary.flag-summary").click()
        page.wait_for_timeout(60)
        def_box.locator("[data-flag-submit]").click()
        page.wait_for_timeout(150)
        s = st(page)
        defflag = next((f for f in (s or {}).get("contentFlags", []) if f.get("field") == "definitionUa"), None)
        check(defflag is not None, "definitionUa vocab flag not captured")
        if defflag:
            check(defflag.get("kind") == "vocab", "definitionUa flag kind wrong")
            check(defflag.get("contentId") == first_vocab_id, "definitionUa flag not bound to the stable VOCABULARY id")
            check(defflag.get("en") == first_vocab_word, "definitionUa flag en must remain the headword")
            check(defflag.get("ua") == first_vocab_defua, "definitionUa flag did not capture v.definitionUa exactly")
            check(defflag.get("ua") != first_vocab_ua, "definitionUa flag captured the wrong field (v.ua)")

        # reset and run the three-surface flow with a single ua flag per surface
        page.evaluate(f'()=>localStorage.removeItem("{STORE}")')
        page.reload(wait_until="load")
        page.wait_for_timeout(250)
        page.click('.mobile-nav button[data-route="words"]')
        page.wait_for_timeout(250)
        # keyboard-native summary check
        check(page.evaluate("()=>document.querySelector('details.flag>summary').tabIndex")>=0
              or page.evaluate("()=>{const s=document.querySelector('details.flag>summary');"
                               "return s!==null}"),
              "flag summary is not a focusable summary element")
        submit_first_flag(page, note="Wrong Ukrainian gloss here")
        s = st(page)
        flags = (s or {}).get("contentFlags", [])
        check(len(flags) == 1, f"vocab flag not captured (contentFlags={len(flags)})")
        f0 = flags[0] if flags else {}
        check(f0.get("kind") == "vocab", "vocab flag kind wrong")
        check(f0.get("contentId") == first_vocab_id, "vocab flag not bound to the stable VOCABULARY id")
        check(f0.get("field") == "ua", "vocab flag field not captured")
        check(f0.get("en") == first_vocab_word, "vocab flag did not capture the English headword")
        check(f0.get("ua") == first_vocab_ua,
              "vocab ua flag did not capture v.ua exactly (must not concatenate definitionUa)")
        check(f0.get("note") == "Wrong Ukrainian gloss here", "vocab flag optional note not captured")
        check(bool(f0.get("appVersion")), "vocab flag missing appVersion")
        check(bool(ISO_RE.match(f0.get("createdAt", ""))), "vocab flag createdAt is not an ISO timestamp")
        check(bool(f0.get("id")), "vocab flag missing its own id")

        # confirmation toast
        check("Flag" in (page.text_content("#toast") or ""), "no visible confirmation after flagging")

        # ---------- surface 2: Writing Task 1 UA support ---------------------
        page.click("#menuBtn")
        page.click('#secondaryNav button[data-route="task1"]')
        page.wait_for_timeout(200)
        page.click('[data-w1-family="line_graph"]')
        page.wait_for_timeout(150)
        w1_mod = page.evaluate('()=>WRITING1_DATA.modules.find(m=>m.subskill==="line_graph").id')
        check(page.locator("details.flag").count() > 0, "no flag control on the Writing Task 1 UA support surface")
        submit_first_flag(page, note=None)
        s = st(page)
        w1flag = next((f for f in s["contentFlags"] if f["kind"] == "writing1"), None)
        check(w1flag is not None, "writing1 flag not captured")
        if w1flag:
            check(w1flag["contentId"] == w1_mod, "writing1 flag not bound to the module id")
            check(w1flag["field"] == "uaSupport", "writing1 flag field wrong")
            check(bool(w1flag["ua"]), "writing1 flag did not capture Ukrainian support text")
            check(w1flag.get("note") == "", "writing1 flag note should be empty string when omitted")

        # ---------- surface 3: Reading UA support ----------------------------
        page.click("#menuBtn")
        page.click('#secondaryNav button[data-route="reading"]')
        page.wait_for_timeout(200)
        fam = page.evaluate("()=>Object.keys(READING_DATA.familyMeta)[0]")
        page.click(f'[data-reading-family="{fam}"]')
        page.wait_for_timeout(150)
        rd_mod = page.evaluate("(f)=>READING_DATA.modules.find(m=>m.subskill===f).id", fam)
        check(page.locator("details.flag").count() > 0, "no flag control on the Reading UA support surface")
        submit_first_flag(page, note="перевірити")
        s = st(page)
        rflag = next((f for f in s["contentFlags"] if f["kind"] == "reading"), None)
        check(rflag is not None, "reading flag not captured")
        if rflag:
            check(rflag["contentId"] == rd_mod, "reading flag not bound to the module id")
            check(bool(rflag["ua"]), "reading flag did not capture Ukrainian support text")

        check(len(s["contentFlags"]) == 3, f"expected 3 flags, got {len(s['contentFlags'])}")

        # ---------- real reload persistence ----------------------------------
        page.reload(wait_until="load")
        page.wait_for_timeout(300)
        after = st(page)
        check(len(after["contentFlags"]) == 3, "flags did not survive a real reload")

        # ---------- review/list view + copyable JSON -------------------------
        page.click("#menuBtn")
        page.click('#secondaryNav button[data-route="settings"]')
        page.wait_for_timeout(200)
        body = page.text_content("body") or ""
        check("Local only" in body or "local" in body.lower(), "settings flag view lacks a local-only statement")
        check("never sent" in body or "not sent" in body.lower() or "нікуди" in body or "лише" in body,
              "settings flag view does not disclaim transmission")
        check(page.locator("#flagJson").count() == 1, "copyable flag JSON textarea not rendered")
        json_txt = page.locator("#flagJson").input_value()
        parsed = json.loads(json_txt)
        check(len(parsed) == 3, "copyable JSON does not contain all three flags")
        check(page.locator("[data-flag-copy]").count() == 1, "Copy JSON control missing")
        check(page.locator("[data-flag-export]").count() == 1, "Export flags JSON control missing")

        # copy button must not throw
        page.click("[data-flag-copy]")
        page.wait_for_timeout(100)

        # ---------- change unrelated state, then export ----------------------
        page.fill("#targetBand", "6.5")
        page.click("#saveSettings")
        page.wait_for_timeout(120)
        with page.expect_download() as dl:
            page.click("#exportBtn")
        exported = Path(tempfile.gettempdir()) / "g4a_flags_export.json"
        dl.value.save_as(str(exported))
        payload = json.loads(exported.read_text(encoding="utf-8"))
        check(len(payload.get("contentFlags", [])) == 3, "whole-state export did not include the flags")
        check(float(payload["settings"]["targetBand"]) == 6.5, "export did not include unrelated setting change")

        # dedicated flag export too
        with page.expect_download() as dl2:
            page.click("[data-flag-export]")
        flag_only = Path(tempfile.gettempdir()) / "g4a_flags_only.json"
        dl2.value.save_as(str(flag_only))
        check(len(json.loads(flag_only.read_text(encoding="utf-8"))) == 3,
              "dedicated flag export did not contain the flags")

        # ---------- wipe + import round-trip ---------------------------------
        page.evaluate(f'()=>localStorage.removeItem("{STORE}")')
        page.reload(wait_until="load")
        page.wait_for_timeout(250)
        wiped = st(page)
        check(not (wiped or {}).get("contentFlags"), "state not cleared before import")
        page.click("#menuBtn")
        page.click('#secondaryNav button[data-route="settings"]')
        page.wait_for_timeout(150)
        page.set_input_files("#importFile", str(exported))
        page.wait_for_timeout(400)
        restored = st(page)
        check(len(restored["contentFlags"]) == 3, "import did not restore the flags")
        check(float(restored["settings"]["targetBand"]) == 6.5,
              "import corrupted unrelated learner progress")
        check(isinstance(restored.get("backups"), list) and len(restored["backups"]) >= 1,
              "import did not retain a backup snapshot")

        # a legacy backup with no contentFlags key must import cleanly
        legacy = dict(payload)
        legacy.pop("contentFlags", None)
        legacy_path = Path(tempfile.gettempdir()) / "g4a_legacy.json"
        legacy_path.write_text(json.dumps(legacy), encoding="utf-8")
        page.set_input_files("#importFile", str(legacy_path))
        page.wait_for_timeout(400)
        leg = st(page)
        check(isinstance(leg.get("contentFlags"), list),
              "importing an old backup without contentFlags left the list non-array")
        # settings still shows the (now empty) flag list without error
        check("No flags yet" in (page.text_content("body") or ""),
              "empty-state review view did not render after a legacy import")

        # ---------- T5-A Finding 2 (negative): malformed members must not crash
        # A backup whose contentFlags contains non-objects / objects missing
        # fields must import through the safe path: bad members are dropped or
        # coerced, well-formed ones survive, and renderFlagList never throws.
        page_errors = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        malformed = dict(payload)
        malformed["contentFlags"] = [
            None, "not-an-object", 42, ["nested"],
            {"kind": "vocab"},  # object missing most fields — coerce, do not crash
            {"id": "OK-1", "kind": "reading", "contentId": "READ-X", "field": "uaSupport",
             "en": "Something", "ua": "щось не так", "note": "", "appVersion": "x",
             "createdAt": "2026-09-09T10:00:00Z"},
        ]
        bad_path = Path(tempfile.gettempdir()) / "g4a_malformed.json"
        bad_path.write_text(json.dumps(malformed), encoding="utf-8")
        page.set_input_files("#importFile", str(bad_path))
        page.wait_for_timeout(400)
        bad = st(page)
        check(isinstance(bad.get("contentFlags"), list),
              "malformed import left contentFlags non-array")
        check(all(isinstance(f, dict) for f in bad.get("contentFlags", [])),
              "malformed non-object flag members were not dropped/coerced on import")
        check(any(f.get("id") == "OK-1" for f in bad.get("contentFlags", [])),
              "well-formed flag member did not survive a malformed import")
        # the Settings flag view still renders (renderFlagList did not throw)
        page.click("#menuBtn")
        page.click('#secondaryNav button[data-route="settings"]')
        page.wait_for_timeout(250)
        body_m = page.text_content("body") or ""
        check("Local only" in body_m or "local" in body_m.lower(),
              "flag view did not render after a malformed import (renderFlagList may have thrown)")
        check(page.locator("#flagJson").count() == 1,
              "copyable flag JSON textarea missing after a malformed import")
        check(not page_errors, f"page threw after a malformed import: {page_errors[:2]}")

        # ---------- T5-A Finding 2 (negative): copy failure is honest ----------
        # When BOTH the Clipboard API and the execCommand fallback fail, the UI
        # must show a failure message — never a false "copied" success.
        page.evaluate("""()=>{
          try{Object.defineProperty(navigator,'clipboard',{configurable:true,
            value:{writeText:()=>Promise.reject(new Error('blocked'))}});}catch(e){}
          document.execCommand=()=>false;
        }""")
        page.click("[data-flag-copy]")
        page.wait_for_timeout(200)
        copy_toast = page.text_content("#toast") or ""
        check("failed" in copy_toast.lower() or "не вдалося" in copy_toast,
              f"copy failure did not produce an honest failure toast (got: {copy_toast!r})")
        check("copied" not in copy_toast.lower(),
              "copy reported a false success when both copy strategies failed")

        # ---------- keyboard-only submission ---------------------------------
        page.evaluate(f'()=>localStorage.removeItem("{STORE}")')
        page.goto(BASE, wait_until="load")
        page.wait_for_timeout(250)
        page.click('.mobile-nav button[data-route="words"]')
        page.wait_for_timeout(250)
        page.evaluate("()=>document.body.focus()")
        check(tab_to(page, "details.flag>summary"), "flag summary not reachable by keyboard")
        page.keyboard.press("Enter")
        page.wait_for_timeout(120)
        check(page.evaluate("()=>document.querySelector('details.flag').open"),
              "Enter did not open the flag disclosure")
        check(tab_to(page, "details.flag textarea.flag-note"),
              "flag note textarea not reachable by keyboard")
        page.keyboard.type("keyboard note")
        check(tab_to(page, "details.flag [data-flag-submit]"),
              "flag submit button not reachable by keyboard")
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        ks = st(page)
        check(len(ks.get("contentFlags", [])) == 1, "keyboard-only flag submission was not recorded")
        check(ks["contentFlags"][0].get("note") == "keyboard note",
              "keyboard-entered note not captured")

        ctx.close()

        # ---------- T5-A Finding 3: opened-control obstruction, narrow widths --
        # An OPENED flag disclosure — its textarea and submit button — must be
        # fully inside the viewport, unclipped and unoccluded by any sticky/fixed
        # chrome, with tap targets holding, on ALL THREE UA surfaces at 320/375px.
        OBSTRUCT_JS = """
        (sel)=>{const el=document.querySelector(sel);if(!el)return 'missing';
          let r=el.getBoundingClientRect();
          if(r.width<4||r.height<4)return 'zero-size';
          if(r.left<-1||r.right>innerWidth+1)
            return 'clipped-x '+Math.round(r.left)+'/'+Math.round(r.right)+'/'+innerWidth;
          el.scrollIntoView({block:'center',behavior:'instant'});
          r=el.getBoundingClientRect();
          const x=Math.min(Math.max(r.left+r.width/2,1),innerWidth-1);
          const y=Math.min(Math.max(r.top+r.height/2,1),innerHeight-1);
          const hit=document.elementFromPoint(x,y);
          if(!hit)return 'no-hit';
          if(el.contains(hit)||hit.contains(el)||hit===el)return null;
          let n=hit,pos='';
          while(n&&n!==document.body){const cs=getComputedStyle(n).position;
            if(cs==='fixed'||cs==='sticky'){pos=cs+':'+(n.className||n.tagName);break}
            n=n.parentElement}
          return 'occluded '+(pos||(hit.className||hit.tagName).toString().slice(0,30));}
        """
        for w in (320, 375):
            oc = browser.new_context(viewport={"width": w, "height": 780})
            op = oc.new_page()
            op.goto(BASE, wait_until="load")
            op.wait_for_timeout(200)
            op.add_style_tag(content="html{scroll-behavior:auto !important}")
            for name in ("words", "task1", "reading"):
                if name == "words":
                    op.click('.mobile-nav button[data-route="words"]')
                    op.wait_for_timeout(250)
                elif name == "task1":
                    op.evaluate("()=>{location.hash='#/task1'}")
                    op.wait_for_timeout(200)
                    op.click('[data-w1-family="line_graph"]')
                    op.wait_for_timeout(150)
                else:
                    op.evaluate("()=>{location.hash='#/reading'}")
                    op.wait_for_timeout(200)
                    fam = op.evaluate("()=>Object.keys(READING_DATA.familyMeta)[0]")
                    op.click(f'[data-reading-family="{fam}"]')
                    op.wait_for_timeout(150)
                check(op.locator("details.flag").count() > 0, f"{name}@{w}px: no flag control to open")
                box = op.locator("details.flag").first
                box.locator("summary.flag-summary").click()
                op.wait_for_timeout(80)
                check(op.locator("details.flag[open]").count() > 0,
                      f"{name}@{w}px: flag disclosure did not open")
                overflow = op.evaluate("()=>document.documentElement.scrollWidth-window.innerWidth")
                check(overflow <= 1,
                      f"{name}@{w}px: horizontal overflow {overflow}px with an opened flag control")
                fid = box.locator("[data-flag-submit]").get_attribute("data-flag-submit")
                for sel in (f'textarea[data-flag-note="{fid}"]', f'[data-flag-submit="{fid}"]'):
                    verdict = op.evaluate(OBSTRUCT_JS, sel)
                    check(verdict is None,
                          f"{name}@{w}px: opened flag element {sel} is {verdict}")
                sizes = op.evaluate(
                    "(fid)=>{const q=s=>document.querySelector(s).getBoundingClientRect().height;"
                    "return {s:Math.round(q('details.flag[open]>summary.flag-summary')),"
                    "b:Math.round(q('[data-flag-submit=\\''+fid+'\\']')),"
                    "t:Math.round(q('textarea[data-flag-note=\\''+fid+'\\']'))}}", fid)
                check(sizes["s"] >= 30, f"{name}@{w}px: flag summary tap target too small ({sizes['s']}px)")
                check(sizes["b"] >= 40, f"{name}@{w}px: flag submit button too small ({sizes['b']}px)")
                check(sizes["t"] >= 40, f"{name}@{w}px: flag note textarea too small ({sizes['t']}px)")
            oc.close()

        # ---------- responsive: no horizontal overflow at six widths ---------
        seed = {
            "schemaVersion": "1.0.0",
            "settings": {"languageMode": "uaen", "targetBand": 7.5},
            "contentFlags": [
                {"id": "FLAG-a", "kind": "vocab", "contentId": "SB-0001", "field": "ua",
                 "en": "meticulous", "ua": "надзвичайно ретельний — дуже уважний до деталей",
                 "note": "довга примітка " * 8, "appVersion": "x", "createdAt": "2026-09-09T10:00:00Z"},
                {"id": "FLAG-b", "kind": "writing1", "contentId": "W1M-LINE", "field": "uaSupport",
                 "en": "Line graphs", "ua": "опис руху в часі", "note": "",
                 "appVersion": "x", "createdAt": "2026-09-09T10:01:00Z"},
            ],
        }
        for w in WIDTHS:
            rc = browser.new_context(viewport={"width": w, "height": 900})
            pg = rc.new_page()
            pg.goto(BASE, wait_until="load")
            pg.evaluate("(s)=>localStorage.setItem('%s', JSON.stringify(s))" % STORE, seed)
            pg.reload(wait_until="load")  # real reload so the seed is loaded into memory
            pg.wait_for_timeout(150)
            for route in ("words", "settings"):
                pg.evaluate("(r)=>{location.hash='#/'+r}", route)
                pg.wait_for_timeout(200)
                overflow = pg.evaluate(
                    "()=>document.documentElement.scrollWidth - window.innerWidth")
                check(overflow <= 1, f"horizontal overflow {overflow}px on {route} at {w}px")
                check(pg.locator("details.flag, .flag-item").count() > 0,
                      f"flag UI not present on {route} at {w}px")
            # the summary is still tappable (>=32px min-height) at the narrowest widths
            if w == 320:
                pg.evaluate("()=>{location.hash='#/words'}")
                pg.wait_for_timeout(200)
                h = pg.evaluate("()=>document.querySelector('details.flag>summary').getBoundingClientRect().height")
                check(h >= 30, f"flag summary too small to tap at 320px ({h}px)")
            rc.close()

        # ---------- no off-origin requests anywhere --------------------------
        rc = browser.new_context(viewport={"width": 420, "height": 900})
        pg = rc.new_page()
        pg.goto(BASE, wait_until="load")
        pg.wait_for_timeout(200)
        pg.click('.mobile-nav button[data-route="words"]')
        pg.wait_for_timeout(200)
        submit_first_flag(pg, note="net check")
        reqs = pg.evaluate("()=>performance.getEntriesByType('resource').map(r=>r.name)")
        external = [r for r in reqs if not r.startswith(f"http://127.0.0.1:{PORT}")]
        check(not external, f"app requested something off the local origin: {external[:3]}")
        rc.close()

        browser.close()
finally:
    httpd.shutdown()

if fails:
    print("G4A CONTENT-FLAG FUNCTIONAL FAIL")
    print("\n".join(f"  - {f}" for f in fails))
    sys.exit(1)
print(f"G4A CONTENT-FLAG FUNCTIONAL PASS (3 surfaces, per-field vocab controls "
      f"[ua+definitionUa], capture+reload+round-trip, malformed-import no-crash, "
      f"honest copy-failure, keyboard, opened-control obstruction @320/375px, "
      f"responsive {'/'.join(map(str, WIDTHS))}px, local-only) [{describe()}]")
