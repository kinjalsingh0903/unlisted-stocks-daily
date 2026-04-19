"""
Chittorgarh upcoming IPOs scraper.
Source: https://www.chittorgarh.com/report/upcoming-ipos-drhp-filed/158/all/

Returns list of {name, ipo_status, ipo_window}.
Used at enrichment time to fill IPO Status + Expected Window when we can
name-match one of our top-15 picks to a company on this list.
"""
import re
from bs4 import BeautifulSoup
from src.scrapers.base import fetch_html, normalize_name


def scrape(url):
    try:
        html = fetch_html(url)
    except Exception:
        return []

    soup = BeautifulSoup(html, "html.parser")
    records = []

    # Chittorgarh uses HTML tables. Find the upcoming-IPO table.
    for table in soup.find_all("table"):
        header = table.find("tr")
        if not header:
            continue
        hdr_text = header.get_text(" ", strip=True).lower()
        # Must contain "company" and some IPO-related label
        if "company" not in hdr_text:
            continue
        if not any(k in hdr_text for k in ["status", "drhp", "filing", "ipo"]):
            continue

        for tr in table.find_all("tr")[1:]:
            cells = tr.find_all(["td", "th"])
            if len(cells) < 2:
                continue
            name = cells[0].get_text(" ", strip=True)
            if not name or len(name) < 3:
                continue
            status = cells[1].get_text(" ", strip=True) if len(cells) > 1 else ""
            # Try to find a date-like field in remaining cells
            window = None
            for c in cells[2:]:
                t = c.get_text(" ", strip=True)
                if re.search(r"\b(20\d\d|FY\d\d|Q[1-4])\b", t):
                    window = t
                    break
            records.append({
                "name": name,
                "ipo_status": status or "Filed",
                "ipo_window": window,
            })

    return records


def build_ipo_lookup(chittorgarh_records):
    """Convert list → dict keyed on normalized name, for fast lookup during enrichment."""
    return {normalize_name(r["name"]): r for r in chittorgarh_records}
