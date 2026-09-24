# WALKTHROUGH — Zero to First Success, Holding Your Hand the Whole Way

**This guide assumes nothing.** Not that you know what a terminal is. Not
that you've ever run a script. Take it slow, one step at a time, and check
off each ✅. Every step tells you what you should SEE, so you always know
whether you're on track.

*Time to your first win: about 30 minutes.*

**Mini-glossary (as you read):**
- **Terminal / Command Prompt / PowerShell** — a window where you type
  commands instead of clicking. Windows: Start button → type `powershell`.
  Mac: ⌘-Space → type `terminal`. Linux: Ctrl-Alt-T usually.
- **Directory / folder** — same thing.
- **CSV** — a plain spreadsheet file. Opens in Excel, Numbers, Sheets, or
  LibreOffice.

---

## Part 0 — Set Up Your Workspace (5 minutes)

1. **Unzip** the download (right-click → Extract All / double-click).
   Put it somewhere easy: `C:\Tools\mrts-toolbox` (Windows) or your home
   folder (Mac/Linux). ✅ *You see a folder containing `01-lead-scraper`,
   `02-ai-outreach-pack`, `03-n8n-intake-blueprint`, and several `.md` files.*
2. **Check Python** (needed for products 01 and 02):
   - Windows: double-click `01-lead-scraper\run_windows.bat`. If a window
     opens the Python download page, install Python from it and **tick
     "Add python.exe to PATH"** during install, then run the .bat again.
   - Mac/Linux: open Terminal, type `python3 --version`, press Enter.
     ✅ *You see something like `Python 3.12.1`.* If instead you get an
     error, install Python from https://www.python.org/downloads/ and
     reopen Terminal.
3. ✅ Done. That was the hardest part, and it's over.

> Stuck? Every product's README has a Troubleshooting/Files section. And
> if you'd rather we just did it — https://www.mrtscomputers.com

---

## Part 1 — Your First Lead List (10 minutes)

Work inside the `01-lead-scraper` folder.

1. **Create your config**
   - Windows: double-click `run_windows.bat` — first run creates
     `config.yml` and opens it in Notepad automatically.
   - Mac/Linux: in Terminal: `cd` into the folder (type `cd ` then drag
     the folder into the Terminal window, press Enter), then run
     `./run_mac_linux.sh` — it creates `config.yml` and opens an editor.
2. **Edit three lines** in `config.yml`:
   - `town:` → your target area, be specific (`Asheville, NC`)
   - `category:` → one from the list in the file (`roofer`, `plumber`, …)
   - `contact:` → **your real email** (it identifies your polite traffic
     to the free map service — this keeps you welcome)
   Save and close.
3. **Run it**
   - Windows: double-click `run_windows.bat` again.
   - Mac/Linux: `./run_mac_linux.sh` again.
4. **What you should SEE** (takes 1–5 minutes, website-checking takes
   longest):
   ```
   [*] Locating 'Asheville, NC' via OpenStreetMap ...
   [+] Found: Asheville, ... (35.5951, -82.5515)
   [*] Querying Overpass API for craft=roofer within 10000 m ...
   [+] Overpass returned 14 places
   [+] 12 named places after cleanup
   [*] Visiting 7 published websites (max 5 pages each, 1 req/sec) ...
       [1/7] Example Roofing: info@exampleroofing.com
       ...
   [OK] Wrote 12 leads (5 with email) to leads.csv
   ```
5. ✅ **Open `leads.csv`** (double-click it). You have real local
   businesses with phones, websites, and some emails. **That's your first
   win.**

**Tune it:** bigger `radius_meters` = more leads. Different `category` =
different market. `--no-crawl` flag = skip website emails, faster runs.

**Rules of the road (2-minute read, protects you):**
`../legal/SCRAPING-101.md`. You are the operator — blocks, ISP
complaints, or C&D letters are your responsibility, not ours. The polite
defaults are load-bearing; don't remove them.

---

## Part 2 — Turn a Lead Into a Draft Email (10 minutes)

Work inside `02-ai-outreach-pack`.

1. **Create your config** the same way as Part 1 (`run_windows.bat` /
   `run_mac_linux.sh`). Fill in **YOUR** name, business, phone, email —
   this is legally required on real outreach, and it's what makes the
   emails yours.
2. **Draft without any AI first** (sanity check the plumbing):
   - Windows: edit `run_windows.bat` line `python outreach_runner.py ...`
     to add `--no-ai` — or in Terminal:
     `python outreach_runner.py --lead sample-lead.yml --no-ai`
   - ✅ *You see a complete sample email printed, with your name at the
     bottom.* Plumbing works.
3. **Now with AI — pick ONE:**
   - **Easiest (free, no signup):** in `config.yml` set `provider: free`.
     The tool fetches the provider's live model list every run and
     auto-picks a working model, so renames/retirements never break you.
   - **Most private (also free):** install Ollama from
     https://ollama.com, then in Terminal: `ollama pull llama3.1:8b`.
     Set `provider: ollama`. Everything stays on your machine.
4. **Run it:** `python outreach_runner.py --lead sample-lead.yml`
   - ✅ *You see `[*] Model '...' confirmed available` (or an
     auto-selection notice), then a personalized email for the sample
     business.*
5. **Use a REAL lead from Part 1:**
   `python outreach_runner.py --leads-csv ../01-lead-scraper/leads.csv --row 1`
   ✅ *A draft written around that actual business.*
6. **Save it:** add `--save`. The draft lands in `drafts/first_touch/`.
7. ✅ **Read it. Fix anything wrong. Paste it into YOUR email client and
   send it yourself.** The tool never sends — that's your compliance
   seatbelt.

**The law in 5 lines** (full version: `../legal/DISCLAIMER.md` §4):
identify yourself, honor opt-outs immediately, one sequence of 3 emails
max, business-relevant and specific, and you are the sender under
CAN-SPAM/CASL/GDPR.

---

## Part 3 — The Intake Machine (10–15 minutes, one-time)

Goal: a form on a website that fills a Google Sheet, pings your Discord,
and auto-emails the customer. Full detail with troubleshooting:
`03-n8n-intake-blueprint/SETUP.md`. Condensed:

1. **Install n8n** (free): in Terminal: `npx --yes n8n` (first run
   downloads ~100 MB — a few quiet minutes is normal; needs Node.js from
   nodejs.com) — or Docker: `docker run -it --rm -p 5678:5678 -v
   n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n`.
   ✅ *Browser at http://localhost:5678 shows n8n.*
2. **Import:** Workflows → Create → ⋯ → Import from File → pick
   `03-n8n-intake-blueprint/one-page-site-intake.json`.
   ✅ *You see 5 connected boxes: Form → Sheets → Discord → Gmail → Reply.*
3. **Google Sheet:** create one, add the 8 headers listed in SETUP.md,
   paste the Sheet ID into the Sheets node, sign in when n8n asks.
4. **Discord (optional):** Server Settings → Integrations → Webhooks →
   copy URL into the Discord node's credential.
5. **Gmail:** click node → create credential → sign in. Edit the message
   to sound like you.
6. **Test:** Execute workflow → open the form URL from the Form node →
   submit. ✅ *Row appears in the Sheet, Discord pings, email arrives.*
7. **Activate** (toggle top-right). Done — it runs 24/7 on your machine.

---

## When Something Goes Wrong

| You see | Do this |
|---|---|
| `Python not found` | Reinstall Python, tick "Add to PATH" (Windows) |
| `Could not find 'X' on OpenStreetMap` | Make the town more specific: `Town, STATE` |
| Zero leads | Bigger `radius_meters`, different `category` |
| Outreach: `Could not reach Ollama` | Run `ollama serve` in another Terminal, or set `provider: free` |
| Outreach: `free is struggling right now` | Free endpoints get busy — re-run in a few minutes, or switch provider. The tool already retried alternate live models for you |
| n8n node red error | Click the node — it names the missing credential/ID |
| Anything else | Product README → open an issue in the repo → or https://www.mrtscomputers.com |

## Where Everything Lives

```
GETTING-STARTED.md         OS-by-OS install (Windows/Mac/Linux/ChromeOS)
WALKTHROUGH.md             this file
legal/DISCLAIMER.md        read once — your responsibilities, our limits
legal/SCRAPING-101.md      read before scraping — blocks, ISPs, C&Ds
legal/TERMS-OF-USE.md      the agreement — arbitration, refund-only remedy
legal/PRIVACY.md           what we collect (nothing) and what you collect
legal/THIRD-PARTY-NOTICES.md  license/bundling rules if you resell
SALES-COPY.md              ready-made product pages (if you resell)
```

**The deal, in three sentences:** the software is MIT and yours; you are
the operator and the data controller, full stop; the most we could ever
owe anyone is a refund of the purchase price, and disputes go to binding
arbitration — never a courtroom. Read `legal/TERMS-OF-USE.md` once; it's
written in plain English on purpose.

*Questions, setup help, or "just do it for me":*
**https://www.mrtscomputers.com**
