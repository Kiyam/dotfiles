---
name: sheet-music
description: Sheet music library on gaia. search (find a piece on IMSLP and file it), ingest (file the Inbox or IMSLP links), organise (tidy the whole library).
disable-model-invocation: true
---

# Sheet music

The library is `gaia:/srv/mergerfs/gaia_data/gaia-library/Sheet Music` (ssh host `gaia`, user `ruyi`, no root), laid out by **RULES.md** in this skill's dir. New files arrive in `Sheet Music/Inbox/`.

Standing permission from the user: delete anything junk, broken, incomplete, duplicate or confusing inside this folder without asking. It can all be re-fetched from IMSLP.

Every change to the library goes through `apply.py` or a deletion the rules call for, so work in a scratch dir on the Mac and keep the library itself untouched by hand.

## Modes

The first word of the arguments picks the mode; read its file and follow it.

- `search <piece>`: find it on IMSLP, have the user download it, file it. **search.md**
- `ingest [IMSLP links…]`: fetch any links, then file everything in the Inbox. **ingest.md**
- `organise`: whole-library tidy beyond what ingest touches. **organise.md**

No mode given: run `lint.py` (see ingest.md); a non-empty Inbox means ingest, otherwise ask.

## Tools

- `imslp.py` (Mac): `search "<query>"` lists IMSLP work pages; `work "<title or URL>"` lists every edition with publisher, editors, licence, an EU copyright status, and a direct link per file.
- `lint.py`, `survey.py`, `apply.py` run on gaia: `ssh gaia python3 - [args] < <script>`.
- gaia has `python3-img2pdf`, `python3-pil`, `7zip` (command `7z`) and `unar`. If one is missing, ask the user to install it (you have no root). Zip/7z: `7z x -o<dir> <archive>`. RAR, or any archive with GBK names: `unar -e GB18030 -D -o <dir> <archive>`.
- Long remote commands: write a script locally, `scp` it, run it. Inline quoting through ssh breaks on spaces and CJK.
