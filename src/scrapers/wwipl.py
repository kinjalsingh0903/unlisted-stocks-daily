"""WWIPL (Wealth Wisdom) — portfolio list with Last Traded Prices."""
import re
from bs4 import BeautifulSoup
from src.scrapers.base import fetch_html, parse_price


def scrape(url):
    try:
        html = fetch_html(url, expect_markers=["wwipl", "wealth"])
    except Exception:
        return []

    soup = BeautifulSoup(html, "html.parser")
    stocks = {}

    # Each stock is wrapped in an anchor that links to /unlisted-shares/<slug>-share-price
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/unlisted-shares/" not in href or "share-price" not in href:
            continue
        text = a.get_text(" ", strip=True)
        if not text or "Last Traded Price" not in text:
            continue

        # Name is the first line, price is after "Last Traded Price"
        m = re.search(r"^(.*?)\s+Last\s+Traded\s+Price\s+([\d,.]+)", text, re.S)
        if not m:
            continue
        name = m.group(1).strip()
        # Drop trailing short-form alias like "63sats" that's just a repeat
        name_parts = name.split(None, 1)
        # Clean: take only until we hit repeat of alias
        name = re.sub(r"\s+", " ", name).strip()

        price = parse_price(m.group(2))
        if not name or len(name) < 3:
            continue
        full_url = href if href.startswith("http") else "https://wwipl.com" + href
        key = name.lower()
        if key not in stocks:
            stocks[key] = {"name": name, "price": price, "url": full_url}

    return list(stocks.values())
