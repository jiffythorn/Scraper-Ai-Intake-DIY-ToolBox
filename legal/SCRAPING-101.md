# SCRAPING-101 — Read Before Your First Run

**The one-paragraph version:** you are the operator. Every request the
scraper makes goes out over your connection, from your IP, under your
identity. Blocks, ISP complaints, cease-and-desist letters, and legal claims
land on **you** — not on us, not on the tool. The tool is deliberately
polite (OpenStreetMap open data + published public pages + robots.txt + 1
req/sec), and that's the whole protection you get. We are **not liable** for
any consequence of your scraping. If that trade doesn't sit right, don't
run it — or [hire us to build a compliance-safe pipeline](https://www.mrtscomputers.com)
instead.

---

## How the Internet Actually Feels About Scrapers

Most of the web does not distinguish between "research" and "attack." This
is the reality check nobody puts in the README:

- **Blocks are automatic.** Datacenter IPs and aggressive patterns get
  blacklisted by services like Cloudflare, Akamai, DataDome, and their
  friends, often before a human ever looks. One bad day of scraping can get
  your office IP challenged with a CAPTCHA wall for weeks. Some businesses
  go further: proxy vendors keep lists of "abuser" IPs that get blocked
  everywhere, automatically, long after you've stopped.
- **Your home IP is precious.** Burn it and it follows you. Blocked home
  IP = your whole household loses access to sites that use those lists.
  That's why we ship the scraper with brakes: 1 req/sec, robots.txt
  respected, few pages, open-data-first. Don't touch the brakes.
- **ISPs and hosts forward complaints.** When a site operator complains to
  your ISP or hosting provider, they forward it. Expect a stern email,
  possible temporary suspension, and — if you ignore it — termination of
  your service. ISPs have abuse desks; they use them.
- **Cease-and-desist letters are real.** A C&D is a legal letter from a
  site's lawyers. It usually demands you stop, delete the data, and
  confirm in writing. In some places ignoring one converts a gray-area
  practice into a willful violation claim. If you get one: **stop, consult
  a lawyer, comply.**
- **Legal claims are possible.** US plaintiffs have argued CFAA
  (unauthorized access), breach of contract (ToS), trespass to chattels,
  and misappropriation. Post-*hiQ v. LinkedIn*, scraping generally-public
  data is safer than it was — but ToS claims, C&D compliance, state laws,
  EU database rights, and good old-fashioned lawsuits didn't vanish. Some
  jurisdictions restrict scraping even of public data. That risk is yours.
- **Some sites just hate scrapers on principle** and will spend real money
  to identify and pursue them. A polite crawler that respects robots.txt
  still gets some people furious. If you're not ready to be disliked, don't
  scrape.

## Why OpenStreetMap Is the Entire Strategy

The scraper queries OpenStreetMap — **open data, explicitly licensed for
reuse** (ODbL), community-run, and *designed* to be queried by tools like
this. It's the legal, ToS-compliant backbone of the whole product. The
website-email step visits **only websites the businesses themselves
published** in their OSM profile, politely, robots-aware. That's about as
clean as lead generation gets. Stay on that path and 90% of the risk
 evaporates. The remaining 10% is yours.

## Your Responsibilities (Checklist)

Before your first run:

- [ ] I read this file and [`DISCLAIMER.md`](DISCLAIMER.md) section 3.
- [ ] I set a real `contact:` in `config.yml` so operators can reach me
      instead of blocking me.
- [ ] I kept `max_pages_per_site` small and `1 req/sec` untouched.
- [ ] I'm using **open data sources only** (OpenStreetMap) — no logged-in
      scraping, no paywall/technical-block bypass, no directory-dumping of
      sites that forbid it.
- [ ] I know what I'll do with the data, and it's lawful where I operate.
- [ ] I'm ready to stop immediately if any source objects.

While running / after:

- [ ] Keep records: what you scraped, when, from where. Records are your
      defense if anyone ever asks.
- [ ] Stop + honor opt-outs the same day for outreach. (See the outreach
      pack's compliance notes.)
- [ ] Never resell raw scraped data as "a database" (see
      [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY attribution note) for OSM
      attribution duty if you distribute derived data).

## If Something Goes Wrong

- **Blocked?** Stop. Wait it out (hours to weeks). Don't rotate proxies to
  evade — that converts "polite over-enthusiasm" into "deliberate
  circumvention."
- **ISP/host complaint?** Respond promptly, in writing, politely. Stop the
  activity first.
- **Cease-and-desist?** Stop. Preserve records. **Lawyer. Now.**
- **Legal claim?** **Lawyer. Now.** Nothing in these docs is legal advice;
  we're not liable, and neither is the tool.

## The Free Alternative (Yes, Really)

If a free, legal, no-risk source of business names is all you need, the
scraper's OpenStreetMap-only mode (`--no-crawl`) already gives you that.
No blocks, no ISP risk, no C&D risk — just open data and a CSV.

---

**Prefer someone else carries the risk and does it right?**
[MrTsComputers.com](https://www.mrtscomputers.com)
