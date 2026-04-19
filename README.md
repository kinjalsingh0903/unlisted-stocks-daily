# Unlisted Stocks Daily

A daily-automated pipeline that scrapes Indian unlisted / pre-IPO stock platforms,
ranks the top 10 by consensus, populates an Excel template, and emails it to
your inbox. Built to run on GitHub Actions at 7 AM IST every day, free forever.

---

## How it works

Every morning at 1:30 AM UTC (7:00 AM IST), GitHub Actions runs `main.py`. The
script:

1. Scrapes each of 34 source websites for unlisted stock listings
2. Ranks the top 10 by consensus (how many sources list each stock)
3. Populates the pre-designed Excel template
4. Sends the file as an email attachment to your Gmail
5. Uploads a copy as a GitHub artifact as backup

---

## One real thing to know before you deploy

Most Indian unlisted-share websites use Cloudflare anti-bot protection, which
blocks requests from data-center IPs (including GitHub Actions runners). A
plain Python scraper from GitHub Actions will get **403 Forbidden** from most
sites.

**Two ways around this:**

- **Recommended**: Sign up for ScraperAPI ([scraperapi.com](https://www.scraperapi.com/)).
  Free tier is 1,000 requests/month (you'll use ~100/month with 4 active scrapers).
  Paid tier is $29/mo for 100k requests. Add the API key as a GitHub secret and
  the script automatically routes through their residential IPs. No code changes needed.

- **Without ScraperAPI**: the pipeline still runs and delivers a file, but many
  sources will 403 and the Excel will have sparse data. OK for testing the plumbing.

---

## Setup — do these once

### Step 1: Create the GitHub repository

You already did this. Repo name: `unlisted-stocks-daily`, private.

### Step 2: Copy files into the repo

Clone the repo locally, then copy the contents of this folder into it, commit,
and push. The repo should look like:

```
unlisted-stocks-daily/
├── .github/workflows/daily.yml
├── template/unlisted_stocks_top10_template.xlsx
├── src/
│   ├── config.py
│   ├── populate.py
│   ├── deliver.py
│   ├── rank.py
│   └── scrapers/
│       ├── base.py
│       ├── unlistedzone.py
│       ├── incredmoney.py
│       ├── unlistedarena.py
│       └── stockify.py
├── main.py
├── requirements.txt
├── .gitignore
├── .env.example
└── README.md
```

### Step 3: Add GitHub Secrets

Go to your repo on GitHub → **Settings** → **Secrets and variables** → **Actions**
→ **New repository secret**. Add these four:

| Secret name            | Value                                         | Required |
|------------------------|-----------------------------------------------|----------|
| `GMAIL_SENDER`         | Your Gmail address (e.g. `you@gmail.com`)     | Yes |
| `GMAIL_APP_PASSWORD`   | The 16-character app password you generated   | Yes |
| `RECIPIENT_EMAIL`      | Where to deliver (same as sender is fine)     | Optional, defaults to sender |
| `SCRAPERAPI_KEY`       | Your ScraperAPI key                           | Optional, but highly recommended |

If you haven't generated the Gmail App Password yet, do so at
[myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).
You need 2-Step Verification on first.

### Step 4: Test manually once

Go to your repo on GitHub → **Actions** tab → **Daily unlisted stocks run** →
**Run workflow** (top right) → **Run workflow**.

This triggers the pipeline immediately. Watch the logs. You should see:

- A list of each source attempted, with ✓ or ✗
- The top 10 picks printed
- "Wrote: unlisted_top10_YYYY-MM-DD.xlsx"
- "Emailed to recipient."

Check your Gmail inbox for the attachment.

### Step 5: You're done

The cron in `.github/workflows/daily.yml` is already set to run at 1:30 AM UTC
= 7:00 AM IST every day. You don't need to do anything else. GitHub Actions is
free for public repos and gives 2,000 minutes/month for private repos — way
more than this script will ever use.

---

## Adding more scrapers

Only 4 of the 34 sources have live scrapers on day 1 (UnlistedZone, InCred
Money, Unlisted Arena, Stockify). The other 30 are listed in `src/config.py`
with `"scraper": None` — they're stubbed out.

To add a new one:

1. Create `src/scrapers/<sourcename>.py`, write a `scrape(url)` function that
   returns `[{"name": str, "price": float|None, "url": str|None}, ...]`
2. Register it in `src/scrapers/__init__.py` under `SCRAPER_REGISTRY`
3. In `src/config.py`, change that source's `"scraper": None` to the id you
   just registered
4. Commit and push. Next day's run will pick it up automatically.

---

## Troubleshooting

**All sources returning 403 Forbidden**
→ Sign up for ScraperAPI and add `SCRAPERAPI_KEY` as a GitHub Secret.

**Email not arriving**
→ Check GitHub Actions logs for "Emailed to recipient" confirmation.
  If it says "Missing GMAIL_SENDER", your secrets aren't set.
  If it says SMTP auth failed, the App Password is wrong — regenerate it.

**Cron didn't fire**
→ GitHub Actions disables cron on repos with no activity for 60 days. If that
  happens, any commit re-enables it. Or just use workflow_dispatch to trigger
  manually.

**Excel has lots of blank cells**
→ Expected. Unlisted marketplaces don't publish every field for every stock.
  Fields like 52W High/Low, ROE, P/B often aren't available on scrapeable
  pages. This is honest blanks vs. made-up numbers.

---

## Cost summary

| Item                | Cost              |
|---------------------|-------------------|
| GitHub repo         | Free (private)    |
| GitHub Actions      | Free (~5 min/day, well under 2000 min/mo limit) |
| Gmail SMTP          | Free              |
| ScraperAPI (optional) | Free tier 1k req/mo, or $29/mo for 100k |
| **Total**           | **₹0 to ₹2,400/mo** |

---

## The 34 sources

See the "Sources" sheet in the template for the full list, URLs, and what each
one provides.
