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

- **offworldlabs.com** ([`landing-page-owl`](https://github.com/offworldlabs/landing-page-owl)) — the lab
- **retina.fm** ([`landing-page-retina`](https://github.com/offworldlabs/landing-page-retina)) — the product
- **dash.retina.fm** (`Tower-Finder/dashboard`) — the admin console
- **map.retina.fm** (`Tower-Finder/frontend`) — the live radar map

They read as one family, but each has its own voice. The map is the odd one out:
it is the only dark surface, a Flightradar24-style operational console.

---

## 1. Brand architecture: one family, four voices

The surfaces share a spine (a blue accent, green/amber status colours, a mono
micro-label, hairline rules) and then diverge in personality. The split maps
onto audience. Three are light; the map is dark.

| | **owl** — offworldlabs.com | **retina** — retina.fm | **dash** — dash.retina.fm | **map** — map.retina.fm |
|---|---|---|---|---|
| **Role** | The lab / parent org | The product you buy | The console you operate | The live picture |
| **Audience** | Researchers, funders, press | Prospective node owners | Logged-in operators | Anyone watching the map |
| **Feel** | Editorial, institutional | Commercial, confident | Utilitarian, dense | Dark ops console (FR24-style) |
| **Serif** | Source Serif 4, wt 400 | Fraunces, wt 600 | none | none |
| **Sans** | Inter | DM Sans | system stack | Inter (only font) |
| **Mono** | IBM Plex Mono | JetBrains Mono | SF Mono | none (generic) |
| **Canvas** | warm paper `#f7f6f2` | warm paper `#fafaf9` | cool slate `#f1f5f9` | **navy `#0d1b2a`** |
| **Blue** | muted `#5b8dd9` | punchy `#2563eb` | `#3b82f6` → `#2563eb` | sky `#38bdf8` |
| **Radius** | 4–6px | 8–20px | 4–8px | 3–10px |
| **Buttons** | flat | lift + shadow | flat | flat |
| **Dark UI** | none | one dark section | none | **fully dark** |

A rough rule of thumb for a new page: **who is it for?** Reaching outward to the
scientific or funding world reads as owl. Selling or explaining the kit reads as
retina. Anything behind a login reads as dash. Anything that _is_ the live radar
picture (a map, a track view, an operational overlay) reads as map.

---

## 2. Foundations

The parts that stay roughly constant across all four, and are the safest thing
to carry into new work.

- **A paper-like canvas.** The three outward surfaces use a near-white
  background (warm on the marketing sites, cool slate on the console) with
  near-black text. The **map is the exception**: it is fully dark navy with light
  slate text. So "light paper" is the norm for anything that explains or sells,
  and dark is reserved for the live operational view.
- **A blue accent.** owl sits soft and desaturated, retina and dash land on the
  brighter `#2563eb`/`#3b82f6`, and the map goes brighter still (sky `#38bdf8`)
  to carry on dark. Blue is the only chromatic accent in the UI chrome;
  everything else is ink on canvas. (The map adds an amber `#fbbf24` as a
  selection/focus highlight.)
- **Green and amber as status colours.** Green marks "live" / validated / ADS-B
  truth; amber marks the radar echo, anomalies, and attention. The console adds
  red for outright errors. (The exact shades drift between surfaces; see §10.)
- **A small uppercase micro-label.** Small, uppercase, letter-spaced, muted.
  Used for section eyebrows, stat labels, table headers, nav-section titles, and
  diagram annotations. This is the single most reused idiom and the quickest way
  to make a new page read as "ours". The marketing sites and console set it in
  their mono; the map keeps the uppercase-and-tracked treatment for panel and
  list headers even though it has no mono font.
- **Hairline rules and grid dividers.** 1px borders at low contrast separate
  sections, table rows, fact lists, and card grids. Structure comes from lines,
  not shadows or fills.
- **Flat and quiet.** Minimal ornamentation, few shadows (retina uses a subtle
  button lift; dash reserves shadow for one dropdown), small status dots for
  liveness.
- **The radar diagram.** owl and retina both open with a hand-built SVG of the
  passive-radar geometry (transmitter → target → node) with animated signal
  paths. It is the strongest single motif the two marketing sites share. See §8.

---

## 3. Colour

Values are grouped by role. Per-surface specifics sit in the columns; foundation
roles (semantics) are shared unless a surface overrides them.

### Canvas and ink

| Role | owl | retina | dash | map |
|---|---|---|---|---|
| Canvas | `#f7f6f2` | `#fafaf9` | `#f1f5f9` | `#0d1b2a` |
| Sunk surface | `#edecea` | `#f5f4f0` | `#f8fafc` | `#0f2035` |
| Card / panel | `#ffffff` | `#ffffff` | `#ffffff` | `#132240` |
| Dark section | — | `#090904` / `#242422` | — | (all dark) |
| Ink (primary) | `#0e0e0c` | `#1a1a18` | `#0f172a` | `#e2e8f0` |
| Ink (muted) | `#444440` | `#6b6b63` | `#475569` | `#94a3b8` |
| Ink (subtle) | `#888882` | `#9c9c93` | `#94a3b8` | `#64748b` |
| Border | `rgba(14,14,12,.1)` | `#e8e8e3` | `#e2e8f0` | `rgba(100,180,255,.12)` |

The marketing canvases are warm (a hint of yellow); the console is cool slate;
the map inverts to dark navy. The map's ink ramp is the dark mirror of the
console's slate ramp (`#94a3b8` / `#64748b` recur), and its hairlines are a
blue-tinted translucent white rather than a solid grey.

### Accent

| | owl | retina | dash | map |
|---|---|---|---|---|
| Accent | `#5b8dd9` | `#2563eb` | `#3b82f6` | `#38bdf8` |
| Hover / strong | `#4a7cc8` | `#3b82f6` | `#2563eb` | `#7dd3fc` |
| Wash | `rgba(91,141,217,.15)` | `rgba(37,99,235,.06)` | `rgba(59,130,246,.10)` | `rgba(56,189,248,.15)` |

owl's blue is deliberately soft and low-contrast (an editorial choice, though it
costs link legibility, see §10). retina and dash share the saturated blue, with
dash resting one step lighter and hovering to retina's resting value. The map
pushes to a brighter sky-blue so the accent reads on navy, and adds an amber
`#fbbf24` for the selection/focus highlight the others do not have. Four distinct
blues in all.

### Semantics

| Role | Marketing (owl, retina) | Console (dash) | Map (map) |
|---|---|---|---|
| Success / good | `#16a34a` | `#10b981` (emerald) | `#4ade80` |
| Warning / attention | `#d97706` | `#f59e0b` (amber-500) | `#fbbf24` |
| Error | (unused) | `#ef4444` (red-500) | `#f43f5e` |

Same three roles, brightened a step on the dark map so they carry on navy. Each
pairs with a wash (~10% on light, ~15% on dark) for tinted pill backgrounds. The
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

---

## 4. Typography

Up to three registers per surface: a **display** face for headings, a **body**
face for running text and UI, and a **mono** face for labels and data. The
console collapses everything into the system stack; the map collapses everything
into Inter.

| Register | owl | retina | dash | map |
|---|---|---|---|---|
| Display | Source Serif 4 | Fraunces | system sans | Inter |
| Body | Inter | DM Sans | system sans | Inter |
| Mono | IBM Plex Mono | JetBrains Mono | SF Mono | generic `monospace` |

Loaded from Google Fonts on the marketing sites and the map (Inter); the console
loads no web fonts at all (its CSP restricts `font-src`). Only the two marketing
sites use a serif; the two operational surfaces (dash, map) are sans-only.

**Heading weight is the other big tell.** owl sets headings at 400 (light,
serious, editorial); retina at 600 (present, product-confident); dash and map at
700 (compact, functional). Marketing headings carry a tight `letter-spacing`
around `-0.02em` and line-height near 1.1; the operational surfaces run text
small (down to ~0.62rem) and dense.

**Scale, as used:**

- Hero H1: `clamp(3rem, 6vw, 5rem)` on owl, `clamp(2.8rem, 5vw, 3.8rem)` on
  retina. Fluid, serif, tight leading.
- Section H2 / titles: `clamp(1.6rem, 3vw, 2.4rem)` (owl), `clamp(1.75rem, 3vw,
  2.25rem)` (retina). Console page titles are a flat 24px.
- Body: 16px base, line-height ~1.6–1.7, colour = ink-muted for prose.
- Micro-label: ~0.65–0.75rem, mono, uppercase, `letter-spacing` 0.04–0.14em,
  colour = ink-subtle. The `.label` class in `tokens.css` captures the common
  case.

---

## 5. Shape, space and motion

### Shape

| | owl | retina | dash | map |
|---|---|---|---|---|
| Radius (default) | 4px | 12px | 8px | 6px |
| Radius (small) | 3px | 8px | 4px | 3px |
| Radius (large) | 6px | 20px | 12px | 10px |

Crisp on owl, soft on retina, moderate on dash, tight on the map. Borders are
always 1px hairlines; nothing uses a heavy stroke. The map builds elevation from
backdrop-blur (14–20px) and subtle shadow rather than cards, since its panels
float over the map.

### Space

- Marketing content sits in a centred column: `max-width` 860px for prose,
  1120–1200px for wide/hero rows. The console is full-width and fluid with a
  250px sidebar. The map is full-bleed: a 280px left aircraft list (collapsing
  to 36px), a 280px right detail panel, and a full-width bottom playback bar.
- Nav / header height: 56px (owl), 64px (retina), 56px (dash).
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
None of the surfaces currently honour `prefers-reduced-motion`; the `tokens.css`
`.reveal` helper adds the guard, and new work should keep it.

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
  line. Understated.

---

## 7. Voice and copy

Plain, specific, quietly confident. The marketing copy leads with what the thing
does ("See the sky with radio echoes", "Building the instruments science is
missing"), states numbers without hype (35 mi range, VHF/UHF, open source), and
cites literature rather than asserting authority. Technical terms are used
directly, not dumbed down, but each is given a one-line plain-English gloss.

Note the public sites use **US spelling** ("color", "Atlanta", "meter"), which
differs from the British house style used for internal docs like this one. Keep a
page consistent with its surface: US spelling on the public sites.

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

---

## 9. Using the tokens

[`tokens.css`](tokens.css) carries every value above as CSS custom properties.
The token names are unified across the four surfaces (the live sites each use
their own naming), so a page gets one vocabulary.

```html
<link rel="stylesheet" href="tokens.css">
<body class="retina">        <!-- owl | retina | dash | map -->
  <h1 style="font-family: var(--font-display); font-weight: var(--heading-weight)">…</h1>
</body>
```

Add exactly one surface class (`owl`, `retina`, `dash`, or `map`) to `<body>`;
it sets that surface's fonts, canvas, ink, accent, and radii. The `map` class is
dark, so `var(--ink)` is light and `var(--canvas)` is navy: components written
against the tokens invert automatically. The shared `:root` layer provides the
semantic colours, base rhythm, and the `.label` / `.reveal` helpers.

---

## 10. Improvements, gaps and discrepancies

Observations from reading the four surfaces side by side. Recorded here, not
filed as work; a snapshot of loose ends rather than a plan.

**Divergence that looks accidental rather than intentional**

- **Four unrelated type systems.** owl, retina and dash use three different
  serifs, sans and monos between them; the map adds a fourth by going Inter-only.
  The tiered personality is deliberate; the choice of *different families* for
  each register reads more like independent authoring than a considered split. A
  shared mono (or reusing Inter, already on two surfaces), would cost little and
  tie things together.
- **Four distinct blues.** `#5b8dd9` / `#2563eb` / `#3b82f6` / `#38bdf8`. dash and
  retina nearly agree; owl and map each go their own way. One accent value, or a
  documented light/dark pair, would read as more intentional.
- **Token naming drift.** owl uses `--ink` / `--paper`, retina uses `--text` /
  `--bg`, dash uses `--bg-primary` / `--text-primary`, and the map has no custom
  properties at all (hardcoded hex throughout). Nothing is portable between them.
  `tokens.css` proposes one naming; adopting it in the live sites would remove
  the drift.
- **Semantic colours drift by a shade.** Green is `#16a34a` (marketing),
  `#10b981` (console), `#4ade80` (map); amber and red shift similarly. Close
  enough to look like one intent, far enough to not match.
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
- **No `prefers-reduced-motion`.** All of them run infinite animations (pulses,
  dashed signal flow, ring expansions, the map's pulsing "LIVE" badge) with no
  reduced-motion guard. The
  `tokens.css` `.reveal` helper adds one; the SVG loops need the same treatment.
- **Focus styles.** None of the surfaces define a visible `:focus-visible`
  treatment; keyboard focus rides on the browser default.

**Polish**

- **Missing social metadata.** None of the three set `og:image` /
  `twitter:card` / canonical, so link previews are bare. A single shared OG image
  per surface would help.
- **The operational surfaces carry little brand.** dash dropped the type system
  for system fonts and cool slate; the map runs Inter-only on dark navy with a
  brighter blue. Both are defensible for tools, but between them they share
  almost nothing visible with the marketing brand beyond a blue accent and the
  uppercase micro-label. Standardising the micro-label and reusing one blue would
  connect all four without slowing the tools down.
- **The dark map is unaudited for contrast here.** The accessibility notes above
  were checked against the light surfaces; the map's light-slate-on-navy ramp
  looks reasonable but has not been contrast-tested, and it inherits the same
  no-`prefers-reduced-motion`, no-`:focus-visible` gaps.
- **Inconsistent animation approach.** retina's hero uses inline SVG SMIL
  (`<animate>`) while owl and dash use CSS keyframes. Standardising on CSS would
  make the shared radar motif portable.
