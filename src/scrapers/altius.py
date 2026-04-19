"""Altius Investech: A-Z anchor index of companies."""
import re
from bs4 import BeautifulSoup
from src.scrapers.base import fetch_html


def scrape(url):
    try:
        html = fetch_html(url, expect_markers=["altius", "company"])
    except Exception:
        return []

    soup = BeautifulSoup(html, "html.parser")
    stocks = {}
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/company/" not in href:
            continue
        name = re.sub(r"\s+", " ", a.get_text(" ", strip=True)).strip()
        if not name or len(name) < 3:
            continue
        full_url = href if href.startswith("http") else "https://altiusinvestech.com" + href
        key = name.lower()
        if key not in stocks:
            stocks[key] = {"name": name, "price": None, "url": full_url}
    return list(stocks.values())
