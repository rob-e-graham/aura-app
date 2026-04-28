# AURA — Colourway System

The thinking behind every orb, every card palette, every merch capsule.
Three traditions feed it: **chromotherapy**, **aura research**, and
**fashion / streetwear colourways**. Each card sits in the intersection.

This doc is the behind-the-scenes for Fam, designers, fabric printers,
and anyone who needs to know *why* a card looks the way it does.

---

## 🎯 The rule (one line)

**Each card = one personality colour, one supporting accent, one tonal
shade of the personality.** Three colours, one family, one accent.

In code:
```
c1 = primary           ← the personality (chromotherapy hue)
c2 = supporting        ← the accent (fashion-styled secondary)
c3 = darken(c1, 0.32)  ← the grounding (tonal shade of c1)
```

The orb starts solid `c1`, blends through `c2` once, lands on `c3`, then
gets a hard rim grounded in `c1`'s family. **The eye reads ONE colour with
its own shadow + a single accent — not three competing colours.**

---

## Why three traditions

### 1. Chromotherapy (the why behind the primary colour)

Each of the 78 cards is anchored to a chromotherapy hue — the colour
chromatherapy practitioners associate with that emotional / energetic state.

| Card energy | Primary colour | Chromotherapy meaning |
|---|---|---|
| New beginnings (Leap, Spark) | Yellow / Gold | clarity, ego, awakening |
| Love (Love, Bond, Joy) | Rose / Soft Blush | heart-centre, connection |
| Will / momentum (Sovereign, Triumph) | Red | drive, vitality, root |
| Reflection (Oracle, Stillness) | Indigo / Violet | inner sight, intuition |
| Growth (Bloom, Seed) | Leaf Green | abundance, nurture |
| Calm (Calm, Surrender) | Sky / Aqua | release, flow |
| Mind (Clarity, Discernment) | Sapphire / Blue | thought, communication |
| Foundation (Stability, Legacy) | Forest / Deep Green | rootedness, structure |

The primary colour `c1` is **never** a marketing choice — it's the
chromotherapy hue. That's the system's spine.

### 2. AURA research (the why behind the orb shape)

Modern aura readers describe a healthy aura as:
- **One dominant colour** that radiates from the body
- **Layered with one or two supporting hues** that signal mood / focus
- **Held by a deeper grounding shade** at the outer edge — the
  "containment"

A balanced aura reads as **harmonious**. A muddy or chaotic aura reads as
**out of balance**. The visual language of the AURA orb mirrors this:

```
  ┌──────────────── outer rim (grounding shade — c1 darkened)
  │  ┌───────────── tertiary (c3 — tonal shade of c1)
  │  │  ┌────────── secondary (c2 — supporting accent)
  │  │  │  ┌─────── primary (c1 — full saturation, dominant)
  │  │  │  │
  ●──●──●──●  ← centre of the orb (always c1, always solid)
```

If the orb's three colours are clashing contrasts (red + cyan + green),
the aura reads as chaotic. If they're tonal (sage + cream + forest),
it reads as resolved. **AURA orbs = resolved auras. Always.**

### 3. Fashion / streetwear colourways (the why behind the harmony)

Look at how successful colourways in fashion work:

- **Nike Air Max "Sail/Wheat":** cream + tan + soft brown — three shades
  of one warm family, no contrast.
- **BAPE "1ST CAMO Olive":** olive + sage + military green — variations
  on green, no clash.
- **Aesop packaging:** amber glass + cream label + black type — one hue
  developed three ways.
- **The Row:** black + bone + camel — neutrals in conversation, never
  competing.
- **Adidas Yeezy "Bone":** off-white + cream + sand — micro-shifts of
  one tone.

The successful streetwear / quiet-luxury formula is **monochromatic with
ONE accent**, not rainbow. AURA orbs follow the same rule.

The orb is also designed to be **wearable** — when this same palette
becomes a scarf print, a tee chest mark, a poster, an enamel pin, the
viewer sees one beautiful tonal blend, not a clashing tarot diagram.

---

## How the orb gradient breaks down

For a 380-px-radius orb, the gradient stops are:

| Stop | % of radius | Colour | Role | Visual reading |
|---|---|---|---|---|
| 0% | 0–22% | `c1` (solid) | personality core | the dot you see — one strong colour |
| 22–42% | 20% band | `mid12` (c1 ↔ c2 blend) | transition | softens into the accent |
| 42–56% | 14% band | `c2` | supporting accent | the "vibe" colour |
| 56–68% | 12% band | `mid23` (c2 ↔ c3 blend) | transition | resolves toward the grounding |
| 68–78% | 10% band | `c3` (darker shade of c1) | grounding tone | depth of the primary |
| 78–86% | 8% band | `rimSoft` (c3 ↔ c1 mix) | aura halo | soft outer glow |
| 86–96% | 10% band | `rimSoft` fading | atmosphere | bleeds into the card |
| 96–100% | 4% band | transparent | edge | clean drop-off |
| **+ rim layer** | 60–82% | `darken(c1, 0.46)` | hard outer ring | the containment edge |

**Read it as:** centre is the personality (one colour, full saturation,
22% of the orb's radius — that's the "dot"). Then the accent enters and
fades. Then the grounding shade pulls the orb back into c1's family.
Then the hard rim contains it like an aura's outer boundary.

---

## What "balanced" means for an AURA orb

An orb is **balanced** when:

1. **The centre is one solid colour** (no white dot, no muddied blend).
2. **The dominant area is `c1`** — the primary should occupy the most
   visual space.
3. **The accent (`c2`) is short-lived** — a band, not a competing region.
4. **The outer fade is in `c1`'s family** — same hue, deeper value.
5. **The rim is grounded** — also `c1`-derived, never a contrasting hue.

An orb is **out of balance** when:
- The accent overpowers the primary.
- The outer ring is a contrasting hue (e.g. green centre + purple ring).
- The rim looks like it belongs to a different card.

The redesign on Apr 27, 2026 enforced this rule by deriving `c3` and
`rim` from `c1` directly (via `darken`), instead of using the raw third
colour from the card data — which often gave clashing tarot-style triads.

---

## The forbidden hue: brown

Per launch feedback, brown is **off-limits** for the personality colour.
Reasons:

- Browns are not flattering against most skin tones (the orbs need to be
  wearable in the merch line — scarf, tee, jewellery — and brown next to
  skin is usually muddy).
- Browns don't photograph well on social media (they read as "dust" not
  "intention").
- Streetwear/quiet-luxury brands use deep neutrals (charcoal, ink, taupe)
  rather than warm browns. Aesthetic shift.

Cards that previously used brown have replacements queued:
| Old (brown) | Replacement direction |
|---|---|
| `#8D6E63` Earth Brown (Scarcity) | Slate Plum or Smoked Lilac |
| `#BF360C` Rust (Grit) | Burgundy or Wine |
| `#89614D` Cocoa (Pause, Rest) | Petrol Blue or Charcoal |
| `#BBAF6D` Olive-Mustard (Oracle) | Smoked Saffron or Soft Indigo |

Implementation note: replacements happen in `auraDeck` in `index.html`.
After update, re-run `python3 brand/render_card_socials.py` to regenerate
the 78 social posters.

---

## Three colourway moods (system-wide tuning)

Each card is fixed to its chromotherapy primary, but the **secondary**
colour can shift to give the deck three "moods":

### Mood A — Pastel Wellness (current)
Soft secondaries, low saturation accents. Reads calm, feminine, spa.
Best for: app default, women's apparel capsule, healing line.

### Mood B — Streetwear Bold
Saturated mid-tone secondaries, moodier rims. Reads modern, unisex,
fashion-forward. Best for: tee drops, poster line, men's capsule.

### Mood C — Night Editorial
Deep secondaries, near-black rims. Reads premium, evening, gallery.
Best for: limited prints, brand campaign imagery, editorial shoots.

We're shipping in **Mood A** (pastel wellness). Mood B + C are post-launch
expansions — same chromotherapy spine, different mood layer on top.

---

## Where this doc plugs in

- **Designers:** when picking secondaries for a new card, follow the
  three-tradition test: is c1 a chromotherapy primary? Is c2 a fashion-
  acceptable accent (no brown)? Is c3 a tonal shade of c1?
- **Fam:** when explaining a card on social, lead with the chromotherapy
  meaning of c1, then describe the vibe of c2. Never explain c3 — it's
  always "depth of the primary".
- **Print / merch:** the SVG export of any orb already encodes the new
  c3 = darken(c1) rule. Sending an SVG to a printer = sending a
  fashion-grade tonal palette automatically.
- **Voice doc:** "Timeless Wisdom" is the marketing language for the
  chromotherapy + aura tradition behind the colours. Use it.

---

*Locked Apr 27, 2026. Update whenever the colour system itself changes,
not just when individual cards do.*
