import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import requests

MAX_WEBSITE_PAGES = 5
MAX_INTERNAL_LINKS = 12


def is_human_readable_text(value: str) -> bool:
    cleaned_value = " ".join(value.split())

    if len(cleaned_value) < 25:
        return False

    blocked_fragments = (
        "queryselector",
        "addEventlistener",
        "modulepreload",
        "__vite__",
        "react.",
        ".js",
        "assets/",
        "localhost",
        "node_modules",
        "function(",
        "for(var",
        "typeof ",
        "object.keys(",
        "enqueuesetstate",
        "return ",
        "const ",
        "text/javascript",
        "application/javascript",
        "application/ecmascript",
        "button, input, select",
        "you are probably offline",
        "not a valid json response",
        "flash player",
        "left/right arrow",
        "increase or decrease volume",
        "<img id=",
        "<iframe src",
        "zloirock.ru",
    )

    lower_value = cleaned_value.lower()

    if any(fragment in lower_value for fragment in blocked_fragments):
        return False

    word_count = len(cleaned_value.split())

    if word_count < 4:
        return False

    alphabetic_characters = sum(character.isalpha() for character in cleaned_value)

    return alphabetic_characters >= max(20, int(len(cleaned_value) * 0.45))


def remove_irrelevant_sections(soup: BeautifulSoup) -> None:
    for tag in soup([
        "script",
        "style",
        "noscript",
        "svg",
        "button",
        "form",
        "input",
        "textarea",
        "select",
        "label",
    ]):
        tag.decompose()

    for tag in soup.find_all(["header", "nav", "footer", "aside"]):
        tag.decompose()

    for tag in list(soup.find_all(True)):
        if getattr(tag, "attrs", None) is None:
            continue

        role = str(tag.get("role") or "").lower()

        if role in {"navigation", "banner", "contentinfo", "complementary"}:
            tag.decompose()


def clean_content_blocks(content_blocks: list[str]) -> list[str]:
    cleaned_blocks: list[str] = []
    seen_blocks: set[str] = set()
    blocked_exact_phrases = {
        "home",
        "about us",
        "contact",
        "gallery",
        "book a table",
        "news",
        "food & beverages",
        "food and beverages",
        "menu",
    }

    for block in content_blocks:
        normalized_block = " ".join(block.split()).strip()
        lowercase_block = normalized_block.lower()

        if not normalized_block or lowercase_block in seen_blocks:
            continue

        if lowercase_block in blocked_exact_phrases:
            continue

        if len(normalized_block) < 35 and len(normalized_block.split()) < 6:
            continue

        if normalized_block.count(" · ") >= 3:
            continue

        if normalized_block.count("|") >= 3:
            continue

        seen_blocks.add(lowercase_block)
        cleaned_blocks.append(normalized_block)

    return cleaned_blocks


def build_request_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False

    return session


def build_request_headers() -> dict[str, str]:
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }


def fetch_url(
    session: requests.Session,
    url: str,
    headers: dict[str, str],
) -> requests.Response:
    try:
        response = session.get(
            url,
            timeout=15,
            headers=headers,
            allow_redirects=True,
        )
        response.raise_for_status()

        return response
    except requests.exceptions.SSLError:
        response = session.get(
            url,
            timeout=15,
            headers=headers,
            allow_redirects=True,
            verify=False,
        )
        response.raise_for_status()

        return response


def extract_text_from_script_bundles(
    soup: BeautifulSoup,
    page_url: str,
    session: requests.Session,
    headers: dict[str, str],
) -> list[str]:
    parsed_page_url = urlparse(page_url)
    collected_blocks: list[str] = []
    seen_blocks: set[str] = set()

    for script_tag in soup.find_all("script", src=True):
        script_url = urljoin(page_url, script_tag["src"])
        parsed_script_url = urlparse(script_url)

        if parsed_script_url.netloc and parsed_script_url.netloc != parsed_page_url.netloc:
            continue

        if not parsed_script_url.path.endswith(".js"):
            continue

        try:
            response = fetch_url(
                session=session,
                url=script_url,
                headers=headers,
            )
        except requests.RequestException:
            continue

        matches: list[str] = []
        matches.extend(re.findall(r':"([^"\\]{3,250})"', response.text))
        matches.extend(re.findall(r":'([^'\\\\]{3,250})'", response.text))
        matches.extend(re.findall(r'children:"([^"\\]{3,250})"', response.text))
        matches.extend(re.findall(r"children:'([^'\\\\]{3,250})'", response.text))

        for match in matches:
            normalized_match = " ".join(match.split())

            if normalized_match in seen_blocks:
                continue

            if not is_human_readable_text(normalized_match):
                continue

            seen_blocks.add(normalized_match)
            collected_blocks.append(normalized_match)

            if len(collected_blocks) >= 40:
                return collected_blocks

    return collected_blocks


def extract_internal_links(
    soup: BeautifulSoup,
    page_url: str,
) -> list[str]:
    parsed_page_url = urlparse(page_url)
    preferred_keywords = (
        "about",
        "service",
        "project",
        "work",
        "portfolio",
        "experience",
        "contact",
        "faq",
        "product",
        "solution",
    )
    candidate_links: list[str] = []
    seen_links: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        absolute_url = urljoin(page_url, anchor["href"])
        parsed_link = urlparse(absolute_url)

        if parsed_link.scheme not in {"http", "https"}:
            continue

        if parsed_link.netloc != parsed_page_url.netloc:
            continue

        normalized_url = parsed_link._replace(fragment="", query="").geturl().rstrip("/")

        if not normalized_url or normalized_url == page_url.rstrip("/"):
            continue

        if normalized_url in seen_links:
            continue

        seen_links.add(normalized_url)
        candidate_links.append(normalized_url)

    return sorted(
        candidate_links,
        key=lambda link: (
            0 if any(keyword in link.lower() for keyword in preferred_keywords) else 1,
            len(link),
        ),
    )[:MAX_INTERNAL_LINKS]


def extract_page_content(
    page_url: str,
    response_text: str,
    session: requests.Session,
    headers: dict[str, str],
) -> tuple[str, str]:
    soup = BeautifulSoup(response_text, "html.parser")

    page_title = ""

    if soup.title and soup.title.string:
        page_title = soup.title.string.strip()

    metadata_blocks: list[str] = []

    if page_title:
        metadata_blocks.append(page_title)

    for meta_name in (
        "description",
        "og:description",
        "twitter:description",
        "og:title",
        "twitter:title",
    ):
        meta_tag = soup.find("meta", attrs={"name": meta_name}) or soup.find(
            "meta",
            attrs={"property": meta_name},
        )

        if meta_tag and meta_tag.get("content"):
            metadata_blocks.append(meta_tag["content"].strip())

    remove_irrelevant_sections(soup)
    main_container = soup.body or soup

    content_blocks: list[str] = []

    for tag in main_container.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
        block_text = tag.get_text(" ", strip=True)

        if block_text and block_text not in content_blocks:
            content_blocks.append(block_text)

    content_blocks = clean_content_blocks(content_blocks)

    if content_blocks:
        visible_text = " ".join(content_blocks)
    else:
        visible_text = main_container.get_text(separator=" ")

    visible_text = " ".join(visible_text.split())
    cleaned_text = " ".join(" ".join(metadata_blocks + [visible_text]).split())

    if len(visible_text) < 120:
        bundle_blocks = extract_text_from_script_bundles(
            soup=soup,
            page_url=page_url,
            session=session,
            headers=headers,
        )

        if bundle_blocks:
            cleaned_text = " ".join(
                " ".join(metadata_blocks + bundle_blocks).split()
            )

    if len(cleaned_text) < 40:
        raise ValueError("Website content was too limited to import")

    return page_title or page_url, cleaned_text


def scrape_website_pages(url: str) -> list[tuple[str, str, str]]:
    session = build_request_session()
    headers = build_request_headers()
    pending_urls: list[str] = [url.rstrip("/")]
    visited_urls: set[str] = set()
    scraped_pages: list[tuple[str, str, str]] = []
    last_error: Exception | None = None

    while pending_urls and len(scraped_pages) < MAX_WEBSITE_PAGES:
        current_url = pending_urls.pop(0)

        if current_url in visited_urls:
            continue

        visited_urls.add(current_url)

        try:
            response = fetch_url(
                session=session,
                url=current_url,
                headers=headers,
            )

            page_title, cleaned_text = extract_page_content(
                page_url=current_url,
                response_text=response.text,
                session=session,
                headers=headers,
            )
            scraped_pages.append((current_url, page_title, cleaned_text))

            soup = BeautifulSoup(response.text, "html.parser")

            for link in extract_internal_links(soup=soup, page_url=current_url):
                if link not in visited_urls and link not in pending_urls:
                    pending_urls.append(link)
        except Exception as exc:
            last_error = exc
            continue

    if not scraped_pages and last_error is not None:
        raise last_error

    return scraped_pages


def scrape_website_text(url: str) -> str:
    scraped_pages = scrape_website_pages(url)

    return "\n\n".join(
        f"{page_title}\n{page_text}"
        for _, page_title, page_text in scraped_pages
    )
