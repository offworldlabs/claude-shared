# Brand guide

> A snapshot of how the Offworld Labs surfaces look today, gathered so a new page
> can match them without guessing. This captures **what we have**, not a target
> we are aiming for: where the sites disagree, that is recorded rather than
> resolved. Treat it as a description to build against, and update it when the
> sites change rather than the other way round.
>
> Companion file: [`tokens.css`](tokens.css) holds the same values as CSS custom
> properties, so a page can consume them instead of transcribing hex codes.

The design lives in five hand-authored surfaces, none of which shares a
stylesheet with the others:

- **offworldlabs.com** ([`landing-page-owl`](https://github.com/offworldlabs/landing-page-owl)) — the lab
- **retina.fm** ([`landing-page-retina`](https://github.com/offworldlabs/landing-page-retina)) — the product
- **dash.retina.fm** (`retina-server/dashboard`) — the admin console
- **map.retina.fm** (`retina-server/frontend`) — the live radar map
- **owl.local** ([`retina-gui`](https://github.com/offworldlabs/retina-gui)) — the node's own UI

They read as one family, but each has its own voice. Two sit apart: the map is
the only dark surface, a Flightradar24-style operational console, and owl-os is
the only one that runs on hardware in someone's house rather than on a server.

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
maps onto audience. Four are light; the map is dark.

| | **owl** — offworldlabs.com | **retina** — retina.fm | **dash** — dash.retina.fm | **map** — map.retina.fm | **owl-os** — owl.local |
|---|---|---|---|---|---|
| **Role** | The lab / parent org | The product you buy | The console you operate | The live picture | The node you own |
| **Audience** | Researchers, funders, press | Prospective node owners | Logged-in operators | Anyone watching the map | Whoever has the box |
| **Feel** | Editorial, institutional | Commercial, confident | Utilitarian, dense | Dark ops console (FR24-style) | Appliance settings, unhurried |
| **Serif** | Source Serif 4, wt 400 | Fraunces, wt 600 | none | none | none |
| **Sans** | Inter | DM Sans | system stack | Inter (only font) | Inter |
| **Mono** | IBM Plex Mono | JetBrains Mono | SF Mono | none (generic) | JetBrains Mono |
| **Canvas** | warm paper `#f7f6f2` | warm paper `#fafaf9` | cool slate `#f1f5f9` | **navy `#0d1b2a`** | near-white warm `#fffdfb` |
| **Blue** | muted `#5b8dd9` | punchy `#2563eb` | `#3b82f6` → `#2563eb` | sky `#38bdf8` | `#2f8adc`, accents only |
| **Radius** | 4–6px | 8–20px | 4–8px | 3–10px | 6–14px |
| **Buttons** | flat | lift + shadow | flat | flat | flat, primary is ink |
| **Dark UI** | none | one dark section | none | **fully dark** | none |

A rough rule of thumb for a new page: **who is it for?** Reaching outward to the
scientific or funding world reads as owl. Selling or explaining the kit reads as
retina. Anything behind a login reads as dash. Anything that _is_ the live radar
picture (a map, a track view, an operational overlay) reads as map. Anything a
node owner does to their own hardware reads as owl-os.

dash and owl-os are worth telling apart, since both are settings pages for the
same hardware. dash is an operator holding a fleet at arm's length: dense,
tabular, many rows on one screen, always behind a login. owl-os is one person and
one box on their own network, reached without a password, so it runs a 720px
column, one decision per row, and explains each in a sentence underneath.

---

## 2. Foundations

The parts that stay roughly constant across all five, and are the safest thing
to carry into new work.

- **A paper-like canvas.** Four of the five use a near-white background (warm on
  the marketing sites and owl-os, cool slate on the console) with near-black
  text; owl-os pushes furthest toward white at `#fffdfb`. The **map is the
  exception**: it is fully dark navy with light slate text. So "light paper" is
  the norm for anything that explains, sells or configures, and dark is reserved
  for the live operational view.
- **A blue accent.** owl sits soft and desaturated, retina and dash land on the
  brighter `#2563eb`/`#3b82f6`, owl-os lands between them at `#2f8adc`, and the
  map goes brighter still (sky `#38bdf8`) to carry on dark. Blue is the only
  chromatic accent in the UI chrome; everything else is ink on canvas. (The map
  adds an amber `#fbbf24` as a selection/focus highlight.) owl-os spends its blue
  the most sparingly: the primary button is ink, and the accent is kept for focus
  rings, hover borders, selection washes and the one card that is _this_ node.
- **Green and amber as status colours.** Green marks "live" / validated / ADS-B
  truth; amber marks the radar echo, anomalies, and attention. The console adds
  red for outright errors. (The exact shades drift between surfaces; see §10.)
- **A small uppercase micro-label.** Small, uppercase, letter-spaced, muted.
  Used for section eyebrows, stat labels, table headers, nav-section titles, and
  diagram annotations. This is the single most reused idiom and the quickest way
  to make a new page read as "ours". All five surfaces have it. The marketing
  sites and console set it in their mono; the map and owl-os keep the
  uppercase-and-tracked treatment for section and panel headers in their sans,
  the map because it has no mono and owl-os by choice (it has JetBrains Mono and
  spends it on data instead).
- **Hairline rules and grid dividers.** 1px borders at low contrast separate
  sections, table rows, fact lists, and card grids. Structure comes from lines,
  not shadows or fills.
- **Flat and quiet.** Minimal ornamentation, few shadows (retina uses a subtle
  button lift; dash reserves shadow for one dropdown), small status dots for
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
roles (semantics) are shared unless a surface overrides them.

### Canvas and ink

| Role | owl | retina | dash | map | owl-os |
|---|---|---|---|---|---|
| Canvas | `#f7f6f2` | `#fafaf9` | `#f1f5f9` | `#0d1b2a` | `#fffdfb` |
| Sunk surface | `#edecea` | `#f5f4f0` | `#f8fafc` | `#0f2035` | `#fbfaf8` |
| Card / panel | `#ffffff` | `#ffffff` | `#ffffff` | `#132240` | `#ffffff` |
| Dark section | — | `#090904` / `#242422` | — | (all dark) | — |
| Ink (primary) | `#0e0e0c` | `#1a1a18` | `#0f172a` | `#e2e8f0` | `#13161c` |
| Ink (muted) | `#444440` | `#6b6b63` | `#475569` | `#94a3b8` | `#494d54` |
| Ink (subtle) | `#888882` | `#9c9c93` | `#94a3b8` | `#64748b` | `#83868c` |
| Border | `rgba(14,14,12,.1)` | `#e8e8e3` | `#e2e8f0` | `rgba(100,180,255,.12)` | `#eae7e4` |

The marketing canvases are warm (a hint of yellow); the console is cool slate;
the map inverts to dark navy. The map's ink ramp is the dark mirror of the
console's slate ramp (`#94a3b8` / `#64748b` recur), and its hairlines are a
blue-tinted translucent white rather than a solid grey.

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

| | owl | retina | dash | map | owl-os |
|---|---|---|---|---|---|
| Accent | `#5b8dd9` | `#2563eb` | `#3b82f6` | `#38bdf8` | `#2f8adc` |
| Hover / strong | `#4a7cc8` | `#3b82f6` | `#2563eb` | `#7dd3fc` | `#1a7acb` |
| Wash | `rgba(91,141,217,.15)` | `rgba(37,99,235,.06)` | `rgba(59,130,246,.10)` | `rgba(56,189,248,.15)` | `#e3f4ff` (opaque) |
| Wash edge | — | `rgba(37,99,235,.15)` | — | — | `#c4daf2` |

owl's blue is deliberately soft and low-contrast (an editorial choice, though it
costs link legibility, see §10). retina and dash share the saturated blue, with
dash resting one step lighter and hovering to retina's resting value. The map
pushes to a brighter sky-blue so the accent reads on navy. owl-os sits between
dash and the map, a shade cyan-ward of both. Five distinct blues in all.

Two things owl-os does differently with it. Its washes are **opaque tints**, not
alpha overlays, so a wash keeps its colour over any ground it lands on rather
than picking up whatever is behind it. And every wash carries a matching **edge**
one step darker (`#c4daf2` for the accent, `#bee2c9` for success), so a tinted
region is bounded rather than bleeding into the page. The map adds an amber
`#fbbf24` for a selection/focus highlight; owl-os uses the accent wash plus a
3px inset rail for the same job.

### Semantics

| Role | Marketing (owl, retina) | Console (dash) | Map (map) | Node (owl-os) |
|---|---|---|---|---|
| Success / good | `#16a34a` | `#10b981` (emerald) | `#4ade80` | `#33a868` |
| Warning / attention | `#d97706` | `#f59e0b` (amber-500) | `#fbbf24` | `#e1a035` |
| Error | (unused) | `#ef4444` (red-500) | `#f43f5e` | `#e64343` |

Same three roles, brightened a step on the dark map so they carry on navy, and
landing between the marketing and console sets on owl-os. Each pairs with a wash
(~10% on light, ~15% on dark; opaque on owl-os) for tinted pill backgrounds. The
console's charts extend the accent into a categorical palette (`#3b82f6,
#10b981, #f59e0b, #ef4444, #8b5cf6, #ec4899, #06b6d4, #84cc16, #f97316,
#14b8a6`, with `#94a3b8` for an "others" slice); reuse that ordering for any new
dashboard chart.

The map's live data colours are a separate, radar-specific scheme, not these
status roles: "truth" (solver agreeing with ADS-B) is **teal `#2dd4bf`**, the
ground-truth dot is **cyan `#22d3ee`**, and radar detections run a **Doppler
gradient** from dark-blue approaching (`#1e3a8a`) through cyan at zero (`#22d3ee`)
to dark-red receding (`#991b1b`). Green there means coverage polygons, not truth.
See §8.

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
console collapses everything into the system stack; the map collapses everything
into Inter.

| Register | owl | retina | dash | map | owl-os |
|---|---|---|---|---|---|
| Display | Source Serif 4 | Fraunces | system sans | Inter | Inter |
| Body | Inter | DM Sans | system sans | Inter | Inter |
| Mono | IBM Plex Mono | JetBrains Mono | SF Mono | generic `monospace` | JetBrains Mono |

Loaded from Google Fonts on the marketing sites, the map (Inter) and owl-os; the
console loads no web fonts at all (its CSP restricts `font-src`). Only the two
marketing sites use a serif; the three operational surfaces (dash, map, owl-os)
are sans-only.

owl-os is the only surface that borrows both its faces from siblings rather than
choosing new ones (Inter from owl and the map, JetBrains Mono from retina), and
so is the least type-divergent of the five. It also asks Inter for
`font-feature-settings: 'ss01', 'cv11'` (the single-storey `g` and the
straight-tailed `l`), which is what stops a screen full of node IDs and
frequencies from reading as body copy.

**Heading weight is the other big tell.** owl sets headings at 400 (light,
serious, editorial); retina and owl-os at 600 (present, product-confident); dash
and map at 700 (compact, functional). Marketing headings carry a tight
`letter-spacing` around `-0.02em` and line-height near 1.1; the operational
surfaces run text small (down to ~0.62rem) and dense.

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
  wizard step alike. Console page titles are a flat 24px.
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

| | owl | retina | dash | map | owl-os |
|---|---|---|---|---|---|
| Radius (default) | 4px | 12px | 8px | 6px | 10px |
| Radius (small) | 3px | 8px | 4px | 3px | 6px |
| Radius (large) | 6px | 20px | 12px | 10px | 14px |

Crisp on owl, soft on retina, moderate on dash, tight on the map, second-softest
on owl-os. Borders are always 1px hairlines; nothing uses a heavy stroke. The map
builds elevation from backdrop-blur (14–20px) and subtle shadow rather than
cards, since its panels float over the map.

owl-os is the only surface with a real elevation scale: a hairline `shadow-sm` at
rest, a 24px-blur `shadow-md` on hover and for the sticky save bar, and a
`shadow-pop` for modals. All three are tinted with the ink colour rather than
black, so a raised card warms rather than greys.

### Space

- Marketing content sits in a centred column: `max-width` 860px for prose,
  1120–1200px for wide/hero rows. The console is full-width and fluid with a
  250px sidebar. The map is full-bleed: a 280px left aircraft list (collapsing
  to 36px), a 280px right detail panel, and a full-width bottom playback bar.
- owl-os runs a 720px column on Home, a 200px + fluid two-column shell on Config
  (max 1100px), and a fixed 560px column for every wizard step. One decision per
  row, with its explanation directly underneath.
- Nav / header height: 56px (owl), 64px (retina), 56px (dash). owl-os stacks two
  rows instead, a fleet bar over the page tabs, and its config side-nav sticks
  below both at 58px.
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

owl and dash animate in CSS; retina's hero mixes in inline SVG SMIL (`<animate>`).

owl-os runs none of the three. It defines no `@keyframes` at all: motion is
limited to 120ms colour, border and shadow transitions on hover, a 150ms switch
throw, and a 2px nudge on a card's arrow. Nothing on the page moves unless it was
touched, which is reasonable for a settings surface someone reaches when
something needs fixing, and the reason its one animated component, the simulator,
is also the only place on any surface that checks `prefers-reduced-motion` before
starting. Everything else across all five surfaces still runs its loops
unguarded; the `tokens.css` `.reveal` helper adds the guard, and new work should
keep it.

---

## 6. Components

- **Nav.** Fixed top bar, `backdrop-filter: blur(...)` over a translucent
  canvas, a hairline bottom border. Logo left (mono wordmark, or logo + mono
  text on owl), links centre/left, a primary CTA right. Collapses to a hamburger
  under ~860–960px.
- **Buttons.** Primary = solid ink (marketing) or solid accent (console),
  inverse text, small radius. owl and dash keep them flat; retina lifts them
  (`translateY(-1px)` + soft shadow) on hover. Secondary = text link with a
  hairline underline (owl), or an outline button (retina/dash).
- **Section eyebrow.** A `.label` micro-label above each H2 naming the section
  ("About", "Flagship project", "Capabilities"). The consistent opener for a
  marketing section.
- **Fact rows / metrics.** Label-value pairs on hairline-divided rows (owl's
  RETINA facts), or a bordered 4-up metrics bar (retina). Values in the display
  face, labels muted. A tidy way to present specs.
- **Cards.** White, 1px border, surface radius, no shadow. Grids of cards use a
  1px gap over a border-coloured background so the dividers read as shared lines
  (retina's steps/features, dash's panels).
- **Badges / pills.** Rounded (12px), tinted `-wash` background with matching
  text colour, often a leading status dot. Success/warning/error on the console;
  "live" on the marketing sites.
- **Footer.** Hairline top border, mono wordmark left, muted links, a `© 2026`
  line. Understated. owl-os fills its footer with versions instead (node ID,
  owl-os version, retina-node version, each value in mono), so the first thing
  anyone is asked for in a support conversation is already on screen.

The node UI adds several components the other surfaces have no use for. They are
worth knowing about before building anything else that runs on a node.

- **Fleet bar over page tabs.** Two stacked rows reading as one banner: the
  parent row is every node on the network (each an absolute link to its own
  `ret<node_id>.local`, the current one included), the child row is which page of
  this node. The child row is set apart by a lighter ground and no border of its
  own. The tab strip is the only part that gives under pressure: it scrolls
  rather than wrapping or squashing the furniture around it.
- **Wizard shell.** A fixed head / scrolling body / fixed foot at `100dvh`, body
  capped at 560px. Progress is a row of 24×4px bars, not numbered circles: ink
  for done, accent for the current step, hairline for what is ahead.
- **Switches and segmented controls.** A 36×20px track that fills with **ink**
  when on, not accent, since on/off is not a brand moment; plus an inset
  segmented control whose active segment is a raised white pill.
- **Sticky save bar.** Pinned to the bottom of the config page with a shadow and
  a live count of what has changed, so a long form never hides the fact that it
  has unsaved edits.
- **Rail-marked selection.** The selected row of a table, the active side-nav
  link and the matching manage-list item all take a 2–3px `inset` box-shadow
  rail plus a wash, rather than a border change. Selection reads without shifting
  layout by a pixel.
- **Peak meter.** A segmented dBFS ladder per tuner, styled as rack gear, with
  the reading in tabular mono to its right and an alarm state in `--danger`.
- **Line-art icons.** 24×24 stroke SVGs inlined in the markup at `stroke-width:
  1.6`, round caps and joins, `currentColor`. No icon font, no sprite sheet. The
  antenna mark (a dot under two arcs, on a mast) is the node glyph, and it means
  the same thing everywhere it appears: a nav tab, a node card, a "listening on"
  row.
- **Bootstrap underneath.** owl-os is the only surface built on a CSS framework
  (Bootstrap 5.3 from a CDN), with a block of overrides mapping Bootstrap's
  components onto the tokens. Two consequences worth carrying: Bootstrap also
  defines `.nav`, so the banner needs `flex-wrap: nowrap` set back explicitly,
  and Bootstrap's `.is-invalid` styling is scoped to its own `.form-control`
  classes, so a custom input needs its own invalid rules or a validation message
  points at nothing.

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
device and does _not_ match how the live map (map.retina.fm) actually colours
radar data. On the real map, "truth" is teal/cyan, radar detections run a
blue↔red Doppler gradient, and green is used for coverage polygons (see §3). So
a diagram and the live map deliberately tell the same story two different ways:
keep the green/amber convention for explanatory illustrations, and the
Doppler/teal scheme for anything showing genuine detections.

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
The token names are unified across the five surfaces (the live sites each use
their own naming), so a page gets one vocabulary.

```html
<link rel="stylesheet" href="tokens.css">
<body class="retina">        <!-- owl | retina | dash | map | owl-os -->
  <h1 style="font-family: var(--font-display); font-weight: var(--heading-weight)">…</h1>
</body>
```

Add exactly one surface class (`owl`, `retina`, `dash`, `map` or `owl-os`) to
`<body>`; it sets that surface's fonts, canvas, ink, accent, and radii. The `map`
class is dark, so `var(--ink)` is light and `var(--canvas)` is navy: components
written against the tokens invert automatically. The shared `:root` layer
provides the semantic colours, base rhythm, and the `.label` / `.reveal` helpers.

Two things to know about `.owl-os` specifically. Its colours stay in OKLCH, since
that is what the live stylesheet holds; `var()` does not care, but a value copied
out of it will not paste into a hex field. And it is the only surface where
`--border-strong` is not actually stronger, because nothing darker than the
standard hairline exists there, so it adds `--border-light` for the quieter
divider used inside a card. A component that wants a visible outline should reach for
`--border` on this surface, not `--border-strong`.

---

## 10. Improvements, gaps and discrepancies

Observations from reading the five surfaces side by side. Recorded here, not
filed as work; a snapshot of loose ends rather than a plan.

**Divergence that looks accidental rather than intentional**

- **Four unrelated type systems.** owl, retina and dash use three different
  serifs, sans and monos between them; the map adds a fourth by going Inter-only.
  The tiered personality is deliberate; the choice of *different families* for
  each register reads more like independent authoring than a considered split. A
  shared mono (or reusing Inter, already on three surfaces), would cost little and
  tie things together. owl-os is the one surface that already does this: Inter
  from owl and the map, JetBrains Mono from retina, nothing new. It is the model
  the others could follow.
- **Five distinct blues.** `#5b8dd9` / `#2563eb` / `#3b82f6` / `#38bdf8` /
  `#2f8adc`. dash and retina nearly agree; owl, map and owl-os each go their own
  way. One accent value, or a documented light/dark pair, would read as more
  intentional.
- **The micro-label is mono on three surfaces and sans on two.** It is described
  here as the single most reused idiom, and it is, but the map has no mono to
  set it in and owl-os has one and chooses not to. Since it is the strongest
  shared signal, settling whether it is a mono idiom or just an
  uppercase-and-tracked one would be worth more than it costs.
- **Token naming drift.** owl uses `--ink` / `--paper`, retina uses `--text` /
  `--bg`, dash uses `--bg-primary` / `--text-primary`, owl-os uses `--ink` /
  `--bg` / `--line`, and the map has no custom properties at all (hardcoded hex
  throughout). Nothing is portable between them. `tokens.css` proposes one
  naming; adopting it in the live sites would remove the drift. owl-os is the
  closest to a system already, with a deliberate three-step ink ramp, a
  colour/wash/edge triple per semantic role, and its own Bootstrap compatibility
  aliases mapping the old names onto the new ones.
- **Semantic colours drift by a shade.** Green is `#16a34a` (marketing),
  `#10b981` (console), `#4ade80` (map), `#33a868` (owl-os); amber and red shift
  similarly. Close enough to look like one intent, far enough to not match.
- **One surface is in OKLCH and four are in hex.** owl-os's ramps are perceptual
  and its neighbours' are not, so "one step lighter" means something different
  depending on which stylesheet you are in. Not a problem while nothing is
  shared; it becomes one the moment a value is moved between surfaces.
- **Washes are alpha on four surfaces and opaque on owl-os.** An alpha wash picks
  up whatever is behind it, an opaque one does not. Both are defensible, but a
  component copied between surfaces changes behaviour silently. Only owl-os gives
  its washes a matching edge colour, which is the part most worth spreading.
- **The "truth" colour story is inconsistent.** The marketing diagrams say green
  = ADS-B truth; the live map says teal/cyan = truth and reserves green for
  coverage. Defensible (illustration vs data viz), but a viewer moving from the
  homepage to the map meets two different colour languages for the same idea.
- **No shared stylesheet.** Every value is inlined per surface, so drift is the
  default. `tokens.css` is the first step toward a single source.

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
- **No `prefers-reduced-motion`, with one exception.** The four animated surfaces
  run infinite animations (pulses, dashed signal flow, ring expansions, the map's
  pulsing "LIVE" badge) with no reduced-motion guard. The `tokens.css` `.reveal`
  helper adds one; the SVG loops need the same treatment. owl-os's flight-path
  simulator is the only thing in the estate that already checks, and it shows the
  pattern is cheap.
- **Focus styles.** None of the surfaces define a visible `:focus-visible`
  treatment; keyboard focus rides on the browser default. owl-os is halfway
  there: its inputs take an accent border plus a 3px accent ring on `:focus`, but
  as `:focus` rather than `:focus-visible`, so the ring also fires on mouse
  click, and its buttons and links get nothing at all.

**Polish**

- **Missing social metadata.** None of them set `og:image` / `twitter:card` /
  canonical, so link previews are bare. A single shared OG image per surface would
  help. owl-os is the one case where this genuinely does not matter: it is served
  off a box on a home network and cannot be linked to from anywhere.
- **The operational surfaces carry little brand.** dash dropped the type system
  for system fonts and cool slate; the map runs Inter-only on dark navy with a
  brighter blue. Both are defensible for tools, but between them they share
  almost nothing visible with the marketing brand beyond a blue accent and the
  uppercase micro-label. Standardising the micro-label and reusing one blue would
  connect all five without slowing the tools down. owl-os is the counter-example
  worth pointing at: it is just as much a tool and still carries the warm canvas,
  a branded mono, and the hairline-and-micro-label idiom intact.
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
- **The dark map is unaudited for contrast here.** The accessibility notes above
  were checked against the light surfaces; the map's light-slate-on-navy ramp
  looks reasonable but has not been contrast-tested, and it inherits the same
  no-`prefers-reduced-motion`, no-`:focus-visible` gaps.
- **Inconsistent animation approach.** retina's hero uses inline SVG SMIL
  (`<animate>`) while owl and dash use CSS keyframes. Standardising on CSS would
  make the shared radar motif portable.
