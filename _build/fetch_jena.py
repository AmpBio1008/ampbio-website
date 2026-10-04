# -*- coding: utf-8 -*-
"""
Download the images for _build/jena-featured.json and save them as
assets/jena-<slug>.webp.

  python _build/fetch_jena.py               (run from the site/ directory)

Structural formulas come as black line art on transparency, which would vanish
on the site's navy, so they are flattened onto white and trimmed to the drawing
with an even margin. Photos are just resized. Nothing is upscaled. An entry
with "kind": "drawn" is drawn from its SMILES instead of downloaded.
"""
import io, json, os, sys, urllib.request
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
BASE = "https://www.jenabioscience.com"
MAX_W = 660  # 2x the 330px hero tile


def get(src):
    req = urllib.request.Request(BASE + src, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return Image.open(io.BytesIO(r.read()))


def flatten_structure(im):
    im = im.convert("RGBA")
    white = Image.new("RGBA", im.size, (255, 255, 255, 255))
    im = Image.alpha_composite(white, im).convert("RGB")
    box = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
    if box:
        im = im.crop(box)
    pad = int(max(im.size) * 0.08)
    out = Image.new("RGB", (im.width + 2 * pad, im.height + 2 * pad), "white")
    out.paste(im, (pad, pad))
    return out


def draw(smiles):
    """Black-and-white skeletal formula in the same style as Jena's drawings,
    for products whose image on jenabioscience.com is wrong (needs rdkit)."""
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from rdkit.Chem.Draw import rdMolDraw2D
    mol = Chem.MolFromSmiles(smiles)
    AllChem.Compute2DCoords(mol)
    d = rdMolDraw2D.MolDraw2DCairo(1200, 900)
    o = d.drawOptions()
    o.useBWAtomPalette()
    o.bondLineWidth = 3
    o.minFontSize = o.maxFontSize = 34
    o.padding = 0.04
    d.DrawMolecule(mol)
    d.FinishDrawing()
    return Image.open(io.BytesIO(d.GetDrawingText()))


def main():
    data = json.load(io.open(os.path.join(HERE, "jena-featured.json"), encoding="utf-8"))
    for p in data["featured"]:
        if p["kind"] == "drawn":
            im = flatten_structure(draw(p["smiles"]))
        else:
            im = get(p["src"])
            im = flatten_structure(im) if p["kind"] == "structure" else im.convert("RGB")
        if im.width > MAX_W:
            im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
        path = os.path.join(SITE, "assets", "jena-%s.webp" % p["slug"])
        im.save(path, "WEBP", quality=88, method=6)
        print("%-34s %4dx%-4d %6d bytes" % (os.path.basename(path), im.width, im.height,
                                             os.path.getsize(path)))


if __name__ == "__main__":
    sys.exit(main())
