"""Delisted Stocks — Buy/Sell price table + featured cards."""
import re
from bs4 import BeautifulSoup
from src.scrapers.base import fetch_html, parse_price


def scrape(url):
    try:
        html = fetch_html(url, expect_markers=["delistedstocks", "unlisted"])
    except Exception:
        return []

    soup = BeautifulSoup(html, "html.parser")
    stocks = {}

    # --- Strategy 1: the full table at the bottom of the page ---
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if len(rows) < 3:
            continue
        hdr = " ".join(c.get_text(" ", strip=True).lower()
                       for c in rows[0].find_all(["th", "td"]))
        if "company" not in hdr or not ("buy" in hdr or "sell" in hdr):
            continue
        for tr in rows[1:]:
            cells = tr.find_all(["td", "th"])
            if len(cells) < 3:
                continue
            name_cell = cells[0]
            name_link = name_cell.find("a")
            name = name_link.get_text(strip=True) if name_link else name_cell.get_text(strip=True)
            name = re.sub(r"\s+", " ", name).strip()
            if not name or len(name) < 3:
                continue
            buy_price = parse_price(cells[1].get_text(strip=True))
            sell_price = parse_price(cells[2].get_text(strip=True))
            # Average buy/sell for a mid price
            prices = [p for p in (buy_price, sell_price) if p is not None]
            price = round(sum(prices) / len(prices), 2) if prices else None

            detail_url = None
            if name_link and name_link.get("href"):
                href = name_link["href"]
                detail_url = href if href.startswith("http") else "https://www.delistedstocks.in" + href

            key = name.lower()
            if key not in stocks:
                stocks[key] = {"name": name, "price": price, "url": detail_url}
        break

    # --- Strategy 2: also grab the featured "Top Trending" cards ---
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/shares/" not in href:
            continue
        name = a.get_text(" ", strip=True)
        # The card text tends to include "Unlisted Shares" and prices
        name = re.sub(r"\s*Unlisted\s*Shares?.*$", "", name, flags=re.I).strip()
        if not name or len(name) < 3:
            continue
        full_url = href if href.startswith("http") else "https://www.delistedstocks.in" + href
        key = name.lower()
        if key not in stocks:
            stocks[key] = {"name": name, "price": None, "url": full_url}

    return list(stocks.values())
