from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def now() -> datetime:
    return datetime.utcnow()


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)


class Source(TimestampMixin, Base):
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    adapter_key: Mapped[str] = mapped_column(String(100), unique=True)
    start_url: Mapped[str] = mapped_column(String(500))
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    scan_interval_hours: Mapped[int] = mapped_column(Integer, default=24)
    last_scan_started_at: Mapped[datetime | None]
    last_scan_succeeded_at: Mapped[datetime | None]
    last_scan_status: Mapped[str | None] = mapped_column(String(30))
    last_error: Mapped[str | None] = mapped_column(Text)


class IpTitle(TimestampMixin, Base):
    __tablename__ = "ip_titles"
    id: Mapped[int] = mapped_column(primary_key=True)
    canonical_name: Mapped[str] = mapped_column(String(200), unique=True)
    chinese_name: Mapped[str | None] = mapped_column(String(200))
    japanese_name: Mapped[str | None] = mapped_column(String(200))
    english_name: Mapped[str | None] = mapped_column(String(200))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    aliases: Mapped[list["IpAlias"]] = relationship(cascade="all, delete-orphan")


class IpAlias(Base):
    __tablename__ = "ip_aliases"
    __table_args__ = (UniqueConstraint("ip_title_id", "normalized_alias"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    ip_title_id: Mapped[int] = mapped_column(ForeignKey("ip_titles.id", ondelete="CASCADE"))
    alias: Mapped[str] = mapped_column(String(200))
    normalized_alias: Mapped[str] = mapped_column(String(200), index=True)
    alias_type: Mapped[str] = mapped_column(String(30), default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Event(TimestampMixin, Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    ip_title_id: Mapped[int] = mapped_column(ForeignKey("ip_titles.id"), index=True)
    canonical_title: Mapped[str] = mapped_column(String(500))
    normalized_title: Mapped[str] = mapped_column(String(500), index=True)
    event_type: Mapped[str] = mapped_column(String(40), default="other")
    status: Mapped[str] = mapped_column(String(40), default="discovered")
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    business_hours_text: Mapped[str | None] = mapped_column(Text)
    venue_name: Mapped[str | None] = mapped_column(String(300))
    address: Mapped[str | None] = mapped_column(Text)
    entry_type: Mapped[str] = mapped_column(String(40), default="unknown")
    entry_summary: Mapped[str | None] = mapped_column(Text)
    official_detail_url: Mapped[str] = mapped_column(String(1000), unique=True)
    first_discovered_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    last_checked_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class EventSource(Base):
    __tablename__ = "event_sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    source_event_title: Mapped[str] = mapped_column(String(500))
    detail_url: Mapped[str] = mapped_column(String(1000))
    source_card_image_url: Mapped[str | None] = mapped_column(String(1000))
    raw_date_text: Mapped[str | None] = mapped_column(Text)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class EventImage(Base):
    __tablename__ = "event_images"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    image_type: Mapped[str] = mapped_column(String(30), default="unknown")
    local_path: Mapped[str] = mapped_column(String(1000))
    original_url: Mapped[str] = mapped_column(String(1000))
    source_page_url: Mapped[str] = mapped_column(String(1000))
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    width: Mapped[int | None]
    height: Mapped[int | None]
    file_size: Mapped[int]
    version_number: Mapped[int] = mapped_column(default=1)
    is_latest: Mapped[bool] = mapped_column(default=True)
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class EventEntryRule(TimestampMixin, Base):
    __tablename__ = "event_entry_rules"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    entry_type: Mapped[str] = mapped_column(String(40), default="unknown")
    application_start_at: Mapped[datetime | None]
    application_deadline_at: Mapped[datetime | None]
    result_announcement_at: Mapped[datetime | None]
    ticket_url: Mapped[str | None] = mapped_column(String(1000))
    identity_check_required: Mapped[bool] = mapped_column(default=False)
    companion_rule: Mapped[str | None] = mapped_column(Text)
    original_text: Mapped[str | None] = mapped_column(Text)
    source_page_url: Mapped[str] = mapped_column(String(1000))


class ScanRun(Base):
    __tablename__ = "scan_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    finished_at: Mapped[datetime | None]
    status: Mapped[str] = mapped_column(String(30), default="running")
    discovered_card_count: Mapped[int] = mapped_column(default=0)
    matched_ip_count: Mapped[int] = mapped_column(default=0)
    detail_success_count: Mapped[int] = mapped_column(default=0)
    detail_failure_count: Mapped[int] = mapped_column(default=0)
    goods_image_count: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str | None] = mapped_column(Text)


class ScanCard(Base):
    __tablename__ = "scan_cards"
    id: Mapped[int] = mapped_column(primary_key=True)
    scan_run_id: Mapped[int] = mapped_column(ForeignKey("scan_runs.id"), index=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), index=True)
    source_section: Mapped[str] = mapped_column(String(200))
    source_position: Mapped[int]
    title: Mapped[str] = mapped_column(String(500))
    detail_url: Mapped[str] = mapped_column(String(1000))
    image_url: Mapped[str | None] = mapped_column(String(1000))
    summary_text: Mapped[str | None] = mapped_column(Text)
    raw_date_text: Mapped[str | None] = mapped_column(Text)
    matched_ip_id: Mapped[int | None] = mapped_column(ForeignKey("ip_titles.id"), index=True)
    matched_alias: Mapped[str | None] = mapped_column(String(200))
    match_field: Mapped[str | None] = mapped_column(String(50))
    match_score: Mapped[float | None]
    match_reason: Mapped[str | None] = mapped_column(String(200))
    detail_status: Mapped[str] = mapped_column(String(30), default="not_matched")
    detail_error: Mapped[str | None] = mapped_column(Text)
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class PageSnapshot(Base):
    __tablename__ = "page_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    event_id: Mapped[int | None] = mapped_column(ForeignKey("events.id"))
    url: Mapped[str] = mapped_column(String(1000))
    content_hash: Mapped[str] = mapped_column(String(64))
    html_path: Mapped[str] = mapped_column(String(1000))
    screenshot_path: Mapped[str | None] = mapped_column(String(1000))
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=now)
