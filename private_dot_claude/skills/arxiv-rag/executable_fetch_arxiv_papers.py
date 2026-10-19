#!/usr/bin/env python3
"""
Fetch arXiv papers referenced in a BibTeX file, pull their LaTeX sources,
flatten \\input/\\include, convert to Markdown (pandoc if available, else
light cleanup), and write one .md per paper plus an index.

Usage:
    python3 fetch_arxiv_papers.py --bib path/to/bibliography.bib \
        --out path/to/output_dir [--limit N] [--only key1,key2] [--force]

    # Plain-text reference list (one paragraph per ref):
    python3 fetch_arxiv_papers.py --refs path/to/refs.txt --out output_dir

    # Search arXiv by title for entries lacking an eprint:
    python3 fetch_arxiv_papers.py --bib bib.bib --out out --search-fallback
"""

from __future__ import annotations

import argparse
import gzip
import io
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

ARXIV_EPRINT_URL = "https://arxiv.org/e-print/{id}"
ARXIV_API_URL = "https://export.arxiv.org/api/query"
USER_AGENT = "arxiv-rag-skill/0.1 (+https://claude.com/claude-code)"
POLITE_DELAY_S = 3.1  # arXiv asks for ~3s between source-download requests
API_DELAY_S = 8.0     # search API trips rate-limit at ~3s; 8s is safe


# ----------------------------- BibTeX parsing -----------------------------

ENTRY_RE = re.compile(r"@(?P<type>\w+)\s*\{\s*(?P<key>[^,\s]+)\s*,", re.IGNORECASE)


def _strip_braces(value: str) -> str:
    value = value.strip()
    if value.startswith("{") and value.endswith("}"):
        value = value[1:-1]
    elif value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    return value.strip()


def _split_entries(text: str) -> list[tuple[str, str, str]]:
    """Return list of (entry_type, key, body) for each @entry{...} in text."""
    out: list[tuple[str, str, str]] = []
    i = 0
    while i < len(text):
        m = ENTRY_RE.search(text, i)
        if not m:
            break
        depth = 1
        j = m.end()
        while j < len(text) and depth > 0:
            c = text[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            j += 1
        body = text[m.end():j - 1]
        out.append((m.group("type").lower(), m.group("key"), body))
        i = j
    return out


def _parse_fields(body: str) -> dict[str, str]:
    """Naive field parser sufficient for typical bib files."""
    fields: dict[str, str] = {}
    i = 0
    n = len(body)
    while i < n:
        eq = body.find("=", i)
        if eq == -1:
            break
        name = body[i:eq].strip().strip(",").strip().lower()
        j = eq + 1
        while j < n and body[j].isspace():
            j += 1
        if j >= n:
            break
        if body[j] == "{":
            depth = 1
            k = j + 1
            while k < n and depth > 0:
                if body[k] == "{":
                    depth += 1
                elif body[k] == "}":
                    depth -= 1
                k += 1
            value = body[j + 1:k - 1]
            i = k
        elif body[j] == '"':
            k = j + 1
            while k < n and body[k] != '"':
                k += 1
            value = body[j + 1:k]
            i = k + 1
        else:
            k = j
            while k < n and body[k] != ",":
                k += 1
            value = body[j:k]
            i = k
        fields[name] = _strip_braces(value)
        while i < n and body[i] in ",\n\r\t ":
            i += 1
    return fields


@dataclass
class BibEntry:
    key: str
    entry_type: str
    fields: dict[str, str] = field(default_factory=dict)

    @property
    def title(self) -> str:
        t = self.fields.get("title", "").strip()
        return re.sub(r"\s+", " ", t)

    @property
    def arxiv_id(self) -> str | None:
        # Check dedicated fields first, then fall back to fields where an
        # arXiv id is sometimes embedded ("arXiv preprint arXiv:...").
        candidates = [
            self.fields.get("eprint", ""),
            self.fields.get("archiveprefix", ""),
            self.fields.get("journal", ""),
            self.fields.get("note", ""),
            self.fields.get("howpublished", ""),
        ]
        for c in candidates:
            m = re.search(r"(arXiv:)?\s*([a-z\-]+/\d{7}|\d{4}\.\d{4,5})(v\d+)?",
                          c, re.IGNORECASE)
            if m:
                return m.group(2)
        return None


def parse_bib(path: Path) -> list[BibEntry]:
    text = path.read_text(encoding="utf-8", errors="replace")
    entries: list[BibEntry] = []
    for etype, key, body in _split_entries(text):
        entries.append(BibEntry(key=key, entry_type=etype, fields=_parse_fields(body)))
    return entries


# ------------------------- Plain-text refs parsing ------------------------

TITLE_QUOTE_RE = re.compile(r'"([^"]+)"')
ARXIV_INLINE_RE = re.compile(r"arXiv:?\s*([a-z\-]+/\d{7}|\d{4}\.\d{4,5})", re.IGNORECASE)
YEAR_PAREN_RE = re.compile(r"\((\d{4})\)")
DOI_INLINE_RE = re.compile(r"doi:\s*(10\.\S+?)(?:[\s.,)]|$)", re.IGNORECASE)


def _slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def parse_refs_txt(path: Path) -> list[BibEntry]:
    """Parse a plain-text references file.

    Each reference is one paragraph (blank lines separate). Headers without
    a year-in-parens are skipped. Tries to extract a quoted title, first
    author, year, arXiv id, and DOI.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    paragraphs = re.split(r"\n\s*\n", text)
    entries: list[BibEntry] = []
    used_keys: set[str] = set()
    for para in paragraphs:
        flat = re.sub(r"\s+", " ", para).strip()
        if not flat:
            continue
        year_m = YEAR_PAREN_RE.search(flat)
        title_m = TITLE_QUOTE_RE.search(flat)
        if not year_m or not title_m:
            continue  # likely a section header
        year = year_m.group(1)
        title = title_m.group(1).strip().rstrip(".")
        # First author chunk = text before first comma
        first_chunk = flat.split(",", 1)[0].strip()
        last_name = _slugify(first_chunk.split()[0]) or "anon"
        STOP = {"the", "a", "an", "of", "on", "to", "for"}
        title_words = [w for w in title.split() if _slugify(w) not in STOP]
        title_first = _slugify((title_words or title.split())[0]) or "paper"
        base_key = f"{last_name}{year}{title_first}"
        key = base_key
        n = 2
        while key in used_keys:
            key = f"{base_key}_{n}"
            n += 1
        used_keys.add(key)
        fields: dict[str, str] = {"title": title, "year": year}
        am = ARXIV_INLINE_RE.search(flat)
        if am:
            fields["eprint"] = am.group(1)
        dm = DOI_INLINE_RE.search(flat)
        if dm:
            fields["doi"] = dm.group(1)
        # crude author snippet up to the quoted title
        author_end = title_m.start()
        author_snippet = flat[:author_end].strip().rstrip(".").strip()
        if author_snippet:
            fields["author"] = author_snippet
        entries.append(BibEntry(key=key, entry_type="article", fields=fields))
    return entries


# ----------------------------- arXiv API search ---------------------------


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", s.lower())


STOP_WORDS = {"the", "a", "an", "of", "on", "to", "for", "and", "with", "in",
              "by", "from", "is", "are", "as", "via"}


def _title_tokens(s: str) -> list[str]:
    return [w for w in _norm(s).split() if w and w not in STOP_WORDS and len(w) > 2]


def _arxiv_api_get(query: str) -> str | None:
    url = f"{ARXIV_API_URL}?search_query={urllib.parse.quote(query)}&max_results=5"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    backoff = 15.0
    for attempt in range(2):  # 1 retry max -> total wait ~15s, not 7min
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                xml = r.read().decode("utf-8", errors="replace")
            time.sleep(API_DELAY_S)
            return xml
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt == 0:
                print(f"  ! arxiv 429; sleeping {backoff:.0f}s and retrying once",
                      file=sys.stderr)
                time.sleep(backoff)
                continue
            print(f"  ! arxiv API error: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"  ! arxiv API error: {e}", file=sys.stderr)
            return None
    return None


def _best_entry_match(xml: str, want_tokens: set[str]) -> str | None:
    if not want_tokens:
        return None
    entries = re.findall(r"<entry>(.*?)</entry>", xml, flags=re.DOTALL)
    best: tuple[float, str] | None = None
    for ent in entries:
        id_m = re.search(r"<id>http://arxiv\.org/abs/([^<]+)</id>", ent)
        title_em = re.search(r"<title>(.*?)</title>", ent, flags=re.DOTALL)
        if not id_m or not title_em:
            continue
        got = set(_title_tokens(title_em.group(1).strip()))
        if not got:
            continue
        overlap = len(want_tokens & got) / len(want_tokens)
        if overlap >= 0.6 and (best is None or overlap > best[0]):
            aid = re.sub(r"v\d+$", "", id_m.group(1).strip())
            best = (overlap, aid)
    return best[1] if best else None


def lookup_arxiv_by_title(title: str, first_author: str = "") -> str | None:
    """Search arXiv by title; return best-match arxiv id or None.

    Tries an exact-quoted-title query first, then falls back to a query
    using only the most distinctive title tokens + author. Sleeps
    POLITE_DELAY_S after every API call.
    """
    want = set(_title_tokens(title))
    # Attempt 1: full quoted title (+ author).
    q1 = f'ti:"{title}"'
    if first_author:
        q1 += f' AND au:"{first_author}"'
    xml = _arxiv_api_get(q1)
    if xml:
        aid = _best_entry_match(xml, want)
        if aid:
            return aid
    # Attempt 2: OR over the 3 longest tokens + author. Avoids missing
    # papers whose arxiv title has variant spelling (Hypocentre/Hypocenter)
    # or different punctuation than the citing source.
    toks = _title_tokens(title)
    distinctive = sorted(set(toks), key=len, reverse=True)[:3]
    if not distinctive:
        return None
    title_or = "(" + " OR ".join(f"ti:{t}" for t in distinctive) + ")"
    q2 = title_or + (f' AND au:"{first_author}"' if first_author else "")
    xml = _arxiv_api_get(q2)
    if not xml:
        return None
    return _best_entry_match(xml, want)


# ----------------------------- arXiv download -----------------------------


def download_eprint(arxiv_id: str, dest_dir: Path) -> Path | None:
    """Download the source tarball for an arxiv id; return path or None."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    out_path = dest_dir / f"{arxiv_id.replace('/', '_')}.src"
    if out_path.exists() and out_path.stat().st_size > 0:
        return out_path
    url = ARXIV_EPRINT_URL.format(id=arxiv_id)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
    except Exception as e:
        print(f"  ! download failed for {arxiv_id}: {e}", file=sys.stderr)
        return None
    out_path.write_bytes(data)
    return out_path


def extract_source(src_path: Path, work_dir: Path) -> tuple[Path | None, str]:
    """Extract arxiv source archive. Returns (dir_or_none, reason)."""
    work_dir.mkdir(parents=True, exist_ok=True)
    data = src_path.read_bytes()
    if data[:4] == b"%PDF":
        return None, "pdf-only upload (no LaTeX source on arXiv)"
    # Try tar.gz first
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tf:
            try:
                tf.extractall(work_dir, filter="data")  # py3.12+ safe filter
            except TypeError:
                # Older Python (e.g. macOS's 3.9) has no filter: extract only
                # regular files/dirs that stay inside work_dir.
                root = work_dir.resolve()
                safe = [m for m in tf.getmembers()
                        if (m.isfile() or m.isdir())
                        and (root / m.name).resolve().is_relative_to(root)]
                tf.extractall(work_dir, members=safe)
        return work_dir, ""
    except tarfile.ReadError:
        pass
    except Exception as e:
        print(f"  ! tar extract failed: {e}", file=sys.stderr)
    # Try gzip of a single .tex
    try:
        decompressed = gzip.decompress(data)
        out = work_dir / "main.tex"
        out.write_bytes(decompressed)
        return work_dir, ""
    except OSError:
        pass
    # Maybe it's a raw .tex
    head = data[:200].lstrip().lower()
    if b"\\documentclass" in head or b"\\input" in head or b"\\begin" in head:
        out = work_dir / "main.tex"
        out.write_bytes(data)
        return work_dir, ""
    return None, "unknown archive format"


# ----------------------------- TeX flattening -----------------------------


def find_main_tex(root: Path) -> Path | None:
    """Find the top-level .tex file (one containing \\documentclass)."""
    tex_files = sorted(root.rglob("*.tex"))
    if not tex_files:
        return None
    candidates: list[tuple[int, Path]] = []
    for p in tex_files:
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if "\\documentclass" in txt:
            candidates.append((p.stat().st_size, p))
    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][1]
    return tex_files[0]


INPUT_RE = re.compile(r"\\(?:input|include|subfile)\s*\{([^}]+)\}")


def flatten_tex(tex_path: Path, root: Path, seen: set[Path] | None = None) -> str:
    seen = set() if seen is None else seen
    if tex_path in seen:
        return ""
    seen.add(tex_path)
    try:
        text = tex_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

    def _resolve(name: str) -> Path | None:
        candidates = [
            (tex_path.parent / name),
            (tex_path.parent / f"{name}.tex"),
            (root / name),
            (root / f"{name}.tex"),
        ]
        for c in candidates:
            if c.is_file():
                return c
        # Best-effort match by basename
        base = Path(name).name
        for c in [root / f"{base}.tex", root / base]:
            if c.is_file():
                return c
        return None

    def _replace(match: re.Match[str]) -> str:
        name = match.group(1).strip()
        resolved = _resolve(name)
        if resolved is None:
            return f"% [missing include: {name}]\n"
        return "\n" + flatten_tex(resolved, root, seen) + "\n"

    return INPUT_RE.sub(_replace, text)


# ----------------------------- TeX -> Markdown ----------------------------


def have_pandoc() -> bool:
    return shutil.which("pandoc") is not None


def tex_to_md_pandoc(tex_text: str) -> str | None:
    try:
        result = subprocess.run(
            ["pandoc", "-f", "latex", "-t", "gfm",
             "--wrap=none", "--mathjax"],
            input=tex_text.encode("utf-8"),
            capture_output=True,
            timeout=120,
        )
        if result.returncode == 0:
            return result.stdout.decode("utf-8", errors="replace")
        print(f"  ! pandoc failed: {result.stderr.decode('utf-8', errors='replace')[:200]}",
              file=sys.stderr)
    except Exception as e:
        print(f"  ! pandoc error: {e}", file=sys.stderr)
    return None


PREAMBLE_RE = re.compile(r"^.*?\\begin\{document\}", re.DOTALL)
ENDDOC_RE = re.compile(r"\\end\{document\}.*$", re.DOTALL)
COMMENT_RE = re.compile(r"(?<!\\)%.*?$", re.MULTILINE)
SECTION_RE = re.compile(r"\\(section|subsection|subsubsection|paragraph)\*?\s*\{([^}]*)\}")
TEXTBF_RE = re.compile(r"\\textbf\s*\{([^}]*)\}")
TEXTIT_RE = re.compile(r"\\(?:textit|emph)\s*\{([^}]*)\}")
TEXTTT_RE = re.compile(r"\\texttt\s*\{([^}]*)\}")
LABEL_RE = re.compile(r"\\(?:label|ref|eqref|cite[a-z]*)\s*\{[^}]*\}")
URL_RE = re.compile(r"\\url\s*\{([^}]*)\}")
HREF_RE = re.compile(r"\\href\s*\{([^}]*)\}\s*\{([^}]*)\}")
ITEMIZE_BEGIN_RE = re.compile(r"\\begin\{(itemize|enumerate)\}")
ITEMIZE_END_RE = re.compile(r"\\end\{(?:itemize|enumerate)\}")
ITEM_RE = re.compile(r"\\item\s*")
ENV_VERBATIM_RE = re.compile(r"\\begin\{(verbatim|lstlisting)\}(.*?)\\end\{\1\}", re.DOTALL)


def tex_to_md_light(tex_text: str) -> str:
    text = PREAMBLE_RE.sub("", tex_text, count=1)
    text = ENDDOC_RE.sub("", text)
    text = COMMENT_RE.sub("", text)
    text = ENV_VERBATIM_RE.sub(lambda m: f"\n```\n{m.group(2).strip()}\n```\n", text)

    def _section(m: re.Match[str]) -> str:
        level = {"section": "##", "subsection": "###",
                 "subsubsection": "####", "paragraph": "#####"}[m.group(1)]
        return f"\n\n{level} {m.group(2).strip()}\n\n"

    text = SECTION_RE.sub(_section, text)
    text = TEXTBF_RE.sub(r"**\1**", text)
    text = TEXTIT_RE.sub(r"*\1*", text)
    text = TEXTTT_RE.sub(r"`\1`", text)
    text = URL_RE.sub(r"<\1>", text)
    text = HREF_RE.sub(r"[\2](\1)", text)
    text = LABEL_RE.sub("", text)
    text = ITEMIZE_BEGIN_RE.sub("\n", text)
    text = ITEMIZE_END_RE.sub("\n", text)
    text = ITEM_RE.sub("- ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ----------------------------- Driver ------------------------------------


@dataclass
class Result:
    key: str
    title: str
    arxiv_id: str | None
    status: str  # "ok", "no-arxiv", "download-fail", "extract-fail", "no-tex"
    out_file: str | None = None
    note: str = ""


ARXIV_ID_RE = re.compile(r"([a-z\-]+/\d{7}|\d{4}\.\d{4,5})(v\d+)?", re.IGNORECASE)
TITLE_STOPWORDS = {"a", "an", "the", "on", "of", "for", "and", "in", "to", "with"}


def entry_from_arxiv(spec: str) -> BibEntry | None:
    """Build a BibEntry for one arXiv paper (id, arXiv:id or abs/pdf URL),
    filling title/authors/year from the arXiv API."""
    m = ARXIV_ID_RE.search(spec)
    if not m:
        print(f"  ! not an arXiv id: {spec!r}", file=sys.stderr)
        return None
    aid = m.group(1)
    url = f"{ARXIV_API_URL}?id_list={urllib.parse.quote(aid)}&max_results=1"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            xml = r.read().decode("utf-8", errors="replace")
        time.sleep(API_DELAY_S)
    except Exception as e:
        print(f"  ! arxiv API error for {aid}: {e}", file=sys.stderr)
        xml = ""
    entry_xml = xml.split("<entry>", 1)[1] if "<entry>" in xml else ""
    title_m = re.search(r"<title>(.*?)</title>", entry_xml, re.DOTALL)
    year_m = re.search(r"<published>(\d{4})", entry_xml)
    authors = re.findall(r"<name>(.*?)</name>", entry_xml)
    title = re.sub(r"\s+", " ", title_m.group(1)).strip() if title_m else ""
    year = year_m.group(1) if year_m else ""
    last = _slugify(authors[0].split()[-1]) if authors else ""
    word = next((_slugify(w) for w in title.split()
                 if _slugify(w) and _slugify(w) not in TITLE_STOPWORDS), "")
    key = f"{last}{year}{word}" or _slugify(aid)
    fields = {"title": title, "author": " and ".join(authors),
              "year": year, "eprint": aid, "archiveprefix": "arXiv"}
    return BibEntry(key=key, entry_type="misc",
                    fields={k: v for k, v in fields.items() if v})


def process_entry(entry: BibEntry, out_dir: Path, cache_dir: Path,
                  use_pandoc: bool, force: bool,
                  search_fallback: bool = False,
                  id_overrides: dict[str, str] | None = None) -> Result:
    title = entry.title or entry.key
    aid = entry.arxiv_id
    if id_overrides and entry.key in id_overrides:
        aid = id_overrides[entry.key]
        print(f"  = {entry.key} (arXiv:{aid}, from --id override)")
    # If the .md already exists, treat as cached regardless of how aid resolves.
    md_path = out_dir / f"{entry.key}.md"
    if md_path.exists() and not force:
        cached_aid = aid
        note = "cached"
        try:
            head = md_path.read_text(encoding="utf-8", errors="replace")[:2000]
        except Exception:
            head = ""
        if not cached_aid:
            m = re.search(r"arXiv[^\w\d]*\[?([a-z\-]+/\d{7}|\d{4}\.\d{4,5})",
                          head, flags=re.IGNORECASE)
            if m:
                cached_aid = m.group(1)
        # PDF-sourced entries (no arXiv) are still "ok" — note where the
        # text came from so the index makes the distinction obvious.
        if not cached_aid and "source**: extracted from" in head:
            note = "cached (PDF)"
        return Result(entry.key, title, cached_aid, "ok",
                      out_file=md_path.name, note=note)
    if not aid and search_fallback and title:
        # First-author hint (last name) helps disambiguate common titles.
        author = entry.fields.get("author", "")
        first_au = ""
        if author:
            # Bib format "Last, First and ..." or "First Last and ..."
            first = author.split(" and ")[0]
            if "," in first:
                first_au = first.split(",", 1)[0].strip()
            else:
                first_au = first.strip().split()[-1] if first.strip() else ""
        print(f"  ? searching arXiv for {entry.key!r} by title...")
        aid = lookup_arxiv_by_title(title, first_au)
        if aid:
            print(f"    -> matched arXiv:{aid}")
    if not aid:
        return Result(entry.key, title, None, "no-arxiv",
                      note="no arXiv eprint (search fallback found nothing)"
                      if search_fallback else "no arXiv eprint field")

    md_path = out_dir / f"{entry.key}.md"
    if md_path.exists() and not force:
        return Result(entry.key, title, aid, "ok",
                      out_file=md_path.name, note="cached")

    print(f"  - {entry.key} (arXiv:{aid})")
    src_dir = cache_dir / "src"
    src_path = download_eprint(aid, src_dir)
    if src_path is None:
        return Result(entry.key, title, aid, "download-fail")

    work_dir = cache_dir / "work" / aid.replace("/", "_")
    if work_dir.exists():
        shutil.rmtree(work_dir)
    extracted, reason = extract_source(src_path, work_dir)
    if extracted is None:
        return Result(entry.key, title, aid, "extract-fail", note=reason)

    main_tex = find_main_tex(extracted)
    if main_tex is None:
        return Result(entry.key, title, aid, "no-tex")

    flat = flatten_tex(main_tex, extracted)
    md = tex_to_md_pandoc(flat) if use_pandoc else None
    if md is None:
        md = tex_to_md_light(flat)

    header = (
        f"# {title}\n\n"
        f"- **citekey**: `{entry.key}`\n"
        f"- **arXiv**: [{aid}](https://arxiv.org/abs/{aid})\n"
    )
    if entry.fields.get("author"):
        author_clean = re.sub(r'\s+', ' ', entry.fields['author'])
        header += f"- **authors**: {author_clean}\n"
    if entry.fields.get("year"):
        header += f"- **year**: {entry.fields['year']}\n"
    if entry.fields.get("journal"):
        header += f"- **journal**: {entry.fields['journal']}\n"
    if entry.fields.get("doi"):
        header += f"- **doi**: {entry.fields['doi']}\n"
    header += "\n---\n\n"

    md_path.write_text(header + md + "\n", encoding="utf-8")
    return Result(entry.key, title, aid, "ok", out_file=md_path.name)


def write_index(results: list[Result], out_dir: Path) -> None:
    lines = ["# arXiv RAG Index", ""]
    ok = [r for r in results if r.status == "ok"]
    skipped = [r for r in results if r.status != "ok"]
    lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}  ")
    lines.append(f"OK: {len(ok)} / {len(results)}  ")
    lines.append("")
    lines.append("## Papers")
    lines.append("")
    lines.append("| citekey | title | arXiv | file |")
    lines.append("|---|---|---|---|")
    for r in ok:
        aid = r.arxiv_id or ""
        link = f"[{aid}](https://arxiv.org/abs/{aid})" if aid else ""
        lines.append(f"| `{r.key}` | {r.title} | {link} | [{r.out_file}]({r.out_file}) |")
    if skipped:
        lines.append("")
        lines.append("## Skipped / failed")
        lines.append("")
        lines.append("| citekey | status | note |")
        lines.append("|---|---|---|")
        for r in skipped:
            lines.append(f"| `{r.key}` | {r.status} | {r.note} |")
    (out_dir / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bib", type=Path, default=[],
                    help="Path to .bib file (may be repeated)", action="append")
    ap.add_argument("--refs", type=Path, default=[],
                    help="Plain-text references file (may be repeated)",
                    action="append")
    ap.add_argument("--out", required=True, type=Path,
                    help="Output directory (will contain papers/ and index.md)")
    ap.add_argument("--cache", type=Path, default=None,
                    help="Cache dir for downloads & extraction (default: <out>/.cache)")
    ap.add_argument("--limit", type=int, default=0,
                    help="Process at most N new entries (0 = no limit)")
    ap.add_argument("--only", type=str, default="",
                    help="Comma-separated citekeys to restrict to")
    ap.add_argument("--force", action="store_true",
                    help="Re-process even if output .md already exists")
    ap.add_argument("--no-pandoc", action="store_true",
                    help="Skip pandoc even if installed")
    ap.add_argument("--search-fallback", action="store_true",
                    help="When an entry has no eprint, query the arXiv API by title")
    ap.add_argument("--arxiv", action="append", default=[], metavar="ID",
                    help="Single arXiv paper by id, arXiv:id or URL; no .bib needed (repeatable)")
    ap.add_argument("--id", action="append", default=[],
                    metavar="KEY=ARXIVID",
                    help="Manually inject an arXiv id for a citekey (repeatable)")
    args = ap.parse_args(argv)
    if not args.bib and not args.refs and not args.arxiv:
        ap.error("at least one of --bib, --refs or --arxiv is required")
    id_overrides: dict[str, str] = {}
    for spec in args.id:
        if "=" not in spec:
            ap.error(f"--id expects KEY=ARXIVID, got {spec!r}")
        k, v = spec.split("=", 1)
        id_overrides[k.strip()] = v.strip()

    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = args.cache or (out_dir / ".cache")
    cache_dir.mkdir(parents=True, exist_ok=True)

    only = {k.strip() for k in args.only.split(",") if k.strip()}
    use_pandoc = have_pandoc() and not args.no_pandoc
    print(f"Pandoc: {'yes' if use_pandoc else 'no (light cleanup)'}")

    entries: list[BibEntry] = []
    seen_keys: set[str] = set()
    for bib_path in args.bib:
        for e in parse_bib(bib_path):
            if e.key in seen_keys:
                continue
            seen_keys.add(e.key)
            entries.append(e)
    for refs_path in args.refs:
        for e in parse_refs_txt(refs_path):
            if e.key in seen_keys:
                continue
            seen_keys.add(e.key)
            entries.append(e)
    for spec in args.arxiv:
        e = entry_from_arxiv(spec)
        if e and e.key not in seen_keys:
            seen_keys.add(e.key)
            entries.append(e)
    print(f"Parsed {len(entries)} unique entries "
          f"from {len(args.bib)} bib + {len(args.refs)} refs file(s)"
          f" + {len(args.arxiv)} --arxiv id(s)")

    if only:
        entries = [e for e in entries if e.key in only]
        print(f"Filtered to {len(entries)} entries via --only")

    results: list[Result] = []
    processed_new = 0
    for entry in entries:
        md_path = out_dir / f"{entry.key}.md"
        is_new = not md_path.exists()
        if args.limit and is_new and processed_new >= args.limit:
            results.append(Result(entry.key, entry.title, entry.arxiv_id,
                                  "no-arxiv" if not entry.arxiv_id else "ok",
                                  out_file=md_path.name if md_path.exists() else None,
                                  note="skipped (limit reached)" if entry.arxiv_id else ""))
            continue
        r = process_entry(entry, out_dir, cache_dir, use_pandoc, args.force,
                          search_fallback=args.search_fallback,
                          id_overrides=id_overrides)
        results.append(r)
        # polite delay only when we actually hit the network
        if is_new and r.status in {"ok", "download-fail", "extract-fail", "no-tex"}:
            if r.status == "ok" and r.note != "cached":
                processed_new += 1
                time.sleep(POLITE_DELAY_S)

    write_index(results, out_dir)
    ok = sum(1 for r in results if r.status == "ok")
    print(f"\nWrote {ok}/{len(results)} -> {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
