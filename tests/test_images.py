from app.services.goods_image_detector import detect_goods_images
from app.services.image_downloader import sha256_bytes


def test_goods_detection_and_hash_deduplication():
    html = (
        '<h2>商品一覧</h2><div><img src="goods.jpg" alt="GOODS lineup"></div>'
        '<img src="logo.png" alt="logo">'
    )
    assert [x.url for x in detect_goods_images(html)] == ["goods.jpg"]
    assert sha256_bytes(b"same") == sha256_bytes(b"same")
