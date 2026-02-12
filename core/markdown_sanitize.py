import re


PAGE_SEPARATOR = re.compile(
    r"^\{?\d+\}?-+[\s\n]*$",
    re.MULTILINE
)


IMAGE_DESCRIPTION = re.compile(
    r"Image /page/(\d+)/[\w/]+/\d+ description: (.+?)(?=\nImage /page/|\n#|\Z)",
    re.IGNORECASE | re.DOTALL
)


GARBLED_TEXT = re.compile(
    r"^(?:[A-Z\*]{3,}\s+){4,}.*$",
    re.MULTILINE
)


OCR_FIXES = [
    (r'\b([A-Z]+)ENI\b', r'\1EN'),
    (r'fase\b', r'phase'),
    (r'\borganigram\b', r'organization chart'),
]


def _format_image_description(match):

    page_num = match.group(1)
    description = match.group(2).strip()
    

    return f"\n**[Image from page {page_num}]:** {description}\n\n"


def sanitize_markdown(md: str) -> str:

    if not md:
        return ""
    

    md = md.replace("\u0000", "").replace("\x00", "")
    

    md = PAGE_SEPARATOR.sub("", md)
    

    md = IMAGE_DESCRIPTION.sub(_format_image_description, md)
    

    md = GARBLED_TEXT.sub("", md)
    

    for pattern, replacement in OCR_FIXES:
        md = re.sub(pattern, replacement, md, flags=re.IGNORECASE)
    

    md = re.sub(r"\n{3,}", "\n\n", md)
    md = re.sub(r"[ \t]+$", "", md, flags=re.MULTILINE)
    
    return md.strip()