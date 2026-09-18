#!/usr/bin/env python3
"""Refresh the commit tallies baked into index.html.

The page counts commits live, from the same GitHub endpoint this script
uses, but the numbers in the markup still matter: they are what a reader
sees before the fetch lands, what they keep if it fails, and what the
social card is drawn from. Left alone they drift.

Run from the repo root: python3 tools/counts.py
Then redraw the card, which reads its numbers back out of index.html:
python3 tools/art/make_assets.py
"""
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "index.html"

# the same four repos, in the same order, as the fetch on the page
REPO = [("frozen-dawn", "c-fd"), ("flare-plus", "c-fp"),
        ("canvas-and-clay", "c-cc"), ("Heart-Disease-Predictor", "c-hd")]

API = "https://api.github.com/repos/cjaron03/{}/commits?per_page=1&sha=main"


def tally(repo: str) -> int:
    """GitHub does not expose a commit count. Asking for one commit a page
    makes the number of the last page the count, and it arrives in the Link
    header, which is the trick the page itself uses."""
    req = urllib.request.Request(API.format(repo),
                                 headers={"Accept": "application/vnd.github+json",
                                          "User-Agent": "jaronc.com-counts"})
    with urllib.request.urlopen(req, timeout=20) as res:
        link = res.headers.get("Link") or ""
    m = re.search(r'[?&]page=(\d+)[^>]*>;\s*rel="last"', link)
    if not m:
        raise RuntimeError(f"{repo}: no last page in the Link header")
    return int(m.group(1))


def main() -> int:
    try:
        counts = {sid: tally(repo) for repo, sid in REPO}
    except (urllib.error.URLError, RuntimeError, TimeoutError) as e:
        # a wrong number is worse than a stale one, so nothing is written
        print(f"could not read the counts: {e}", file=sys.stderr)
        return 1
    counts["c-all"] = sum(counts.values())

    s = PAGE.read_text(encoding="utf-8")
    moved = []
    for sid, n in counts.items():
        pat = re.compile(rf'(<b id="{sid}">)(\d+)(</b>)')
        m = pat.search(s)
        if not m:
            print(f"no span carries id {sid}", file=sys.stderr)
            return 1
        if m.group(2) != str(n):
            moved.append(f"{sid} {m.group(2)} to {n}")
        s = pat.sub(rf"\g<1>{n}\g<3>", s, count=1)

    PAGE.write_text(s, encoding="utf-8")
    print("\n".join(moved) if moved else "already current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
