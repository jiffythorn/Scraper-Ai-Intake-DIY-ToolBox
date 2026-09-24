# SETUP — One-Page Site Intake (n8n)

From zero to a working intake pipeline (form → Google Sheet → Discord ping →
welcome email) in about 10 minutes. Everything runs on **your** n8n with
**your** free accounts. No subscriptions.

---

## Step 0 — Get n8n running (skip if you have it)

n8n's community edition is free and self-hosted. Pick one:

**Option A — quick try (Node.js):**
```bash
npx --yes n8n
```
The first run downloads ~100 MB — expect 3–8 quiet minutes (that's
normal, not a freeze). Leave the terminal open → open
<http://localhost:5678>

> **About the npm warnings:** during install, npm prints a pile of
> `deprecated` and `ERESOLVE peer dependency` notices. They look scary and
> are **harmless** — routine noise from n8n's big dependency tree, not
> errors. (The package GUI hides them for you.) As long as n8n eventually
> says `Editor is now accessible via: http://localhost:5678`, you're fine.

**Option B — Docker (recommended for "always on"):**
```bash
docker run -it --rm --name n8n -p 5678:5678 \
  -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
```

> Self-hosting n8n on a $5 VPS so it runs 24/7 with HTTPS and backups?
> [We do that.](https://www.mrtscomputers.com)

## Step 1 — Import the blueprint (1 min)

In n8n: **Workflows → Create Workflow → ⋯ menu → Import from File** → pick
`one-page-site-intake.json`.

You'll see the pipeline: **Form → Google Sheets → Discord → Gmail → Reply**.

## Step 2 — Google Sheet (2 min)

1. Create a new Google Sheet (free Google account). Name it "Website Leads".
2. In row 1 add these headers **exactly** (the blueprint auto-maps by name):
   `Your name | Email | Business name | What do you need? | Phone (optional) | Tell us about your project | It's OK to email me a reply and occasional tips (no spam, unsubscribe anytime) | submittedAt`
3. Copy the Sheet ID from its URL:
   `https://docs.google.com/spreadsheets/d/`**`THIS_PART`**`/edit`
4. In n8n, click the **Google Sheets** node → replace `PASTE_YOUR_GOOGLE_SHEET_ID`
   and select your tab.
5. Click **Create New Credential** and sign in to Google in the popup.
   That's OAuth — your credentials live in YOUR n8n.

## Step 3 — Discord ping (2 min)

1. In your Discord server: **Server Settings → Integrations → Webhooks →
   New Webhook** → copy the URL. (No Discord? Right-click the node →
   Disable — or delete it.)
2. Click the **Discord** node → **Create New Credential** → paste the URL.

## Step 4 — Welcome email (2 min)

1. Click the **Gmail** node → **Create New Credential** → sign in.
2. Edit the message text and signature (node → "Message" field) to sound
   like you.
3. Prefer another sender? Swap in the SMTP/Resend/SendGrid node — any
   sender works. **Gmail's free limit is ~500 recipients/day**; don't try
   to make this node your cold-email cannon, that's not what it's for.

## Step 5 — Test & activate (2 min)

1. Save, then click **Execute workflow** → open the **Form URL** shown in
   the Form Trigger node (it looks like `http://localhost:5678/form/...`).
2. Submit a test entry. Watch it hit the Sheet, Discord, and your inbox.
3. **Toggle Active** (top-right). Done — it now runs 24/7 on your machine.

## Put it on your one-page site

- **Link it:** yoursite.com → button → the Form URL (works everywhere).
- **Embed it:** `<iframe src="YOUR_N8N_FORM_URL" style="width:100%;height:800px;border:0"></iframe>`
  (see `html-form.html` for a ready-made snippet).
- Using the hosted `n8n.cloud` trial on a real domain? Set up your own
  domain or reverse proxy first — the free self-hosted + reverse-proxy
  route is the zero-cost one.

## Troubleshooting

| Symptom | Fix |
|---|---|
| A screen asks to **"Add a code sandbox"** (n8n Assistant) | That's n8n's optional AI-Assistant preview — it needs a paid model key + Docker and is **not used by this blueprint**. The package GUI (START-HERE) disables it automatically. If you started n8n manually, close the dialog, or relaunch with `N8N_DISABLED_MODULES=instance-ai npx --yes n8n` |
| Sheet node errors "column not found" | Headers must match labels exactly (Step 2.2), or open the node → Columns → re-map by hand |
| Gmail sends from wrong account | Re-check which Google account you authorized |
| Form page 404 after activation | The public URL is the Form Trigger node's **Production URL**, not the test URL |
| Discord silent | Webhook URL credential wrong, or node disabled |

## Privacy & Compliance Notes (30 seconds, do this)

- Submissions contain **personal information** and flow through your n8n
  and the services YOU connected (Google, Discord, your email provider).
  You are the data controller — link a privacy policy from your form page
  and only collect what you'll use. See [`../legal/DISCLAIMER.md`](../legal/DISCLAIMER.md).
- Don't connect tools or data sources you wouldn't trust with your
  customers' details. Local n8n + local secrets + reputable processors =
  the whole secret.
- The consent checkbox on the form isn't decoration — honor it, and honor
  any unsubscribe the same day.

## Customize

- Add fields (budget, address, photo upload) in the Form Trigger node —
  add matching Sheet headers.
- Add an SMS/Telegram node after Discord for urgent leads.
- Add an n8n "Filter" node to route "Something else / not sure" to a human
  review channel.

Built a variant others would want? PR it — see
[`../CONTRIBUTING.md`](../CONTRIBUTING.md).

---

**Want the whole intake system installed, branded, and monitored for you?**
That's a flat-fee setup — **[MrTsComputers.com](https://www.mrtscomputers.com)**
