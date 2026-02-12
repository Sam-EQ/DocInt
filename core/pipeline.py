from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser

_ARTIFACT_DICT = create_model_dict()


def get_converter() -> PdfConverter:
    config = {
        "output_format": "markdown",
        "paginate_output": True,
        "use_llm": False,
        "disable_image_extraction": False,
        "force_ocr": True,
        "layout_batch_size": 16,
        "text_batch_size": 16,
    }

    parser = ConfigParser(config)

    return PdfConverter(
        artifact_dict=_ARTIFACT_DICT,
        config=parser.generate_config_dict(),
        processor_list=parser.get_processors(),
        renderer=parser.get_renderer(),
        llm_service=None,  
    )


_CONVERTER = get_converter()
