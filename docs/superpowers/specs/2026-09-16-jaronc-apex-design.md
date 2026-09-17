# jaronc.com, the apex site

Design document. Written 16 September 2026.

## What this is

A single public page at `jaronc.com` that indexes four projects and points
at the work itself. It is not a CV, not a blog, and not a second dev
journal. The journal at `frozendawn.jaronc.com` stays the only deep thing;
this page exists so that someone who lands on the name can tell within ten
seconds what gets built here, in what, and at what scale.

## Decisions already settled

1. **Audience: hiring legible.** It reads as a personal site, but stack,
   scale and how to reach me are findable fast. No CV page, no skills bar
   chart, no "open to opportunities" banner.
2. **Depth: index, links out.** One page. Each project gets a line about
   what it is and a line about what was hard, then links away.
3. **Visual direction: Field.** Near black `#08090c`, accent `#6ee7c8`,
   Helvetica Neue. The background is a flow field of streamlines integrated
   once and drawn in progressively, then left completely still.
4. **Headline: the name.** The `<h1>` is `Jaron Cabral` and the lede under
   it carries the claim. Aphorism headlines were tried and rejected for
   reading as corny.
5. **Not space themed.** Nothing orbital, no starfield, no rockets. The sci
   fi reading comes from behaviour, not decoration.

## Repo and hosting

New public repo **`cjaron03/cjaron03.github.io`**, confirmed available on
16 September 2026.

A user site repo publishes from the repository root and is the canonical
home for the account, so `cjaron03.github.io` keeps working as a fallback
address if DNS is ever wrong. GitHub Pages requires a public repo for a
custom domain on a free account, which is the same reason
`frozen-dawn-journal` is public.

GitHub Pages serves one site per repo, so this cannot be added to
`frozen-dawn-journal`. The two sites are independent deploys that happen to
share a domain.

Pages settings: source `main`, path `/`, custom domain `jaronc.com`,
enforce HTTPS once the certificate is issued.

## DNS

The registrar is Porkbun. As of 16 September 2026 the apex and `www` still
resolve to the Porkbun parking fleet (`207.207.210.23`, `.36`, `.50`) via a
wildcard record. A specific record beats a wildcard, so the wildcard stays
and nothing is deleted.

| Type  | Host             | Answer                |
| ----- | ---------------- | --------------------- |
| ALIAS | (blank, apex)    | `cjaron03.github.io`  |
| CNAME | `www`            | `cjaron03.github.io`  |

ALIAS rather than the four `185.199.10x.153` A records: Porkbun supports
ALIAS at the apex, it is one record instead of four, and it follows
GitHub's address changes without intervention.

`frozendawn.jaronc.com` already has its own CNAME and is unaffected.

**Expect a delay on the certificate.** When `frozendawn.jaronc.com` was set
up, GitHub's edge fleet rolled the certificate out unevenly and the IPv6
edge served `CN=*.github.io` for a while, which surfaces as curl SSL error
60. That is not a misconfiguration. Verify with a deterministic check
repeated until it passes consistently, not a single request, because
requests race between a good IPv4 edge and a stale IPv6 one.

## Build

**There is no build step.** A one page site does not need the fragment and
shell pipeline the journal uses. The repo is:

```
index.html      the whole site
CNAME           jaronc.com
assets/         favicon, og image
tools/check.py  the checks, adapted from the journal
docs/           this document
```

`CNAME` is committed rather than generated, because there is no build to
generate it and no second place for the hostname to drift to.

### Checks

`tools/check.py` is carried over from the journal and trimmed to what
applies to one page. It must fail the build on:

1. any literal em dash in `index.html`
2. US spellings from the journal's existing word list
3. a relative link or asset reference that does not resolve on disk
4. a missing `<title>`, `<meta name="description">`, or og tag
5. `CNAME` not matching the canonical URL in the page's `og:url`
6. `node --check` failing on the inline script

## Live commit counts

The four counts are fetched at runtime, not baked. Same technique already
running in production on the journal homepage:

```
GET https://api.github.com/repos/<owner>/<repo>/commits?per_page=1&sha=main
```

The `Link` response header's `rel="last"` page number is the commit count.
One unauthenticated request per repo, four total, well inside the rate
limit for a page view.

Current values are written into the markup as fallback text so the page is
never blank and degrades to correct-as-of-deploy if the API is unreachable
or rate limited. Counts as of 16 September 2026: Frozen Dawn 553, flare+
48, Canvas & Clay 95, Heart Disease Predictor 10.

Note the known discrepancy carried over from the journal: `sha=main` counts
main only, while numbers derived from a full mirror count all branches. For
Frozen Dawn these differ. The live number is the one shown, and that is
deliberate.

## Page structure

```
<h1>Jaron Cabral</h1>
lede
facts strip
four project rows
footer
```

Above the rows, a monospace top line: the name on the left, `WORK, 2025 TO
2026` on the right.

**Lede:** "I build the parts of a system that do not have a library yet. **A
game engine simulating a planet dying, a forecaster that has to admit when
it is wrong, and a gallery that runs with the internet unplugged.**"

The second sentence is the whole page in one line, and it is emphasised
because it is the part a reader skimming for ten seconds should catch. The
three clauses map, in order, onto rows one, two and three.

### The facts strip

A single monospace line under the lede, above a hairline rule, carrying the
things a recruiter scans for and nothing else: `4 PROJECTS`, `706 COMMITS`,
the languages, the runtime stack, and `2025 TO 2026`. Numbers are in the ink
colour, labels are dim.

This is deliberately a line of text and not a chart. It exists because
decision 1 asks the page to be legible to someone hiring within ten seconds,
and without it those facts are only inferable by reading four rows.

### The four projects

Selected from thirteen repos. `maze-pathfinding-alorithms` (one commit,
8KB of coursework) and `webhook` (empty, 2018) are excluded: including them
lowers the average rather than raising the count.

Each row carries name, what it is, what was hard, stack, live count, and a
link to GitHub. Frozen Dawn additionally links to the journal and is marked
with the accent dot.

Both sentences render, not just the first. The second is prefixed with a
bolded "The hard part." and set a step dimmer, so the row reads as a claim
and then its evidence. Two lines per row is also what stops four rows from
leaving half a viewport empty; a row is about 105px, and four of them plus
the header block and the footer fill a laptop screen with no scroll.

**1. Frozen Dawn** &middot; Java, NeoForge &middot; 553

> A Minecraft mod where Earth becomes a rogue planet, and the thing hunting
> you learns how you play.
>
> The Architect re-weighs its options as the world changes, so the cost of
> thinking had to stay inside a frame budget while everything around it was
> simulating a six phase collapse.

Links: `github.com/cjaron03/frozen-dawn`, `frozendawn.jaronc.com`

**2. flare+** &middot; Python, Svelte &middot; 48

> Predicts solar flares from live NOAA GOES data: which class in the next
> 24 to 48 hours, and how long until one arrives.
>
> Flares are rare, so a model that always says "none" scores well and is
> useless. The work was calibration and survival analysis, and reporting
> honestly how often it is wrong.

Links: `github.com/cjaron03/flare-plus`

**3. Canvas & Clay** &middot; Python, Svelte &middot; 95

> A local first digital gallery that runs on a network with no internet,
> installed by someone who is not technical.
>
> Every assumption a web application makes about being online had to come
> out, and the installer had to be a wizard rather than a README.

Links: `github.com/cjaron03/canvas-and-clay`

**4. Heart Disease Predictor** &middot; Python, Jupyter &middot; 10

> A cardiovascular risk model over the UCI Cleveland dataset, taken through
> CRISP-DM end to end.
>
> 303 patients is not many, and being accurate on average is not the same
> as being useful to a doctor, so the value is in the SHAP explanations
> rather than the score.

Links: `github.com/cjaron03/Heart-Disease-Predictor`

### Footer

Pushed to the bottom of the viewport with `margin-top:auto` inside a flex
column, so the page closes on a line rather than trailing off into empty
background. It carries `github.com/cjaron03` and `frozendawn.jaronc.com` on
the left and `jaronc.com` on the right.

**No email address for now**; the slot exists in the markup and stays empty
until one is chosen.

## The row glyphs

Each row carries a 168 by 52 glyph that is the actual thing the project is,
taken from that project's own source rather than invented.

| Project | Glyph | Source |
| --- | --- | --- |
| Frozen Dawn | Black, then the eyes snap open and light rips out across the glyph. It checks what blocked it twice, comes back to the reader, stops dead and tilts while the bright band pulses, then levels, narrows, and fires a second pulse. Then it closes | The mod's own three block rows at `#008CB4`, `#00D2FF`, `#005064`, the chapter II card on the journal, and `ArchitectThinkingController` plus `ArchitectModel` for the pause and the pose |
| flare+ | A GOES X-ray flux curve across the C, M and X class lines: a long quiet band, a rise in seconds, a decay over the rest of the box, with the M line lighting as it is crossed | The `#f97316` to `#fb7185` gradient from `ui-frontend/public/favicon.svg`, on the curve the model actually reads |
| Canvas & Clay | Three framed works on a gallery rail whose thumbnails resolve one after another | Accent `#5a9fd4` from `frontend/src/app.css` |
| Heart Disease Predictor | A PQRST ECG trace with a sweep running along it | `#ef4444`, three cycles across the box |

Using the same Architect eye on both sites is deliberate: it is the one
object that appears in the mod, the journal and the portfolio, so the three
read as one body of work.

These two were rebuilt twice, and the second pass is the one worth
recording, because both failures were the same failure at different sizes.

flare+ was its own app icon beside a line that drew in. An icon of an icon
carries a project's colours and nothing else, so the icon went and the
colours moved onto the curve the model actually reads: GOES X-ray flux
across the C, M and X class lines, a real event profile with a fast rise and
a slow decay. The draw crawls through the quiet band and rips through the
rise, because the waiting is most of that problem and a constant speed hid
it.

Frozen Dawn first wobbled, then ran a literal decision loop: the eyes
scored three small candidate blocks in turn and committed to one. That was
accurate and still flat, because it was a diagram drawn at 10px in a corner
of the box. What flare+ got right is amplitude. One long quiet, then a
single gesture that crosses the whole glyph.

So the eyes became the whole glyph, at 26 by 13 blocks instead of 15 by 7,
and they run the beat the journal already opens chapter II on: black, then
the eyes, then the blue. They snap open with an overshoot while a two pixel
bar rips outward across all 168px. They look away twice, return to the
reader, narrow, and fire a second pulse. Then they close and it goes dark
again.

The narrowing is the point. The first pulse is it waking up and the second
is it deciding, and between them it stops looking around and holds on
whoever is reading. Opening and blinking are both `scaleY`, and one element
cannot run two animations on one property, so the eye is two nested
elements.

A reader who lands during the 0.34s dark phase sees nothing in that slot.
That is accepted: it is 4% of an 8.4s cycle, and a thing that wakes up has
to have been asleep.

### The pause is the thinking

The loop then gained the part it was missing, and it is the only part of
the glyph that is copied out of the mod line for line rather than
interpreted.

`ArchitectThinkingController` is what the Architect does when it stops. It
only runs while the entity is stationary with a live target. It counts
still ticks, and at six of them it writes `PURSUIT_PAUSE_START` with a
cause: `TARGET_MOVED`, `PATH_SEARCH`, `OBSTRUCTION` or `ROUTE_EXECUTION`.
For forty ticks after a route change it looks at what blocked it rather
than at the player. At thirty two still ticks it rolls, deterministically
off its own UUID, a one in three chance of the hand to chin pose, and rate
limits that to once per 240 ticks.

`ArchitectModel` draws the pose: `head.zRot = -0.15F * tilt`, which is
**-8.6 degrees**, with `head.xRot` nudged forward by `0.035F`. The tilt
eases in at `0.16` per tick, so it lands in about a third of a second.

The glyph uses those numbers as written. It tilts exactly -8.6 degrees with
a 1.5px nod, eased in over the six ticks the controller waits before it
will call a pause a pause. The two look aways earlier in the loop are the
route change behaviour, not decoration: it is checking what blocked it.

While it is tilted the bright `#00D2FF` band pulses three times and the eye
nearly goes out between pulses. The controller is writing decision records
the whole time it stands there, and those pulses are those records. The
band carries it because it is the only part of the eye the mod lights up.

The mod tilts on one pause in three. The glyph tilts every cycle, because a
mark that performed its best beat a third of the time would read as broken
rather than as faithful. That is the one place this glyph knowingly departs
from the source.

## Performance rules

The journal hit a real problem where a `forwards`-filled animation combined
with a `filter` kept elements permanently on the compositor's animating
list, and the page was described as laggy. These rules exist because of
that:

1. **No `filter` anywhere.** Not on the glyphs, not on the background.
2. **Landed states animate transform and opacity only.**
3. **The background flow field draws once and stops.** 190 streamlines
   integrated once, five points drawn per frame, then the loop exits. It
   does not run at rest.
4. **Glyph animations pause off screen.** An IntersectionObserver toggles
   `animation-play-state: paused` on any glyph whose row has left the
   viewport.
5. **Restarting an animation from JS clears the property and forces a
   layout in between**, otherwise it continues the old timeline.

## Accessibility and responsive

- `prefers-reduced-motion: reduce` disables every glyph animation, lands
  the rows opaque and untransformed, and draws the flow field in one pass.
- All glyphs are `aria-hidden`; they carry no information not already in
  the text.
- Under 760px the rows stack, the glyph moves below the text, and the
  headline drops to 33px.
- The page must fill the window at every width, which the journal
  originally got wrong.

## Out of scope

Blog, contact form, analytics, light mode, per-project detail pages, a CV
page, and any second page of any kind.

## Open items

1. **Email address.** Deferred by decision. The footer slot stays empty.
2. **Social preview image.** Setting it is a web-only repo setting with no
   REST endpoint, so it has to be uploaded by hand in Settings once the
   repo exists.
3. **Repo hygiene surfaced by the portfolio audit and not yet done.** All
   public repos have no licence, which technically means nobody may legally
   use or fork them; no repo has topics or a homepage set, so GitHub search
   surfaces none of them; and `maze-pathfinding-alorithms` has a typo in its
   name. None block this site.
