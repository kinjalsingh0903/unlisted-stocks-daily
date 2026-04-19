"""
Central config for unlisted-stocks-daily.
34 sources. 4 have implemented scrapers for day 1 (scraper field set).
Add scrapers incrementally as each site is verified.
"""
import os

SOURCES = [
    # ==== Original 14 ====
    {"id": "unlistedzone",        "name": "UnlistedZone",           "url": "https://unlistedzone.com/unlisted-shares-price-list-india",      "category": "Marketplace",    "scraper": "unlistedzone"},
    {"id": "incredmoney",         "name": "InCred Money",           "url": "https://www.incredmoney.com/unlisted-shares",                    "category": "Wealth",         "scraper": "incredmoney"},
    {"id": "unlistedarena",       "name": "Unlisted Arena",         "url": "https://www.unlistedarena.com/unlisted-shares-list/",            "category": "Broker",         "scraper": "unlistedarena"},
    {"id": "stockify",            "name": "Stockify",               "url": "https://stockify.net.in/unlisted-shares-price-list-india/",      "category": "Marketplace",    "scraper": "stockify"},
    {"id": "planify",             "name": "Planify",                "url": "https://planify.in/",                                            "category": "Marketplace",    "scraper": None},
    {"id": "altius",              "name": "Altius Investech",       "url": "https://altiusinvestech.com/companymain",                        "category": "Marketplace",    "scraper": "altius"},
    {"id": "sharescart",          "name": "SharesCart",             "url": "https://www.sharescart.com/unlisted-shares/",                    "category": "Marketplace",    "scraper": "sharescart"},
    {"id": "unlistedsharebrokers","name": "Unlisted Share Brokers", "url": "https://www.unlistedsharebrokers.com/",                          "category": "Broker",         "scraper": None},
    {"id": "precize",             "name": "Precize",                "url": "https://www.precize.in/",                                        "category": "Marketplace",    "scraper": None},
    {"id": "wwipl",               "name": "WWIPL",                  "url": "https://wwipl.com/unlisted-companies-india",                     "category": "Marketplace",    "scraper": "wwipl"},
    {"id": "ritscapital",         "name": "Rits Capital",           "url": "https://www.ritscapital.com/",                                   "category": "Advisory",       "scraper": None},
    {"id": "delistedstocks",      "name": "Delisted Stocks",        "url": "https://www.delistedstocks.in/",                                 "category": "Marketplace",    "scraper": "delistedstocks"},
    {"id": "sebi",                "name": "SEBI Filings",           "url": "https://www.sebi.gov.in/filings/public-issues.html",             "category": "Regulator",      "scraper": None},
    {"id": "mca",                 "name": "MCA Portal",             "url": "https://www.mca.gov.in/",                                        "category": "Regulator",      "scraper": None},
    # ==== New 20 ====
    {"id": "tradeunlisted",       "name": "TradeUnlisted",          "url": "https://tradeunlisted.com/",                                     "category": "Broker",         "scraper": None},
    {"id": "dharawat",            "name": "Dharawat Securities",    "url": "https://buysellunlistedshares.com/",                             "category": "Broker",         "scraper": None},
    {"id": "unlistedkart",        "name": "UnlistedKart",           "url": "https://unlistedkart.com/",                                      "category": "Marketplace",    "scraper": None},
    {"id": "qapita",              "name": "Qapita",                 "url": "https://www.qapita.com/",                                        "category": "Cap table",      "scraper": None},
    {"id": "parasram",            "name": "Parasram Trade",         "url": "https://parasramtrade.com/",                                     "category": "Broker",         "scraper": None},
    {"id": "chittorgarh",         "name": "Chittorgarh",            "url": "https://www.chittorgarh.com/",                                   "category": "IPO tracker",    "scraper": None},
    {"id": "ipocentral",          "name": "IPO Central",            "url": "https://www.ipocentral.in/",                                     "category": "IPO tracker",    "scraper": None},
    {"id": "ipowatch",            "name": "IPO Watch",              "url": "https://www.ipowatch.in/",                                       "category": "IPO tracker",    "scraper": None},
    {"id": "moneycontrol",        "name": "Moneycontrol",           "url": "https://www.moneycontrol.com/",                                  "category": "News",           "scraper": None},
    {"id": "et_markets",          "name": "Economic Times Markets", "url": "https://economictimes.indiatimes.com/markets",                   "category": "News",           "scraper": None},
    {"id": "livemint",            "name": "LiveMint Markets",       "url": "https://www.livemint.com/market",                                "category": "News",           "scraper": None},
    {"id": "business_standard",   "name": "Business Standard",      "url": "https://www.business-standard.com/markets",                      "category": "News",           "scraper": None},
    {"id": "financial_express",   "name": "Financial Express",      "url": "https://www.financialexpress.com/market/",                       "category": "News",           "scraper": None},
    {"id": "ndtv_profit",         "name": "NDTV Profit",            "url": "https://www.ndtvprofit.com/markets",                             "category": "News",           "scraper": None},
    {"id": "trendlyne",           "name": "Trendlyne",              "url": "https://trendlyne.com/",                                         "category": "Screener",       "scraper": None},
    {"id": "tickertape",          "name": "Tickertape",             "url": "https://www.tickertape.in/",                                     "category": "Screener",       "scraper": None},
    {"id": "screener_in",         "name": "Screener.in",            "url": "https://www.screener.in/",                                       "category": "Screener",       "scraper": None},
    {"id": "tijori",              "name": "Tijori Finance",         "url": "https://www.tijorifinance.com/",                                 "category": "Research",       "scraper": None},
    {"id": "stockedge",           "name": "StockEdge",              "url": "https://web.stockedge.com/",                                     "category": "Research",       "scraper": None},
    {"id": "equitymaster",        "name": "Equity Master",          "url": "https://www.equitymaster.com/",                                  "category": "Research",       "scraper": None},
]

TOP_N = 15

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
REQUEST_TIMEOUT = 30
REQUEST_DELAY_SECONDS = 1.5

# ===== ScraperAPI toggle — solves the 403 problem =====
# Most Indian unlisted-share sites block data-center IPs (incl. GitHub Actions).
# Set SCRAPERAPI_KEY as a GitHub Secret to route requests through their residential IPs.
# Free tier: 1000 requests/month. Paid: $29/mo for 100k. Sign up at https://www.scraperapi.com/
SCRAPERAPI_KEY = os.environ.get("SCRAPERAPI_KEY", "").strip()
USE_SCRAPERAPI = bool(SCRAPERAPI_KEY)

# Email (Gmail SMTP with App Password)
GMAIL_SENDER = os.environ.get("GMAIL_SENDER", "").strip()
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "").strip() or GMAIL_SENDER
EMAIL_SUBJECT = "Top 10 Unlisted Stocks — {date}"
EMAIL_BODY = """Good morning,

Attached is today's Top 10 Unlisted Stocks watchlist for {date_long}.

Ranking: consensus across enabled sources ({n_ok} of {n_total} active today).
Ties broken by 1Y return, then Revenue Growth YoY.

— Daily pipeline
"""

TEMPLATE_PATH = "template/unlisted_stocks_top10_template.xlsx"
