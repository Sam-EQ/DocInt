import re
from hashlib import md5
from typing import List, Tuple


MERGED_HEADING = re.compile(r"(#{2,6})\s+(\*\*[^*]+\*\*)(.+)")


SUBTITLE_H4 = re.compile(r"^####\s+(.+)$")


BROKEN_BOLD = re.compile(r"\*{3,}([^*]+)\*{3,}")


HTML_LINK = re.compile(r'<a href="([^"]+)">([^<]+)</a>')


def _fix_broken_bold(md: str) -> str:
    """Fix markdown with 4+ asterisks (should be 2)."""
    return BROKEN_BOLD.sub(r"**\1**", md)


def _convert_html_links(md: str) -> str:
    """Convert HTML links to markdown format."""
    return HTML_LINK.sub(r"[\2](\1)", md)


def _split_merged_headings(md: str) -> str:
    """Split headings that have bold text merged on the same line."""
    lines = md.split("\n")
    out = []

    for line in lines:
        m = MERGED_HEADING.match(line)
        if m:
            lvl, bold, rest = m.groups()
            out.append(f"{lvl} {bold}")
            rest = rest.strip()
            if rest:  
                out.append(f"{'#' * (len(lvl) + 1)} {rest}")
        else:
            out.append(line)

    return "\n".join(out)


def _demote_subtitle_h4s(md: str) -> str:

    lines = md.split("\n")
    out = []

    for i, line in enumerate(lines):
        m = SUBTITLE_H4.match(line)
        if m and i > 0 and lines[i - 1].startswith("## "):

            out.append(f"**{m.group(1)}**")
        else:
            out.append(line)

    return "\n".join(out)


def _dedupe_tables(md: str) -> str:
    blocks = md.split("\n\n")
    seen = set()
    out = []

    for block in blocks:

        if "|" in block and "\n|" in block:

            block_hash = md5(block.strip().encode("utf-8")).hexdigest()
            if block_hash in seen:
                continue
            seen.add(block_hash)
        out.append(block)

    return "\n\n".join(out)


def _normalize_bullets(md: str) -> str:
    lines = md.split("\n")
    out = []
    
    for line in lines:
# Replace • with - at start of lines
        if re.match(r"^\s*[•●◦]\s+", line):
            line = re.sub(r"^(\s*)[•●◦]\s+", r"\1- ", line)
        out.append(line)
    
    return "\n".join(out)


def _fix_heading_levels(md: str) -> str:

    lines = md.split("\n")
    out = []
    last_level = 1  
    
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")
    
    for line in lines:
        m = heading_pattern.match(line)
        if m:
            hashes, title = m.groups()
            level = len(hashes)
            

            if level > last_level + 1:

                level = last_level + 1
                line = f"{'#' * level} {title}"
            
            last_level = level
        
        out.append(line)
    
    return "\n".join(out)


def fix_document_structure(md: str) -> str:

    md = _fix_broken_bold(md)


    md = _convert_html_links(md)
    

    md = _split_merged_headings(md)
    

    md = _demote_subtitle_h4s(md)
    

    md = _fix_heading_levels(md)
    

    md = _normalize_bullets(md)
    

    md = _dedupe_tables(md)
    
    return md