from quran_dataset.normalize import normalize_arabic, strip_diacritics


def test_strips_harakat_and_quranic_marks():
    assert strip_diacritics("بِسْمِ ٱللَّهِ") == "بسم ٱلله"


def test_unifies_alef_forms():
    assert normalize_arabic("ٱللَّهِ أَحَدٌ إِلَٰه آمَنُوا") == "الله احد اله امنوا"


def test_ta_marbuta_and_alef_maqsura():
    assert normalize_arabic("رَحْمَةً هُدًى") == "رحمه هدي"


def test_removes_bom_and_extra_spaces():
    assert normalize_arabic("﻿قُلْ   هُوَ") == "قل هو"
