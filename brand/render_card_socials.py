#!/usr/bin/env python3
"""
Generate one social post per AURA card — 78 in total.

For each card:
  - Reads the card data (name, affirmation, 3-colour palette) from index.html
  - Builds an SVG with the card-personality orb + name + affirmation + AURA mark
  - Renders to PNG via macOS qlmanage
  - Outputs both Instagram square (1080×1080) and 4:5 portrait (1080×1350)

Output:  brand/social/cards/{slug}-1080.png  (square)
         brand/social/cards/{slug}-4-5.png   (portrait)
         brand/social/cards/_index.md         (gallery contact-sheet HTML)

Run:  python3 render_card_socials.py
"""
import os
import re
import json
import subprocess
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_HTML = os.path.join(ROOT, 'index.html')
OUT_DIR = os.path.join(ROOT, 'brand', 'social', 'cards')
SVG_TMP = os.path.join(OUT_DIR, '_svg')
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(SVG_TMP, exist_ok=True)


# ─── 1. Extract the auraDeck array from index.html ──────────────────────
def extract_deck():
    with open(SRC_HTML, encoding='utf-8') as fh:
        text = fh.read()
    # Find the start of `const auraDeck = [`
    m = re.search(r'const auraDeck\s*=\s*\[', text)
    if not m:
        raise RuntimeError('Could not locate auraDeck in index.html')
    start = m.end() - 1   # the opening '['
    # Find the matching closing bracket using balance counting
    depth = 0
    end = None
    for i in range(start, len(text)):
        ch = text[i]
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise RuntimeError('Could not find end of auraDeck array')
    array_text = text[start:end]

    # Pull each card object out individually — they're {...},
    # at the top level of the array. Use brace-balance matching.
    cards = []
    i = 0
    while i < len(array_text):
        ch = array_text[i]
        if ch == '{':
            j = i
            d = 0
            while j < len(array_text):
                cj = array_text[j]
                if cj == '{':
                    d += 1
                elif cj == '}':
                    d -= 1
                    if d == 0:
                        cards.append(array_text[i:j+1])
                        i = j + 1
                        break
                j += 1
        else:
            i += 1

    parsed = []
    for raw in cards:
        # Convert JS object syntax → JSON
        s = raw
        # Quote unquoted keys: id: → "id":
        s = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', s)
        # NOTE: do NOT convert single→double quotes — apostrophes inside
        # strings ("You've", "don't") break that. The deck uses " throughout.
        # Strip trailing commas inside arrays/objects
        s = re.sub(r',(\s*[}\]])', r'\1', s)
        try:
            parsed.append(json.loads(s))
        except json.JSONDecodeError as e:
            print(f'  ⚠  parse error on card: {raw[:80]}…  ({e})')
    return parsed


# ─── 2. Hex helpers (mirrors the JS in index.html) ──────────────────────
def hex_rgb(hexstr):
    h = hexstr.replace('#', '').ljust(6, '0')[:6]
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

def rgb_hex(r, g, b):
    def c(v): return f'{max(0, min(255, round(v))):02x}'
    return '#' + c(r) + c(g) + c(b)

def blend_hex(a, b, t):
    ar, ag, ab_ = hex_rgb(a); br, bg_, bb = hex_rgb(b)
    return rgb_hex(ar + (br-ar)*t, ag + (bg_-ag)*t, ab_ + (bb-ab_)*t)

def darken_hex(hexstr, amt):
    r, g, b = hex_rgb(hexstr)
    return rgb_hex(r*(1-amt), g*(1-amt), b*(1-amt))

def lighten_hex(hexstr, amt):
    r, g, b = hex_rgb(hexstr)
    return rgb_hex(r + (255-r)*amt, g + (255-g)*amt, b + (255-b)*amt)


# ─── 3. Build the orb gradient (mirrors buildCardOrbGradient in JS) ─────
def build_orb_gradient(colors):
    c1 = colors[0] if len(colors) > 0 else '#9560D6'
    c2 = colors[1] if len(colors) > 1 else '#26A69A'
    c3 = colors[2] if len(colors) > 2 else '#1976D2'
    inner_lift = lighten_hex(c1, 0.22)
    mid12 = blend_hex(c1, c2, 0.55)
    mid23 = blend_hex(c2, c3, 0.55)
    rim = darken_hex(c3, 0.34)
    rim_soft = darken_hex(c3, 0.18)
    body = (
        f'radial-gradient(circle at 50% 50%, '
        f'{inner_lift} 0%, {c1} 12%, {mid12} 26%, {c2} 40%, '
        f'{mid23} 52%, {c3} 62%, {rim_soft} 70%, {rim_soft}66 76%, transparent 84%)'
    )
    rim_layer = (
        f'radial-gradient(circle at 50% 50%, transparent 58%, '
        f'{rim} 62%, {rim} 66%, transparent 70%)'
    )
    return body, rim_layer


# ─── 4. SVG template (Instagram 4:5 — 1080×1350) ────────────────────────
SVG_TEMPLATE_4_5 = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1350" width="1080" height="1350">
  <defs>
    <radialGradient id="bgNight" cx="50%" cy="42%" r="68%">
      <stop offset="0%"  stop-color="{atmos_hex}" stop-opacity="0.34"/>
      <stop offset="36%" stop-color="#160F22" stop-opacity="1"/>
      <stop offset="100%" stop-color="#06040A" stop-opacity="1"/>
    </radialGradient>
    <radialGradient id="orbBody{nid}" cx="50%" cy="50%" r="50%">
      <stop offset="0%"  stop-color="{c1_lift}"/>
      <stop offset="12%" stop-color="{c1}"/>
      <stop offset="26%" stop-color="{mid12}"/>
      <stop offset="40%" stop-color="{c2}"/>
      <stop offset="52%" stop-color="{mid23}"/>
      <stop offset="62%" stop-color="{c3}"/>
      <stop offset="70%" stop-color="{rim_soft}"/>
      <stop offset="76%" stop-color="{rim_soft}" stop-opacity="0.4"/>
      <stop offset="84%" stop-color="{rim_soft}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="orbRim{nid}" cx="50%" cy="50%" r="50%">
      <stop offset="58%" stop-color="{rim}" stop-opacity="0"/>
      <stop offset="62%" stop-color="{rim}" stop-opacity="1"/>
      <stop offset="66%" stop-color="{rim}" stop-opacity="1"/>
      <stop offset="70%" stop-color="{rim}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="goldSparkle" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%"  stop-color="#FFE38A"/>
      <stop offset="50%" stop-color="#F5D77A"/>
      <stop offset="100%" stop-color="#A77E20"/>
    </linearGradient>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400&amp;display=swap');
      .name {{
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-weight: 400;
        font-size: 132px;
        letter-spacing: 0.06em;
        fill: #F8F4FF;
        text-anchor: middle;
      }}
      .affirmation {{
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-weight: 300;
        font-style: italic;
        font-size: 44px;
        letter-spacing: 0.02em;
        fill: rgba(232, 220, 248, 0.86);
        text-anchor: middle;
      }}
      .brand {{
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-weight: 300;
        font-size: 28px;
        letter-spacing: 0.42em;
        fill: rgba(232, 220, 248, 0.46);
        text-anchor: middle;
      }}
      .handle {{
        font-family: -apple-system, 'Inter', 'Helvetica Neue', sans-serif;
        font-weight: 400;
        font-size: 22px;
        letter-spacing: 0.18em;
        fill: rgba(232, 220, 248, 0.35);
        text-anchor: middle;
      }}
    </style>
  </defs>

  <rect width="1080" height="1350" fill="url(#bgNight)"/>

  <!-- Subtle stars -->
  <g fill="#FFFFFF" opacity="0.55">
    <circle cx="148"  cy="200"  r="2.6"/>
    <circle cx="924"  cy="156"  r="2.0"/>
    <circle cx="240"  cy="1180" r="2.2"/>
    <circle cx="888"  cy="1216" r="2.4"/>
    <circle cx="92"   cy="612"  r="1.6"/>
    <circle cx="980"  cy="624"  r="1.8"/>
    <circle cx="408"  cy="120"  r="1.6"/>
    <circle cx="640"  cy="1280" r="1.8"/>
    <circle cx="540"  cy="86"   r="2.4"/>
  </g>

  <!-- The orb (centred in the upper-middle) -->
  <g transform="translate(540, 540)">
    <circle r="380" fill="url(#orbBody{nid})"/>
    <circle r="380" fill="url(#orbRim{nid})"/>
  </g>

  <!-- Card name -->
  <text class="name" x="540" y="1010">{name}</text>

  <!-- Affirmation, wrapped onto up to 2 lines -->
  <text class="affirmation" x="540" y="1108">{affirm_line1}</text>
  {affirm_line2_tag}

  <!-- AURA brand strip — bottom -->
  <g transform="translate(540, 1248)">
    <!-- Sparkle mark to the left of AURA -->
    <g transform="translate(-120, -22) scale(0.42)">
      <path d="M42,3.5 C42,30.9 51.6,40 80.5,40 C51.6,40 42,50.1 42,80.5 C42,50.1 32.4,40 3.5,40 C32.4,40 42,30.9 42,3.5 Z"
            fill="url(#goldSparkle)"/>
      <circle cx="42" cy="42" r="38.5" fill="none"
              stroke="#D4A93A" stroke-width="1.6" stroke-opacity="0.6"/>
    </g>
    <text class="brand" x="0" y="0">AURA</text>
  </g>
  <text class="handle" x="540" y="1300">aura-me.app</text>
</svg>
"""


def slugify(name):
    s = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')
    return s or 'card'


def wrap_affirmation(text, max_chars=42):
    """Two-line wrap. Affirmations are short; this is just an aesthetic guard."""
    if len(text) <= max_chars:
        return text, ''
    words = text.split(' ')
    line1, line2 = [], []
    n = len(words)
    target = sum(len(w) for w in words) // 2
    used = 0
    for i, w in enumerate(words):
        if used + len(w) <= target:
            line1.append(w); used += len(w) + 1
        else:
            line2 = words[i:]; break
    if not line2:
        return text, ''
    return ' '.join(line1), ' '.join(line2)


def render_card_svg(card):
    """Return rendered SVG string for one card."""
    colors = card.get('colors', ['#9560D6','#26A69A','#1976D2'])
    while len(colors) < 3:
        colors.append(colors[-1])

    c1, c2, c3 = colors[0], colors[1], colors[2]
    line1, line2 = wrap_affirmation(card.get('affirmation', '').strip().strip('"'))

    affirm_line2_tag = (f'<text class="affirmation" x="540" y="1170">{line2}</text>'
                        if line2 else '')

    return SVG_TEMPLATE_4_5.format(
        nid=card.get('id', 0),
        atmos_hex=lighten_hex(c1, 0.10),
        c1=c1, c2=c2, c3=c3,
        c1_lift=lighten_hex(c1, 0.22),
        mid12=blend_hex(c1, c2, 0.55),
        mid23=blend_hex(c2, c3, 0.55),
        rim=darken_hex(c3, 0.34),
        rim_soft=darken_hex(c3, 0.18),
        name=card.get('name', '').strip(),
        affirm_line1=line1,
        affirm_line2_tag=affirm_line2_tag,
    )


def svg_to_png(svg_path, png_path, max_size=1350):
    """Render SVG → PNG via qlmanage, then crop to actual content."""
    tmp_dir = '/tmp/aura-cardsoc'
    os.makedirs(tmp_dir, exist_ok=True)
    subprocess.run(
        ['qlmanage', '-t', '-s', str(max_size), '-o', tmp_dir, svg_path],
        capture_output=True, check=True
    )
    rendered = os.path.join(tmp_dir, os.path.basename(svg_path) + '.png')
    if not os.path.exists(rendered):
        return False

    # qlmanage gives us a square — content is in the upper portion.
    # Open as RGBA, find non-transparent bbox, crop, then resize to canonical sizes.
    img = Image.open(rendered).convert('RGBA')
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)

    # Aspect-fit into 1080×1350 (4:5)
    target_w, target_h = 1080, 1350
    img.thumbnail((target_w, target_h), Image.LANCZOS)
    canvas = Image.new('RGB', (target_w, target_h), (13, 13, 15))
    px = (target_w - img.width) // 2
    py = (target_h - img.height) // 2
    if img.mode == 'RGBA':
        canvas.paste(img, (px, py), mask=img.split()[3])
    else:
        canvas.paste(img, (px, py))
    canvas.save(png_path, 'PNG', optimize=True)
    os.remove(rendered)
    return True


def main():
    print('Extracting auraDeck from index.html…')
    deck = extract_deck()
    print(f'Found {len(deck)} cards.\n')
    if len(deck) < 70:
        print(f'WARNING: expected ~78 cards, got {len(deck)}. Check parser.')

    print(f'Rendering to {OUT_DIR}…\n')
    success = 0
    for i, card in enumerate(deck, 1):
        name = card.get('name', f'card-{card.get("id", i)}')
        slug = f"{card.get('id', i):02d}-{slugify(name)}"
        svg_path = os.path.join(SVG_TMP, f'{slug}.svg')
        png_path = os.path.join(OUT_DIR, f'{slug}.png')

        with open(svg_path, 'w', encoding='utf-8') as fh:
            fh.write(render_card_svg(card))

        if svg_to_png(svg_path, png_path):
            print(f'  ✓ {slug:.<48s} {os.path.getsize(png_path)//1024} KB')
            success += 1
        else:
            print(f'  ✗ {slug} — render failed')

    print(f'\n{success}/{len(deck)} cards rendered.')
    print(f'Output:  {OUT_DIR}')

    # Write a contact sheet HTML so they can be reviewed at a glance
    sheet = os.path.join(OUT_DIR, '_contact-sheet.html')
    cards_html = '\n'.join(
        f'<figure><img src="{slugify(c.get("name", "card"))}" loading="lazy"/>'
        f'<figcaption>{c.get("name", "")}</figcaption></figure>'
        for c in deck
    )
    # Simpler: list the actual filenames since we slug+id them
    filenames = sorted(f for f in os.listdir(OUT_DIR) if f.endswith('.png'))
    items = '\n'.join(
        f'  <figure><img src="{f}" loading="lazy"/>'
        f'<figcaption>{f.replace(".png","")}</figcaption></figure>'
        for f in filenames
    )
    with open(sheet, 'w', encoding='utf-8') as fh:
        fh.write(f'''<!doctype html><html><head><meta charset="utf-8">
<title>AURA — All 78 social cards</title>
<style>
body {{ background:#0d0d0f; color:#fafafa; font-family:-apple-system,sans-serif; padding:32px; }}
h1 {{ font-family:'Cormorant Garamond',serif; font-weight:300; letter-spacing:0.08em; font-size:44px; margin-bottom:24px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:16px; }}
figure {{ margin:0; }}
img {{ width:100%; border-radius:18px; display:block; }}
figcaption {{ font-size:12px; color:rgba(255,255,255,0.55); padding:8px 4px; font-family:ui-monospace,monospace; }}
</style></head><body>
<h1>AURA — 78 card socials</h1>
<div class="grid">
{items}
</div>
</body></html>''')
    print(f'Contact sheet: {sheet}')


if __name__ == '__main__':
    main()
