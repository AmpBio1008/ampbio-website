# -*- coding: utf-8 -*-
"""
Generate the Virongy catalogue page and the two Virongy blocks on the existing
pages, from _build/virongy-products.json.

  python _build/build_virongy.py            (run from the site/ directory)

Writes:
  virongy.html                              - full catalogue page
  index.html      between VIRONGY-MARQUEE markers   - homepage scrolling strip
  products.html   between VIRONGY-BANNER markers    - distributor feature banner
  assets/docs/MANIFEST.txt is written by _build/fetch_docs.py

The header and footer are lifted verbatim out of products.html so the new page
can never drift from the rest of the site. Document download buttons are only
emitted for PDFs that actually exist in assets/docs/.
"""
import io, json, os, re, sys
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
CATALOGUE = os.path.join(HERE, "virongy-products.json")
DOCS_DIR = os.path.join(SITE, "assets", "docs")
DOC_MAP_PATH = os.path.join(HERE, "doc-map.json")
DOC_MAP = (json.load(io.open(DOC_MAP_PATH, encoding="utf-8"))
           if os.path.exists(DOC_MAP_PATH) else {})

DISTRIBUTOR_LINE = "Exclusive Distributor in India"
PARTNER = "Virongy Biosciences"

AMBER = "#FD9D05"
NAVY = "#0a1524"
NAVY_DEEP = "#081321"
CARD = "#0b1a2c"
HAIRLINE = "rgba(255,255,255,0.08)"

F_HEAD = "'D-DIN Condensed','D-DIN',sans-serif"
F_MONO = "'IBM Plex Mono',monospace"
F_BODY = "'D-DIN','IBM Plex Sans',sans-serif"


def logo(height, margin):
    """Partner badge. Virongy's logo is dark artwork on transparency, so on the
    navy sections it sits on a light plate rather than being recoloured. The
    amber ring and lift make it read as a deliberate badge, not a pasted image.
    Padding scales with the logo so the proportions hold at every size; the
    .amp-vlogo hook shrinks it on phones (styles.css)."""
    pv, ph = int(round(height * 0.38)), int(round(height * 0.58))
    return ('<span class="amp-vlogo" style="display:inline-block;'
            'background:linear-gradient(158deg,#f7fafd 0%%,#dfe7f1 100%%);'
            'border-radius:14px;padding:%dpx %dpx;margin:%s;'
            'box-shadow:0 0 0 1px rgba(253,157,5,0.42),0 16px 40px rgba(0,0,0,0.45)">'
            '<img src="assets/virongy-logo.webp" alt="Virongy Biosciences" '
            'style="height:%dpx;width:auto;display:block"></span>'
            % (pv, ph, margin, height))


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def read(path):
    return io.open(os.path.join(SITE, path), encoding="utf-8").read()


def write(path, text):
    io.open(os.path.join(SITE, path), "w", encoding="utf-8", newline="").write(text)


def slice_between(text, start_marker, end_marker, inclusive=True):
    i = text.index(start_marker)
    j = text.index(end_marker, i) + len(end_marker)
    return text[i:j] if inclusive else text[i + len(start_marker):j - len(end_marker)]


def replace_block(text, name, body):
    """Swap the content between <!-- name:START --> and <!-- name:END -->."""
    start, end = "<!-- %s:START -->" % name, "<!-- %s:END -->" % name
    if start not in text:
        raise SystemExit("marker %s missing - add it to the page first" % start)
    i = text.index(start) + len(start)
    j = text.index(end, i)
    return text[:i] + body + text[j:]


# ---------------------------------------------------------------- page parts

def bullet_list(items, colour="#c4cede"):
    rows = []
    for t in items:
        rows.append(
            '<li class="amp-bullet" style="display:flex;gap:10px;align-items:flex-start;'
            'color:%s;font-size:0.9rem;line-height:1.45">'
            '<span style="flex:0 0 5px;width:5px;height:5px;border-radius:50%%;'
            'background:%s;margin-top:7px"></span>%s</li>' % (colour, AMBER, esc(t)))
    return ('<ul style="list-style:none;margin:0;padding:0;display:flex;'
            'flex-direction:column;gap:7px">%s</ul>' % "".join(rows))


def detail_block(label, inner):
    return ('<div style="margin-top:16px">'
            '<div style="font-family:%s;font-size:0.68rem;letter-spacing:0.16em;'
            'color:%s;text-transform:uppercase;margin-bottom:9px">%s</div>%s</div>'
            % (F_MONO, AMBER, esc(label), inner))


def option_pills(values):
    pills = []
    for v in values:
        pills.append(
            '<span style="display:inline-block;border:1px solid rgba(253,157,5,0.35);'
            'color:#dbe3ee;font-size:0.78rem;line-height:1.2;padding:5px 10px;'
            'border-radius:999px;white-space:nowrap">%s</span>' % esc(v))
    return ('<div style="display:flex;flex-wrap:wrap;gap:6px">%s</div>'
            % "".join(pills))


def doc_buttons(docs):
    """`docs` comes from _build/doc-map.json, written by fetch_docs.py, so the
    page and the files on disk can never disagree about names."""
    out = []
    for d in docs:
        local = os.path.join(SITE, d["path"].replace("/", os.sep))
        if not os.path.exists(local):
            continue
        out.append(
            '<a class="amp-doc" href="%s" download style="display:inline-flex;'
            'align-items:center;gap:8px;border:1px solid rgba(253,157,5,0.45);color:%s;'
            'font-size:0.82rem;font-weight:600;padding:8px 14px;border-radius:6px;'
            'transition:background .2s">'
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="%s" '
            'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>'
            '<polyline points="7 10 12 15 17 10"></polyline>'
            '<line x1="12" y1="15" x2="12" y2="3"></line></svg>%s</a>'
            % (esc(d["path"]), AMBER, AMBER, esc(d["label"])))
    if not out:
        return ""
    return detail_block("Documents",
                        '<div style="display:flex;flex-wrap:wrap;gap:8px">%s</div>'
                        % "".join(out))


def product_card(p):
    parts = []
    if p["applications"]:
        parts.append(detail_block("Applications", bullet_list(p["applications"])))
    if p["features"]:
        parts.append(detail_block("Key features", bullet_list(p["features"])))
    if p["contents"]:
        parts.append(detail_block("Kit contents", bullet_list(p["contents"])))
    for opt in p["options"]:
        parts.append(detail_block(opt["label"], option_pills(opt["values"])))
    parts.append(doc_buttons(DOC_MAP.get(p["slug"], [])))

    quote_href = "connect.html?product=%s" % quote(p["name"])
    return (
        '\n        <article class="amp-vp" id="%(slug)s" style="background:%(card)s;'
        'border:1px solid %(hair)s;border-radius:16px;overflow:hidden;display:flex;'
        'flex-direction:column">\n'
        '          <div style="position:relative;height:190px;overflow:hidden;background:%(navy)s">'
        '<img src="%(img)s" alt="%(alt)s" loading="lazy" style="position:absolute;inset:0;'
        'width:100%%;height:100%%;object-fit:cover;display:block"></div>\n'
        '          <div style="padding:24px 24px 26px;display:flex;flex-direction:column;flex:1">\n'
        '            <h3 style="font-family:%(fh)s;font-weight:700;font-size:1.22rem;'
        'line-height:1.16;color:#fff;margin:0 0 10px">%(name)s</h3>\n'
        '            <p style="color:#c4cede;font-size:0.93rem;line-height:1.6;margin:0">%(summary)s</p>\n'
        '            %(detail)s\n'
        '            <a class="amp-quote" href="%(href)s" style="margin-top:22px;align-self:flex-start;'
        'display:inline-flex;align-items:center;gap:9px;background:%(amber)s;color:%(navy)s;'
        'font-family:%(fb)s;font-weight:700;font-size:0.88rem;padding:11px 22px;border-radius:6px;'
        'transition:background .2s">Request a quote <span class="amp-arrow">&rarr;</span></a>\n'
        '          </div>\n'
        '        </article>' % {
            "slug": esc(p["slug"]), "card": CARD, "hair": HAIRLINE, "navy": NAVY,
            "img": esc(p["image"]), "alt": esc(p["name"]), "fh": F_HEAD, "fb": F_BODY,
            "name": esc(p["name"]), "summary": esc(p["summary"]),
            "detail": "".join(parts), "href": esc(quote_href), "amber": AMBER})


def category_section(cat, products, dark):
    anchor = re.sub(r"[^a-z0-9]+", "-", cat.lower()).strip("-")
    cards = "".join(product_card(p) for p in products)
    return (
        '\n  <!-- ================= %(upper)s ================= -->\n'
        '  <section id="%(anchor)s" style="background:%(bg)s;padding:70px 0 76px">\n'
        '    <div style="max-width:1240px;margin:0 auto;padding:0 32px">\n'
        '      <div style="display:flex;align-items:baseline;justify-content:space-between;'
        'gap:20px;flex-wrap:wrap;margin:0 0 34px">\n'
        '        <h2 style="font-family:%(fh)s;font-weight:700;font-size:clamp(1.5rem,2.6vw,2.2rem);'
        'line-height:1.1;letter-spacing:-0.01em;text-transform:uppercase;color:#fff;margin:0">%(cat)s</h2>\n'
        '        <div style="font-family:%(fm)s;font-size:0.74rem;letter-spacing:0.18em;'
        'color:#8b98ab;text-transform:uppercase">%(n)d product%(s)s</div>\n'
        '      </div>\n'
        '      <div class="amp-vp-grid" style="display:grid;grid-template-columns:repeat(2,1fr);gap:22px">%(cards)s\n'
        '      </div>\n'
        '    </div>\n'
        '  </section>\n' % {
            "upper": cat.upper(), "anchor": anchor, "bg": NAVY_DEEP if dark else NAVY,
            "fh": F_HEAD, "fm": F_MONO, "cat": esc(cat), "n": len(products),
            "s": "" if len(products) == 1 else "s", "cards": cards})


def category_nav(cats, counts):
    pills = []
    for c in cats:
        anchor = re.sub(r"[^a-z0-9]+", "-", c.lower()).strip("-")
        pills.append(
            '<a class="amp-catpill" href="#%s" style="display:inline-flex;align-items:center;'
            'gap:8px;border:1px solid rgba(253,157,5,0.4);color:#dbe3ee;font-size:0.88rem;'
            'padding:9px 16px;border-radius:999px;transition:background .2s,color .2s">'
            '%s <span style="color:%s;font-weight:700">%d</span></a>'
            % (anchor, esc(c), AMBER, counts[c]))
    return ('<div style="display:flex;flex-wrap:wrap;gap:10px">%s</div>' % "".join(pills))


# ---------------------------------------------------------------- generators

PAGE_STYLE = """<style>
  /* ---- Virongy catalogue page-specific rules ---- */
  .amp-vp { transition: transform 0.35s cubic-bezier(0.22,0.61,0.36,1), box-shadow 0.35s; }
  .amp-vp img { transition: transform 0.5s cubic-bezier(0.22,0.61,0.36,1); }
  .amp-vp h3 { transition: color 0.3s; }
  .amp-vp:hover { transform: translateY(-5px); box-shadow: 0 18px 44px rgba(0,0,0,0.45), 0 0 0 1px rgba(253,157,5,0.5); }
  .amp-vp:hover img { transform: scale(1.05); }
  .amp-vp:hover h3 { color: #FD9D05; }
  .amp-quote:hover { background: #e08c00 !important; }
  .amp-doc:hover { background: rgba(253,157,5,0.14); }
  .amp-catpill:hover { background: rgba(253,157,5,0.14); color: #FD9D05; }

  @media (max-width: 1024px) {
    .amp-vp-grid { grid-template-columns: 1fr !important; }
  }
</style>"""


def build_page(data):
    products = data["products"]
    src = read("products.html")
    header = slice_between(src, "  <!-- ================= HEADER ================= -->",
                           "  </header>")
    footer = slice_between(src, "  <!-- ================= FOOTER ================= -->",
                           "  </footer>")

    counts = {c: sum(1 for p in products if p["category"] == c) for c in data["categories"]}
    cats = [c for c in data["categories"] if counts.get(c)]

    title = "%s — %s for India | Ampbio" % (PARTNER, "Exclusive Distributor")
    desc = ("Ampbio is the exclusive distributor in India for Virongy Biosciences, USA. "
            "Browse %d Virongy products - pseudoviruses, neutralization assay kits, viral "
            "protein expression vectors, transduction reagents, cell lines and custom "
            "vector design." % len(products))

    sections = "".join(category_section(c, [p for p in products if p["category"] == c], i % 2 == 1)
                       for i, c in enumerate(cats))

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
<link href="https://fonts.cdnfonts.com/css/d-din" rel="stylesheet">
<link rel="canonical" href="https://amps.bio/virongy.html">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Ampbio">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="https://amps.bio/virongy.html">
<meta property="og:image" content="https://amps.bio/assets/ampbio-logo.png">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="%(title)s">
<meta name="twitter:description" content="%(desc)s">
<meta name="twitter:image" content="https://amps.bio/assets/ampbio-logo.png">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="assets/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="stylesheet" href="styles.css">
%(style)s
</head>
<body>

<div id="amp-root" style="background:#0a1524;color:#fff;overflow-x:clip">

%(header)s

  <!-- ================= HERO ================= -->
  <section class="amp-hero" style="position:relative;overflow:hidden;min-height:600px;padding-top:76px;display:flex;align-items:center">
    <img src="assets/hero-products.webp" alt="Virongy Biosciences virology research reagents" style="position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover;object-position:70%% center;display:block;z-index:0">
    <div style="position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,rgba(8,17,29,0.97) 0%%,rgba(8,17,29,0.92) 34%%,rgba(8,17,29,0.5) 68%%,rgba(8,17,29,0.18) 100%%)"></div>
    <div style="position:absolute;inset:0;z-index:1;background:linear-gradient(0deg,rgba(8,17,29,0.6) 0%%,rgba(8,17,29,0) 42%%)"></div>
    <div style="position:relative;z-index:2;max-width:1240px;margin:0 auto;padding:56px 32px;width:100%%">
      <div style="max-width:720px">
        <div style="font-family:%(fm)s;font-size:0.78rem;letter-spacing:0.24em;color:%(amber)s;text-transform:uppercase;margin-bottom:22px">%(dline)s</div>
        %(logo)s
        <h1 class="amp-h1" style="font-family:%(fh)s;font-weight:800;font-size:clamp(2rem,3.9vw,3.3rem);line-height:1.05;letter-spacing:-0.01em;text-transform:uppercase;margin:0 0 22px">
          <span style="color:#fff">Virongy Biosciences </span><span style="color:%(amber)s">in India.</span>
        </h1>
        <p style="color:#c4cede;font-size:1.12rem;line-height:1.62;margin:0 0 30px;max-width:620px">Ampbio is the exclusive distributor in India for Virongy Biosciences, USA &mdash; pseudoviruses and single-cycle viruses, neutralization assay kits, viral protein expression vectors, transduction and transfection reagents, reporter cell lines and custom vector design.</p>
        %(catnav)s
      </div>
    </div>
  </section>
%(sections)s
  <!-- ================= ENQUIRY BAND ================= -->
  <section style="position:relative;background:#fdecdd;overflow:hidden;min-height:280px;display:flex;align-items:center">
    <img src="assets/cta-bg2.webp" alt="Molecular spheres" class="amp-cta-visual" style="position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover;display:block;transform:scaleX(-1)">
    <div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(253,236,221,0.97) 34%%,rgba(253,236,221,0.82) 52%%,rgba(253,236,221,0.35) 74%%,rgba(253,236,221,0.1) 100%%)"></div>
    <div style="position:relative;z-index:2;width:100%%;max-width:1240px;margin:0 auto;padding:56px 32px">
      <h2 style="font-family:%(fh)s;font-weight:700;font-size:clamp(1.7rem,3.2vw,2.7rem);line-height:1.06;letter-spacing:0.01em;text-transform:uppercase;margin:0;color:#1a1c1e">Request a Virongy quotation</h2>
      <div style="width:56px;height:3px;background:%(amber)s;margin:20px 0 18px"></div>
      <p style="color:#3a4048;font-size:1rem;line-height:1.65;margin:0 0 26px;max-width:540px">Tell us the product, variant and pack size you need. We will confirm availability, lead time and pricing for delivery in India.</p>
      <a class="amp-cta-btn" href="connect.html" style="display:inline-flex;align-items:center;gap:10px;background:%(amber)s;color:%(navy)s;font-family:%(fb)s;font-weight:700;font-size:0.98rem;padding:14px 30px;border-radius:7px;transition:background .25s,box-shadow .3s,transform .3s cubic-bezier(0.22,0.61,0.36,1)">Connect <span class="amp-arrow">&rarr;</span></a>
      <p style="color:#59636f;font-size:0.82rem;line-height:1.6;margin:26px 0 0;max-width:640px">Catalogue as of %(gen)s. Product names, specifications and availability are those of Virongy Biosciences and are subject to change &mdash; please confirm current details with us. All products are for research use only.</p>
    </div>
  </section>

%(footer)s

</div>

<script src="app.js"></script>
</body>
</html>
""" % {"title": esc(title), "desc": esc(desc), "style": PAGE_STYLE, "header": header,
       "footer": footer, "sections": sections, "catnav": category_nav(cats, counts),
       "fm": F_MONO, "fh": F_HEAD, "fb": F_BODY, "amber": AMBER, "navy": NAVY,
       "dline": DISTRIBUTOR_LINE, "gen": data["generated"], "logo": logo(76, "0 0 28px")}


def build_marquee(data):
    by = {p["slug"]: p for p in data["products"]}
    feats = [by[s] for s in data["featured"] if s in by]
    tiles = []
    for p in feats:
        tiles.append(
            '\n          <a class="amp-mq-tile" href="virongy.html#%s" style="flex:0 0 auto;'
            'width:212px;display:flex;flex-direction:column;gap:11px;text-decoration:none">'
            '<div style="position:relative;height:142px;border-radius:14px;overflow:hidden;'
            'background:%s;border:1px solid %s"><img src="%s" alt="%s" '
            'style="position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover;display:block">'
            '</div><div style="font-family:%s;font-weight:700;font-size:0.92rem;line-height:1.2;'
            'color:#dbe3ee">%s</div></a>'
            % (esc(p["slug"]), CARD, HAIRLINE, esc(p["image"]), esc(p["name"]),
               F_HEAD, esc(p["name"])))
    # the list is rendered twice so the -50% translation loops seamlessly
    track = "".join(tiles)

    return (
        # Same composition as the PLATFORMS section on this page: copy block on
        # the left, visual on the right, then the full-bleed row underneath.
        '\n  <section style="background:%(navy)s;padding:80px 0 76px;overflow:hidden">\n'
        '    <div style="max-width:1240px;margin:0 auto;padding:0 32px 54px">\n'
        '      <div class="amp-vhead" style="display:grid;'
        'grid-template-columns:minmax(0,1.2fr) minmax(0,0.8fr);gap:54px;align-items:center">\n'
        '        <div>\n'
        '          <div class="amp-vlead" style="font-family:%(fm)s;font-size:0.95rem;'
        'letter-spacing:0.2em;color:%(amber)s;text-transform:uppercase;margin-bottom:20px">'
        '%(dline)s</div>\n'
        '          <h2 style="font-family:%(fh)s;font-weight:700;font-size:clamp(1.8rem,3vw,2.6rem);'
        'line-height:1.08;letter-spacing:-0.01em;text-transform:uppercase;color:#fff;margin:0 0 20px">'
        'Featured Products from <span style="color:%(amber)s">Virongy Biosciences</span></h2>\n'
        '          <p style="color:#9fabbd;font-size:1rem;line-height:1.65;margin:0 0 28px;'
        'max-width:460px">Ampbio is the exclusive distributor in India for Virongy Biosciences, '
        'USA &mdash; %(n)d products spanning pseudoviruses, neutralization assay kits, viral protein '
        'expression vectors, transduction reagents and reporter cell lines.</p>\n'
        '          <a class="amp-cta-btn" href="virongy.html" style="display:inline-flex;'
        'align-items:center;gap:10px;background:%(amber)s;color:%(navy)s;font-family:%(fb)s;'
        'font-weight:700;font-size:0.95rem;padding:13px 28px;border-radius:7px;'
        'transition:background .25s,box-shadow .3s,transform .3s cubic-bezier(0.22,0.61,0.36,1)">'
        'View the Virongy range <span class="amp-arrow">&rarr;</span></a>\n'
        '        </div>\n'
        '        <div class="amp-vhead-mark" style="justify-self:end">%(logo)s</div>\n'
        '      </div>\n'
        '    </div>\n'
        '    <div class="amp-marquee" style="position:relative;overflow:hidden">\n'
        '      <div class="amp-marquee-track" style="display:flex;gap:20px;width:max-content;'
        'padding:0 10px">%(track)s%(track)s\n'
        '      </div>\n'
        '    </div>\n'
        '  </section>\n' % {
            "navy": NAVY, "fm": F_MONO, "fh": F_HEAD, "fb": F_BODY, "amber": AMBER,
            "dline": DISTRIBUTOR_LINE, "track": track, "logo": logo(62, "0"),
            "n": len(data["products"])})


def build_banner(data):
    n = len(data["products"])
    return (
        # First section on products.html, so the top padding also has to clear
        # the 76px fixed header (76 + 74).
        '\n  <section style="background:%(navy)s;padding:150px 0 0">\n'
        '    <div style="max-width:1240px;margin:0 auto;padding:0 32px">\n'
        '      <div class="amp-promo-card amp-vdist" style="position:relative;border-radius:15px;'
        'overflow:hidden;min-height:230px;background:#06101e;border:1px solid %(hair)s;display:flex">\n'
        '        <div style="position:absolute;inset:0"><img src="assets/promo-dna.webp" '
        'alt="DNA helix" style="position:absolute;inset:0;width:100%%;height:100%%;'
        'object-fit:cover;display:block"></div>\n'
        '        <div style="position:absolute;inset:0;background:linear-gradient(90deg,'
        'rgba(6,16,30,0.97) 0%%,rgba(6,16,30,0.93) 42%%,rgba(6,16,30,0.45) 66%%,rgba(6,16,30,0.08) 100%%)"></div>\n'
        '        <div style="position:relative;z-index:2;padding:34px;display:flex;flex-direction:column;'
        'align-items:flex-start;width:56%%;min-width:320px">\n'
        '          <div style="font-family:%(fm)s;font-size:0.72rem;letter-spacing:0.18em;color:%(amber)s;'
        'text-transform:uppercase;margin-bottom:14px">%(dline)s</div>\n'
        '          %(logo)s\n'
        '          <p style="color:#c4cede;font-size:0.98rem;line-height:1.6;margin:0 0 24px">Ampbio is the '
        'exclusive distributor in India for Virongy Biosciences, USA. %(n)d products across pseudoviruses, '
        'neutralization assay kits, viral protein expression vectors, transduction reagents, reporter cell '
        'lines and custom vector design.</p>\n'
        '          <a class="amp-promo-cta" href="virongy.html" style="margin-top:auto;background:%(amber)s;'
        'color:%(navy)s;font-family:%(fb)s;font-weight:700;font-size:0.92rem;padding:12px 24px;'
        'border-radius:6px;transition:background .2s">View Virongy Products</a>\n'
        '        </div>\n'
        '      </div>\n'
        '    </div>\n'
        '  </section>\n' % {
            "navy": NAVY, "hair": HAIRLINE, "fm": F_MONO, "fb": F_BODY,
            "amber": AMBER, "dline": DISTRIBUTOR_LINE, "n": n, "logo": logo(56, "0 0 18px")})


def write_manifest(data):
    rows, seen = [], set()
    for p in data["products"]:
        for d in p["docs"]:
            if d["file"] in seen:
                continue
            seen.add(d["file"])
            have = os.path.exists(os.path.join(DOCS_DIR, d["file"]))
            rows.append("%-6s %-72s %s" % ("HAVE" if have else "NEED", d["file"], p["name"]))
    have = sum(1 for r in rows if r.startswith("HAVE"))
    text = ("Virongy product documents referenced by virongy.com.\n"
            "Drop the files into site/assets/docs/ using exactly these filenames,\n"
            "then re-run _build/build_virongy.py to add the download buttons.\n\n"
            "%d of %d present.\n\n%s\n" % (have, len(rows), "\n".join(sorted(rows))))
    io.open(os.path.join(HERE, "pdf-manifest.txt"), "w", encoding="utf-8").write(text)
    return have, len(rows)


def check(path):
    """Catch malformed markup before it can ship - an unterminated <img left by a
    bad edit once swallowed the logo chip and rendered the logo at full size."""
    s = read(path)
    problems = []
    # a '<' inside a tag means the previous tag was never closed
    for m in re.finditer(r"<(img|span|a|div)\b[^>]*<", s):
        problems.append("unterminated <%s> near: %s" % (m.group(1), m.group(0)[:90]))
    for tag in ("article", "section", "ul", "li", "h3"):
        o = len(re.findall(r"<%s\b" % tag, s))
        c = len(re.findall(r"</%s>" % tag, s))
        if o != c:
            problems.append("%s: %d open vs %d close" % (tag, o, c))
    for bad in ("$", "Add to cart", "Select options"):
        if bad in s and path == "virongy.html":
            problems.append("price/shop wording leaked: %r" % bad)
    if problems:
        raise SystemExit("%s FAILED:\n  %s" % (path, "\n  ".join(problems)))
    return len(re.findall(r'src="assets/virongy-logo\.webp"', s))


def main():
    data = json.load(io.open(CATALOGUE, encoding="utf-8"))
    write("virongy.html", build_page(data))
    write("index.html", replace_block(read("index.html"), "VIRONGY-MARQUEE", build_marquee(data)))
    write("products.html", replace_block(read("products.html"), "VIRONGY-BANNER", build_banner(data)))
    for p in ("virongy.html", "index.html", "products.html"):
        n = check(p)
        print("checked           %-16s ok  (%d logo image%s)" % (p, n, "" if n == 1 else "s"))
    have = sum(len(v) for v in DOC_MAP.values())
    total = sum(len(p["docs"]) for p in data["products"])
    print("virongy.html      %d products in %d categories" % (
        len(data["products"]), len(data["categories"])))
    print("index.html        marquee, %d featured products" % len(data["featured"]))
    print("products.html     distributor banner")
    print("documents         %d download buttons across %d products "
          "(see assets/docs/MANIFEST.txt)" % (have, len(DOC_MAP)))


if __name__ == "__main__":
    main()
