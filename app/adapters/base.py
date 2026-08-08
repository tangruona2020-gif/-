from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date


@dataclass(slots=True)
class EventCard:
    title: str
    detail_url: str
    image_url: str | None = None
    summary_text: str = ""
    raw_date_text: str = ""
    source_position: int = 0
    source_section: str = ""


@dataclass(slots=True)
class ParsedEventDetail:
    title: str
    description: str = ""
    start_date: date | None = None
    end_date: date | None = None
    business_hours_text: str | None = None
    venue_name: str | None = None
    address: str | None = None
    event_type: str = "other"
    entry_type: str = "unknown"
    entry_summary: str | None = None
    related_urls: list[str] = field(default_factory=list)
    candidate_images: list[str] = field(default_factory=list)
    raw_entry_text: str | None = None


class BaseAdapter(ABC):
    adapter_key: str
    source_name: str
    start_url: str
    requires_browser = False

    async def discover(self) -> list[EventCard]:
        html = await self.fetch_event_detail(self.start_url)
        return self.discover_event_cards(html, self.start_url)

    @abstractmethod
    def discover_event_cards(self, html: str, base_url: str | None = None) -> list[EventCard]: ...
    @abstractmethod
    def parse_event_card(self, element: object, position: int = 0) -> EventCard: ...
    @abstractmethod
    async def fetch_event_detail(self, url: str) -> str: ...
    @abstractmethod
    def parse_event_detail(self, html: str, url: str) -> ParsedEventDetail: ...
    @abstractmethod
    def find_related_pages(self, html: str, url: str) -> list[str]: ...
    @abstractmethod
    def find_goods_images(self, html: str, url: str) -> list[str]: ...
    @abstractmethod
    def parse_entry_information(self, html: str, url: str) -> dict[str, object]: ...
    @abstractmethod
    def health_check(self, html: str) -> tuple[bool, str]: ...
