"""Map supplied Chinese IP titles to Japanese Wikipedia titles without guessing."""

import json
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data" / "seed" / "ip_titles_zh.txt"
OUTPUT = ROOT / "data" / "seed" / "ip_titles_wikimedia.json"
API = "https://zh.wikipedia.org/w/api.php"
USER_AGENT = (
    "GoodsPopupMonitor/0.1 "
    "(personal IP-title research; manual run; https://www.the-chara.com/)"
)


def chunks(values: list[str], size: int) -> list[list[str]]:
    return [values[index : index + size] for index in range(0, len(values), size)]


def main() -> None:
    titles = [line.strip() for line in INPUT.read_text(encoding="utf-8").splitlines() if line.strip()]
    results: dict[str, dict[str, object]] = {
        title: {"chinese_name": title, "japanese_name": None, "source": None}
        for title in titles
    }

    with httpx.Client(timeout=30, headers={"User-Agent": USER_AGENT}) as client:
        for batch in chunks(titles, 50):
            response = client.post(
                API,
                data={
                    "action": "query",
                    "format": "json",
                    "formatversion": "2",
                    "redirects": "1",
                    "converttitles": "1",
                    "prop": "langlinks",
                    "lllang": "ja",
                    "lllimit": "1",
                    "titles": "|".join(batch),
                },
            )
            response.raise_for_status()
            payload = response.json()["query"]
            aliases = {item["from"]: item["to"] for item in payload.get("normalized", [])}
            aliases.update({item["from"]: item["to"] for item in payload.get("converted", [])})
            aliases.update({item["from"]: item["to"] for item in payload.get("redirects", [])})
            pages = {page["title"]: page for page in payload["pages"]}
            for supplied in batch:
                resolved = supplied
                visited: set[str] = set()
                while resolved in aliases and resolved not in visited:
                    visited.add(resolved)
                    resolved = aliases[resolved]
                page = pages.get(resolved)
                langlinks = page.get("langlinks", []) if page else []
                if langlinks:
                    results[supplied]["japanese_name"] = langlinks[0]["title"]
                    results[supplied]["source"] = f"https://zh.wikipedia.org/wiki/{resolved}"

    ordered = [results[title] for title in titles]
    OUTPUT.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    resolved_count = sum(bool(item["japanese_name"]) for item in ordered)
    print(f"total={len(ordered)} resolved={resolved_count} unresolved={len(ordered)-resolved_count}")
    for item in ordered:
        if not item["japanese_name"]:
            print(f"UNRESOLVED\t{item['chinese_name']}")


if __name__ == "__main__":
    main()
