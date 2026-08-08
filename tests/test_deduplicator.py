from app.services.event_deduplicator import compare_events


def test_same_url():
    result = compare_events(
        {"official_detail_url": "https://x/1"}, {"official_detail_url": "https://x/1"}
    )
    assert result.duplicate and result.reason == "same_detail_url"
