import re
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup, Tag

from app.adapters.base import BaseAdapter, EventCard, ParsedEventDetail
from app.config import get_settings
from app.services.date_parser import parse_date_range
from app.services.event_classifier import classify_event
from app.services.goods_image_detector import detect_goods_images

SELECTORS = {
    "section": ["section", "div"],
    "card": ["article", "li", ".event", ".event-item", ".event_list_item"],
    "title": ["h1", "h2", "h3", "h4", ".title"],
}
TARGET_SECTIONS = ("開催予定のイベント", "THEキャラ CAFE・CAFE STAND")
CATALOG_SECTIONS = {
    "過去のイベント一覧": "開催予定のイベント",
    "過去のカフェ一覧": "THEキャラ CAFE・CAFE STAND",
}


class TheCharaAdapter(BaseAdapter):
    adapter_key = "the_chara"
    source_name = "THEキャラ"
    start_url = "https://www.the-chara.com/"

    async def discover(self) -> list[EventCard]:
        homepage = await self.fetch_event_detail(self.start_url)
        navigation_cards = self.discover_event_cards(homepage, self.start_url)
        catalog_urls = list(
            dict.fromkeys(card.detail_url.split("#", 1)[0] for card in navigation_cards)
        )
        if len(catalog_urls) != 1:
            raise ValueError(
                "THEキャラ page structure changed: target sections do not share one catalog URL"
            )
        catalog_html = await self.fetch_event_detail(catalog_urls[0])
        return self.discover_catalog_cards(catalog_html, catalog_urls[0])

    def discover_catalog_cards(self, html: str, base_url: str) -> list[EventCard]:
        soup = BeautifulSoup(html, "html.parser")
        cards: list[EventCard] = []
        seen: set[str] = set()
        current_section: str | None = None

        for heading in soup.find_all(["h2", "h3"]):
            if not isinstance(heading, Tag):
                continue
            title = heading.get_text(" ", strip=True)
            if heading.name == "h2":
                current_section = CATALOG_SECTIONS.get(title)
                continue
            if current_section is None or "widget-title" not in (heading.get("class") or []):
                continue

            link: Tag | None = None
            container: Tag | None = None
            for ancestor in heading.parents:
                if not isinstance(ancestor, Tag):
                    continue
                candidates = []
                for candidate in ancestor.find_all("a", href=True):
                    if not isinstance(candidate, Tag):
                        continue
                    target = urljoin(base_url, str(candidate["href"]))
                    if "/blog/?p=" in target and "p=110062" not in target:
                        candidates.append(candidate)
                unique_urls = {
                    urljoin(base_url, str(candidate["href"])) for candidate in candidates
                }
                if len(unique_urls) == 1:
                    link = candidates[0]
                    container = ancestor
                    break
                if ancestor.name in {"article", "main"}:
                    break
            if link is None or container is None:
                continue

            detail_url = urljoin(base_url, str(link["href"]))
            if detail_url in seen:
                continue
            image = container.find("img")
            image_url = None
            if isinstance(image, Tag):
                raw_image_url = image.get("data-src") or image.get("src")
                if raw_image_url:
                    image_url = urljoin(base_url, str(raw_image_url))
            summary = container.get_text(" ", strip=True)
            date_match = re.search(r"20\d{2}[^\n]{0,80}(?:日|まで|～|〜|-)", summary)
            cards.append(
                EventCard(
                    title=title,
                    detail_url=detail_url,
                    image_url=image_url,
                    summary_text=summary,
                    raw_date_text=date_match.group(0) if date_match else "",
                    source_position=len(cards),
                    source_section=current_section,
                )
            )
            seen.add(detail_url)

        missing = [
            section
            for section in TARGET_SECTIONS
            if not any(c.source_section == section for c in cards)
        ]
        if missing:
            raise ValueError(
                "THEキャラ catalog structure changed: no cards for section(s): "
                + ", ".join(missing)
            )
        return cards

    def _sections(self, soup: BeautifulSoup) -> list[tuple[str, Tag]]:
        sections: list[tuple[str, Tag]] = []
        missing: list[str] = []
        for label in TARGET_SECTIONS:
            heading = soup.find(
                lambda node, expected=label: isinstance(node, Tag)
                and node.name in {"h1", "h2", "h3", "h4"}
                and node.get_text(" ", strip=True) == expected
            )
            if not isinstance(heading, Tag):
                missing.append(label)
                continue
            section = heading.find_parent("section")
            container = section if isinstance(section, Tag) else heading.parent
            if not isinstance(container, Tag):
                missing.append(label)
                continue
            sections.append((label, container))
        if missing:
            labels = ", ".join(missing)
            raise ValueError(f"THEキャラ page structure changed: missing section(s): {labels}")
        return sections

    def discover_event_cards(self, html: str, base_url: str | None = None) -> list[EventCard]:
        soup = BeautifulSoup(html, "html.parser")
        cards: list[EventCard] = []
        seen: set[str] = set()
        position = 0
        for section_name, section in self._sections(soup):
            candidates: list[Tag] = list(section.select(",".join(SELECTORS["card"])))
            if not candidates:
                candidates = [
                    a.parent
                    for a in section.find_all("a", href=True)
                    if isinstance(a, Tag) and isinstance(a.parent, Tag)
                ]
            section_count = 0
            for node in candidates:
                try:
                    card = self.parse_event_card(node, position)
                    card.detail_url = urljoin(base_url or self.start_url, card.detail_url)
                    card.source_section = section_name
                    if card.image_url:
                        card.image_url = urljoin(base_url or self.start_url, card.image_url)
                    if card.detail_url not in seen:
                        seen.add(card.detail_url)
                        cards.append(card)
                        position += 1
                        section_count += 1
                except ValueError:
                    continue
            if section_count == 0:
                raise ValueError(
                    f"THEキャラ page structure changed: section has no cards: {section_name}"
                )
        if not cards:
            raise ValueError(
                "THEキャラ page structure changed: upcoming section has no event cards"
            )
        return cards

    def parse_event_card(self, element: object, position: int = 0) -> EventCard:
        if not isinstance(element, Tag):
            raise ValueError("card is not a DOM element")
        link = element if element.name == "a" else element.find("a", href=True)
        if not isinstance(link, Tag) or not link.get("href"):
            raise ValueError("card link missing")
        title_node = element.select_one(",".join(SELECTORS["title"]))
        image = element.find("img")
        title = (title_node or link).get_text(" ", strip=True)
        if not title and isinstance(image, Tag):
            title = str(image.get("alt") or "").strip()
        if not title:
            raise ValueError("card title missing")
        text = element.get_text(" ", strip=True)
        date_match = re.search(r"20\d{2}[^\n]{0,50}(?:日|まで|～|〜|-)", text)
        image_url = None
        if isinstance(image, Tag):
            image_url = image.get("data-src") or image.get("src")
        return EventCard(
            title,
            str(link["href"]),
            str(image_url) if image_url else None,
            text,
            date_match.group(0) if date_match else "",
            position,
        )

    async def fetch_event_detail(self, url: str) -> str:
        settings = get_settings()
        if not settings.enable_external_requests:
            raise RuntimeError("External requests are disabled")
        async with httpx.AsyncClient(
            timeout=settings.http_timeout_seconds,
            headers={"User-Agent": "GoodsPopupMonitor/0.1 (+personal research)"},
            follow_redirects=True,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    def parse_event_detail(self, html: str, url: str) -> ParsedEventDetail:
        soup = BeautifulSoup(html, "html.parser")
        title_node = soup.select_one("h1, main h2, article h2")
        if not title_node:
            raise ValueError("detail title missing")
        text = soup.get_text("\n", strip=True)
        start, end = parse_date_range(text)

        def labeled(*labels: str) -> str | None:
            for label in labels:
                match = re.search(rf"{re.escape(label)}\s*[：:]?\s*([^\n]+)", text)
                if match:
                    return match.group(1).strip()
            return None

        entry = self.parse_entry_information(html, url)
        return ParsedEventDetail(
            title=title_node.get_text(" ", strip=True),
            description=text,
            start_date=start,
            end_date=end,
            business_hours_text=labeled("営業時間"),
            venue_name=labeled("会場", "開催場所"),
            address=labeled("住所", "所在地"),
            event_type=classify_event(text),
            entry_type=str(entry["entry_type"]),
            entry_summary=str(entry["original_text"]) if entry["original_text"] else None,
            related_urls=self.find_related_pages(html, url),
            candidate_images=self.find_goods_images(html, url),
            raw_entry_text=str(entry["original_text"]) if entry["original_text"] else None,
        )

    def find_related_pages(self, html: str, url: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        result = []
        keys = (
            "商品",
            "GOODS",
            "グッズ",
            "詳細",
            "入場",
            "整理券",
            "抽選",
            "予約",
            "チケット",
            "注意事項",
        )
        host = urlparse(url).netloc
        for a in soup.find_all("a", href=True):
            if not isinstance(a, Tag):
                continue
            target = urljoin(url, str(a["href"]))
            label = a.get_text(" ", strip=True)
            if any(k.lower() in label.lower() for k in keys) and (
                urlparse(target).netloc == host or "livepocket" in target
            ):
                if target not in result:
                    result.append(target)
        return result[:20]

    def find_goods_images(self, html: str, url: str) -> list[str]:
        return [urljoin(url, x.url) for x in detect_goods_images(html)]

    def parse_entry_information(self, html: str, url: str) -> dict[str, object]:
        text = BeautifulSoup(html, "html.parser").get_text("\n", strip=True)
        lines = [
            x
            for x in text.splitlines()
            if any(k in x for k in ("入場", "整理券", "抽選", "予約", "LivePocket"))
        ]
        raw = "\n".join(lines) or None
        kind = "unknown"
        if "抽選" in text:
            kind = "lottery"
        elif "予約" in text:
            kind = "reservation"
        elif "整理券" in text:
            kind = "numbered_ticket"
        elif "チケット" in text or "LivePocket" in text:
            kind = "paid_ticket"
        elif "自由入場" in text:
            kind = "free_entry"
        return {"entry_type": kind, "original_text": raw, "source_page_url": url}

    def health_check(self, html: str) -> tuple[bool, str]:
        try:
            cards = self.discover_event_cards(html)
            counts = {
                section: sum(card.source_section == section for card in cards)
                for section in TARGET_SECTIONS
            }
            summary = ", ".join(f"{section}={count}" for section, count in counts.items())
            return True, f"found {len(cards)} target event card(s): {summary}"
        except ValueError as exc:
            return False, str(exc)
