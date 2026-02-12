import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


def validate_markdown(md: str) -> str:

    issues: List[Tuple[str, str]] = []
    
    image_count = len(re.findall(r'\*\*\[Image from page \d+\]:\*\*', md))
    if image_count > 0:
        logger.info(f"Found {image_count} preserved image descriptions")
    
    last_level = None
    for line in md.splitlines():
        m = re.match(r"(#+)\s+", line)
        if not m:
            continue

        level = len(m.group(1))
        
        if last_level and level > last_level + 1:
            issues.append((
                "heading_jump",
                f"Heading jump detected: H{last_level} → H{level} : {line.strip()}"
            ))

        last_level = level
    
    broken_bold = re.findall(r"\*{3,}[^*]+\*{3,}", md)
    if broken_bold:
        issues.append((
            "broken_bold",
            f"Found {len(broken_bold)} instances of broken bold (3+ asterisks)"
        ))
    
    html_tags = re.findall(r"<[^>]+>", md)
    if html_tags:
        invalid_tags = [tag for tag in html_tags if not tag.startswith("<detail")]
        if invalid_tags:
            issues.append((
                "html_tags",
                f"Found {len(invalid_tags)} HTML tags that should be markdown"
            ))
    
    incomplete = re.findall(r"^.+[a-z]-\s*$", md, re.MULTILINE)
    if incomplete:
        issues.append((
            "incomplete_sentences",
            f"Found {len(incomplete)} potentially incomplete sentences"
        ))
    
    separators = re.findall(r"^\{?\d+\}?-+\s*$", md, re.MULTILINE)
    if separators:
        issues.append((
            "page_separators",
            f"Found {len(separators)} remaining page separator markers"
        ))
    
    truncations = md.count("*[truncated]*")
    if truncations > 0:
        logger.info(f"Found {truncations} truncation markers")
    
    layout_warnings = len(re.findall(r'> \*\*Note:\*\* .+complex layout', md, re.IGNORECASE))
    if layout_warnings > 0:
        logger.info(f"Found {layout_warnings} complex layout warnings")
    
    if issues:
        logger.warning(f"Markdown validation found {len(issues)} issue types:")
        for issue_type, message in issues:
            logger.warning(f"  [{issue_type}] {message}")
    else:
        logger.info("Markdown validation passed with no issues")
    
    return md