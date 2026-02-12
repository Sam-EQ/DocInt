import re
from typing import List, Dict

PAGE_RE = re.compile(r"_page_(\d+)_", re.IGNORECASE)


def extract_images(rendered) -> List[Dict]:
    images = []

    if not rendered.images:
        return images

    for name, img in rendered.images.items():
        m = PAGE_RE.search(name)
        page = int(m.group(1)) if m else None

        images.append({
            "name": name,      # markdown reference
            "image": img,      # in-memory image object
            "page": page,
        })

    return images
