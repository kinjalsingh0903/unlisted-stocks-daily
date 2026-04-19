"""UnlistedZone: each stock is an <a> in an <h5>, price in the next <h5>."""
from bs4 import BeautifulSoup
from src.scrapers.base import fetch_html, parse_price


def scrape(url):
    try:
        html = fetch_html(url, expect_markers=["unlistedzone", "unlisted"])
    except Exception:
        return []

    soup = BeautifulSoup(html, "html.parser")
    stocks = []
    for a in soup.find_all("a", href=True):
        if "/shares/" not in a.get("href", ""):
            continue
        h5 = a.find_parent("h5")
        if not h5:
            continue
        name = a.get_text(strip=True)
        if not name or len(name) < 3:
            continue
        price = None
        next_h5 = h5.find_next_sibling("h5")
        if next_h5 and "₹" in next_h5.get_text():
            price = parse_price(next_h5.get_text().split("(")[0])
        full_url = a["href"] if a["href"].startswith("http") else "https://unlistedzone.com" + a["href"]
        stocks.append({"name": name, "price": price, "url": full_url})

    # Dedupe
    seen = set()
    unique = []
    for s in stocks:
        key = s["name"].lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(s)
    return unique
