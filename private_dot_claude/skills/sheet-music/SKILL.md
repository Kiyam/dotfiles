---
name: sheet-music
description: File new sheet music on gaia into the organised library (instrument → composer → work), merging scans into PDFs and deleting junk.
disable-model-invocation: true
---

# Sheet music

The library is `gaia:/srv/mergerfs/gaia_data/gaia-library/Sheet Music` (ssh host `gaia`, user `ruyi`, no root). The user drops new files into `Sheet Music/Inbox/`, or occasionally straight into the tree; your job is to make the whole library obey **the rules** below again.

Standing permission from the user: delete anything junk, broken, incomplete, duplicate or confusing inside this folder without asking. It can all be re-fetched from IMSLP.

Work in a scratch dir on the Mac; never edit the library by hand except through `apply.py` and the deletions the rules call for.

## Steps

1. **Lint.** `ssh gaia python3 - < lint.py` (this skill's dir). It lists Inbox contents and every file breaking a mechanical rule. Done when you hold the list.
2. **Unpack.** Archives (`.zip .rar .7z`) in the list: extract on gaia into a sibling folder (see *Tools*), then delete the archive. Garbled names are GBK: re-decode with `bytes.decode('gb18030')`. Re-run lint. Done when lint shows no archives.
3. **Identify.** For every flagged file, open page 1 (copy it to scratch with `scp`/`tar`, view with Read; `qpdf --empty --pages f.pdf 1 -- p1.pdf` for big PDFs, `sips -s format png` for tif/bmp). Determine composer, work, catalogue number, instrumentation, part, arranger, and page order for image sets. Read titles and composers off the page, never from the filename alone: source folders are often mislabelled. Done when every flagged file has an identity or a delete verdict.
4. **Map.** Write `map.tsv` (`src<TAB>dest`, paths relative to the library root). Image pages of one piece share one `.pdf` dest, rows in page order. Check each dest against what already exists (`ssh gaia "ls '…/<Instrument>/<Composer>'"`): same piece already present → keep the better copy (complete > incomplete, typeset > scan, one edition only) and delete the other. Done when every flagged file is either mapped or listed for deletion, and no dest collides.
5. **Review with the user** when anything is uncertain (composer read from memory, ambiguous instrumentation); otherwise proceed.
6. **Apply.** `scp map.tsv gaia:sheet-map.tsv && ssh gaia python3 - sheet-map.tsv < apply.py`. It moves/merges each src to its dest, refuses to overwrite, and deletes merged sources. Then delete the files on your delete list and any empty folders.
7. **Verify.** Re-run lint: done when it reports nothing. Spot-check one merged PDF visually. Remove `~/sheet-map.tsv` on gaia.

## The rules

### Layout
```
Violin/<Composer>/…          solo violin, violin + piano, violin concertos
Violin/Studies/<Author>/…    etudes, methods, scales
Piano/<Composer>/…           Piano/Studies/ABRSM Grade N/…
Cello/<Composer>/…           cello + piano (same for any other solo instrument)
Voice/<Composer>/…           songs, jianpu
Chamber/{Duo,Trio,Quartet,Quintet,String Orchestra}/<Composer>/…
Collections/<Book title>/…   multi-composer books kept together
```
- Instrument = what the sheet is **for** (the arrangement's forces, not the original's). Violin + piano accompaniment → `Violin`. Two violins, violin + cello → `Chamber/Duo`.
- Concerto with piano reduction → `Violin/<Composer>/<Work>/`; its orchestral parts → `<Work>/Parts/`; full score → `<Work> - Score.pdf`.
- Orchestral/choral works with no solo or chamber role have no home: delete.
- Genre subfolder inside a composer (`Piano/Chopin/Nocturnes/`) once that composer has more than ~10 works of one genre.

### Composer folders
- Surname, common English spelling, ASCII: `Tchaikovsky`, `Dvorak`, `Saint-Saens`. Disambiguate: `Bach, J.C.`, `Strauss, Johann II`, `Strauss, Richard`.
- Chinese people: `Pinyin 汉字`, family name first: `Ma Sicong 马思聪`, `Chen Gang 陈钢 & He Zhanhao 何占豪`. Same form for arrangers.
- No composer: `Traditional (Chinese)`, `Traditional (<Country>)`; film/TV themes → `Film`; jazz standards → `Jazz`.
- Arrangements: folder = **original** composer, arranger in the name `(arr. Heifetz)`. Exception: Kreisler's own pieces and pastiches (Liebesleid, Praeludium & Allegro, "in the style of…") → `Kreisler`.

### File names
`<Work>[ <catalogue>][ (arr. X)][ - <Part>].pdf`
- English title, Title Case: `Violin Sonata No.5 in F Op.24 'Spring'`, `Nocturne Op.9 No.2`, `String Quartet in G K.387`. Styles: `No.5`, `Op.24`, `K.387`, `BWV 1042`, `D.574`, `RV 269`.
- Chinese works: `English - Pinyin (汉字)` when an established English title exists (`Butterfly Lovers Violin Concerto - Liang Zhu (梁祝)`), else `Pinyin (汉字) - English` (`Liangxiao (良宵) - A Beautiful Evening`). Under ~120 characters.
- Multi-file works (parts, separate movements) get a folder named like the work: `Violin/Bach/Violin Concerto No.2 in E BWV 1042/Violin Concerto No.2 in E BWV 1042 - Solo Violin.pdf`. Single-file works sit directly in the composer folder.
- Parts: `Score`, `Violin`, `Piano`, `Violin 1`, `Violin 2`, `Viola`, `Cello`, `Double Bass`, `Solo Violin`, `Continuo`, … Movements: `- I. Allegro` or `- Mvt 1`.
- No `/ \ : * ? " < > |`; plain ASCII apostrophe.

### Keep and delete
- Keep: `.pdf` (scores), `.mp3` only for ABRSM backing tracks, `.doc/.docx` programme notes beside their work.
- Image scans (`jpg gif tif bmp png`) are never kept loose: merge into one PDF per piece/part.
- Delete: MIDI, Finale/Sibelius files (`.mus .sib`), web leftovers (`.htm`, `*_files/`), `.url .txt .db .ini`, installers, OS junk (`.DS_Store`, `Thumbs.db`), archives once extracted.
- Delete broken or incomplete scores (missing pages, truncated PDFs, unidentifiable fragments), photos that aren't music, and extra editions: one copy per piece/part, never `(alt)` or `(2)` names.

## Tools

gaia has `python3-img2pdf`, `python3-pil`, `7zip` (command `7z`) and `unar` installed. If one is missing, ask the user to install it (you have no root).
- Zip/7z: `7z x -o<dir> <archive>`. RAR, or any archive with GBK names: `unar -e GB18030 -D -o <dir> <archive>`.
- Long remote commands: write a script locally, `scp` it, run it. Inline quoting through ssh breaks on spaces and CJK.
