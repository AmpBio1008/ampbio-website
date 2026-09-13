# -*- coding: utf-8 -*-
"""
Stamp styles.css and app.js with a content hash in every page.

  python _build/version_assets.py        (run last, after the other builders)

Why this exists: GitHub Pages serves everything with Cache-Control max-age=600,
and each file expires on its own clock. So after a deploy a returning visitor
could hold a fresh index.html and a ten-minute-old styles.css. That is not
cosmetic - the browse menu is injected by app.js and positioned entirely by
CSS, so with the old stylesheet .amp-mm-mount falls back to position:static,
the 36 KB panel renders inline in the page flow and the header collapses.

Adding ?v=<hash> means new HTML can only ever request the stylesheet and script
that were built with it; the old ones stay cached under their old URL, harmless.
app.js reads the same hash back off its own src and appends it to the menu.html
request, so the menu fragment cannot go stale either.
"""
import hashlib, io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
ASSETS = ["styles.css", "app.js", "menu.html"]
ROOT_PAGES = ["index.html", "products.html", "scientific-platforms.html",
              "support-training.html", "about.html", "connect.html", "virongy.html",
              "privacy-policy.html", "terms-of-use.html", "disclaimer.html"]


def all_pages():
    out = list(ROOT_PAGES)
    d = os.path.join(SITE, "virongy")
    if os.path.isdir(d):
        out += ["virongy/" + f for f in sorted(os.listdir(d)) if f.endswith(".html")]
    return out


def main():
    h = hashlib.sha1()
    for a in ASSETS:
        p = os.path.join(SITE, a)
        if os.path.exists(p):
            h.update(io.open(p, "rb").read())
    ver = h.hexdigest()[:8]

    changed = 0
    for page in all_pages():
        p = os.path.join(SITE, page)
        s = io.open(p, encoding="utf-8").read()
        before = s
        # keep whatever ../ prefix the page already uses
        s = re.sub(r'href="((?:\.\./)?)styles\.css(?:\?v=[0-9a-f]+)?"',
                   lambda m: 'href="%sstyles.css?v=%s"' % (m.group(1), ver), s)
        s = re.sub(r'src="((?:\.\./)?)app\.js(?:\?v=[0-9a-f]+)?"',
                   lambda m: 'src="%sapp.js?v=%s"' % (m.group(1), ver), s)
        if s != before:
            io.open(p, "w", encoding="utf-8", newline="").write(s)
            changed += 1

    print("asset version      %s  (%d pages stamped)" % (ver, changed))
    return ver


if __name__ == "__main__":
    main()
