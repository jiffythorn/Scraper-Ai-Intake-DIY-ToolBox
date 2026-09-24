# 02 · AI Outreach Pack

A complete local-AI outreach system: **7 structured prompts** + a
zero-dependency runner that drafts emails using an AI model **on your own
machine** (Ollama). Your leads, prompts, and drafts never touch anyone's
cloud.

**This tool drafts only — it never sends email.** You review, paste into
your own mail client, and send as yourself, one human-checked email at a
time. That's a feature: it keeps you on the right side of spam law *and*
spam filters.

## Run It (2 minutes)

```bash
cp config.example.yml config.yml     # edit: who you are (required — it's the law)
python3 outreach_runner.py --lead sample-lead.yml              # draft via Ollama
python3 outreach_runner.py --lead sample-lead.yml --no-ai      # no model needed
python3 outreach_runner.py --list                              # see all 7 modes
```

## Local AI or Cloud AI — Your Choice

**Local (default, recommended):** install [Ollama](https://ollama.com), then
`ollama pull llama3.1:8b && ollama serve`. Free, fully private —
leads and prompts never leave your machine.

**Cloud (any OpenAI-compatible API, or Anthropic):** one config switch —

```yaml
provider: openai_compatible          # or: anthropic
base_url: https://api.groq.com/openai/v1   # OpenAI, Groq, OpenRouter, Gemini, DeepSeek, Mistral...
model: llama-3.3-70b-versatile
api_key: env:OPENAI_API_KEY          # keep the secret out of the file
```

Works with OpenAI, Groq (free tier), OpenRouter, Google Gemini's
OpenAI-compatible endpoint, DeepSeek, Mistral, Together, LM Studio, vLLM —
anything that speaks the standard `/chat/completions` shape. No SDKs.

**The honest tradeoff:** cloud mode sends your lead data and prompts to
*that provider* under *their* privacy policy. Local mode sends them	nowhere.
That's the whole decision — see [`../legal/DISCLAIMER.md`](../legal/DISCLAIMER.md).
```

## The 7 Modes

| Mode | What it writes |
|---|---|
| `website_audit` | 3 specific findings on a prospect's site + the best opening line |
| `first_touch` | cold email #1 — one observation, one question, zero hype |
| `followup_1` | short bump that *adds* something (never "just bumping this") |
| `followup_2` | the polite goodbye that ends the sequence |
| `reengage` | warm re-contact months later (real conversations only) |
| `referral_request` | ask happy clients for warm intros (your best channel) |
| `reply_handling` | triages any reply — including hard-stops for OPT_OUT and autoresponders |

Each prompt lives in `prompts/` as editable markdown with three sections:
the **system prompt**, the **user template** (with `{{placeholders}}`),
and a **TEMPLATE FALLBACK** so the pack works with no AI at all.

## Works With the Lead Scraper

`01-lead-scraper` output feeds this directly:

```bash
python3 outreach_runner.py --leads-csv ../01-lead-scraper/leads.csv --row 1 --save
```

## Built-In Guardrails

- **Opt-out line is mandatory** — appended/enforced in every mode's output
- **Sender identity required** from config (CAN-SPAM/CASL/GDPR basics)
- **Hard stop logic** — `reply_handling` outputs "do not email" text for
  opt-outs and autoresponders, and the sequence ends after `followup_2`
- **Drafts only** — no SMTP, no bulk send, no scheduler. That part is a
  *service*: [MrTsComputers.com](https://www.mrtscomputers.com)
- **Cloud mode is opt-in** — your key, your account, your provider's terms

## Compliance In 5 Lines (full version: [`../legal/DISCLAIMER.md`](../legal/DISCLAIMER.md))

1. Identify yourself truthfully in every email.
2. Honor opt-outs immediately and forever.
3. One sequence (3 emails), then stop.
4. Business-relevant, specific, low volume — not scraped-list blasts.
5. You are the sender; the law looks at you, not at a prompt file.

---

**Want this connected to your real inbox and lead flow, tuned to your
voice?** That's a flat-fee build — **[MrTsComputers.com](https://www.mrtscomputers.com)**
