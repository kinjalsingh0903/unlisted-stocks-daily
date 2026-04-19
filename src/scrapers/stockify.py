"""Stockify: parses the price list table."""
import re
from bs4 import BeautifulSoup
from src.scrapers.base import fetch_html


def _clean_name(name):
    if not name:
        return ""
    parts = name.split("Unlisted Shares")
    first = parts[0].strip() if parts else name.strip()
    return re.sub(r"\s+", " ", first).strip()


def _to_float(txt):
    if not txt:
        return None
    cleaned = re.sub(r"[^\d.\-]", "", str(txt))
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_table(html):
    soup = BeautifulSoup(html, "html.parser")
    stocks = []
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if len(rows) < 3:
            continue
        hdr = " ".join(c.get_text(" ", strip=True).lower()
                       for c in rows[0].find_all(["th", "td"]))
        if "company" not in hdr or "price" not in hdr:
            continue
        for tr in rows[1:]:
            cells = tr.find_all(["td", "th"])
            if len(cells) < 7:
                continue
            name_cell = cells[1]
            name_link = name_cell.find("a")
            name = _clean_name(name_link.get_text(" ", strip=True)) if name_link else _clean_name(name_cell.get_text(" ", strip=True))
            if not name:
                continue
            detail_url = None
            if name_link and name_link.get("href"):
                href = name_link["href"]
                detail_url = href if href.startswith("http") else "https://stockify.net.in" + href
            stocks.append({
                "name": name,
                "price": _to_float(cells[2].get_text(strip=True)),
                "face_value": _to_float(cells[3].get_text(strip=True)),
                "book_value": _to_float(cells[4].get_text(strip=True)),
                "market_cap_cr": _to_float(cells[5].get_text(strip=True)),
                "pe": _to_float(cells[6].get_text(strip=True)),
                "ipo_status": cells[7].get_text(strip=True) if len(cells) > 7 else None,
                "url": detail_url,
            })
        break
    return stocks


def _parse_cards(html):
    """Fallback: parse trending-shares page as linked cards."""
    soup = BeautifulSoup(html, "html.parser")
    stocks = {}
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/companies/" not in href:
            continue
        name = _clean_name(a.get_text(" ", strip=True))
        # Price may be in a sibling
        price = None
        parent = a.find_parent()
        if parent:
            m = re.search(r"₹\s*([\d,]+(?:\.\d+)?)", parent.get_text(" ", strip=True))
            if m:
                price = _to_float(m.group(1))
        if not name or len(name) < 3:
            continue
        full_url = href if href.startswith("http") else "https://stockify.net.in" + href
        key = name.lower()
        if key not in stocks:
            stocks[key] = {"name": name, "price": price, "url": full_url}
    return list(stocks.values())


def scrape(url):
    """Try the price-list table first; fall back to trending-shares cards."""
    markers = ["stockify", "unlisted"]
    try:
        html = fetch_html(url, expect_markers=markers)
    except Exception:
        return []

    stocks = _parse_table(html)
    if stocks:
        return stocks

    # Table not found on this page — try the buy-unlisted-shares (cards) page
    try:
        html = fetch_html("https://stockify.net.in/buy-unlisted-shares/",
                         expect_markers=markers)
    except Exception:
        return []
    return _parse_cards(html)
