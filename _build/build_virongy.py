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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pages

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


# Product pages live in virongy/, one level below the root pages, so every
# relative link in shared markup has to be lifted by one directory.
def reroot(html, rel):
    """Prefix relative href/src values with `rel` (e.g. '../')."""
    if not rel:
        return html
    def fix(m):
        attr, url = m.group(1), m.group(2)
        if re.match(r"^(https?:|//|/|#|mailto:|tel:|data:)", url):
            return m.group(0)
        return '%s="%s%s"' % (attr, rel, url)
    return re.sub(r'\b(href|src)="([^"]+)"', fix, html)


def product_url(slug, in_virongy_dir):
    """Link to a product page from a root page or from a sibling product page."""
    return ("%s.html" % slug) if in_virongy_dir else ("virongy/%s.html" % slug)


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


def _chrome():
    """Header and footer, lifted verbatim from products.html so the Virongy
    pages can never drift from the rest of the site.

    The browse-menu wiring is stripped out again: products.html already carries
    it from the last build_menu run, and copying it here would bake one page's
    wiring into another's markup. build_menu.py re-adds it afterwards, to every
    page, from one place."""
    src = read("products.html")
    header = slice_between(src, "  <!-- ================= HEADER ================= -->",
                           "  </header>")
    header = re.sub(r'<span class="amp-mm">(.*?)<span class="amp-mm-mount"[^>]*>'
                    r'</span></span>', r"\1", header, flags=re.S)
    header = header.replace('<a class="amp-mm-m" ', '<a ')
    return (header,
            slice_between(src, "  <!-- ================= FOOTER ================= -->",
                          "  </footer>"))


def _exists(path):
    return os.path.exists(os.path.join(SITE, path.replace("/", os.sep)))


def build_index(data):
    header, footer = _chrome()
    products = data["products"]
    counts = {c: sum(1 for p in products if p["category"] == c)
              for c in data["categories"]}
    cats = [c for c in data["categories"] if counts.get(c)]

    title = "Virongy Biosciences — Exclusive Distributor for India | Ampbio"
    desc = ("Exclusive distributor in India for Virongy Biosciences, USA: %d products "
            "across pseudoviruses, neutralization kits and expression vectors."
            % len(products))

    body = pages.index_body(data, logo(70, "0 0 26px"), cats, counts)
    return pages.shell(title, desc, "https://amps.bio/virongy.html", body, "",
                       header, footer)


def build_product(p, data):
    header, footer = _chrome()
    rel = "../"
    header, footer = reroot(header, rel), reroot(footer, rel)

    siblings = [q for q in data["products"] if q["category"] == p["category"]]
    i = siblings.index(p)
    prev = siblings[i - 1] if i else None
    nxt = siblings[i + 1] if i + 1 < len(siblings) else None
    others = [q for q in siblings if q is not p][:4]

    detail = []
    if p["applications"]:
        detail.append(pages.detail_block("Applications", pages.bullet_list(p["applications"])))
    if p["features"]:
        detail.append(pages.detail_block("Key features", pages.bullet_list(p["features"])))
    if p["contents"]:
        detail.append(pages.detail_block("Kit contents", pages.bullet_list(p["contents"])))
    for opt in p["options"]:
        detail.append(pages.detail_block(opt["label"], pages.option_pills(opt["values"])))
    detail.append(pages.doc_buttons(DOC_MAP.get(p["slug"], []), rel, _exists))

    url = "https://amps.bio/virongy/%s.html" % p["slug"]
    body = pages.product_body(
        p, "".join(detail), pages.breadcrumb(p, rel),
        pages.prev_next(prev, nxt), rel,
        "%sconnect.html?product=%s" % (rel, quote(p["name"])))
    body += pages.related(others, p["category"])
    body += pages.enquiry_band(rel)

    return pages.shell(
        "%s | Virongy Biosciences — Ampbio India" % p["name"],
        pages.meta_description(p), url, body, rel, header, footer,
        extra_head=pages.product_jsonld(p, url))


def build_marquee(data):
    by = {p["slug"]: p for p in data["products"]}
    feats = [by[s] for s in data["featured"] if s in by]
    tiles = []
    for p in feats:
        tiles.append(
            '\n          <a class="amp-mq-tile" href="virongy/%s.html" style="flex:0 0 auto;'
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
        'line-height:1.35;max-width:100%%;'
        'transition:background .25s,box-shadow .3s,transform .3s cubic-bezier(0.22,0.61,0.36,1)">'
        'Virongy Biosciences &ndash; Virological Research Tools and Platforms '
        '<span class="amp-arrow">&rarr;</span></a>\n'
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
        'border-radius:6px;transition:background .2s;line-height:1.35;max-width:100%%">'
        'Virongy Biosciences &ndash; Virological Research Tools and Platforms</a>\n'
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


ROOT_URLS = [("", "1.0"), ("products.html", "0.9"), ("virongy.html", "0.9"),
             ("scientific-platforms.html", "0.9"), ("support-training.html", "0.9"),
             ("about.html", "0.8"), ("connect.html", "0.8")]


def write_sitemap(data):
    urls = list(ROOT_URLS) + [("virongy/%s.html" % p["slug"], "0.7")
                              for p in data["products"]]
    body = "".join(
        "  <url>\n    <loc>https://amps.bio/%s</loc>\n"
        "    <changefreq>monthly</changefreq>\n    <priority>%s</priority>\n  </url>\n"
        % (loc, pri) for loc, pri in urls)
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % body)
    return len(urls)


def main():
    data = json.load(io.open(CATALOGUE, encoding="utf-8"))
    products = data["products"]

    os.makedirs(os.path.join(SITE, "virongy"), exist_ok=True)
    write("virongy.html", build_index(data))
    for p in products:
        write("virongy/%s.html" % p["slug"], build_product(p, data))

    write("index.html", replace_block(read("index.html"), "VIRONGY-MARQUEE", build_marquee(data)))
    write("products.html", replace_block(read("products.html"), "VIRONGY-BANNER", build_banner(data)))

    for page in ("virongy.html", "index.html", "products.html"):
        check(page)
    for p in products[:]:
        check("virongy/%s.html" % p["slug"])

    n_urls = write_sitemap(data)
    have = sum(len(v) for v in DOC_MAP.values())
    print("virongy.html      range index, %d categories" % len(data["categories"]))
    print("virongy/*.html    %d product pages" % len(products))
    print("index.html        marquee, %d featured products" % len(data["featured"]))
    print("products.html     distributor banner")
    print("sitemap.xml       %d URLs" % n_urls)
    print("documents         %d download buttons across %d products "
          "(see assets/docs/MANIFEST.txt)" % (have, len(DOC_MAP)))


if __name__ == "__main__":
    main()
