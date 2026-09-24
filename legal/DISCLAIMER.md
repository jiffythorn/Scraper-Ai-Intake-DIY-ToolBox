# DISCLAIMER — READ BEFORE USE

**Version 1.0 — September 2026**

## 1. No Legal Advice

Mr T's Computers ("we", "us") is not a law firm and nothing in these tools,
their documentation, or this repository is legal advice. You are solely
responsible for determining whether your use of these tools complies with the
laws, regulations, and terms of service that apply **to you and in your
jurisdiction**. Consult a qualified attorney before using these tools for
commercial outreach or data collection.

## 2. You Are The Operator

These tools are designed to run **on your own machine or your own server**
(self-hosted). We never receive, store, see, or process:

- the data you scrape,
- the leads or emails you generate,
- the AI models you run or the prompts you send,
- the workflow connections (Sheets, Discord, Telegram, email) you configure.

Because everything runs on infrastructure **you control**, **you** are the
data collector and the data controller. We have no ability to monitor,
restrict, or undo what the software does on your machine.

## 3. Web Scraping Risks

The lead-scraper tool queries public data sources (e.g., OpenStreetMap
Overpass API) and may fetch publicly published pages. You must:

- respect each source's Terms of Service and `robots.txt`,
- respect rate limits (the tool's defaults are deliberately polite — do not
  remove them),
- never scrape data from sources where you are logged in or bypassing a
  paywall or technical block,
- verify that how you use any collected data (storage, resale, emailing) is
  lawful where you operate.

Some jurisdictions restrict scraping even of public data. That risk is yours,
not ours.

## 4. Email & Outreach Risks

The outreach pack and workflow blueprints can send messages to real people.
You must comply with all applicable anti-spam and privacy laws, including
without limitation CAN-SPAM (US), CASL (Canada), and the GDPR/ePrivacy rules
(EU/UK): identification, a working unsubscribe/opt-out, truthful subject
lines, lawful basis for contacting the person, and honoring removal requests.
Unsolicited bulk email can result in fines, blacklisting, and legal claims
against **you**.

## 5. AI Output

Prompts and AI models (cloud or local, e.g., Ollama) produce generated text
that may be inaccurate, unoriginal, or inappropriate. You must review every
message before it is sent. We are not responsible for anything an AI model
writes on your behalf.

## 6. Third-Party Online Services: Your Accounts, Your Risk, Not Our Liability

The Tools can connect to services **we do not operate and do not control**:
free community AI endpoints (e.g., Pollinations.ai), Ollama models you
install, OpenAI/Groq/OpenRouter/Anthropic and other paid AI APIs, OpenStreetMap's
Overpass and Nominatim, Google Sheets, Discord, Telegram, webhooks, email
senders, and n8n itself. When you direct the Tools to any third-party service:

- **You choose the service, you make the account, you supply any key.** We
  have no relationship with these providers and receive nothing from them.
- **Data you send there is governed by THEIR terms and privacy policies,
  not ours.** If you send lead data or personal information to a cloud AI
  endpoint, that provider receives and may process, log, or retain it under
  its own rules. Read their policy before sending anyone's personal data —
  especially other people's.
- **They can change or disappear at any time.** Free endpoints rate-limit,
  go down, change models, or shut off without notice. Paid APIs change
  prices and terms. Nothing we ship depends on any one of them staying the
  same.
- **Security is yours.** You are running software on your own machine:
  keep it patched, never put API keys in files you share or commit, prefer
  `api_key: env:VARNAME`, never send special-category/sensitive personal
  data (health, financial, minors, etc.) to any third-party endpoint, and
  treat anything leaving your machine as leaving your control.
- **Free endpoints are shared community infrastructure.** Do not send
  personal data of real people to them. Use them for drafts, testing, and
  non-personal content; use a local model for anything involving personal
  information.
- **We are NOT LIABLE for any third-party service** — its availability,
  its security, its handling of your data, its terms changes, its
  bandwidth, its conduct, or anything else about it. You use third-party
  services entirely at your own risk, and any dispute is between you and
  that provider. To the maximum extent permitted by law we disclaim all
  liability for third-party services, even if we listed or linked them,
  even if the Tools name them, and even if you followed our documentation
  in choosing them.

## 7. Warranty & Liability

> **Scraper users, start here:** scraping runs against servers you don't
> own, using your connection and your identity. Consequences — IP blocks,
> ISP complaints, cease-and-desist letters, or legal claims — land on **you**.
> Read **[`SCRAPING-101.md`](SCRAPING-101.md)** before the first run.

THE TOOLS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND (see LICENSE for
the full MIT text). To the maximum extent permitted by law, we are not liable
for any damages, fines, data loss, account bans, blacklisting, lost profits,
or legal claims arising from your use of these tools. You run them at your
own risk.

**No guarantee of results or usability.** We do not promise the Tools will
produce leads, replies, sales, rankings, or any business outcome, that they
will be uninterrupted or error-free, or that any third-party service they
use stays available, free, or unchanged. Your results depend on your
market, your compliance, and your effort.

**Exclusive remedy.** If anything goes wrong, the most we owe anyone is a
**refund of the purchase price actually paid** — no attorneys' fees, court
or filing costs, or other expenses are recoverable from us under any
circumstances, and we are never liable for indirect or consequential
damages. See `TERMS-OF-USE.md` sections 7 and 12.

**Who is protected.** All protections here extend to Mr T's Computers'
owner(s), employees, contractors, volunteers, affiliates, associates,
suppliers, and every open-source contributor — personally and collectively.
See `TERMS-OF-USE.md` sections 8–13 (covered parties, assumption of risk,
release, indemnification, no-reliance, and **binding arbitration with a
class action waiver** — disputes go to a neutral arbitrator whose decision
is final, not to court).

## 8. Fair Play

Do not use these tools to harass, deceive, spam, or target people who have
asked not to be contacted. We may refuse support or custom work to anyone
using the tools abusively.

**Questions about compliant setup or a custom, policy-safe build for your
business? That's a service we sell: <https://www.mrtscomputers.com>**
