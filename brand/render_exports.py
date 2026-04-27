#!/usr/bin/env python3
"""
Render every brand SVG to high-resolution PNG + JPG.

Pipeline:
  1. qlmanage renders SVG → 2048-square PNG (with transparent padding)
  2. PIL detects the non-transparent bounding box and crops cleanly
  3. PIL saves a PNG (transparent) and JPG (composited onto a chosen bg)

Run:  python3 render_exports.py
"""
import os
import subprocess
import sys
from PIL import Image

BRAND_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(BRAND_DIR, 'exports')
os.makedirs(EXPORT_DIR, exist_ok=True)

# (filename without .svg, jpg-background-rgb)
TARGETS = [
    # Horizontal wordmarks
    ('aura-wordmark-gold',         (255, 255, 255)),  # gold on white
    ('aura-wordmark-mono-black',   (255, 255, 255)),  # black on white
    ('aura-wordmark-mono-white',   ( 13,  13,  15)),  # white on night
    # Stacked lockups
    ('aura-stacked-gold',          (255, 255, 255)),
    ('aura-stacked-mono-black',    (255, 255, 255)),
    ('aura-stacked-mono-white',    ( 13,  13,  15)),
    # Sparkle marks
    ('aura-sparkle-gold',          (255, 255, 255)),
    ('aura-sparkle-mono-black',    (255, 255, 255)),
    ('aura-sparkle-mono-white',    ( 13,  13,  15)),
    ('aura-sparkle-mark-only',     (255, 255, 255)),
    # App icon (square, big background — already designed)
    ('aura-app-icon',              ( 13,  13,  15)),
]

PADDING_PX = 24   # whitespace breathing room around the content


def render_svg_to_png(svg_path, png_path, max_size=2048):
    """Use macOS qlmanage to render SVG → PNG. Returns True on success."""
    tmp_dir = '/tmp/aura-render'
    os.makedirs(tmp_dir, exist_ok=True)
    subprocess.run(
        ['qlmanage', '-t', '-s', str(max_size), '-o', tmp_dir, svg_path],
        capture_output=True, check=True
    )
    rendered = os.path.join(tmp_dir, os.path.basename(svg_path) + '.png')
    if not os.path.exists(rendered):
        return False
    os.replace(rendered, png_path)
    return True


def crop_to_content(img, padding=PADDING_PX):
    """
    Crop a PIL image to the bounding box of its non-transparent pixels,
    padded by `padding` on each side. Returns the cropped image.

    For images with no alpha channel (already a square JPG), this is a no-op.
    """
    if img.mode != 'RGBA':
        return img
    bbox = img.getbbox()
    if not bbox:
        return img
    left, top, right, bottom = bbox
    w, h = img.size
    left   = max(0, left   - padding)
    top    = max(0, top    - padding)
    right  = min(w, right  + padding)
    bottom = min(h, bottom + padding)
    return img.crop((left, top, right, bottom))


def composite_on_bg(img, bg_rgb):
    """Composite an RGBA image onto a flat RGB background. Returns RGB."""
    if img.mode != 'RGBA':
        return img.convert('RGB')
    bg = Image.new('RGB', img.size, bg_rgb)
    bg.paste(img, mask=img.split()[3])
    return bg


def export_one(name, jpg_bg):
    svg_path = os.path.join(BRAND_DIR, f'{name}.svg')
    if not os.path.exists(svg_path):
        print(f'  ⚠ skipping (missing): {name}.svg')
        return

    raw_png = os.path.join(EXPORT_DIR, f'{name}.raw.png')
    print(f'  rendering {name}.svg …')
    if not render_svg_to_png(svg_path, raw_png):
        print(f'  ✗ qlmanage failed: {name}')
        return

    img = Image.open(raw_png).convert('RGBA')
    cropped = crop_to_content(img)

    # Save PNG (preserves transparency)
    png_out = os.path.join(EXPORT_DIR, f'{name}.png')
    cropped.save(png_out, 'PNG', optimize=True)

    # Save JPG with the chosen background
    jpg_out = os.path.join(EXPORT_DIR, f'{name}.jpg')
    composite_on_bg(cropped, jpg_bg).save(jpg_out, 'JPEG', quality=92, optimize=True)

    # Clean up the un-cropped raw PNG
    os.remove(raw_png)

    w, h = cropped.size
    print(f'    ✓ {w}×{h} → {name}.png + {name}.jpg')


def main():
    print('Rendering AURA brand exports …\n')
    for name, jpg_bg in TARGETS:
        export_one(name, jpg_bg)
    print('\nDone. Files in:', EXPORT_DIR)


if __name__ == '__main__':
    main()
