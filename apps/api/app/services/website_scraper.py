from bs4 import BeautifulSoup
import requests


def scrape_website_text(url: str) -> str:
    response = requests.get(
        url,
        timeout=10,
        headers={
            "User-Agent": "Mozilla/5.0 AI Chat Platform Bot",
        },
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ")

    cleaned_text = " ".join(text.split())

    return cleaned_text