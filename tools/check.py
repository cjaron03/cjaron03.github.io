#!/usr/bin/env python3
"""Refuse to ship a broken index.html.

There is no build step here, so this runs against the file that actually
gets served. Six checks, each one a mistake that has already happened at
least once on the journal next door.

    python3 tools/check.py
"""
import re, shutil, subprocess, sys, tempfile
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "index.html"

fails: list[str] = []
notes: list[str] = []


def fail(what: str, detail: str) -> None:
    fails.append(f"{what}: {detail}")


if not PAGE.exists():
    print("FAILED (1)\n  missing: index.html")
    raise SystemExit(1)

s = PAGE.read_text(encoding="utf-8")


# ---- 1. no em dashes, anywhere -------------------------------------------
# a standing style rule for this project. the exemptions are the places a
# double hyphen is not punctuation: css custom properties, the js decrement,
# comment delimiters, section dividers and base64 payloads.
if s.count("—"):
    fail("em dash", f"index.html x{s.count(chr(0x2014))}")
t = re.sub(r"base64,[A-Za-z0-9+/=\s]+", "base64,X", s)
t = t.replace("<!--", "").replace("-->", "")
t = re.sub(r"/\*[^*]*?-{4,}.*?\*/", "", t, flags=re.S)
t = re.sub(r"//\s*-{3,}[^\n]*", "", t)
t = re.sub(r"--[A-Za-z][\w-]*", "VAR", t)
t = re.sub(r"\w--", "", t)
if re.findall(r"--", t):
    fail("double hyphen", f"index.html x{len(re.findall('--', t))}")


# ---- 2. the page is written in UK english --------------------------------
# only the prose is checked. css is full of color and center and behavior,
# and those are property names, not words, so the styles, the scripts and
# every attribute come out before anything is matched.
prose = re.sub(r"<(style|script)\b.*?</\1>", " ", s, flags=re.S | re.I)
prose = re.sub(r"<[^>]*>", " ", prose)

US = {
    "color": "colour", "colors": "colours", "colored": "coloured",
    "behavior": "behaviour", "behaviors": "behaviours",
    "behavioral": "behavioural",
    "center": "centre", "centers": "centres", "centered": "centred",
    "analyze": "analyse", "analyzed": "analysed", "analyzes": "analyses",
    "analyzing": "analysing", "analyzer": "analyser",
    "paralyze": "paralyse", "paralyzed": "paralysed",
    "catalog": "catalogue", "catalogs": "catalogues",
    "dialog": "dialogue", "dialogs": "dialogues",
    "defense": "defence", "offense": "offence",
    "favor": "favour", "favors": "favours", "favorite": "favourite",
    "favorites": "favourites", "favored": "favoured",
    "flavor": "flavour", "flavors": "flavours",
    "honor": "honour", "humor": "humour", "labor": "labour",
    "neighbor": "neighbour", "neighbors": "neighbours",
    "rumor": "rumour", "vapor": "vapour", "savor": "savour",
    "armor": "armour", "armored": "armoured",
    "endeavor": "endeavour",
    "meter": "metre", "meters": "metres",
    "kilometer": "kilometre", "kilometers": "kilometres",
    "centimeter": "centimetre", "centimeters": "centimetres",
    "liter": "litre", "liters": "litres",
    "fiber": "fibre", "fibers": "fibres",
    "theater": "theatre",
    "traveled": "travelled", "traveling": "travelling",
    "traveler": "traveller",
    "canceled": "cancelled", "canceling": "cancelling",
    "modeled": "modelled", "modeling": "modelling",
    "labeled": "labelled", "labeling": "labelling",
    "signaled": "signalled", "signaling": "signalling",
    "fueled": "fuelled", "fueling": "fuelling",
    "totaled": "totalled",
    "judgment": "judgement",
    "gray": "grey", "grayed": "greyed",
    "maneuver": "manoeuvre", "maneuvers": "manoeuvres",
    "skeptical": "sceptical", "skepticism": "scepticism",
    "mold": "mould", "molded": "moulded",
    "math": "maths",
}
for w in sorted(set(re.findall(r"[A-Za-z]+", prose.lower()))):
    if w in US:
        fail("us spelling", f"{w} (use {US[w]})")


# ---- 3. every relative reference resolves on disk -------------------------
# the icons and the card are referenced by relative path, so a missing file
# gives every tab a blank icon and every pasted link a blank card, while the
# page itself still looks perfectly fine locally.
for ref in sorted(set(re.findall(r'(?:href|src|content)="([^"]+)"', s))):
    if ref.startswith(("http://", "https://", "//", "#", "data:", "mailto:")):
        continue
    if not re.search(r"\.[A-Za-z0-9]{2,5}$", ref):
        continue                      # a description or an og value, not a path
    if not (ROOT / ref.split("?")[0]).exists():
        fail("missing file", f"index.html references {ref}")
for ph in re.findall(r"__[A-Z]+__", s):
    fail("placeholder left unfilled", ph)


# ---- 4. the page introduces itself ---------------------------------------
# without these the tab says index.html and every pasted link is a bare url.
need = [
    (r"<title>[^<]{3,}</title>", "<title>"),
    (r'<meta name="description" content="[^"]{40,}"', 'meta description'),
    (r'<meta property="og:title" content="[^"]{3,}"', "og:title"),
    (r'<meta property="og:description" content="[^"]{40,}"', "og:description"),
    (r'<meta property="og:url" content="https://[^"]+"', "og:url"),
    (r'<meta property="og:image" content="https://[^"]+"', "og:image"),
    (r'<meta property="og:type" content="[^"]+"', "og:type"),
    (r'<link rel="icon"', "favicon link"),
]
for pat, name in need:
    if not re.search(pat, s):
        fail("head incomplete", f"no {name}")

# og:image has to be absolute, because the machine reading it is not a
# browser and has no page to resolve a relative path against.
m = re.search(r'<meta property="og:image" content="([^"]+)"', s)
if m:
    u = urlparse(m.group(1))
    local = ROOT / u.path.lstrip("/")
    if not local.exists():
        fail("og:image missing", f"{m.group(1)} is not in the repo at {u.path}")


# ---- 5. the custom domain survived -----------------------------------------
# pages serves the site from whatever host the CNAME file names. lose that
# file and the domain silently reverts to the github.io address, while every
# og:url in the page keeps naming a host the site is no longer served from.
m = re.search(r'<meta property="og:url" content="([^"]+)"', s)
host = urlparse(m.group(1)).hostname if m else None
if host and not host.endswith(".github.io"):
    cname = ROOT / "CNAME"
    if not cname.exists():
        fail("missing CNAME", f"pages would fall back off {host}")
    elif cname.read_text(encoding="utf-8").strip() != host:
        fail("CNAME mismatch",
             f"{cname.read_text(encoding='utf-8').strip()} but og:url says {host}")

m = re.search(r'<link rel="canonical" href="([^"]+)"', s)
if m and host and urlparse(m.group(1)).hostname != host:
    fail("canonical mismatch", f"{m.group(1)} but og:url says {host}")


# ---- 6. every script block parses ------------------------------------------
# the script carries the scroll reveal, the glyph pausing and the live commit
# counts. if it throws on load the rows never arrive and the page is blank.
node = shutil.which("node")
if not node:
    notes.append("node not found, script syntax check skipped")
else:
    with tempfile.TemporaryDirectory() as tmp:
        for i, block in enumerate(re.findall(r"<script>(.*?)</script>", s, re.S)):
            p = Path(tmp) / f"block{i}.js"
            p.write_text(block, encoding="utf-8")
            r = subprocess.run([node, "--check", str(p)], capture_output=True, text=True)
            if r.returncode:
                fail("script syntax",
                     f"block {i}: {r.stderr.strip().splitlines()[0]}")


for n in notes:
    print(f"  note: {n}")
if fails:
    print(f"FAILED ({len(fails)})")
    for x in fails:
        print(f"  {x}")
    sys.exit(1)
print(f"checks passed (index.html, {len(s):,} bytes)")
