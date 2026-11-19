"""Judgement candidates for a whole-library tidy (lint.py covers the mechanical rules). Run on gaia:
    ssh gaia python3 - < survey.py
Each line is a candidate to examine, not a verdict."""
import collections, difflib, os, re, unicodedata

ROOT = os.environ.get("SHEET_LIB", "/srv/mergerfs/gaia_data/gaia-library/Sheet Music")


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


PART = re.compile(r" - (Score|Part|Solo .*|Violin.*|Viola|Cello|Piano.*|Double Bass|Continuo|[IVX]+\. .*|Mvt \d+.*)$")


def work_key(name):
    """(identity of the work incl. arranger, whether the name carries a part/movement suffix)."""
    stem = os.path.splitext(name)[0]
    return norm(PART.sub("", stem)), bool(PART.search(stem))


composers = collections.defaultdict(list)  # composer folder -> instrument paths holding it
for top in sorted(os.listdir(ROOT)):
    base = os.path.join(ROOT, top)
    if not os.path.isdir(base) or top == "Inbox":
        continue
    groups = sorted(os.listdir(base)) if top == "Chamber" else [""]
    for g in groups:
        gdir = os.path.join(base, g)
        if not os.path.isdir(gdir):
            continue
        for c in sorted(os.listdir(gdir)):
            if os.path.isdir(os.path.join(gdir, c)):
                composers[c].append(os.path.join(top, g).rstrip("/"))

# 1. Composer folders that are probably one person under two spellings.
names = sorted(composers)
for i, a in enumerate(names):
    for b in names[i + 1:]:
        if difflib.SequenceMatcher(None, norm(a), norm(b)).ratio() > 0.85:
            print(f"composer spelling?     '{a}' ({', '.join(composers[a])})  vs  '{b}' ({', '.join(composers[b])})")

for dirpath, dirs, files in os.walk(ROOT):
    rel = os.path.relpath(dirpath, ROOT)
    if rel.startswith("Inbox"):
        continue
    parts = rel.split(os.sep)
    in_composer = len(parts) == (3 if parts[0] == "Chamber" else 2)
    docs = [f for f in files if f.lower().endswith(".pdf")]

    # 2. Same work twice in one folder: extra editions.
    by_work = collections.defaultdict(list)
    for f in docs:
        by_work[work_key(f)[0]].append(f)
    for k, fs in by_work.items():
        parted = [f for f in fs if work_key(f)[1]]
        if len(fs) > 1 and len(parted) < len(fs):
            print(f"duplicate work?        {rel}: {' | '.join(sorted(fs))}")

    if in_composer:
        # 3. Multi-file works sitting loose in the composer folder: they belong in a work folder.
        for k, fs in by_work.items():
            if len(fs) > 1 and all(work_key(f)[1] for f in fs):
                print(f"needs work folder      {rel}: {len(fs)} files of '{k}'")
        # 4. Genre subfolder threshold (> ~10 works of one genre).
        genres = collections.Counter(re.split(r"[ ,]", norm(os.path.splitext(f)[0]))[0] for f in docs)
        for g, n in genres.items():
            if n > 10:
                print(f"genre subfolder?       {rel}: {n} loose '{g}…' works")
