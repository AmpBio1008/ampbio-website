# -*- coding: utf-8 -*-
"""
Generate the Jena Bioscience range page, its product pages and the Jena row
of the homepage hero strip, from _build/jena-products.json.

  python _build/build_jena.py               (run from the site/ directory)

Writes:
  jena.html                                     range page
  jena/<slug>.html                              one page per product
  index.html   between JENA-HERO-STRIP markers  second row of the hero strip

Ampbio is an AUTHORISED (not exclusive) distributor in India for Jena
Bioscience; every line that says so comes from DISTRIBUTOR_LINE. The range
starts with the 8 products Jena features on its own homepage; add products to
the catalogue and re-run to grow it. Same page template as Virongy and Sepflow
(pages.py). Nothing links to jenabioscience.com and no prices are shown.
Product text is from Jena's public product pages and data sheets
(_build/jena_assets.py); the structure drawings from _build/fetch_jena.py.
"""
import io, json, os, sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pages
from build_virongy import (HERE, SITE, AMBER, NAVY, CARD, HAIRLINE, F_HEAD, F_MONO, esc,
                           reroot, read, write, replace_block, _chrome, check)
from build_sepflow import spec_table

CATALOGUE = os.path.join(HERE, "jena-products.json")
DISTRIBUTOR_LINE = "Authorised Distributor in India"

PARTNER = {
    "name": "Jena Bioscience",
    "short": "Jena Bioscience",
    "dir": "jena",
    "index": "jena.html",
    "media_note": "Supplied in India by Ampbio",
    "manufacturer_url": None,
    "quote_lead": "Tell us the product, catalogue number and pack size you need. We will "
                  "confirm availability, lead time and pricing for delivery in India.",
}

# Keeps this row moving at the same speed as Virongy's (11 tiles, 72s).
SECONDS_PER_TILE = 72 / 11.0


def badge(height, margin, rel=""):
    """Same badge as Virongy's and Sepflow's. Jena's logo is white artwork for a
    dark header; this is the same vector in dark navy, for the light plate."""
    pv, ph = int(round(height * 0.38)), int(round(height * 0.58))
    return ('<span class="amp-vlogo" style="display:inline-block;'
            'background:linear-gradient(158deg,#f7fafd 0%%,#dfe7f1 100%%);'
            'border-radius:14px;padding:%dpx %dpx;margin:%s;'
            'box-shadow:0 0 0 1px rgba(253,157,5,0.42),0 16px 40px rgba(0,0,0,0.45)">'
            '<img src="%sassets/jena-logo.svg" alt="Jena Bioscience" '
            'style="height:%dpx;width:auto;display:block"></span>'
            % (pv, ph, margin, rel, height))


def detail_html(p, rel):
    parts = []
    if p.get("applications"):
        parts.append(pages.detail_block("Applications", pages.bullet_list(p["applications"])))
    if p.get("ligands"):
        parts.append(pages.detail_block("Specific ligands", pages.bullet_list(p["ligands"])))
    if p.get("contents"):
        parts.append(pages.detail_block("Contents", pages.bullet_list(p["contents"])))
    for opt in p.get("options", []):
        parts.append(pages.detail_block(opt["label"], pages.option_pills(opt["values"])))
    for g in p.get("specs", []):
        parts.append(pages.detail_block(g["group"], spec_table(g)))
    parts.append(pages.doc_buttons(p.get("docs", []), rel,
                                   lambda path: os.path.exists(os.path.join(SITE, path))))
    return "".join(parts)


def index_body(data, cats, counts):
    hero = data["hero"]
    body = (
        '\n  <!-- ================= HERO ================= -->\n'
        '  <section class="amp-hero" style="position:relative;overflow:hidden;min-height:560px;'
        'padding-top:76px;display:flex;align-items:center">\n'
        '    <img src="%(img)s" alt="%(alt)s" style="position:absolute;inset:0;width:100%%;'
        'height:100%%;object-fit:cover;object-position:%(pos)s;display:block;z-index:0">\n'
        '    <div style="position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,'
        'rgba(8,17,29,0.97) 0%%,rgba(8,17,29,0.92) 34%%,rgba(8,17,29,0.5) 68%%,'
        'rgba(8,17,29,0.18) 100%%)"></div>\n'
        '    <div style="position:absolute;inset:0;z-index:1;background:linear-gradient(0deg,'
        'rgba(8,17,29,0.6) 0%%,rgba(8,17,29,0) 42%%)"></div>\n'
        '    <div style="position:relative;z-index:2;max-width:1240px;margin:0 auto;'
        'padding:52px 32px;width:100%%">\n'
        '      <div style="max-width:720px">\n'
        '        <div style="font-family:%(fm)s;font-size:0.78rem;letter-spacing:0.24em;'
        'color:%(amber)s;text-transform:uppercase;margin-bottom:20px">%(dline)s</div>\n'
        '        %(logo)s\n'
        '        <h1 class="amp-h1" style="font-family:%(fh)s;font-weight:800;'
        'font-size:clamp(2rem,3.9vw,3.3rem);line-height:1.05;letter-spacing:-0.01em;'
        'text-transform:uppercase;margin:0 0 20px">'
        '<span style="color:#fff">Jena Bioscience </span>'
        '<span style="color:%(amber)s">in India.</span></h1>\n'
        '        <p style="color:#c4cede;font-size:1.1rem;line-height:1.62;margin:0 0 28px;'
        'max-width:620px">%(lead)s</p>\n'
        '        %(nav)s\n'
        '      </div>\n'
        '    </div>\n'
        '  </section>\n' % {
            "img": esc(hero["image"]), "alt": esc(hero["alt"]), "pos": hero["position"],
            "fm": F_MONO, "fh": F_HEAD, "amber": AMBER, "dline": DISTRIBUTOR_LINE,
            "logo": badge(44, "0 0 26px"), "lead": esc(data["lead"]),
            "nav": pages.category_nav(cats, counts)})
    body += pages.catbar(cats, counts, {})
    products = data["products"]
    body += "".join(
        pages.index_section(c, [p for p in products if p["category"] == c], i % 2 == 1,
                            PARTNER)
        for i, c in enumerate(cats))
    body += pages.enquiry_band("", PARTNER)
    body += pages.back_to_top()
    return body


def build_index(data):
    header, footer = _chrome()
    products = data["products"]
    counts = {c: sum(1 for p in products if p["category"] == c) for c in data["categories"]}
    cats = [c for c in data["categories"] if counts.get(c)]
    title = "Jena Bioscience — Authorised Distributor for India | Ampbio"
    desc = ("Authorised distributor in India for Jena Bioscience, Germany: nucleotides, "
            "click-chemistry nucleosides, dNTPs and Quantifoil cryo-EM grids.")
    return pages.shell(title, desc, "https://amps.bio/jena.html",
                       index_body(data, cats, counts), "", header, footer)


def build_product(p, data):
    header, footer = _chrome()
    rel = "../"
    header, footer = reroot(header, rel), reroot(footer, rel)
    siblings = [q for q in data["products"] if q["category"] == p["category"]]
    i = siblings.index(p)
    prev = siblings[i - 1] if i else None
    nxt = siblings[i + 1] if i + 1 < len(siblings) else None
    others = [q for q in siblings if q is not p][:4]
    if not others:
        others = [q for q in data["products"] if q is not p][:4]

    url = "https://amps.bio/jena/%s.html" % p["slug"]
    page_p = dict(p, image=p["hero_image"])
    body = pages.product_body(
        page_p, detail_html(p, rel), pages.breadcrumb(p, rel, PARTNER),
        pages.prev_next(prev, nxt), rel,
        "%sconnect.html?product=%s" % (rel, quote("%s (%s)" % (p["name"], p["sku"]))), PARTNER)
    body += pages.related(others, p["category"], PARTNER)
    body += pages.enquiry_band(rel, PARTNER)
    return pages.shell(
        "%s | Jena Bioscience — Ampbio India" % p["name"],
        pages.meta_description(page_p, partner=PARTNER), url, body, rel, header, footer,
        extra_head=pages.product_jsonld(page_p, url, PARTNER))


def tile(p):
    # Structural formulas are line art on white, so every Jena tile is a white
    # plate with the drawing contained rather than cropped to fill.
    return (
        '\n          <a class="amp-mq-tile amp-mq-plate" href="jena/%s.html" title="%s" '
        'style="flex:0 0 auto;width:330px;display:flex;flex-direction:column;gap:9px;'
        'text-decoration:none"><div style="position:relative;height:222px;border-radius:12px;'
        'overflow:hidden;background:#fff;border:1px solid %s"><img src="%s" '
        'alt="%s" style="position:absolute;inset:0;width:100%%;height:100%%;object-fit:contain;'
        'padding:7%% 9%%;box-sizing:border-box;display:block"></div>'
        '<div style="font-family:%s;font-weight:700;font-size:1rem;line-height:1.2;'
        'color:#dbe3ee">%s</div></a>'
        % (esc(p["slug"]), esc(p["name"]), HAIRLINE, esc(p["tile_image"]), esc(p["name"]),
           F_HEAD, esc(p["name"])))


def build_hero_strip(data):
    by = {p["slug"]: p for p in data["products"]}
    feats = [by[s] for s in data["featured"] if s in by]
    track = "".join(tile(p) for p in feats)
    return (
        '\n      <div class="amp-marquee" style="position:relative;overflow:hidden">\n'
        '        <div class="amp-marquee-track" style="display:flex;gap:18px;'
        'width:max-content;padding:0 10px;animation-duration:%ds">%s%s\n'
        '        </div>\n'
        '      </div>\n    '
        % (round(SECONDS_PER_TILE * len(feats)), track, track))


def check_jena(path):
    s = read(path)
    for bad in ("jenabioscience.com", "€", "Exclusive Distributor", "exclusive distributor",
                "Add to cart"):
        if bad in s and not (bad.lower().startswith("exclusive") and path == "index.html"):
            raise SystemExit("%s FAILED: %r must not appear" % (path, bad))
    check(path)


def main():
    data = json.load(io.open(CATALOGUE, encoding="utf-8"))
    products = data["products"]
    os.makedirs(os.path.join(SITE, "jena"), exist_ok=True)
    write("jena.html", build_index(data))
    for p in products:
        write("jena/%s.html" % p["slug"], build_product(p, data))
    write("index.html", replace_block(read("index.html"), "JENA-HERO-STRIP",
                                      build_hero_strip(data)))
    for page in ["jena.html", "index.html"] + ["jena/%s.html" % p["slug"] for p in products]:
        check_jena(page)
    print("jena.html         range page, %d products" % len(products))
    print("jena/*.html       %d product pages" % len(products))
    print("index.html        Jena hero row, %d tiles -> product pages" % len(data["featured"]))


if __name__ == "__main__":
    main()
