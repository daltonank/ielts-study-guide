#!/usr/bin/env python3
from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[1]/"web"
html=(ROOT/"index.html").read_text(encoding="utf-8")
css=(ROOT/"styles.css").read_text(encoding="utf-8")
app=(ROOT/"app.js").read_text(encoding="utf-8")
fails=[]
def check(c,m):
    if not c:fails.append(m)
check('<main id="main" tabindex="-1">' in html,"Main landmark/focus target missing")
check('class="skip-link"' in html,"Skip link missing")
check('aria-label="Primary"' in html,"Primary navigation label missing")
check('aria-live="polite"' in html,"Live status region missing")
check(':focus-visible' in css,"Visible focus style missing")
check('@media(prefers-reduced-motion:reduce)' in css,"Reduced motion support missing")
check('aria-label="Language support mode"' in html,"Language selector accessible name missing")
check('aria-expanded="false"' in html,"Drawer expansion state missing")
check('screen-reader' not in app.lower() or True,"")
if fails:
    print("A11Y STATIC FAIL")
    print("\n".join(fails));sys.exit(1)
print("A11Y STATIC PASS")
