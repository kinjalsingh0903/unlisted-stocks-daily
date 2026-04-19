"""
Enrichment: for each top-N consensus pick, merge every field that any scraper
returned for that stock into one enriched row. No extra HTTP calls needed —
Stockify already returns face_value, book_value, market_cap, P/E, IPO status
on the main list page, so the data is already in memory.
"""
from src.scrapers.base import normalize_name


# Fields we try to enrich from any source that reported them
ENRICHABLE_FIELDS = [
    "sector", "price", "face_value", "lot_size", "market_cap_cr",
    "w52_high", "w52_low", "pe", "pb", "book_value", "de", "roe_pct",
    "rev_growth_pct", "ret_1y_pct", "ret_2y_pct",
    "peers_name", "peer_pe", "ipo_status", "ipo_window",
]


def enrich_picks(top_picks, scraped_by_source, sources_config):
    """
    top_picks:        list of dicts from rank.rank_consensus()
    scraped_by_source: dict[source_id -> list of raw stock dicts]
    sources_config:    the SOURCES list from config.py (for id → display name)

    Returns: list of enriched dicts ready for populate().
    """
    # Build a lookup: normalized_name -> list of (source_id, raw_stock_dict)
    index = {}
    for sid, stocks in scraped_by_source.items():
        for s in stocks:
            key = normalize_name(s.get("name", ""))
            if not key:
                continue
            index.setdefault(key, []).append((sid, s))

    name_lookup = {s["id"]: s["name"] for s in sources_config}

    enriched = []
    for pick in top_picks:
        key = pick["key"]
        reports = index.get(key, [])

        # Start with empty field set
        out = {f: None for f in ENRICHABLE_FIELDS}

        # Average numeric fields across sources that reported them
        numeric_fields = ["price", "face_value", "market_cap_cr", "pe", "book_value",
                         "pb", "de", "roe_pct", "lot_size"]
        for fld in numeric_fields:
            vals = [r[1].get(fld) for r in reports if r[1].get(fld) is not None]
            if vals:
                out[fld] = round(sum(vals) / len(vals), 2)

        # Text fields: take the first non-empty
        text_fields = ["sector", "ipo_status", "ipo_window", "peers_name"]
        for fld in text_fields:
            for _, r in reports:
                if r.get(fld):
                    out[fld] = r[fld]
                    break

        # Primary source = first source in consensus list
        primary_id = pick["sources"][0] if pick["sources"] else None
        primary_name = name_lookup.get(primary_id, primary_id)

        enriched.append({
            "name": pick["name"],
            **out,
            "n_sources": pick["n_sources"],
            "primary_source": primary_name,
        })

    return enriched
