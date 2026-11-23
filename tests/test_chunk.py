import pytest

from quran_dataset.chunk import by_ruku, by_verse, by_window, stats


def verse(surah, ayah, ruku):
    return {"id": f"{surah}:{ayah}", "surah": surah, "ayah": ayah, "ruku": ruku,
            "text_ar": f"ar{surah}.{ayah}", "text_en": f"en {surah} {ayah}"}


# Surah 1 has 5 verses (ruku 1); surah 2 has 4 verses (ruku 2, 3).
VERSES = [verse(1, a, 1) for a in range(1, 6)] + [verse(2, 1, 2), verse(2, 2, 2), verse(2, 3, 3), verse(2, 4, 3)]


def test_by_verse_is_one_to_one():
    chunks = by_verse(VERSES)
    assert len(chunks) == len(VERSES)
    assert chunks[0]["id"] == "verse/1:1"


def test_windows_never_cross_surahs():
    for c in by_window(VERSES, size=3, stride=2):
        assert len({vid.split(":")[0] for vid in c["verse_ids"]}) == 1


def test_windows_cover_every_verse():
    covered = {vid for c in by_window(VERSES, size=3, stride=2) for vid in c["verse_ids"]}
    assert covered == {v["id"] for v in VERSES}


def test_window_ids_show_range():
    assert by_window(VERSES, size=3, stride=2)[0]["id"] == "window3/1:1-3"


def test_window_rejects_bad_params():
    with pytest.raises(ValueError):
        by_window(VERSES, size=0)


def test_by_ruku_groups_sections():
    assert [c["verse_ids"] for c in by_ruku(VERSES)] == [
        ["1:1", "1:2", "1:3", "1:4", "1:5"], ["2:1", "2:2"], ["2:3", "2:4"]]


def test_stats_counts():
    s = stats(by_verse(VERSES))
    assert s["chunks"] == 9 and s["verses_mean"] == 1.0
