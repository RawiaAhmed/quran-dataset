"""Download the Quran from the Quran Cloud API and build a verse-level dataset."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

from .normalize import normalize_arabic

API = "https://api.alquran.cloud/v1/quran/{edition}"
ARABIC_EDITION = "quran-uthmani"
ENGLISH_EDITION = "en.sahih"
TOTAL_VERSES = 6236
BISMILLAH_WORDS = 4  # بسم الله الرحمن الرحيم


def fetch_edition(edition: str, cache_dir: Path) -> dict:
    """Return the API `data` object for an edition, cached on disk."""
    cache = cache_dir / f"{edition}.json"
    if not cache.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(API.format(edition=edition), headers={"User-Agent": "quran-dataset"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.load(resp)
        if payload.get("code") != 200:
            raise RuntimeError(f"API error for {edition}: {payload.get('status')}")
        cache.write_text(json.dumps(payload["data"], ensure_ascii=False), encoding="utf-8")
    return json.loads(cache.read_text(encoding="utf-8"))


def split_bismillah(surah: int, ayah: int, text: str) -> tuple[str, bool]:
    """The Uthmani edition prefixes ayah 1 of every surah except 1 and 9 with the
    Bismillah. Return (text without it, whether it was removed)."""
    text = text.replace("﻿", "")
    if ayah != 1 or surah in (1, 9):
        return text, False
    words = text.split(" ")
    if normalize_arabic(words[0]).startswith("بسم") and len(words) > BISMILLAH_WORDS:
        return " ".join(words[BISMILLAH_WORDS:]), True
    return text, False


def merge(arabic: dict, english: dict) -> list[dict]:
    verses = []
    for s_ar, s_en in zip(arabic["surahs"], english["surahs"], strict=True):
        for a_ar, a_en in zip(s_ar["ayahs"], s_en["ayahs"], strict=True):
            assert a_ar["number"] == a_en["number"], "editions out of sync"
            surah, ayah = s_ar["number"], a_ar["numberInSurah"]
            text_ar, had_bismillah = split_bismillah(surah, ayah, a_ar["text"])
            verses.append(
                {
                    "id": f"{surah}:{ayah}",
                    "number": a_ar["number"],
                    "surah": surah,
                    "ayah": ayah,
                    "surah_name_ar": s_ar["name"],
                    "surah_name_en": s_ar["englishName"],
                    "surah_meaning_en": s_ar["englishNameTranslation"],
                    "revelation": s_ar["revelationType"],
                    "juz": a_ar["juz"],
                    "hizb_quarter": a_ar["hizbQuarter"],
                    "ruku": a_ar["ruku"],
                    "page": a_ar["page"],
                    "sajda": bool(a_ar["sajda"]),
                    "bismillah_prefix": had_bismillah,
                    "text_ar": text_ar,
                    "text_ar_plain": normalize_arabic(text_ar),
                    "text_en": a_en["text"],
                }
            )
    if len(verses) != TOTAL_VERSES:
        raise ValueError(f"expected {TOTAL_VERSES} verses, got {len(verses)}")
    return verses


def write_jsonl(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def build(data_dir: Path) -> list[dict]:
    raw = data_dir / "raw"
    verses = merge(fetch_edition(ARABIC_EDITION, raw), fetch_edition(ENGLISH_EDITION, raw))
    write_jsonl(verses, data_dir / "verses.jsonl")
    return verses
