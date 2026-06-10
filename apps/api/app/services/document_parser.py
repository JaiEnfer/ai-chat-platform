import csv
import io
import json
from collections.abc import Iterable
from pathlib import Path

from bs4 import BeautifulSoup

from app.services.text_cleanup import normalize_extracted_text


def normalize_text(text: str) -> str:
    return normalize_extracted_text(text)


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    content_blocks: list[str] = []

    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
        block_text = tag.get_text(" ", strip=True)

        if block_text and block_text not in content_blocks:
            content_blocks.append(block_text)

    if content_blocks:
        return normalize_text("\n".join(content_blocks))

    return normalize_text(soup.get_text(" "))


def collect_json_strings(value: object) -> Iterable[str]:
    if isinstance(value, str):
        yield value
        return

    if isinstance(value, dict):
        for nested_value in value.values():
            yield from collect_json_strings(nested_value)
        return

    if isinstance(value, list):
        for nested_value in value:
            yield from collect_json_strings(nested_value)


def parse_uploaded_document(filename: str, file_bytes: bytes) -> str:
    extension = Path(filename).suffix.lower()

    if extension in {".txt", ".md", ".rst"}:
        return normalize_text(file_bytes.decode("utf-8", errors="ignore"))

    if extension in {".html", ".htm"}:
        return html_to_text(file_bytes.decode("utf-8", errors="ignore"))

    if extension == ".csv":
        text_stream = io.StringIO(file_bytes.decode("utf-8", errors="ignore"))
        reader = csv.reader(text_stream)
        rows = [" | ".join(cell.strip() for cell in row if cell.strip()) for row in reader]
        return normalize_text("\n".join(row for row in rows if row))

    if extension == ".json":
        data = json.loads(file_bytes.decode("utf-8", errors="ignore"))
        return normalize_text(" ".join(collect_json_strings(data)))

    if extension == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(file_bytes))
        page_text = [page.extract_text() or "" for page in reader.pages]
        return normalize_text("\n\n".join(page_text))

    if extension == ".docx":
        from docx import Document

        document = Document(io.BytesIO(file_bytes))
        paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
        return normalize_text("\n".join(paragraphs))

    raise ValueError(
        "Unsupported file type. Upload txt, md, html, csv, json, pdf, or docx."
    )
