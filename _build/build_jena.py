# -*- coding: utf-8 -*-
"""
Generate the Jena Bioscience row of the homepage hero strip from
_build/jena-featured.json.

  python _build/build_jena.py               (run from the site/ directory)

Writes index.html between the JENA-HERO-STRIP markers. Images come from
_build/fetch_jena.py. Nothing here links to jenabioscience.com: until amps.bio
has Jena product pages, each tile opens the Connect form pre-filled with the
product and its catalogue number.
"""
import io, json, os, sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_virongy import HERE, F_HEAD, HAIRLINE, esc, read, write, replace_block

# Keeps the two rows moving at the same speed: the Virongy track has 11 tiles
# on a 72s loop (styles.css), this one has fewer.
VIRONGY_TILES, VIRONGY_SECONDS = 11, 72


def tile(p):
    label = "%s (%s)" % (p["name"], p["sku"])
    # Structural formulas are line art on white, so every Jena tile is a white
    # plate with the image contained rather than cropped to fill.
    return (
        '\n          <a class="amp-mq-tile amp-mq-plate" href="connect.html?product=%s" '
        'title="%s" style="flex:0 0 auto;width:330px;display:flex;flex-direction:column;gap:9px;'
        'text-decoration:none"><div style="position:relative;height:222px;border-radius:12px;'
        'overflow:hidden;background:#fff;border:1px solid %s"><img src="assets/jena-%s.webp" '
        'alt="%s" style="position:absolute;inset:0;width:100%%;height:100%%;object-fit:contain;'
        'padding:7%% 9%%;box-sizing:border-box;display:block"></div>'
        '<div style="font-family:%s;font-weight:700;font-size:1rem;line-height:1.2;'
        'color:#dbe3ee">%s</div></a>'
        % (quote(label), esc(p["name"]), HAIRLINE, esc(p["slug"]), esc(p["name"]), F_HEAD,
           esc(p["name"])))


def build_hero_strip(data):
    feats = data["featured"]
    track = "".join(tile(p) for p in feats)
    seconds = round(VIRONGY_SECONDS * len(feats) / VIRONGY_TILES)
    return (
        '\n      <div class="amp-marquee" style="position:relative;overflow:hidden">\n'
        '        <div class="amp-marquee-track" style="display:flex;gap:18px;'
        'width:max-content;padding:0 10px;animation-duration:%ds">%s%s\n'
        '        </div>\n'
        '      </div>\n    '
        % (seconds, track, track))


def main():
    data = json.load(io.open(os.path.join(HERE, "jena-featured.json"), encoding="utf-8"))
    home = read("index.html")
    write("index.html", replace_block(home, "JENA-HERO-STRIP", build_hero_strip(data)))
    print("index.html: Jena hero row, %d tiles" % len(data["featured"]))


if __name__ == "__main__":
    main()
