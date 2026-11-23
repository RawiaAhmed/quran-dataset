# quran-dataset

[![CI](https://github.com/RawiaAhmed/quran-dataset/actions/workflows/ci.yml/badge.svg)](https://github.com/RawiaAhmed/quran-dataset/actions/workflows/ci.yml)

A clean, verse-level dataset of the Quran in Arabic (Uthmani script) and English (Saheeh International), plus three chunking strategies measured side by side. It is the data layer for a bilingual RAG system: before choosing an embedding model or a retriever, you need to know what a "document" is.

Built with the Python standard library only. One command downloads, cleans and chunks all 6,236 verses.

```bash
uv sync
uv run quran-dataset build     # downloads to data/, writes verses + chunks, prints the table below
```

## Chunking: measured, not guessed

| strategy | chunks | verses per chunk | English words (mean) | median | max | Arabic words (mean) | chunks under 10 English words |
|---|---|---|---|---|---|---|---|
| `verse` | 6,236 | 1 | 25 | 21 | 256 | 13 | **1,052** |
| `window3` (3 verses, stride 2) | 3,091 | 3.0 | 77 | 71 | 350 | 39 | 1 |
| `ruku` | 556 | 11.2 | 286 | 287 | 614 | 147 | 0 |

What the numbers say:

- **Per-verse chunks give exact citations but 17% of them are under 10 words.** Verses like "Alif, Lam, Meem." or "By the fig and the olive" carry almost no meaning on their own, so an embedding of them is mostly noise.
- **Ruku sections are the traditional thematic units**, so each chunk is about one subject. They are long (≈290 English words), which dilutes the embedding and makes the citation a range of ~11 verses.
- **Overlapping 3-verse windows are the middle ground**: short chunks almost disappear (1 left), every verse appears in at least one window, and windows never cross a surah boundary.

Day 2 tests these against real questions with Recall@5 instead of word counts.

## Cleaning decisions

**The Bismillah is split off the first verse.** The Uthmani edition prefixes verse 1 of every surah with "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ", but it is only counted as a verse in Al-Fatiha (1:1), and Surah At-Tawbah (9) has none. Left in, the same four words would be embedded 112 times and match every query about mercy. The prefix is removed and recorded in `bismillah_prefix` so nothing is lost.

**The match is on normalized text, not raw bytes.** Some surahs spell the first word "بِّسْمِ" (with a shadda), so an exact string match misses them. Matching on the normalized form catches every variant.

**Two Arabic fields, for two jobs.** `text_ar` keeps full diacritics for display and citation. `text_ar_plain` strips harakat and Quranic marks, unifies alef forms (أ إ آ ٱ → ا), alef maqsura (ى → ي) and ta marbuta (ة → ه). That is what keyword search should match against, because users type "الرحمن" not "ٱلرَّحْمَٰنِ".

**Downloads are cached.** Raw API responses land in `data/raw/`, so rebuilding does not hit the API again.

## Output

`data/verses.jsonl`, one verse per line:

```json
{"id": "2:1", "surah": 2, "ayah": 1, "surah_name_ar": "سُورَةُ البَقَرَةِ", "surah_name_en": "Al-Baqara",
 "revelation": "Medinan", "juz": 1, "hizb_quarter": 1, "ruku": 2, "page": 2, "sajda": false,
 "bismillah_prefix": true, "text_ar": "الٓمٓ", "text_ar_plain": "الم", "text_en": "Alif, Lam, Meem."}
```

`data/chunks/{verse,window3,ruku}.jsonl`, one chunk per line with `verse_ids` for citations.

## Tests

```bash
uv run pytest              # 15 offline tests: normalization, Bismillah handling, chunk boundaries
uv run pytest -m network   # full build against the live API: 6,236 verses, 112 Bismillah prefixes, 15 sajda verses
```

## Data source and licence

Text comes from the [Quran Cloud API](https://alquran.cloud/api) (editions `quran-uthmani` and `en.sahih`). The generated data is not committed: run the build to get it, and check the API's terms before redistributing. The code is MIT licensed.

## Part of a series

Day 1 of a bilingual Quran RAG project:

1. **quran-dataset**: data and chunking (this repo)
2. [arabic-embed-bench](https://github.com/RawiaAhmed/arabic-embed-bench): which embedding model retrieves Arabic and English best
3. quran-rag: hybrid search, reranking and verse-cited answers
