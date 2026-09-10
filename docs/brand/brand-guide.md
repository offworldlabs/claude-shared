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
builds elevation from backdrop-blur (20px on the detail panel, 14px on the
playback bar) and subtle shadow rather than cards, since its panels float over
the map.

The three-step scale is a fair summary for four of the surfaces and a
simplification for two. The map actually spends 2, 3, 4, 5, 6 and 10px in its
stylesheet plus 8 and 12px inline, and retina spends 5, 6, 8, 10, 12 and 20px,
with neither of its two button radii matching the 12px recorded as its default.

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

The five surfaces do not have the same component set, and the differences are
larger than the colour and type differences in §3 and §4. Before reaching for a
pattern, check it exists on the surface you are building for.

| | owl | retina | dash | map | owl-os |
|---|---|---|---|---|---|
| Form controls | **none** | **none** | inline, ad hoc | a few, ad hoc | a real set |
| Tables | none | none | yes | none | one |
| Modal / dialog | none | none | **native `confirm()`** | one | three |
| Toasts | none | none | none | yes | none |
| Tabs | none | none | one page | app shell only | yes |
| Icons | 36px, part-filled | Unicode glyphs | 24px, stroke 2 | inline SVG | 24px, stroke 1.6 |
| Framework | none | none | none | none | Bootstrap 5.3 |
| Custom properties | yes | yes | yes | **none** | yes |
| `:focus` styling | none | none | **none** | one rule | inputs only |

The two marketing sites have no `<form>`, `<input>`, `<select>`, `<textarea>` or
`<table>` between them, and no `:focus` or `:active` rule in either file. Their
only stateful control is the mobile nav toggle, and retina's one transaction
leaves for Stripe. So everything below about controls concerns dash, map and
owl-os alone.

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
- **map** has an app-shell header (gradient `#0d1b2a → #132240 → #0f2035`, 18px
  32px, a ⌁ glyph as the mark) plus its own full-width toolbar strip below, which
  is in normal flow rather than floating over the map.
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

| | owl | retina | dash | map (`.toggle-btn`) | owl-os |
|---|---|---|---|---|---|
| Padding | 0.7rem 1.4rem | 0.55rem 1.25rem | 8px 16px | 3px 8px | 8px 14px |
| Radius | 4px | 8px (10px large) | 4px | 5px | 8px |
| Size / weight | 0.875rem 500 | 0.875rem 500 | 13px 500 | 0.7rem | 13.5px 500 |
| Disabled | n/a | n/a | secondary only | one `<option>` | 0.55 opacity |
| Busy | n/a | n/a | label text only | n/a | spinner in label |

Three things worth knowing. On the marketing sites every button is an `<a>`, so
no disabled, active or busy state is expressible at all. On dash the disabled
rule is attached only to `.btn-secondary`, so a disabled primary or outline
button looks enabled. And the map's column above describes `.toggle-btn`, a small
bordered chip used about twenty times in the toolbar and the console's dominant
control. Its `.active` state (a `rgba(56,189,248,0.18)` fill with a
`rgba(56,189,248,0.5)` border and `#7dd3fc` text) carries almost all of the
surface's on/off state, standing in for the switches it does not have.

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

**map has a handful, also inline.** Two different search boxes for the same job
(the sidebar's is borderless and transparent with a placeholder at `#1e293b`,
close to invisible; the toolbar's is a bordered pill), a native sort `<select>`
carrying the surface's only `:focus` rule, three unstyled number inputs in the
filter popover, one native checkbox in the owner popover, and the playback
scrubber, which is a native `input[type=range]` tinted with
`accent-color: #38bdf8` and otherwise left as the browser drew it.

Neither dash nor map has a toggle switch, a radio, a date picker or a file input
anywhere.

### Feedback: loading, empty, validation, errors

- **Loading.** owl-os shows Bootstrap's spinner, always shrunk by the same
  copy-pasted inline style rather than a class, and swaps a button's label for
  spinner plus text while it works. dash has no spinner and no skeleton at all:
  every page returns the text "Loading…" in its empty-state box, and in-table
  loading is an ad hoc centred cell. map has one Suspense fallback reading
  "Loading map…". Nothing anywhere uses a skeleton.
- **Empty states.** dash centres muted text at 48px 20px, with an icon slot that
  is defined and never used, and copy that drifts from neutral ("No invites yet.")
  to exclamatory. map's is "No aircraft" in `#1e293b` on `#0f2035`, which is very
  nearly invisible. owl-os's is a help line that names the next action ("No cached
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
- **Tables.** Only dash and owl-os have one. dash's is 11px uppercase muted
  headers over 13px rows with a hairline under each and a 2% row hover, wrapped
  in a horizontal scroller: no sticky header, no zebra, no sortable headers, no
  row selection. Sorting, where it exists, is a `<select>` or a row of buttons.
  owl-os's tower table adds what dash lacks: a selected row marked by a wash plus
  a 3px inset rail.
- **Badges are not one component.** §3's status colours are consistent; the
  shapes they are poured into are not. Across the five surfaces there are at
  least seven: a 12px tinted-wash pill with a leading dot (dash, three variants
  only, so an unmatched state renders as an undecorated pill with a bare black
  dot); an outline pill with a dot (owl-os `.ds-pill`); a tinted 999px chip
  (owl-os `.node-chip`); a 6px tinted rectangle (owl-os `.tower-badge`); a 6px
  solid-ink corner badge (retina's kit); a 5px green wash (retina's savings tag);
  an 8px outline chip (retina's OSS row); a 3px translucent source badge and a
  4px gradient connection badge (map); and owl's live label, which is white on a
  black scrim over the iframe. Pick the surface's own shape rather than assuming
  the pill.

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
  altitude and speed in tabular numerals; selection is an amber left rail over a
  wash, and truth-only rows drop to 0.65 opacity.
- **Two panel treatments, not one.** The detail and playback panels use
  backdrop-blur (20px and 14px); the four inline overlay cards use no blur at all,
  only an opaque near-black fill and a soft shadow.
- **Blur as meaning.** A blurred edge means measured but approximate (node
  uncertainty discs at 5px, fuzzy coverage at 3.5px); a sharp dashed edge means a
  declared model, which is why the theoretical Yagi cone stays crisp. Worth
  preserving as a rule rather than a style.
- **Leaflet supplies the rest.** Zoom control, attribution and popups are
  inherited unstyled, so the popups are Leaflet's default white bubbles sitting on
  a dark console. Tiles are filtered to `opacity 0.82` with
  `saturate(0.85) brightness(0.78)` to sit under the overlay.

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
- **Three of the five have no shared control styling.** owl-os is the only
  surface where a text input, a select and a switch are defined once and reused.
  dash's stylesheet contains no `input`, `select` or `textarea` selector at all,
  so its controls are styled inline per call site and have already split into
  three incompatible text-input variants and three select variants; map is the
  same story at smaller scale, with two different search boxes for one job. This
  is the largest single gap between the surfaces, and the cheapest to close.
- **Dead CSS on three surfaces.** owl's three-up pillars block, retina's kit
  placeholder, and owl-os's `.ds-textarea` / `.ds-steps` / `.ds-step` are all
  fully styled with no markup using them. Harmless, but each one reads as an
  available component to the next person building a page.

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
  click, and its buttons and links get nothing at all. The rest is worse than
  "undefined": owl, retina and dash contain no `:focus` rule whatsoever, map has
  exactly one (its sort select), and both map text inputs set `outline: none`,
  which removes the browser default without replacing it.

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
  treating it as intentional.
- **Native dialogs on a designed surface.** dash confirms destructive actions with
  `window.confirm()` and reports save errors with `alert()`. Both are unstyled OS
  chrome in the middle of a console that otherwise controls every pixel.
