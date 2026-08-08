from dataclasses import dataclass
from difflib import SequenceMatcher

from app.services.ip_matcher import normalize


@dataclass(slots=True)
class DedupResult:
    duplicate: bool
    possible_duplicate: bool
    reason: str


def compare_events(left: dict, right: dict) -> DedupResult:
    if left.get("official_detail_url") == right.get("official_detail_url"):
        return DedupResult(True, False, "same_detail_url")
    if left.get("image_hash") and left.get("image_hash") == right.get("image_hash"):
        return DedupResult(True, False, "same_image_hash")
    ratio = SequenceMatcher(
        None, normalize(left.get("title", "")), normalize(right.get("title", ""))
    ).ratio()
    same = left.get("ip_title_id") == right.get("ip_title_id") and left.get(
        "start_date"
    ) == right.get("start_date")
    if same and ratio >= 0.85:
        return DedupResult(True, False, "same_ip_title_date")
    if ratio >= 0.85 and left.get("venue_name") == right.get("venue_name"):
        return DedupResult(True, False, "high_title_similarity_same_venue")
    if ratio >= 0.7:
        return DedupResult(False, True, "possible_duplicate")
    return DedupResult(False, False, "no_match")
