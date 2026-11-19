# Ingest: file new music into the library

Every rule referred to here is in **RULES.md**; read it before step 4.

1. **Fetch links** (only when the user gave IMSLP links). A work page link → run search.md steps 3–5 on it. A direct file link → the user already chose it: run search.md steps 4–5 for it. Done when every linked file is in the Inbox.
2. **Lint.** `ssh gaia python3 - < lint.py`. It lists Inbox contents and every file breaking a mechanical rule anywhere in the library. Done when you hold the list.
3. **Unpack.** Archives (`.zip .rar .7z`) in the list: extract on gaia into a sibling folder (see *Tools* in SKILL.md), then delete the archive. Garbled names are GBK: re-decode with `bytes.decode('gb18030')`. Re-run lint. Done when lint shows no archives.
4. **Identify.** For every flagged file, open page 1 (copy it to scratch with `scp`/`tar`, view with Read; `qpdf --empty --pages f.pdf 1 -- p1.pdf` for big PDFs, `sips -s format png` for tif/bmp). Determine composer, work, catalogue number, instrumentation, part, arranger, and page order for image sets. Read titles and composers off the page, never from the filename alone: source folders are often mislabelled. Done when every flagged file has an identity or a delete verdict.
5. **Map.** Write `map.tsv` (`src<TAB>dest`, paths relative to the library root). Image pages of one piece share one `.pdf` dest, rows in page order. Check each dest against what already exists (`ssh gaia "ls '…/<Instrument>/<Composer>'"`): same piece already present → keep the better copy (complete > incomplete, typeset > scan, one edition only) and delete the other. Done when every flagged file is either mapped or listed for deletion, and no dest collides.
6. **Review with the user** when anything is uncertain (composer read from memory, ambiguous instrumentation); otherwise proceed.
7. **Apply.** `scp map.tsv gaia:sheet-map.tsv && ssh gaia python3 - sheet-map.tsv < apply.py`. It moves/merges each src to its dest, refuses to overwrite, and deletes merged sources. Then delete the files on your delete list and any empty folders.
8. **Verify.** Re-run lint: done when it prints `clean`. Spot-check one merged PDF visually. Remove `~/sheet-map.tsv` on gaia. Tell the user where each new piece now lives.
