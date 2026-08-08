from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.registry import ADAPTERS
from app.database import get_db
from app.models import Event, IpAlias, IpTitle, ScanCard, ScanRun, Source
from app.schemas.api import AliasCreate, EventOut, IpCreate, IpOut, IpPatch, SourceOut
from app.services.ip_matcher import normalize

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/sources", response_model=list[SourceOut])
def sources(db: Session = Depends(get_db)):
    return db.scalars(select(Source)).all()


@router.post("/sources/{source_id}/scan", status_code=202)
async def scan_source(source_id: int, db: Session = Depends(get_db)):
    source = db.get(Source, source_id)
    if not source:
        raise HTTPException(404, "Source not found")
    if source.adapter_key not in ADAPTERS:
        raise HTTPException(501, "Adapter not implemented")
    from app.services.scan_service import scan

    return await scan(db, source)


@router.get("/ip-titles", response_model=list[IpOut])
def ips(db: Session = Depends(get_db)):
    return db.scalars(select(IpTitle)).all()


@router.post("/ip-titles", response_model=IpOut)
def create_ip(body: IpCreate, db: Session = Depends(get_db)):
    obj = IpTitle(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/ip-titles/{ip_id}", response_model=IpOut)
def patch_ip(ip_id: int, body: IpPatch, db: Session = Depends(get_db)):
    obj = db.get(IpTitle, ip_id)
    if not obj:
        raise HTTPException(404, "IP not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/ip-titles/{ip_id}/aliases")
def add_alias(ip_id: int, body: AliasCreate, db: Session = Depends(get_db)):
    if not db.get(IpTitle, ip_id):
        raise HTTPException(404, "IP not found")
    obj = IpAlias(
        ip_title_id=ip_id,
        alias=body.alias,
        normalized_alias=normalize(body.alias),
        alias_type=body.alias_type,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"id": obj.id}


@router.delete("/ip-aliases/{alias_id}", status_code=204)
def delete_alias(alias_id: int, db: Session = Depends(get_db)):
    obj = db.get(IpAlias, alias_id)
    if not obj:
        raise HTTPException(404, "Alias not found")
    db.delete(obj)
    db.commit()


@router.get("/events", response_model=list[EventOut])
def events(db: Session = Depends(get_db)):
    return db.scalars(select(Event)).all()


@router.get("/events/{event_id}", response_model=EventOut)
def event(event_id: int, db: Session = Depends(get_db)):
    obj = db.get(Event, event_id)
    if not obj:
        raise HTTPException(404, "Event not found")
    return obj


@router.get("/scans")
def scans(db: Session = Depends(get_db)):
    return db.scalars(select(ScanRun).order_by(ScanRun.started_at.desc())).all()


@router.get("/scans/{scan_id}/cards")
def scan_cards(scan_id: int, matched_only: bool = False, db: Session = Depends(get_db)):
    if not db.get(ScanRun, scan_id):
        raise HTTPException(404, "Scan run not found")
    query = select(ScanCard).where(ScanCard.scan_run_id == scan_id)
    if matched_only:
        query = query.where(ScanCard.matched_ip_id.is_not(None))
    return db.scalars(query.order_by(ScanCard.source_position)).all()
