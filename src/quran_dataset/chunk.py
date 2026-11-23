"""Three chunking strategies for verse-level Quran data, plus stats to compare them."""

from __future__ import annotations

import statistics
from itertools import groupby


def _chunk(kind: str, verses: list[dict]) -> dict:
    first, last = verses[0], verses[-1]
    ref = first["id"] if first is last else f"{first['id']}-{last['ayah']}"
    return {
        "id": f"{kind}/{ref}",
        "strategy": kind,
        "surah": first["surah"],
        "verse_ids": [v["id"] for v in verses],
        "text_ar": " ".join(v["text_ar"] for v in verses),
        "text_en": " ".join(v["text_en"] for v in verses),
    }


def by_verse(verses: list[dict]) -> list[dict]:
    """One chunk per verse. Precise citations, but short verses lack context."""
    return [_chunk("verse", [v]) for v in verses]


def by_window(verses: list[dict], size: int = 3, stride: int = 2) -> list[dict]:
    """Overlapping windows of `size` verses, never crossing a surah boundary."""
    if size < 1 or stride < 1:
        raise ValueError("size and stride must be >= 1")
    chunks = []
    for _, group in groupby(verses, key=lambda v: v["surah"]):
        surah = list(group)
        start = 0
        while True:
            chunks.append(_chunk(f"window{size}", surah[start : start + size]))
            if start + size >= len(surah):
                break
            start += stride
    return chunks


def by_ruku(verses: list[dict]) -> list[dict]:
    """One chunk per ruku: the traditional thematic section (556 in total)."""
    return [_chunk("ruku", list(g)) for _, g in groupby(verses, key=lambda v: v["ruku"])]


def stats(chunks: list[dict]) -> dict:
    words_en = [len(c["text_en"].split()) for c in chunks]
    words_ar = [len(c["text_ar"].split()) for c in chunks]
    verses = [len(c["verse_ids"]) for c in chunks]
    return {
        "chunks": len(chunks),
        "verses_mean": round(statistics.mean(verses), 1),
        "words_en_mean": round(statistics.mean(words_en)),
        "words_en_median": statistics.median(words_en),
        "words_en_max": max(words_en),
        "words_ar_mean": round(statistics.mean(words_ar)),
        "under_10_words_en": sum(w < 10 for w in words_en),
    }


STRATEGIES = {
    "verse": by_verse,
    "window3": by_window,
    "ruku": by_ruku,
}
