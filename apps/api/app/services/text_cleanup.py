import re
import unicodedata

COMMON_MOJIBAKE_REPLACEMENTS = {
    "Â·": " ",
    "â€¢": " ",
    "â€“": "-",
    "â€”": "-",
    "â€˜": "'",
    "â€™": "'",
    'â€œ': '"',
    'â€\x9d': '"',
    "Ã—": "x",
    "ﬁ": "fi",
    "ﬂ": "fl",
    "\uf0b7": " ",
    "\u2022": " ",
    "\u25cf": " ",
    "\u25aa": " ",
    "\u25ab": " ",
    "\u200b": "",
    "\u200c": "",
    "\u200d": "",
    "\ufeff": "",
    "\ufffd": "",
}

BLOCKED_LINE_PATTERNS = (
    r"^page\s+\d+(\s+of\s+\d+)?$",
    r"^www\.[^\s]+$",
)


def _replace_common_mojibake(text: str) -> str:
    cleaned = text

    for wrong, right in COMMON_MOJIBAKE_REPLACEMENTS.items():
        cleaned = cleaned.replace(wrong, right)

    return cleaned


def _normalize_line(line: str) -> str:
    line = unicodedata.normalize("NFKC", line)
    line = _replace_common_mojibake(line)
    line = "".join(
        character
        for character in line
        if character in "\t\n\r" or unicodedata.category(character)[0] != "C"
    )
    line = re.sub(r"https?://\S+", lambda match: match.group(0).strip(".,;"), line)
    line = re.sub(r"\s*[|/\\]+\s*", " | ", line)
    line = re.sub(r"\s*[-]{2,}\s*", " - ", line)
    line = re.sub(r"\s+", " ", line)
    line = re.sub(r"\s+([,.;:!?])", r"\1", line)

    return line.strip(" -|")


def _should_drop_line(line: str) -> bool:
    lowered = line.lower()

    if not lowered:
        return True

    if sum(character.isalpha() for character in line) < 2:
        return True

    if re.fullmatch(r"[\W_]+", line):
        return True

    return any(re.fullmatch(pattern, lowered) for pattern in BLOCKED_LINE_PATTERNS)


def normalize_extracted_text(text: str) -> str:
    if not text:
        return ""

    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")
    raw_lines = normalized_text.split("\n")
    cleaned_lines: list[str] = []

    for raw_line in raw_lines:
        cleaned_line = _normalize_line(raw_line)

        if _should_drop_line(cleaned_line):
            continue

        cleaned_lines.append(cleaned_line)

    paragraphs: list[str] = []
    current_paragraph: list[str] = []

    for line in cleaned_lines:
        if not current_paragraph:
            current_paragraph.append(line)
            continue

        previous_line = current_paragraph[-1]
        should_join_tightly = (
            not previous_line.endswith((".", "!", "?", ":"))
            and not line[:1].isupper()
        ) or previous_line.endswith(("(", "/", "|"))

        if should_join_tightly:
            current_paragraph[-1] = f"{previous_line} {line}".strip()
            continue

        if previous_line.endswith((".", "!", "?", ":")) or line[:1].isupper():
            paragraphs.append(" ".join(current_paragraph).strip())
            current_paragraph = [line]
            continue

        current_paragraph.append(line)

    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph).strip())

    cleaned_paragraphs = []

    for paragraph in paragraphs:
        paragraph = re.sub(r"\s{2,}", " ", paragraph).strip()
        paragraph = re.sub(r"\s*\|\s*", " | ", paragraph)

        if paragraph:
            cleaned_paragraphs.append(paragraph)

    return "\n\n".join(cleaned_paragraphs)
