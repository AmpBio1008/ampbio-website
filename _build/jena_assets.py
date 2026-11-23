# -*- coding: utf-8 -*-
"""
Assemble _build/jena-products.json, the product pictures and the documents
for the Jena Bioscience pages.

  python _build/jena_assets.py <products.json> <pdf-dir>   (run from site/)

<products.json> is the product text taken from Jena's public product pages
(prices dropped at source) and finished by hand; <pdf-dir> holds Jena's data
sheets and safety data sheets as downloaded. Both are working material and are
not kept in the repo; what this writes is.

Writes:
  assets/jena-<slug>-main.webp      4:3 product-page picture on a white plate
  assets/jena-<slug>-card.webp      3:2 card picture on a white plate
  assets/docs/jena/<file>.pdf       data sheet + SDS per product
  _build/jena-products.json
The structure drawings themselves (assets/jena-<slug>.webp) come from
_build/fetch_jena.py.
"""
import io, json, os, shutil, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
ASSETS = os.path.join(SITE, "assets")
DOCS = os.path.join(ASSETS, "docs", "jena")

NUC = "Nucleotides & Nucleosides"
CRYO = "Crystallography & Cryo-EM"


def plate(src, w, h, path, fill=0.78):
    """The drawing centred on white, at most `fill` of the plate either way."""
    im = Image.open(src).convert("RGB")
    s = min(w * fill / im.width, h * fill / im.height)
    s = min(s, 2.2)  # the Quantifoil micrograph is small; cap the enlargement
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    out = Image.new("RGB", (w, h), "white")
    out.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    out.save(path, "WEBP", quality=88, method=6)


def main(products_path, pdf_dir):
    products = json.load(io.open(products_path, encoding="utf-8"))
    os.makedirs(DOCS, exist_ok=True)
    pdfs = sorted(os.listdir(pdf_dir))
    for p in products:
        slug = p["slug"]
        src = os.path.join(ASSETS, "jena-%s.webp" % slug)
        plate(src, 1200, 900, os.path.join(ASSETS, "jena-%s-main.webp" % slug))
        plate(src, 660, 440, os.path.join(ASSETS, "jena-%s-card.webp" % slug))
        p["image"] = "assets/jena-%s-card.webp" % slug
        p["hero_image"] = "assets/jena-%s-main.webp" % slug
        p["tile_image"] = "assets/jena-%s.webp" % slug

        # Jena files documents under the catalogue number without the pack
        # suffix (NU-406.0003.pdf, NU-406_MSDS.0004.pdf).
        base = p["sku"]  # already the base number in jena-featured.json
        docs = []
        for f in pdfs:
            if f.split(".")[0] == base:
                docs.append({"label": "Data sheet", "path": "assets/docs/jena/" + f})
            elif f.split(".")[0] == base + "_MSDS":
                docs.append({"label": "Safety data sheet", "path": "assets/docs/jena/" + f})
        for d in docs:
            shutil.copyfile(os.path.join(pdf_dir, os.path.basename(d["path"])),
                            os.path.join(SITE, d["path"]))
        p["docs"] = sorted(docs, key=lambda d: d["label"])
        p["doc_count"] = len(docs)
        print("%-26s %-26s docs:%d" % (slug, p["category"], len(docs)))

    data = {
        "source": "jenabioscience.com product pages and data sheets, read Nov 2026",
        "categories": [NUC, CRYO],
        "featured": [p["slug"] for p in products],
        "lead": ("Ampbio is an authorised distributor in India for Jena Bioscience, Germany. "
                 "This range opens with the products Jena features: non-hydrolysable and "
                 "click-chemistry nucleotides, a dNTP bundle and Quantifoil® cryo-EM grids."),
        "hero": {"image": "assets/plat-chemicals.webp",
                 "alt": "Molecular structure", "position": "70% center"},
        "products": products,
    }
    path = os.path.join(HERE, "jena-products.json")
    io.open(path, "w", encoding="utf-8").write(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    print("wrote %s (%d products)" % (os.path.relpath(path, SITE), len(products)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
