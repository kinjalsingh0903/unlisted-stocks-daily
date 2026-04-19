"""
Unlisted Stocks — orchestrator (v5).

Key upgrades from v4:
  - Parallel list scraping (ThreadPoolExecutor) — faster, more reliable
  - Detailed per-source logging: shows (success, 0 stocks, or specific error)
  - Cross-source detail enrichment: if a pick came from InCred only, we STILL
    try to look up its Stockify and UnlistedZone detail pages by slug inference
    — this is what unblocks fields when list scrapers partially fail
"""
import sys
import re
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from src.config import SOURCES, TOP_N
from src.scrapers import get_scraper
from src.scrapers.base import normalize_name
from src.rank import rank_consensus
from src.enrich import enrich_picks
from src.populate import populate
from src.deliver import send_email


def _fetch_one(src):
    """Wrapper that isolates each scraper's success/failure."""
    sid = src["id"]
    name = src["name"]
    url = src["url"]
    scraper_id = src["scraper"]
    if not scraper_id:
        return (sid, name, None, "no scraper registered")
    scraper = get_scraper(scraper_id)
    if not scraper:
        return (sid, name, None, "scraper module missing")
    try:
        stocks = scraper(url)
        return (sid, name, stocks, None)
    except Exception as e:
        return (sid, name, None, f"{type(e).__name__}: {str(e)[:120]}")


def _name_to_slug(name):
    """Convert 'NSE India Limited' → 'nse-india-limited' for URL inference."""
    s = name.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    return s


def _guess_stockify_url(name):
    """Stockify detail URLs: /companies/<slug>-unlisted-shares/"""
    slug = _name_to_slug(name)
    return f"https://stockify.net.in/companies/{slug}-unlisted-shares/"


def _guess_unlistedzone_url(name):
    """UnlistedZone detail URLs: /shares/<slug>-unlisted-shares/"""
    slug = _name_to_slug(name)
    return f"https://unlistedzone.com/shares/{slug}-unlisted-shares/"


def run():
    today = datetime.today()
    date_str = today.strftime("%d %b %Y")
    date_long = today.strftime("%A, %d %B %Y")
    out_path = f"unlisted_top15_{today.strftime('%Y-%m-%d')}.xlsx"

    print(f"\n=== Unlisted Stocks — {date_str} ===\n")

    # ---------- Step 1: PARALLEL scrape of all list pages ----------
    print("Scraping list pages (parallel)...")
    scraped_by_source = {}
    fetched_names = set()
    failed = []

    active = [s for s in SOURCES if s["scraper"]]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(_fetch_one, s): s for s in active}
        for fut in as_completed(futures):
            sid, name, stocks, err = fut.result()
            if stocks is not None:
                scraped_by_source[sid] = stocks
                fetched_names.add(name)
                print(f"  ✓ {name:28} {len(stocks)} stocks")
                if len(stocks) == 0:
                    # Not a fetch failure but no data was parsed — log explicitly
                    print(f"    ⚠ returned 0 stocks — parser may be stale")
            else:
                failed.append((name, err))
                print(f"  ✗ {name:28} {err}")

    n_ok = sum(1 for stocks in scraped_by_source.values() if stocks)
    n_total = len(SOURCES)

    if n_ok == 0:
        print("\nERROR: zero sources returned data. Aborting.")
        sys.exit(1)

    # ---------- Step 2: consensus rank → top 15 ----------
    top_picks = rank_consensus(scraped_by_source)
    print(f"\nTop {TOP_N} picks (consensus across {n_ok} productive sources):")
    for i, p in enumerate(top_picks, 1):
        print(f"  {i:2}. {p['name']:40} ({p['n_sources']} sources)")

    # ---------- Step 3: merge list-page fields ----------
    picks_for_template = enrich_picks(top_picks, scraped_by_source, SOURCES)

    # ---------- Step 4: detail-page enrichment (with URL inference fallback) ----------
    print("\nDetail-page enrichment...")
    from src.scrapers.stockify_detail import enrich_stockify_detail
    from src.scrapers.unlistedzone_detail import enrich_unlistedzone_detail
    from src.scrapers.planify_detail import enrich_planify_detail

    stockify_urls = {
        s.get("name", "").lower(): s.get("url")
        for s in scraped_by_source.get("stockify", []) if s.get("url")
    }
    uz_urls = {
        s.get("name", "").lower(): s.get("url")
        for s in scraped_by_source.get("unlistedzone", []) if s.get("url")
    }

    def find_url(name, url_map):
        pname = name.lower()
        for sname, url in url_map.items():
            if pname in sname or sname in pname:
                return url
        return None

    def _guess_planify_url(name):
        slug = re.sub(r"[^\w\s-]", "", name.lower())
        slug = re.sub(r"\s+", "-", slug).strip("-")
        return f"https://www.planify.in/research-report/{slug}/"

    def enrich_one_pick(p):
        total_added = 0
        # Stockify
        sky_url = find_url(p["name"], stockify_urls) or _guess_stockify_url(p["name"])
        try:
            fields = enrich_stockify_detail(sky_url)
            for k, v in fields.items():
                if v is not None and p.get(k) is None:
                    p[k] = v
                    total_added += 1
        except Exception:
            pass

        # UnlistedZone
        uz_url = find_url(p["name"], uz_urls) or _guess_unlistedzone_url(p["name"])
        try:
            fields = enrich_unlistedzone_detail(uz_url)
            for k, v in fields.items():
                if v is not None and p.get(k) is None:
                    p[k] = v
                    total_added += 1
        except Exception:
            pass

        # Planify
        planify_url = _guess_planify_url(p["name"])
        try:
            fields = enrich_planify_detail(planify_url)
            for k, v in fields.items():
                if v is not None and p.get(k) is None:
                    p[k] = v
                    total_added += 1
        except Exception:
            pass

        return (p["name"], total_added)

    # Parallel detail-page fetching
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(enrich_one_pick, p) for p in picks_for_template]
        for fut in as_completed(futures):
            name, n_added = fut.result()
            print(f"  {name:40} +{n_added} fields")

    # ---------- Step 5: IPO pipeline match across 3 sources ----------
    print("\nIPO pipeline lookup (Chittorgarh + IPO Central + IPO Watch)...")
    try:
        from src.scrapers.chittorgarh import scrape as ch_scrape, build_ipo_lookup
        all_ipo_records = []
        ipo_urls = [
            "https://www.chittorgarh.com/report/upcoming-ipos-drhp-filed/158/all/",
            "https://www.ipocentral.in/upcoming-ipo/",
            "https://ipowatch.in/upcoming-ipo-list/",
        ]
        for iu in ipo_urls:
            try:
                recs = ch_scrape(iu)
                all_ipo_records.extend(recs)
            except Exception:
                continue
        ipo_lookup = build_ipo_lookup(all_ipo_records)
        print(f"  {len(all_ipo_records)} total IPO pipeline records across 3 sources")
        for p in picks_for_template:
            key = normalize_name(p["name"])
            match = ipo_lookup.get(key)
            if match:
                if not p.get("ipo_status"):
                    p["ipo_status"] = match.get("ipo_status")
                if not p.get("ipo_window"):
                    p["ipo_window"] = match.get("ipo_window")
    except Exception as e:
        print(f"  ✗ IPO pipeline lookup failed: {type(e).__name__}")

    # ---------- Step 6: peer lookup ----------
    try:
        from src.peers import peer_lookup
        for p in picks_for_template:
            if p.get("sector"):
                peers, peer_pe = peer_lookup(p["sector"])
                if peers and not p.get("peers_name"):
                    p["peers_name"] = peers
                if peer_pe and not p.get("peer_pe"):
                    p["peer_pe"] = peer_pe
    except Exception as e:
        print(f"  ✗ Peer lookup failed: {type(e).__name__}")

    # ---------- Step 7: populate ----------
    populate(picks_for_template, fetched_names, out_path)
    print(f"\nWrote: {out_path}")

    # ---------- Step 8: email ----------
    try:
        send_email(out_path, date_str, date_long, n_ok, n_total)
        print("Emailed to recipient.")
    except Exception as e:
        print(f"\nERROR sending email: {e}")
        sys.exit(2)

    if failed:
        print(f"\nFailed sources ({len(failed)}):")
        for name, err in failed:
            print(f"  - {name}: {err}")


if __name__ == "__main__":
    try:
        run()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
