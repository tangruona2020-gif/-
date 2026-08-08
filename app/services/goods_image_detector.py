from dataclasses import dataclass
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag


@dataclass(slots=True)
class ImageCandidate:
    url: str
    image_type: str
    reason: str


def detect_goods_images(html: str) -> list[ImageCandidate]:
    soup = BeautifulSoup(html, "html.parser")
    found = []
    positive = ("goods", "グッズ", "商品一覧", "商品情報", "販売商品", "お品書き", "lineup", "item")
    negative = ("logo", "banner", "icon", "map", "avatar", "sns")
    for img in soup.find_all("img"):
        if not isinstance(img, Tag):
            continue
        src = img.get("data-original") or img.get("data-src") or img.get("src")
        if not src:
            continue
        parent_text = img.parent.get_text(" ", strip=True) if isinstance(img.parent, Tag) else ""
        context = " ".join(
            [
                str(img.get("alt") or ""),
                str(img.get("title") or ""),
                urlparse(str(src)).path,
                parent_text[:200],
            ]
        ).lower()
        if any(x in context for x in negative):
            continue
        width = int(str(img.get("width", "0"))) if str(img.get("width", "")).isdigit() else 0
        if any(x.lower() in context for x in positive):
            found.append(ImageCandidate(str(src), "goods_list", "goods keyword near image"))
        elif width >= 800:
            found.append(ImageCandidate(str(src), "unknown", "large image; manual review required"))
    return found
