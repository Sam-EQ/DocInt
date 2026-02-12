import asyncio
import sys
import time
from pathlib import Path

from marker.output import text_from_rendered
from config import TEMP_DIR
from core.pipeline import _CONVERTER
from core.markdown_sanitize import sanitize_markdown
from core.markdown_layout_cleaner import detect_and_clean_complex_layouts, remove_truncated_sentences
from core.markdown_structure_fix import fix_document_structure
from core.normalize_headings import normalize_heading_jumps
from core.markdown_canonicalize import canonicalize_markdown
from core.markdown_validate import validate_markdown


async def debug_pipeline(pdf: Path):

    out = TEMP_DIR / "debug"
    out.mkdir(parents=True, exist_ok=True)

    print(f"📄 Processing: {pdf.name}")
    print(f"📁 Output dir: {out}\n")

    pipeline_start = time.perf_counter()

    # Stage 1: Raw extraction
    print("Stage 1: PDF extraction...")
    t0 = time.perf_counter()
    rendered = await asyncio.to_thread(_CONVERTER, str(pdf))
    md, _, _ = text_from_rendered(rendered)
    (out / "01_raw_marker.md").write_text(md, encoding="utf-8")
    dt = time.perf_counter() - t0
    print(f"  ✓ Lines: {len(md.splitlines())}, Chars: {len(md)} — {dt:.2f}s")

    # Stage 2: Basic sanitization
    print("Stage 2: Basic sanitization...")
    t0 = time.perf_counter()
    md = sanitize_markdown(md)
    (out / "02_sanitized.md").write_text(md, encoding="utf-8")
    dt = time.perf_counter() - t0
    print(f"  ✓ Lines: {len(md.splitlines())}, Chars: {len(md)} — {dt:.2f}s")

    # Stage 3: Complex layout cleaning
    print("Stage 3: Complex layout cleaning...")
    t0 = time.perf_counter()
    md = detect_and_clean_complex_layouts(md)
    (out / "03_layout_cleaned.md").write_text(md, encoding="utf-8")
    dt = time.perf_counter() - t0
    print(f"  ✓ Lines: {len(md.splitlines())}, Chars: {len(md)} — {dt:.2f}s")

    # Stage 4: Structure fixes
    print("Stage 4: Structure fixes...")
    t0 = time.perf_counter()
    md = fix_document_structure(md)
    (out / "04_structure_fixed.md").write_text(md, encoding="utf-8")
    dt = time.perf_counter() - t0
    print(f"  ✓ Lines: {len(md.splitlines())}, Chars: {len(md)} — {dt:.2f}s")

    # Stage 5: Heading normalization
    print("Stage 5: Heading normalization...")
    t0 = time.perf_counter()
    md = normalize_heading_jumps(md)
    (out / "05_headings_normalized.md").write_text(md, encoding="utf-8")
    dt = time.perf_counter() - t0
    print(f"  ✓ Lines: {len(md.splitlines())}, Chars: {len(md)} — {dt:.2f}s")

    # Stage 6: Truncation marking
    print("Stage 6: Truncation marking...")
    t0 = time.perf_counter()
    md = remove_truncated_sentences(md)
    (out / "06_truncations_marked.md").write_text(md, encoding="utf-8")
    dt = time.perf_counter() - t0
    print(f"  ✓ Lines: {len(md.splitlines())}, Chars: {len(md)} — {dt:.2f}s")

    # Stage 7: LLM canonicalization
    #######  print(f"  ✓ Lines: {len(md.splitlines())}, Chars: {len(md)} — {dt:.2f}s")

    # Stage 8: Validation
    print("Stage 8: Validation...")
    t0 = time.perf_counter()
    md = validate_markdown(md)
    (out / "08_final.md").write_text(md, encoding="utf-8")
    dt = time.perf_counter() - t0
    print(f"  ✓ Lines: {len(md.splitlines())}, Chars: {len(md)} — {dt:.2f}s")

    total_time = time.perf_counter() - pipeline_start

    print(f"\n✅ Debug complete!")
    print(f"📂 All stages saved in: {out}")
    print(f"⏱️ Total pipeline time: {total_time:.2f}s")
    print("\n📊 Compare files to see what each stage does:")
    print("   diff 01_raw_marker.md 02_sanitized.md")
    print("   diff 04_structure_fixed.md 05_headings_normalized.md")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug.py <path-to-pdf>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)

    asyncio.run(debug_pipeline(pdf_path))
