import argparse
import asyncio

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Source
from app.services.scan_service import scan


async def run(source_key: str | None, all_enabled: bool) -> None:
    with SessionLocal() as db:
        query = select(Source).where(Source.enabled)
        if not all_enabled:
            query = query.where(Source.adapter_key == source_key)
        sources = db.scalars(query).all()
        if not sources:
            raise SystemExit("No matching enabled source. Run seed first.")
        for source in sources:
            print(await scan(db, source))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--source")
    group.add_argument("--all", action="store_true")
    args = parser.parse_args()
    asyncio.run(run(args.source, args.all))


if __name__ == "__main__":
    main()
