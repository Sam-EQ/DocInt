import asyncio
from pathlib import Path
from marker.output import text_from_rendered
from core.pipeline import _CONVERTER


async def extract_raw_markdown_with_images(pdf_path: Path) -> str:
    rendered = await asyncio.to_thread(_CONVERTER, str(pdf_path))
    md, _, _ = text_from_rendered(rendered)
    return md.strip()
