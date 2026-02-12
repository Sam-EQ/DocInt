import asyncio
import sys
import time
from pathlib import Path

from marker.output import text_from_rendered
from config import TEMP_DIR
from core.pipeline import _CONVERTER
from core.image_extractor import extract_images
from core.image_captioner import describe_images_parallel
from core.image_injector import inject_descriptions


async def debug_pipeline(pdf: Path):
    start_total = time.perf_counter()

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    out = TEMP_DIR / "debug"
    out.mkdir(parents=True, exist_ok=True)

    print(f"📄 PDF: {pdf.name}")

    t0 = time.perf_counter()

    rendered = await asyncio.to_thread(_CONVERTER, str(pdf))
    md, _, _ = text_from_rendered(rendered)

    t_marker = time.perf_counter() - t0
    print(f"⏱️ Marker extraction: {t_marker:.2f}s")

    t0 = time.perf_counter()

    images = extract_images(rendered)
    print(f"🖼️ Images detected: {len(images)}")

    descriptions = await describe_images_parallel(images)

    t_images = time.perf_counter() - t0
    print(f"⏱️ Image captioning: {t_images:.2f}s")
    t0 = time.perf_counter()

    final_md = inject_descriptions(md, images, descriptions)

    path = out / "final_with_images.md"
    path.write_text(final_md, encoding="utf-8")

    t_write = time.perf_counter() - t0
    print(f"⏱️ Injection + write: {t_write:.2f}s")

    total = time.perf_counter() - start_total

    print("\n✅ Done")
    print(f"📄 Output: {path}")
    print(f"⏱️ TOTAL TIME: {total:.2f}s")


if __name__ == "__main__":
    asyncio.run(debug_pipeline(Path(sys.argv[1])))
