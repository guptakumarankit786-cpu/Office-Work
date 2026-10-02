"""Amazon main image (Image 1) for CURRYiT Chettinad Chicken Curry.

Places the ORIGINAL pack photo, untouched, on a pure-white Amazon canvas.
The pack pixels are only scaled (uniformly, no distortion). Nothing on the
pack is redrawn, recoloured, retouched or regenerated. Only the environment
around it changes: background -> pure white (255,255,255), a soft contact
shadow underneath, centred composition.

Usage:  python3 make_main_image.py <original_pack_photo> [out.jpg]
Best input: the brand's own high-resolution packshot (>= 1700 px tall).
"""
import sys
from PIL import Image, ImageDraw, ImageFilter

CANVAS = 2000          # Amazon: >=1000 px for zoom; 2000 x 2000 recommended
FILL = 0.85            # product occupies ~85% of the longest side (Amazon guidance)
WHITE_T = 238          # pixels lighter than this, connected to the edge = background

def product_mask(img):
    """Mask of the pack: everything NOT edge-connected near-white background."""
    g = img.convert("L")
    bg = g.point(lambda v: 255 if v >= WHITE_T else 0)
    w, h = bg.size
    seed = Image.new("L", (w + 2, h + 2), 255); seed.paste(bg, (1, 1))
    ImageDraw.floodfill(seed, (0, 0), 128)          # border-connected white -> 128
    m = seed.crop((1, 1, w + 1, h + 1)).point(lambda v: 0 if v == 128 else 255)
    return m.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.8))

def main(src, out):
    img = Image.open(src).convert("RGB")
    mask = product_mask(img)
    box = mask.getbbox()
    if not box:
        sys.exit("Could not find the product against the background.")
    pack, pmask = img.crop(box), mask.crop(box)
    pw, ph = pack.size
    s = (CANVAS * FILL) / max(pw, ph)
    if s > 1:
        print(f"WARNING: source is {pw}x{ph}px; upscaling x{s:.1f} will look soft. "
              "Use the original high-resolution packshot for the final listing image.")
    nw, nh = round(pw * s), round(ph * s)
    pack = pack.resize((nw, nh), Image.LANCZOS)
    pmask = pmask.resize((nw, nh), Image.LANCZOS)

    canvas = Image.new("RGB", (CANVAS, CANVAS), (255, 255, 255))
    x, y = (CANVAS - nw) // 2, (CANVAS - nh) // 2 - int(CANVAS * 0.01)
    # very subtle contact shadow (neutral grey, blurred ellipse just under the base)
    sh = Image.new("L", (CANVAS, CANVAS), 0)
    d = ImageDraw.Draw(sh)
    d.ellipse((x + nw * 0.08, y + nh - nh * 0.015, x + nw * 0.92, y + nh + nh * 0.035), fill=70)
    sh = sh.filter(ImageFilter.GaussianBlur(CANVAS * 0.012))
    canvas.paste(Image.new("RGB", canvas.size, (120, 120, 120)), (0, 0), sh)
    canvas.paste(pack, (x, y), pmask)               # original pixels, uniform scale only
    canvas.save(out, "JPEG", quality=95, subsampling=0, optimize=True)
    # compliance check: corners must be pure white
    px = [canvas.getpixel(p) for p in [(0, 0), (CANVAS - 1, 0), (0, CANVAS - 1), (CANVAS - 1, CANVAS - 1)]]
    print(f"Saved {out}  {CANVAS}x{CANVAS}  product {nw}x{nh}  corners={px}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "CURRYiT_Chettinad_Image1_main.jpg")
