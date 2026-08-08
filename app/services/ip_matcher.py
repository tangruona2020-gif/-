import re
import unicodedata
from dataclasses import dataclass


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).strip().lower()
    value = re.sub(r"[~‐‑‒–—―〜～]", "-", value)
    return re.sub(r"\s+", " ", value)


@dataclass(slots=True)
class MatchResult:
    matched_ip_id: int
    matched_alias: str
    match_field: str
    match_score: float
    reason: str


def match_ip(fields: dict[str, str], aliases: list[tuple[int, str]]) -> MatchResult | None:
    order = ["title", "card_text", "detail_title", "detail_text", "meta", "image"]
    for field in order:
        haystack = normalize(fields.get(field, ""))
        for ip_id, alias in sorted(aliases, key=lambda x: len(normalize(x[1])), reverse=True):
            needle = normalize(alias)
            if needle and (haystack == needle or needle in haystack):
                exact = haystack == needle
                return MatchResult(
                    ip_id,
                    alias,
                    field,
                    1.0 if exact else 0.9,
                    "exact_normalized_title" if exact else f"alias_in_{field}",
                )
    return None
