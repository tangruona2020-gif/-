import hashlib
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import httpx
from PIL import Image


@dataclass(slots=True)
class DownloadedImage:
    path: Path
    sha256: str
    width: int
    height: int
    file_size: int


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


async def download_image(url: str, target_dir: Path, timeout: float = 20) -> DownloadedImage:
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        content = response.content
    digest = sha256_bytes(content)
    target_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(BytesIO(content)) as image:
        width, height = image.size
        fmt = image.format.lower() if image.format else "img"
    path = target_dir / f"{digest}.{fmt}"
    if not path.exists():
        path.write_bytes(content)
    return DownloadedImage(path, digest, width, height, len(content))
