#!/usr/bin/env python3
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent))
from browser_env import launch_chromium, describe
ROOT=Path(__file__).resolve().parents[1]/"web"
widths=[320,375,430,768,1024,1440]
# Inline local assets so the sandboxed browser never navigates or fetches.
html=(ROOT/"index.html").read_text(encoding="utf-8")
css=(ROOT/"styles.css").read_text(encoding="utf-8")
vocab=(ROOT/"vocabulary.js").read_text(encoding="utf-8")
data=(ROOT/"data.js").read_text(encoding="utf-8")
reading=(ROOT/"reading_data.js").read_text(encoding="utf-8")
writing1=(ROOT/"writing1_data.js").read_text(encoding="utf-8")
app=(ROOT/"app.js").read_text(encoding="utf-8")
html=html.replace('<link rel="stylesheet" href="styles.css">',f'<style>{css}</style>')
html=html.replace('<script src="vocabulary.js"></script>',f'<script>{vocab}</script>')
html=html.replace('<script src="data.js"></script>',f'<script>{data}</script>')
html=html.replace('<script src="reading_data.js"></script>',f'<script>{reading}</script>')
html=html.replace('<script src="writing1_data.js"></script>',f'<script>{writing1}</script>')
html=html.replace('<script src="app.js"></script>',f'<script>{app}</script>')
fails=[]
with sync_playwright() as p:
    browser=launch_chromium(p)
    for w in widths:
      page=browser.new_page(viewport={"width":w,"height":900})
      page.set_content(html, wait_until="load")
      page.wait_for_timeout(80)
      dims=page.evaluate("()=>({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth,nav:document.querySelectorAll('.mobile-nav button').length,main:document.querySelector('#main')?.innerText.length||0})")
      if dims["sw"]>dims["cw"]+1:fails.append(f"{w}px horizontal overflow {dims}")
      if dims["nav"]!=5:fails.append(f"{w}px nav count {dims['nav']}")
      if dims["main"]<100:fails.append(f"{w}px main content did not render")
      page.select_option("#languageMode","uahelp")
      page.wait_for_timeout(20)
      if page.locator(".ua-note").count()<1:fails.append(f"{w}px UA Help rendered no Ukrainian support block")
      # open/close drawer keyboard-reachable control
      page.locator("#menuBtn").click()
      if page.locator("#drawer").get_attribute("hidden") is not None:fails.append(f"{w}px drawer failed to open")
      page.close()
    browser.close()
if fails:
  print("RESPONSIVE FAIL")
  print("\\n".join(fails));sys.exit(1)
print("RESPONSIVE PASS:",", ".join(map(str,widths)))
