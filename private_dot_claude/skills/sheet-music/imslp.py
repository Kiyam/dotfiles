"""IMSLP lookup via the open MediaWiki API (runs on the Mac, stdlib only).

    python3 imslp.py search "franck violin sonata"     -> work pages
    python3 imslp.py work "Violin Sonata (Franck, César)" -> editions, files, direct links, EU status

PDF downloads sit behind a CAPTCHA, so this prints links for the user to click; it never downloads.
EU status: PD-EU = composer and every named editor/arranger died more than 70 years before this year;
CC = a Creative Commons licence; CHECK = anything else (unknown dates, recent editors, other licences).
"""
import datetime, json, re, sys, urllib.parse, urllib.request

API = "https://imslp.org/api.php"
CUTOFF = datetime.date.today().year - 71  # France: life + 70, counted from 1 January after death


def api(**params):
    params["format"] = "json"
    req = urllib.request.Request(f"{API}?{urllib.parse.urlencode(params)}", headers={"User-Agent": "sheet-music-skill"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def wikitext(page):
    r = api(action="parse", page=page, prop="wikitext", redirects=1)
    if "parse" not in r:
        sys.exit(f"no IMSLP page '{page}': run search first and pass an exact title")
    return r["parse"]["wikitext"]["*"]


def fields(block):
    """'|Key=Value' lines of one template block -> dict."""
    out = {}
    for line in block.splitlines():
        m = re.match(r"\|([^=|{}]+)=(.*)", line)
        if m:
            out[m.group(1).strip()] = m.group(2).strip()
    return out


def died(name_or_cat):
    try:
        m = re.search(r"Died Year=(\d{4})", wikitext(f"Category:{name_or_cat}"))
        return int(m.group(1)) if m else None
    except Exception:
        return None


def publisher(m):
    a = (m.group(1).split("|") + [""] * 7)[:7]  # short|full|city|date|year|plate|extra
    return f"{a[1] or a[0]}, {a[2]} {a[4]}" + (f" (plate {a[5]})" if a[5] else "")


def plain(s):
    while re.search(r"\{\{(?!P\||Link(?:Ed|Arr)\|)[^{}]*\}\}", s):  # innermost helper templates first
        s = re.sub(r"\{\{(flat|sharp)\}\}", lambda m: "b" if m.group(1) == "flat" else "#", s)
        s = re.sub(r"\{\{(?!P\||Link(?:Ed|Arr)\|)[^{}]*\}\}", "", s)
    s = re.sub(r"\{\{P\|([^{}]*)\}\}", publisher, s)
    s = re.sub(r"\{\{Link(?:Ed|Arr)\|([^|}]*)\|([^|}]*)[^}]*\}\}", r"\1 \2", s)
    s = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\{\{[^{}]*\}\}|<br\s*/?>", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def search(q):
    res = api(action="query", list="search", srsearch=q, srnamespace=0, srlimit=15)["query"]["search"]
    for r in res:
        print(r["title"])
    if not res:
        print("no results")


def work(page):
    page = urllib.parse.unquote(page.rsplit("/wiki/", 1)[-1]).replace("_", " ")
    t = wikitext(page)
    info = fields(t[t.find("*****WORK INFO*****"):])
    composer = re.search(r"\(([^()]*)\)\s*$", page)
    composer = composer.group(1) if composer else ""
    cdied = died(composer)
    print(f"# {page}\nopus: {info.get('Opus/Catalogue Number', '')}  instrumentation: {info.get('Instrumentation', '')}")
    print(f"composer: {composer}, died {cdied or '?'}  (PD-EU cutoff: died <= {CUTOFF})\n")

    files_sec = t[t.find("*****FILES*****"):t.find("*****WORK INFO*****")]
    heading, editions = "", []
    for chunk in re.split(r"(?m)^(?=\{\{#fte:imslpfile|=+[^=\n]+=+\s*$)", files_sec):
        h = re.match(r"(=+)([^=\n]+)=+", chunk)
        if h:
            level = len(h.group(1))
            heading = h.group(2).strip() if level <= 3 else heading.split(" > ")[0] + " > " + h.group(2).strip()
            continue
        if chunk.startswith("{{#fte:imslpfile"):
            editions.append((heading, fields(chunk)))

    names = [f["File Name " + k[len("File Name "):]] for _, f in editions for k in f if k.startswith("File Name ")]
    urls = {}
    for i in range(0, len(names), 50):
        q = api(action="query", prop="imageinfo", iiprop="url|size", titles="|".join("File:" + n for n in names[i:i + 50]))
        norm = {n["to"]: n["from"] for n in q["query"].get("normalized", [])}
        for p in q["query"]["pages"].values():
            if "imageinfo" in p:
                ii = p["imageinfo"][0]
                urls[norm.get(p["title"], p["title"])[5:]] = ("https:" + ii["url"], ii["size"])

    for n, (heading, f) in enumerate(editions, 1):
        people = (f.get("Editor", "") + f.get("Arranger", "")).replace("{{FE}}", "")  # FE = first edition, no editor
        eds = re.findall(r"\{\{Link(?:Ed|Arr)\|([^|}]*)\|([^|}]*)\|?\d*\|?(\d*)\}\}", people)
        ed_died = [int(d) if d else None for _, _, d in eds]
        unnamed = plain(re.sub(r"\{\{Link(?:Ed|Arr)[^}]*\}\}|\([^)]*\)", "", people)).strip(" ,;&")
        lic = f.get("Copyright", "")
        if "Creative Commons" in lic:
            status = "CC"
        elif "dedicated" in lic.lower():
            status = "PD-dedicated"  # living author waived rights
        elif cdied and cdied <= CUTOFF and all(d and d <= CUTOFF for d in ed_died) and not unnamed:
            status = "PD-EU"
        else:
            status = "CHECK"
        print(f"## [{n}] {heading}  — {status}")
        print(f"   publisher: {plain(f.get('Publisher Information', ''))}")
        if f.get("Editor") or f.get("Arranger"):
            print(f"   editor/arranger: {plain(f.get('Editor', '') + ' ' + f.get('Arranger', ''))}  died {ed_died or '?'}")
        print(f"   type: {f.get('Image Type', '?')}  licence: {lic or '?'}  notes: {plain(f.get('Misc. Notes', ''))[:120]}")
        for k in sorted((k for k in f if k.startswith("File Name ")), key=lambda k: int(k.split()[-1])):
            i = k.split()[-1]
            name = f[k]
            url, size = urls.get(name.replace("_", " "), urls.get(name, ("?", 0)))
            print(f"   - {plain(f.get('File Description ' + i, '?'))} ({size / 1e6:.1f} MB): {url}")
        print()


if __name__ == "__main__":
    cmd, arg = sys.argv[1], " ".join(sys.argv[2:])
    {"search": search, "work": work}[cmd](arg)
