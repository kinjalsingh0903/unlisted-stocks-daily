"""Planify detail-page enricher.

Planify's URL pattern: /research-report/<slug>/
The detail page has structured text like:
  "NSE, Unlisted Shares are trading at ₹1,906.00 per share and face value
   is ₹1.00/share, with a 52-week high of ₹2,470.00 and 52-week low of
   ₹1,650.00. The minimun lot size is 100 shares..."

We parse this prose with regex.
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


def enrich_planify_detail(detail_url):
    if not detail_url or "planify.in" not in detail_url:
        return {}
    try:
        html = fetch_html(detail_url, expect_markers=["planify", "unlisted"])
    except Exception:
        return {}

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    out = {}

    # Price: "trading at ₹1,906.00 per share"
    m = re.search(r"trading\s*at\s*₹\s*([\d,.]+)", text, re.I)
    if m:
        out["price"] = _num(m.group(1))

    # Face Value: "face value is ₹1.00/share"
    m = re.search(r"face\s*value\s*is\s*₹\s*([\d,.]+)", text, re.I)
    if m:
        out["face_value"] = _num(m.group(1))

    # 52 Week High: "52-week high of ₹2,470.00"
    m = re.search(r"52[-\s]?week\s*high\s*of\s*₹\s*([\d,.]+)", text, re.I)
    if m:
        out["w52_high"] = _num(m.group(1))

    # 52 Week Low: "52-week low of ₹1,650.00"
    m = re.search(r"52[-\s]?week\s*low\s*of\s*₹\s*([\d,.]+)", text, re.I)
    if m:
        out["w52_low"] = _num(m.group(1))

    # Lot Size: "lot size is 100 shares" or "minimun lot size is 100 shares"
    m = re.search(r"lot\s*size\s*(?:is\s*)?([\d,]+)\s*shares", text, re.I)
    if m:
        out["lot_size"] = _num(m.group(1))

    return {k: v for k, v in out.items() if v is not None}
