# -*- coding: utf-8 -*-
"""
The Virongy browse menu: taxonomy + HTML.

Virongy's own site has a five-level hover menu. This rebuilds the same shape
from our catalogue rather than copying their markup, so it stays in step with
the catalogue automatically and covers all 52 products.

(An earlier version of this note claimed their menu was broken. That was wrong
and is corrected here: all 52 of their product links resolve, seven of them via
301 redirects to renamed pages. Their menu omits 3 of their 53 products.)

Every product is reachable two ways, as on Virongy's site:
  Virus-Specific Tools -> family -> virus -> product
  <product type>       -> product

A product legitimately appears under several viruses when it covers several
(the Betacoronavirus pseudovirus covers SARS-CoV, SARS-CoV-2 and MERS-CoV).

Families are assigned explicitly rather than by matching product names: this
drives customer-facing navigation for virology reagents, and a wrong guess
would file a reagent under the wrong pathogen.
"""

# family -> [(virus or None, [product slugs])]
FAMILIES = [
    ("Coronaviridae", [
        ("SARS-CoV-2", ["coronavirus-alpha-pseudovirus", "sars-cov-2-pseudoviruses",
                        "sars-cov-2-pseudoviral-neutralization-assay-kit",
                        "sars-cov-2-rapid-neutralizing-antibody-kit",
                        "sars-cov-2-protein-expression-vectors",
                        "sars-cov-2-neutralizing-antibody"]),
        ("SARS-CoV", ["coronavirus-alpha-pseudovirus", "sars-cov-2-pseudoviruses",
                      "sars-cov-neutralization-assay-kit"]),
        ("MERS-CoV", ["coronavirus-alpha-pseudovirus", "sars-cov-2-pseudoviruses",
                      "mers-cov-pseudoviral-neutralization-assay-kit"]),
    ]),
    ("Filoviridae", [
        ("Ebolavirus", ["filoviruses-alpha-pseudovirus",
                        "ebola-pseudoviral-neutralization-assay-kit",
                        "filoviral-protein-expression-vectors"]),
        ("Marburg Virus", ["filoviruses-alpha-pseudovirus",
                           "marburg-pseudoviral-neutralization-assay-kit",
                           "filoviral-protein-expression-vectors"]),
    ]),
    ("Bunyaviridae", [
        ("Crimean-Congo Haemorrhagic Fever Virus", ["bunyavirus-protein-expression-vectors"]),
        ("Rift Valley Fever Virus", ["bunyaviridae-pseudoviruses",
                                     "bunyavirus-protein-expression-vectors"]),
    ]),
    ("Hantaviridae", [
        ("Andes Virus", ["rapid-alpha-pseudoviruses-for-orthohantavirus",
                         "bunyaviridae-pseudoviruses",
                         "hantavirus-pseudoviral-neutralization-assay-kit"]),
    ]),
    ("Arenaviridae", [
        ("Lassa Virus", ["lassa-alpha-pseudovirus",
                         "lassa-pseudoviral-neutralization-assay-kit",
                         "arenaviral-protein-expression-vectors"]),
    ]),
    ("Flaviviridae", [
        ("Dengue Virus", ["flavivirus-protein-expression-vectors"]),
        ("Zika Virus", ["flavivirus-protein-expression-vectors"]),
    ]),
    ("Togaviridae", [
        ("Chikungunya Virus", ["pseudovirus-for-alphaviruses",
                               "pseudoviral-neutralization-assay-kits-for-togaviridae",
                               "togavirus-protein-expression-vectors"]),
        ("Semliki Forest Virus", ["pseudovirus-for-alphaviruses",
                                  "pseudoviral-neutralization-assay-kits-for-togaviridae",
                                  "togavirus-protein-expression-vectors"]),
        ("Equine Encephalitis Viruses (VEEV, EEEV)",
         ["pseudovirus-for-alphaviruses",
          "pseudoviral-neutralization-assay-kits-for-togaviridae"]),
    ]),
    ("Orthomyxoviridae (Influenza)", [
        (None, ["influenza-a-alpha-pseudoviruses",
                "influenza-a-pseudoviral-neutralization-assay-kit",
                "orthomyxovirus-protein-expression-vectors"]),
    ]),
    ("Paramyxoviridae (Nipah)", [
        (None, ["nipah-pseudovirus", "nipah-pseudoviral-neutralization-assay-kit",
                "nipah-protein-expression-vectors"]),
    ]),
    ("Rhabdoviridae (Rabies, VSV)", [
        ("Rabies Virus", ["rapid-alpha-pseudoviruses-for-rabies",
                          "rabies-neutralization-assay-kit"]),
        ("Vesicular Stomatitis Virus", ["vsv-g-pseudotyped-lentivirus"]),
    ]),
    ("Pneumoviridae (RSV)", [
        (None, ["pneumoviral-protein-expression-vectors"]),
    ]),
    ("Papillomaviridae (HPV)", [
        (None, ["pseudoviruses-for-human-papillomaviridae"]),
    ]),
    ("Hepadnaviridae (Hepatitis B)", [
        (None, ["hepadnavirus-protein-expression-vectors"]),
    ]),
    ("Retroviridae (HIV)", [
        (None, ["hiv-neutralization-assay-kit", "hiv-rev-dependent-reporter-cells",
                "r8-71-hiv-rcl-positive-control-virus"]),
    ]),
]

AMBER = "#FD9D05"
NAVY = "#0a1524"
PANEL = "#0d1c30"
HAIRLINE = "rgba(255,255,255,0.09)"
F_MONO = "'IBM Plex Mono',monospace"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def check(products):
    """Every slug in the taxonomy must exist, and every product must be filed."""
    known = {p["slug"] for p in products}
    used, bad = set(), []
    for fam, viruses in FAMILIES:
        for virus, slugs in viruses:
            for s in slugs:
                used.add(s)
                if s not in known:
                    bad.append("%s / %s -> unknown product %r" % (fam, virus, s))
    return bad, sorted(known - used)


def _leaf(p, pad):
    # Root-absolute: this fragment is shared by pages at the site root and by
    # product pages one level down, so a relative href cannot serve both.
    return ('<li><a href="/virongy/%s.html" style="display:block;padding:%s;'
            'color:#c4cede;font-size:0.86rem;line-height:1.35">%s</a></li>'
            % (esc(p["slug"]), pad, esc(p["name"])))


def _branch(label, inner, depth):
    """A row that opens a nested panel on hover (desktop) or tap (mobile).

    A panel holding only products is marked `amp-mm-leaf`: those may scroll
    when long, but a panel that has flyouts of its own must never get an
    overflow, or it becomes a clipping context and cuts its own children off.
    """
    leaf = "" if "amp-mm-has" in inner else " amp-mm-leaf"
    return ('<li class="amp-mm-has">'
            '<a href="#" class="amp-mm-toggle" aria-haspopup="true" aria-expanded="false" '
            'style="display:flex;align-items:center;justify-content:space-between;gap:12px;'
            'padding:9px 16px;color:#dbe3ee;font-size:0.88rem;line-height:1.3">'
            '<span>%s</span>'
            '<svg class="amp-mm-chev" width="13" height="13" viewBox="0 0 24 24" fill="none" '
            'stroke="%s" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
            '<polyline points="9 6 15 12 9 18"></polyline></svg></a>'
            '<ul class="amp-mm-panel amp-mm-d%d%s">%s</ul></li>'
            % (esc(label), AMBER, depth, leaf, inner))


def build(products, categories):
    """The whole menu as one <ul>. `products` is the catalogue list."""
    by = {p["slug"]: p for p in products}

    # --- Virus-Specific Tools -----------------------------------------
    # The virus sits inside the family panel as a heading rather than as a
    # fourth flyout. Four cascading columns do not fit: the nav is right of
    # centre, so the fourth column starts around x=1595 and runs off a
    # 1440px screen entirely. Grouping keeps it to three columns and is
    # easier to scan besides - the whole family is visible at once.
    fams = []
    for fam, viruses in FAMILIES:
        if len(viruses) == 1 and viruses[0][0] is None:
            inner = "".join(_leaf(by[s], "9px 16px") for s in viruses[0][1] if s in by)
        else:
            parts = []
            for virus, slugs in viruses:
                parts.append(
                    '<li class="amp-mm-grp" style="padding:11px 16px 5px;'
                    'font-family:%s;font-size:0.64rem;letter-spacing:0.14em;'
                    'text-transform:uppercase;color:%s">%s</li>'
                    % (F_MONO, AMBER, esc(virus)))
                parts.append("".join(_leaf(by[s], "7px 16px 7px 26px")
                                     for s in slugs if s in by))
            inner = "".join(parts)
        fams.append(_branch(fam, inner, 3))
    virus_tools = _branch("Virus-Specific Tools", "".join(fams), 2)

    # --- one branch per product type -----------------------------------
    types = []
    for cat in categories:
        items = [p for p in products if p["category"] == cat]
        if not items:
            continue
        leaves = "".join(_leaf(p, "9px 16px") for p in items)
        types.append(_branch(cat, leaves, 2))

    all_link = ('<li><a href="/virongy.html" style="display:block;padding:11px 16px;'
                'color:%s;font-weight:700;font-size:0.86rem;border-top:1px solid %s">'
                'View the full Virongy range &rarr;</a></li>' % (AMBER, HAIRLINE))

    head = ('<li class="amp-mm-head" style="padding:12px 16px 9px;font-family:%s;'
            'font-size:0.66rem;letter-spacing:0.16em;text-transform:uppercase;'
            'color:%s;border-bottom:1px solid %s">Virongy Biosciences &middot; '
            'Exclusive Distributor in India</li>' % (F_MONO, AMBER, HAIRLINE))

    return ('<ul class="amp-mm-panel amp-mm-d1">%s%s%s%s</ul>'
            % (head, virus_tools, "".join(types), all_link))


NAV_ITEM = """<span class="amp-mm">%(link)s<span class="amp-mm-mount" hidden></span></span>"""


def nav_item(link_html):
    """Wrap the header's Products link so the panel has somewhere to mount.
    The panel itself is fetched from menu.html on first use - inlining 41 KB of
    markup into all seven pages, twice over for mobile, would add half a
    megabyte to the site for a menu most visitors never open."""
    return NAV_ITEM % {"link": link_html}
