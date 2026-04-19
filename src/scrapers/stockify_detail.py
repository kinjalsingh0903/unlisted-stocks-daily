"""
Stockify detail-page enricher.
For a given stock detail URL, pulls:
  - sector
  - P/B ratio
  - Debt/Equity
  - ROE %
  - Revenue Growth YoY %
  - IPO/DRHP status (refined)

Called per-pick after ranking, not for every stock.
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


def enrich_stockify_detail(detail_url):
    """Fetch one detail page and return a dict of extracted fields.
    Returns empty dict on any failure.
    """
    if not detail_url or "stockify.net.in/companies" not in detail_url:
        return {}
    try:
        html = fetch_html(detail_url)
    except Exception:
        return {}

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    out = {}

    # Sector — appears as "Industry: X | Sector: Y" near the top
    m = re.search(r"Sector:\s*([A-Za-z &/\-]+?)(?:\s*[|\.]|\s{2,}|$)", text)
    if m:
        out["sector"] = m.group(1).strip()

    # DRHP status — "DRHP: not filed" or "DRHP: filed"
    m = re.search(r"DRHP:\s*([A-Za-z ]+?)(?:\s{2,}|$|[,\.])", text, re.I)
    if m:
        status = m.group(1).strip()
        out["ipo_status"] = "Filed" if "not" not in status.lower() else "Not Filed"

    # Key Indicators table — find the row values
    # The table has rows like "Price To Earning (PE) | 18.20"
    # We use label-based lookup because row order can vary
    def find_indicator(label_patterns):
        """Find a number following any of the given label strings in order."""
        for pat in label_patterns:
            m = re.search(pat + r"[\s|]+([\d,.\-]+)%?", text, re.I)
            if m:
                return _num(m.group(1))
        return None

    out["pb"] = find_indicator([r"Price\s*\|\s*Book", r"Price\s*To\s*Book", r"P/B\s+Ratio"])
    out["de"] = find_indicator([r"Debt\s*\|\s*Equity", r"Debt\s*To\s*Equity", r"D/E\s+Ratio"])
    out["roe_pct"] = find_indicator([r"Return\s*on\s*Equity"])

    # Revenue Growth: the Profit & Loss table has a row "Revenue Growth %" with
    # 5 values like "-0.8% | 16% | 2.1% | 37.1% | -"
    # We want the most recent (first of the series, since table goes 2025 → 2021)
    m = re.search(r"Revenue\s*Growth\s*%[\s|]+([\-\d.]+)%", text, re.I)
    if m:
        out["rev_growth_pct"] = _num(m.group(1))

    return out
