"""Full build against the real API. Run with: uv run pytest -m network"""

import pytest

from quran_dataset.build import TOTAL_VERSES, build


@pytest.mark.network
def test_full_build(tmp_path):
    verses = build(tmp_path)
    assert len(verses) == TOTAL_VERSES
    by_id = {v["id"]: v for v in verses}
    assert by_id["1:1"]["bismillah_prefix"] is False
    assert by_id["2:1"]["bismillah_prefix"] is True
    assert by_id["2:255"]["text_en"].startswith("Allah - there is no deity")
    assert sum(v["bismillah_prefix"] for v in verses) == 112  # 114 surahs minus 1 and 9
    assert sum(v["sajda"] for v in verses) == 15
