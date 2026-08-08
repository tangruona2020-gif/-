from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.adapters.registry import get_adapter
from app.models import Event, EventSource, IpAlias, ScanCard, ScanRun, Source
from app.services.ip_matcher import match_ip, normalize


async def scan(db: Session, source: Source) -> dict[str, object]:
    run = ScanRun(source_id=source.id)
    db.add(run)
    db.commit()
    db.refresh(run)
    source.last_scan_started_at = datetime.utcnow()
    source.last_scan_status = "running"
    db.commit()
    adapter = get_adapter(source.adapter_key)
    try:
        cards = await adapter.discover()
        previous = (
            db.scalar(
                select(func.max(ScanRun.discovered_card_count)).where(
                    ScanRun.source_id == source.id
                )
            )
            or 0
        )
        if previous > 5 and not cards:
            raise RuntimeError("suspicious zero-card result after previous successful scan")
        run.discovered_card_count = len(cards)
        aliases = [(a.ip_title_id, a.alias) for a in db.scalars(select(IpAlias)).all()]
        matched_cards: list[dict[str, object]] = []
        for card in cards:
            matched = match_ip({"title": card.title, "card_text": card.summary_text}, aliases)
            scan_card = ScanCard(
                scan_run_id=run.id,
                source_id=source.id,
                source_section=card.source_section,
                source_position=card.source_position,
                title=card.title,
                detail_url=card.detail_url,
                image_url=card.image_url,
                summary_text=card.summary_text,
                raw_date_text=card.raw_date_text,
                matched_ip_id=matched.matched_ip_id if matched else None,
                matched_alias=matched.matched_alias if matched else None,
                match_field=matched.match_field if matched else None,
                match_score=matched.match_score if matched else None,
                match_reason=matched.reason if matched else None,
                detail_status="pending" if matched else "not_matched",
            )
            db.add(scan_card)
            db.commit()
            if not matched:
                continue
            run.matched_ip_count += 1
            matched_cards.append(
                {
                    "source_section": card.source_section,
                    "title": card.title,
                    "detail_url": card.detail_url,
                    "matched_ip_id": matched.matched_ip_id,
                    "matched_alias": matched.matched_alias,
                    "match_field": matched.match_field,
                    "match_score": matched.match_score,
                    "reason": matched.reason,
                }
            )
            try:
                detail_html = await adapter.fetch_event_detail(card.detail_url)
                detail = adapter.parse_event_detail(detail_html, card.detail_url)
                event = db.scalar(select(Event).where(Event.official_detail_url == card.detail_url))
                if not event:
                    event = Event(
                        ip_title_id=matched.matched_ip_id,
                        canonical_title=detail.title,
                        normalized_title=normalize(detail.title),
                        event_type=detail.event_type,
                        start_date=detail.start_date,
                        end_date=detail.end_date,
                        business_hours_text=detail.business_hours_text,
                        venue_name=detail.venue_name,
                        address=detail.address,
                        entry_type=detail.entry_type,
                        entry_summary=detail.entry_summary,
                        official_detail_url=card.detail_url,
                    )
                    db.add(event)
                    db.flush()
                    db.add(
                        EventSource(
                            event_id=event.id,
                            source_id=source.id,
                            source_event_title=card.title,
                            detail_url=card.detail_url,
                            source_card_image_url=card.image_url,
                            raw_date_text=card.raw_date_text,
                        )
                    )
                else:
                    event.last_checked_at = datetime.utcnow()
                run.detail_success_count += 1
                scan_card.detail_status = "success"
                db.commit()
            except Exception as exc:
                run.detail_failure_count += 1
                db.rollback()
                persisted_card = db.get(ScanCard, scan_card.id)
                if persisted_card is not None:
                    persisted_card.detail_status = "failed"
                    persisted_card.detail_error = str(exc)
                db.commit()
        run.status = "success" if not run.detail_failure_count else "partial"
        source.last_scan_succeeded_at = datetime.utcnow()
        source.last_scan_status = run.status
    except Exception as exc:
        run.status = "failed"
        run.error_message = str(exc)
        source.last_scan_status = "failed"
        source.last_error = str(exc)
    run.finished_at = datetime.utcnow()
    db.commit()
    return {
        "scan_run_id": run.id,
        "status": run.status,
        "cards": run.discovered_card_count,
        "matched": run.matched_ip_count,
        "failures": run.detail_failure_count,
        "matched_cards": matched_cards if "matched_cards" in locals() else [],
    }
