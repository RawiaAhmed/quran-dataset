"""Arabic text normalization for search and matching."""

import re

# Tashkeel (harakat), Quranic annotation marks, tatweel, and the small high/low signs.
_DIACRITICS = re.compile(
    "["
    "ؐ-ؚ"  # honorifics and small signs
    "ً-ٟ"  # harakat: fathatan .. wavy hamza below
    "ٰ"  # superscript (dagger) alef
    "ۖ-ۭ"  # Quranic annotation signs
    "࣓-ࣿ"  # extended Arabic marks
    "ـ"  # tatweel
    "]"
)
_ALEF = re.compile("[آأإٱٲٳ]")  # آ أ إ ٱ -> ا
_SPACES = re.compile(r"\s+")


def strip_diacritics(text: str) -> str:
    return _DIACRITICS.sub("", text)


def normalize_arabic(text: str) -> str:
    """Return a plain form of Arabic text for keyword search.

    Removes diacritics and Quranic marks, unifies alef forms, alef maqsura -> ya,
    ta marbuta -> ha, and collapses whitespace. Lossy: use only for matching.
    """
    text = text.replace("﻿", "")
    text = strip_diacritics(text)
    text = _ALEF.sub("ا", text)
    text = text.replace("ى", "ي")  # ى -> ي
    text = text.replace("ة", "ه")  # ة -> ه
    return _SPACES.sub(" ", text).strip()
