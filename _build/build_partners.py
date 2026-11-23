# -*- coding: utf-8 -*-
"""
"Our Partners" band directly under the homepage hero: one card per partner
with its logo, Ampbio's status (exclusive / authorised distributor in India),
what the range covers, and a link to it.

  python _build/build_partners.py           (run from the site/ directory)

Writes index.html between the PARTNERS-BAND markers. Product counts are read
from the catalogues, so they stay right as ranges grow. Run after the three
range builders.
"""
import io, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_virongy import (HERE, AMBER, NAVY, CARD, HAIRLINE, F_HEAD, F_MONO, esc, read,
                           write, replace_block)

# In the order of the hero rows. Status words come from the agreements:
# Virongy and Sepflow exclusive, Jena authorised.
PARTNERS = [
    ("virongy-products.json", "Virongy Biosciences", "USA", "assets/virongy-logo.webp",
     "Exclusive", "Pseudoviruses, neutralization assay kits, viral protein expression "
     "vectors and transduction reagents.", "virongy.html"),
    ("jena-products.json", "Jena Bioscience", "Germany", "assets/jena-logo.svg",
     "Authorised", "Nucleotides, click-chemistry nucleosides, dNTPs and Quantifoil® "
     "cryo-EM grids.", "jena.html"),
    ("sepflow-products.json", "Sepflow", "China", "assets/sepflow-logo.webp",
     "Exclusive", "Chromatography and protein purification systems, ChromX software, "
     "pumps and valve modules.", "sepflow.html"),
]


def card(name, country, logo, kind, blurb, href, n):
    return (
        '\n        <a class="amp-platform amp-partner" href="%(href)s" style="display:flex;'
        'flex-direction:column;align-items:flex-start;gap:14px;background:%(card)s;'
        'border:1px solid %(hair)s;border-radius:15px;padding:24px 26px 22px;'
        'text-decoration:none">\n'
        '          <span style="display:inline-flex;align-items:center;padding:9px 14px;'
        'border-radius:10px;background:linear-gradient(158deg,#f7fafd 0%%,#dfe7f1 100%%);'
        'box-shadow:0 0 0 1px rgba(253,157,5,0.42)"><img src="%(logo)s" alt="%(name)s" '
        'style="height:30px;width:auto;display:block"></span>\n'
        '          <span class="amp-partner-status" style="font-family:%(fm)s;font-size:0.72rem;letter-spacing:0.16em;'
        'text-transform:uppercase;color:%(amber)s;line-height:1.5">%(kind)s Distributor '
        'in India</span>\n'
        '          <span style="color:#9fabbd;font-size:0.95rem;line-height:1.6">'
        '<span style="color:#fff;font-weight:700">%(name)s</span>, %(country)s. '
        '%(blurb)s</span>\n'
        '          <span style="margin-top:auto;color:%(amber)s;font-weight:700;'
        'font-size:0.9rem">View %(n)d products <span class="amp-arrow">&rarr;</span></span>\n'
        '        </a>' % {
            "href": href, "card": CARD, "hair": HAIRLINE, "logo": logo, "name": esc(name),
            "fm": F_MONO, "amber": AMBER, "kind": kind, "country": country,
            "blurb": esc(blurb), "n": n})


def build_band():
    cards = []
    for fname, name, country, logo, kind, blurb, href in PARTNERS:
        path = os.path.join(HERE, fname)
        if not os.path.exists(path):
            continue
        n = len(json.load(io.open(path, encoding="utf-8"))["products"])
        cards.append(card(name, country, logo, kind, blurb, href, n))
    return (
        '\n  <section style="background:%(navy)s;padding:56px 0 60px">\n'
        '    <div style="max-width:1240px;margin:0 auto;padding:0 32px">\n'
        '      <div style="display:flex;align-items:baseline;justify-content:space-between;'
        'gap:20px;flex-wrap:wrap;margin:0 0 26px">\n'
        '        <h2 style="font-family:%(fh)s;font-weight:700;font-size:clamp(1.5rem,2.6vw,2.2rem);'
        'line-height:1.1;letter-spacing:-0.01em;text-transform:uppercase;color:#fff;margin:0">'
        'Our <span style="color:%(amber)s">partners.</span></h2>\n'
        '        <div style="font-family:%(fm)s;font-size:0.74rem;letter-spacing:0.18em;'
        'color:#8b98ab;text-transform:uppercase">Distribution in India</div>\n'
        '      </div>\n'
        '      <div class="amp-partners" style="display:grid;grid-template-columns:repeat(3,1fr);'
        'gap:20px">%(cards)s\n'
        '      </div>\n'
        '    </div>\n'
        '  </section>\n  ' % {"navy": NAVY, "fh": F_HEAD, "fm": F_MONO, "amber": AMBER,
                              "cards": "".join(cards)})


def main():
    write("index.html", replace_block(read("index.html"), "PARTNERS-BAND", build_band()))
    print("index.html        partners band, %d partners" % len(PARTNERS))


if __name__ == "__main__":
    main()
