"""
UnlistedZone detail-page enricher.
Pulls fields from stock detail pages like:
  https://unlistedzone.com/shares/nse-india-limited-unlisted-shares/

Available fields:
  - Lot Size (e.g. "250 Shares")
  - 52 Week High / Low
  - Market Cap, P/E, P/B, D/E, ROE, Book Value, Face Value
  - ISIN
"""
import re
from bs4 import BeautifulSoup
from src.scrapers.base import fetch_html


def _num(txt):
    if not txt:
        return None
    cleaned = re.sub(r"[^\d.\-]", "", str(txt))
    try:
        return float(cleaned)
    except ValueError:
        return None


def enrich_unlistedzone_detail(detail_url):
    """Fetch an UnlistedZone detail page and extract the Fundamentals block."""
    if not detail_url or "unlistedzone.com/shares" not in detail_url:
        return {}
    try:
        html = fetch_html(detail_url)
    except Exception:
        return {}

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    out = {}

    # The Fundamentals block has labels followed by values:
    # "Lot Size 250 Shares", "52 Week High ₹ 2400", "P/E Ratio 38.48"
    # We use label-proximity regexes.

    def grab(label_patterns, value_pattern=r"₹?\s*([\d,]+(?:\.\d+)?)"):
        for lp in label_patterns:
            pat = lp + r"\s*" + value_pattern
            m = re.search(pat, text, re.I)
            if m:
                return _num(m.group(1))
        return None

    out["lot_size"] = grab([r"Lot\s*Size"], r"([\d,]+)\s*(?:Share|share)")
    out["w52_high"] = grab([r"52\s*Week\s*High"])
    out["w52_low"]  = grab([r"52\s*Week\s*Low"])
    out["market_cap_cr"] = grab([r"Market\s*Cap\s*\(in\s*cr\.?\)", r"Market\s*Cap(?:\s*\(in\s*cr\.?\))?"])
    out["pe"] = grab([r"P/E\s*Ratio", r"Price[-\s]to[-\s]Earning"])
    out["pb"] = grab([r"P/B\s*Ratio", r"Price[-\s]to[-\s]Book"])
    out["de"] = grab([r"Debt\s*to\s*Equity", r"D/E"])
    out["roe_pct"] = grab([r"ROE\s*\(%?\)?"])
    out["book_value"] = grab([r"Book\s*Value"])
    out["face_value"] = grab([r"Face\s*Value"])

    # Strip None values so we don't overwrite better data
    return {k: v for k, v in out.items() if v is not None}
