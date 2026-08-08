def classify_event(text: str) -> str:
    value = text.lower()
    online_words = ("オンライン", "通販")
    offline_words = (
        "pop up",
        "popup",
        "ポップアップ",
        "期間限定ショップ",
        "期間限定ストア",
        "カフェ",
        "展示",
        "会場",
    )
    if any(word in value for word in online_words) and any(word in value for word in offline_words):
        return "offline_and_online"
    rules = [
        ("collaboration_cafe", ("コラボカフェ", "collaboration cafe")),
        ("only_shop", ("only shop", "オンリーショップ")),
        ("exhibition", ("展覧会", "展示会", "記念展")),
        ("store_fair", ("店舗フェア", "フェア")),
        ("limited_shop", ("期間限定ショップ", "期間限定ストア")),
        ("popup_shop", ("pop up shop", "popup shop", "ポップアップショップ", "ポップアップストア")),
    ]
    for kind, words in rules:
        if any(word in value for word in words):
            return kind
    return "other"
