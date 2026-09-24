# Mr T's DIY Toolbox

**Free, open-source tools for DIYers — from [MrTsComputers.com](https://www.mrtscomputers.com)**

Run everything on **your own machine**. No subscriptions, no telemetry, no
accounts, no data leaving your computer. If you'd rather have it installed,
customized, or maintained for you — [we do that too](SERVICES.md).

```
legal/                  LICENSE · DISCLAIMER · TERMS · PRIVACY · SCRAPING-101
                        THIRD-PARTY-NOTICES (license & bundling rules)
01-lead-scraper/        Local lead scraper — stdlib-only Python, polite by default
02-ai-outreach-pack/    AI outreach — 7 prompts + Ollama / free keyless / cloud runner
03-n8n-intake-blueprint/ One-page site intake → Sheets → Discord → email (n8n JSON)
GETTING-STARTED.md      Windows / macOS / Linux / ChromeOS install walkthrough
WALKTHROUGH.md          Zero-to-first-success, hand-holding, assumes nothing
SERVICES.md             "Or hire us" — custom build & setup services
CONTRIBUTING.md         How custom client work feeds back into this repo
```

## The Golden Rule of this Toolbox

> **Your machine. Your data. Your responsibility.**

Everything here is self-hosted by design. We can't see your leads, your
emails, your keys, or your logs — and we never want to. That also means the
legal and compliance side (anti-spam laws, scraping rules, privacy rules) is
**your** call. Read [`legal/DISCLAIMER.md`](legal/DISCLAIMER.md) before using
any tool commercially. The tools are deliberately polite and rate-limited;
don't remove the brakes.

## Quickstart (60 seconds each)

**1 — Lead scraper** (needs only Python 3.9+, nothing to install):

```bash
cd 01-lead-scraper
cp config.example.yml config.yml     # edit: town, business type, radius
python3 lead_scraper.py              # → leads.csv in this folder
```

**2 — AI outreach pack** (needs [Ollama](https://ollama.com) for local mode):

```bash
cd 02-ai-outreach-pack
cp config.example.yml config.yml     # edit: your business, model, tone
python3 outreach_runner.py --lead sample-lead.yml          # dry run, prints only
python3 outreach_runner.py --lead sample-lead.yml --send  # actually save drafts
```

**3 — n8n intake blueprint** (needs [n8n](https://n8n.io) — free, self-hosted):

```bash
cd 03-n8n-intake-blueprint
# Import one-page-site-intake.json into n8n → open SETUP.md → ~10 minutes
```

New here? Start with **[GETTING-STARTED.md](GETTING-STARTED.md)** —
Windows, macOS, Linux, even Chromebook. Double-click launchers included.

## Selling or bundling this?

You can — it's MIT. Read
**[legal/THIRD-PARTY-NOTICES.md](legal/THIRD-PARTY-NOTICES.md)** first:
bundling rules, n8n's Sustainable Use License (don't resell n8n itself),
OSM ODbL share-alike for redistributed datasets, and model-license duties.

## Scraping? Read this first

**[legal/SCRAPING-101.md](legal/SCRAPING-101.md)** — blocks, ISP
complaints, cease-and-desist letters, and why you carry 100% of the
responsibility. One page, plain English, no legalese.

## Support & Custom Work

Community support: open an issue in this repo (best effort, no guarantees).

Want it done **for** you — installed, customized to your market, configured
to be compliance-safe, and maintained? That's our day job:

### 👉 [MrTsComputers.com — custom builds & setup](https://www.mrtscomputers.com)

## License & Legal

- Code: [MIT](legal/LICENSE) — free to use, modify, even resell, with attribution
- **Read first:** [Disclaimer](legal/DISCLAIMER.md) · [Terms of Use](legal/TERMS-OF-USE.md) · [Privacy](legal/PRIVACY.md)

*You are the operator. You are the data controller. Use fairly, contact
honestly, and don't be a spammer.*
