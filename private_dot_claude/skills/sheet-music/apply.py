"""Apply a map (src<TAB>dest, relative to the library root) on gaia:
    ssh gaia python3 - <map-path-on-gaia> < apply.py
Rows sharing a dest are image pages merged in row order.
Images -> one PDF; other files moved. Never overwrites. Sources removed only after success."""
import collections, io, os, shutil, sys
import img2pdf
from PIL import Image

LIB = os.environ.get("SHEET_LIB", "/srv/mergerfs/gaia_data/gaia-library/Sheet Music")
IMG = {".jpg", ".jpeg", ".gif", ".tif", ".tiff", ".bmp", ".png"}
groups = collections.OrderedDict()
for line in open(sys.argv[1], encoding="utf-8"):
    if line.strip():
        s, d = line.rstrip("\n").split("\t")
        groups.setdefault(d, []).append(s)


def pages(path):
    """Bytes img2pdf accepts directly, else Pillow-converted PNG frames (bmp, odd gif/tif modes)."""
    raw = open(path, "rb").read()
    try:
        img2pdf.convert(raw)
        return [raw]
    except Exception:
        out = []
        with Image.open(path) as im:
            for i in range(getattr(im, "n_frames", 1)):
                im.seek(i)
                b = io.BytesIO()
                im.convert("L" if im.mode in ("1", "L", "LA") else "RGB").save(b, "PNG")
                out.append(b.getvalue())
        return out


errors = 0
for d, srcs in groups.items():
    dst = os.path.join(LIB, d)
    try:
        if os.path.exists(dst):
            raise FileExistsError("dest exists")
        missing = [s for s in srcs if not os.path.isfile(os.path.join(LIB, s))]
        if missing:
            raise FileNotFoundError(missing)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        exts = {os.path.splitext(s)[1].lower() for s in srcs}
        if d.lower().endswith(".pdf") and exts <= IMG:
            data = [p for s in srcs for p in pages(os.path.join(LIB, s))]
            with open(dst, "wb") as f:
                f.write(img2pdf.convert(data, rotation=img2pdf.Rotation.ifvalid))
            for s in srcs:
                os.remove(os.path.join(LIB, s))
        elif len(srcs) == 1:
            shutil.move(os.path.join(LIB, srcs[0]), dst)
        else:
            raise ValueError(f"{len(srcs)} non-image srcs share one dest")
        print("OK  ", d)
    except Exception as e:
        errors += 1
        print("FAIL", d, repr(e)[:200])
print(f"{len(groups)} dests, {errors} errors")
sys.exit(1 if errors else 0)
