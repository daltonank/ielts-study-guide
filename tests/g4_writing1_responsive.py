#!/usr/bin/env python3
"""G4 Writing Task 1 responsive validation at the six approved widths.

VALIDATION_SPEC.md section 6 and UX_DESIGN_SPEC.md section 18: the new
chart/visual surfaces must stay interpretable on a phone, must not overflow the
page horizontally, must not shrink data labels to illegibility, and must keep
touch targets usable. Where a visual genuinely cannot compress, it is allowed to
scroll inside its own container rather than clipping or shrinking.
"""
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent))
from browser_env import launch_chromium, describe

ROOT = Path(__file__).resolve().parents[1] / 'web'
SHIM = ("<script>const __ls={};Object.defineProperty(window,'localStorage',{value:{"
        "getItem:k=>Object.prototype.hasOwnProperty.call(__ls,k)?__ls[k]:null,"
        "setItem:(k,v)=>{__ls[k]=String(v)},removeItem:k=>{delete __ls[k]},"
        "clear:()=>{Object.keys(__ls).forEach(k=>delete __ls[k])}}});</script>")
html = (ROOT / 'index.html').read_text(encoding='utf-8').replace('<head>', '<head>' + SHIM)
for name in ['styles.css', 'vocabulary.js', 'data.js', 'reading_data.js', 'writing1_data.js', 'app.js']:
    content = (ROOT / name).read_text(encoding='utf-8')
    if name == 'styles.css':
        html = html.replace('<link rel="stylesheet" href="styles.css">', f'<style>{content}</style>')
    else:
        html = html.replace(f'<script src="{name}"></script>', f'<script>{content}</script>')

WIDTHS = [320, 375, 430, 768, 1024, 1440]
# One exercise per visual family, so every rendering path is measured.
FAMILIES = ['line_graph', 'bar_chart', 'pie_chart', 'table', 'process_diagram', 'map_plan', 'mixed_visual']
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def overflow(page, where):
    d = page.evaluate('()=>({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth})')
    check(d['sw'] <= d['cw'] + 1, f'{where}: horizontal overflow {d}')


with sync_playwright() as p:
    browser = launch_chromium(p)
    for w in WIDTHS:
        page = browser.new_page(viewport={'width': w, 'height': 900})
        page.set_content(html, wait_until='load')
        page.wait_for_timeout(120)
        page.click('#menuBtn')
        page.click('#secondaryNav button[data-route="task1"]')
        page.wait_for_timeout(90)
        overflow(page, f'{w}px family list')
        check(page.locator('.family-card').count() == 7, f'{w}px: family cards missing')

        for fam in FAMILIES:
            page.click(f'[data-w1-family="{fam}"]')
            page.wait_for_timeout(70)
            overflow(page, f'{w}px {fam} module')
            first = page.evaluate('(f)=>WRITING1_DATA.exercises.find(e=>e.questionFamily===f).id', fam)
            page.click(f'[data-w1-exercise="{first}"]')
            page.wait_for_timeout(90)
            overflow(page, f'{w}px {fam} exercise')

            # The visual must be present and must not be clipped by its panel.
            check(page.locator('.w1-visual').count() == 1, f'{w}px {fam}: no visual panel')
            clipped = page.evaluate('''()=>{const out=[];
              document.querySelectorAll('.w1-visual svg').forEach(s=>{
                const r=s.getBoundingClientRect();
                if(r.width<40||r.height<40) out.push([Math.round(r.width),Math.round(r.height)]);});
              return out}''')
            check(not clipped, f'{w}px {fam}: visual collapsed {clipped}')

            # Data labels must stay legible. Charts are allowed to scroll inside
            # their own container rather than shrinking below that floor.
            small = page.evaluate('''()=>{const bad=[];
              document.querySelectorAll('.w1-visual svg text').forEach(t=>{
                const fs=parseFloat(getComputedStyle(t).fontSize);
                if(fs<9) bad.push(Math.round(fs*10)/10);});
              return bad.slice(0,5)}''')
            check(not small, f'{w}px {fam}: data labels shrunk to {small} px')

            # Anything wider than its box must be in a scroll container, not clipped.
            spill = page.evaluate('''()=>{const bad=[];
              document.querySelectorAll('.w1-visual svg, .w1-visual table').forEach(el=>{
                let n=el.parentElement,scrollable=false;
                while(n&&!n.classList.contains('w1-visual')){
                  if(['auto','scroll'].includes(getComputedStyle(n).overflowX)){scrollable=true;break}
                  n=n.parentElement}
                const box=el.closest('.w1-visual').getBoundingClientRect();
                const r=el.getBoundingClientRect();
                if(r.right>box.right+1&&!scrollable) bad.push(el.tagName);});
              return bad}''')
            check(not spill, f'{w}px {fam}: content spills its panel without a scroll container {spill}')

            # Touch targets on the answer controls.
            short = page.evaluate('''()=>{const bad=[];
              document.querySelectorAll('.w1-opt, .w1-chk, .w1-order-ctl .btn, #w1Form .btn').forEach(el=>{
                const h=el.getBoundingClientRect().height;
                if(h>0&&h<40) bad.push([el.className,Math.round(h)]);});
              return bad.slice(0,4)}''')
            check(not short, f'{w}px {fam}: answer control under practical touch size {short}')

            page.click(f'[data-w1-back-family="{fam}"]')
            page.wait_for_timeout(50)
            page.click('[data-w1-home]')
            page.wait_for_timeout(50)

        # The writing flow, which carries the timer and the long textarea.
        page.click('[data-w1-family="line_graph"]')
        page.wait_for_timeout(60)
        pid = page.evaluate('()=>WRITING1_DATA.prompts.find(p=>p.questionFamily==="line_graph").id')
        page.click(f'[data-w1-prompt="{pid}"]')
        page.wait_for_timeout(100)
        overflow(page, f'{w}px writing flow')
        check(page.locator('#w1Timer').count() == 1, f'{w}px: writing timer missing')
        ta = page.evaluate('()=>{const t=document.querySelector(".w1-draft");const r=t.getBoundingClientRect();'
                           'return {h:Math.round(r.height),w:Math.round(r.width),fs:parseFloat(getComputedStyle(t).fontSize)}}')
        check(ta['h'] >= 120, f'{w}px: draft textarea too short {ta}')
        check(ta['fs'] >= 15, f'{w}px: draft text too small {ta}')
        page.fill(f'[data-w1-draft="{pid}"]', 'The line graph compares recycling rates. ' * 20)
        page.wait_for_timeout(80)
        overflow(page, f'{w}px writing flow with a long draft')
        page.close()
    browser.close()

if fails:
    print('G4 WRITING TASK 1 RESPONSIVE FAIL')
    print('\n'.join(fails))
    sys.exit(1)
print('G4 WRITING TASK 1 RESPONSIVE PASS:', ', '.join(map(str, WIDTHS)))
