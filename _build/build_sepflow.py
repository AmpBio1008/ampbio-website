# -*- coding: utf-8 -*-
"""
Generate the Sepflow range page, its product pages and the Sepflow blocks on
the existing pages, from _build/sepflow-products.json.

  python _build/build_sepflow.py            (run from the site/ directory)

Writes:
  sepflow.html                                    range page
  sepflow/<slug>.html                             one page per product
  index.html     between SEPFLOW-HERO-STRIP markers   third row of the hero strip
  products.html  between SEPFLOW-BANNER markers       distributor card
  sitemap.xml                                     rewritten with the Sepflow pages

Same page template as the Virongy range (pages.py), with the Sepflow partner
settings. Sepflow sells instruments rather than reagents, so a product page
also carries a specification table and a picture gallery. The copy and the
specifications were read off Sepflow's product images (their site has no text
to copy); _build/sepflow_assets.py made the pictures. Nothing links to
sepflow.com.cn and no prices are shown.
"""
import io, json, os, re, sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pages
from build_virongy import (HERE, SITE, AMBER, NAVY, NAVY_DEEP, CARD, HAIRLINE, F_HEAD,
                           F_MONO, F_BODY, esc, reroot, read, write, replace_block,
                           _chrome, check, write_sitemap)

CATALOGUE = os.path.join(HERE, "sepflow-products.json")
DISTRIBUTOR_LINE = "Exclusive Distributor in India"

PARTNER = {
    "name": "Sepflow",
    "short": "Sepflow",
    "dir": "sepflow",
    "index": "sepflow.html",
    "media_note": pages.status_note("Exclusive", "Sepflow"),
    "manufacturer_url": None,
    "quote_lead": "Tell us the system, configuration and application you have in mind. "
                  "We will confirm the specification, lead time and pricing for "
                  "delivery in India.",
}

# Rows sit in the same 2.4s-per-tile rhythm as Virongy's (11 tiles, 72s).
SECONDS_PER_TILE = 72 / 11.0


def badge(height, margin, rel=""):
    """Same badge as Virongy's (build_virongy.logo): light plate, amber ring.
    Sepflow's own logo is white artwork for a dark header; this is the same
    artwork in dark navy so it reads on the plate."""
    pv, ph = int(round(height * 0.38)), int(round(height * 0.58))
    return ('<span class="amp-vlogo" style="display:inline-block;'
            'background:linear-gradient(158deg,#f7fafd 0%%,#dfe7f1 100%%);'
            'border-radius:14px;padding:%dpx %dpx;margin:%s;'
            'box-shadow:0 0 0 1px rgba(253,157,5,0.42),0 16px 40px rgba(0,0,0,0.45)">'
            '<img src="%sassets/sepflow-logo.webp" alt="Sepflow" '
            'style="height:%dpx;width:auto;display:block"></span>'
            % (pv, ph, margin, rel, height))


# ---------------------------------------------------------------- page parts

def spec_table(group):
    rows = "".join(
        '<tr style="border-top:1px solid %s">'
        '<th scope="row" style="text-align:left;font-weight:500;color:#8b98ab;'
        'padding:9px 16px 9px 0;width:44%%;vertical-align:top;line-height:1.45">%s</th>'
        '<td style="color:#dbe3ee;padding:9px 0;vertical-align:top;line-height:1.45">%s</td></tr>'
        % (HAIRLINE, esc(label), esc(value)) for label, value in group["rows"])
    return ('<table class="amp-spec" style="width:100%%;border-collapse:collapse;'
            'font-size:0.88rem;border-bottom:1px solid %s">%s</table>' % (HAIRLINE, rows))


def detail_html(p):
    parts = []
    if p.get("features"):
        parts.append(pages.detail_block("Key features", pages.bullet_list(p["features"])))
    if p.get("applications"):
        parts.append(pages.detail_block("Applications", pages.bullet_list(p["applications"])))
    if p.get("contents"):
        parts.append(pages.detail_block("Included", pages.bullet_list(p["contents"])))
    for opt in p.get("options", []):
        parts.append(pages.detail_block(opt["label"], pages.option_pills(opt["values"])))
    for g in p.get("specs", []):
        parts.append(pages.detail_block(g["group"], spec_table(g)))
    return "".join(parts)


def gallery(p, rel):
    if not p.get("gallery"):
        return ""
    tiles = "".join(
        '<figure style="margin:0;position:relative;border-radius:12px;overflow:hidden;'
        'background:%s;border:1px solid %s;aspect-ratio:4/3">'
        '<img src="%s%s" alt="%s" loading="lazy" style="position:absolute;inset:0;'
        'width:100%%;height:100%%;object-fit:cover;display:block"></figure>'
        % (CARD, HAIRLINE, rel, esc(g["src"]), esc(g["alt"])) for g in p["gallery"])
    return (
        '\n  <section style="background:%(navy)s;padding:0 0 64px">\n'
        '    <div style="max-width:1240px;margin:0 auto;padding:0 32px">\n'
        '      <div style="font-family:%(fm)s;font-size:0.7rem;letter-spacing:0.18em;'
        'text-transform:uppercase;color:%(amber)s;margin:0 0 16px">Gallery</div>\n'
        '      <div class="amp-gal" style="display:grid;grid-template-columns:'
        'repeat(auto-fill,minmax(260px,1fr));gap:18px">%(tiles)s</div>\n'
        '    </div>\n'
        '  </section>\n' % {"navy": NAVY, "fm": F_MONO, "amber": AMBER, "tiles": tiles})


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
        '<span style="color:#fff">Sepflow </span>'
        '<span style="color:%(amber)s">in India.</span></h1>\n'
        '        <p style="color:#c4cede;font-size:1.1rem;line-height:1.62;margin:0 0 28px;'
        'max-width:620px">%(lead)s</p>\n'
        '        %(nav)s\n'
        '      </div>\n'
        '    </div>\n'
        '  </section>\n' % {
            "img": esc(hero["image"]), "alt": esc(hero["alt"]), "pos": hero["position"],
            "fm": F_MONO, "fh": F_HEAD, "amber": AMBER, "dline": DISTRIBUTOR_LINE,
            "logo": badge(46, "0 0 26px"), "lead": esc(data["lead"]),
            "nav": pages.category_nav(cats, counts)})
    body += pages.catbar(cats, counts, data.get("short", {}))
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
    title = "Sepflow — Exclusive Distributor for India | Ampbio"
    desc = ("Exclusive distributor in India for Sepflow chromatography and protein "
            "purification systems: %d products including AIpure systems, pumps, valves "
            "and ChromX software." % len(products))
    return pages.shell(title, desc, "https://amps.bio/sepflow.html",
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
    if not others:  # a one-product category still gets neighbours to browse
        others = [q for q in data["products"] if q is not p][:4]

    url = "https://amps.bio/sepflow/%s.html" % p["slug"]
    page_p = dict(p, image=p["hero_image"])
    body = pages.product_body(
        page_p, detail_html(p), pages.breadcrumb(p, rel, PARTNER),
        pages.prev_next(prev, nxt), rel,
        "%sconnect.html?product=%s" % (rel, quote("Sepflow " + p["name"])), PARTNER)
    body += gallery(p, rel)
    body += pages.related(others, p["category"], PARTNER)
    body += pages.enquiry_band(rel, PARTNER)
    return pages.shell(
        "%s | Sepflow — Ampbio India" % p["name"],
        pages.meta_description(page_p, partner=PARTNER), url, body, rel, header, footer,
        extra_head=pages.product_jsonld(page_p, url, PARTNER))


# ------------------------------------------------------------ other pages

def build_hero_strip(data):
    """The third row of the homepage hero strip. Same tile as the Virongy row
    (build_virongy.tiles_track), linking to our Sepflow pages."""
    by = {p["slug"]: p for p in data["products"]}
    feats = [by[s] for s in data["featured"] if s in by]
    track = "".join(
        '\n          <a class="amp-mq-tile" href="sepflow/%s.html" title="%s" style="flex:0 0 auto;'
        'width:330px;display:flex;flex-direction:column;gap:9px;text-decoration:none">'
        '<div style="position:relative;height:222px;border-radius:12px;overflow:hidden;'
        'background:%s;border:1px solid %s"><img src="%s" alt="%s" '
        'style="position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover;display:block">'
        '</div><div style="font-family:%s;font-weight:700;font-size:1rem;line-height:1.2;'
        'color:#dbe3ee">%s</div></a>'
        % (esc(p["slug"]), esc(p["name"]), CARD, HAIRLINE, esc(p["image"]), esc(p["name"]),
           F_HEAD, esc(p["name"])) for p in feats)
    return (
        '\n      <div class="amp-marquee" style="position:relative;overflow:hidden">\n'
        '        <div class="amp-marquee-track" style="display:flex;gap:18px;'
        'width:max-content;padding:0 10px;animation-duration:%ds">%s%s\n'
        '        </div>\n'
        '      </div>\n    '
        % (round(SECONDS_PER_TILE * len(feats)), track, track))


def promo_banner(href, dline, logo, image, alt, position, text, cta):
    """Distributor card on products.html: the same .amp-promo-card component as
    Virongy's, so the partner cards read as a set. Shared with build_jena.py."""
    return (
        '\n  <section style="background:%(navy)s;padding:22px 0 0">\n'
        '    <div style="max-width:1240px;margin:0 auto;padding:0 32px">\n'
        '      <div class="amp-promo-card amp-vdist" style="position:relative;border-radius:15px;'
        'overflow:hidden;min-height:230px;background:#06101e;border:1px solid %(hair)s;display:flex">\n'
        '        <div style="position:absolute;inset:0"><img src="%(img)s" alt="%(alt)s" '
        'style="position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover;'
        'object-position:%(pos)s;display:block"></div>\n'
        '        <div style="position:absolute;inset:0;background:linear-gradient(90deg,'
        'rgba(6,16,30,0.97) 0%%,rgba(6,16,30,0.93) 42%%,rgba(6,16,30,0.45) 66%%,rgba(6,16,30,0.08) 100%%)"></div>\n'
        '        <div style="position:relative;z-index:2;padding:34px;display:flex;flex-direction:column;'
        'align-items:flex-start;width:56%%;min-width:320px">\n'
        '          <div style="font-family:%(fm)s;font-size:0.72rem;letter-spacing:0.18em;color:%(amber)s;'
        'text-transform:uppercase;margin-bottom:14px">%(dline)s</div>\n'
        '          %(logo)s\n'
        '          <p style="color:#c4cede;font-size:0.98rem;line-height:1.6;margin:0 0 24px">%(text)s</p>\n'
        '          <a class="amp-promo-cta" href="%(href)s" style="margin-top:auto;background:%(amber)s;'
        'color:%(navy)s;font-family:%(fb)s;font-weight:700;font-size:0.92rem;padding:12px 24px;'
        'border-radius:6px;transition:background .2s;line-height:1.35;max-width:100%%">%(cta)s</a>\n'
        '        </div>\n'
        '      </div>\n'
        '    </div>\n'
        '  </section>\n' % {
            "navy": NAVY, "hair": HAIRLINE, "fm": F_MONO, "fb": F_BODY, "amber": AMBER,
            "dline": dline, "logo": logo, "href": href,
            "img": esc(image), "alt": esc(alt), "pos": position,
            "text": esc(text), "cta": esc(cta)})


def build_banner(data):
    b = data["banner"]
    return promo_banner("sepflow.html", DISTRIBUTOR_LINE, badge(40, "0 0 18px"), b["image"],
                        b["alt"], b.get("position", "center"), data["blurb"], data["cta"])


def check_sepflow(path):
    s = read(path)
    for bad in ("sepflow.com", "aliyuncs", "€", "¥", "RMB", "Add to cart"):
        if bad in s:
            raise SystemExit("%s FAILED: %r must not appear" % (path, bad))
    check(path)


def main():
    data = json.load(io.open(CATALOGUE, encoding="utf-8"))
    products = data["products"]

    os.makedirs(os.path.join(SITE, "sepflow"), exist_ok=True)
    write("sepflow.html", build_index(data))
    for p in products:
        write("sepflow/%s.html" % p["slug"], build_product(p, data))

    home = read("index.html")
    home = replace_block(home, "SEPFLOW-HERO-STRIP", pages.hero_row(
        pages.row_tag("assets/sepflow-logo.webp", "Sepflow", "Exclusive"),
        build_hero_strip(data)))
    write("index.html", home)
    write("products.html",
          replace_block(read("products.html"), "SEPFLOW-BANNER", build_banner(data)))

    for page in ["sepflow.html", "index.html", "products.html"] + [
            "sepflow/%s.html" % p["slug"] for p in products]:
        check_sepflow(page)

    n = write_sitemap(json.load(io.open(os.path.join(HERE, "virongy-products.json"),
                                        encoding="utf-8")))
    print("sepflow.html      range page, %d categories" % len(data["categories"]))
    print("sepflow/*.html    %d product pages" % len(products))
    print("index.html        hero row (%d tiles) + band" % len(data["featured"]))
    print("products.html     distributor card")
    print("sitemap.xml       %d URLs" % n)


if __name__ == "__main__":
    main()
