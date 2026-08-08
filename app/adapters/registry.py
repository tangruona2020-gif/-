from app.adapters.base import BaseAdapter
from app.adapters.the_chara import TheCharaAdapter

ADAPTERS: dict[str, type[BaseAdapter]] = {"the_chara": TheCharaAdapter}


def get_adapter(key: str) -> BaseAdapter:
    try:
        return ADAPTERS[key]()
    except KeyError as exc:
        raise ValueError(f"Adapter not implemented: {key}") from exc
