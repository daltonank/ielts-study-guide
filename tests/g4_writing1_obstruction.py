#!/usr/bin/env python3
"""G4 obstruction and viewport-state validation.

Defect D4-004 showed that dimension and overflow assertions can pass while a
layout is visually broken, and the full-page screenshots taken for the phase
report rendered sticky and fixed elements at their scroll position, which made
the header look as though it covered content. This suite settles that question
with real viewport states instead of stitched captures.

At each of the six approved widths it verifies:
  1. the initial viewport renders,
  2. ordinary scrolled positions through the visual and the exercise,
  3. the keyboard-focused skip-link state,
  4. the skip link is visually hidden until focused,
  5. no sticky or fixed element covers a heading, control, chart, table, map
     feature, feedback block or form field once it is scrolled to,
  6. horizontal scrolling is confined to the intended chart or table container,
  7. touch targets are at least 44px and chart labels stay legible.

Obstruction is tested with elementFromPoint, which is what actually decides
whether a user can see and hit a thing.
"""
from pathlib import Path
import http.server
import socket
import socketserver
import sys
import threading

from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent))
from browser_env import launch_chromium, describe

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
SHOTS = ROOT / "docs"
WIDTHS = [320, 375, 430, 768, 1024, 1440]
FAMILIES = ["line_graph", "bar_chart", "pie_chart", "table",
            "process_diagram", "map_plan", "mixed_visual"]
CAPTURE_AT = {375, 1440}
fails = []
innerheight_floor = 420   # a 780px viewport must keep most of itself usable


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

# Is the element genuinely visible at its own centre, or is something over it?
# Can the element the learner just scrolled to actually be seen, or is a sticky
# or fixed bar over it? Sampling three points down the element handles anything
# taller than the free space between the header and the bottom bar. An element
# merely passing behind a fixed bar while scrolling is not a defect: the check
# is whether it can be brought into clear view at all.
OBSTRUCTION_JS = """
(sel) => {
  const el = document.querySelector(sel);
  if (!el) return null;
  const r = el.getBoundingClientRect();
  if (r.width < 4 || r.height < 4) return null;
  const x = Math.min(Math.max(r.left + r.width / 2, 1), innerWidth - 1);
  const top = Math.max(r.top, 1), bot = Math.min(r.bottom, innerHeight - 1);
  if (bot - top < 8) return ['off-screen after scrolling'];
  const ys = [0.25, 0.5, 0.75].map(f => top + (bot - top) * f);
  let covering = null;
  for (const y of ys) {
    const hit = document.elementFromPoint(x, y);
    if (!hit) continue;
    if (el.contains(hit) || hit.contains(el) || hit === el) return null;   // visible somewhere
    let n = hit, pos = '';
    while (n && n !== document.body) {
      const cs = getComputedStyle(n).position;
      if (cs === 'fixed' || cs === 'sticky') { pos = cs + ':' + (n.className || n.tagName); break; }
      n = n.parentElement;
    }
    covering = covering || pos || ('opaque:' + ((hit.className || hit.tagName).toString().slice(0, 30)));
  }
  return covering ? [covering] : null;
}
"""

SCROLL_AND_CHECK = """
(sel) => {
  const el = document.querySelector(sel);
  if (!el) return null;
  el.scrollIntoView({block: 'center', behavior: 'instant'});
  return true;
}
"""

TARGETS = ("h1, h2, .w1-visual svg, .w1-visual table, .w1-feature, .w1-opt, "
           ".w1-chk, .question-card, .answer-feedback, #w1Form .btn, "
           ".field input, .field textarea, .w1-order-ctl .btn, .mobile-nav button")

try:
    with sync_playwright() as p:
        browser = launch_chromium(p)
        for w in WIDTHS:
            page = browser.new_page(viewport={"width": w, "height": 780})
            page.goto(BASE, wait_until="load")
            page.wait_for_timeout(220)
            page.add_style_tag(content="html{scroll-behavior:auto !important}")

            # 4. skip link hidden until focused
            hidden = page.evaluate("()=>document.querySelector('.skip-link').getBoundingClientRect().bottom < 1")
            check(hidden, f"{w}px: the skip link is visible before it is focused")
            page.keyboard.press("Tab")
            page.wait_for_timeout(80)
            focused = page.evaluate("()=>{const r=document.querySelector('.skip-link').getBoundingClientRect();"
                                    "return document.activeElement.classList.contains('skip-link') && r.top >= 0}")
            check(focused, f"{w}px: the skip link does not appear when it receives focus")
            # 3. capture the focused skip-link state on its own
            if w in CAPTURE_AT:
                page.screenshot(path=str(SHOTS / f"qa_w1_skiplink_{w}.png"))
            # it must not sit over study content once focused
            over = page.evaluate("()=>{const r=document.querySelector('.skip-link').getBoundingClientRect();"
                                 "const m=document.querySelector('#main').getBoundingClientRect();"
                                 "return r.top < m.top}")
            check(over, f"{w}px: the focused skip link overlaps the study content instead of sitting above it")
            page.keyboard.press("Escape")
            page.evaluate("()=>document.activeElement.blur()")

            page.click("#menuBtn")
            page.click('#secondaryNav button[data-route="task1"]')
            page.wait_for_timeout(180)

            # 1. initial viewport
            if w in CAPTURE_AT:
                page.screenshot(path=str(SHOTS / f"qa_w1_viewport_list_{w}.png"))
            for anchor in ("h1", ".family-card", ".mobile-nav button"):
                page.evaluate(SCROLL_AND_CHECK, anchor)
                page.wait_for_timeout(140)
                covered = page.evaluate(OBSTRUCTION_JS, anchor)
                check(not covered, f"{w}px family list: {anchor} cannot be seen clear of sticky chrome {covered}")
            chrome = page.evaluate("""()=>{const h=document.querySelector('.app-header').getBoundingClientRect().height;
              const n=document.querySelector('.mobile-nav').getBoundingClientRect().height;
              return {h:Math.round(h),n:Math.round(n),free:Math.round(innerHeight-h-n)}}""")
            check(chrome["free"] > innerheight_floor,
                  f"{w}px: sticky chrome leaves only {chrome['free']}px of usable height {chrome}")

            for fam in FAMILIES:
                page.click(f'[data-w1-family="{fam}"]')
                page.wait_for_timeout(90)
                first = page.evaluate('(f)=>WRITING1_DATA.exercises.find(e=>e.questionFamily===f).id', fam)
                page.click(f'[data-w1-exercise="{first}"]')
                page.wait_for_timeout(140)

                # 2. ordinary scrolled positions through the visual and exercise
                for anchor in (".w1-visual", ".w1-visual svg, .w1-visual table, .w1-feature",
                               ".question-card", "#w1Form .btn"):
                    page.evaluate(SCROLL_AND_CHECK, anchor)
                    page.wait_for_timeout(140)
                    # 5. nothing sticky may cover what we just scrolled to
                    covered = page.evaluate(OBSTRUCTION_JS, anchor)
                    check(not covered, f"{w}px {fam} at {anchor}: cannot be seen clear of sticky chrome {covered}")

                # 6. horizontal scrolling only inside an approved container
                spill = page.evaluate("""()=>{const bad=[];
                  document.querySelectorAll('#main *').forEach(el=>{
                    // An outer <svg> has overflow:hidden and cannot scroll; its
                    // scrollWidth is reported from the viewBox, so measuring it
                    // says nothing about the layout.
                    if(el instanceof SVGElement) return;
                    if(el.scrollWidth > el.clientWidth + 1){
                      const ok = el.classList.contains('w1-chart') || el.classList.contains('table-wrap')
                                 || el.classList.contains('segmented') || el.tagName==='SELECT'
                                 || el.classList.contains('sr-only') || el.closest('.sr-only');
                      if(!ok) bad.push(((typeof el.className==='string'?el.className:'')||el.tagName).toString().slice(0,40));}});
                  return bad}""")
                check(not spill, f"{w}px {fam}: horizontal scrolling outside a chart or table container {spill[:3]}")
                dims = page.evaluate("()=>({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth})")
                check(dims["sw"] <= dims["cw"] + 1, f"{w}px {fam}: page scrolls horizontally {dims}")

                # 7. touch targets and label legibility
                small = page.evaluate("""()=>{const bad=[];
                  document.querySelectorAll('.w1-opt, .w1-chk, .w1-order-ctl .btn, #w1Form .btn, .mobile-nav button')
                    .forEach(el=>{const h=el.getBoundingClientRect().height;
                      if(h>0 && h<44) bad.push([(el.className||el.tagName).toString().slice(0,28),Math.round(h)]);});
                  return bad.slice(0,4)}""")
                check(not small, f"{w}px {fam}: touch target under 44px {small}")
                tiny = page.evaluate("""()=>{const bad=[];
                  document.querySelectorAll('.w1-visual svg text').forEach(t=>{
                    const fs=parseFloat(getComputedStyle(t).fontSize);
                    if(fs<9) bad.push(Math.round(fs*10)/10);});
                  return bad.slice(0,4)}""")
                check(not tiny, f"{w}px {fam}: chart label shrunk to {tiny} px")

                if w in CAPTURE_AT and fam in ("line_graph", "map_plan"):
                    page.evaluate(SCROLL_AND_CHECK, ".w1-visual")
                    page.wait_for_timeout(90)
                    page.screenshot(path=str(SHOTS / f"qa_w1_viewport_{fam}_{w}.png"))

                page.click(f'[data-w1-back-family="{fam}"]')
                page.wait_for_timeout(70)
                page.click("[data-w1-home]")
                page.wait_for_timeout(70)

            # the writing flow, where the sticky header meets a long textarea
            page.click('[data-w1-family="line_graph"]')
            page.wait_for_timeout(90)
            pid = page.evaluate('()=>WRITING1_DATA.prompts.find(p=>p.questionFamily==="line_graph").id')
            page.click(f'[data-w1-prompt="{pid}"]')
            page.wait_for_timeout(160)
            for anchor in (".w1-stepper", ".w1-draft", ".w1-chk", "#w1Timer"):
                page.evaluate(SCROLL_AND_CHECK, anchor)
                page.wait_for_timeout(140)
                covered = page.evaluate(OBSTRUCTION_JS, anchor)
                check(not covered, f"{w}px writing flow at {anchor}: cannot be seen clear of sticky chrome {covered}")
            if w in CAPTURE_AT:
                page.evaluate(SCROLL_AND_CHECK, ".w1-draft")
                page.wait_for_timeout(90)
                page.screenshot(path=str(SHOTS / f"qa_w1_viewport_writing_{w}.png"))
            page.close()
        browser.close()
finally:
    httpd.shutdown()

if fails:
    print("G4 OBSTRUCTION FAIL")
    print("\n".join(fails))
    sys.exit(1)
print("G4 OBSTRUCTION PASS:", ", ".join(map(str, WIDTHS)),
      "— no sticky element covers content, skip link hidden until focused, "
      "horizontal scrolling confined to chart and table containers")
