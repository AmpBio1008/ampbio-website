# -*- coding: utf-8 -*-
"""
Page shells for the Virongy section: the range index and the 52 product pages.

Kept apart from build_virongy.py so the markup for a page is readable in one
place. Everything here takes `rel` - the prefix that reaches the site root,
"" for virongy.html and "../" for a page inside virongy/ - because the same
header, footer and asset links are reused at both depths.
"""
import re

AMBER = "#FD9D05"
NAVY = "#0a1524"
NAVY_DEEP = "#081321"
CARD = "#0b1a2c"
HAIRLINE = "rgba(255,255,255,0.08)"
F_HEAD = "'D-DIN Condensed','D-DIN',sans-serif"
F_MONO = "'IBM Plex Mono',monospace"
F_BODY = "'D-DIN','IBM Plex Sans',sans-serif"

SITE = "https://amps.bio"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


STYLE = """<style>
  /* ---- Virongy pages ---- */
  .amp-vp { transition: transform 0.35s cubic-bezier(0.22,0.61,0.36,1), box-shadow 0.35s; }
  .amp-vp img { transition: transform 0.5s cubic-bezier(0.22,0.61,0.36,1); }
  .amp-vp h3 { transition: color 0.3s; }
  .amp-vp:hover { transform: translateY(-5px); box-shadow: 0 18px 44px rgba(0,0,0,0.45), 0 0 0 1px rgba(253,157,5,0.5); }
  .amp-vp:hover img { transform: scale(1.05); }
  .amp-vp:hover h3 { color: #FD9D05; }
  .amp-quote:hover { background: #e08c00 !important; }
  .amp-doc:hover { background: rgba(253,157,5,0.14); }
  .amp-catpill:hover { background: rgba(253,157,5,0.14); color: #FD9D05; }
  .amp-crumb a:hover { color: #FD9D05; }
  .amp-pn:hover { border-color: rgba(253,157,5,0.6); background: rgba(253,157,5,0.08); }

  @media (max-width: 1024px) {
    .amp-vp-grid { grid-template-columns: 1fr !important; }
    .amp-prod { grid-template-columns: 1fr !important; gap: 30px !important; }
    .amp-prod-media { position: static !important; }
  }
  @media (max-width: 620px) {
    .amp-pn-row { grid-template-columns: 1fr !important; }
  }
</style>"""


def shell(title, desc, canonical, body, rel, header, footer, extra_head=""):
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
<link rel="canonical" href="%(canonical)s">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Ampbio">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(canonical)s">
<meta property="og:image" content="%(site)s/assets/ampbio-logo.png">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="%(title)s">
<meta name="twitter:description" content="%(desc)s">
<meta name="twitter:image" content="%(site)s/assets/ampbio-logo.png">
<link rel="icon" href="%(rel)sassets/favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="%(rel)sassets/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="%(rel)sassets/apple-touch-icon.png">
<link rel="stylesheet" href="%(rel)sstyles.css">
%(style)s%(extra)s
</head>
<body>

<div id="amp-root" style="background:#0a1524;color:#fff;overflow-x:clip">

%(header)s
%(body)s
%(footer)s

</div>

<script src="%(rel)sapp.js"></script>
</body>
</html>
""" % {"title": esc(title), "desc": esc(desc), "canonical": canonical, "site": SITE,
       "rel": rel, "style": STYLE, "extra": extra_head, "header": header,
       "footer": footer, "body": body}


# ------------------------------------------------------------------ index

def compact_card(p, in_dir):
    href = ("%s.html" % p["slug"]) if in_dir else ("virongy/%s.html" % p["slug"])
    bits = []
    n = sum(len(o["values"]) for o in p["options"])
    if n:
        bits.append("%d option%s" % (n, "" if n == 1 else "s"))
    if p.get("doc_count"):
        bits.append("%d document%s" % (p["doc_count"], "" if p["doc_count"] == 1 else "s"))
    meta = ("<div style=\"font-family:%s;font-size:0.66rem;letter-spacing:0.14em;"
            "text-transform:uppercase;color:#8b98ab;margin-top:10px\">%s</div>"
            % (F_MONO, esc(" · ".join(bits)))) if bits else ""
    return (
        '\n        <a class="amp-vp" id="%(slug)s" href="%(href)s" style="background:%(card)s;'
        'border:1px solid %(hair)s;border-radius:14px;overflow:hidden;display:flex;'
        'flex-direction:column;text-decoration:none">\n'
        '          <div style="position:relative;height:150px;overflow:hidden;background:%(navy)s">'
        '<img src="%(img)s" alt="%(alt)s" loading="lazy" style="position:absolute;inset:0;'
        'width:100%%;height:100%%;object-fit:cover;display:block"></div>\n'
        '          <div style="padding:16px 18px 20px;display:flex;flex-direction:column;flex:1">\n'
        '            <h3 style="font-family:%(fh)s;font-weight:700;font-size:1.02rem;'
        'line-height:1.18;color:#fff;margin:0 0 8px">%(name)s</h3>\n'
        '            <p style="color:#9fabbd;font-size:0.86rem;line-height:1.5;margin:0">%(teaser)s</p>\n'
        '            %(meta)s\n'
        '            <span style="margin-top:14px;color:%(amber)s;font-weight:700;'
        'font-size:0.84rem">View product &rarr;</span>\n'
        '          </div>\n'
        '        </a>' % {
            "slug": esc(p["slug"]), "href": esc(href), "card": CARD, "hair": HAIRLINE,
            "navy": NAVY, "img": esc(("../" if in_dir else "") + p["image"]),
            "alt": esc(p["name"]), "fh": F_HEAD, "name": esc(p["name"]),
            "teaser": esc(teaser(p["summary"])), "meta": meta, "amber": AMBER})


def teaser(summary, limit=118):
    if len(summary) <= limit:
        return summary
    cut = summary[:limit]
    return cut[:cut.rfind(" ")].rstrip(" ,;.") + "…"


def anchor(cat):
    return re.sub(r"[^a-z0-9]+", "-", cat.lower()).strip("-")


def index_section(cat, products, dark):
    cards = "".join(compact_card(p, False) for p in products)
    return (
        '\n  <section id="%(anchor)s" style="background:%(bg)s;padding:64px 0 70px">\n'
        '    <div style="max-width:1240px;margin:0 auto;padding:0 32px">\n'
        '      <div style="display:flex;align-items:baseline;justify-content:space-between;'
        'gap:20px;flex-wrap:wrap;margin:0 0 30px">\n'
        '        <h2 style="font-family:%(fh)s;font-weight:700;font-size:clamp(1.5rem,2.6vw,2.2rem);'
        'line-height:1.1;letter-spacing:-0.01em;text-transform:uppercase;color:#fff;margin:0">%(cat)s</h2>\n'
        '        <div style="font-family:%(fm)s;font-size:0.74rem;letter-spacing:0.18em;'
        'color:#8b98ab;text-transform:uppercase">%(n)d product%(s)s</div>\n'
        '      </div>\n'
        '      <div class="amp-vp-grid" style="display:grid;'
        'grid-template-columns:repeat(auto-fill,minmax(264px,1fr));gap:20px">%(cards)s\n'
        '      </div>\n'
        '    </div>\n'
        '  </section>\n' % {
            "anchor": anchor(cat), "bg": NAVY_DEEP if dark else NAVY, "fh": F_HEAD,
            "fm": F_MONO, "cat": esc(cat), "n": len(products),
            "s": "" if len(products) == 1 else "s", "cards": cards})


# ---------------------------------------------------------------- product

SEP = '<span style="margin:0 9px;color:#5f6d7f">/</span>'


def breadcrumb(p, rel):
    """Home / Virongy Biosciences / <category> / <product>, so a visitor landing
    straight on a product page knows where they are and can step back up."""
    return (
        '<nav class="amp-crumb" aria-label="Breadcrumb" style="font-size:0.84rem;'
        'color:#8b98ab;margin:0 0 20px;line-height:1.7">'
        '<a href="%(rel)sindex.html" style="color:#8b98ab">Home</a>%(sep)s'
        '<a href="%(rel)svirongy.html" style="color:#8b98ab">Virongy Biosciences</a>%(sep)s'
        '<a href="%(rel)svirongy.html#%(anch)s" style="color:#8b98ab">%(cat)s</a>%(sep)s'
        '<span style="color:#dbe3ee">%(name)s</span></nav>'
        % {"rel": rel, "sep": SEP, "anch": anchor(p["category"]),
           "cat": esc(p["category"]), "name": esc(p["name"])})


def prev_next(prev, nxt):
    def cell(p, label, align):
        if not p:
            return "<div></div>"
        return (
            '<a class="amp-pn" href="%s.html" style="display:block;border:1px solid %s;'
            'border-radius:10px;padding:14px 18px;text-decoration:none;text-align:%s;'
            'transition:border-color .2s,background .2s">'
            '<div style="font-family:%s;font-size:0.64rem;letter-spacing:0.16em;'
            'text-transform:uppercase;color:%s;margin-bottom:6px">%s</div>'
            '<div style="color:#dbe3ee;font-size:0.92rem;line-height:1.3">%s</div></a>'
            % (esc(p["slug"]), HAIRLINE, align, F_MONO, AMBER, label, esc(p["name"])))
    return ('<div class="amp-pn-row" style="display:grid;grid-template-columns:1fr 1fr;'
            'gap:16px;margin-top:40px">%s%s</div>'
            % (cell(prev, "&larr; Previous", "left"), cell(nxt, "Next &rarr;", "right")))


def related(items, cat):
    if not items:
        return ""
    cards = "".join(compact_card(p, True) for p in items)
    return (
        '\n  <section style="background:%(bg)s;padding:60px 0 70px">\n'
        '    <div style="max-width:1240px;margin:0 auto;padding:0 32px">\n'
        '      <h2 style="font-family:%(fh)s;font-weight:700;font-size:clamp(1.3rem,2.2vw,1.8rem);'
        'line-height:1.1;text-transform:uppercase;color:#fff;margin:0 0 8px">More in %(cat)s</h2>\n'
        '      <p style="color:#8b98ab;font-size:0.92rem;margin:0 0 26px">Other Virongy products '
        'in the same category.</p>\n'
        '      <div class="amp-vp-grid" style="display:grid;'
        'grid-template-columns:repeat(auto-fill,minmax(264px,1fr));gap:20px">%(cards)s\n'
        '      </div>\n'
        '    </div>\n'
        '  </section>\n'
        % {"bg": NAVY_DEEP, "fh": F_HEAD, "cat": esc(cat), "cards": cards})


def bullet_list(items):
    rows = "".join(
        '<li class="amp-bullet" style="display:flex;gap:10px;align-items:flex-start;'
        'color:#c4cede;font-size:0.9rem;line-height:1.45">'
        '<span style="flex:0 0 5px;width:5px;height:5px;border-radius:50%%;'
        'background:%s;margin-top:7px"></span>%s</li>' % (AMBER, esc(t)) for t in items)
    return ('<ul style="list-style:none;margin:0;padding:0;display:flex;'
            'flex-direction:column;gap:7px">%s</ul>' % rows)


def detail_block(label, inner):
    return ('<div style="margin-top:18px">'
            '<div style="font-family:%s;font-size:0.68rem;letter-spacing:0.16em;'
            'color:%s;text-transform:uppercase;margin-bottom:9px">%s</div>%s</div>'
            % (F_MONO, AMBER, esc(label), inner))


def option_pills(values):
    pills = "".join(
        '<span style="display:inline-block;border:1px solid rgba(253,157,5,0.35);'
        'color:#dbe3ee;font-size:0.78rem;line-height:1.2;padding:5px 10px;'
        'border-radius:999px;white-space:nowrap">%s</span>' % esc(v) for v in values)
    return '<div style="display:flex;flex-wrap:wrap;gap:6px">%s</div>' % pills


def doc_buttons(docs, rel, exists):
    """`docs` comes from _build/doc-map.json, written by fetch_docs.py, so the
    page and the files on disk can never disagree about names. `exists` is a
    predicate so this module stays free of filesystem concerns."""
    out = []
    for d in docs:
        if not exists(d["path"]):
            continue
        out.append(
            '<a class="amp-doc" href="%s%s" download style="display:inline-flex;'
            'align-items:center;gap:8px;border:1px solid rgba(253,157,5,0.45);color:%s;'
            'font-size:0.82rem;font-weight:600;padding:8px 14px;border-radius:6px;'
            'transition:background .2s">'
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="%s" '
            'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>'
            '<polyline points="7 10 12 15 17 10"></polyline>'
            '<line x1="12" y1="15" x2="12" y2="3"></line></svg>%s</a>'
            % (rel, esc(d["path"]), AMBER, AMBER, esc(d["label"])))
    if not out:
        return ""
    return detail_block("Documents",
                        '<div style="display:flex;flex-wrap:wrap;gap:8px">%s</div>'
                        % "".join(out))


def category_nav(cats, counts):
    pills = "".join(
        '<a class="amp-catpill" href="#%s" style="display:inline-flex;align-items:center;'
        'gap:8px;border:1px solid rgba(253,157,5,0.4);color:#dbe3ee;font-size:0.88rem;'
        'padding:9px 16px;border-radius:999px;transition:background .2s,color .2s">'
        '%s <span style="color:%s;font-weight:700">%d</span></a>'
        % (anchor(c), esc(c), AMBER, counts[c]) for c in cats)
    return '<div style="display:flex;flex-wrap:wrap;gap:10px">%s</div>' % pills


def enquiry_band(rel):
    return (
        '\n  <!-- ================= ENQUIRY BAND ================= -->\n'
        '  <section style="position:relative;background:#fdecdd;overflow:hidden;'
        'min-height:260px;display:flex;align-items:center">\n'
        '    <img src="%(rel)sassets/cta-bg2.webp" alt="Molecular spheres" class="amp-cta-visual" '
        'style="position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover;'
        'display:block;transform:scaleX(-1)">\n'
        '    <div style="position:absolute;inset:0;background:linear-gradient(90deg,'
        'rgba(253,236,221,0.97) 34%%,rgba(253,236,221,0.82) 52%%,rgba(253,236,221,0.35) 74%%,'
        'rgba(253,236,221,0.1) 100%%)"></div>\n'
        '    <div style="position:relative;z-index:2;width:100%%;max-width:1240px;margin:0 auto;'
        'padding:52px 32px">\n'
        '      <h2 style="font-family:%(fh)s;font-weight:700;font-size:clamp(1.6rem,3vw,2.5rem);'
        'line-height:1.06;text-transform:uppercase;margin:0;color:#1a1c1e">'
        'Request a Virongy quotation</h2>\n'
        '      <div style="width:56px;height:3px;background:%(amber)s;margin:18px 0 16px"></div>\n'
        '      <p style="color:#3a4048;font-size:1rem;line-height:1.65;margin:0 0 24px;'
        'max-width:540px">Tell us the product, variant and pack size you need. We will confirm '
        'availability, lead time and pricing for delivery in India.</p>\n'
        '      <a class="amp-cta-btn" href="%(rel)sconnect.html" style="display:inline-flex;'
        'align-items:center;gap:10px;background:%(amber)s;color:%(navy)s;font-family:%(fb)s;'
        'font-weight:700;font-size:0.98rem;padding:14px 30px;border-radius:7px;'
        'transition:background .25s,box-shadow .3s,transform .3s cubic-bezier(0.22,0.61,0.36,1)">'
        'Connect <span class="amp-arrow">&rarr;</span></a>\n'
        '    </div>\n'
        '  </section>\n'
        % {"rel": rel, "fh": F_HEAD, "fb": F_BODY, "amber": AMBER, "navy": NAVY})


def index_body(data, logo_html, cats, counts):
    body = (
        '\n  <!-- ================= HERO ================= -->\n'
        '  <section class="amp-hero" style="position:relative;overflow:hidden;min-height:560px;'
        'padding-top:76px;display:flex;align-items:center">\n'
        '    <img src="assets/hero-products.webp" alt="Virongy Biosciences virology research reagents" '
        'style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;'
        'object-position:70% center;display:block;z-index:0">\n'
        '    <div style="position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,'
        'rgba(8,17,29,0.97) 0%,rgba(8,17,29,0.92) 34%,rgba(8,17,29,0.5) 68%,'
        'rgba(8,17,29,0.18) 100%)"></div>\n'
        '    <div style="position:absolute;inset:0;z-index:1;background:linear-gradient(0deg,'
        'rgba(8,17,29,0.6) 0%,rgba(8,17,29,0) 42%)"></div>\n'
        '    <div style="position:relative;z-index:2;max-width:1240px;margin:0 auto;'
        'padding:52px 32px;width:100%">\n'
        '      <div style="max-width:720px">\n'
        '        <div style="font-family:' + F_MONO + ';font-size:0.78rem;letter-spacing:0.24em;'
        'color:' + AMBER + ';text-transform:uppercase;margin-bottom:20px">'
        'Exclusive Distributor in India</div>\n'
        '        ' + logo_html + '\n'
        '        <h1 class="amp-h1" style="font-family:' + F_HEAD + ';font-weight:800;'
        'font-size:clamp(2rem,3.9vw,3.3rem);line-height:1.05;letter-spacing:-0.01em;'
        'text-transform:uppercase;margin:0 0 20px">'
        '<span style="color:#fff">Virongy Biosciences </span>'
        '<span style="color:' + AMBER + '">in India.</span></h1>\n'
        '        <p style="color:#c4cede;font-size:1.1rem;line-height:1.62;margin:0 0 28px;'
        'max-width:620px">Ampbio is the exclusive distributor in India for Virongy Biosciences, '
        'USA &mdash; pseudoviruses and single-cycle viruses, neutralization assay kits, viral '
        'protein expression vectors, transduction and transfection reagents, reporter cell lines '
        'and custom vector design.</p>\n'
        '        ' + category_nav(cats, counts) + '\n'
        '      </div>\n'
        '    </div>\n'
        '  </section>\n')
    products = data["products"]
    body += "".join(
        index_section(c, [p for p in products if p["category"] == c], i % 2 == 1)
        for i, c in enumerate(cats))
    body += enquiry_band("")
    body += ('\n  <section style="background:%s;padding:0 0 46px">\n'
             '    <div style="max-width:1240px;margin:0 auto;padding:0 32px">\n'
             '      <p style="color:#8b98ab;font-size:0.82rem;line-height:1.6;margin:0;'
             'max-width:780px">Catalogue as of %s. Product names, specifications and '
             'availability are those of Virongy Biosciences and are subject to change &mdash; '
             'please confirm current details with us. All products are for research use only.</p>\n'
             '    </div>\n  </section>\n' % (NAVY, data["generated"]))
    return body


def product_body(p, detail_html, crumb, pn, rel, quote_href):
    return (
        '\n  <section style="background:%(navy)s;padding:116px 0 64px">\n'
        '    <div style="max-width:1240px;margin:0 auto;padding:0 32px">\n'
        '      %(crumb)s\n'
        '      <div class="amp-prod" style="display:grid;grid-template-columns:'
        'minmax(0,0.85fr) minmax(0,1.15fr);gap:48px;align-items:start">\n'
        '        <div class="amp-prod-media" style="position:sticky;top:100px">\n'
        '          <div style="position:relative;border-radius:14px;overflow:hidden;'
        'background:%(card)s;border:1px solid %(hair)s;aspect-ratio:4/3">'
        '<img src="%(img)s" alt="%(alt)s" style="position:absolute;inset:0;width:100%%;'
        'height:100%%;object-fit:cover;display:block"></div>\n'
        '          <div style="font-family:%(fm)s;font-size:0.64rem;letter-spacing:0.14em;'
        'text-transform:uppercase;color:#8b98ab;margin-top:14px;line-height:1.6">'
        'Supplied in India by Ampbio &middot; Research use only</div>\n'
        '        </div>\n'
        '        <div>\n'
        '          <div style="font-family:%(fm)s;font-size:0.7rem;letter-spacing:0.18em;'
        'text-transform:uppercase;color:%(amber)s;margin-bottom:12px">%(cat)s</div>\n'
        '          <h1 style="font-family:%(fh)s;font-weight:800;'
        'font-size:clamp(1.7rem,3.2vw,2.6rem);line-height:1.08;letter-spacing:-0.01em;'
        'color:#fff;margin:0 0 16px">%(name)s</h1>\n'
        '          <p style="color:#c4cede;font-size:1rem;line-height:1.68;margin:0">%(summary)s</p>\n'
        '          %(detail)s\n'
        '          <a class="amp-quote" href="%(quote)s" style="margin-top:28px;'
        'display:inline-flex;align-items:center;gap:9px;background:%(amber)s;color:%(navy)s;'
        'font-family:%(fb)s;font-weight:700;font-size:0.95rem;padding:13px 28px;'
        'border-radius:7px;transition:background .2s">Request a quote '
        '<span class="amp-arrow">&rarr;</span></a>\n'
        '          %(pn)s\n'
        '        </div>\n'
        '      </div>\n'
        '    </div>\n'
        '  </section>\n' % {
            "navy": NAVY, "card": CARD, "hair": HAIRLINE, "fm": F_MONO, "fh": F_HEAD,
            "fb": F_BODY, "amber": AMBER, "crumb": crumb,
            "img": esc(rel + p["image"]), "alt": esc(p["name"]),
            "cat": esc(p["category"]), "name": esc(p["name"]),
            "summary": esc(p["summary"]), "detail": detail_html,
            "quote": esc(quote_href), "pn": pn})


def product_jsonld(p, url):
    import json
    data = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": p["name"],
        "description": p["summary"],
        "category": p["category"],
        "image": "%s/%s" % (SITE, p["image"]),
        "url": url,
        "brand": {"@type": "Brand", "name": "Virongy Biosciences"},
        "manufacturer": {"@type": "Organization", "name": "Virongy Biosciences",
                         "url": "https://virongy.com"},
    }
    return ('\n<script type="application/ld+json">%s</script>'
            % json.dumps(data, ensure_ascii=False))
