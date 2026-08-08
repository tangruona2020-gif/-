from datetime import date

from pydantic import BaseModel, ConfigDict


class IpCreate(BaseModel):
    canonical_name: str
    chinese_name: str | None = None
    japanese_name: str | None = None
    english_name: str | None = None
    enabled: bool = True


class IpPatch(BaseModel):
    canonical_name: str | None = None
    chinese_name: str | None = None
    japanese_name: str | None = None
    english_name: str | None = None
    enabled: bool | None = None


class AliasCreate(BaseModel):
    alias: str
    alias_type: str = "manual"


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SourceOut(ORMModel):
    id: int
    name: str
    adapter_key: str
    start_url: str
    enabled: bool


class IpOut(ORMModel):
    id: int
    canonical_name: str
    chinese_name: str | None
    japanese_name: str | None
    english_name: str | None
    enabled: bool


class EventOut(ORMModel):
    id: int
    ip_title_id: int
    canonical_title: str
    event_type: str
    status: str
    start_date: date | None
    end_date: date | None
    venue_name: str | None
    official_detail_url: str
