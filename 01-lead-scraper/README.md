# 01 · Local Lead Scraper

Find local businesses and their published contact emails — running **100% on
your machine**. Zero dependencies: if you have Python 3.9+, you're done
installing.

**Data source: OpenStreetMap** — a legal, open-licensed, community-run map
database. This tool deliberately does **not** scrape Google Maps (that
violates Google's ToS and gets accounts banned).

```
leads.csv →  name | category | address | phone | email | website | osm_id ...
```

## Run It (60 seconds)

```bash
cp config.example.yml config.yml    # then edit town + category
python3 lead_scraper.py
```

That's it. No `pip install`. No API keys. No accounts.

Handy flags:

```bash
python3 lead_scraper.py --town "Knoxville, TN" --category plumber
python3 lead_scraper.py --limit 25          # first 25 leads only
python3 lead_scraper.py --no-crawl          # skip website visits (faster)
```

## How It Works

1. **Locate** your town via OpenStreetMap's Nominatim (1 request).
2. **Query** the Overpass API for businesses in your category within your
   radius (1 request).
3. **Optionally visit each business's published website** — the one they list
   publicly on their OSM profile — to find a publicly published contact
   email (a few pages per site).

## Politeness Is Built In (and load-bearing)

- **robots.txt respected** on every website visit — the crawler skips
  anything disallowed
- **1 request/second** to websites, tiny page caps (`max_pages_per_site: 5`)
- **1–2 total requests** to OpenStreetMap's free community servers per run,
  with a polite `User-Agent` identifying you via the `contact:` config value
- **Stay-on-site crawling** — it never follows links away from the
  business's own website

Don't remove these brakes. They're what keep the free services (and you)
welcome. Blocked or rate-limited access = your own fault.

## What This Tool Is Not

- Not a Gmail-extractor, directory-dumper, or paid-database bypass. It reads
  **public, openly licensed data and published public pages only.**
- Not a spam machine. What you do with the CSV is governed by **your** laws:
  CAN-SPAM (US), CASL (Canada), GDPR/ePrivacy (EU/UK). You are the data
  controller. See [`../legal/DISCLAIMER.md`](../legal/DISCLAIMER.md).

## Files

| File | Purpose |
|---|---|
| `lead_scraper.py` | the whole tool — single file, stdlib only |
| `config.example.yml` | copy to `config.yml` and edit |
| `sample-leads.csv` | what output looks like (fake data) |

## Tweak It

- **New category?** Add one line to `CATEGORIES` in `lead_scraper.py`
  (find the tag at <https://wiki.openstreetmap.org/wiki/Map_Features>), or
  use `osm_tag: key=value` in config.
- **Different area shape?** `radius_meters` is all yours.
- Built something generally useful? PRs welcome — see
  [`../CONTRIBUTING.md`](../CONTRIBUTING.md).

---

**DIY not your thing?** We install, tune, and maintain this for your exact
market — **[MrTsComputers.com](https://www.mrtscomputers.com)**

💚 *Saved you time? [Tips keep this free](https://www.mrtscomputers.com) —
tip button floats on the left of the site.*
