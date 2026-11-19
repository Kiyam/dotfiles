# Sheet music library rules

## Layout
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

## Composer folders
- Surname, common English spelling, ASCII: `Tchaikovsky`, `Dvorak`, `Saint-Saens`. Disambiguate: `Bach, J.C.`, `Strauss, Johann II`, `Strauss, Richard`.
- Chinese people: `Pinyin 汉字`, family name first: `Ma Sicong 马思聪`, `Chen Gang 陈钢 & He Zhanhao 何占豪`. Same form for arrangers.
- No composer: `Traditional (Chinese)`, `Traditional (<Country>)`; film/TV themes → `Film`; jazz standards → `Jazz`.
- Arrangements: folder = **original** composer, arranger in the name `(arr. Heifetz)`. Exception: Kreisler's own pieces and pastiches (Liebesleid, Praeludium & Allegro, "in the style of…") → `Kreisler`.

## File names
`<Work>[ <catalogue>][ (arr. X)][ - <Part>].pdf`
- English title, Title Case: `Violin Sonata No.5 in F Op.24 'Spring'`, `Nocturne Op.9 No.2`, `String Quartet in G K.387`. Styles: `No.5`, `Op.24`, `K.387`, `BWV 1042`, `D.574`, `RV 269`.
- Chinese works: `English - Pinyin (汉字)` when an established English title exists (`Butterfly Lovers Violin Concerto - Liang Zhu (梁祝)`), else `Pinyin (汉字) - English` (`Liangxiao (良宵) - A Beautiful Evening`). Under ~120 characters.
- Multi-file works (parts, separate movements) get a folder named like the work: `Violin/Bach/Violin Concerto No.2 in E BWV 1042/Violin Concerto No.2 in E BWV 1042 - Solo Violin.pdf`. Single-file works sit directly in the composer folder.
- Parts: `Score`, `Violin`, `Piano`, `Violin 1`, `Violin 2`, `Viola`, `Cello`, `Double Bass`, `Solo Violin`, `Continuo`, … Movements: `- I. Allegro` or `- Mvt 1`.
- No `/ \ : * ? " < > |`; plain ASCII apostrophe.

## Keep and delete
- Keep: `.pdf` (scores), `.mp3` only for ABRSM backing tracks, `.doc/.docx` programme notes beside their work.
- Image scans (`jpg gif tif bmp png`) are never kept loose: merge into one PDF per piece/part.
- Delete: MIDI, Finale/Sibelius files (`.mus .sib`), web leftovers (`.htm`, `*_files/`), `.url .txt .db .ini`, installers, OS junk (`.DS_Store`, `Thumbs.db`), archives once extracted.
- Delete broken or incomplete scores (missing pages, truncated PDFs, unidentifiable fragments), photos that aren't music, and extra editions: one copy per piece/part, never `(alt)` or `(2)` names.
