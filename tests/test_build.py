from quran_dataset.build import split_bismillah

BISMILLAH = "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"


def test_removes_bismillah_prefix_from_first_ayah():
    text, removed = split_bismillah(2, 1, f"{BISMILLAH} الٓمٓ")
    assert (text, removed) == ("الٓمٓ", True)


def test_handles_shadda_variant():
    text, removed = split_bismillah(95, 1, "بِّسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ وَٱلتِّينِ وَٱلزَّيْتُونِ")
    assert removed and text == "وَٱلتِّينِ وَٱلزَّيْتُونِ"


def test_keeps_al_fatiha_first_verse():
    # In Al-Fatiha the Bismillah *is* verse 1.
    text, removed = split_bismillah(1, 1, "﻿" + BISMILLAH)
    assert (text, removed) == (BISMILLAH, False)


def test_leaves_at_tawbah_and_later_verses_alone():
    assert split_bismillah(9, 1, "بَرَآءَةٌ")[1] is False
    assert split_bismillah(2, 2, f"{BISMILLAH} x")[1] is False
