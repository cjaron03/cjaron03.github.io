#!/usr/bin/env python3
"""Draw the favicon and the social card.

Both are the page's own materials: the ground, the accent, the flow field
the homepage draws behind itself, and the little accent dot that sits next
to every project name. Nothing here is decoration invented for the card.

Run from the repo root: python3 tools/art/make_assets.py
Everything lands in assets/ and is committed, so a deploy never has to
draw anything.
"""
import math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT   = Path(__file__).resolve().parent.parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

GROUND = (8, 9, 12)
INK    = (232, 234, 238)
ACCENT = (110, 231, 200)
MUTED  = (164, 171, 186)
DIM    = (91, 97, 112)

NEUE = "/System/Library/Fonts/HelveticaNeue.ttc"
MED, REG = 10, 0                      # face indices inside the collection
MONO = "/System/Library/Fonts/SFNSMono.ttf"


def font(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)


def over(rgb, a):
    """The canvas draws its lines as alpha over the ground. Same result,
    computed once, so PIL only ever paints opaque pixels."""
    return tuple(int(round(c * a + g * (1 - a))) for c, g in zip(rgb, GROUND))


def track(d, xy, text, f, fill, sp):
    """Letter spacing, which PIL has no notion of."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + sp
    return x


# ---- the flow field, the same field the page draws ----------------------
def ang(px, py):
    return (math.sin(px * 0.0047) * 1.9
            + math.cos(py * 0.0058) * 1.6
            + math.sin((px * 0.7 + py) * 0.0031) * 1.4)


def field(d, W, H, k=1, seeds=170, seed=7):
    """Integrated once and drawn whole. The page animates the draw; a still
    image only needs where the lines ended up.

    k is the supersample factor. the angle function is tuned in css pixels,
    so it is sampled in css pixels and only the step is scaled up, which
    keeps the card's field the same size as the page's rather than twice
    as tight."""
    r = random.Random(seed)
    for _ in range(seeds):
        px, py = r.uniform(-0.1, 1.1) * W, r.uniform(-0.1, 1.1) * H
        hot = r.random() < 0.13
        pts = []
        for _ in range(340):
            pts.append((px, py))
            a = ang(px / k, py / k)
            px += math.cos(a) * 2.4 * k
            py += math.sin(a) * 2.4 * k
            if not (-0.2 * W < px < 1.2 * W and -0.2 * H < py < 1.2 * H):
                break
        if len(pts) > 26:
            d.line(pts, fill=over(ACCENT, .34) if hot else over(MUTED, .13),
                   width=5 if hot else 4, joint="curve")


# ---- the icon -----------------------------------------------------------
# a J and the accent dot that marks every live project on the page. two
# marks is the most a 16px tab icon can hold and still be read.
def icon(px):
    S = px * 4
    im = Image.new("RGB", (S, S), GROUND)
    d = ImageDraw.Draw(im)
    f = font(NEUE, int(S * 0.70), MED)
    box = d.textbbox((0, 0), "J", font=f)
    d.text(((S - (box[2] + box[0])) / 2 - S * 0.02,
            (S - (box[3] + box[1])) / 2), "J", font=f, fill=INK)
    r = S * 0.085
    cx, cy = S * 0.775, S * 0.245
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ACCENT)
    im.resize((px, px), Image.LANCZOS).save(ASSETS / f"icon-{px}.png")


# ---- the social card ----------------------------------------------------
def card():
    W, H, K = 1200, 630, 2
    im = Image.new("RGB", (W * K, H * K), GROUND)
    d = ImageDraw.Draw(im)
    field(d, W * K, H * K, K)

    pad = 84 * K
    track(d, (pad, 66 * K), "JARONC.COM", font(MONO, 17 * K), DIM, 3.4 * K)

    d.text((pad - 6 * K, 176 * K), "Jaron Cabral",
           font=font(NEUE, 104 * K, MED), fill=(255, 255, 255))

    lede = font(NEUE, 30 * K, REG)
    d.text((pad, 330 * K),
           "Mostly software.", font=lede, fill=MUTED)
    d.text((pad, 372 * K),
           "Sometimes entire worlds.", font=lede, fill=MUTED)

    d.line([(pad, 494 * K), (W * K - pad, 494 * K)], fill=(25, 28, 36), width=2 * K)
    m = font(MONO, 17 * K)
    x = track(d, (pad, 522 * K), "4 PROJECTS", m, (198, 204, 216), 3.2 * K)
    x = track(d, (x + 22 * K, 522 * K), "698 COMMITS", m, (198, 204, 216), 3.2 * K)
    track(d, (x + 22 * K, 522 * K), "JAVA  PYTHON  SVELTE  JUPYTER", m, DIM, 3.2 * K)

    r = 7 * K
    cx, cy = W * K - pad - r, 529 * K
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ACCENT)

    im.resize((W, H), Image.LANCZOS).save(ASSETS / "og.png")


if __name__ == "__main__":
    for s in (32, 180, 512):
        icon(s)
    card()
    for f in sorted(ASSETS.iterdir()):
        print(f"  {f.name}  {f.stat().st_size:,} bytes")
