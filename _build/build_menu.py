# -*- coding: utf-8 -*-
"""
Write menu.html (the shared Virongy browse panel) and wire the header of every
page to it.

  python _build/build_menu.py            (run from the site/ directory)

The panel markup is ~41 KB. Inlining it into seven pages, twice over so the
mobile drawer has its own copy, would add over half a megabyte of HTML to the
site for a menu most visitors never open - so it lives in one file that app.js
fetches the first time someone opens the menu, and the browser then caches it
for every other page.
"""
import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import menu  # noqa: E402

ROOT_PAGES = ["index.html", "products.html", "scientific-platforms.html",
              "support-training.html", "about.html", "connect.html", "virongy.html"]


def all_pages():
    """Root pages plus every generated product page under virongy/."""
    out = list(ROOT_PAGES)
    d = os.path.join(SITE, "virongy")
    if os.path.isdir(d):
        out += ["virongy/" + f for f in sorted(os.listdir(d)) if f.endswith(".html")]
    return out

# The desktop nav's Products link, on the active page and on the others.
DESKTOP = re.compile(
    r'(<a(?:\s+data-navlink)?\s+href="(?:\.\./)?products\.html"[^>]*>Products</a>)')
# The mobile drawer's Products link. The "padding:12px 0" is what distinguishes
# it from the desktop link, which on products.html itself carries the same
# amber colour and would otherwise match first.
MOBILE = re.compile(
    r'(<a href="(?:\.\./)?products\.html" style="color:#(?:FD9D05|eef2f8)[^"]*'
    r'padding:12px 0[^"]*">Products</a>)')


def read(p):
    return io.open(os.path.join(SITE, p), encoding="utf-8").read()


def write(p, s):
    io.open(os.path.join(SITE, p), "w", encoding="utf-8", newline="").write(s)


def main():
    data = json.load(io.open(os.path.join(HERE, "virongy-products.json"),
                             encoding="utf-8"))
    bad, unfiled = menu.check(data["products"])
    if bad:
        raise SystemExit("taxonomy errors:\n  " + "\n  ".join(bad))

    panel = menu.build(data["products"], data["categories"])
    write("menu.html", panel + "\n")
    print("menu.html          %.1f KB, %d product links, %d branches"
          % (len(panel) / 1024.0, panel.count("virongy.html#"),
             panel.count("amp-mm-has")))

    for page in all_pages():
        s = read(page)
        # Unwire first, so re-running is idempotent no matter what a previous
        # (or buggier) run left behind.
        s = re.sub(r'<span class="amp-mm">(.*?)<span class="amp-mm-mount"[^>]*>'
                   r'</span></span>', r"\1", s, flags=re.S)
        s = s.replace('<a class="amp-mm-m" ', '<a ')
        m = DESKTOP.search(s)
        if not m:
            print("  SKIP (no desktop Products link): %s" % page)
            continue
        s = s[:m.start()] + menu.nav_item(m.group(1)) + s[m.end():]

        mm = MOBILE.search(s)
        if mm:
            link = mm.group(1).replace("<a ", '<a class="amp-mm-m" ', 1)
            s = s[:mm.start()] + link + s[mm.end():]
        write(page, s)
        print("  wired %s" % page)

    print("\n%d products filed under a virus family, %d type-only"
          % (len(data["products"]) - len(unfiled), len(unfiled)))


if __name__ == "__main__":
    main()
