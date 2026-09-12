# -*- coding: utf-8 -*-
"""
Download the Virongy product documents into per-product folders.

  python _build/fetch_docs.py            (run from the site/ directory)

Layout produced under assets/docs/:

  <product-slug>/<document>.pdf     documents linked from that product's page
  _company/                         brochure, capability statement
  _unassigned/                      PDFs in Virongy's media library that no
                                    product page links to - kept so nothing is
                                    lost, but NOT filed against a product,
                                    because guessing which product an MSDS
                                    belongs to is not safe.

Each unique file is downloaded once and copied into every product that links
it. Writes assets/docs/MANIFEST.txt describing what landed where and what is
missing.
"""
import io, json, os, re, shutil, sys, time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
DOCS = os.path.join(SITE, "assets", "docs")
CACHE = os.path.join(HERE, "doc-cache")
CATALOGUE = os.path.join(HERE, "virongy-products.json")
MEDIA_API = ("https://virongy.com/wp-json/wp/v2/media"
             "?media_type=application&per_page=100&_fields=source_url,title")
UA = "Mozilla/5.0 (compatible; amps.bio document sync)"

# Company-wide material rather than a product document.
COMPANY = re.compile(r"(?i)capability-statement|product-brochure")
# Artwork saved as PDF - not a document.
ARTWORK = re.compile(r"(?i)particle-image|image-for-product-page|product-pic|"
                     r"logo-with-dna|image-2|^particle-image")


def fetch(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except Exception:
            if i == retries - 1:
                raise
            time.sleep(2)


def slug(s, limit=46):
    """Short, whole-word names. The cap matters: the deepest product folder plus
    a long filename otherwise pushes the absolute path past Windows' 260-char
    limit, and git then refuses to index the file."""
    s = re.sub(r"(?i)\.pdf$", "", s)
    s = s.replace("–", "-").replace("—", "-").replace("’", "")
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    s = re.sub(r"-{2,}", "-", s)
    if len(s) > limit:
        cut = s[:limit]
        if "-" in cut[20:]:
            cut = cut[:cut.rfind("-")]
        s = cut
    # a truncated name should not end on a dangling "...-with" / "...-the"
    s = re.sub(r"-(with|the|and|for|of|a|an|to|in|on|by)$", "", s.strip("-"))
    return s.strip("-") or "document"


# A link label that says nothing about the document itself.
GENERIC = re.compile(r"(?i)^(download|click|view|open|read|here|the )|pdf version|^download the")


def doc_name(label, filename):
    """Readable filename. Virongy's link text is usually descriptive, but some
    links just say 'Download the PDF version here', and some echo the raw
    filename including its VBI-HBK revision prefix."""
    base = filename if (not label or GENERIC.search(label)) else label
    base = re.sub(r"(?i)^vbi[-\s_]*hbk[-\s_]*\d+([-\s_]*rev\s*\d+)?[-\s_]*", "", base)
    base = re.sub(r"(?i)^\d+\.\s*", "", base)
    base = re.sub(r"(?i)\bvirongy'?s?\b", "", base)
    return slug(base) + ".pdf"


def download(url):
    """Fetch once into the cache; return the local path."""
    name = url.rsplit("/", 1)[-1]
    path = os.path.join(CACHE, name)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    data = fetch(url)
    if not data.startswith(b"%PDF"):
        raise ValueError("not a PDF (%d bytes)" % len(data))
    io.open(path, "wb").write(data)
    return path


def place(src, folder, filename):
    os.makedirs(folder, exist_ok=True)
    dest = os.path.join(folder, filename)
    stem, ext = os.path.splitext(filename)
    n = 2
    while os.path.exists(dest) and os.path.getsize(dest) != os.path.getsize(src):
        dest = os.path.join(folder, "%s-%d%s" % (stem, n, ext))
        n += 1
    shutil.copyfile(src, dest)
    return dest


def main():
    os.makedirs(CACHE, exist_ok=True)
    os.makedirs(DOCS, exist_ok=True)
    data = json.load(io.open(CATALOGUE, encoding="utf-8"))

    rows, failures, linked_names = [], [], set()
    doc_map = {}          # slug -> [{label, path}] for build_virongy.py
    total_products = 0

    # ---- documents linked from a product page --------------------------
    for p in data["products"]:
        if not p["docs"]:
            continue
        total_products += 1
        folder = os.path.join(DOCS, p["slug"])
        for d in p["docs"]:
            linked_names.add(d["file"])
            try:
                src = download(d["source"])
            except Exception as e:
                failures.append("%s  <- %s  (%s)" % (p["name"], d["file"], e))
                continue
            dest = place(src, folder, doc_name(d["label"], d["file"]))
            rows.append((p["slug"], os.path.basename(dest),
                         os.path.getsize(dest), d["file"]))
            doc_map.setdefault(p["slug"], []).append({
                "label": d["label"],
                "path": "assets/docs/%s/%s" % (p["slug"], os.path.basename(dest)),
                "bytes": os.path.getsize(dest)})
        print("  %-46s %d doc(s)" % (p["slug"][:46], len(p["docs"])))

    # ---- everything else in the media library ---------------------------
    extras, company = [], []
    try:
        media = json.loads(fetch(MEDIA_API).decode("utf-8"))
    except Exception as e:
        media = []
        failures.append("media library listing failed (%s)" % e)

    for m in media:
        url = m.get("source_url", "")
        if not url.lower().endswith(".pdf"):
            continue
        name = url.rsplit("/", 1)[-1]
        if name in linked_names or ARTWORK.search(name):
            continue
        bucket = "_company" if COMPANY.search(name) else "_unassigned"
        try:
            src = download(url)
        except Exception as e:
            failures.append("%s  (%s)" % (name, e))
            continue
        dest = place(src, os.path.join(DOCS, bucket), slug(name) + ".pdf")
        (company if bucket == "_company" else extras).append(
            (os.path.basename(dest), os.path.getsize(dest), name))

    # ---- products whose page names a document but never links it --------
    unlinked = [p["name"] for p in data["products"] if not p["docs"]]

    total = sum(r[2] for r in rows) + sum(x[1] for x in extras + company)
    lines = [
        "Virongy product documents, downloaded from virongy.com on %s" % time.strftime("%Y-%m-%d"),
        "",
        "%d product folders, %d filed documents" % (total_products, len(rows)),
        "%d unassigned, %d company documents" % (len(extras), len(company)),
        "%.1f MB on disk" % (total / 1048576.0),
        "",
        "=" * 78,
        "FILED BY PRODUCT",
        "=" * 78,
    ]
    for s, fn, size, orig in sorted(rows):
        lines.append("%-46s %-44s %7.0f KB" % (s, fn, size / 1024.0))

    lines += ["", "=" * 78,
              "COMPANY DOCUMENTS  (assets/docs/_company/)", "=" * 78]
    for fn, size, orig in sorted(company):
        lines.append("%-60s %7.0f KB" % (fn, size / 1024.0))

    lines += ["", "=" * 78,
              "UNASSIGNED  (assets/docs/_unassigned/)",
              "In Virongy's media library but not linked from any product page,",
              "so they are NOT filed against a product - the filename alone is not",
              "safe evidence of which product an MSDS or protocol belongs to.",
              "=" * 78]
    for fn, size, orig in sorted(extras):
        lines.append("%-60s %7.0f KB" % (fn, size / 1024.0))

    lines += ["", "=" * 78,
              "NO DOWNLOADABLE DOCUMENTS",
              "These product pages link no PDF. Several of them do list document",
              "names (e.g. Cellment shows 'MSDS' and 'Protocol'), but Virongy has",
              "not hyperlinked them and the files are not in their media library -",
              "so they have to be requested from Virongy directly.",
              "=" * 78]
    for n in sorted(unlinked):
        lines.append("  %s" % n)

    if failures:
        lines += ["", "=" * 78, "FAILED", "=" * 78] + ["  " + f for f in failures]

    io.open(os.path.join(DOCS, "MANIFEST.txt"), "w", encoding="utf-8").write(
        "\n".join(lines) + "\n")
    io.open(os.path.join(HERE, "doc-map.json"), "w", encoding="utf-8").write(
        json.dumps(doc_map, indent=2, ensure_ascii=False))

    print("\n%d filed, %d unassigned, %d company, %d failed, %.1f MB"
          % (len(rows), len(extras), len(company), len(failures), total / 1048576.0))


if __name__ == "__main__":
    main()
