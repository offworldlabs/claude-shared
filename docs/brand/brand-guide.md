# Brand guide

> A snapshot of how the Offworld Labs surfaces look today, gathered so a new page
> can match them without guessing. This captures **what we have**, not a target
> we are aiming for: where the sites disagree, that is recorded rather than
> resolved. Treat it as a description to build against, and update it when the
> sites change rather than the other way round.
>
> Companion file: [`tokens.css`](tokens.css) holds the same values as CSS custom
> properties, so a page can consume them instead of transcribing hex codes.

The design lives in four hand-authored surfaces, none of which shares a
stylesheet with the others:

- **offworldlabs.com** ([`landing-page-owl`](https://github.com/offworldlabs/landing-page-owl)): the lab
- **retina.fm** ([`landing-page-retina`](https://github.com/offworldlabs/landing-page-retina)): the product
- **app.retina.fm** (`retina-server/dashboard`): the console, holding the live
  radar map at `/map` (where `/` lands), the public archive browser at `/data`,
  and the node owner's pages
- **owl.local** ([`retina-gui`](https://github.com/offworldlabs/retina-gui)): the node's own UI

They read as one family, but each has its own voice. Two sit apart: the console
is the only one that goes dark, and owl-os is the only one that runs on hardware
in someone's house rather than on a server.

**The console is one bundle on one origin.** Its pages, the map and the data
explorer are routes of a single SPA, reading one palette and one component file
(`packages/shared/css/tokens.css` and `ui.css` in retina-server). They share a
hostname because the session cookie is host-only, so a sign-in covers only the
origin that set it. The retired names `dash.`, `map.` and `data.retina.fm` are
Cloudflare redirects into the matching path on `app.retina.fm`.
`admin.retina.fm` is the same bundle again, with the admin route table chosen by
hostname, so it looks like the console and is not listed separately anywhere
below.

**The map is a page of the console with a voice of its own.** It sits inside
the console's chrome (sidebar, header, palette, type) and draws a full-bleed
operational view beneath it, Flightradar24-style: controls floating over the
basemap with a shadow, a data palette chosen by measurement, toasts, a compact
toolbar. Where the map departs from the rest of the console, the tables below
give it a column of its own; everywhere else "the console" includes it.

**Only the console themes.** It carries one light/dark pair and follows the OS
unless told otherwise (§3), and the map wears whichever half the rest of the
console is wearing. The other three surfaces are light only.

**A copy of the console's look runs outside `retina-server`.** Tower Finder
(`tower-finder-service/frontend`, the standalone illuminator search at
`towers.retina.fm`) took the console's palette, token names and appearance
switch rather than growing a look of its own, and sets them in Inter rather than
the system stack. It holds a copy rather than importing the shared package,
since the two build separately. It has no column in the tables below and gets
no voice of its own in §1; where §3 and §6 describe the themed cascade or the
switch, it is included.

owl-os is the odd repository as well as the odd surface. The UI is authored in
[`retina-gui`](https://github.com/offworldlabs/retina-gui) but shipped by
[`owl-os`](https://github.com/offworldlabs/owl-os), which clones it at a pinned
tag into the SD-card image, brands it `OWL-OS` in the page title and the nav,
and serves it from the node on port 80. Its style is therefore read from
retina-gui `main`; what a node in the field is running is whatever tag the image
pinned (see §10).

**`retnode.com` is this same surface, not another one.** One Flask app on one
port answers to every name a node has: `owl.local` and `ret<node_id>.local` on
the LAN, and `ret<node_id>.retnode.com` over the Cloudflare tunnel from
anywhere. Same templates, same `common.css`, so there is nothing separate to
capture. What differs is the *pathway*, which is decided by hostname alone: the
LAN is unauthenticated (being on the network is the credential), while the
tunnel hostname is challenged for a password and refuses the operations that
need physical presence. Visually that costs a login page, a refusal page, and
greyed-out cards for the services whose ports the tunnel does not route.

One name under that domain is genuinely a different page. The delay-Doppler
display embedded on offworldlabs.com,
`radar3.retnode.com/display/detection/delay-doppler/`, is **blah2's** own web
output, not this UI: there is no `/display` route in retina-gui. It is a
hand-built tunnel that predates the per-node ones, and its look belongs to
blah2 rather than to any surface described here.

---

## 1. Brand architecture: one family, five voices

The surfaces share a spine (a blue accent, green/amber status colours, a small
uppercase micro-label, hairline rules) and then diverge in personality. The split
maps onto audience. The console speaks in two registers, its pages and its map,
so the map has a column of its own here. Three of the four surfaces are light
and nothing else; the console carries both halves of one palette pair (§3).

| | **owl** · offworldlabs.com | **retina** · retina.fm | **console** · app.retina.fm | **map** · app.retina.fm/map | **owl-os** · owl.local |
|---|---|---|---|---|---|
| **Role** | The lab / parent org | The product you buy | The console you operate, and the archive you fetch from | The live picture | The node you own |
| **Audience** | Researchers, funders, press | Prospective node owners | Signed-in node owners and operators; anyone on the archive | Anyone watching the map | Whoever has the box |
| **Feel** | Editorial, institutional | Commercial, confident | Utilitarian, dense | Operational map (FR24-style) under the console's chrome | Appliance settings, unhurried |
| **Serif** | Source Serif 4, wt 400 | Fraunces, wt 600 | none | none | none |
| **Sans** | Inter | DM Sans | system stack | the console's | Inter |
| **Mono** | IBM Plex Mono | JetBrains Mono | SF Mono | the console's | JetBrains Mono |
| **Canvas** | warm paper `#f7f6f2` | warm paper `#fafaf9` | cool slate `#f1f5f9`, dark navy `#0d1b2a` | the console's | near-white warm `#fffdfb` |
| **Blue** | muted `#5b8dd9` | punchy `#2563eb` | `#3b82f6` → `#2563eb`, dark `#38bdf8` | the console's, plus an amber selection | `#2f8adc`, accents only |
| **Radius** | 4–6px | 8–20px | 3–16px, 999px chips | 2–12px | 6–14px |
| **Buttons** | flat | lift + shadow | flat | flat, a compact toggle | flat, primary is ink |
| **Dark UI** | none | one dark section | **follows the OS**, three-state switch | the console's theme | none |

A rough rule of thumb for a new page: **who is it for?** Reaching outward to the
scientific or funding world reads as owl. Selling or explaining the kit reads as
retina. Anything behind a login, or anything that hands the public the archive,
reads as the console. Anything that _is_ the live radar picture (a map, a track
view, an operational overlay) reads as the map. Anything a node owner does to
their own hardware reads as owl-os.

The console and owl-os are worth telling apart, since both are settings pages for
the same hardware. The console holds nodes at arm's length: dense, tabular, many
rows on one screen, and behind a sign-in for anything beyond the public map,
archive, leaderboard and knowledge pages. owl-os is one person and one box on
their own network, reached without a password, so it runs a 720px column, one
decision per row, and explains each in a sentence underneath.

---

## 2. Foundations

The parts that stay roughly constant across all four, and are the safest thing
to carry into new work.

- **A paper-like canvas.** Three of the four are near-white and only near-white
  (warm on the marketing sites, `#fffdfb` on owl-os, which pushes furthest
  toward white). The console is cool slate on a light OS and navy on a dark
  one, the map included. So "light paper" is the norm for anything that explains
  or sells, and the surface that operates the network is the one that can go
  dark (§3).
- **A blue accent.** owl sits soft and desaturated, retina and the console land
  on the brighter `#2563eb`/`#3b82f6`, owl-os lands between them at `#2f8adc`,
  and the console's dark half goes brighter still (sky `#38bdf8`) to carry on
  navy. Blue is the only chromatic accent in the UI chrome; everything else is
  ink on canvas. (The map adds amber for the selected track.) owl-os spends its
  blue the most sparingly: the primary button is ink, and the accent is kept for
  focus rings, hover borders, selection washes and the one card that is _this_
  node.
- **Green and amber as status colours.** Green marks "live" / validated / ADS-B
  truth; amber marks the radar echo, anomalies, and attention. The console adds
  red for outright errors. (The exact shades drift between surfaces; see §10.)
- **A small uppercase micro-label.** Small, uppercase, letter-spaced, muted.
  Used for section eyebrows, stat labels, table headers, nav-section titles, and
  diagram annotations. This is the single most reused idiom and the quickest way
  to make a new page read as "ours". All four surfaces have it, and only the two
  marketing sites set it in their mono. The console and owl-os keep the
  uppercase-and-tracked treatment in their sans: the console because it never
  spent its mono on it (stat labels, table headers and nav-section titles are all
  the system stack), and owl-os by choice, having JetBrains Mono and spending it
  on data instead.
- **Hairline rules and grid dividers.** 1px borders at low contrast separate
  sections, table rows, fact lists, and card grids. Structure comes from lines,
  not shadows or fills.
- **Flat and quiet.** Minimal ornamentation, few shadows (retina uses a subtle
  button lift; the console keeps shadow for what floats: the header dropdown,
  two of the data explorer's panels and what floats over the map), small status dots for
  liveness. owl-os is the one partial exception: its cards carry a hairline
  shadow at rest and brighten their border plus deepen the shadow on hover, which
  is how a whole card reads as clickable without a border change alone carrying
  it.
- **The radar diagram.** owl and retina both open with a hand-built SVG of the
  passive-radar geometry (transmitter → target → node) with animated signal
  paths. It is the strongest single motif the two marketing sites share. owl-os
  has a working relative of it, a draggable flight-path simulator. See §8.

---

## 3. Colour

Values are grouped by role. Per-surface specifics sit in the columns; foundation
roles (semantics) are shared unless a surface overrides them. The console takes
two columns, one per half of its pair.

### Canvas and ink

| Role | owl | retina | console, light | console, dark | owl-os |
|---|---|---|---|---|---|
| Canvas | `#f7f6f2` | `#fafaf9` | `#f1f5f9` | `#0d1b2a` | `#fffdfb` |
| Sunk surface | `#edecea` | `#f5f4f0` | `#f1f5f9` (= canvas) | `#0f2035` | `#fbfaf8` |
| Card / panel | `#ffffff` | `#ffffff` | `#ffffff` | `#132240` | `#ffffff` |
| Dark section | n/a | `#090904` / `#242422` | n/a | (the whole surface) | n/a |
| Ink (primary) | `#0e0e0c` | `#1a1a18` | `#0f172a` | `#e2e8f0` | `#13161c` |
| Ink (muted) | `#444440` | `#6b6b63` | `#475569` | `#94a3b8` | `#494d54` |
| Ink (subtle) | `#888882` | `#9c9c93` | `#94a3b8` | `#64748b` | `#83868c` |
| Border | `rgba(14,14,12,.1)` | `#e8e8e3` | `#e2e8f0` | `rgba(100,180,255,.14)` | `#eae7e4` |

**The two console columns are one pair, held in one file.**
`packages/shared/css/tokens.css` is the source in retina-server, read by every
console page and by the map, so the map carries no chrome palette of its own. Three
consumers that cannot read a custom property hold values written out, each held
to the file by a test: the chart theme (Semantics, below), the map's data
palette (for Leaflet and SVG) and the API reference's Scalar theme. The map's
chrome adds a handful of tokens beside the pair (`--panel-shadow`,
`--map-chip-*`, `--violet`) and overrides `--tile-filter` and, on the light
half, `--bg-sunk`, in `dashboard/src/pages/map/map-surface.css`. tower-finder
holds a hand copy of the pair.

The marketing canvases are warm (a hint of yellow); the console is cool slate,
inverting to dark navy. The dark ink ramp is the mirror of the light slate ramp
(`#94a3b8` / `#64748b` recur), and the dark hairlines are a blue-tinted
translucent white rather than a solid grey.

**What decides which half you get** is the viewer, falling back to the OS. The
control has three states, and the third, `system`, is the default and the one a
viewer who has never touched the control is on. It stamps no attribute at all
and lets a `prefers-color-scheme` block answer, so the preference keeps working
when the OS changes its mind mid-session, where stamping a resolved value would
pin the surface to whatever the OS happened to be at load. The map has no
control of its own: it takes the console's resolved theme, so a first visit on
a machine set to light gets a light map. tower-finder behaves the same way with
its own copy of the control.

The cascade follows from that. Light sits on the bare selector, because the
default must paint before any JavaScript runs, and `data-theme` buys dark: the
attribute is stamped from JavaScript, so whichever half depends on it is the one
that can flash the other before first paint. The media query is guarded
`:not([data-theme="light"])`, which is what lets an explicit light choice beat a
dark OS. The cost of the third state is the dark half written twice, once per
selector, since CSS cannot share a declaration block across a media query
boundary; the console (in `packages/shared`) and tower-finder each guard the two
copies against drifting with a test rather than with the stylesheet. The map
element's own blocks are keyed the other way round, dark unless
`data-theme="light"`, which is harmless because the map always carries the
console's resolved theme as its attribute. Everything is written against the
custom properties, so the whole chrome inverts from one block.

Two tokens exist because of that pairing.

**`--bg-sunk` is the third surface tier.** On the light half a recessed region
can be made by letting the canvas show through, the canvas already being darker
than a card; the dark ramp inverts, card lighter than canvas, so a recessed pane
needs a colour of its own at `#0f2035`. It pays for the map's left aircraft
list, the Physics page's scene, ground-truth and performance sections, the
config page's JSON view, and the ground of the appearance switch. The map lightens its
light half to `#f8fafc`, since its recessed pane sits against panels that
already float. That is also the light input ground, which is why the aircraft
list's inputs take the card colour instead (§6).

**`--accent-ink` is what sits _on_ the accent** rather than beside it. It is a
token and not a literal white because the dark accent is a bright sky blue, on
which white is about 2.1:1; there it becomes a near-black `#082f49`. Any solid
accent fill carrying text needs it, and the shared `.btn-primary` already reads
it.

owl-os crosses the two: a warm canvas like the marketing sites, over a **cool**
ink ramp like the console. It is also the only surface authored in **OKLCH**
rather than hex (`oklch(0.20 0.012 260)` and so on), so its ramps are even
perceptual steps by construction. The hex column above is the sRGB equivalent,
for comparison only; the values in the stylesheet are the OKLCH ones.

owl-os is the only surface whose second border token goes **lighter** rather than
darker: `#eae7e4` bounds a card, `#f3f1ef` divides rows inside one. Structure
therefore gets quieter as you go inward, which is what keeps a config page of
thirty stacked rows from reading as a grid.

### Accent

| | owl | retina | console, light | console, dark | owl-os |
|---|---|---|---|---|---|
| Accent | `#5b8dd9` | `#2563eb` | `#3b82f6` | `#38bdf8` | `#2f8adc` |
| Hover / strong | `#4a7cc8` | `#3b82f6` | `#2563eb` | `#7dd3fc` | `#1a7acb` |
| Wash | `rgba(91,141,217,.15)` | `rgba(37,99,235,.06)` | `rgba(59,130,246,.10)` | `rgba(56,189,248,.16)` | `#e3f4ff` (opaque) |
| Wash edge | n/a | `rgba(37,99,235,.15)` | n/a | n/a | `#c4daf2` |
| Tint (hover) | n/a | n/a | `rgba(59,130,246,.05)` | `rgba(56,189,248,.07)` | n/a |

owl's blue is deliberately soft and low-contrast (an editorial choice, though it
costs link legibility, see §10). retina and the console share the saturated
blue, with the console resting one step lighter and hovering to retina's resting
value. The console's dark half pushes to a brighter sky blue so the accent reads
on navy. owl-os sits between the console's two, a shade cyan-ward of both. That
makes five distinct blues across four surfaces, two of them the console's.

The console is the only surface with **two** accent washes. The tint is the wash
at hover strength and sits deliberately below the wash proper, so a hovered row
and a selected one stay apart instead of collapsing into the same fill.

Two things owl-os does differently with it. Its washes are **opaque tints**, not
alpha overlays, so a wash keeps its colour over any ground it lands on rather
than picking up whatever is behind it. And every wash carries a matching **edge**
one step darker (`#c4daf2` for the accent, `#bee2c9` for success), so a tinted
region is bounded rather than bleeding into the page. The map adds amber for the
selected track (`#fbbf24` on dark, `#d97706` on light); owl-os uses the accent
wash plus a 3px inset rail for the same job.

### Semantics

| Role | Marketing (owl, retina) | Console, light | Console, dark | Node (owl-os) |
|---|---|---|---|---|
| Success / good | `#16a34a` | `#10b981` (emerald) | `#4ade80` | `#33a868` |
| Warning / attention | `#d97706` | `#f59e0b` (amber-500) | `#fbbf24` | `#e1a035` |
| Error | (unused) | `#ef4444` (red-500) | `#f43f5e` | `#e64343` |

Same three roles, brightened a step on the console's dark half so they carry on
navy, and landing between the marketing and console sets on owl-os. Each pairs
with a wash (~10% on light, ~15% on dark; opaque on owl-os) for tinted pill
backgrounds. The console's charts extend the accent into a categorical palette
(`#3b82f6, #10b981, #f59e0b, #ef4444, #8b5cf6, #ec4899, #06b6d4, #84cc16,
#f97316, #14b8a6`, with `#94a3b8` for an "others" slice) and a lighter run of
the same hues for the dark half (`#60a5fa, #34d399, #fbbf24, #f87171, #a78bfa,
#f472b6, #22d3ee, #a3e635, #fb923c, #2dd4bf`); reuse that ordering for any new
chart. Both live in `useChartTheme()`, since Recharts paints from props and
cannot read a custom property.

The map's live data colours are a separate, radar-specific scheme, not these
status roles, and the one part of the estate chosen by measurement rather than by
eye: each value is held to a contrast floor against its own basemap, and each
pair of marks to a CIEDE2000 distance from the others. The second is the
constraint that gets forgotten, and the one that binds here, because the four
track lanes all draw the same aircraft glyph and colour is the only thing telling
them apart. **Truth** (the ADS-B fix the solves are measured against) is drawn
only on a synthetic fleet's view (the admin console's `/sim`, or a local stack),
so the public map carries none. Where it is drawn it wears no lane hue: a
simulated target's truth sits at the far end of the neutral ramp from the
canvas, near-white `#f8fafc` on dark and slate `#1e293b` on light, since it is
the reference rather than a fifth lane, and one flying without a transponder is
grey beside it. Truth mirrored from the live ADS-B feed is teal, the one hue
family no lane uses. Radar detections run a **Doppler gradient** from dark-blue approaching
(`#1e3a8a`) through a neutral slate at zero to dark-red receding (`#991b1b` on
dark, `#7f1d1d` on light), so no radial motion reads as the absence of a
direction rather than as a third colour. Green there means coverage polygons,
never truth. See §8.

Both palettes carry the same keys, so a component asks for a role and gets the
value for whichever theme is drawn. The light theme is the tighter of the two:
a near-white ground leaves every category competing for the dark end of its hue,
where a dark ground admits the whole light end, so it is light that constrains
any new category.

owl-os carries a domain palette of its own that no other surface has, because no
other surface asks a person to pick a transmitter. **Broadcast band** is a
categorical hue (FM `#3b82f6`, VHF `#8b5cf6`, UHF `#ec4899`, each on an 8% wash),
and **suitability** reuses the status ramp as a judgement: ideal is the success
green, good is the warning amber, too far is a neutral grey `#9b9fa5`, and too
close is the danger red. Amber and red there are not faults, only "workable" and
"pick another one", which is the one place the status colours are spent on
something other than health.

---

## 4. Typography

Up to three registers per surface: a **display** face for headings, a **body**
face for running text and UI, and a **mono** face for labels and data. The
console collapses everything into the system stack, the map included.

| Register | owl | retina | console | owl-os |
|---|---|---|---|---|
| Display | Source Serif 4 | Fraunces | system sans | Inter |
| Body | Inter | DM Sans | system sans | Inter |
| Mono | IBM Plex Mono | JetBrains Mono | SF Mono | JetBrains Mono |

Loaded from Google Fonts on the marketing sites and owl-os; the console loads no
web fonts at all (its CSP limits `font-src` to its own origin and `data:` URIs). Only the two
marketing sites use a serif; the two operational surfaces (the console and
owl-os) are sans-only.

owl-os is the only surface that borrows both its faces from siblings rather than
choosing new ones (Inter from owl, JetBrains Mono from retina), and so is the
least type-divergent of the four. It also asks Inter for
`font-feature-settings: 'ss01', 'cv11'` (the single-storey `g` and the
straight-tailed `l`), which is what stops a screen full of node IDs and
frequencies from reading as body copy.

**Heading weight is the other big tell.** owl sets headings at 400 (light,
serious, editorial); retina and owl-os at 600 (present, product-confident); the
console at 700 (compact, functional). Marketing headings carry a tight
`letter-spacing` around `-0.02em` and line-height near 1.1; the operational
surfaces run text small (down to 8px on the map) and dense.

owl-os keeps the marketing surfaces' `-0.02em` on page titles while sitting at
console sizes, and runs a 14px base rather than 16px: small enough for a page of
settings, large enough not to read as a table.

**Scale, as used:**

- Hero H1: `clamp(3rem, 6vw, 5rem)` on owl, `clamp(2.8rem, 5vw, 3.8rem)` on
  retina. Fluid, serif, tight leading.
- Section H2 / titles: `clamp(1.6rem, 3vw, 2.4rem)` (owl), `clamp(1.75rem, 3vw,
  2.25rem)` (retina). Console page titles are a flat 24px.
- Body: 16px base, line-height ~1.6–1.7, colour = ink-muted for prose. owl-os
  runs 14px / 1.5, and drops to 12–12.5px for the help line under a field.
- Page title (owl-os): a flat 26px / 600 / `-0.02em`, on Home, Config and every
  wizard step alike.
- Micro-label: ~0.65–0.75rem, mono, uppercase, `letter-spacing` 0.04–0.14em,
  colour = ink-subtle. The `.label` class in `tokens.css` captures the common
  case. owl-os sets its own at 11–11.5px, weight 500–600, tracking 0.04–0.08em,
  in Inter rather than mono.
- Numbers (owl-os): anything that changes in place (a dBFS reading, a countdown,
  a step counter) is mono with `font-variant-numeric: tabular-nums`, so it does
  not jitter as it updates. Worth copying anywhere a value refreshes live.

---

## 5. Shape, space and motion

### Shape

| | owl | retina | console | owl-os |
|---|---|---|---|---|
| Radius (default) | 4px | 12px | 8px | 10px |
| Radius (small) | 3px | 8px | 4px | 6px |
| Radius (large) | 6px | 20px | 12px, as a literal | 14px |

Crisp on owl, soft on retina, moderate on the console, second-softest on owl-os.
The console's tokens hold only the first two steps: 12px is written as a literal
on its pills (the status badge, the map's count and source chips) and the
sign-in card, and the data explorer's filter chips go fully round at 999px.
Borders are always 1px hairlines; nothing uses a heavy stroke. What floats over
the map's moving basemap (the legend, the filters popover, the overflow menu,
Leaflet's controls) carries a shadow as standard (`--panel-shadow`), heavier on
dark than on light because a soft shadow does almost nothing there and the
elevation has to come from the panel being lighter than the canvas.

The three-step scale is a fair summary for three of the surfaces and a
simplification for retina, which spends 5, 6, 8, 10, 12 and 20px, with neither
of its two button radii matching the 12px recorded as its default. The map keeps
mostly to the console's two tokens, with a scatter of 2–5px literals left over.

owl-os is the only surface with a real elevation scale: a hairline `shadow-sm` at
rest, a 24px-blur `shadow-md` on hover and for the sticky save bar, and a
`shadow-pop` for modals. All three are tinted with the ink colour rather than
black, so a raised card warms rather than greys.

### Space

- Marketing content sits in a centred column: `max-width` 860px for prose,
  1120–1200px for wide/hero rows. The console is full-width and fluid, with a
  250px sidebar that collapses to a 64px icon rail and 24px of content padding.
  The map drops the padding and starts with the rail collapsed, then goes
  full-bleed under the header: a 280px left aircraft list (collapsing to 36px),
  a 300px right detail panel, and a playback bar across the foot of the map.
- owl-os runs a 720px column on Home, a 200px + fluid two-column shell on Config
  (max 1100px), and a fixed 560px column for every wizard step. One decision per
  row, with its explanation directly underneath.
- Nav / header height: 56px (owl), 64px (retina), 56px (the console). owl-os
  stacks two rows instead, a fleet bar over the page tabs, and its config
  side-nav sticks below both at 58px.
- Section padding: ~5–6rem vertical on the marketing sites, 24px content padding
  in the console.
- Cards/panels: ~20px body padding, 16px header; grids gap ~16px.

### Motion

Three patterns recur:

1. **Reveal on scroll.** Elements start at `opacity: 0` + a small `translateY`
   and transition in via an `IntersectionObserver` toggling a class. ~0.45–0.5s.
2. **Live pulse.** The "live" / status dot pulses opacity on a ~2s loop.
3. **Signal march.** The radar diagram animates `stroke-dashoffset` so the dashed
   signal paths flow from transmitter to target to node.

owl and the console animate in CSS; retina's hero mixes in inline SVG SMIL
(`<animate>`). The console's keyframes are all on the map (the live pulse, a
panel slide, an anomaly pulse) bar one, the data explorer's drawer slide.

owl-os runs none of the three. It defines no `@keyframes` at all: motion is
limited to 120ms colour, border and shadow transitions on hover, a 150ms switch
throw, and a 2px nudge on a card's arrow. Nothing on the page moves unless it was
touched, which is reasonable for a settings surface someone reaches when
something needs fixing, and the reason its one animated component, the simulator,
checks `prefers-reduced-motion` before starting. The map guards its whole page
with a single reduced-motion block, though the rest of the console has none, so
the drawer slide runs regardless; owl's `/learn` page carries its own guard, and
the two marketing home pages still run their loops unguarded. The `tokens.css`
`.reveal` helper adds the guard, and new work should keep it.

---

## 6. Components

The four surfaces do not have the same component set, and the differences are
larger than the colour and type differences in §3 and §4; within the console,
the map differs from the other pages as much again. Before reaching for a
pattern, check it exists where you are building.

| | owl | retina | console | map | owl-os |
|---|---|---|---|---|---|
| Form controls | **none** | **none** | a shared `.input`; the data explorer scopes its own | one rule for the page | a real set |
| Tables | none | none | yes | one, in the shortcut help | one |
| Modal / dialog | none | none | one drawer; one native `confirm()` | one | three |
| Toasts | none | none | none | yes | none |
| Tabs | none | none | one page | none | yes |
| Icons | 36px, part-filled | Unicode glyphs | 24px, stroke 2 | inline SVG | 24px, stroke 1.6 |
| Framework | none | none | none | none | Bootstrap 5.3 |
| Custom properties | yes | yes | yes, themed | the console's, plus its chrome | yes |
| Theme control | none | none | `.theme-switch`, 3 states | the console's | none |
| `:focus` styling | none | none | inputs, and two scoped rings | the whole page | inputs only |

The two marketing sites have no `<form>`, `<input>`, `<select>`, `<textarea>` or
`<table>` between them, and no `:focus` or `:active` rule in either file. Their
only stateful control is the mobile nav toggle, and retina's one transaction
leaves for Stripe. So everything below about controls concerns the console and
owl-os alone.

### Chrome: nav and footer

- **Marketing nav.** Fixed top bar, `backdrop-filter: blur(16–20px)` over a
  translucent canvas, a hairline bottom border. Logo left (mono wordmark, or logo
  plus mono text on owl), links centre, a primary CTA right. 56px on owl, 64px on
  retina. Under 860px (owl) or 960px (retina) it collapses to a hamburger that is
  a literal `☰` text character, not an icon, opening an absolutely positioned
  blurred panel. Neither sets `aria-expanded`, traps focus, or changes the glyph
  when open.
- **The console is not a top bar.** It runs a 250px left sidebar plus a 56px
  header. The sidebar carries a brand block (a 32px accent square holding an
  "R", the name, and an 11px muted sub-label naming the console: "Node
  Dashboard", or "Admin Console" on the admin host, with the toggle that
  collapses the sidebar to a 64px icon rail), then sections titled in the
  micro-label, then `.nav-item` rows at 8px 12px with 18px icons: hover tints
  the row, active takes `--accent-light` with `--accent` text. Two navigation
  trees exist, the owner's and the admin's, chosen by hostname. On the app host
  a viewer with no session gets the owner's tree with the entries that need one
  greyed out and leading to the sign-in page; the admin host sends them straight
  to sign in. The header holds the page title, the appearance switch, and either a
  "Sign in" link or the avatar menu. Under 768px the sidebar, and the collapse
  toggle inside it, is `display: none` with nothing in its place, so navigation
  is simply unreachable on a phone (§10).
- **The map and the data explorer are pages in that shell**, with no chrome of
  their own above it. The map's full-width toolbar strip sits directly under the
  console header, in normal flow rather than floating over the map, and the two
  read as a single header block.
- **owl-os** stacks a fleet bar over page tabs; see the node section below.
- **Footer.** Hairline top border, mono wordmark left, muted links, a `© 2026`
  line. Understated. The console has none. owl-os fills its footer with
  versions instead (node ID, owl-os version, retina-node version, each value in
  mono), so the first thing anyone is asked for in a support conversation is
  already on screen.

### Buttons

Primary is solid ink on the marketing sites and owl-os, solid accent on the
console. owl, the console and owl-os keep buttons flat; retina lifts them
(`translateY(-1px)` plus a soft shadow) on hover. Secondary is a text link with a
hairline underline (owl), or an outline button (retina, the console, owl-os).

| | owl | retina | console (`.btn`) | map (`.toggle-btn`) | owl-os |
|---|---|---|---|---|---|
| Padding | 0.7rem 1.4rem | 0.55rem 1.25rem | 8px 16px | 3px 9px | 8px 14px |
| Radius | 4px | 8px (10px large) | 4px | 4px | 8px |
| Size / weight | 0.875rem 500 | 0.875rem 500 | 13px 500 | 12px 500 | 13.5px 500 |
| Disabled | n/a | n/a | every `.btn`, at 0.4 opacity | the console's | 0.55 opacity |
| Busy | n/a | n/a | label text only | n/a | spinner in label |

Three things worth knowing. On the marketing sites every button is an `<a>`, so
no disabled, active or busy state is expressible at all. On the console one rule
disables every `.btn`, matching `[aria-disabled="true"]` alongside `:disabled`,
so its link-buttons disable too; and the pressed state is keyed to ARIA rather
than a class (`aria-pressed`, or `aria-expanded` on a button whose panel is
open, drawn as the accent wash, an accent border and the hover accent as text),
so what is drawn and what a screen reader announces cannot disagree. And the
map's column describes `.toggle-btn`, the console's outline button at toolbar
density and the map's dominant control. That pressed state carries almost all
of the map's on/off state, standing in for the switches it does not have. The
one exception is the anomalies toggle, which reports a condition as well as a
state and so takes the error colour while it is filtering.

### Form controls

**owl-os is the only surface with a designed set.** One rule serves text inputs,
selects and textareas: full width, `--surface` ground, 1px `--line`, radius 8px,
padding 8px 10px, 13.5px. Focus clears the outline and takes an `--accent` border
plus a 3px accent ring at 12% alpha; `.is-invalid` swaps both for `--danger`.
Around it:

- Number fields carry `.ds-input mono`, so digits are JetBrains Mono with tabular
  figures, and the unit sits beside the field rather than inside it (mono 12.5px
  `--ink-3`).
- A select is styled as an input and gets no custom chevron, so the dropdown
  arrow is the browser's. Readonly selects are `disabled` rather than restyled.
- Read-only values use `.cfg-readonly`: mono on `--surface-2` behind a padlock,
  with a hidden input carrying the real value so the form still posts it.
- The switch is 36×20px with a 16px knob and fills with **ink** when on, not
  accent, since on/off is not a brand moment. The segmented control is inset on
  `--surface-2` with the active segment as a raised white pill.
- That pill does not port. Building it in `preview.html` against each surface's
  tokens showed why: it reads from the step between `--surface` and
  `--canvas-sunk`, and those two sit within 1.2:1 on owl, retina and both halves
  of the console. owl-os gets away with it by pairing the fill with `shadow-md`,
  which is the one surface with a shadow scale to spend. Anywhere else the active
  segment needs a hairline or a text-colour shift to be visible at all.
- Checkboxes are native at `accent-color: var(--ink)`, wrapped in a row with a
  12.5px help line beneath. **Radios are native and entirely unstyled**: no class
  exists for them, they are positioned with an inline `margin-top`, and only one
  of them sets `accent-color`, so the rest render in the browser's blue.
- Field furniture is a label at 13px/500 with the explanation directly under it at
  12px `--ink-3`, in a two-column row that puts the control on the right.
- `.ds-textarea` is defined and never used; there is no textarea on the surface.

**The console has one shared rule, `.input`**, in `packages/shared/css/ui.css`:
the `--bg-input` ground, a hairline `--border-light`, `--radius-sm`, 6px 12px
padding, 13px, 260px wide, with `.input-sm` a size down to sit beside a card
title. Focus clears the outline and takes an accent border. There is no hover,
disabled or error treatment, no help text and no inline validation message, and
the config editor's textarea is still styled inline at its call site.

**The data explorer scopes a denser rule of its own** under `.de-card`, styling
bare `input` and `select` elements rather than a class: the same ground, border
and radius at 6px 9px, a checkbox rule setting `accent-color`, and the same
accent-border focus. Its filter bar carries date, time, number and search inputs
and a select, the spread a bare-element rule saves restyling one by one.

**The map has one rule of its own**, so a filter input matches a console input:
text, number and search inputs and selects together, on the `--bg-input` ground
with a hairline border, `--radius-sm`, and an accent border on focus. The
aircraft list overrides the ground to the card colour, because `--bg-input` and
the map's `--bg-sunk` are the same value on the light half (§3) and a field on
that pane would otherwise be left with only its border. What is still ad hoc is
the playback scrubber, a native `input[type=range]` tinted with `accent-color`
and otherwise left as the browser drew it, and one native checkbox in the
node-owner control.

The map has no toggle switch, radio, date picker or file input anywhere. The
console's radios are the appearance switch below and the location-privacy
choice, which is a pair of native radios in a styled row.

### Theme control

§3 covers what the switch does to the surface. This is the control itself.

**The console and tower-finder run the same object**, `.theme-switch`: three
icon buttons in one `role="radiogroup"` on a `--bg-sunk` ground behind a
hairline, `--radius-sm` outside and 3px on each button, over 2px of padding and a
2px gap. Each button holds 15px of Feather line art drawn in `currentColor` (sun,
monitor, moon, on a 24-unit box with a 2-unit round-capped stroke), so setting
the ink is what tints the glyph; the active one takes `--accent-light` behind
`--accent`. Ordered **light → system → dark**, which reads as a run from one
extreme to the other with the neutral between them rather than putting the
default first.

- **Names, not glyphs.** The buttons carry no text, so each takes an
  `aria-label` and the same word as `title`, and the `<svg>` is `aria-hidden` so
  the name is not read twice. Without that a screen reader meets three
  unlabelled radios and the control is unusable rather than merely bare.
- **One tab stop, not three.** Choosing `role="radio"` over three independent
  toggle buttons is what obliges the radiogroup contract: a roving `tabIndex`
  puts Tab on whichever option is checked, and Left/Up and Right/Down move the
  selection *and* the focus, wrapping at both ends, with Home and End going to
  the ends. Only those keys are `preventDefault`ed; everything else passes
  through, or the arrows scroll the page while the selection moves underneath.
- **It sits in the top bar on both.** The console puts it straight in the
  header, so a signed-out viewer on the map or the data explorer has it as well;
  the avatar menu holds only the email and "Sign out". tower-finder has no
  signed-in user and puts it in its own top bar.
- **It wants a surface under it, not a canvas.** The ground is `--bg-sunk`,
  which on the light half *is* the canvas value (§3), so a switch dropped
  straight onto a page reads as three loose glyphs and only its hairline bounds
  it. In the header bar, which is `--bg-secondary`, the recess reads as
  intended.

The map has no theme control of its own. Its overflow menu's "Basemap" item
cycles the tiles under the chrome, labelled "Light", "Muted" and "OSM" (Positron,
Voyager and OpenStreetMap), so "Light" there names a basemap rather than a
theme. The basemap follows the theme until a viewer picks one by hand.

### Feedback: loading, empty, validation, errors

- **Loading.** owl-os shows Bootstrap's spinner, always shrunk by the same
  copy-pasted inline style rather than a class, and swaps a button's label for
  spinner plus text while it works. The console has no spinner and no skeleton
  at all: pages return the text "Loading…" in their empty-state box, a table
  shows a "Loading…" row in place of its rows (see the console's other pages, below),
  and the map, loaded lazily, waits behind the console-wide "Loading…" screen. Nothing anywhere uses a skeleton. The data
  explorer is the one page that does not load as a page: it fetches a day at a
  time and gives each day its own state and its own Retry, so one slow or failed
  day does not blank the rest. On any page that fetches several independent
  things, that is the shape to copy.
- **Empty states.** The console centres muted text at 48px 20px, with an icon
  slot that is styled and never used, and copy that states the absence ("No
  nodes connected yet", "No anomalies detected"). The data explorer's copy names the next action
  ("Pick a date range."), and the map's "No aircraft" is the same shape at the
  same size, in the muted ink. owl-os's is a help line that names the next action
  ("No cached tower search results yet. Run the Location step..."), which is the
  one worth copying.
- **Validation.** Only owl-os has any. A form-level banner above the form carries
  the specific refusal, falling back to "Please fix the highlighted fields below",
  and each offending field takes `.is-invalid`.
- **Error banners.** owl-os uses a danger-tinted banner at the top of the form and
  an info-tinted one in the same shape for neutral notices. The console has one
  shared `.notice`, a warning wash, with `.notice.error` on the error wash; save
  failures land there. The map has an emergency-squawk alert inside the detail
  panel.
- **Error boundaries.** The console's is the empty-state box with `role="alert"`,
  a heading, a sentence and two styled buttons ("Try again", "Reload page"). A
  per-page boundary resets on navigation, so one broken page leaves the sidebar
  working. The map wraps itself in another with map-specific wording, inside the
  map element so the fallback takes the map's theme.

### Overlays: modals, popovers, toasts

- **owl-os** has three Bootstrap modals doing three different jobs, and the split
  is worth copying: a form modal, a destructive confirmation that lists the
  consequences in prose, and a blocking progress modal set
  `data-bs-backdrop="static" data-bs-keyboard="false"` so it cannot be dismissed
  while the run holds the SDR. It also puts a fixed scrim over the whole wizard
  when the session expires, rather than leaving live-looking controls behind.
- **The console has no shared modal component.** One consequential action,
  graduating a polled radar or returning it to probation, confirms with native
  `window.confirm()`. Outside the map
  its popovers are the avatar menu in the header and the data explorer's node
  picker.
- **The data explorer has a drawer**, which is the shape to reach for when the
  content is something to read beside the list rather than a decision to make.
  560px on the right, a scrim over the page, a 0.18s slide in, split head / body
  / foot. It carries a key-value block, a preview table and a curl line, none of
  which fits a native dialog, and it leaves the list in place so the next file is
  one click away rather than a re-open. It is the only drawer in the estate, so
  treat it as a pattern with one instance rather than a settled one.
- **The map** has one modal, the keyboard-shortcut help, plus an overflow menu and
  a filters popover in its toolbar; stats and the node-owner control are inline
  cards in the aircraft list's header. It is the only page with **toasts**: a
  bottom-right stack of chips with four tones, a 2.5s life (6s for an emergency
  squawk), no dismiss control and no animation.
- **Tooltips.** No surface has a styled tooltip component. The console relies on
  the native `title` attribute, used around thirty times on the map alone. The
  one exception is the map's `.radar3-error-label`, a Leaflet tooltip restyled in
  place.

### Data display

- **Section eyebrow.** A micro-label above each H2 naming the section. The
  consistent opener for a marketing section, and the strongest shared idiom.
- **Fact rows and metrics.** Label-value pairs on hairline-divided rows (owl's
  RETINA facts), a bordered 4-up metrics bar (retina), stat cards with a 28px/700
  value and four tint modifiers (the console), or label-value rows on hairlines
  with tabular-numeric values (the map's detail panel, owl-os's node cards).
- **Cards.** White, 1px border, surface radius. Flat on the marketing sites and
  the console; owl-os gives them a resting hairline shadow and lifts them on
  hover. retina's grids use a 1px gap over a border-coloured ground so dividers
  read as shared lines; **the console's do not**, using a real 16px gap with
  per-card borders.
- **Tables.** Only the console and owl-os have one. The console's is 11px
  uppercase muted headers over 13px rows with a hairline under each, hovering to
  `--bg-card-hover` and taking the accent wash when selected, wrapped in a
  horizontal scroller: no sticky header, no zebra, no sortable headers. Sorting,
  where it exists, is a `<select>` or a row of buttons. owl-os's tower table
  marks its selected row with a wash plus a 3px inset rail, the rail being what
  the console's lacks. The data explorer's file
  listing is the console's type scale over a CSS grid rather than a `<table>`,
  since its rows nest three levels (day → node → file) and collapse; it does put
  the sort on the column header, which is the one thing the console's tables are
  missing and the easiest to port back. Its one real `<table>` is the frame
  preview inside the drawer.
- **Badges are not one component.** §3's status colours are consistent; the
  shapes they are poured into are not. Across the four surfaces there are at
  least seven: a 12px tinted-wash pill with a leading dot (the console's
  `.badge`, in six variants, whose shape the map's source and connection badges
  copy); an outline pill with a dot (owl-os `.ds-pill`); a tinted
  999px chip (owl-os `.node-chip`); a 6px tinted rectangle (owl-os
  `.tower-badge`); a 6px solid-ink corner badge (retina's kit); a 5px green wash
  (retina's savings tag); an 8px outline chip (retina's OSS row); and owl's live
  label, which is white on a black scrim over the iframe. Pick the surface's own
  shape rather than assuming the pill. The data explorer uses no badge: its 999px
  chip is a filter toggle (an outline `.btn` with `aria-pressed`) rather than a
  status readout, and reusing the status badge for it would have been the wrong
  call.

### Per-surface components worth knowing

**owl-os (the node UI).**

- **Fleet bar over page tabs.** Two stacked rows reading as one banner: the
  parent row is every node on the network (each an absolute link to its own
  `ret<node_id>.local`, the current one included), the child row is which page of
  this node. The child row is set apart by a lighter ground and no border of its
  own. The tab strip is the only part that gives under pressure: it scrolls
  rather than wrapping or squashing the furniture around it.
- **Wizard shell.** A fixed head / scrolling body / fixed foot at `100dvh`, body
  capped at 560px. Progress is a row of 24×4px bars, not numbered circles: ink
  for done, accent for the current step, hairline for what is ahead.
- **Sticky save bar.** Pinned to the bottom of the config page with a shadow and
  a live count of what has changed, so a long form never hides the fact that it
  has unsaved edits.
- **Rail-marked selection.** The selected table row, the active side-nav link and
  the matching manage-list item all take a 2–3px `inset` box-shadow rail plus a
  wash, rather than a border change. Selection reads without shifting layout by a
  pixel.
- **Peak meter.** A segmented dBFS ladder per tuner, styled as rack gear, with
  the reading in tabular mono to its right and an alarm state in `--danger`.
- **Bootstrap underneath.** owl-os is the only surface on a CSS framework
  (Bootstrap 5.3 from a CDN), with a block of overrides mapping its components
  onto the tokens. Two consequences worth carrying: Bootstrap also defines `.nav`,
  so the banner needs `flex-wrap: nowrap` set back explicitly, and Bootstrap
  scopes `.is-invalid` to its own `.form-control` classes, so a custom input needs
  its own invalid rules or a validation message points at nothing.

**The map (the live picture).**

- **Virtualised aircraft list.** Fixed 40px rows with five rows of overscan inside
  a spacer sized to the full count. The row height is a constant shared between
  the TSX and the CSS, so changing one alone breaks the scroll maths. Rows carry a
  colour indicator, a rotating aircraft glyph, callsign, and right-aligned
  altitude and speed in tabular numerals; selection is an accent left rail over
  the wash (the sidebar's active row takes the wash without the rail), and
  truth-only rows drop to 0.7 opacity. Note that the list and the map mark selection in different languages
  on purpose: the list is chrome and takes the accent, the map is data and keeps
  amber for the selected track.
- **Shadow for what floats, and only that.** The legend, the filters popover,
  the overflow menu and Leaflet's zoom and attribution controls sit over the
  tiles and share one treatment: a card-coloured fill (85% opaque on the
  attribution), a hairline and `--panel-shadow`. The detail panel, the playback bar and the aircraft list's
  inline cards sit beside the tiles or along their edge, and are flat. Nothing
  blurs what is behind it.
- **Blur as meaning.** A blurred edge means measured but approximate (node
  uncertainty discs at 5px, fuzzy coverage at 3.5px); a sharp dashed edge means a
  declared model, which is why the theoretical Yagi cone stays crisp. Worth
  preserving as a rule rather than a style.
- **Leaflet, mostly brought onto the surface.** The zoom control and the
  attribution take the surface's hairline, radius and panel shadow; popups are
  still Leaflet's own white bubbles, which read as foreign on the dark theme. How
  far the basemap is pushed back is a token, `--tile-filter`, because each theme
  has a basemap its colours were measured against: dark tints Voyager down to
  `saturate(0.85) brightness(0.78) opacity(0.82)`, light swaps in Positron and
  barely touches it (`saturate(0.9)`).

**The console's other pages.** Most listings are one shared `<DataTable>`, which
owns the header row and the two rows every page would otherwise write by hand:
a "Loading…" row while it waits and the empty text when there is nothing.
Pagination is one shared `<Pager>`, a centred Prev / Next pair with "Page N of
M" between them, used on eleven pages at a page size of 25 (50 on Storage). Tabs exist in the stylesheet (a 2px accent underline
on the active tab) but are used on exactly one page. Charts are Recharts,
coloured from `useChartTheme()` (§3), which a test holds to the tokens.

**owl and retina (the marketing sites).** Both are built from hairline-divided
row lists rather than cards: owl has three separate ones (use cases, team,
funders) that share the idiom but no class and each redeclare their own borders.
owl's other notable component is the live-radar iframe, a 4:3 near-black box with
an overlaid mono "live" label and a pulsing green dot, and no loading or error
state. retina's are the autoplaying muted video with its legend row, the pricing
block with its savings tag and tick checklist, and a fully inverted dark features
section, the only dark region on a light surface. Both carry dead CSS for
components that no longer exist in the markup: owl's three-up pillars, retina's
kit placeholder.

---

## 7. Voice and copy

Plain, specific, quietly confident. The marketing copy leads with what the thing
does ("See the sky with radio echoes", "Building the instruments science is
missing"), states numbers without hype (35 mi range, VHF/UHF, open source), and
cites literature rather than asserting authority. Technical terms are used
directly, not dumbed down, but each is given a one-line plain-English gloss.

Note the public sites use **US spelling** ("color", "Atlanta", "meter"), which
differs from the British house style used for internal docs like this one. owl-os
goes the other way and uses **British** spelling in its UI copy ("analyser"),
matching the internal docs rather than the sites. Keep a page consistent with its
surface: US spelling on the public sites, British on the node.

owl-os also carries the most second person of any surface, because it is the only
one addressing the owner of the hardware: "How your node sees", "The sky above
your node", "Use this to find your node's data". Where it has to say no, it says
why in the same breath: a greyed-out service card explains that the port is not
routed over the support tunnel, rather than leaving it to be discovered by
clicking.

---

## 8. The radar diagram motif

owl and retina both open with a bespoke SVG of the passive-radar geometry. It is
worth reusing (or extending) rather than reinventing, because it carries most of
the "this is a radar project" signal. In the **marketing diagram** the colour
semantics are:

- **Blue** = the reference / illumination signal from the broadcast transmitter,
  and node antennas.
- **Amber (`#d97706`)** = the echo returning from the target.
- **Green (`#16a34a`)** = a live node LED / status.
- **Ink / grey** = structure: ground line, tower lattice, node body, and mono
  annotations (`FM TRANSMITTER`, `NODE A`, `Δt → range & velocity`).

The diagram is annotated with the same micro-label used elsewhere, which ties it
to the rest of the page. Coverage circles use a low-opacity accent fill with a
dashed accent stroke.

**One caveat worth knowing:** this simplified green/amber scheme is a marketing
device and does _not_ match how the live map (`app.retina.fm/map`) actually
colours radar data. The public map draws no truth at all (only a synthetic
fleet's view does, in neutral or teal), radar detections run a blue↔red Doppler
gradient, and green is used for coverage polygons (see §3). So a diagram and the live map deliberately tell the same story
two different ways: keep the green/amber convention for explanatory
illustrations, and the measured scheme for anything showing genuine detections.

### The node's working relative: the flight-path simulator

owl-os carries the only other bespoke diagram in the estate, and it is the motif
turned into an instrument. Two side-by-side SVG panels, a sky elevation view and
a plan view, carry a flight path the owner drags around to see what their own
node would pick up. Its colour scheme is the surface's own tokens rather than the
marketing green/amber: the antenna beam is an 8% accent fill inside an
`--accent-edge` outline, the intended path is a dashed `--ink-subtle` line, and
what the node would actually see is drawn in solid accent. Structure is
`--line` and `--line-2`, exactly as elsewhere on the page.

Two things to carry from it. It is the one animated thing on any surface that
checks `prefers-reduced-motion` first (see §5). And it sets `touch-action: none`
on the scene, so dragging across the sky on a phone does not scroll the page out
from under the gesture.

---

## 9. Using the tokens

[`tokens.css`](tokens.css) carries every value above as CSS custom properties.
The token names are unified across the four surfaces (the live sites each use
their own naming), so a page gets one vocabulary.

```html
<link rel="stylesheet" href="tokens.css">
<body class="retina">   <!-- owl | retina | console | owl-os -->
  <h1 style="font-family: var(--font-display); font-weight: var(--heading-weight)">…</h1>
</body>
```

Add exactly one surface class (`owl`, `retina`, `console` or `owl-os`) to
`<body>`; it sets that surface's fonts, canvas, ink, accent, and radii. Add `map`
beside `console` for a map-like page: it brings the map's selection amber, its
truth colours and its lighter sunk tier. The shared `:root` layer provides the
semantic colours, base rhythm, and the `.label` / `.reveal` helpers.

The console's dark half is reached with `data-theme="dark"`, as on the live
surface, and components written against the tokens invert automatically: under
it `var(--ink)` is light and `var(--canvas)` is navy.

What this file cannot reproduce is the `system` state the console actually
defaults to, since a stylesheet of classes has no way to be handed an OS
preference. Here the bare class is the light half; there it is what shows when
the OS asks for light or cannot be asked. Build against both halves rather than
against whichever one the class gives you.

Two things to know about `.owl-os` specifically. Its colours stay in OKLCH, since
that is what the live stylesheet holds; `var()` does not care, but a value copied
out of it will not paste into a hex field. And it is the only surface where
`--border-strong` is not actually stronger, because nothing darker than the
standard hairline exists there, so it adds `--border-light` for the quieter
divider used inside a card. A component that wants a visible outline should reach for
`--border` on this surface, not `--border-strong`.

---

## 10. Improvements, gaps and discrepancies

Observations from reading the four surfaces side by side. Recorded here, not
filed as work; a snapshot of loose ends rather than a plan.

**Divergence that looks accidental rather than intentional**

- **Three unrelated type systems.** owl, retina and the console pick their own
  sans and mono, and the two marketing sites their own serif, with nothing in
  common between the three. The tiered personality is deliberate; the choice of
  *different families* for each register reads more like independent authoring
  than a considered split. A shared mono (or reusing Inter, already on owl,
  owl-os and tower-finder) would cost little and tie things together. owl-os is
  the one surface that already does this: Inter from owl, JetBrains Mono from
  retina, nothing new. It is the model the others could follow.
- **Five distinct blues.** `#5b8dd9` / `#2563eb` / `#3b82f6` / `#38bdf8` /
  `#2f8adc`. retina and the console's light half nearly agree, and the sky blue
  is the console's dark half by design; owl and owl-os each go their own way.
  One accent value per theme would read as more intentional.
- **The micro-label is mono on two surfaces and sans on two.** It is described
  here as the single most reused idiom, and it is, but the console never set it
  in its mono and owl-os has one and chooses not to. Since it is the strongest
  shared signal, settling whether it is a mono idiom or just an
  uppercase-and-tracked one would be worth more than it costs.
- **Token naming drift.** owl uses `--ink` / `--paper`, retina uses `--text` /
  `--bg`, the console uses `--bg-primary` / `--text-primary`, and owl-os uses
  `--ink` / `--bg` / `--line`. Nothing is portable between them. `tokens.css`
  proposes one naming; adopting it in the live sites would remove the drift.
  owl-os is the closest to a system already, with a deliberate three-step ink
  ramp, a colour/wash/edge triple per semantic role, and its own Bootstrap
  compatibility aliases mapping the old names onto the new ones.
- **Semantic colours drift by a shade.** Green is `#16a34a` (marketing),
  `#10b981` (the console's light half), `#33a868` (owl-os); amber and red shift
  similarly. Close enough to look like one intent, far enough to not match. (The
  console's dark half brightens its set on purpose, §3.)
- **One surface is in OKLCH and three are in hex.** owl-os's ramps are perceptual
  and its neighbours' are not, so "one step lighter" means something different
  depending on which stylesheet you are in. Not a problem while nothing is
  shared; it becomes one the moment a value is moved between surfaces.
- **Washes are alpha on three surfaces and opaque on owl-os.** An alpha wash picks
  up whatever is behind it, an opaque one does not. Both are defensible, but a
  component copied between surfaces changes behaviour silently. Only owl-os gives
  its washes a matching edge colour, which is the part most worth spreading.
- **The "truth" colour story is inconsistent.** The marketing diagrams say green
  = ADS-B truth; the map draws truth only on a synthetic fleet's view, in neutral
  or teal, and reserves green for coverage. Defensible (illustration vs data viz),
  but the homepage and the map speak two different colour languages for the
  same idea.
- **No stylesheet crosses a repository.** The console's pages and map read one
  palette and one component file, but every other surface inlines its own
  values, and tower-finder holds a hand copy of the console's, so drift is the
  default between them. `tokens.css` is the first step toward a single source.
- **Dead CSS on three surfaces.** owl's three-up pillars block, retina's kit
  placeholder, and owl-os's `.ds-textarea` / `.ds-steps` / `.ds-step` are all
  fully styled with no markup using them. Harmless, but each one reads as an
  available component to the next person building a page.
- **Only one surface can express elevation.** owl-os is alone in having a shadow
  scale; the other three have at most a shadow or two for what floats (retina's
  button lift; the console's avatar menu, the data explorer's node panel and
  download basket, what floats over the map). Any component that separates two layers by
  raising one, the segmented control being the clearest case, works on owl-os
  and flattens everywhere else, because `--surface` and `--canvas-sunk` are
  within 1.2:1 on all of them. A shared shadow token would unblock a class of
  component the other surfaces currently cannot build.

**Accessibility**

- **owl's link/accent contrast fails.** `#5b8dd9` on `#f7f6f2` is roughly 3:1,
  below the 4.5:1 AA threshold for normal text. retina's `#2563eb` is comfortably above
  it. Darkening owl's blue for links (its `--accent-strong` is a start) would fix
  the most common case.
- **owl-os fails the same way, twice over.** Its accent on its canvas is ~3.6:1,
  and `--ink-3`, the colour of every help line under every field at 12px, is
  also ~3.6:1. The help text is the larger problem of the two, since it carries
  the explanation of what the setting does and is set smaller than the label it
  explains. Both are one OKLCH lightness step from passing: dropping either to
  `oklch(0.56 …)` clears 4.5:1 without touching its hue or chroma.
- **`prefers-reduced-motion` is honoured in places, not as a rule.** owl's and
  retina's home pages run infinite animations (pulses, dashed signal flow, ring
  expansions) with no guard, and their SVG loops need one as much as their CSS
  does. The map guards its whole page with a single block, though the rest of
  the console has none; owl-os's flight-path simulator checks before it starts,
  and owl's `/learn` page carries its own. Between them they show the pattern is
  cheap. The `tokens.css` `.reveal` helper adds the guard for new work.
- **Focus styles.** Only the map defines a visible `:focus-visible` treatment
  across a whole page, an accent outline; everywhere else keyboard focus rides
  on the browser default. The rest of the console is a third of the way there:
  its inputs clear the outline and take an accent border, a 1px hue change
  carrying the whole cue, and two scoped `:focus-visible` rings exist (the
  sign-in page's back link and the data explorer's node map), but its buttons and
  links get nothing. owl-os is halfway: its inputs take an accent border plus a
  3px accent ring on `:focus`, but as `:focus` rather than `:focus-visible`, so
  the ring also fires on mouse click, and its buttons and links get nothing at
  all. owl and retina contain no `:focus` rule whatsoever. The map's one-line
  rule is the model to copy, and would cover the whole console with only its
  `.app.map-surface` scope widened.

**Polish**

- **Missing social metadata.** None of them set `og:image` / `twitter:card` /
  canonical, so link previews are bare. A single shared OG image per surface would
  help. owl-os is the one case where this genuinely does not matter: it is served
  off a box on a home network and cannot be linked to from anywhere.
- **The console carries little brand.** It dropped the type system for system
  fonts and cool slate, and agrees with almost nothing on the marketing sites
  beyond a blue accent and the uppercase micro-label. Standardising the
  micro-label and reusing one blue would connect all four without slowing the
  tools down. owl-os is the counter-example worth pointing at: it is just as much
  a tool and still carries the warm canvas, a branded mono, and the
  hairline-and-micro-label idiom intact.
- **owl-os is the only surface on a CSS framework.** Bootstrap 5.3 arrives from a
  CDN and is then overridden token by token. It works, but it means the surface
  carries a second, competing set of component styles, and the guide's §6 notes
  two places where the two have already collided. Anything new built for a node
  should be written against the tokens, not against Bootstrap.
- **What a node runs is not what this describes.** owl-os pins retina-gui at a
  tag when it bakes the image (`retina_gui_version` in
  `plugins/playbooks/os_setup/versions.yml`), so the style captured here, read
  from retina-gui `main`, runs ahead of the fleet until the next image. Check
  the pin before assuming a node has a component this guide describes.
- **The map is the only thing measured rather than eyeballed.** Its data palette
  is held to a contrast floor against its own basemap and a CIEDE2000 distance
  between marks, in both themes (§3). The console's chrome ramp is not covered by
  that, and neither is any other surface: the accessibility notes above were
  checked against the light surfaces by inspection.
- **Inconsistent animation approach.** retina's hero uses inline SVG SMIL
  (`<animate>`) while owl and the console use CSS keyframes. Standardising on CSS
  would make the shared radar motif portable.
- **A colour reference that resolves to the wrong thing.** owl-os's calibration
  spinner carries Bootstrap's `.text-primary`, which its override block does not
  redefine, so that one spinner is Bootstrap blue `#0d6efd` rather than the
  surface accent.
- **The console is unreachable on a phone.** Its 250px sidebar, and the collapse
  toggle inside it, is `display: none` under 768px with no hamburger and no
  replacement, so there is no way to move between pages at that width. The map
  and the data explorer, the pages most likely to be opened from a shared link
  on a phone, sit in the same shell. Worth confirming against real usage before
  treating it as intentional.
- **A native dialog on a designed surface.** The console confirms graduating a
  polled radar with `window.confirm()`, unstyled OS chrome in the middle of a
  console that otherwise controls every pixel, when it already holds two styled
  alternatives written against the same tokens: the map's modal for a decision,
  the data explorer's drawer for something to read.
