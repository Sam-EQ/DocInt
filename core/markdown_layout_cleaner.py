import re
from typing import List


def detect_and_clean_complex_layouts(md: str) -> str:

    lines = md.split("\n")
    out: List[str] = []
    in_garbled_block = False
    garbled_lines: List[str] = []
    
    for i, line in enumerate(lines):
        is_garbled = _is_garbled_line(line)
        
        if is_garbled:
            if not in_garbled_block:
                in_garbled_block = True
                garbled_lines = [line]
            else:
                garbled_lines.append(line)
        else:
            if in_garbled_block:
                cleaned = _process_garbled_block(garbled_lines)
                if cleaned:
                    out.append(cleaned)
                in_garbled_block = False
                garbled_lines = []
            
            out.append(line)
    
    if in_garbled_block and garbled_lines:
        cleaned = _process_garbled_block(garbled_lines)
        if cleaned:
            out.append(cleaned)
    
    return "\n".join(out)


def _is_garbled_line(line: str) -> bool:

    if not line.strip():
        return False
    

    if line.strip().startswith("**[Image from page"):
        return False
    

    if re.match(r"^#+\s+", line) or re.match(r"^\s*[-•]\s+", line):
        return False
    

    caps_words = len(re.findall(r'\b[A-Z]{2,}\b', line))
    bold_markers = line.count("**")
    total_words = len(line.split())
    
    if total_words > 5:
        caps_ratio = caps_words / total_words
        has_excessive_bold = bold_markers > 10
        return caps_ratio > 0.6 or has_excessive_bold
    
    return False


def _process_garbled_block(lines: List[str]) -> str:
    combined = " ".join(lines)
    if len(combined) > 200:
        return (
            f"\n> **Note:** The following content may be from a diagram or complex layout:\n\n"
            f"{combined}\n"
        )
    return combined


def remove_truncated_sentences(md: str) -> str:
    lines = md.split("\n")
    out: List[str] = []
    for line in lines:
        if re.search(r'\b[a-z]+-\s*$', line):
            line = line.rstrip() + " *[truncated]*"
        out.append(line)
    return "\n".join(out)