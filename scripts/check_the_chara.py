"""Perform a low-frequency, read-only health check against THEキャラ."""

import asyncio
import urllib.robotparser

import httpx

from app.adapters.the_chara import TheCharaAdapter

USER_AGENT = "GoodsPopupMonitor/0.1 (+personal research; low-frequency manual check)"
ROBOTS_URL = "https://www.the-chara.com/robots.txt"
HOME_URL = "https://www.the-chara.com/"


async def main() -> None:
    async with httpx.AsyncClient(
        timeout=20,
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
    ) as client:
        robots_response = await client.get(ROBOTS_URL)
        print(f"robots_status={robots_response.status_code}")
        robots = urllib.robotparser.RobotFileParser()
        robots.set_url(ROBOTS_URL)
        robots.parse(robots_response.text.splitlines())
        allowed = robots.can_fetch(USER_AGENT, HOME_URL)
        print(f"homepage_allowed={allowed}")
        if not allowed:
            return

        response = await client.get(HOME_URL)
        print(f"homepage_status={response.status_code}")
        print(f"content_type={response.headers.get('content-type')}")
        print(f"html_bytes={len(response.content)}")
        lowered = response.text.lower()
        blocked = any(marker in lowered for marker in ("captcha", "cf-chl-", "access denied"))
        print(f"anti_bot_detected={blocked}")
        if blocked:
            return

        ok, reason = TheCharaAdapter().health_check(response.text)
        print(f"adapter_health={ok}")
        print(f"adapter_reason={reason}")


if __name__ == "__main__":
    asyncio.run(main())
