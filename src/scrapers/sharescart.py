"""SharesCart: horizontal ticker with concatenated name + price + % change."""
import re
from bs4 import BeautifulSoup
from src.scrapers.base import fetch_html, parse_price

TICKER = re.compile(
    r"([A-Z][A-Za-z0-9 &.\-/]{2,40}?)\s*₹\s*([\d,]+(?:\.\d+)?)\s*\(([\-\+]?\d+(?:\.\d+)?)%\)"
)


def scrape(url):
    try:
        html = fetch_html(url, expect_markers=["sharescart", "unlisted"])
    except Exception:
        return []

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    stocks = {}
    for m in TICKER.finditer(text):
        name = m.group(1).strip()
        if any(w in name.lower() for w in ["share", "price", "copyright", "disclaimer", "rated"]):
            continue
        if len(name) < 2:
            continue
        key = name.lower()
        if key not in stocks:
            stocks[key] = {"name": name, "price": parse_price(m.group(2)), "url": None}
    return list(stocks.values())
