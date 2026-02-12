import asyncio
import os
from pathlib import Path
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from marker.config.parser import ConfigParser

from config import TEMP_DIR
from core.markdown_sanitize import sanitize_markdown
from core.markdown_layout_cleaner import detect_and_clean_complex_layouts, remove_truncated_sentences
from core.markdown_structure_fix import fix_document_structure
from core.normalize_headings import normalize_heading_jumps
from core.markdown_canonicalize import canonicalize_markdown
from core.markdown_validate import validate_markdown

_ARTIFACT_DICT = create_model_dict()


def get_converter():
    config = {
        "output_format": "markdown",
        "paginate_output": True,
        "use_llm": True,
        "llm_service": "marker.services.openai.OpenAIService",
        "openai_api_key": os.environ["OPENAI_API_KEY"],
        "openai_model": "gpt-4o-mini",
        "disable_image_extraction": True,  
        "force_ocr": True, 
        "layout_batch_size": 16,
        "text_batch_size": 16,
        "device": "cuda",
    }
    parser = ConfigParser(config)
    return PdfConverter(
        artifact_dict=_ARTIFACT_DICT,
        config=parser.generate_config_dict(),
        processor_list=parser.get_processors(),
        renderer=parser.get_renderer(),
        llm_service=parser.get_llm_service(),
    )


_CONVERTER = get_converter()


async def run_pipeline(pdf_path: str) -> str:

    rendered = await asyncio.to_thread(_CONVERTER, str(pdf_path))
    md, _, _ = text_from_rendered(rendered)

    md = sanitize_markdown(md)

    md = detect_and_clean_complex_layouts(md)

    md = fix_document_structure(md)

    md = normalize_heading_jumps(md)

    md = remove_truncated_sentences(md)

    md = await canonicalize_markdown(md)

    md = validate_markdown(md)

    out_dir = TEMP_DIR / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_stem = Path(pdf_path).stem
    final_path = out_dir / f"{pdf_stem}_final.md"
    
    final_path.write_text(md, encoding='utf-8')
    print(f"Processing complete. Saved to: {final_path}")

    return md