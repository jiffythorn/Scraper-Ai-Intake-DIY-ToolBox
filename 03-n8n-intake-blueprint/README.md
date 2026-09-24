# 03 · One-Page Site Intake Blueprint (n8n)

A plug-and-play **n8n workflow JSON** that turns a form on your one-page
site into a full intake pipeline:

```
Form submit → Google Sheet (free) → Discord ping (instant) → Welcome email → Confirmation page
```

Save 3 hours of webhook wiring. Runs on **your** n8n (free community
edition) with **your** free Google/Discord/Gmail accounts. No paid tools,
no vendor lock-in — the JSON is yours to edit.

## Install (10 minutes)

```bash
# 1) get n8n (free, self-hosted):
npx --yes n8n              # first run downloads ~100MB, be patient
                           # or the Docker one-liner in SETUP.md

# 2) import the blueprint:
#    n8n → Create Workflow → ⋯ → Import from File → one-page-site-intake.json

# 3) follow SETUP.md — paste your Sheet ID + Discord webhook, sign in once.
```

Full walkthrough with screenshots-level detail: **[SETUP.md](SETUP.md)**

## What's In the Box

| File | Purpose |
|---|---|
| `one-page-site-intake.json` | the n8n workflow (import as-is) |
| `SETUP.md` | 10-minute setup, troubleshooting, privacy checklist |
| `html-form.html` | drop-in snippet to embed the form in any one-pager |

## Licensing Note (30 seconds)

The blueprint JSON is ours, MIT-licensed — sell it, bundle it, ship it.
**n8n itself** uses the Sustainable Use License: run it for your own
business and build workflows for clients, but don't rebrand or resell n8n
as a service. Full details:
[`../legal/THIRD-PARTY-NOTICES.md`](../legal/THIRD-PARTY-NOTICES.md)

## Why This Flow Works

- **Sheet first** — every lead lands in a spreadsheet you own. No SaaS
  holding your leads hostage.
- **Discord ping** — you hear the phone *before* the lead closes the tab.
- **Instant welcome email** — the lead knows a human got it (and you look
  organized even when you're under the truck).
- **Consent checkbox built in** — personal-information handling starts
  honest. You're the data controller: see
  [`../legal/DISCLAIMER.md`](../legal/DISCLAIMER.md).

## Make It Yours

Everything is plain n8n — add nodes, change fields, wire SMS, whatever.
Some ideas: budget field → auto-flag big jobs; photo upload → save to
Google Drive; new-lead digest at 8am. If you build a generally useful
variant, [contribute it back](../CONTRIBUTING.md).

---

**Don't want to touch n8n at all?** We install, brand, and monitor this
exact pipeline — **[MrTsComputers.com](https://www.mrtscomputers.com)**

💚 *Saved you time? [Tips keep this free](https://www.mrtscomputers.com) —
tip button floats on the left of the site.*
