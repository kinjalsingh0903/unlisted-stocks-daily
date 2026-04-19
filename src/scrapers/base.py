"""Shared HTTP utilities with ScraperAPI integration, retries, and diagnostics.

Critical behaviors added in v5:
  - Retry on ScraperAPI rate limits (429) with backoff
  - Detect ScraperAPI error pages (short HTML, no real content)
  - Raise a clear exception if fetched HTML doesn't look like the target site
  - Logging-friendly: surface fetch size so we can tell real HTML from error pages
"""
import re
import time
import requests

from src.config import (
    USER_AGENT, REQUEST_TIMEOUT, REQUEST_DELAY_SECONDS,
    SCRAPERAPI_KEY, USE_SCRAPERAPI,
)

_last_request_ts = 0.0


class FetchError(Exception):
    pass


def fetch_html(url, extra_headers=None, render_js=False, expect_markers=None, max_retries=3):
    """Polite GET with retries and ScraperAPI support.

    expect_markers: optional list of strings that should appear in the returned
                    HTML. If none are found, the fetch is treated as an error
                    (likely a ScraperAPI block page or empty response).
    """
    global _last_request_ts
    elapsed = time.time() - _last_request_ts
    if elapsed < REQUEST_DELAY_SECONDS:
        time.sleep(REQUEST_DELAY_SECONDS - elapsed)

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-IN,en;q=0.9",
    }
    if extra_headers:
        headers.update(extra_headers)

    last_err = None
    for attempt in range(max_retries):
        try:
            if USE_SCRAPERAPI:
                api_url = "https://api.scraperapi.com/"
                params = {
                    "api_key": SCRAPERAPI_KEY,
                    "url": url,
                    "country_code": "in",
                }
                if render_js:
                    params["render"] = "true"
                resp = requests.get(api_url, params=params, headers=headers, timeout=REQUEST_TIMEOUT + 30)
            else:
                resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)

            _last_request_ts = time.time()

            # ScraperAPI returns 429 on concurrency/rate limits — back off
            if resp.status_code == 429:
                wait = (attempt + 1) * 5
                time.sleep(wait)
                continue

            resp.raise_for_status()

            html = resp.text

            # Sanity check: HTML too short probably means a block or error page
            if len(html) < 500:
                raise FetchError(f"HTML too short ({len(html)} bytes) — likely block page")

            # Expected marker check (e.g. "company", "unlisted") — ensures we
            # got the real site, not a Cloudflare challenge / ScraperAPI error
            if expect_markers:
                low = html.lower()
                if not any(m.lower() in low for m in expect_markers):
                    raise FetchError(
                        f"HTML missing expected markers {expect_markers} — likely block page"
                    )

            return html

        except (requests.RequestException, FetchError) as e:
            last_err = e
            if attempt < max_retries - 1:
                time.sleep((attempt + 1) * 3)
                continue

    raise FetchError(f"All {max_retries} attempts failed. Last error: {last_err}")


def parse_price(text):
    if not text:
        return None
    cleaned = str(text).replace("₹", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


# === Name alias table ===
ALIASES = {
    "nse": "national stock exchange",
    "nse india": "national stock exchange",
    "national stock exchange ltd nse": "national stock exchange",
    "national stock exchange of india": "national stock exchange",
    "nse india limited": "national stock exchange",
    "msei": "metropolitan stock exchange",
    "metropolitan stock exchange msei": "metropolitan stock exchange",
    "metropolitan stock exchange of india": "metropolitan stock exchange",
    "csk": "chennai super kings",
    "chennai super kings cricket": "chennai super kings",
    "chennai super kings cricket csk": "chennai super kings",
    "hdfc sec": "hdfc securities",
    "hdfc securities ltd": "hdfc securities",
    "oyo": "oravel stays",
    "oyo rooms": "oravel stays",
    "oravel stays": "oravel stays",
    "pharmeasy": "api holdings",
    "pharmeasy api holdings": "api holdings",
    "api holdings": "api holdings",
    "orbis financial": "orbis financial",
    "orbis financial corporation": "orbis financial",
    "ask investment managers": "ask investment managers",
    "ask im": "ask investment managers",
    "ncdex": "ncdex",
    "national commodity derivatives exchange": "ncdex",
    "national commodity and derivatives exchange": "ncdex",
    "nayara energy": "nayara energy",
    "essar oil": "nayara energy",
    "nayara energy formerly essar oil": "nayara energy",
    "apollo green energy": "apollo green energy",
    "apollo green": "apollo green energy",
    "anheuser busch inbev india": "anheuser busch inbev india",
    "ab inbev india": "anheuser busch inbev india",
    "anheuser busch inbev sabmiller india": "anheuser busch inbev india",
    "sabmiller india": "anheuser busch inbev india",
    "bigbasket": "bigbasket",
    "big basket": "bigbasket",
    "supermarket grocery supplies": "bigbasket",
    "bira": "bira 91",
    "bira 91": "bira 91",
    "bira91": "bira 91",
    "b9 beverages": "bira 91",
    "parag parikh financial advisory services": "parag parikh",
    "parag parikh financial advisory services ppfas": "parag parikh",
    "ppfas": "parag parikh",
    "tata capital": "tata capital",
    "tata capital financial services": "tata capital",
    "hdb financial": "hdb financial",
    "hdb financial services": "hdb financial",
    "cochin international airport": "cochin international airport",
    "cial": "cochin international airport",
    "capgemini": "capgemini",
    "capgemini technology services india": "capgemini",
    "capgemini technology services": "capgemini",
    "indofil industries": "indofil industries",
    "indofil": "indofil industries",
    "hero fincorp": "hero fincorp",
    "merino industries": "merino industries",
    "indian potash": "indian potash",
    "mohan meakin": "mohan meakin",
    "av thomas": "av thomas",
    "a v thomas": "av thomas",
    "a v thomas and company": "av thomas",
    "adtech systems": "adtech systems",
    "polymatech electronics": "polymatech",
    "polymatech": "polymatech",
    "reliance retail": "reliance retail",
    "haldiram": "haldiram",
    "haldirams": "haldiram",
    "zepto": "zepto",
    "onix renewable": "onix renewable",
    "goodluck defence": "goodluck defence",
    "goodluck defence aerospace": "goodluck defence",
}


def _basic_normalize(name):
    if not name:
        return ""
    s = name.lower()
    noise_patterns = [
        r"\bunlisted\s+shares?\b",
        r"\bunlisted\s+share\b",
        r"\bpre[-\s]?ipo\b",
        r"\blimited\b",
        r"\bltd\.?\b",
        r"\bprivate\b",
        r"\bpvt\.?\b",
        r"\bcompany\b",
        r"\bcorporation\b",
        r"\bcorp\.?\b",
        r"\bshares?\b",
        r"\(.*?\)",
        r"[^\w\s&]",
    ]
    for p in noise_patterns:
        s = re.sub(p, " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def normalize_name(name):
    if not name:
        return ""
    basic = _basic_normalize(name)
    if basic in ALIASES:
        return ALIASES[basic]
    for key, canonical in ALIASES.items():
        if len(key) >= 6 and key in basic:
            return canonical
    return basic
