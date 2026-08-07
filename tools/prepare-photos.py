#!/usr/bin/env python3
"""
prepare-photos.py — turn raw phone photos and Instagram screenshots into
the files the birthday card expects.

    python tools/prepare-photos.py

It reads everything from  tools/inbox/  and writes  assets/photo.jpg  plus
assets/memory-1.jpg, memory-2.jpg, ...

For Instagram screenshots it finds the actual photo inside the screenshot and
throws away the app chrome — the status bar, the username header, the
like/comment row and the caption. Detection works by scanning down the
screenshot for the band of rows that aren't Instagram's flat dark background.

Ordering: files are used in filename order. Put a `1-` prefix on whichever
one you want as the main portrait, or pass --main <filename>.

Options
-------
  --inbox DIR      where to read from       (default tools/inbox)
  --out DIR        where to write to        (default assets)
  --main NAME      which file becomes the main portrait
  --no-crop NAME   skip auto-cropping for this file (repeatable)
  --top N          force the crop's top edge, in pixels (with --only)
  --bottom N       force the crop's bottom edge, in pixels (with --only)
  --only NAME      process just this one file
  --debug          also write *_debug.png showing the detected crop
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps, ImageDraw, ImageFilter, ImageStat
except ImportError:
    sys.exit("Pillow is missing.  Run:  python -m pip install Pillow")

ROOT = Path(__file__).resolve().parent.parent

PORTRAIT_SIZE = 1000   # assets/photo.jpg  (square)
MEMORY_SIZE   = 900    # assets/memory-N.jpg (square)
JPEG_QUALITY  = 88

# An Instagram screenshot is tall and narrow; a normal photo isn't.
SCREENSHOT_MIN_RATIO = 1.9


# ----------------------------------------------------------------------
# Finding the photo inside a screenshot
# ----------------------------------------------------------------------
FLAT = 2.5      # stddev below this means "solid colour, edge to edge"


def row_spread(img):
    """Per-row standard deviation of brightness, across the full width.

    Instagram's dark-mode chrome is a solid fill, so its rows measure a dead
    flat 0. The photo is full-bleed, so even a night shot never gets close.
    Rows of caption text score high, but they sit between flat rows, which is
    what lets us tell a block of text from the photo itself.
    """
    small = img.convert("L").resize((200, img.height), Image.BILINEAR)
    px = small.load()
    w = small.width
    out = []
    for y in range(small.height):
        total = 0
        sq = 0
        for x in range(w):
            v = px[x, y]
            total += v
            sq += v * v
        mean = total / w
        out.append(max(0.0, sq / w - mean * mean) ** 0.5)
    return out


def find_photo_band(img):
    """Return (top, bottom) of the photo embedded in a screenshot."""
    spread = row_spread(img)
    h = len(spread)

    runs, start = [], None
    for y in range(h):
        if spread[y] > FLAT:
            if start is None:
                start = y
        elif start is not None:
            runs.append((start, y - 1))
            start = None
    if start is not None:
        runs.append((start, h - 1))

    if not runs:
        return 0, h - 1

    top, bottom = max(runs, key=lambda r: r[1] - r[0])

    # A full-bleed photo is always taller than it is... well, tall. If the best
    # run is short we've locked onto a caption; better to keep everything than
    # to silently ship a crop of somebody's username.
    if bottom - top < img.width * 0.8:
        return 0, h - 1

    return top, bottom


def crop_screenshot(img, force_top=None, force_bottom=None):
    top, bottom = find_photo_band(img)
    if force_top is not None:
        top = force_top
    if force_bottom is not None:
        bottom = force_bottom

    # Trim a couple of pixels so no chrome hairline survives, and shave the
    # right edge where iOS parks its scroll indicator.
    pad = 3
    top = min(img.height - 2, top + pad)
    bottom = max(top + 1, bottom - pad)
    right = img.width - 14
    return img.crop((0, top, right, bottom)), (top, bottom)


# ----------------------------------------------------------------------
# Removing the carousel badge
# ----------------------------------------------------------------------
def badge_box(img):
    """Find the bounds of Instagram's '1/2' carousel pill in the top-right.

    Only called when you've told us a badge is there (--erase-badge), because
    auto-detection is a bad trade: a corner full of shelves and vases looks a
    lot like a pill to a heuristic, and a wrong guess quietly smears a photo
    you can't easily check. Knowing one exists, locating it is easy — it's the
    stuff in the corner that doesn't match the surrounding background.
    """
    w, h = img.size
    x0, x1 = int(w * 0.74), w
    y0, y1 = 0, int(h * 0.09)
    if x1 - x0 < 10 or y1 - y0 < 10:
        return None

    grey = img.convert("L")

    # Background level, sampled from a band just below the pill.
    ref = grey.crop((x0, y1, x1, min(h, y1 + (y1 - y0) * 2)))
    base = ImageStat.Stat(ref).mean[0]

    px = grey.crop((x0, y0, x1, y1)).load()
    pw, ph = x1 - x0, y1 - y0

    bx0, by0, bx1, by1 = pw, ph, 0, 0
    found = False
    for yy in range(ph):
        for xx in range(pw):
            if abs(px[xx, yy] - base) > 24:
                found = True
                bx0, by0 = min(bx0, xx), min(by0, yy)
                bx1, by1 = max(bx1, xx), max(by1, yy)

    if not found:
        return None

    pad = 6
    return (max(0, x0 + bx0 - pad), max(0, y0 + by0 - pad),
            min(w, x0 + bx1 + pad), min(h, y0 + by1 + pad))


def erase_badge(img, box):
    """Paint the badge out using the texture immediately to its left."""
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    img = img.convert("RGB")

    # Borrow an equally sized slab from the left, mirrored so it tiles cleanly.
    donor_x = max(0, x0 - bw)
    donor = img.crop((donor_x, y0, donor_x + bw, y1)).transpose(Image.FLIP_LEFT_RIGHT)
    img.paste(donor, (x0, y0))

    # Feather the join so the patch doesn't read as a rectangle.
    pad = 18
    rx0, ry0 = max(0, x0 - pad), max(0, y0 - pad)
    rx1, ry1 = min(img.width, x1 + pad), min(img.height, y1 + pad)
    region = img.crop((rx0, ry0, rx1, ry1))
    blurred = region.filter(ImageFilter.GaussianBlur(6))

    mask = Image.new("L", region.size, 0)
    ImageDraw.Draw(mask).rectangle(
        [x0 - rx0 - 6, y0 - ry0 - 6, x1 - rx0 + 6, y1 - ry0 + 6], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(9))

    region.paste(blurred, (0, 0), mask)
    img.paste(region, (rx0, ry0))
    return img


# ----------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------
def square(img, size, focus_y=0.14, focus_x=0.5, zoom=1.0):
    """Crop to a square window and scale it to `size`.

    zoom    1.0 takes the largest square that fits; 0.7 takes a tighter one.
    focus_y where that window sits vertically, 0 = flush with the top. The
            default is deliberately small: in a posed portrait the head sits
            near the top edge, and a clipped forehead is the one mistake you
            always notice.
    focus_x same, horizontally. Centred by default.
    """
    w, h = img.size
    side = max(16, min(int(min(w, h) * zoom), min(w, h)))

    x = max(0, min(w - side, int((w - side) * focus_x)))
    y = max(0, min(h - side, int((h - side) * focus_y)))

    return img.crop((x, y, x + side, y + side)).resize((size, size), Image.LANCZOS)


def save(img, path, size, focus_y=0.14, focus_x=0.5, zoom=1.0):
    out = square(img, size, focus_y, focus_x, zoom)
    if out.mode != "RGB":
        out = out.convert("RGB")
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    kb = path.stat().st_size / 1024
    print(f"    -> {path.relative_to(ROOT)}  ({size}x{size}, {kb:.0f} KB)")


# ----------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inbox", default=str(ROOT / "tools" / "inbox"))
    ap.add_argument("--out", default=str(ROOT / "assets"))
    ap.add_argument("--main")
    ap.add_argument("--no-crop", action="append", default=[])
    ap.add_argument("--rotate", action="append", default=[], metavar="NAME=DEG",
                    help="rotate a file before cropping, e.g. --rotate bed.jpg=90")
    ap.add_argument("--focus", action="append", default=[], metavar="NAME=0.2",
                    help="where the square crop sits vertically, 0 = keep the very top")
    ap.add_argument("--focus-x", action="append", default=[], metavar="NAME=0.5",
                    help="where the square crop sits horizontally, 0.5 = centred")
    ap.add_argument("--zoom", action="append", default=[], metavar="NAME=0.8",
                    help="tighten the crop, 1.0 = widest square that fits")
    ap.add_argument("--erase-badge", action="append", default=[], metavar="NAME",
                    help="paint out Instagram's '1/2' carousel pill on this file")
    ap.add_argument("--only")
    ap.add_argument("--top", type=int)
    ap.add_argument("--bottom", type=int)
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    inbox = Path(args.inbox)
    outdir = Path(args.out)

    def pairs(items, cast):
        out = {}
        for item in items:
            if "=" not in item:
                sys.exit(f"Expected NAME=VALUE, got {item!r}")
            k, v = item.rsplit("=", 1)
            out[k] = cast(v)
        return out

    rotations = pairs(args.rotate, int)
    focuses = pairs(args.focus, float)
    focuses_x = pairs(args.focus_x, float)
    zooms = pairs(args.zoom, float)

    if not inbox.exists():
        inbox.mkdir(parents=True, exist_ok=True)
        sys.exit(f"Created {inbox}\nDrop your photos in there and run this again.")

    exts = {".jpg", ".jpeg", ".png", ".heic", ".webp", ".bmp"}
    files = sorted(p for p in inbox.iterdir()
                   if p.is_file() and p.suffix.lower() in exts)

    if args.only:
        files = [p for p in files if p.name == args.only]
    if not files:
        sys.exit(f"No images found in {inbox}")

    # The main portrait: --main, else the first file alphabetically.
    main_name = args.main or files[0].name
    if main_name not in {p.name for p in files}:
        sys.exit(f"--main {main_name!r} isn't in {inbox}")

    print(f"Reading {len(files)} image(s) from {inbox}\n")

    memory_n = 0
    for path in files:
        try:
            img = Image.open(path)
        except Exception as e:
            print(f"  {path.name}: can't open ({e}) — skipping")
            continue

        img = ImageOps.exif_transpose(img)          # honour phone rotation

        if path.name in rotations:
            deg = rotations[path.name]
            img = img.rotate(deg, expand=True)      # positive = anticlockwise
            print(f"  {path.name}  rotated {deg}°")

        w, h = img.size
        is_shot = (h / w) >= SCREENSHOT_MIN_RATIO and path.name not in args.no_crop

        print(f"  {path.name}  {w}x{h}")

        if is_shot:
            cropped, (top, bottom) = crop_screenshot(
                img,
                args.top if args.only else None,
                args.bottom if args.only else None,
            )
            print(f"    screenshot: kept rows {top}-{bottom} "
                  f"({cropped.width}x{cropped.height})")

            if path.name in args.erase_badge:
                box = badge_box(cropped)
                if box:
                    cropped = erase_badge(cropped, box)
                    print(f"    painted out the carousel badge at {box}")
                else:
                    print("    no badge found to erase")
            if args.debug:
                dbg = img.convert("RGB").copy()
                d = ImageDraw.Draw(dbg)
                d.rectangle([2, top, w - 3, bottom], outline=(0, 255, 90), width=8)
                dbg.save(outdir.parent / f"{path.stem}_debug.png")
            img = cropped
        else:
            print("    treated as a normal photo (no crop)")

        fy = focuses.get(path.name, 0.14)
        fx = focuses_x.get(path.name, 0.5)
        zm = zooms.get(path.name, 1.0)

        if path.name == main_name:
            save(img, outdir / "photo.jpg", PORTRAIT_SIZE, fy, fx, zm)
        else:
            memory_n += 1
            save(img, outdir / f"memory-{memory_n}.jpg", MEMORY_SIZE, fy, fx, zm)

    print("\nDone. Refresh the card to see them.")
    if memory_n:
        print(f"Gallery slots filled: memory-1 .. memory-{memory_n}")


if __name__ == "__main__":
    main()
