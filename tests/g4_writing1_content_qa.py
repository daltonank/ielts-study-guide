#!/usr/bin/env python3
"""Content QA for G4: check the prose claims the structural validator cannot.

tests/g4_writing1_validation.py proves every FIGURE is derivable from its
visual. It cannot prove that a sentence like "less than a third" or "the
largest single step in the ranking" is TRUE. This script re-derives each such
claim from the data and asserts it, one sampled item per visual family plus
every quantified claim in the model responses that involves arithmetic.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
raw = (ROOT / "web" / "writing1_data.js").read_text(encoding="utf-8")
data = json.loads(re.search(r"window\.WRITING1_DATA=(\{.*\});\s*$", raw, re.S).group(1))
V = {v["id"]: v for v in data["visuals"]}
X = {e["id"]: e for e in data["exercises"]}
P = {p["id"]: p for p in data["prompts"]}

results = []


def check(label, cond, detail=""):
    results.append((label, bool(cond), detail))


def series(vid, name):
    v = V[vid]
    s = next(s for s in v["series"] if s["name"] == name)
    return dict(zip(v["categories"], s["values"]))


def comp_series(vid, ci, name):
    c = V[vid]["components"][ci]
    s = next(s for s in c["series"] if s["name"] == name)
    return dict(zip(c["categories"], s["values"]))


def slices(vid, snap, ci=None):
    v = V[vid] if ci is None else V[vid]["components"][ci]
    sn = next(s for s in v["snapshots"] if s["label"] == snap)
    return {x["label"]: x["value"] for x in sn["slices"]}


def rows(vid, ci=None):
    v = V[vid] if ci is None else V[vid]["components"][ci]
    return {r["label"]: dict(zip(v["columns"], r["cells"])) for r in v["rows"]}


# ---------------- LINE GRAPH ----------------
t = series("W1V-LINE-01", "Tromso")
check("LINE-01 W1X-LINE-04 'more than tripling'", t["2025"] > 3 * t["2005"],
      f"{t['2025']} vs 3x{t['2005']}={3*t['2005']}")
check("LINE-01 model 'more than three times its opening figure'", t["2025"] > 3 * t["2005"])
o, b = series("W1V-LINE-01", "Oslo"), series("W1V-LINE-01", "Bergen")
check("LINE-01 model 'Bergen began slightly ahead ... order had reversed'",
      b["2005"] > o["2005"] and o["2025"] > b["2025"],
      f"2005 {b['2005']}>{o['2005']}; 2025 {o['2025']}>{b['2025']}")
check("LINE-01 W1X-LINE-01 'Tromso overtook both by 2015'",
      t["2015"] > o["2015"] and t["2015"] > b["2015"] and t["2010"] < min(o["2010"], b["2010"]))
check("LINE-01 W1X-LINE-04 'never levels off / no reversal'",
      all(t[a] < t[c] for a, c in zip(["2005", "2010", "2015", "2020"], ["2010", "2015", "2020", "2025"])))

n, r_, e = (series("W1V-LINE-02", k) for k in ("Northgate", "Riverside", "Eastfield"))
check("LINE-02 W1X-LINE-05 'Riverside and Northgate both gained exactly 6'",
      (r_["2024"] - r_["2010"]) == (n["2024"] - n["2010"]) == 6)
check("LINE-02 W1X-LINE-05 'Riverside grew more proportionally'",
      (r_["2024"] / r_["2010"]) > (n["2024"] / n["2010"]))
check("LINE-02 W1X-LINE-05 '2020 is not a plotted year'", "2020" not in V["W1V-LINE-02"]["categories"])
check("LINE-02 W1X-LINE-05 'Northgate not largest throughout'", e["2010"] > n["2010"])
check("LINE-02 crossover is between 2018 and 2022",
      e["2018"] > r_["2018"] and r_["2022"] > e["2022"])
check("LINE-02 W1X-LINE-07 'peak 19 then dip then partial recovery'",
      n["2018"] == max(n.values()) and n["2022"] < n["2018"] and n["2018"] > n["2024"] > n["2022"])
check("LINE-02 W1X-LINE-07 'not a doubling to 2018'", n["2018"] < 2 * n["2010"])
check("LINE-02 model 'largest in 2010 finished smallest'",
      max(("Eastfield", e["2010"]), ("Riverside", r_["2010"]), ("Northgate", n["2010"]), key=lambda x: x[1])[0] == "Eastfield"
      and min(("Eastfield", e["2024"]), ("Riverside", r_["2024"]), ("Northgate", n["2024"]), key=lambda x: x[1])[0] == "Eastfield")
check("LINE-02 model 'smallest finished in the middle'",
      min(("Eastfield", e["2010"]), ("Riverside", r_["2010"]), ("Northgate", n["2010"]), key=lambda x: x[1])[0] == "Riverside"
      and e["2024"] < r_["2024"] < n["2024"])

h, w, s_ = (series("W1V-LINE-03", k) for k in ("Hydroelectric", "Wind", "Solar"))
check("LINE-03 W1X-LINE-08 'wind crossed hydro between 2010 and 2015'",
      w["2010"] < h["2010"] and w["2015"] > h["2015"])
check("LINE-03 W1X-LINE-09 'rose by 66, to 68'", w["2020"] - w["2000"] == 66 and w["2020"] == 68)
check("LINE-03 model 'hydro stayed in a narrow band'", max(h.values()) - min(h.values()) <= 3)
check("LINE-03 model 'solar passed hydro in the final years'",
      s_["2015"] < h["2015"] and s_["2020"] > h["2020"])
check("LINE-03 model 'wind comfortably the largest of the three'",
      w["2020"] > s_["2020"] and w["2020"] > h["2020"])

# ---------------- BAR CHART ----------------
eat = series("W1V-BAR-01", "Eating out")
live = series("W1V-BAR-01", "Live events")
cult = series("W1V-BAR-01", "Cultural visits")
strm = series("W1V-BAR-01", "Streaming services")
groups = V["W1V-BAR-01"]["categories"]
check("BAR-01 'eating out highest in every group'",
      all(eat[g] > max(live[g], cult[g], strm[g]) for g in groups))
check("BAR-01 'cultural visits the only category that rises with age'",
      cult["50 and over"] > cult["18-29"]
      and eat["50 and over"] < eat["18-29"]
      and live["50 and over"] < live["18-29"]
      and strm["50 and over"] < strm["18-29"])
check("BAR-01 'cultural overtakes live events in the oldest group'",
      cult["50 and over"] > live["50 and over"] and cult["18-29"] < live["18-29"])
check("BAR-01 W1X-BAR-04 'live events ends at less than a third of youngest'",
      live["50 and over"] < live["18-29"] / 3, f"{live['50 and over']} < {live['18-29']/3:.2f}")
check("BAR-01 model 'cultural ends second largest in oldest group'",
      sorted([eat["50 and over"], live["50 and over"], cult["50 and over"], strm["50 and over"]], reverse=True)[1]
      == cult["50 and over"])

cyc = series("W1V-BAR-02", "Cycle to work")
cities = V["W1V-BAR-02"]["categories"]
vals = [cyc[c] for c in cities]
gaps = [vals[i] - vals[i + 1] for i in range(len(vals) - 1)]
check("BAR-02 'cities are in descending order'", vals == sorted(vals, reverse=True))
check("BAR-02 W1X-BAR-05 'Copenhagen-Munich is the widest adjacent gap'",
      gaps[1] == max(gaps), f"gaps={gaps}")
check("BAR-02 W1X-BAR-05 'Dublin and Naples NOT almost identical'", cyc["Dublin"] > 2 * cyc["Naples"])
check("BAR-02 model 'Munich less than half the Amsterdam figure'", cyc["Munich"] < cyc["Amsterdam"] / 2)
check("BAR-02 model 'Naples roughly a twelfth of Amsterdam'",
      abs(cyc["Naples"] - cyc["Amsterdam"] / 12) < 0.51, f"{cyc['Naples']} vs {cyc['Amsterdam']/12:.2f}")
check("BAR-02 model 'only Amsterdam and Copenhagen approach half'",
      cyc["Amsterdam"] > 40 and cyc["Copenhagen"] > 40 and cyc["Munich"] < 40)

road = series("W1V-BAR-03", "Road")
rail = series("W1V-BAR-03", "Rail")
water = series("W1V-BAR-03", "Water")
air = series("W1V-BAR-03", "Air")
check("BAR-03 'rail the only mode to fall'",
      rail["2020"] < rail["1990"] and all(m["2020"] > m["1990"] for m in (road, water, air)))
check("BAR-03 W1X-BAR-07 'rail shed 70'", rail["1990"] - rail["2020"] == 70)
check("BAR-03 W1X-BAR-07 'rail did NOT halve'", rail["2020"] > rail["1990"] / 2)
check("BAR-03 W1X-BAR-07 'rail NOT smallest in 2020'", rail["2020"] > air["2020"])
check("BAR-03 model 'road increase 360 exceeds any other mode in either year'",
      (road["2020"] - road["1990"]) == 360
      and 360 > max(rail["1990"], rail["2020"], water["1990"], water["2020"], air["1990"], air["2020"]))
check("BAR-03 model 'air quadrupled'", air["2020"] == 4 * air["1990"])
check("BAR-03 model 'rail lost second place to water'",
      rail["1990"] > water["1990"] and water["2020"] > rail["2020"])
check("BAR-03 W1X-BAR-09 'road the largest share in both years'",
      road["1990"] == max(road["1990"], rail["1990"], water["1990"], air["1990"])
      and road["2020"] == max(road["2020"], rail["2020"], water["2020"], air["2020"]))

# ---------------- PIE CHART ----------------
w24 = slices("W1V-PIE-01", "2024")
check("PIE-01 sums to 100", sum(w24.values()) == 100)
check("PIE-01 W1X-PIE-01 'bathing + flushing well over half'",
      w24["Bathing and showering"] + w24["Toilet flushing"] > 55)
check("PIE-01 model 'those two are three fifths'",
      w24["Bathing and showering"] + w24["Toilet flushing"] == 60)
check("PIE-01 model 'kitchen less than half the flushing share'",
      w24["Kitchen and drinking"] < w24["Toilet flushing"] / 2)
check("PIE-01 model 'other roughly an eighth of the largest'",
      abs(w24["Other"] - w24["Bathing and showering"] / 8) <= 0.5,
      f"{w24['Other']} vs {w24['Bathing and showering']/8:.2f}")
check("PIE-01 W1X-PIE-07 'bathing just over a third'", 33.4 <= w24["Bathing and showering"] <= 36)
check("PIE-01 W1X-PIE-07 'bathing is the single largest'",
      w24["Bathing and showering"] == max(w24.values()))

p00, p20 = slices("W1V-PIE-02", "2000"), slices("W1V-PIE-02", "2020")
check("PIE-02 both snapshots sum to 100", sum(p00.values()) == 100 and sum(p20.values()) == 100)
check("PIE-02 'organic largest in both, but loses share'",
      p00["Organic"] == max(p00.values()) and p20["Organic"] == max(p20.values())
      and p20["Organic"] < p00["Organic"])
check("PIE-02 'plastics becomes second largest'",
      sorted(p20.values(), reverse=True)[1] == p20["Plastics"]
      and sorted(p00.values(), reverse=True)[1] == p00["Paper"])
check("PIE-02 W1X-PIE-04 'plastics more than doubled, +14 points'",
      p20["Plastics"] > 2 * p00["Plastics"] and p20["Plastics"] - p00["Plastics"] == 14)
check("PIE-02 W1X-PIE-03 'exactly three categories moved 9 points or more'",
      sorted(abs(p20[k] - p00[k]) for k in p00)[-3:] == [9, 11, 14])
check("PIE-02 model 'paper fell more steeply than organic in proportional terms'",
      (p00["Paper"] - p20["Paper"]) / p00["Paper"] > (p00["Organic"] - p20["Organic"]) / p00["Organic"])
check("PIE-02 model 'none of glass, metal, other shifted by more than four points'",
      all(abs(p20[k] - p00[k]) <= 4 for k in ("Glass", "Metal", "Other")))
check("PIE-02 'composition became more even (lower spread)'",
      (max(p20.values()) - min(p20.values())) < (max(p00.values()) - min(p00.values())))

pg = slices("W1V-PIE-03", "2024")
check("PIE-03 sums to 100", sum(pg.values()) == 100)
check("PIE-03 W1X-PIE-05 'career advancement well over a third'", pg["Career advancement"] > 34)
check("PIE-03 W1X-PIE-05 'career NOT more than 3x sponsorship'",
      pg["Career advancement"] < 3 * pg["Employer sponsorship"])
check("PIE-03 W1X-PIE-05 'family + other NOT more than a fifth'",
      pg["Family expectation"] + pg["Other"] < 20)
check("PIE-03 model 'top two well over half'",
      pg["Career advancement"] + pg["Interest in the subject"] > 55)
check("PIE-03 model 'gap between first and second is 14 points'",
      pg["Career advancement"] - pg["Interest in the subject"] == 14)
check("PIE-03 model 'two smallest are around an eighth'",
      abs((pg["Family expectation"] + pg["Other"]) - 100 / 8) <= 0.5)

# ---------------- TABLE ----------------
t1 = rows("W1V-TAB-01")
a19, a23 = "Arrivals 2019 (m)", "Arrivals 2023 (m)"
s19, s23 = "Stay 2019 (nights)", "Stay 2023 (nights)"
check("TAB-01 'Riverford the only destination to lose arrivals'",
      [k for k in t1 if t1[k][a23] < t1[k][a19]] == ["Riverford"])
check("TAB-01 'Highland Park the only stay to rise'",
      [k for k in t1 if t1[k][s23] > t1[k][s19]] == ["Highland Park"])
check("TAB-01 W1X-TAB-04 'Riverford fell by 0.8'",
      abs((t1["Riverford"][a19] - t1["Riverford"][a23]) - 0.8) < 1e-9)
check("TAB-01 model 'Old Harbour busiest in both years'",
      t1["Old Harbour"][a19] == max(r[a19] for r in t1.values())
      and t1["Old Harbour"][a23] == max(r[a23] for r in t1.values()))
check("TAB-01 model 'Highland Park smallest throughout'",
      t1["Highland Park"][a19] == min(r[a19] for r in t1.values())
      and t1["Highland Park"][a23] == min(r[a23] for r in t1.values()))
check("TAB-01 model 'Coastal Bay the largest stay reduction'",
      max(t1, key=lambda k: t1[k][s19] - t1[k][s23]) == "Coastal Bay")
check("TAB-01 model 'Highland Park retains the longest stay'",
      t1["Highland Park"][s23] == max(r[s23] for r in t1.values()))

t2 = rows("W1V-TAB-02")
check("TAB-02 W1X-TAB-05 'Northvale below 100 on all four'",
      all(x < 100 for x in t2["Northvale"].values()))
check("TAB-02 W1X-TAB-05 'Metroport above on housing+food, below on transport+utilities'",
      t2["Metroport"]["Housing"] > 100 and t2["Metroport"]["Food"] > 100
      and t2["Metroport"]["Transport"] < 100 and t2["Metroport"]["Utilities"] < 100)
check("TAB-02 W1X-TAB-05 'Metroport housing NOT more than twice Northvale'",
      t2["Metroport"]["Housing"] < 2 * t2["Northvale"]["Housing"])
check("TAB-02 W1X-TAB-06 'Northvale has the lowest transport index'",
      t2["Northvale"]["Transport"] == min(r["Transport"] for r in t2.values()))
check("TAB-02 model 'Southcliff has the highest transport index'",
      t2["Southcliff"]["Transport"] == max(r["Transport"] for r in t2.values()))
check("TAB-02 model 'Rivergate has the highest utilities'",
      t2["Rivergate"]["Utilities"] == max(r["Utilities"] for r in t2.values()))
check("TAB-02 model 'food varies least across the four cities'",
      (lambda sp: sp["Food"] == min(sp.values()))(
          {c: max(r[c] for r in t2.values()) - min(r[c] for r in t2.values())
           for c in V["W1V-TAB-02"]["columns"]}))

t3 = rows("W1V-TAB-03")
yrs = V["W1V-TAB-03"]["columns"]
check("TAB-03 every column sums to 100",
      all(sum(t3[k][y] for k in t3) == 100 for y in yrs))
check("TAB-03 'services largest in every year'",
      all(t3["Services"][y] == max(t3[k][y] for k in t3) for y in yrs))
check("TAB-03 'services grows at every reading'",
      all(t3["Services"][yrs[i]] < t3["Services"][yrs[i + 1]] for i in range(len(yrs) - 1)))
check("TAB-03 W1X-TAB-07 'services rose by 24 points'",
      t3["Services"]["2025"] - t3["Services"]["1995"] == 24)
check("TAB-03 W1X-TAB-07 'services was ALREADY largest in 1995'",
      t3["Services"]["1995"] == max(t3[k]["1995"] for k in t3))
check("TAB-03 W1X-TAB-07 '44 is not around two thirds'",
      abs(t3["Services"]["1995"] / 100 - 2 / 3) > 0.15)
check("TAB-03 model 'manufacturing lost roughly half its share'",
      abs(t3["Manufacturing"]["2025"] - t3["Manufacturing"]["1995"] / 2) <= 2)
check("TAB-03 model 'agriculture fell further proportionally than manufacturing'",
      (t3["Agriculture"]["1995"] - t3["Agriculture"]["2025"]) / t3["Agriculture"]["1995"]
      > (t3["Manufacturing"]["1995"] - t3["Manufacturing"]["2025"]) / t3["Manufacturing"]["1995"])
check("TAB-03 model 'agriculture ends smallest, having begun ahead of public admin'",
      t3["Agriculture"]["2025"] == min(t3[k]["2025"] for k in t3)
      and t3["Agriculture"]["1995"] > t3["Public administration"]["1995"])
check("TAB-03 model 'public administration is the only other riser'",
      t3["Public administration"]["2025"] > t3["Public administration"]["1995"])

# ---------------- PROCESS ----------------
pr = V["W1V-PROC-01"]
check("PROC-01 'eight stages, cyclical'", len(pr["stages"]) == 8 and pr["cyclical"] is True)
check("PROC-01 W1X-PROC-03 'split at 1-5 prepare / 6-8 remanufacture'",
      pr["stages"][0]["label"] == "Collection" and pr["stages"][4]["label"] == "Crushing"
      and pr["stages"][5]["label"] == "Melting" and pr["stages"][7]["label"] == "Distribution")
check("PROC-01 'no temperature or duration is stated anywhere'",
      not re.search(r"\d+\s*(°|degrees|celsius|minutes|hours)", json.dumps(pr), re.I))
sal = V["W1V-PROC-02"]
check("PROC-02 'six stages, cyclical, no durations given'",
      len(sal["stages"]) == 6 and sal["cyclical"] is True
      and not re.search(r"\b\d+\s*(years|months|days)\b", json.dumps(sal), re.I))
check("PROC-02 W1X-PROC-05 'alevin and fry are separate stages'",
      {s["label"] for s in sal["stages"]} >= {"Alevin", "Fry"})
rw = V["W1V-PROC-03"]
check("PROC-03 'seven stages, NOT cyclical'", len(rw["stages"]) == 7 and rw["cyclical"] is False)
check("PROC-03 W1X-PROC-08 'disinfection is a later stage than storage'",
      [s["n"] for s in rw["stages"] if "Storage" in s["label"]][0]
      < [s["n"] for s in rw["stages"] if "Ultraviolet" in s["label"]][0])

# ---------------- MAP ----------------
wm = {f["label"]: f for f in V["W1V-MAP-01"]["features"]}
check("MAP-01 'woodland and school unchanged'",
      wm["Woodland"]["status"] == "unchanged" and wm["Primary school"]["status"] == "unchanged")
check("MAP-01 'shop is replaced, not removed'", wm["Village shop"]["status"] == "replaced")
check("MAP-01 'farmland removed and housing added, both in the south'",
      wm["Farmland"]["status"] == "removed" and wm["Housing estate"]["status"] == "added"
      and wm["Farmland"]["area"] == wm["Housing estate"]["area"] == "south")
check("MAP-01 'bypass added on the eastern edge'",
      wm["Bypass road"]["status"] == "added" and "eastern" in wm["Bypass road"]["area"])
lib = {f["label"]: f for f in V["W1V-MAP-02"]["features"]}
check("MAP-02 W1X-MAP-05 'reading room and staircase both retained'",
      lib["Silent reading room"]["status"] == "unchanged" and lib["Main staircase"]["status"] == "unchanged")
check("MAP-02 W1X-MAP-05 'cafe is an addition, issue desk a replacement'",
      lib["Cafe"]["status"] == "added" and lib["Issue desk"]["status"] == "replaced")
check("MAP-02 W1X-MAP-07 'journal stacks removed, pods added, same wing'",
      lib["Print journal stacks"]["status"] == "removed" and lib["Group study pods"]["status"] == "added"
      and lib["Print journal stacks"]["area"] == lib["Group study pods"]["area"])
res = {f["label"]: f for f in V["W1V-MAP-03"]["features"]}
check("MAP-03 'harbour and footpath unchanged'",
      res["Fishing harbour"]["status"] == "unchanged" and res["Coastal footpath"]["status"] == "unchanged")
check("MAP-03 'caravan park removed, hotel added, both east'",
      res["Caravan park"]["status"] == "removed" and res["Hotel complex"]["status"] == "added"
      and res["Caravan park"]["area"] == res["Hotel complex"]["area"] == "east")

# ---------------- MIXED ----------------
cons = comp_series("W1V-MIX-01", 0, "Total consumption")
mix = slices("W1V-MIX-01", "2024", ci=1)
check("MIX-01 pie sums to 100", sum(mix.values()) == 100)
check("MIX-01 'renewables the largest single source'", mix["Renewables"] == max(mix.values()))
check("MIX-01 W1X-MIX-04 'virtually flat between 2019 and 2024'",
      cons["2024"] - cons["2019"] <= 5, f"{cons['2019']} -> {cons['2024']}")
check("MIX-01 'growth before 2019 is much larger than after'",
      (cons["2019"] - cons["2010"]) > 10 * (cons["2024"] - cons["2019"]))
check("MIX-01 model 'increase to 2019 is around a fifth'",
      abs((cons["2019"] - cons["2010"]) / cons["2010"] - 0.2) < 0.02)

rail_t = rows("W1V-MIX-02", ci=0)
sat = comp_series("W1V-MIX-02", 1, "Satisfied")
c18, c23 = "2018 (m)", "2023 (m)"
gained = [k for k in rail_t if rail_t[k][c23] > rail_t[k][c18]]
top2 = sorted(sat, key=lambda k: -sat[k])[:2]
check("MIX-02 W1X-MIX-05 'the two gaining lines are the two most satisfied'",
      set(gained) == set(top2), f"gained={gained} top2={top2}")
check("MIX-02 'City Loop is busiest, and NOT the lowest satisfaction'",
      rail_t["City Loop"][c18] == max(r[c18] for r in rail_t.values())
      and sat["City Loop"] > sat["Northern Line"])
check("MIX-02 W1X-MIX-06 'Coastal Line rose by 3.7'",
      abs((rail_t["Coastal Line"][c23] - rail_t["Coastal Line"][c18]) - 3.7) < 1e-9)
check("MIX-02 'satisfaction is given for 2023 only'",
      V["W1V-MIX-02"]["components"][1]["title"].endswith("2023"))

emp = comp_series("W1V-MIX-03", 0, "In work")
dest = slices("W1V-MIX-03", "2024", ci=1)
check("MIX-03 pie sums to 100", sum(dest.values()) == 100)
check("MIX-03 'health highest, humanities lowest'",
      emp["Health"] == max(emp.values()) and emp["Humanities"] == min(emp.values()))
check("MIX-03 model 'humanities roughly twenty-four points below the leader'",
      abs((emp["Health"] - emp["Humanities"]) - 24) <= 1)
check("MIX-03 model 'top three separated by only a few points'",
      max(emp["Health"], emp["Computing"], emp["Engineering"])
      - min(emp["Health"], emp["Computing"], emp["Engineering"]) <= 5)
check("MIX-03 W1X-MIX-08 '68 per cent is a clear majority'", emp["Humanities"] > 50)
check("MIX-03 model 'just over half entered full-time employment'",
      50 < dest["Full-time employment"] <= 60)

# ---------------- report ----------------
print("G4 CONTENT QA — PROSE CLAIMS RE-DERIVED FROM DATA")
print("=" * 52)
fails = [(l, d) for l, ok, d in results if not ok]
for label, ok, detail in results:
    if not ok:
        print(f"FAIL: {label} {('· ' + detail) if detail else ''}")
print(f"Claims checked: {len(results)}")
print(f"Failed: {len(fails)}")
sys.exit(1 if fails else 0)
