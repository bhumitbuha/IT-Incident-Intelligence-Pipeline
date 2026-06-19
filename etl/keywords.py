import re

from config import CATEGORY_MAP

KEYWORD_PATTERNS = {
    kw: re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE) for kw in CATEGORY_MAP
}


def extract_keywords(text: str) -> list[str]:
    if not text:
        return []
    found = []
    for kw, pattern in KEYWORD_PATTERNS.items():
        if pattern.search(text):
            found.append(kw)
    return found


def map_to_category(keywords: list[str], raw_category: str) -> str:
    if raw_category:
        norm = raw_category.strip().lower()
        if norm in CATEGORY_MAP:
            return CATEGORY_MAP[norm]
    for kw in keywords:
        if kw in CATEGORY_MAP:
            return CATEGORY_MAP[kw]
    return "Uncategorized"
