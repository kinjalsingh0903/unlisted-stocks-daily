"""Unlisted Arena: each stock is a link to /unlisted-shares-list/buy-<slug>."""
import re
from bs4 import BeautifulSoup
from src.scrapers.base import fetch_html


def scrape(url):
    try:
        html = fetch_html(url, expect_markers=["unlistedarena", "unlisted"])
    except Exception:
        return []

    soup = BeautifulSoup(html, "html.parser")
    stocks = {}
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not re.search(r"/unlisted-shares-list/buy-[^/]+-unlisted-shares/?$", href):
            continue
        name = a.get("title", "").strip() or a.get_text(strip=True)
        name = re.sub(r"\s*[Uu]nlisted\s+[Ss]hares?\s*$", "", name).strip()
        if not name or len(name) < 2:
            continue
        full_url = href if href.startswith("http") else "https://www.unlistedarena.com" + href
        key = name.lower()
        if key not in stocks:
            stocks[key] = {"name": name, "price": None, "url": full_url}
    return list(stocks.values())
