# THIRD-PARTY NOTICES & BUNDLING RULES

What this toolbox uses, under what license, and what you may legally do —
including **selling it, bundling it, or shipping it inside paid products.**

**Last reviewed: September 2026.** Licenses change; verify before you ship.

## The Short Version for Sellers

You may **sell, bundle, repackage, and resell** everything in this toolbox —
the tools themselves are **MIT-licensed, our own original work, with no
third-party code vendored in**. Your obligations are light:

1. Keep the MIT license + copyright notice intact (it's already in
   `LICENSE`).
2. Keep attribution where we put it (READMEs, file headers, "source" column
   in the scraper's CSV).
3. Don't market the tools as your own original work.
4. If you **distribute derived OSM data** (not just the tool), OSM's ODbL
   share-alike applies — see below.

That's it. Now the details.

---

## Inventory: Everything These Tools Touch

### Our own code (MIT)

`01-lead-scraper/lead_scraper.py`, `02-ai-outreach-pack/outreach_runner.py`,
the prompt files, the n8n blueprint JSON, the HTML snippet, and all docs are
**original work by Mr T's Computers, MIT-licensed**. There is no copied-in
third-party code anywhere in this repository — the Python tools are written
against the **Python standard library only** (Python Software Foundation
License, which permits any use including commercial, no notices required
beyond what Python itself ships with).

### Python (PSF License)

Any Python ≥ 3.9 works. The PSF license allows commercial bundling, resale,
and embedding without extra obligations. You may ship Python itself in a
bundle if you want (e.g., an embedded distribution) — the embedded
distribution's permissive terms are documented on python.org.

### OpenStreetMap data (ODbL 1.0) — the one to actually read

The scraper **queries** OSM's Overpass/Nominatim APIs — that's plain use,
no obligations beyond politeness. But the **data** OSM returns is licensed
**Open Database License (ODbL) 1.0**:

- **Using** the data internally (reading leads.csv, calling leads, market
  research): free, no share-alike, no attribution duty in practice.
- **Distributing a "derived database"** (e.g., you resell a cleaned
  leads-database file, or republish the dataset): ODbL share-alike kicks
  in — the derived database must also be ODbL-licensed, with attribution
  "© OpenStreetMap contributors". Individual business *names and contact
  details* in a normal marketing workflow are generally treated as ordinary
  facts; whole datasets are not. When in doubt, attribute: it costs
  nothing — our CSV's `source` column already carries the notice.
- **Attribution when publishing:** "© OpenStreetMap contributors" — already
  embedded in every row the scraper writes.

We are not liable for OSM's availability, data quality, or conduct. OSM is
a community service — be polite (the tool is), or lose access.

### n8n (Sustainable Use License) — read before you RESSELL n8n itself

The blueprint JSON (`one-page-site-intake.json`) is **our MIT work** — you
may sell it, bundle it, or include it in any product.

**n8n itself** is NOT open source in the MIT sense: n8n's community edition
uses the **Sustainable Use License**. In plain English:

- **You may:** run n8n for your own business, for your employer, or to
  deliver *services* to clients (building workflows FOR a client who runs
  their own n8n is fine), self-host it, and modify it for internal use.
- **You may NOT:** repackage, rebrand, or resell n8n itself as your own
  product, or offer a *hosted n8n-as-a-service* to outsiders. Selling
  *setup services* and *workflow blueprints* is explicitly the permitted
  "services" path — selling *the software* is not.
- The safe framing for your customers: **"You run your own free n8n; we
  sell you the blueprint + setup."** That's exactly what this toolbox does.

Full terms: <https://docs.n8n.io/license/>. We are not liable for n8n, its
changes, or its conduct.

### Ollama (MIT) and AI models (varies)

- **Ollama** is MIT-licensed: use, bundle, resell freely. It's a local
  server — user runs it on their machine; nothing to do with us.
- **Models pulled through Ollama** carry their own licenses (Meta Llama
  community license, Gemma terms, Apache-2.0, etc.). Most allow commercial
  use with notice requirements; a few have restrictions (e.g., Llama's
  naming rules). **The user pulls the model** — our tool never ships one.
  If YOU bundle a model with your product, YOU take on that model's
  license compliance. Check before you ship.

### Free community AI endpoint (Pollinations.ai)

Used only as the keyless, opt-in `provider: free`. It's a free community
service: no license to redistribute, no SLA, can rate-limit or vanish, and
**never send real people's personal data through it**. We are not liable
for it. Don't build a business that depends on any single free endpoint.

### Google Sheets / Gmail / Discord (n8n blueprint connections)

Commercial services under their own terms (Google APIs ToS, Discord ToS).
Users connect their own free accounts. Nothing is redistributed here — no
licensing issue for bundling the blueprint. Respect their rate limits and
usage policies (Gmail ~500 sends/day free tier).

---

## Bundling Recipes (What You Can Legally Ship)

| You want to... | Allowed? | What you must keep |
|---|---|---|
| Sell this toolbox as-is for $9.99–$19.99 | **Yes** (MIT) | LICENSE + attribution |
| Bundle it inside a larger paid course/product | **Yes** (MIT) | LICENSE + attribution |
| Rebrand the tools as your own | **No** — MIT requires original attribution; "your own work" claims violate it |
| Sell setup/configuration services around them | **Yes** — services are always yours to sell |
| Sell the n8n blueprint | **Yes** — it's our MIT work |
| Resell n8n itself / host it for clients as a service | **No** — Sustainable Use License |
| Ship Ollama binary inside your bundle | **Yes** (MIT) | its license file |
| Ship an AI model inside your bundle | **Depends** — check the model's own license first |
| Resell a cleaned OSM-derived leads *database* | **Share-alike** — ODbL applies to the dataset; attribute "© OpenStreetMap contributors" |
| Use leads internally for marketing calls/emails | **Yes** — ordinary use, no share-alike |

## Attribution Strings (Copy-Paste)

For the toolbox itself (keep in your product page or About file):

> Contains Mr T's DIY Toolbox (MIT) — https://www.mrtscomputers.com

For any published OSM-derived data:

> Data © OpenStreetMap contributors, available under the Open Database
> License (ODbL) — https://www.openstreetmap.org/copyright

---

*This file is practical guidance, not legal advice — we are not lawyers and
not liable for your use of any third-party service or artifact. For a
commercially significant redistribution, get a real IP attorney to review.*
