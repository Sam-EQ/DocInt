import re
from typing import List, Optional

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def normalize_heading_jumps(md: str) -> str:

    lines = md.splitlines()
    out: List[str] = []
    prev_level: Optional[int] = None

    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)

        if not m:
            out.append(line)
            continue

        hashes, title = m.groups()
        level = len(hashes)
        
        title = title.replace("**", "").strip()

        if prev_level is not None and level > prev_level + 1:
            title_lower = title.lower()
            
            is_label = (
                len(title) < 50 and
                (title.isupper() or 
                 any(keyword in title_lower for keyword in ['purpose', 'overview', 'references', 'general', 'typical']))
            )
            
            if is_label:
                out.append(f"**{title}**")
                continue
            else:
                level = prev_level + 1
                line = f"{'#' * level} {title}"

        if "**" in title:
            title = title.replace("**", "").strip()
            line = f"{hashes} {title}"

        out.append(line)
        prev_level = level

    return "\n".join(out)