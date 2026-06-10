import re

from app.models.knowledge_item import KnowledgeItem

CHUNK_SOURCE_PATTERN = re.compile(r"^knowledge-item:(\d+):")


def parse_knowledge_item_id(source: str) -> int | None:
    match = CHUNK_SOURCE_PATTERN.match(source)

    if not match:
        return None

    return int(match.group(1))


def build_source_snippet(content: str, max_chars: int = 180) -> str:
    cleaned = " ".join(content.split()).strip()

    if len(cleaned) <= max_chars:
        return cleaned

    return f"{cleaned[: max_chars - 3].rstrip()}..."


def build_source_label(item: KnowledgeItem) -> str:
    source_label = item.source_label.strip()

    if item.source_type == "website" and item.source_url:
        return item.source_url

    return source_label or item.title
