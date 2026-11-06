"""Mechanical rule check for the sheet music library. Run on gaia: ssh gaia python3 - < lint.py
Prints Inbox contents and every rule violation; prints 'clean' when there is nothing to do."""
import os, re, sys

ROOT = "/srv/mergerfs/gaia_data/gaia-library/Sheet Music"
INSTRUMENTS = {"Violin", "Viola", "Cello", "Double Bass", "Piano", "Voice", "Flute", "Clarinet", "Guitar"}
TOP = INSTRUMENTS | {"Chamber", "Collections", "Inbox"}
ENSEMBLES = {"Duo", "Trio", "Quartet", "Quintet", "Sextet", "Octet", "String Orchestra"}
KEEP_EXT = {".pdf", ".doc", ".docx"}
BAD_CHARS = re.compile(r'[\\:*?"<>|]')
EXTRA_EDITION = re.compile(r" \((alt[^)]*|dup[^)]*|\d+)\)(\.\w+)?$| \(\d+\) - ")
CODE_NAME = re.compile(r"(-a4|-let|_sc|^\d+\.\w+$|^[a-z]{1,4}\d+[a-z]?\.\w+$|^img\d+|^page\d+|^IMSLP\d+)", re.I)
CJK = re.compile(r"[一-鿿]")

issues = []


def flag(path, why):
    issues.append(f"{why:<24} {path}")


for dirpath, dirs, files in os.walk(ROOT):
    rel = os.path.relpath(dirpath, ROOT)
    parts = [] if rel == "." else rel.split(os.sep)
    if not dirs and not files and parts and parts != ["Inbox"]:
        flag(rel, "empty folder")
    for name in dirs + files:
        if BAD_CHARS.search(name):
            flag(os.path.join(rel, name), "forbidden character")
        if CJK.search(name) and not re.search(r"[A-Za-z]{2}", name):
            flag(os.path.join(rel, name), "CJK without pinyin")
        if len(name) > 150:
            flag(os.path.join(rel, name), "name too long")
    if not parts:
        for d in dirs:
            if d not in TOP:
                flag(d, "unknown top folder")
        for f in files:
            flag(f, "file at root")
        continue
    if parts[0] == "Inbox":
        for f in files:
            flag(os.path.join(rel, f), "inbox")
        continue
    if parts[0] == "Chamber" and len(parts) == 1:
        for d in dirs:
            if d not in ENSEMBLES:
                flag(os.path.join(rel, d), "unknown ensemble")
    for f in files:
        p = os.path.join(rel, f)
        ext = os.path.splitext(f)[1].lower()
        if f in (".DS_Store", "Thumbs.db") or f.startswith("._"):
            flag(p, "junk")
            continue
        depth_min = 3 if parts[0] == "Chamber" else 2
        if len(parts) < depth_min:
            flag(p, "outside composer folder")
        if ext == ".mp3":
            if "ABRSM" not in rel:
                flag(p, "audio outside ABRSM")
        elif ext not in KEEP_EXT:
            flag(p, f"disallowed {ext or 'no-ext'}")
        if EXTRA_EDITION.search(f):
            flag(p, "extra edition")
        if CODE_NAME.search(f):
            flag(p, "code-style name")
        elif f[:1].islower():
            flag(p, "lowercase name")

print("\n".join(sorted(issues)) if issues else "clean")
sys.exit(1 if issues else 0)
