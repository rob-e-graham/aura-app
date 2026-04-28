#!/usr/bin/env python3
"""
Generate one social-post PNG per AURA card — 78 in total.

Pure-Pillow renderer (no SVG / qlmanage involvement) so every element
draws reliably: gradient orb, gradient background, stars, all the text
in real Cormorant Garamond from local TTFs, sparkle path drawn as a
polygon, AURA wordmark, handle.

Output: brand/social/cards/{slug}.png   (1080×1350 Instagram 4:5)
        brand/social/cards/_contact-sheet.html

Run:    python3 render_card_socials.py
"""
import math
import os
import re
import json
import random
import colorsys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_HTML   = os.path.join(ROOT, 'index.html')
OUT_DIR    = os.path.join(ROOT, 'brand', 'social', 'cards')
FONT_DIR   = os.path.join(ROOT, 'brand', '_fonts')
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1080, 1350

# ─── Fonts ──────────────────────────────────────────────────────────────
F_REG    = os.path.join(FONT_DIR, 'CormorantGaramond-Regular.ttf')
F_LIGHT  = os.path.join(FONT_DIR, 'CormorantGaramond-Light.ttf')
F_ITAL   = os.path.join(FONT_DIR, 'CormorantGaramond-LightItalic.ttf')
def font(path, size): return ImageFont.truetype(path, size)


# ─── 1. Extract auraDeck (same parser as before) ─────────────────────────
def extract_deck():
    with open(SRC_HTML, encoding='utf-8') as fh:
        text = fh.read()
    m = re.search(r'const auraDeck\s*=\s*\[', text)
    if not m: raise RuntimeError('auraDeck not found')
    start = m.end() - 1
    depth, end = 0, None
    for i in range(start, len(text)):
        if text[i] == '[': depth += 1
        elif text[i] == ']':
            depth -= 1
            if depth == 0: end = i + 1; break
    arr = text[start:end]
    cards, i = [], 0
    while i < len(arr):
        if arr[i] == '{':
            j, d = i, 0
            while j < len(arr):
                if arr[j] == '{': d += 1
                elif arr[j] == '}':
                    d -= 1
                    if d == 0: cards.append(arr[i:j+1]); i = j + 1; break
                j += 1
        else: i += 1
    parsed = []
    for raw in cards:
        s = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', raw)
        s = re.sub(r',(\s*[}\]])', r'\1', s)
        try: parsed.append(json.loads(s))
        except json.JSONDecodeError as e:
            print(f'  ⚠  parse error: {e}; first 80 chars: {raw[:80]}')
    return parsed


# ─── 2. Hex helpers ──────────────────────────────────────────────────────
def hexrgb(h):
    h = h.replace('#','').ljust(6,'0')[:6]
    return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))
def rgbhex(rgb):
    return '#{:02X}{:02X}{:02X}'.format(*[max(0, min(255, int(round(v)))) for v in rgb])
def lerp(a, b, t): return a + (b-a)*t
def lerp_rgb(a, b, t): return tuple(int(round(lerp(a[i],b[i],t))) for i in range(3))
def lighten(rgb, amt): return tuple(int(round(rgb[i] + (255-rgb[i])*amt)) for i in range(3))
def darken(rgb, amt):  return tuple(int(round(rgb[i] * (1-amt))) for i in range(3))
def clamp(v, lo, hi): return max(lo, min(hi, v))

PALETTE_ANCHORS = {
    'major': (268, 0.54, 0.55),
    'energy': (18, 0.78, 0.55),
    'heart': (328, 0.58, 0.60),
    'mind': (228, 0.48, 0.48),
    'foundation': (138, 0.40, 0.46),
    'default': (268, 0.54, 0.55),
}

def hex_to_hsl(hexstr):
    r, g, b = hexrgb(hexstr)
    h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
    return (h * 360.0, s, l)

def hsl_to_hex(h, s, l):
    r, g, b = colorsys.hls_to_rgb((h % 360.0) / 360.0, clamp(l, 0, 1), clamp(s, 0, 1))
    return rgbhex((r * 255.0, g * 255.0, b * 255.0))

def mix_hue(a, b, t):
    delta = ((b - a + 540.0) % 360.0) - 180.0
    return (a + delta * t) % 360.0

def is_muddy(h, s, l):
    return 20 <= h <= 62 and s < 0.45 and l < 0.72

def fashion_score(hexstr, index=0):
    h, s, l = hex_to_hsl(hexstr)
    light_penalty = 0.28 if l > 0.82 else 0.0
    neutral_penalty = 0.34 if s < 0.18 else 0.0
    muddy_penalty = 0.16 if is_muddy(h, s, l) else 0.0
    balance = 1.0 - min(1.0, abs(l - 0.52) / 0.52)
    return (s * 0.9) + (balance * 0.5) + (0.12 if index == 0 else 0.0) - light_penalty - neutral_penalty - muddy_penalty

def style_hex(hexstr, role, anchor_h, primary_h=None):
    h, s, l = hex_to_hsl(hexstr)
    muddy = is_muddy(h, s, l)
    too_light = l > 0.82
    too_neutral = s < 0.18
    if role == 'primary':
        h = mix_hue(h, anchor_h, 0.72 if (muddy or too_light or too_neutral) else 0.16)
        s = clamp(max(s, 0.46 if muddy else 0.52), 0.42, 0.78)
        l = clamp(0.52 if too_light else (0.48 if l < 0.26 else l), 0.40, 0.62)
    elif role == 'secondary':
        target_h = ((primary_h or anchor_h) + 34.0) % 360.0
        h = mix_hue(h, target_h, 0.62 if (muddy or too_light or too_neutral) else 0.18)
        s = clamp(max(s, 0.38), 0.34, 0.72)
        l = clamp(0.64 if too_light else l, 0.34, 0.68)
    else:
        target_h = ((primary_h or anchor_h) - 28.0) % 360.0
        h = mix_hue(h, target_h, 0.68 if (muddy or too_light or too_neutral) else 0.28)
        s = clamp(max(s, 0.32), 0.28, 0.70)
        l = clamp(0.34 if too_light else (0.28 if l < 0.18 else l), 0.24, 0.52)
    return hsl_to_hex(h, s, l)

def normalize_palette(card):
    raw = list(card.get('colors') or ['#9560D6', '#26A69A', '#1976D2'])[:3]
    while len(raw) < 3:
        raw.append(raw[-1])
    group = str(card.get('group') or 'default').strip().lower()
    anchor_h = PALETTE_ANCHORS.get(group, PALETTE_ANCHORS['default'])[0]
    scored = sorted(
        ({'hex': hexc, 'index': idx, 'score': fashion_score(hexc, idx)} for idx, hexc in enumerate(raw)),
        key=lambda item: item['score'],
        reverse=True,
    )
    primary_base = scored[0]['hex']
    primary_idx = scored[0]['index']
    others = [hexc for idx, hexc in enumerate(raw) if idx != primary_idx]
    primary = style_hex(primary_base, 'primary', anchor_h)
    primary_h = hex_to_hsl(primary)[0]
    secondary = style_hex(others[0] if others else raw[(primary_idx + 1) % 3], 'secondary', anchor_h, primary_h)
    tertiary = style_hex(others[1] if len(others) > 1 else raw[(primary_idx + 2) % 3], 'tertiary', anchor_h, primary_h)
    return [primary, secondary, tertiary]


# ─── 3. Build card-personality orb gradient as a Pillow image ────────────
def build_orb_image(colors, size=760):
    """Render the 3-colour personality orb to an RGBA image (transparent bg)."""
    c1 = hexrgb(colors[0])
    c2 = hexrgb(colors[1] if len(colors) > 1 else colors[0])
    c3 = hexrgb(colors[2] if len(colors) > 2 else colors[0])
    # FULL primary colour at the centre — no white dot. Three distinct
    # colours from the card's palette. Harmony is tuned in the data,
    # not collapsed in code.
    mid12 = lerp_rgb(c1, c2, 0.45)
    mid23 = lerp_rgb(c2, c3, 0.50)
    aura = lerp_rgb(c3, c1, 0.18)
    rim_soft = lerp_rgb(c3, aura, 0.35)
    rim = darken(c3, 0.28)

    # Body gradient stops: (offset 0–1, rgba) — c1 holds 0–22% solid
    body_stops = [
        (0.00, (*c1, 255)),
        (0.22, (*c1, 255)),
        (0.42, (*mid12, 255)),
        (0.56, (*c2, 255)),
        (0.68, (*mid23, 255)),
        (0.78, (*c3, 255)),
        (0.86, (*rim_soft, 210)),
        (0.90, (*rim_soft, 120)),
        (0.96, (*rim_soft, 0)),
        (1.00, (*rim_soft, 0)),
    ]
    # Hard outer rim ring
    rim_stops = [
        (0.60, (*rim, 0)),
        (0.68, (*rim, 235)),
        (0.74, (*rim, 235)),
        (0.82, (*rim, 0)),
        (1.00, (*rim, 0)),
    ]

    def sample(stops, t):
        """Linear interpolation between gradient stops."""
        for i in range(len(stops)-1):
            o0, c0 = stops[i]; o1, c1 = stops[i+1]
            if o0 <= t <= o1:
                if o1 == o0: return c1
                k = (t - o0) / (o1 - o0)
                return tuple(int(round(c0[j] + (c1[j]-c0[j])*k)) for j in range(4))
        return stops[-1][1]

    img = Image.new('RGBA', (size, size), (0,0,0,0))
    px = img.load()
    cx = cy = size / 2.0
    R = size / 2.0

    for y in range(size):
        dy = y - cy
        for x in range(size):
            dx = x - cx
            d = math.sqrt(dx*dx + dy*dy) / R
            if d > 1.0:
                continue
            body_c = sample(body_stops, d)
            rim_c  = sample(rim_stops, d)
            # Composite rim over body
            br, bg, bb, ba = body_c
            rr, rg, rbb, ra = rim_c
            if ra > 0:
                a = ra / 255.0
                r = int(round(rr * a + br * (1 - a)))
                g = int(round(rg * a + bg * (1 - a)))
                bch = int(round(rbb * a + bb * (1 - a)))
                final_a = int(round(ra + ba * (1 - a)))
                px[x, y] = (r, g, bch, final_a)
            else:
                px[x, y] = body_c

    # Soft Gaussian blur for that slightly-glowing feel
    img = img.filter(ImageFilter.GaussianBlur(radius=1.8))
    return img


# ─── 4. Background: dark gradient with a faint tint of the card colour ──
def build_background(c1_hex):
    """Radial dark gradient with a subtle tint of the card's primary."""
    tint = lighten(hexrgb(c1_hex), 0.10)   # primary slightly lifted
    near = (22, 15, 34)                     # warm near-mid
    far  = (6, 4, 10)                       # deep outer
    img = Image.new('RGB', (W, H), (0,0,0))
    px = img.load()
    cx, cy = W / 2, H * 0.42
    R = math.sqrt((W*0.68)**2 + (H*0.68)**2)
    for y in range(H):
        dy = y - cy
        for x in range(W):
            dx = x - cx
            t = min(1.0, math.sqrt(dx*dx + dy*dy) / R)
            # Three-stop blend: tint(0%, alpha 0.34) → near(36%) → far(100%)
            if t < 0.36:
                k = t / 0.36
                # Blend tint at 0.34 alpha with near at full alpha
                base = lerp_rgb(tint, near, k)
                # Mix 34% tint contribution at center, 0% by t=0.36
                tint_alpha = (1.0 - k) * 0.34
                col = lerp_rgb(base, tint, tint_alpha * 0.6)  # subtle wash
                # Simplified: just blend tint→near
                col = lerp_rgb(tint, near, k * 0.92)
            else:
                k = (t - 0.36) / 0.64
                col = lerp_rgb(near, far, min(1.0, k))
            px[x, y] = col
    return img


# ─── 5. Sparkle path drawn as a polygon (75% control, 4-point sparkle) ──
def draw_sparkle(canvas, cx, cy, r, color=(212, 169, 58), ring_color=None):
    """Approximation of the 4-point sparkle as a smooth polygon at scale r."""
    # Points roughly mirroring the SVG cubic curves with sampled curve points.
    # Using 64 sampled points around the path for a smooth shape.
    def cubic(p0, p1, p2, p3, t):
        u = 1-t
        return (u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
                u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1])

    # Sparkle in 84-unit space, scale to r (r = full radius from centre).
    # Visual centre at (42, 40) within an 84-unit box.
    # Tips: top (42,3.5), right (80.5,40), bottom (42,80.5), left (3.5,40)
    s = r / 38.5  # scale so radius matches r
    ox, oy = cx, cy

    def P(x, y):
        return (ox + (x - 42) * s, oy + (y - 40) * s)

    segments = [
        (P(42,3.5),  P(42,30.9), P(51.6,40), P(80.5,40)),
        (P(80.5,40), P(51.6,40), P(42,50.1), P(42,80.5)),
        (P(42,80.5), P(42,50.1), P(32.4,40), P(3.5,40)),
        (P(3.5,40),  P(32.4,40), P(42,30.9), P(42,3.5)),
    ]
    poly = []
    for seg in segments:
        for i in range(16):
            poly.append(cubic(*seg, i/16))
    poly.append(segments[-1][3])

    canvas.polygon(poly, fill=color)
    # Optional outer ring
    if ring_color:
        ring_r = r * (38.5/40)
        canvas.ellipse((ox-ring_r, oy-ring_r, ox+ring_r, oy+ring_r),
                       outline=ring_color, width=max(1, int(s*1.6)))


# ─── 6. Wrap text into N lines that fit a max width ──────────────────────
def wrap_text(draw, text, font_, max_w):
    words = text.split()
    lines, line = [], []
    for w in words:
        candidate = ' '.join(line + [w])
        bbox = draw.textbbox((0,0), candidate, font=font_)
        if bbox[2] - bbox[0] <= max_w:
            line.append(w)
        else:
            if line: lines.append(' '.join(line))
            line = [w]
    if line: lines.append(' '.join(line))
    return lines


# ─── 7. Render one card ──────────────────────────────────────────────────
def render_card(card, out_path):
    colors = normalize_palette(card)
    name = card.get('name', '').strip()
    affirm = card.get('affirmation', '').strip().strip('"')

    # Background
    canvas = build_background(colors[0]).convert('RGBA')

    # Stars (deterministic per-card so each gets a unique starfield)
    rnd = random.Random(card.get('id', 0) * 7919)
    star_layer = Image.new('RGBA', (W, H), (0,0,0,0))
    sd = ImageDraw.Draw(star_layer)
    for _ in range(28):
        x = rnd.randint(40, W-40)
        y = rnd.randint(40, H-40)
        # Avoid the orb area roughly
        if abs(x - W/2) < 380 and abs(y - 540) < 380: continue
        r = rnd.choice([1.4, 1.6, 1.8, 2.2, 2.6])
        a = rnd.randint(120, 220)
        sd.ellipse((x-r, y-r, x+r, y+r), fill=(255, 255, 255, a))
    canvas = Image.alpha_composite(canvas, star_layer)

    # Orb
    orb = build_orb_image(colors, size=760)
    canvas.paste(orb, (W//2 - 380, 540 - 380), orb)

    # Text
    draw = ImageDraw.Draw(canvas)

    # Name — Cormorant Garamond Regular 132pt
    name_font = font(F_REG, 132)
    name_bbox = draw.textbbox((0,0), name, font=name_font)
    name_w = name_bbox[2] - name_bbox[0]
    draw.text((W//2 - name_w//2, 988), name, font=name_font, fill=(248, 244, 255, 255))

    # Affirmation — Light italic 44pt, wrap to 2 lines
    aff_font = font(F_ITAL, 44)
    aff_lines = wrap_text(draw, affirm, aff_font, W - 200)[:2]
    y = 1160
    for line in aff_lines:
        b = draw.textbbox((0,0), line, font=aff_font)
        lw = b[2] - b[0]
        draw.text((W//2 - lw//2, y), line, font=aff_font, fill=(232, 220, 248, 220))
        y += 56

    # Brand strip — sparkle + AURA wordmark + handle
    brand_y = 1268
    sparkle_x = W//2 - 130
    draw_sparkle(draw, sparkle_x, brand_y, 22,
                 color=(212, 169, 58, 255),
                 ring_color=(212, 169, 58, 160))

    aura_font = font(F_LIGHT, 36)
    aura_bbox = draw.textbbox((0,0), 'AURA', font=aura_font)
    # Letter-spaced manually
    spaced = 'A U R A'
    sb = draw.textbbox((0,0), spaced, font=aura_font)
    sw = sb[2] - sb[0]
    draw.text((W//2 - sw//2 + 20, brand_y - 22), spaced, font=aura_font,
              fill=(232, 220, 248, 200))

    handle_font = font(F_LIGHT, 22)
    handle = 'aura-me.app'
    hb = draw.textbbox((0,0), handle, font=handle_font)
    hw = hb[2] - hb[0]
    draw.text((W//2 - hw//2, 1316), handle, font=handle_font,
              fill=(232, 220, 248, 130))

    # Save
    canvas.convert('RGB').save(out_path, 'PNG', optimize=True)


# ─── 8. Main ─────────────────────────────────────────────────────────────
def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-') or 'card'

def main():
    print('Extracting auraDeck…')
    deck = extract_deck()
    print(f'Found {len(deck)} cards.\n')

    print('Rendering with pure Pillow (every element drawn directly)…\n')
    success = 0
    for card in deck:
        cid = card.get('id', 0)
        name = card.get('name', f'card-{cid}')
        slug = f'{cid:02d}-{slugify(name)}'
        out_path = os.path.join(OUT_DIR, f'{slug}.png')
        try:
            render_card(card, out_path)
            kb = os.path.getsize(out_path) // 1024
            print(f'  ✓ {slug:.<48s} {kb} KB')
            success += 1
        except Exception as e:
            print(f'  ✗ {slug}: {e}')

    print(f'\n{success}/{len(deck)} rendered.')
    print(f'Output: {OUT_DIR}')

    # Contact sheet
    files = sorted(f for f in os.listdir(OUT_DIR) if f.endswith('.png'))
    items = '\n'.join(
        f'  <figure><img src="{f}" loading="lazy"/>'
        f'<figcaption>{f.replace(".png","")}</figcaption></figure>'
        for f in files
    )
    sheet = os.path.join(OUT_DIR, '_contact-sheet.html')
    with open(sheet, 'w') as fh:
        fh.write(f'''<!doctype html><html><head><meta charset="utf-8">
<title>AURA — All 78 social cards</title>
<style>
body {{ background:#0d0d0f; color:#fafafa; font-family:-apple-system,sans-serif; padding:32px; margin:0; }}
h1 {{ font-family:'Cormorant Garamond',serif; font-weight:300; letter-spacing:0.08em; font-size:44px; margin-bottom:24px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:14px; }}
figure {{ margin:0; }}
img {{ width:100%; border-radius:14px; display:block; }}
figcaption {{ font-size:11px; color:rgba(255,255,255,0.55); padding:6px 4px; font-family:ui-monospace,monospace; }}
</style></head><body>
<h1>AURA — 78 social cards</h1>
<div class="grid">
{items}
</div>
</body></html>''')
    print(f'Contact sheet: {sheet}')


if __name__ == '__main__':
    main()
