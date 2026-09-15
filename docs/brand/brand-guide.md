# Brand guide

> A snapshot of how the Offworld Labs surfaces look today, gathered so a new page
> can match them without guessing. This captures **what we have**, not a target
> we are aiming for: where the sites disagree, that is recorded rather than
> resolved. Treat it as a description to build against, and update it when the
> sites change rather than the other way round.
>
> Companion file: [`tokens.css`](tokens.css) holds the same values as CSS custom
> properties, so a page can consume them instead of transcribing hex codes.

The design lives in six hand-authored surfaces, none of which shares a
stylesheet with the others:

- **offworldlabs.com** ([`landing-page-owl`](https://github.com/offworldlabs/landing-page-owl)) — the lab
- **retina.fm** ([`landing-page-retina`](https://github.com/offworldlabs/landing-page-retina)) — the product
- **dash.retina.fm** (`retina-server/dashboard`) — the admin console
- **data.retina.fm** (`retina-server/data-explorer`) — the public archive browser
- **map.retina.fm** (`retina-server/frontend`) — the live radar map
- **owl.local** ([`retina-gui`](https://github.com/offworldlabs/retina-gui)) — the node's own UI

They read as one family, but each has its own voice. Two sit apart: the map is
the only one dark by default, a Flightradar24-style operational console; owl-os
is the only one that runs on hardware in someone's house rather than on a
server.

**Three of them theme, on one palette.** The map has offered light beside its
default dark for longest; dash and data now carry both halves of that same pair
rather than inventing a ramp of their own, and follow the OS unless told
otherwise (§3). The other three are light only. `admin.retina.fm` is dash's own
bundle behind a role check rather than a seventh surface, so it themes with it
and is not listed separately anywhere below.

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

## 1. Brand architecture: one family, six voices

The surfaces share a spine (a blue accent, green/amber status colours, a small
uppercase micro-label, hairline rules) and then diverge in personality. The split
maps onto audience. Three of the six are light and nothing else; the other
three carry both halves of one palette pair, and differ in what decides which
half you get (§3).

| | **owl** — offworldlabs.com | **retina** — retina.fm | **dash** — dash.retina.fm | **data** — data.retina.fm | **map** — map.retina.fm | **owl-os** — owl.local |
|---|---|---|---|---|---|---|
| **Role** | The lab / parent org | The product you buy | The console you operate | The archive you fetch from | The live picture | The node you own |
| **Audience** | Researchers, funders, press | Prospective node owners | Logged-in operators | Anyone wanting the data | Anyone watching the map | Whoever has the box |
| **Feel** | Editorial, institutional | Commercial, confident | Utilitarian, dense | Utilitarian, dense | Dark ops console (FR24-style) | Appliance settings, unhurried |
| **Serif** | Source Serif 4, wt 400 | Fraunces, wt 600 | none | none | none | none |
| **Sans** | Inter | DM Sans | system stack | system stack | Inter (only font) | Inter |
| **Mono** | IBM Plex Mono | JetBrains Mono | SF Mono | SF Mono | none (generic) | JetBrains Mono |
| **Canvas** | warm paper `#f7f6f2` | warm paper `#fafaf9` | cool slate `#f1f5f9`, dark `#0d1b2a` | cool slate `#f1f5f9`, dark `#0d1b2a` | **navy `#0d1b2a`**, light `#f1f5f9` | near-white warm `#fffdfb` |
| **Blue** | muted `#5b8dd9` | punchy `#2563eb` | `#3b82f6` → `#2563eb`, dark `#38bdf8` | `#3b82f6` → `#2563eb`, dark `#38bdf8` | sky `#38bdf8`, light `#3b82f6` | `#2f8adc`, accents only |
| **Radius** | 4–6px | 8–20px | 4–8px | 4–8px | 2–12px | 6–14px |
| **Buttons** | flat | lift + shadow | flat | flat | flat | flat, primary is ink |
| **Dark UI** | none | one dark section | **follows the OS**, the map's palette | **follows the OS**, the map's palette | **dark by default**, light opt-in | none |

A rough rule of thumb for a new page: **who is it for?** Reaching outward to the
scientific or funding world reads as owl. Selling or explaining the kit reads as
retina. Anything behind a login reads as dash. Anything that hands the public
the archive reads as data, which is dash's vocabulary without the login and
without the sidebar. Anything that _is_ the live radar picture (a map, a track
view, an operational overlay) reads as map. Anything a node owner does to their
own hardware reads as owl-os.

dash and owl-os are worth telling apart, since both are settings pages for the
same hardware. dash is an operator holding a fleet at arm's length: dense,
tabular, many rows on one screen, always behind a login. owl-os is one person and
one box on their own network, reached without a password, so it runs a 720px
column, one decision per row, and explains each in a sentence underneath.

---

## 2. Foundations

The parts that stay roughly constant across all six, and are the safest thing
to carry into new work.

- **A paper-like canvas.** Three of the six are near-white and only near-white
  (warm on the marketing sites, `#fffdfb` on owl-os, which pushes furthest
  toward white). dash and data are cool slate on a light OS and navy on a dark
  one; the **map is navy** whatever the OS says. So "light paper" is the norm
  for anything that explains or sells, and the three surfaces that operate the
  network are the three that can go dark (§3).
- **A blue accent.** owl sits soft and desaturated, retina and dash land on the
  brighter `#2563eb`/`#3b82f6`, owl-os lands between them at `#2f8adc`, and the
  map goes brighter still (sky `#38bdf8`) to carry on dark, dropping back to
  dash's `#3b82f6` when it is themed light. Blue is the only chromatic accent in
  the UI chrome; everything else is ink on canvas. (The map adds an amber
  `#fbbf24` as a selection/focus highlight.) owl-os spends its blue
  the most sparingly: the primary button is ink, and the accent is kept for focus
  rings, hover borders, selection washes and the one card that is _this_ node.
  data spends dash's blue on light and the map's on dark, adding none of its own.
- **Green and amber as status colours.** Green marks "live" / validated / ADS-B
  truth; amber marks the radar echo, anomalies, and attention. The consoles add
  red for outright errors. (The exact shades drift between surfaces; see §10.)
- **A small uppercase micro-label.** Small, uppercase, letter-spaced, muted.
  Used for section eyebrows, stat labels, table headers, nav-section titles, and
  diagram annotations. This is the single most reused idiom and the quickest way
  to make a new page read as "ours". All six surfaces have it, and only the two
  marketing sites set it in their mono. dash, data, the map and owl-os keep the
  uppercase-and-tracked treatment in their sans: the two consoles because dash
  never spent its mono on it (stat labels, table headers and nav-section titles
  are all the system stack, and data copied that), the map because it has no
  mono, and owl-os by choice, having JetBrains Mono and spending it on data
  instead.
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

| Role | owl | retina | dash / data | map | owl-os |
|---|---|---|---|---|---|
| Canvas | `#f7f6f2` | `#fafaf9` | `#f1f5f9` | `#0d1b2a` | `#fffdfb` |
| Sunk surface | `#edecea` | `#f5f4f0` | `#f1f5f9` (= canvas) | `#0f2035` | `#fbfaf8` |
| Card / panel | `#ffffff` | `#ffffff` | `#ffffff` | `#132240` | `#ffffff` |
| Dark section | — | `#090904` / `#242422` | — | (the dark theme) | — |
| Ink (primary) | `#0e0e0c` | `#1a1a18` | `#0f172a` | `#e2e8f0` | `#13161c` |
| Ink (muted) | `#444440` | `#6b6b63` | `#475569` | `#94a3b8` | `#494d54` |
| Ink (subtle) | `#888882` | `#9c9c93` | `#94a3b8` | `#64748b` | `#83868c` |
| Border | `rgba(14,14,12,.1)` | `#e8e8e3` | `#e2e8f0` | `rgba(100,180,255,.14)` | `#eae7e4` |

**dash and data share a column because they share every value in it.** data was
built by copying dash's token block, and the two have not diverged; where the
rest of this guide says "dash" about a colour, it is true of data as well.

The marketing canvases are warm (a hint of yellow); the consoles are cool slate;
the map inverts to dark navy. The map's ink ramp is the dark mirror of the
console's slate ramp (`#94a3b8` / `#64748b` recur), and its hairlines are a
blue-tinted translucent white rather than a solid grey.

**The map's column above is its dark theme, which is the default there.** These
are not two palettes but one pair, and three surfaces now run it. The map's
light theme takes dash's values almost wholesale (§10 has the one exception),
and dash and data carry the same pair with the halves the other way up.

**What decides which half you get is not the same question on the two**, and it
is the part most easily got wrong. dash and data **follow the OS**: their
control has three states, and the third, `system`, is the default and the one a
viewer who has never touched the control is on. It stamps no attribute at all
and lets a `prefers-color-scheme` block answer, so the preference keeps working
when the OS changes its mind mid-session — where stamping a resolved value
would pin the surface to whatever the OS happened to be at load. The map
**never asks the OS**: its control is a boolean, and dark is what a first visit
gets on a machine set to light.

What all three do share is the cascade rule. A surface puts on its bare selector
the half it must be able to paint before any JavaScript runs, and spends
`data-theme` on the other: dark on the map, light on dash and data. The
attribute is stamped from JavaScript, so whichever half depends on it is the one
that can flash the other before first paint. On dash and data the media query is
guarded `:not([data-theme="light"])`, which is what lets an explicit light
choice beat a dark OS. Everything on all three is written against the custom
properties, so the whole chrome inverts from one block.

Two tokens exist because of that sharing.

**`--bg-sunk` is the third surface tier**, and all three themed surfaces carry
it. On a light surface a recessed region can be made by letting the canvas show
through, the canvas already being darker than a card; the dark ramp inverts,
card lighter than canvas, so a recessed pane needs a colour of its own at
`#0f2035`. It pays for the map's left aircraft list and, on the Physics tab, the
scene, ground-truth and solver sections, and for data's appearance switch. The
light half of it is the one value the three do not agree on (§10).

**`--accent-ink` is what sits _on_ the accent** rather than beside it, and is
dash's and data's alone — the map defines none. It is a token and not a literal
white because the dark accent is a bright sky blue, on which white is about
1.8:1; there it becomes a near-black `#082f49`. Any solid accent fill carrying
text — a primary button, the sidebar mark — needs it, so a component moved onto
the map has to bring its own answer.

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

| | owl | retina | dash / data | map | owl-os |
|---|---|---|---|---|---|
| Accent | `#5b8dd9` | `#2563eb` | `#3b82f6` | `#38bdf8` | `#2f8adc` |
| Hover / strong | `#4a7cc8` | `#3b82f6` | `#2563eb` | `#7dd3fc` | `#1a7acb` |
| Wash | `rgba(91,141,217,.15)` | `rgba(37,99,235,.06)` | `rgba(59,130,246,.10)` | `rgba(56,189,248,.16)` | `#e3f4ff` (opaque) |
| Wash edge | — | `rgba(37,99,235,.15)` | — | — | `#c4daf2` |
| Tint (hover) | — | — | — | `rgba(56,189,248,.07)` | — |

owl's blue is deliberately soft and low-contrast (an editorial choice, though it
costs link legibility, see §10). retina and dash share the saturated blue, with
dash resting one step lighter and hovering to retina's resting value. The map
pushes to a brighter sky-blue so the accent reads on navy, and takes dash's
value when themed light rather than adding another. owl-os sits between dash and
the map, a shade cyan-ward of both. Still five distinct blues across six
surfaces: dash and data are one value, and the themed surfaces swap between two
that already exist rather than introducing a third.

The map is the only surface with **two** accent washes. The tint is the wash at
hover strength and sits deliberately below the wash proper, so a hovered row and
a selected one stay apart instead of collapsing into the same fill (light:
`rgba(59,130,246,.05)` under `rgba(59,130,246,.10)`).

Two things owl-os does differently with it. Its washes are **opaque tints**, not
alpha overlays, so a wash keeps its colour over any ground it lands on rather
than picking up whatever is behind it. And every wash carries a matching **edge**
one step darker (`#c4daf2` for the accent, `#bee2c9` for success), so a tinted
region is bounded rather than bleeding into the page. The map adds an amber
`#fbbf24` for a selection/focus highlight; owl-os uses the accent wash plus a
3px inset rail for the same job.

### Semantics

| Role | Marketing (owl, retina) | Consoles (dash, data) | Map (map) | Node (owl-os) |
|---|---|---|---|---|
| Success / good | `#16a34a` | `#10b981` (emerald) | `#4ade80` | `#33a868` |
| Warning / attention | `#d97706` | `#f59e0b` (amber-500) | `#fbbf24` | `#e1a035` |
| Error | (unused) | `#ef4444` (red-500) | `#f43f5e` | `#e64343` |

Same three roles, brightened a step on the dark map so they carry on navy, and
landing between the marketing and console sets on owl-os. The two sets travel
with the theme rather than with the surface: the map's light theme takes the
console set unchanged, and dash's and data's dark takes the map's. Each pairs
with a wash (~10% on light, ~15% on dark; opaque on owl-os) for tinted pill
backgrounds. The console's charts
extend the accent into a categorical palette (`#3b82f6,
#10b981, #f59e0b, #ef4444, #8b5cf6, #ec4899, #06b6d4, #84cc16, #f97316,
#14b8a6`, with `#94a3b8` for an "others" slice); reuse that ordering for any new
dashboard chart.

The map's live data colours are a separate, radar-specific scheme, not these
status roles, and the one part of the estate chosen by measurement rather than by
eye: each value is held to a contrast floor against its own basemap, and each
pair of marks to a CIEDE2000 distance from the others. The second is the
constraint that gets forgotten, and the one that binds here, because the four
track lanes all draw the same aircraft glyph and colour is the only thing telling
them apart. **Truth** (the ADS-B fix the solves are measured against) wears no
hue at all: it sits at the far end of the neutral ramp from the canvas, near-white
`#f8fafc` on dark and slate `#1e293b` on light, since it is the reference rather
than a fifth lane. A simulated target flying without a transponder is grey beside
it. Radar detections run a **Doppler gradient** from dark-blue approaching
(`#1e3a8a`) through a neutral slate at zero to dark-red receding (`#991b1b`), so
no radial motion reads as the absence of a direction rather than as a third
colour. Green there means coverage polygons, never truth. See §8.

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
console collapses everything into the system stack; the map collapses everything
into Inter.

| Register | owl | retina | dash / data | map | owl-os |
|---|---|---|---|---|---|
| Display | Source Serif 4 | Fraunces | system sans | Inter | Inter |
| Body | Inter | DM Sans | system sans | Inter | Inter |
| Mono | IBM Plex Mono | JetBrains Mono | SF Mono | generic `monospace` | JetBrains Mono |

Loaded from Google Fonts on the marketing sites, the map (Inter) and owl-os; the
two consoles load no web fonts at all (their CSP restricts `font-src`). Only the
two marketing sites use a serif; the four operational surfaces (dash, data, map,
owl-os) are sans-only.

owl-os is the only surface that borrows both its faces from siblings rather than
choosing new ones (Inter from owl and the map, JetBrains Mono from retina), and
so is the least type-divergent of the six. It also asks Inter for
`font-feature-settings: 'ss01', 'cv11'` (the single-storey `g` and the
straight-tailed `l`), which is what stops a screen full of node IDs and
frequencies from reading as body copy.

**Heading weight is the other big tell.** owl sets headings at 400 (light,
serious, editorial); retina and owl-os at 600 (present, product-confident); dash,
data and map at 700 (compact, functional). Marketing headings carry a tight
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

| | owl | retina | dash / data | map | owl-os |
|---|---|---|---|---|---|
| Radius (default) | 4px | 12px | 8px | 8px | 10px |
| Radius (small) | 3px | 8px | 4px | 4px | 6px |
| Radius (large) | 6px | 20px | 12px | 12px | 14px |

Crisp on owl, soft on retina, moderate on dash, data and the map, which take the
same scale, second-softest on owl-os. data defines only the first two steps,
having nothing large enough to need the third. Borders are always 1px
hairlines; nothing uses a heavy stroke. The map's panels float over a moving
basemap rather than sitting on a page, so it is the one surface where a card
carries a shadow as
standard (`--panel-shadow`), heavier on dark than on light because a soft shadow
does almost nothing there and the elevation has to come from the panel being
lighter than the canvas.

The three-step scale is a fair summary for five of the surfaces and a
simplification for one. The map is now the closest to keeping to it: most of its
radius rules read `--radius` or `--radius-sm`, with 12px reserved for pills and a
scatter of 2–6px literals left over. retina is the outlier, spending 5, 6, 8, 10,
12 and 20px, with neither of its two button radii matching the 12px recorded as
its default.

owl-os is the only surface with a real elevation scale: a hairline `shadow-sm` at
rest, a 24px-blur `shadow-md` on hover and for the sticky save bar, and a
`shadow-pop` for modals. All three are tinted with the ink colour rather than
black, so a raised card warms rather than greys.

### Space

- Marketing content sits in a centred column: `max-width` 860px for prose,
  1120–1200px for wide/hero rows. dash is full-width and fluid with a 250px
  sidebar; data has no sidebar to hold (one page, no nav tree, no login) and
  runs a 1400px centred column under a top bar instead. The map is full-bleed:
  a 280px left aircraft list (collapsing to 36px), a 280px right detail panel,
  and a full-width bottom playback bar.
- owl-os runs a 720px column on Home, a 200px + fluid two-column shell on Config
  (max 1100px), and a fixed 560px column for every wizard step. One decision per
  row, with its explanation directly underneath.
- Nav / header height: 56px (owl), 64px (retina), 56px (dash and data). owl-os
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

owl and dash animate in CSS; retina's hero mixes in inline SVG SMIL (`<animate>`).

owl-os runs none of the three. It defines no `@keyframes` at all: motion is
limited to 120ms colour, border and shadow transitions on hover, a 150ms switch
throw, and a 2px nudge on a card's arrow. Nothing on the page moves unless it was
touched, which is reasonable for a settings surface someone reaches when
something needs fixing, and the reason its one animated component, the simulator,
checks `prefers-reduced-motion` before starting. The map guards its whole
surface with a single reduced-motion block, and owl's `/learn` page carries its
own; the two marketing home pages still run their loops unguarded. The
`tokens.css` `.reveal` helper adds the guard, and new work should keep it.

---

## 6. Components

The six surfaces do not have the same component set, and the differences are
larger than the colour and type differences in §3 and §4. Before reaching for a
pattern, check it exists on the surface you are building for.

| | owl | retina | dash | data | map | owl-os |
|---|---|---|---|---|---|---|
| Form controls | **none** | **none** | inline, ad hoc | one shared rule | one shared rule | a real set |
| Tables | none | none | yes | a grid listing, one table | none | one |
| Modal / dialog | none | none | **native `confirm()`** | one drawer | one | three |
| Toasts | none | none | none | none | yes | none |
| Tabs | none | none | one page | none | app shell only | yes |
| Icons | 36px, part-filled | Unicode glyphs | 24px, stroke 2 | 15px inline SVG | inline SVG | 24px, stroke 1.6 |
| Framework | none | none | none | none | none | Bootstrap 5.3 |
| Custom properties | yes | yes | yes, themed | yes, themed | yes, themed | yes |
| `:focus` styling | none | none | **none** | inputs | whole surface | inputs only |

The two marketing sites have no `<form>`, `<input>`, `<select>`, `<textarea>` or
`<table>` between them, and no `:focus` or `:active` rule in either file. Their
only stateful control is the mobile nav toggle, and retina's one transaction
leaves for Stripe. So everything below about controls concerns dash, data, the
map and owl-os alone.

### Chrome: nav and footer

- **Marketing nav.** Fixed top bar, `backdrop-filter: blur(16–20px)` over a
  translucent canvas, a hairline bottom border. Logo left (mono wordmark, or logo
  plus mono text on owl), links centre, a primary CTA right. 56px on owl, 64px on
  retina. Under 860px (owl) or 960px (retina) it collapses to a hamburger that is
  a literal `☰` text character, not an icon, opening an absolutely positioned
  blurred panel. Neither sets `aria-expanded`, traps focus, or changes the glyph
  when open.
- **dash is not a top bar.** It runs a 250px left sidebar plus a 56px header. The
  sidebar carries a brand block (32px accent square, 15px name, an 11px muted
  sub-label naming the console), then sections titled in the micro-label, then
  `.nav-item` rows at 8px 12px with 18px icons: hover tints the row, active takes
  `--accent-light` with `--accent` text. Two navigation trees exist, chosen by
  whether the viewer is an admin. Under 768px the sidebar is `display: none` with
  nothing in its place, so navigation is simply unreachable on a phone.
- **data is a top bar**, the one console-family surface that is not a sidebar.
  It has one page, no nav tree and no login, so a 250px rail would carry
  nothing: a 56px bar holds a 28px accent-square mark, sibling-host links out to
  dash and the map, and the three-state appearance switch. It is not a model for
  dash, which has two navigation trees to hold and cannot fit them here. What is
  worth taking from it is narrower: because the bar wraps rather than
  disappearing, data stays navigable at phone width, where dash does not (§10).
- **map** has an app-shell header: one slim identity bar on the panel colour,
  carrying a 24px rounded accent square with a ⌁ glyph as the mark, and dash's
  underline tabs sat on the bar's own bottom rule. Its full-width toolbar strip
  sits directly below, in normal flow rather than floating over the map, and the
  two read as a single header block.
- **owl-os** stacks a fleet bar over page tabs; see the node section below.
- **Footer.** Hairline top border, mono wordmark left, muted links, a `© 2026`
  line. Understated. dash and map have none. owl-os fills its footer with
  versions instead (node ID, owl-os version, retina-node version, each value in
  mono), so the first thing anyone is asked for in a support conversation is
  already on screen.

### Buttons

Primary is solid ink on the marketing sites and owl-os, solid accent on dash and
map. owl, dash and owl-os keep buttons flat; retina lifts them
(`translateY(-1px)` plus a soft shadow) on hover. Secondary is a text link with a
hairline underline (owl), or an outline button (retina, dash, owl-os).

| | owl | retina | dash / data | map (`.toggle-btn`) | owl-os |
|---|---|---|---|---|---|
| Padding | 0.7rem 1.4rem | 0.55rem 1.25rem | 8px 16px | 3px 9px | 8px 14px |
| Radius | 4px | 8px (10px large) | 4px | `--radius-sm` | 8px |
| Size / weight | 0.875rem 500 | 0.875rem 500 | 13px 500 | 12px 500 | 13.5px 500 |
| Disabled | n/a | n/a | dash: secondary only; data: all | one `<option>` | 0.55 opacity |
| Busy | n/a | n/a | label text only | n/a | spinner in label |

Three things worth knowing. On the marketing sites every button is an `<a>`, so
no disabled, active or busy state is expressible at all. On dash the disabled
rule is attached only to `.btn-secondary`, so a disabled primary or outline
button looks enabled; data attaches it to `.btn` itself and matches
`[aria-disabled="true"]` alongside `:disabled`, so its link-buttons disable too,
which is the version to copy. And the map's column above describes
`.toggle-btn`, a small bordered chip used about twenty times in the toolbar and
the console's dominant control. Its `.active` state (the accent wash, an accent
border and accent-strong text) carries almost all of the surface's on/off state,
standing in for the switches it does not have. The one exception is the
anomalies toggle, which reports a condition as well as a state and so takes the
error colour while it is filtering.

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
  `--canvas-sunk`, and those two sit within 1.2:1 on owl, retina, dash and map.
  owl-os gets away with it by pairing the fill with `shadow-md`, which is the one
  surface with a shadow scale to spend. Anywhere else the active segment needs a
  hairline or a text-colour shift to be visible at all.
- Checkboxes are native at `accent-color: var(--ink)`, wrapped in a row with a
  12.5px help line beneath. **Radios are native and entirely unstyled**: no class
  exists for them, they are positioned with an inline `margin-top`, and only one
  of them sets `accent-color`, so the rest render in the browser's blue.
- Field furniture is a label at 13px/500 with the explanation directly under it at
  12px `--ink-3`, in a two-column row that puts the control on the right.
- `.ds-textarea` is defined and never used; there is no textarea on the surface.

**dash has no shared control styling at all.** Its stylesheet contains no
`input`, `select` or `textarea` selector, so every control is styled inline at
the call site and they have diverged into three incompatible text-input variants
(260px at 13px with no background, 180px at 12px on `--bg-input`, and one wholly
unstyled), three select variants, and one textarea (the JSON config editor, 400px
tall in monospace). There is no focus, hover, disabled or error treatment on any
of them, no help text, and no inline validation message. The only labelled form
on the surface is the invite form, whose label is a 12px muted block.

**data has the rule dash lacks.** One declaration covers `input`, `select` and
`textarea` — the `--bg-input` ground, a hairline `--border-light`,
`--radius-sm`, 6px 9px padding, 13px — with a checkbox rule beside it setting
`accent-color`, and a `:focus` that clears the outline and takes an accent
border. Two reasons it is worth having rather than styling each control where it
is used. The filter bar alone carries date, time, number and search inputs and a
select, which is exactly the spread that left dash with three incompatible
text-input variants and three select variants. And it is what makes a surface
themeable cheaply: a control styled inline only inverts if someone remembers it,
where one rule written against the tokens cannot be forgotten — dash's dark
theme had to visit every inline call site instead. Its focus treatment is thin,
though: a 1px border-colour change is the whole cue, which owl-os's accent
border plus a 3px ring at 12% would improve on (§10).

**map has one shared rule, borrowed from dash.** Text, number and search inputs
and selects are styled together on the surface: the `--bg-input` ground, a
hairline border, `--radius-sm`, and an accent border on focus. The aircraft list
overrides the ground to the card colour, because `--bg-input` and `--bg-sunk`
are the same value on light and a field on that pane would otherwise be left
with only its border. What is still ad hoc is the playback scrubber, a native
`input[type=range]` tinted with `accent-color` and otherwise left as the browser
drew it, and one native checkbox in the owner popover.

Neither dash nor map has a toggle switch, a radio, a date picker or a file input
anywhere.

### Feedback: loading, empty, validation, errors

- **Loading.** owl-os shows Bootstrap's spinner, always shrunk by the same
  copy-pasted inline style rather than a class, and swaps a button's label for
  spinner plus text while it works. dash has no spinner and no skeleton at all:
  every page returns the text "Loading…" in its empty-state box, and in-table
  loading is an ad hoc centred cell. map has one Suspense fallback reading
  "Loading map…". Nothing anywhere uses a skeleton. data is the one that does
  not load as a page: it fetches a day at a time and gives each day its own
  state and its own Retry, so one slow or failed day does not blank the rest.
  On any surface that fetches several independent things, that is the shape to
  copy.
- **Empty states.** dash centres muted text at 48px 20px, with an icon slot that
  is defined and never used, and copy that drifts from neutral ("No invites yet.")
  to exclamatory. data's is dash's box with copy that names the next action
  ("Pick a date range."). map's "No aircraft" is the same shape at the same size,
  in the muted ink. owl-os's is a help line that names the next action ("No cached
  tower search results yet. Run the Location step..."), which is the one worth
  copying.
- **Validation.** Only owl-os has any. A form-level banner above the form carries
  the specific refusal, falling back to "Please fix the highlighted fields below",
  and each offending field takes `.is-invalid`.
- **Error banners.** owl-os uses a danger-tinted banner at the top of the form and
  an info-tinted one in the same shape for neutral notices. dash has a warning
  banner on one page and a card-shaped error banner on two others. map has an
  emergency-squawk alert inside the detail panel.
- **Error boundaries.** Both dash and map fall back to an unstyled `<h2>`, a
  sentence and a default browser button. On the dark map that is black-on-white
  in the middle of the console.

### Overlays: modals, popovers, toasts

- **owl-os** has three Bootstrap modals doing three different jobs, and the split
  is worth copying: a form modal, a destructive confirmation that lists the
  consequences in prose, and a blocking progress modal set
  `data-bs-backdrop="static" data-bs-keyboard="false"` so it cannot be dismissed
  while the run holds the SDR. It also puts a fixed scrim over the whole wizard
  when the session expires, rather than leaving live-looking controls behind.
- **dash has no modal component.** Confirmations are native `window.confirm()`
  and save errors are native `alert()`. Its only popover is the user dropdown in
  the header, which is also the only shadow on the surface.
- **data has a drawer**, which is the shape to reach for when the content is
  something to read beside the list rather than a decision to make. 560px on the
  right, a scrim over the page, a 0.18s transform, split head / body / foot. It
  carries a key-value block, a preview table and a curl line, none of which fits
  a native dialog, and it leaves the list in place so the next file is one click
  away rather than a re-open. It is the only drawer in the estate, so treat it
  as a pattern with one instance rather than a settled one.
- **map** has one modal, the keyboard-shortcut help, plus three inline popovers
  (filters, stats, node owner) that share a top-right stack so they cannot
  overlap. It is the only surface with **toasts**: a bottom-right stack of chips
  with four tones, a 2.5s life, no dismiss control and no animation.
- **Tooltips.** No surface has a styled tooltip component. dash and map both rely
  on the native `title` attribute, used around twenty times on map alone. The one
  exception is map's `.radar3-error-label`, a Leaflet tooltip restyled in place.

### Data display

- **Section eyebrow.** A micro-label above each H2 naming the section. The
  consistent opener for a marketing section, and the strongest shared idiom.
- **Fact rows and metrics.** Label-value pairs on hairline-divided rows (owl's
  RETINA facts), a bordered 4-up metrics bar (retina), stat cards with a 28px/700
  value and four tint modifiers (dash), or label-value rows on hairlines with
  tabular-numeric values (map's detail panel, owl-os's node cards).
- **Cards.** White, 1px border, surface radius. Flat on the marketing sites and
  dash; owl-os gives them a resting hairline shadow and lifts them on hover.
  retina's grids use a 1px gap over a border-coloured ground so dividers read as
  shared lines; **dash's do not**, using a real 16px gap with per-card borders.
- **Tables.** Only dash, data and owl-os have one. dash's is 11px uppercase muted
  headers over 13px rows with a hairline under each and a 2% row hover, wrapped
  in a horizontal scroller: no sticky header, no zebra, no sortable headers, no
  row selection. Sorting, where it exists, is a `<select>` or a row of buttons.
  owl-os's tower table adds what dash lacks: a selected row marked by a wash plus
  a 3px inset rail. data's file listing is dash's type scale over a CSS grid
  rather than a `<table>`, since its rows nest three levels (day → node → file)
  and collapse; it does put the sort on the column header, which is the one thing
  dash's tables are missing and the easiest to port back. The one real `<table>`
  on the surface is the frame preview inside the drawer.
- **Badges are not one component.** §3's status colours are consistent; the
  shapes they are poured into are not. Across the six surfaces there are at
  least seven: a 12px tinted-wash pill with a leading dot (dash, three variants
  only, so an unmatched state renders as an undecorated pill with a bare black
  dot, and now the map, which took the same shape for its source and connection
  badges); an outline pill with a dot (owl-os `.ds-pill`); a tinted 999px chip
  (owl-os `.node-chip`); a 6px tinted rectangle (owl-os `.tower-badge`); a 6px
  solid-ink corner badge (retina's kit); a 5px green wash (retina's savings tag);
  an 8px outline chip (retina's OSS row); and owl's live label, which is white on
  a black scrim over the iframe. Pick the surface's own shape rather than
  assuming the pill. data has no badge at all: its 999px `.chip` is an
  interactive filter toggle rather than a status readout, and reusing the status
  badge for it would have been the wrong call.

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

**map (the live console).**

- **Virtualised aircraft list.** Fixed 40px rows with five rows of overscan inside
  a spacer sized to the full count. The row height is a constant shared between
  the TSX and the CSS, so changing one alone breaks the scroll maths. Rows carry a
  colour indicator, a rotating aircraft glyph, callsign, and right-aligned
  altitude and speed in tabular numerals; selection is an accent left rail over
  the wash, matching dash's active nav row, and truth-only rows drop to 0.7
  opacity. Note that the list and the map mark selection in different languages
  on purpose: the list is chrome and takes the accent, the map is data and keeps
  amber for the selected track.
- **One panel treatment.** The detail panel, the playback bar and the inline
  overlay cards are all the same object: an opaque `--bg-card` fill, a hairline,
  and `--panel-shadow`. No panel blurs what is behind it, so a card over the map
  and a card over the sidebar read alike.
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

**dash (the console).** Pagination is the one component repeated verbatim across
six pages: a centred Prev / Next pair with "Page N of M" between them, at a page
size of 25. Tabs exist in the stylesheet (a 2px accent underline on the active
tab) but are used on exactly one page. Charts are Recharts with their chrome set
inline and identically on seven pages, in hard-coded hex rather than the tokens.

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
device and does _not_ match how the live map (map.retina.fm) actually colours
radar data. On the real map, truth is a neutral rather than any hue, radar
detections run a blue↔red Doppler gradient, and green is used for coverage
polygons (see §3). So a diagram and the live map deliberately tell the same story
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
The token names are unified across the six surfaces (the live sites each use
their own naming), so a page gets one vocabulary.

```html
<link rel="stylesheet" href="tokens.css">
<body class="retina">   <!-- owl | retina | dash | data | map | owl-os -->
  <h1 style="font-family: var(--font-display); font-weight: var(--heading-weight)">…</h1>
</body>
```

Add exactly one surface class (`owl`, `retina`, `dash`, `data`, `map` or
`owl-os`) to `<body>`; it sets that surface's fonts, canvas, ink, accent, and
radii. `dash` and `data` are one declaration, since they hold the same values.
The `map` class is dark, so `var(--ink)` is light and `var(--canvas)` is navy:
components written against the tokens invert automatically. The shared `:root`
layer provides the semantic colours, base rhythm, and the `.label` / `.reveal`
helpers.

The two halves are reached with `data-theme`, as on the live surfaces:
`data-theme="light"` beside `map`, `data-theme="dark"` beside `dash` or `data`.
Both directions resolve to the same pair, so a component written against the
tokens is theme-agnostic without being told which surface it is on.

What this file cannot reproduce is the `system` state dash and data actually
default to, since a stylesheet of classes has no way to be handed an OS
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

Observations from reading the six surfaces side by side. Recorded here, not
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
  `--bg`, dash and the map use `--bg-primary` / `--text-primary`, and owl-os uses
  `--ink` / `--bg` / `--line`. Nothing is portable between them. `tokens.css`
  proposes one naming; adopting it in the live sites would remove the drift. The
  map is the one place two surfaces already agree, having taken dash's names
  along with its values, though the two are duplicated rather than shared because
  the apps build separately. owl-os is the closest to a system already, with a
  deliberate three-step ink ramp, a colour/wash/edge triple per semantic role,
  and its own Bootstrap compatibility aliases mapping the old names onto the new
  ones.
- **The two light themes disagree on the sunk tier.** dash and data set
  `--bg-sunk` to the canvas value `#f1f5f9`, so a recessed region is made by
  letting the canvas show through; the map's light theme sets it to `#f8fafc`,
  which is *lighter* than its canvas and identical to its card-hover and input
  grounds, so a "sunk" pane there is not recessed at all. Everything else in the
  pair matches token for token, which is what makes this one look like a
  carry-over rather than a decision. One of the two is wrong; worth settling
  before a component that uses the tier moves between them.
- **The three themed surfaces do not agree on what picks the theme.** dash and
  data have three states and default to `system`; the map has two and defaults
  to dark, never consulting the OS (§3). Defensible on a live operational view
  that people keep open, and the map is also the only one of the three whose
  data colours are held to a contrast floor per theme, so flipping it is not
  free. But it means one estate answers the same question two ways, and a
  viewer on a dark OS meets a light console and a dark map.
- **Semantic colours drift by a shade.** Green is `#16a34a` (marketing),
  `#10b981` (console), `#4ade80` (map), `#33a868` (owl-os); amber and red shift
  similarly. Close enough to look like one intent, far enough to not match.
- **One surface is in OKLCH and four are in hex.** owl-os's ramps are perceptual
  and its neighbours' are not, so "one step lighter" means something different
  depending on which stylesheet you are in. Not a problem while nothing is
  shared; it becomes one the moment a value is moved between surfaces.
- **Washes are alpha on five surfaces and opaque on owl-os.** An alpha wash picks
  up whatever is behind it, an opaque one does not. Both are defensible, but a
  component copied between surfaces changes behaviour silently. Only owl-os gives
  its washes a matching edge colour, which is the part most worth spreading.
- **The "truth" colour story is inconsistent.** The marketing diagrams say green
  = ADS-B truth; the live map gives truth no hue at all and reserves green for
  coverage. Defensible (illustration vs data viz), but a viewer moving from the
  homepage to the map meets two different colour languages for the same idea.
- **No shared stylesheet.** Every value is inlined per surface, so drift is the
  default. `tokens.css` is the first step toward a single source.
- **dash has no shared control styling.** Its stylesheet contains no `input`,
  `select` or `textarea` selector at all, so its controls are styled inline per
  call site and have already split into three incompatible text-input variants
  and three select variants, with no focus, hover, disabled or error treatment on
  any of them. It is the more striking gap for being the surface the other two
  consoles borrowed their whole vocabulary from: the same token names now carry
  a shared control rule on both the map and data, and nothing on dash. data's
  rule is the closest port, having been written against dash's own names.
- **Dead CSS on three surfaces.** owl's three-up pillars block, retina's kit
  placeholder, and owl-os's `.ds-textarea` / `.ds-steps` / `.ds-step` are all
  fully styled with no markup using them. Harmless, but each one reads as an
  available component to the next person building a page.
- **Only one surface can express elevation.** owl-os is alone in having a shadow
  scale; the other four have at most a single hardcoded shadow (retina's button
  lift, dash's dropdown, map's overlay cards). Any component that separates two
  layers by raising one, the segmented control being the clearest case, works on
  owl-os and flattens everywhere else, because `--surface` and `--canvas-sunk`
  are within 1.2:1 on all four. A shared shadow token would unblock a class of
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
  does. The map guards its whole surface with a single block, owl-os's
  flight-path simulator checks before it starts, and owl's `/learn` page carries
  its own; between them they show the pattern is cheap. The `tokens.css`
  `.reveal` helper adds the guard for new work.
- **Focus styles.** Only the map defines a visible `:focus-visible` treatment,
  an accent outline over the whole surface; everywhere else keyboard focus rides
  on the browser default. owl-os is halfway there: its inputs take an accent
  border plus a 3px accent ring on `:focus`, but as `:focus` rather than
  `:focus-visible`, so the ring also fires on mouse click, and its buttons and
  links get nothing at all. data is a third of the way: its inputs clear the
  outline and take an accent border, which is a 1px hue change carrying the
  whole cue, and its buttons and links get nothing. owl, retina and dash contain
  no `:focus` rule whatsoever, which on a page of filters is the worst case of
  the three. The map's one-line rule is the model to copy.

**Polish**

- **Missing social metadata.** None of them set `og:image` / `twitter:card` /
  canonical, so link previews are bare. A single shared OG image per surface would
  help. owl-os is the one case where this genuinely does not matter: it is served
  off a box on a home network and cannot be linked to from anywhere.
- **The operational surfaces carry little brand.** dash dropped the type system
  for system fonts and cool slate; the map runs Inter-only and now takes dash's
  vocabulary as well, so the two consoles agree with each other and with almost
  nothing on the marketing sites beyond a blue accent and the uppercase
  micro-label. Standardising the micro-label and reusing one blue would connect
  all six without slowing the tools down. owl-os is the counter-example
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
- **The map is the only surface measured rather than eyeballed.** Its data
  palette is held to a contrast floor against its own basemap and a CIEDE2000
  distance between marks, in both themes (§3). Its chrome ramp is not covered by
  that, and neither is any other surface: the accessibility notes above were
  checked against the light surfaces by inspection.
- **Inconsistent animation approach.** retina's hero uses inline SVG SMIL
  (`<animate>`) while owl uses CSS keyframes. dash has no `@keyframes` at all, so
  none of §5's three motion patterns appear on it. Standardising on CSS would
  make the shared radar motif portable.
- **Three colour references that resolve to nothing.** dash's error banners are
  coloured `var(--accent-warning, #c0392b)`, and `--accent-warning` is not
  defined anywhere, so both banners always render the fallback, a red that
  appears nowhere else in the palette. owl-os's calibration spinner carries
  Bootstrap's `.text-primary`, which its override block does not redefine, so
  that one spinner is Bootstrap blue `#0d6efd` rather than the surface accent.
  dash's `.badge` has three variants, so a state with no matching modifier
  renders as an undecorated pill with a bare black dot.
- **dash is unreachable on a phone.** Its 250px sidebar is `display: none` under
  768px with no hamburger and no replacement, so there is no way to navigate
  between pages at that width. Worth confirming against real usage before
  treating it as intentional — though data, the console-family surface most
  likely to be opened from a shared link on a phone, does not have the problem,
  because its chrome is a bar that wraps rather than a rail that vanishes.
- **Native dialogs on a designed surface.** dash confirms destructive actions with
  `window.confirm()` and reports save errors with `alert()`. Both are unstyled OS
  chrome in the middle of a console that otherwise controls every pixel, and the
  estate now has two styled alternatives written against the same tokens: the
  map's modal for a decision, data's drawer for something to read.
