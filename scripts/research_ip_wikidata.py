"""Find reviewable Japanese-title candidates through the Wikidata API."""

import json
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data" / "seed" / "ip_titles_zh.txt"
OUTPUT = ROOT / "data" / "seed" / "ip_titles_wikidata_candidates.json"
API = "https://www.wikidata.org/w/api.php"
USER_AGENT = (
    "GoodsPopupMonitor/0.1 "
    "(personal IP-title research; manual run; https://www.the-chara.com/)"
)


def chunks(values: list[str], size: int) -> list[list[str]]:
    return [values[index : index + size] for index in range(0, len(values), size)]


def main() -> None:
    titles = [line.strip() for line in INPUT.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows: list[dict[str, object]] = []
    with httpx.Client(timeout=30, headers={"User-Agent": USER_AGENT}) as client:
        for index, title in enumerate(titles, start=1):
            response = client.get(
                API,
                params={
                    "action": "wbsearchentities",
                    "format": "json",
                    "language": "zh",
                    "uselang": "zh-cn",
                    "type": "item",
                    "limit": "5",
                    "search": title,
                },
            )
            response.raise_for_status()
            candidates = response.json().get("search", [])
            rows.append(
                {
                    "chinese_name": title,
                    "selected_wikidata_id": candidates[0]["id"] if candidates else None,
                    "japanese_name": None,
                    "review_status": "candidate" if candidates else "unresolved",
                    "candidates": [
                        {
                            "id": item["id"],
                            "label": item.get("label"),
                            "description": item.get("description"),
                            "matched_text": item.get("match", {}).get("text"),
                        }
                        for item in candidates
                    ],
                }
            )
            if index < len(titles):
                time.sleep(0.15)

        ids = [str(row["selected_wikidata_id"]) for row in rows if row["selected_wikidata_id"]]
        japanese_labels: dict[str, str] = {}
        for batch in chunks(ids, 50):
            response = client.get(
                API,
                params={
                    "action": "wbgetentities",
                    "format": "json",
                    "ids": "|".join(batch),
                    "props": "labels",
                    "languages": "ja",
                },
            )
            response.raise_for_status()
            for entity_id, entity in response.json().get("entities", {}).items():
                label = entity.get("labels", {}).get("ja", {}).get("value")
                if label:
                    japanese_labels[entity_id] = label

    for row in rows:
        entity_id = row["selected_wikidata_id"]
        if entity_id in japanese_labels:
            row["japanese_name"] = japanese_labels[str(entity_id)]
        elif entity_id:
            row["review_status"] = "candidate_without_japanese_label"

    OUTPUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with_japanese = sum(bool(row["japanese_name"]) for row in rows)
    unresolved = sum(row["review_status"] == "unresolved" for row in rows)
    print(f"total={len(rows)} japanese_candidates={with_japanese} unresolved={unresolved}")
    for row in rows:
        if row["review_status"] != "candidate" or not row["japanese_name"]:
            print(
                f"REVIEW\t{row['chinese_name']}\t{row['review_status']}\t"
                f"{row['japanese_name'] or '-'}"
            )


if __name__ == "__main__":
    main()
