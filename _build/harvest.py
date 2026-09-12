# -*- coding: utf-8 -*-
"""
Harvest the Virongy Biosciences catalogue into a clean JSON file.

Source: virongy.com WooCommerce Store API + the rendered product pages.
PRICES ARE NEVER EXTRACTED - they are dropped at source so they cannot leak
into the generated amps.bio pages.

Run:  python harvest.py <out_dir>
Writes <out_dir>/virongy-products.json and <out_dir>/pages/*.html (cache).
"""
import json, os, re, sys, html, time, io
import urllib.request, urllib.parse

STORE_API = "https://virongy.com/wp-json/wc/store/v1/products?per_page=100"
UA = "Mozilla/5.0 (compatible; amps.bio catalogue build)"

# --- Ampbio category grouping -------------------------------------------
# Virongy's own taxonomy is per-virus-family and far too granular for a
# distributor catalogue page, so each product is mapped explicitly.
CATEGORY = {
    "Pseudoviruses & Single-Cycle Viruses": [
        "pseudovirus-for-alphaviruses", "vsv-g-pseudotyped-lentivirus",
        "sars-cov-2-pseudoviruses", "pseudoviruses-for-human-papillomaviridae",
        "lassa-alpha-pseudovirus", "bunyaviridae-pseudoviruses",
        "coronavirus-alpha-pseudovirus", "nipah-pseudovirus",
        "influenza-a-alpha-pseudoviruses",
        "rapid-alpha-pseudoviruses-for-orthohantavirus",
        "rapid-alpha-pseudoviruses-for-rabies", "filoviruses-alpha-pseudovirus",
    ],
    "Neutralization Assay Kits": [
        "ebola-pseudoviral-neutralization-assay-kit",
        "hiv-pseudoviral-neutralization-assay-kit-copy",
        "hantavirus-pseudoviral-neutralization-assay-kit",
        "influenza-a-pseudoviral-neutralization-assay-kit",
        "lassa-pseudoviral-neutralization-assay-kit",
        "mers-cov-pseudoviral-neutralization-assay-kit",
        "marburg-pseudoviral-neutralization-assay-kit",
        "nipah-pseudoviral-neutralization-assay-kit",
        "rabies-pseudoviral-neutralization-assay-kit-copy",
        "sars-cov-2-nuetralizing-kit",
        "sars-cov-pseudoviral-neutralization-assay-kit-2",
        "sars-cov-2-pseudoviral-neutralization-assay-kit",
        "pseudoviral-neutralization-assay-kits-for-togaviridae",
    ],
    "Viral Protein Expression Vectors": [
        "arenaviral-protein-expression-vectors",
        "bunyavirus-protein-expression-vectors",
        "filoviral-protein-expression-vectors",
        "flavivirus-protein-expression-vectors",
        "hepadnavirus-protein-expression-vectors",
        "orthomyxovirus-protein-expression-vectors",
        "nipah-protein-expression-vectors",
        "pneumoviral-protein-expression-vectors",
        "sars-cov-2-protein-expression-vectors",
        "togavirus-protein-expression-vectors",
    ],
    "Kits & Reagents": [
        "aav-extraction-and-maturation-kit", "intracellular-protein-staining-kit",
        "lentiplus-pseudovirus-assembly-and-infection-kit",
        "low-speed-viral-concentration-kit",
        "vader-%c2%adtrap-high-%c2%adpurity-plasmid-dna-purification-ki",
        "viral-rna-and-dna-extraction-kits",
    ],
    "Transduction & Transfection Reagents": [
        "cellment-cell-attachment-enhancer", "transfectin", "infectin",
    ],
    "Cell Lines, Antibodies & Controls": [
        "exomaxed", "hiv-rev-dependent-reporter-cells-copy",
        "r8-71-hiv-rcl-positive-control-virus", "sars-cov-2-neutralizing-antibody",
    ],
    "Custom Vector Design & Assembly": [
        "aav-vector-customization-tool", "custom-aav-assembly-purification",
        "lentiviral-vector-customization-tool", "retroviral-vector-customization-tool",
    ],
}
CATEGORY_ORDER = list(CATEGORY)
SLUG_TO_CATEGORY = {s: c for c, ss in CATEGORY.items() for s in ss}

# Some source slugs are URL-encoded or unwieldy; these become the local anchor id.
LOCAL_SLUG = {
    "vader-%c2%adtrap-high-%c2%adpurity-plasmid-dna-purification-ki":
        "vader-trap-plasmid-purification-kit",
    "hiv-rev-dependent-reporter-cells-copy": "hiv-rev-dependent-reporter-cells",
    "hiv-pseudoviral-neutralization-assay-kit-copy": "hiv-neutralization-assay-kit",
    "rabies-pseudoviral-neutralization-assay-kit-copy": "rabies-neutralization-assay-kit",
    "sars-cov-pseudoviral-neutralization-assay-kit-2": "sars-cov-neutralization-assay-kit",
    "sars-cov-2-nuetralizing-kit": "sars-cov-2-rapid-neutralizing-antibody-kit",
    "transfectin": "ez-fectin-dna-transfection-kit",
}

# Products with no product image of their own on virongy.com.
IMAGE_FALLBACK = {
    "aav-vector-customization-tool": "https://virongy.com/wp-content/uploads/2021/12/DNA-Expression-Vector-1-1-e1675966135547.png",
    "lentiviral-vector-customization-tool": "https://virongy.com/wp-content/uploads/2021/12/DNA-Expression-Vector-1-1-e1675966135547.png",
    "retroviral-vector-customization-tool": "https://virongy.com/wp-content/uploads/2021/12/DNA-Expression-Vector-1-1-e1675966135547.png",
}

# Homepage marquee selection, in display order.
# Chosen by the customer from "Virongy Products List.pdf"; the comment on each
# line is that document's serial number.
FEATURED = [
    "aav-vector-customization-tool",                        # 1
    "custom-aav-assembly-purification",                     # 6
    "transfectin",                                          # 8  EZ-Fectin
    "lentiplus-pseudovirus-assembly-and-infection-kit",     # 16
    "nipah-protein-expression-vectors",                     # 19
    "influenza-a-alpha-pseudoviruses",                      # 31
    "rapid-alpha-pseudoviruses-for-rabies",                 # 33
    "ebola-pseudoviral-neutralization-assay-kit",           # 42
    "hiv-pseudoviral-neutralization-assay-kit-copy",        # 44
    "nipah-pseudoviral-neutralization-assay-kit",           # 49
    "rabies-pseudoviral-neutralization-assay-kit-copy",     # 50
]

# Attribute labels that carry a price hint in Virongy's own naming.
ATTR_RENAME = {"Size and Price": "Size", "Kit Size": "Kit size",
               "Transfection Kit Size": "Kit size", "Preparations": "Kit size"}


def fetch(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read()
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(2)


def strip_noise(h):
    """Remove style/script blocks before any text extraction."""
    h = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", h or "")
    h = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", h)
    return h


def to_text(h):
    s = re.sub(r"(?is)<br\s*/?>", " ", h or "")
    s = re.sub(r"(?is)</(p|li|div|h[1-6])>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s)
    s = s.replace("­", "").replace("​", "")
    return re.sub(r"\s+", " ", s).strip()


def list_items_after(hblob, heading_words, limit=8, maxlen=160):
    """Pull <li> text from the first <ul>/<ol> that follows a heading."""
    for word in heading_words:
        m = re.search(r"(?i)" + re.escape(word), hblob)
        if not m:
            continue
        tail = hblob[m.end():m.end() + 6000]
        ul = re.search(r"(?is)<(ul|ol)[^>]*>(.*?)</\1>", tail)
        if not ul:
            continue
        items = []
        for li in re.findall(r"(?is)<li[^>]*>(.*?)</li>", ul.group(2)):
            t = to_text(li)
            if 3 < len(t) <= maxlen:
                items.append(t)
        if items:
            return items[:limit]
    return []


# Block-level text that is a section label or boilerplate, never a summary.
SKIP_BLOCK = re.compile(
    r"(?i)^\s*(applications?|background|key features?|highlights?|important|"
    r"example data|example|description|product description|documentation|"
    r"kit includes|kit contents?|instructions?|components?|"
    r"(viral )?(dna|rna) extraction kit components)\b[:\s]*$")
SKIP_START = re.compile(
    r"(?i)^\s*(if you have any questions|want to read more|to enhance your|"
    r"don.t see the|need support|please contact|contact us|click here|"
    r"new!|start designing|order now|available as an add|instructions?\b|"
    r"select how many|hover over|add any add-ons|a confirmation window|"
    r"example\s*\d|\(\*|\*\s*the degree)")
# Elementor dumps raw CSS into some descriptions, outside any <style> tag.
CSS_NOISE = re.compile(r"\{[^{}]*[:;][^{}]*\}")

# Products whose own copy is a UI instruction dump or a one-line note. The text
# below only restates facts the source page states (name, titre, kit format).
SUMMARY_OVERRIDE = {
    "aav-extraction-and-maturation-kit":
        "A kit for extracting and maturing AAV particles from transfected producer "
        "cells. Each base kit includes reagents for 10 preparations, where one "
        "preparation is a single transfected well of a 6-well plate. Supplied as a "
        "Mini (10 preparations) or Midi (50 preparations) format, optionally bundled "
        "with the Low-Speed Viral Concentration Kit or an AAV SEC Purification Kit.",
    "r8-71-hiv-rcl-positive-control-virus":
        "HIV-1 R8.71 replication-competent lentivirus (RCL) positive control virus, "
        "supplied at a titre greater than 5 x 10⁵ fg p24, for use as the reference "
        "control in RCL testing of lentiviral vector material.",
    # virongy.com currently renders the Infectin description under Cellment;
    # this is Cellment's own copy, taken from its product summary.
    "cellment-cell-attachment-enhancer":
        "A proprietary peptide-based media supplement that acts as a cell attachment "
        "enhancer. Cellment strengthens cell adherence to tissue-culture surfaces "
        "during transfection workflows, reducing cell loss at media changes and "
        "handling steps. It is derived from Virongy's Actinator peptide platform, "
        "engineered from human beta-actin sequences.",
    "aav-vector-customization-tool":
        "Design your own AAV vector. Choose up to four open reading frames and select "
        "each component - promoter, linkers, markers and tissue tropism - or supply "
        "your own sequence. Virongy then assembles and supplies the finished vector.",
    "lentiviral-vector-customization-tool":
        "Design your own lentiviral vector. Choose up to four open reading frames and "
        "select each component - promoter, linkers and markers - or supply your own "
        "sequence. Virongy then assembles and supplies the finished vector.",
    "retroviral-vector-customization-tool":
        "Design your own MMLV retroviral vector. Choose up to four open reading frames "
        "and select each component - promoter, linkers and markers - or supply your own "
        "sequence. Virongy then assembles and supplies the finished vector.",
    "custom-aav-assembly-purification":
        "A made-to-order AAV assembly and purification service. Virongy packages your "
        "construct into AAV particles, purifies the prep and supplies the finished "
        "material. Available in 5 x 200 uL and 10 x 1 mL volumes.",
}

# Where virongy.com's own page carries the wrong list for a product.
APPLICATIONS_OVERRIDE = {
    "cellment-cell-attachment-enhancer": [
        "Lentiviral vector production", "AAV production", "Pseudovirus production",
        "Recombinant protein expression", "CRISPR workflows",
    ],
}

# Used when a product has no usable copy of its own (Virongy leaves the
# description empty on the per-variant kits and relies on the parent page).
CATEGORY_FALLBACK = {
    "Neutralization Assay Kits":
        "A ready-to-use 96-well neutralization assay kit built on Virongy's hybrid "
        "alpha-pseudovirus technology. Supplied with pre-counted, ready-to-use target "
        "cells, so no cell culture or CO2 incubator is required - thaw and go. Used to "
        "quantify neutralizing antibodies and screen entry-inhibiting compounds at BSL-2.",
    "Custom Vector Design & Assembly":
        "A custom design and build service. Specify the vector components you need - "
        "open reading frames, promoters, linkers, markers and tropism - and Virongy "
        "assembles, validates and supplies the finished vector.",
}


def blocks(h):
    """Ordered (tag, text) pairs for the block-level elements of a fragment."""
    out = []
    for m in re.finditer(r"(?is)<(p|h[1-6]|li)[^>]*>(.*?)</\1>", h or ""):
        t = to_text(m.group(2))
        if t:
            out.append((m.group(1).lower(), t))
    return out


def summarise(desc_html, short_txt, name, category, src_slug, limit=460):
    """First real paragraph(s) of copy, headings and boilerplate removed."""
    if src_slug in SUMMARY_OVERRIDE:
        return SUMMARY_OVERRIDE[src_slug]
    if category == "Custom Vector Design & Assembly":
        return CATEGORY_FALLBACK[category]

    def gather(allow_headings):
        picked, total = [], 0
        for tag, t in blocks(desc_html):
            if tag == "li":
                continue
            # h1-h3 are section titles; h4-h6 are used as body copy by the
            # SiteOrigin widgets on several product pages.
            if tag in ("h1", "h2", "h3") and not allow_headings:
                continue
            if SKIP_BLOCK.match(t) or SKIP_START.match(t) or CSS_NOISE.search(t):
                continue
            if len(t) < 70:
                continue
            if t.lower().startswith(name.lower()[:40]) and len(t) < 120:
                continue                  # echo of the product title
            picked.append(t)
            total += len(t)
            if total >= 240 or len(picked) == 2:
                break
        return " ".join(picked).strip()

    text = gather(False) or gather(True)
    # Elementor renders its tab strip as one text run ahead of the real copy
    text = re.sub(r"(?i)^(?:\s*(?:product description|product specifications|"
                  r"documentation|references|citations?|protocols?|faq|"
                  r"description)\b[\s:]*)+", "", text).strip()
    # trailing "contact us" / marketing sentences are not product information
    text = re.split(r"(?i)\s(?:please contact|if you have any question|"
                    r"customers can provide|want to read more|don.t see the)", text)[0].strip()
    if len(text) < 80:
        alt = re.split(r"(?i)kit includes|let price_element", short_txt)[0].strip()
        text = alt if len(alt) >= 80 else CATEGORY_FALLBACK.get(category, alt or short_txt)
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) <= limit:
        return text
    cut = text[:limit]
    dot = cut.rfind(". ")
    return (cut[:dot + 1] if dot > 180 else cut.rstrip(" ,;") + "…").strip()


def main(outdir):
    pages = os.path.join(outdir, "pages")
    os.makedirs(pages, exist_ok=True)

    raw = json.loads(fetch(STORE_API).decode("utf-8"))
    products = []

    for p in raw:
        src_slug = p["slug"]
        cat = SLUG_TO_CATEGORY.get(src_slug)
        if not cat:
            print("  SKIP (uncategorised):", src_slug)
            continue

        slug = LOCAL_SLUG.get(src_slug, src_slug)
        name = to_text(p["name"])

        # cache the rendered product page (needed for PDF links)
        cache = os.path.join(pages, slug + ".html")
        if not os.path.exists(cache):
            try:
                body = fetch(p["permalink"]).decode("utf-8", "replace")
            except Exception as e:
                print("  page fetch failed:", slug, e)
                body = ""
            io.open(cache, "w", encoding="utf-8").write(body)
        page = io.open(cache, encoding="utf-8").read()

        # --- description ------------------------------------------------
        desc_html = strip_noise(p.get("description") or "")
        short_html = strip_noise(p.get("short_description") or "")
        desc_txt = to_text(desc_html)
        short_txt = to_text(short_html)
        # the injected WooCommerce price snippet leaks into some short descriptions
        short_txt = re.split(r"let price_element", short_txt)[0].strip()

        summary = summarise(desc_html, short_txt, name, cat, src_slug)

        # --- applications / kit contents / features ----------------------
        blob = desc_html + short_html
        applications = list_items_after(blob, ["Applications:", "Applications"], limit=6)
        contents = list_items_after(blob, ["Kit Includes", "Kit Contents"], limit=6)
        features = list_items_after(blob, ["Key Features", "Highlights"], limit=6)
        applications = APPLICATIONS_OVERRIDE.get(src_slug, applications)
        if applications == features:      # same <ul> matched twice
            applications = []

        # --- options (variants). Never a price. --------------------------
        options = []
        for a in p.get("attributes", []):
            label = ATTR_RENAME.get(a.get("name") or "", a.get("name") or "")
            terms = [to_text(t["name"]) for t in a.get("terms", [])]
            terms = [t for t in terms if t and "$" not in t]
            if terms:
                options.append({"label": label, "values": terms})

        # --- documents (PDF links on the rendered page) ------------------
        docs, seen = [], set()
        for m in re.finditer(r'(?is)<a[^>]+href=["\']([^"\']+\.pdf)[^"\']*["\'][^>]*>(.*?)</a>', page):
            url, label = m.group(1), to_text(m.group(2))
            fn = url.rsplit("/", 1)[-1]
            if fn in seen or "capability-statement" in fn.lower():
                continue
            seen.add(fn)
            if not label or len(label) > 90:
                label = re.sub(r"[-_]+", " ", fn[:-4]).strip()
            docs.append({"label": label, "source": url, "file": fn})

        # --- image -------------------------------------------------------
        img = p["images"][0]["src"] if p.get("images") else IMAGE_FALLBACK.get(src_slug, "")
        img = re.sub(r"^https://i0\.wp\.com/", "https://", img)
        img = img.split("?")[0]
        # Several products share one source image; name the local file after the
        # source so it is downloaded and stored once.
        stem = urllib.parse.unquote(img.rsplit("/", 1)[-1]).rsplit(".", 1)[0]
        stem = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")
        stem = re.sub(r"-(e?\d{8,})$", "", stem)[:44].strip("-")

        products.append({
            "slug": slug,
            "source_slug": src_slug,
            "name": name,
            "category": cat,
            "summary": summary,
            "applications": applications,
            "contents": contents,
            "features": features,
            "options": options,
            "image_source": img,
            "image": "assets/virongy-%s.webp" % stem,
            "docs": docs,
            "featured": src_slug in FEATURED,
        })
        print("  ok  %-46s %s" % (slug[:46], cat))

    order = {c: i for i, c in enumerate(CATEGORY_ORDER)}
    products.sort(key=lambda x: (order[x["category"]], x["name"].lower()))

    feat_order = {LOCAL_SLUG.get(s, s): i for i, s in enumerate(FEATURED)}
    out = {
        "generated": time.strftime("%Y-%m-%d"),
        "source": "virongy.com",
        "categories": CATEGORY_ORDER,
        "featured": sorted([p["slug"] for p in products if p["featured"]],
                           key=lambda s: feat_order.get(s, 99)),
        "products": products,
    }
    path = os.path.join(outdir, "virongy-products.json")
    io.open(path, "w", encoding="utf-8").write(
        json.dumps(out, indent=2, ensure_ascii=False))

    print("\n%d products -> %s" % (len(products), path))
    for c in CATEGORY_ORDER:
        print("   %-40s %d" % (c, sum(1 for p in products if p["category"] == c)))
    print("   featured: %d   with docs: %d   without image: %d" % (
        len(out["featured"]),
        sum(1 for p in products if p["docs"]),
        sum(1 for p in products if not p["image_source"])))


if __name__ == "__main__":
    main(sys.argv[1])
