"""
Peer lookup for unlisted stocks.

There's no single public source that publishes "peers" for unlisted names.
We use a hand-curated map from sector → typical listed peers + a benchmark P/E.
Used as a fallback when per-stock peer data isn't available.
"""

# Maps keyword-in-sector → (peers_name, rough_benchmark_pe)
# Benchmark P/Es are rough market averages, updated periodically.
SECTOR_PEER_MAP = [
    # (keyword,               peers_name_string,                       peer_pe)
    ("stock exchange",         "BSE Ltd, MCX India",                    45.0),
    ("broking",                "Angel One, ICICI Securities, Motilal",  22.0),
    ("nbfc",                   "Bajaj Finance, Cholamandalam, Shriram", 28.0),
    ("lending",                "Bajaj Finance, Cholamandalam",          28.0),
    ("wealth",                 "Nuvama Wealth, 360 ONE",                35.0),
    ("asset management",       "HDFC AMC, Nippon Life India",           30.0),
    ("wealth management",      "Nuvama Wealth, 360 ONE",                35.0),
    ("insurance",              "HDFC Life, SBI Life, ICICI Pru Life",   70.0),
    ("renewable",              "Adani Green, ReNew Power, Suzlon",      45.0),
    ("power",                  "NTPC, Tata Power, Power Grid",          20.0),
    ("semiconductor",          "Tata Elxsi, Sona BLW",                  60.0),
    ("defence",                "Bharat Dynamics, HAL, Mazagon Dock",    50.0),
    ("retail",                 "DMart, Trent, Reliance Retail",         90.0),
    ("fmcg",                   "HUL, Nestle, Britannia",                55.0),
    ("hospitality",            "Indian Hotels, Chalet Hotels",          60.0),
    ("airport",                "GMR Airports",                          80.0),
    ("hotel",                  "Indian Hotels, EIH, Chalet",            60.0),
    ("refining",               "Reliance Industries, IOC, BPCL",        15.0),
    ("oil",                    "Reliance, IOC, BPCL, HPCL",             15.0),
    ("gas",                    "GAIL, Gujarat Gas, IGL",                18.0),
    ("quick commerce",         "Zomato (Blinkit), Swiggy (Instamart)",  0.0),
    ("ecommerce",              "Zomato, Nykaa",                         0.0),
    ("sports",                 "No direct listed peer",                 0.0),
    ("it services",            "Infosys, TCS, Wipro, HCL",              25.0),
    ("technology",             "Infosys, TCS, LTIMindtree",             25.0),
    ("commodity",              "MCX India, BSE",                        40.0),
    ("pharma",                 "Sun Pharma, Cipla, Dr Reddy's",         30.0),
    ("chemical",               "Pidilite, SRF, Deepak Nitrite",         35.0),
    ("snack",                  "Nestle, Britannia, Bikaji",             55.0),
    ("beverage",               "Varun Beverages, United Breweries",     50.0),
    ("custodian",              "CDSL, NSDL (private)",                  55.0),
]


def peer_lookup(sector_text):
    """Given a sector string, return (peers_name, peer_pe) or (None, None)."""
    if not sector_text:
        return (None, None)
    s = sector_text.lower()
    for keyword, peers, pe in SECTOR_PEER_MAP:
        if keyword in s:
            return (peers, pe if pe > 0 else None)
    return (None, None)
