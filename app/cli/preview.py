import argparse
import asyncio

from sqlalchemy import select

from app.adapters.registry import get_adapter
from app.database import SessionLocal
from app.models import IpAlias, Source
from app.services.ip_matcher import match_ip


def display(value: str | None) -> str:
    return (value or "-").replace("\n", " ").replace("\t", " ").strip()


async def preview(source_key: str) -> None:
    with SessionLocal() as db:
        source = db.scalar(select(Source).where(Source.adapter_key == source_key))
        if source is None:
            raise SystemExit(f"Source not found: {source_key}")
        aliases = [(alias.ip_title_id, alias.alias) for alias in db.scalars(select(IpAlias))]

    adapter = get_adapter(source_key)
    cards = await adapter.discover()

    print("栏目\t标题\t日期文字\t图片 URL\t详情 URL\tIP 命中结果")
    matched_count = 0
    for card in cards:
        result = match_ip(
            {
                "title": card.title,
                "card_text": card.summary_text,
                "image": card.image_url or "",
            },
            aliases,
        )
        matched = "未命中"
        if result:
            matched_count += 1
            matched = (
                f"命中 IP#{result.matched_ip_id}; alias={result.matched_alias}; "
                f"field={result.match_field}; score={result.match_score:.2f}; "
                f"reason={result.reason}"
            )
        print(
            "\t".join(
                (
                    display(card.source_section),
                    display(card.title),
                    display(card.raw_date_text),
                    display(card.image_url),
                    display(card.detail_url),
                    matched,
                )
            )
        )
    print(f"\n合计：{len(cards)} 张卡片；命中：{matched_count} 张")


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview cards without opening detail pages")
    parser.add_argument("--source", default="the_chara")
    args = parser.parse_args()
    asyncio.run(preview(args.source))


if __name__ == "__main__":
    main()
