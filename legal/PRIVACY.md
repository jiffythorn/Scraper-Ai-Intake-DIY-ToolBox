# PRIVACY POLICY

**Version 1.0 — September 2026 — MrTsComputers.com**

Short version: **the Tools are self-hosted and collect nothing from you.**
This policy covers (1) the Tools and (2) our website.

## 1. The Software Collects Nothing

The Tools in this repository run locally on your machine or your own server:

- **No telemetry.** No analytics, no crash reporting, no phone-home, no
  license checks, no usage tracking. There is no code path that transmits
  anything to us.
- **Your data stays with you.** Leads, scraped records, CSVs, AI prompts,
  model outputs, workflow credentials, and logs exist only on your machine.
  Deleting them from your machine deletes them, full stop.
- **Your connections are yours.** When you connect the workflow blueprints to
  Google Sheets, Discord, Telegram, email providers, or LLM APIs, you
  authenticate directly with those services with your own accounts and API
  keys. We never see those credentials.

**You become the data controller.** Anything the Tools collect about other
people (e.g., business contact info) is collected by *you*, on *your*
infrastructure, under *your* responsibility. See `legal/DISCLAIMER.md`
section 4 for your legal duties (CAN-SPAM, CASL, GDPR, etc.).

## 2. Third-Party Services: Your Data Leaves Your Machine Only When YOU Choose

The Tools can hand data to third-party services when you configure them to:

- **Local AI (Ollama):** nothing leaves your machine. Private by default.
- **Free community AI endpoints (e.g., Pollinations.ai):** prompt text is
  sent to a shared community service under ITS privacy policy. **Never send
  personal data of real people there** — it is shared infrastructure for
  drafts and testing, not for personal information.
- **Paid AI APIs (OpenAI, Groq, OpenRouter, Anthropic, DeepSeek, Mistral,
  ...):** the provider receives your prompts and lead data under its own
  terms; retention, training use, and logging are governed by THEM, not us.
- **n8n blueprints:** when activated, form submissions flow through n8n and
  on to whichever services YOU connect (Sheets, Discord, Telegram, email
  senders). Every hop is a service with its own terms, servers, and
  policies.

In every case: **you choose the service, you authenticate with your own
accounts, and the data handshake is between you and that provider.** We are
not a party to it, we never see it, and we are **not liable for any
third-party service** — its availability, security, data handling, policy
changes, or conduct. Read each provider's terms before sending personal
information anywhere, and prefer local mode for anything involving real
people's data.

**Security duties that are yours:** keep your machine patched; keep keys
out of shared files (use `api_key: env:VARNAME`); never commit secrets or
lead data to any repository; treat anything leaving your machine as leaving
your control; delete exported data when you're done with it.

## 3. What We Never Receive

We do not receive, and cannot see: your scraped data, your lead lists, the
emails you send, your API keys, your prompts, your model outputs, or your
system information. If you later hire us for custom work, we only access
what you explicitly share with us for that engagement, under a separate
written agreement.

## 4. Our Website (MrTsComputers.com)

When you visit our website or purchase a download:

- **Order data:** name, email, and purchase record from our payment processor
  (e.g., Gumroad), used to deliver files and provide support.
- **Email:** if you join our list, we store your email until you unsubscribe
  (every email includes a working opt-out).
- **Server logs:** standard, short-lived technical logs for security.

We do not sell personal data. Payment details are handled by the payment
processor and never reach us.

## 5. Open-Source Contributions

Public repository activity (issues, pull requests, commits) is public by
design and governed by the hosting platform (e.g., GitHub) — not by us.

## 6. Your Rights

For data we actually hold (order records, mailing list): you may request a
copy, correction, or deletion at any time — email us via
<https://www.mrtscomputers.com>. Data on your own machine is yours to manage.

## 7. Changes

Updates will be posted in this file with a new version date.

**Want a privacy-compliant, professionally configured build instead of DIY?
That's what we do: <https://www.mrtscomputers.com>**
