# Organise: tidy the whole library

Ingest keeps new files right; organise catches what drifts across the whole tree. Read **RULES.md** first: every verdict below is a rule applied.

1. **Survey.** `ssh gaia python3 - < lint.py` and `ssh gaia python3 - < survey.py`. Lint lists hard rule breaks; survey lists judgement candidates: composer folders that may be one person spelled twice, the same work twice in one folder, multi-file works loose in a composer folder, composers past the genre-subfolder threshold. Lint finds anything in the Inbox → run ingest.md first. Done when you hold both lists.
2. **Judge every candidate.** Open the files where the verdict depends on content (which of two editions is complete, typeset, the better scan; whether two composer folders really are one person). Each candidate ends as a move, a delete, or "fine as is" with a one-line reason. Done when every survey line has a verdict.
3. **Map.** Write `map.tsv` as in ingest.md step 5. A folder rename is one row per file inside it. Done when every move is a row, every delete is listed, and no dest collides.
4. **Review with the user.** Show the plan grouped by kind (renames, merges, deletes). Deletes of duplicates and junk are covered by the standing permission; a composer-folder rename or a new genre subfolder changes how the user browses, so it needs their yes.
5. **Apply and verify** as in ingest.md steps 7–8. Done when lint prints `clean` and a re-run of survey shows only the candidates you judged "fine as is".
