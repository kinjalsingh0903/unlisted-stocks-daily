"""Scrapers package. Each scraper exposes a `scrape(url)` function
that returns a list of stock dicts. Fields per dict:
  name (required), price, url, plus any enrichment fields:
  face_value, book_value, market_cap_cr, pe, ipo_status, etc.
"""
from importlib import import_module

SCRAPER_REGISTRY = {
    "unlistedzone":   "src.scrapers.unlistedzone",
    "incredmoney":    "src.scrapers.incredmoney",
    "unlistedarena":  "src.scrapers.unlistedarena",
    "stockify":       "src.scrapers.stockify",
    "altius":         "src.scrapers.altius",
    "sharescart":     "src.scrapers.sharescart",
    "chittorgarh":    "src.scrapers.chittorgarh",
    "wwipl":          "src.scrapers.wwipl",
    "delistedstocks": "src.scrapers.delistedstocks",
}


def get_scraper(scraper_id):
    mod_path = SCRAPER_REGISTRY.get(scraper_id)
    if not mod_path:
        return None
    try:
        mod = import_module(mod_path)
        return getattr(mod, "scrape", None)
    except Exception:
        return None
