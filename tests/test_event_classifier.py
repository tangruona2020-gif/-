from app.services.event_classifier import classify_event


def test_popup_classification():
    assert classify_event("期間限定 POP UP SHOP 開催") == "popup_shop"


def test_plain_goods_is_other():
    assert classify_event("新商品をオンラインストアで発売") == "other"
