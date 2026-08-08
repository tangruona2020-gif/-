from app.services.ip_matcher import match_ip, normalize


def test_normalization():
    assert normalize(" ＳＴＥＩＮＳ；ＧＡＴＥ　～ Test ") == "steins;gate - test"


def test_japanese_english_and_abbreviation_matching():
    aliases = [(1, "メイドインアビス"), (2, "STEINS;GATE"), (3, "まどマギ")]
    assert match_ip({"title": "メイドインアビス POP UP"}, aliases).matched_ip_id == 1
    assert match_ip({"card_text": "STEINS;GATE フェア"}, aliases).matched_ip_id == 2
    assert match_ip({"detail_text": "まどマギ 開催"}, aliases).matched_ip_id == 3


def test_unrelated_does_not_match():
    assert match_ip({"title": "別作品のイベント"}, [(1, "STEINS;GATE")]) is None
