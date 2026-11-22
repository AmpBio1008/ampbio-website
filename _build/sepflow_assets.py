# -*- coding: utf-8 -*-
"""
Assemble _build/sepflow-products.json and the Sepflow pictures from the
transcription of Sepflow's product images.

  python _build/sepflow_assets.py <work-dir>     (run from the site/ directory)

<work-dir> holds raw/<route>/*.png (Sepflow's English product images, as
downloaded from their site) and out_norm/<route>.json (the text read off those
images: copy, specifications, and a verified crop box for each usable picture).
That folder is working material and is not kept in the repo; the catalogue and
the pictures this writes are.

Writes, per product:
  assets/sepflow-<slug>.webp          3:2 card / tile picture (660x440)
  assets/sepflow-<slug>-main.webp     4:3 product-page picture (up to 1200x900)
  assets/sepflow-<slug>-g<N>.webp     4:3 gallery pictures (up to 960x720)
"""
import io, json, os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
ASSETS = os.path.join(SITE, "assets")

SYSTEMS = "Purification Systems"
SOFTWARE = "Software & Accessories"
PUMPS = "Pumps"
VALVES = "Valves"
CATEGORIES = [SYSTEMS, SOFTWARE, PUMPS, VALVES]
SHORT = {}

# route on sepflow.com.cn -> our slug, category, catalogue card. In Sepflow's
# own order within each category.
PRODUCTS = [
    ("AIPure-HC", "aipure-hc", SYSTEMS, "product2.png"),
    ("AIPure-MC", "aipure-mc", SYSTEMS, "product18.png"),
    ("AIpilot-300", "aipilot-300", SYSTEMS, "product3.png"),
    ("AIpilot-600", "aipilot-600", SYSTEMS, "product4.png"),
    ("Lab-TFF", "lab-tff", SYSTEMS, "product5.png"),
    ("ChromX", "chromx", SOFTWARE, "product7.png"),
    (None, "fraction-collector", SOFTWARE, "product6.png"),
    ("25mLPistonPump", "piston-pump-25-ml", PUMPS, "product9.png"),
    ("100mLPistonPump", "piston-pump-100-ml", PUMPS, "product10.png"),
    ("150mLPistonPump", "piston-pump-150-ml", PUMPS, "product16.png"),
    ("300mLPistonPump", "piston-pump-300-ml", PUMPS, "product17.png"),
    ("600mLPistonPump", "piston-pump-600-ml", PUMPS, "product8.png"),
    ("5ColumnPositionValve", "column-valve", VALVES, "product11.png"),
    ("InletValve", "inlet-valve", VALVES, "product12.png"),
    ("InjectValve", "inject-valve", VALVES, "product13.png"),
    ("OutletValve", "outlet-valve", VALVES, "product14.png"),
    ("pHValve", "ph-valve", VALVES, "product15.png"),
]

FEATURED = ["aipure-hc", "aipure-mc", "aipilot-300", "aipilot-600", "lab-tff",
            "fraction-collector", "chromx", "piston-pump-600-ml"]

# Sepflow publishes no detail page for this one - only a catalogue picture -
# so its copy is ours and says no more than that picture shows.
COLLECTOR = {
    "name": "Fraction Collector",
    "subtitle": "Automated fraction collector",
    "summary": ("Sepflow's automated fraction collector (listed in their range as the "
                "Component Collector) dispenses column eluate into a tube rack under "
                "program control. Ask us for the full specification and the systems it "
                "pairs with."),
    "features": [], "applications": [], "options": [], "contents": [],
    # From the AIpure-MC sheet, which lists an open collector as standard.
    "specs": [{"group": "Technical specifications", "rows": [
        ["Tube formats (as supplied with the AIpure-MC)",
         "180 × 1.5 mL, 120 × 15 mL or 42 × 50 mL centrifuge tubes"]]}],
}

# Products shown from their catalogue card (no detail images): crop to the
# instrument, which sits small in an empty studio scene on the card.
CARD_CROP = {"fraction-collector": [55, 232, 395, 487]}

# Copy for the range page, homepage band and Products-page card.
PAGE = {
    "lead": ("Ampbio is the exclusive distributor in India for Sepflow, China: automated "
             "chromatography and protein purification systems from laboratory to pilot "
             "scale, tangential flow filtration, ChromX workstation software, and the "
             "piston pumps and valve modules the systems are built from."),
    "blurb": ("Ampbio is the exclusive distributor in India for Sepflow, China: %d products "
              "spanning automated chromatography systems, tangential flow filtration, ChromX "
              "workstation software, piston pumps and valve modules."),
    "cta": "Sepflow – Chromatography and Protein Purification Systems",
    # (route, raw image, crop) for the two wide pictures
    # Both from the AIpure-HC render against concrete, cropped wide with the
    # instrument right of centre so the copy on the left never sits over it.
    "hero": ("AIPure-HC", "AIpure_HC_en2.png", [0, 380, 1920, 1560],
             "Sepflow AIpure-HC chromatography system", "center 42%"),
    "banner": ("AIPure-HC", "AIpure_HC_en2.png", [0, 560, 1700, 1400],
               "Sepflow AIpure-HC chromatography system", "center 45%"),
}


def crop_save(im, box, ratio, size, path):
    """Crop `box` (raw-image pixels), trimmed to `ratio` about its centre, and
    save at most `size` wide. Never upscales."""
    if box:
        im = im.crop(tuple(int(v) for v in box))
    w, h = im.size
    if w / h > ratio:
        nw = int(round(h * ratio))
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(round(w / ratio))
        im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    if im.width > size:
        im = im.resize((size, int(round(size / ratio))), Image.LANCZOS)
    im.convert("RGB").save(path, "WEBP", quality=86, method=6)
    return im.size


def main(work):
    products, report = [], []
    for route, slug, cat, card in PRODUCTS:
        if route:
            t = json.load(io.open(os.path.join(work, "out_norm", route + ".json"), encoding="utf-8"))
        else:
            t = dict(COLLECTOR, images=[])
        p = {"slug": slug, "name": t["name"], "subtitle": t.get("subtitle", ""),
             "category": cat, "summary": t["summary"],
             "features": t.get("features", []), "applications": t.get("applications", []),
             "contents": t.get("contents", []), "options": t.get("options", []),
             "specs": t.get("specs", []), "docs": []}

        imgs = t.get("images", [])
        main_img = next((i for i in imgs if i.get("use") == "main" and i.get("crop")), None)
        if main_img:
            src = Image.open(os.path.join(work, "raw", route, main_img["raw"]))
            box = main_img["crop"]
            alt = main_img.get("alt") or p["name"]
        else:  # fall back to Sepflow's catalogue card
            src = Image.open(os.path.join(work, "raw", "_cards", card))
            box, alt = CARD_CROP.get(slug), p["name"]
        crop_save(src, box, 4 / 3.0, 1200, os.path.join(ASSETS, "sepflow-%s-main.webp" % slug))
        crop_save(src, box, 3 / 2.0, 660, os.path.join(ASSETS, "sepflow-%s.webp" % slug))
        p["image"] = "assets/sepflow-%s.webp" % slug
        p["hero_image"] = "assets/sepflow-%s-main.webp" % slug
        p["image_alt"] = alt

        p["gallery"] = []
        for n, g in enumerate([i for i in imgs if i.get("use") == "gallery" and i.get("crop")][:4], 1):
            src = Image.open(os.path.join(work, "raw", route, g["raw"]))
            name = "sepflow-%s-g%d.webp" % (slug, n)
            crop_save(src, g["crop"], 4 / 3.0, 960, os.path.join(ASSETS, name))
            p["gallery"].append({"src": "assets/" + name, "alt": g.get("alt") or p["name"]})

        products.append(p)
        report.append("%-22s %-11s main:%s  gallery:%d  spec rows:%d" % (
            slug, cat.split()[0], "detail" if main_img else "card", len(p["gallery"]),
            sum(len(g["rows"]) for g in p["specs"])))

    wide = {}
    for key, size in (("hero", 1920), ("banner", 1400)):
        route, raw, box, alt, pos = PAGE[key]
        im = Image.open(os.path.join(work, "raw", route, raw)).crop(tuple(box))
        if im.width > size:
            im = im.resize((size, round(im.height * size / im.width)), Image.LANCZOS)
        name = "sepflow-%s.webp" % key
        im.convert("RGB").save(os.path.join(ASSETS, name), "WEBP", quality=84, method=6)
        wide[key] = {"image": "assets/" + name, "alt": alt, "position": pos}

    path = os.path.join(HERE, "sepflow-products.json")
    data = {
        "source": "sepflow.com.cn product images, read Nov 2026",
        "categories": CATEGORIES, "short": SHORT, "featured": FEATURED,
        "lead": PAGE["lead"], "blurb": PAGE["blurb"] % len(products), "cta": PAGE["cta"],
        "hero": wide["hero"], "banner": wide["banner"],
        "products": products,
    }
    io.open(path, "w", encoding="utf-8").write(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    print("\n".join(report))
    print("wrote %s (%d products)" % (os.path.relpath(path, SITE), len(products)))


if __name__ == "__main__":
    main(sys.argv[1])
