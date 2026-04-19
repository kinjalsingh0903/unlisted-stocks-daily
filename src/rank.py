"""
Consensus-led ranking: pick top 10 stocks that appear across the most sources.

Tie-break order (as agreed with user):
  1. 1Y return (higher wins)
  2. Revenue growth YoY (higher wins)
Since we don't have those fields from the list-page scrape, ties initially
break by average price across sources (higher = more liquid name) as a proxy,
and later by the enriched fields once enrich.py runs.
"""
from collections import defaultdict
from src.scrapers.base import normalize_name
from src.config import TOP_N


def rank_consensus(scraped_by_source):
    """
    scraped_by_source: dict[source_id -> list of stock dicts from that source]
    Returns: list of up to TOP_N picks, each a dict with:
        name (the cleanest name we saw),
        sources (list of source_ids that carry this stock),
        n_sources (int),
        prices_by_source (dict),
        urls_by_source (dict),
    """
    # Key by normalized name; collect all appearances
    buckets = defaultdict(lambda: {
        "display_names": [],
        "sources": [],
        "prices_by_source": {},
        "urls_by_source": {},
    })

    for source_id, stocks in scraped_by_source.items():
        for s in stocks:
            key = normalize_name(s.get("name", ""))
            if not key:
                continue
            bucket = buckets[key]
            bucket["display_names"].append(s["name"])
            if source_id not in bucket["sources"]:
                bucket["sources"].append(source_id)
            if s.get("price") is not None:
                bucket["prices_by_source"][source_id] = s["price"]
            if s.get("url"):
                bucket["urls_by_source"][source_id] = s["url"]

    # Build candidates
    candidates = []
    for key, b in buckets.items():
        n_sources = len(b["sources"])
        # Pick the shortest display name as canonical (usually cleanest)
        display = min(b["display_names"], key=len)
        # Tie-break proxy: average available price
        prices = list(b["prices_by_source"].values())
        avg_price = sum(prices) / len(prices) if prices else 0.0
        candidates.append({
            "key": key,
            "name": display,
            "sources": b["sources"],
            "n_sources": n_sources,
            "prices_by_source": b["prices_by_source"],
            "urls_by_source": b["urls_by_source"],
            "avg_price": avg_price,
        })

    # Sort: n_sources desc, then avg_price desc (proxy for liquid/high-priced names)
    candidates.sort(key=lambda x: (-x["n_sources"], -x["avg_price"], x["name"]))

    return candidates[:TOP_N]
