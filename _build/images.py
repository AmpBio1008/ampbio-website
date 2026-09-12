# -*- coding: utf-8 -*-
"""
Download the Virongy product imagery and write right-sized WebP into site/assets/.

Matches the pipeline already used for the rest of amps.bio: WebP, sized at ~2x
the largest place the image is rendered, never upscaled, lowercase-hyphen names.

Run:  python images.py <catalogue.json> <site/assets dir>
"""
import io, json, os, re, sys, time
import urllib.request
from PIL import Image

UA = "Mozilla/5.0 (compatible; amps.bio catalogue build)"
LOGO = "https://virongy.com/wp-content/uploads/2022/12/cropped-cropped-Updated-Logo-Bigger-2.png"

# Largest rendered size on the site: product card image well is 260x150 CSS px,
# marquee tile 220x150. 2x for retina, with a little headroom.
MAX_W, MAX_H = 560, 400
QUALITY = 82
LOGO_W = 440          # rendered at up to 200px wide in the hero lockup


def get(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception:
            if i == retries - 1:
                raise
            time.sleep(2)


def convert(raw, dest, max_w, max_h, on_white=True):
    im = Image.open(io.BytesIO(raw))
    src_w, src_h = im.size
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        if on_white:
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[-1])
            im = bg
    else:
        im = im.convert("RGB")
    # never upscale
    scale = min(max_w / im.width, max_h / im.height, 1.0)
    if scale < 1.0:
        im = im.resize((max(1, round(im.width * scale)),
                        max(1, round(im.height * scale))), Image.LANCZOS)
    im.save(dest, "WEBP", quality=QUALITY, method=6)
    return src_w, src_h, im.width, im.height, os.path.getsize(dest)


def main(catalogue, assets):
    data = json.load(open(catalogue, encoding="utf-8"))
    # one entry per distinct local file
    jobs = {}
    for p in data["products"]:
        jobs.setdefault(os.path.basename(p["image"]), p["image_source"])

    total = 0
    print("%-52s %11s -> %9s %8s" % ("file", "source px", "out px", "size"))
    for name, url in sorted(jobs.items()):
        dest = os.path.join(assets, name)
        try:
            sw, sh, ow, oh, size = convert(get(url), dest, MAX_W, MAX_H)
        except Exception as e:
            print("  FAILED %s  <- %s  (%s)" % (name, url, e))
            continue
        total += size
        print("%-52s %5dx%-5d -> %4dx%-4d %7.1fK" %
              (name[:52], sw, sh, ow, oh, size / 1024.0))

    # logo: keep transparency, it sits on a dark hero
    dest = os.path.join(assets, "virongy-logo.webp")
    raw = get(LOGO)
    im = Image.open(io.BytesIO(raw)).convert("RGBA")
    sw, sh = im.size
    if im.width > LOGO_W:
        h = round(im.height * LOGO_W / im.width)
        im = im.resize((LOGO_W, h), Image.LANCZOS)
    im.save(dest, "WEBP", quality=90, method=6)
    size = os.path.getsize(dest)
    total += size
    print("%-52s %5dx%-5d -> %4dx%-4d %7.1fK" %
          ("virongy-logo.webp", sw, sh, im.width, im.height, size / 1024.0))

    print("\n%d files, %.0f KB total" % (len(jobs) + 1, total / 1024.0))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
