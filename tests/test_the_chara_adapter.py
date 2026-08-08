from pathlib import Path

from app.adapters.the_chara import TheCharaAdapter

FIXTURES = Path(__file__).parent / "fixtures"


def test_cards():
    cards = TheCharaAdapter().discover_event_cards(
        (FIXTURES / "the_chara_home.html").read_text(encoding="utf-8")
    )
    assert len(cards) == 3
    assert cards[0].title == "メイドインアビス POP UP SHOP"
    assert cards[0].detail_url == "https://www.the-chara.com/event/abyss"
    assert cards[0].source_section == "開催予定のイベント"
    assert cards[2].source_section == "THEキャラ CAFE・CAFE STAND"


def test_detail_and_goods_and_entry():
    html = (FIXTURES / "the_chara_detail.html").read_text(encoding="utf-8")
    detail = TheCharaAdapter().parse_event_detail(html, "https://www.the-chara.com/event/abyss")
    assert str(detail.start_date) == "2026-08-10"
    assert detail.venue_name == "東京テストホール"
    assert detail.entry_type == "lottery"
    assert detail.candidate_images == ["https://www.the-chara.com/images/goods.jpg"]


def test_catalog_cards_are_split_into_event_and_cafe_sections():
    html = (FIXTURES / "the_chara_catalog.html").read_text(encoding="utf-8")
    cards = TheCharaAdapter().discover_catalog_cards(
        html, "https://www.the-chara.com/blog/?p=110062"
    )
    assert len(cards) == 3
    assert cards[0].source_section == "開催予定のイベント"
    assert cards[0].detail_url == "https://www.the-chara.com/blog/?p=200001"
    assert cards[2].source_section == "THEキャラ CAFE・CAFE STAND"
    assert cards[2].title == "STEINS;GATE × THEキャラCAFE"


def test_structure_health_failure():
    ok, reason = TheCharaAdapter().health_check("<html><body>changed</body></html>")
    assert not ok and "missing section" in reason


def test_missing_cafe_section_is_a_health_failure():
    html = "<section><h2>開催予定のイベント</h2><li><a href='/one'>Event</a></li></section>"
    ok, reason = TheCharaAdapter().health_check(html)
    assert not ok
    assert "THEキャラ CAFE・CAFE STAND" in reason
