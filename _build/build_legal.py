# -*- coding: utf-8 -*-
"""
Generate the three legal pages and wire the footer links that point at them.

  python _build/build_legal.py           (run from the site/ directory)

Text lives in legal_content.py. Header and footer are lifted from products.html
like every other generated page, so they stay in step with the rest of the site.
The footer's Privacy Policy / Terms of Use / Disclaimer / Sitemap links were
href="#" placeholders on all pages; this points them at real files.
"""
import io, os, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pages          # noqa: E402
import legal_content  # noqa: E402

AMBER = "#FD9D05"
NAVY = "#0a1524"
CREAM = "#fdecdd"
F_HEAD = pages.F_HEAD
F_MONO = pages.F_MONO

LINKS = [("Privacy Policy", "privacy-policy.html"),
         ("Terms of Use", "terms-of-use.html"),
         ("Disclaimer", "disclaimer.html"),
         ("Sitemap", "sitemap.xml")]


def read(p):
    return io.open(os.path.join(SITE, p), encoding="utf-8").read()


def write(p, s):
    io.open(os.path.join(SITE, p), "w", encoding="utf-8", newline="").write(s)


def chrome():
    src = read("products.html")
    header = pages.esc  # placeholder to keep linters quiet
    header = src[src.index("  <!-- ================= HEADER ================= -->"):
                 src.index("  </header>") + len("  </header>")]
    header = re.sub(r'<span class="amp-mm">(.*?)<span class="amp-mm-mount"[^>]*>'
                    r'</span></span>', r"\1", header, flags=re.S)
    header = header.replace('<a class="amp-mm-m" ', '<a ')
    footer = src[src.index("  <!-- ================= FOOTER ================= -->"):
                 src.index("  </footer>") + len("  </footer>")]
    return header, footer


def render_blocks(blocks):
    out = []
    for b in blocks:
        if isinstance(b, list):
            items = "".join(
                '<li style="display:flex;gap:11px;align-items:flex-start;margin-bottom:9px">'
                '<span style="flex:0 0 5px;width:5px;height:5px;border-radius:50%%;'
                'background:%s;margin-top:9px"></span><span>%s</span></li>' % (AMBER, t)
                for t in b)
            out.append('<ul style="list-style:none;margin:0 0 18px;padding:0;'
                       'color:#3a4048;font-size:1rem;line-height:1.7">%s</ul>' % items)
        else:
            out.append('<p style="color:#3a4048;font-size:1rem;line-height:1.75;'
                       'margin:0 0 18px">%s</p>' % b)
    return "".join(out)


def build(page, header, footer, updated):
    slug, title, desc, lead, sections = page

    toc = "".join(
        '<li style="margin-bottom:7px"><a href="#%s" style="color:#59636f;'
        'font-size:0.94rem">%s</a></li>' % (pages.anchor(h), h)
        for h, _ in sections)

    body_sections = "".join(
        '\n        <section id="%s" style="margin-bottom:34px">\n'
        '          <h2 style="font-family:%s;font-weight:700;font-size:1.35rem;'
        'line-height:1.2;text-transform:uppercase;color:#1a1c1e;margin:0 0 14px">%s</h2>\n'
        '          %s\n        </section>' % (pages.anchor(h), F_HEAD, h, render_blocks(bs))
        for h, bs in sections)

    body = (
        '\n  <!-- ================= HERO ================= -->\n'
        '  <section style="background:%(navy)s;padding:124px 0 56px">\n'
        '    <div style="max-width:1240px;margin:0 auto;padding:0 32px">\n'
        '      <div style="font-family:%(fm)s;font-size:0.78rem;letter-spacing:0.24em;'
        'color:%(amber)s;text-transform:uppercase;margin-bottom:18px">Legal</div>\n'
        '      <h1 style="font-family:%(fh)s;font-weight:800;'
        'font-size:clamp(2rem,3.6vw,3rem);line-height:1.06;letter-spacing:-0.01em;'
        'text-transform:uppercase;color:#fff;margin:0 0 18px">%(title)s</h1>\n'
        '      <p style="color:#c4cede;font-size:1.08rem;line-height:1.65;margin:0;'
        'max-width:640px">%(lead)s</p>\n'
        '    </div>\n'
        '  </section>\n'
        '\n  <section style="background:%(cream)s;padding:56px 0 72px">\n'
        '    <div class="amp-legal-wrap" style="max-width:1240px;margin:0 auto;'
        'padding:0 32px;display:grid;grid-template-columns:minmax(0,230px) minmax(0,1fr);'
        'gap:52px;align-items:start">\n'
        '      <nav class="amp-legal-toc" aria-label="On this page" '
        'style="position:sticky;top:100px">\n'
        '        <div style="font-family:%(fm)s;font-size:0.66rem;letter-spacing:0.16em;'
        'text-transform:uppercase;color:#8b6a2f;margin-bottom:12px">On this page</div>\n'
        '        <ul style="list-style:none;margin:0;padding:0">%(toc)s</ul>\n'
        '      </nav>\n'
        '      <div>\n'
        '%(sections)s\n'
        '        <p style="color:#8b6a2f;font-size:0.86rem;margin:30px 0 0;'
        'padding-top:18px;border-top:1px solid rgba(10,20,40,0.12)">'
        'Last updated %(updated)s.</p>\n'
        '      </div>\n'
        '    </div>\n'
        '  </section>\n' % {
            "navy": NAVY, "cream": CREAM, "amber": AMBER, "fm": F_MONO, "fh": F_HEAD,
            "title": title, "lead": lead, "toc": toc, "sections": body_sections,
            "updated": updated})

    return pages.shell("%s | Ampbio" % title, desc,
                       "https://amps.bio/%s" % slug, body, "", header, footer)


def wire_footer_links():
    """Point the four footer placeholders at real destinations, everywhere."""
    import glob
    targets = (["index.html", "products.html", "scientific-platforms.html",
                "support-training.html", "about.html", "connect.html", "virongy.html"]
               + [p[0] for p in legal_content.PAGES]
               + sorted(glob.glob(os.path.join(SITE, "virongy", "*.html"))))
    n = 0
    for t in targets:
        rel = "../" if os.path.sep + "virongy" + os.path.sep in t else ""
        path = t if os.path.isabs(t) else os.path.join(SITE, t)
        if not os.path.exists(path):
            continue
        s = io.open(path, encoding="utf-8").read()
        before = s
        for label, href in LINKS:
            s = re.sub(r'(<a class="amp-legal" href=")[^"]*("[^>]*>%s</a>)' % re.escape(label),
                       lambda m: m.group(1) + rel + href + m.group(2), s)
        if s != before:
            io.open(path, "w", encoding="utf-8", newline="").write(s)
            n += 1
    return n


def main():
    updated = time.strftime("%d %B %Y")
    header, footer = chrome()
    for page in legal_content.PAGES:
        write(page[0], build(page, header, footer, updated))
        print("  %-24s %s" % (page[0], page[1]))
    print("footer links wired on %d pages" % wire_footer_links())


if __name__ == "__main__":
    main()
