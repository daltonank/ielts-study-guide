#!/usr/bin/env python3
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent))
from browser_env import launch_chromium, describe
ROOT=Path(__file__).resolve().parents[1]/'web'
html=(ROOT/'index.html').read_text(encoding='utf-8')
shim="<script>const __ls={};Object.defineProperty(window,'localStorage',{value:{getItem:k=>Object.prototype.hasOwnProperty.call(__ls,k)?__ls[k]:null,setItem:(k,v)=>{__ls[k]=String(v)},removeItem:k=>{delete __ls[k]},clear:()=>{Object.keys(__ls).forEach(k=>delete __ls[k])}}});</script>"
html=html.replace('<head>','<head>'+shim)
for name in ['styles.css','vocabulary.js','data.js','reading_data.js','app.js']:
    content=(ROOT/name).read_text(encoding='utf-8')
    if name=='styles.css': html=html.replace('<link rel="stylesheet" href="styles.css">',f'<style>{content}</style>')
    else: html=html.replace(f'<script src="{name}"></script>',f'<script>{content}</script>')
widths=[320,375,430,768,1024,1440]
fails=[]
with sync_playwright() as p:
    browser=launch_chromium(p)
    for w in widths:
        page=browser.new_page(viewport={'width':w,'height':900})
        page.set_content(html,wait_until='load');page.wait_for_timeout(60)
        page.click('#menuBtn');page.click('#secondaryNav button[data-route="reading"]');page.click('[data-reading-family="matching_headings"]');page.click('[data-reading-passage$="P04"]');page.wait_for_timeout(40)
        dims=page.evaluate('()=>({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth,font:parseFloat(getComputedStyle(document.querySelector(".reading-passage")).fontSize),controls:[...document.querySelectorAll(".reading-answer")].map(x=>x.getBoundingClientRect().height)})')
        if dims['sw']>dims['cw']+1:fails.append(f'{w}px horizontal overflow {dims}')
        if dims['font']<15.5:fails.append(f'{w}px reading font too small {dims["font"]}')
        if any(h<40 for h in dims['controls']):fails.append(f'{w}px answer control under practical touch size {dims["controls"]}')
        page.close()
    browser.close()
if fails:
    print('G3 READING RESPONSIVE FAIL')
    print('\n'.join(fails));sys.exit(1)
print('G3 READING RESPONSIVE PASS:',', '.join(map(str,widths)))
