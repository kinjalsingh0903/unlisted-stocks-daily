"""InCred Money: anchor list of unlisted stocks, prices on featured cards."""
import re
from bs4 import BeautifulSoup
from src.scrapers.base import fetch_html, parse_price


def scrape(url):
    try:
        html = fetch_html(url, expect_markers=["incredmoney", "unlisted"])
    except Exception:
        return []

    soup = BeautifulSoup(html, "html.parser")
    stocks = {}
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not re.search(r"/unlisted-shares/[^/]+/[^/]+", href):
            continue
        name = a.get_text(" ", strip=True)
        h3 = a.find("h3")
        if h3:
            name = h3.get_text(strip=True)
        if not name or len(name) < 3:
            continue
        full_url = href if href.startswith("http") else "https://www.incredmoney.com" + href
        parent_text = a.get_text(" ", strip=True)
        price = None
        m = re.search(r"₹\s*([\d,]+(?:\.\d+)?)", parent_text)
        if m:
            price = parse_price("₹" + m.group(1))
        key = name.lower().strip()
        if key not in stocks:
            stocks[key] = {"name": name, "price": price, "url": full_url}
        elif price and not stocks[key]["price"]:
            stocks[key]["price"] = price
    return list(stocks.values())
