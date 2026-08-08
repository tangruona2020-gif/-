from sqlalchemy import select

from app.database import SessionLocal, create_schema
from app.models import IpAlias, IpTitle, Source
from app.services.ip_matcher import normalize

SOURCES = [
    ("THEキャラ", "the_chara", "https://www.the-chara.com/", True),
    ("MEDICOS", "medicos", "", False),
    ("eeo Store", "eeo_store", "", False),
    ("TSUTAYA", "tsutaya", "", False),
    ("スイーツパラダイス", "sweets_paradise", "", False),
    ("GAMERS", "gamers", "", False),
    ("Animega Sofmap", "animega_sofmap", "", False),
    ("Natslive Cafe", "natslive_cafe", "", False),
    ("Bushiroad Creative", "bushiroad", "", False),
    ("DeNA", "dena", "", False),
    ("AMNIBUS", "amnibus", "", False),
    ("AMOCAFE", "amocafe", "", False),
    ("Animate Only Shop", "animate_only_shop", "", False),
    ("中外鉱業", "chugai", "", False),
    ("カラオケの鉄人", "karatetsu", "", False),
]
IPS = [
    ("STEINS;GATE", ["シュタインズ・ゲート", "シュタゲ"]),
    ("メイドインアビス", ["Made in Abyss"]),
    ("魔法少女まどか☆マギカ", ["まどマギ", "Puella Magi Madoka Magica"]),
]


def main() -> None:
    create_schema()
    with SessionLocal() as db:
        for name, key, url, enabled in SOURCES:
            if not db.scalar(select(Source).where(Source.adapter_key == key)):
                db.add(
                    Source(
                        name=name,
                        adapter_key=key,
                        start_url=url or "https://example.invalid/",
                        enabled=enabled,
                    )
                )
        for name, aliases in IPS:
            ip = db.scalar(select(IpTitle).where(IpTitle.canonical_name == name))
            if not ip:
                ip = IpTitle(canonical_name=name)
                db.add(ip)
                db.flush()
                for alias in [name, *aliases]:
                    db.add(
                        IpAlias(
                            ip_title_id=ip.id,
                            alias=alias,
                            normalized_alias=normalize(alias),
                            alias_type="canonical" if alias == name else "manual",
                        )
                    )
        db.commit()
    print("Seed data is ready.")


if __name__ == "__main__":
    main()
