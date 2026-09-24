#!/usr/bin/env bash
# Create the four Gumroad DRAFT listings for Mr T's DIY Toolbox.
# Products are created as drafts (never published) — review & publish manually.
set -e
export PATH="$HOME/.local/bin:$PATH"
cd "$(dirname "$0")/.."

SITE="https://www.mrtscomputers.com"
UPDATES="Your purchase includes the current release plus updates for 90 days from purchase. Later updates are offered as low-cost upgrade packs &mdash; never a subscription."
FINEPRINT="Software is provided &quot;as is&quot; with no guarantee of results. You are the data controller: comply with CAN-SPAM/CASL/GDPR and platform rules. Disputes go to binding arbitration; sole remedy is a refund of the purchase price. See TERMS-OF-USE in the download."
REFUND="14-day refund if the software does not do what this page says. Results are not guaranteed &mdash; the tool working as described is."
RECEIPT="Thanks for supporting open-source tools! Unzip, open the product folder, and double-click START-HERE (.bat on Windows, .sh on Mac/Linux). Guides and legal are readable inside the app window. Updates included for 90 days. Questions: reply to this email."
CROSSSELL="<p><em>Want it done for you? Custom builds and setup: <a href=\"$SITE\">MrTsComputers.com</a></em></p>"

TAGS=(open-source no-subscription self-hosted windows mac linux)

DESC_1="<p><strong>Find local business leads on your own machine. No subscriptions. No API keys. No monthly fee to run it.</strong></p>
<p>A single Python tool that pulls local businesses and their published contact emails into a clean CSV &mdash; politely, legally, from open map data. Apollo charges \$90/month for this. Yours is a one-time payment.</p>
<ul>
<li>Zero dependencies &mdash; if your computer runs Python, you're done installing</li>
<li>Legal, open data &mdash; built on OpenStreetMap, not ToS-violating Google scraping</li>
<li>Emails included &mdash; visits each business's own published site, robots.txt respected</li>
<li>Polite by design &mdash; 1 request/second, rate-limited, won't get you blocked</li>
<li>Windows / macOS / Linux &mdash; double-click START-HERE, no terminal required</li>
<li>100% private &mdash; runs on YOUR machine. No account. No telemetry. Ever.</li>
<li>Open source (MIT) &mdash; read every line, modify anything, it's yours</li>
</ul>
<p><strong>The honest fine print:</strong> you are the data controller. Comply with CAN-SPAM/CASL/GDPR before contacting anyone. Plain-English SCRAPING-101 guide included.</p>
$CROSSSELL"

DESC_2="<p><strong>A complete AI cold-email system that runs on YOUR computer. Your leads and prompts never touch anyone's cloud.</strong></p>
<p>7 battle-tested prompt modes plus a zero-dependency runner that drafts emails with local AI (Ollama) &mdash; or a free no-signup cloud endpoint if you prefer. Drafts only: you review and send from your own inbox, so you stay compliant and out of spam folders.</p>
<ul>
<li>7 modes &mdash; audit, first touch, 2 follow-ups, re-engage, referral ask, reply triage</li>
<li>Local-first &mdash; Ollama = free + private; or flip one switch for free keyless cloud</li>
<li>Works with zero AI &mdash; every prompt has a no-AI template fallback</li>
<li>Compliance built in &mdash; mandatory opt-out line, identity block, hard-stop on &quot;unsubscribe&quot;</li>
<li>Feeds from the Lead Scraper &mdash; point it at leads.csv row 3, get a draft</li>
<li>Windows / macOS / Linux &mdash; double-click START-HERE</li>
<li>Open source (MIT) &mdash; the prompts are yours to rewrite</li>
</ul>
<p><strong>Honest fine print:</strong> this tool drafts. It never sends. One sequence, then stop. You are the sender under the law.</p>
$CROSSSELL"

DESC_3="<p><strong>Form &rarr; Sheet &rarr; Discord &rarr; Welcome email. Imported and live in 10 minutes. The webhook plumbing is done.</strong></p>
<p>A ready-made n8n workflow JSON for one-page-site builders: every lead lands in your own Google Sheet, pings your Discord, and gets an instant &quot;we got it&quot; email &mdash; then shows the client a confirmation. No wiring, no guessing, no \$29/month form SaaS.</p>
<ul>
<li>Import one file, done &mdash; no node-by-node assembly</li>
<li>Own your leads &mdash; plain Google Sheet, not a SaaS database</li>
<li>Instant Discord ping &mdash; call back before the tab closes</li>
<li>Auto welcome email &mdash; looks organized even when you're under a truck</li>
<li>Consent checkbox built in &mdash; honest data handling from lead #1</li>
<li>Drop-in HTML snippet &mdash; embed the form in any one-pager in 1 line</li>
<li>Free stack &mdash; self-hosted n8n + free Google/Discord/Gmail accounts</li>
<li>Open source (MIT) &mdash; every node editable</li>
</ul>
<p><strong>Licensing note:</strong> blueprint is MIT &mdash; yours to use on unlimited client projects. Runs on free self-hosted n8n (don't resell n8n itself).</p>
$CROSSSELL"

DESC_4="<p><strong>The complete local-marketing stack: find leads, reach them like a human, capture them when they reply.</strong></p>
<p>All three tools in one download &mdash; bought separately \$44.97, you save 33%:</p>
<ul>
<li><strong>Local Lead Scraper</strong> (\$14.99 value) &mdash; local business leads + emails, legally, from open map data</li>
<li><strong>AI Outreach Pack</strong> (\$9.99 value) &mdash; 7 AI prompt modes that draft emails on your machine</li>
<li><strong>n8n Intake Blueprint</strong> (\$19.99 value) &mdash; form &rarr; Sheet &rarr; Discord &rarr; email, imported in 10 minutes</li>
</ul>
<p>Each tool has its own one-click START button, its own guides, and the full legal pack. No subscriptions, no telemetry, no accounts &mdash; everything runs on your machine.</p>
<p><strong>Honest fine print:</strong> no guarantee of results; you are the operator and data controller; see TERMS-OF-USE for the plain-English agreement.</p>
$CROSSSELL"

echo "Creating draft 1/4: Local Lead Scraper"
gumroad products create \
  --name "Local Lead Scraper - find local business leads from your own machine" \
  --price 14.99 --currency usd --type digital \
  --file "dist-packages/01-lead-scraper-v1.0.zip" \
  --file-name "01-lead-scraper-v1.0.zip" \
  --file-description "The Lead Scraper package - unzip and double-click START-HERE" \
  --custom-summary "Open-source, zero-subscription lead generation. OpenStreetMap-powered, robots-respecting, CSV out." \
  --description "$DESC_1" \
  --custom-receipt "$RECEIPT" \
  --refund-period 14 --refund-fine-print "$REFUND" \
  --tag "${TAGS[0]}" --tag "${TAGS[1]}" --tag "${TAGS[2]}" \
  --tag "${TAGS[3]}" --tag "${TAGS[4]}" --tag "${TAGS[5]}" \
  --custom-permalink "local-lead-scraper" \
  --yes --quiet

echo "Creating draft 2/4: AI Outreach Pack"
gumroad products create \
  --name "AI Outreach Pack - cold emails drafted by AI on YOUR computer" \
  --price 9.99 --currency usd --type digital \
  --file "dist-packages/02-ai-outreach-pack-v1.0.zip" \
  --file-name "02-ai-outreach-pack-v1.0.zip" \
  --file-description "The AI Outreach package - unzip and double-click START-HERE" \
  --custom-summary "7 prompt modes + local-AI runner. Free no-signup mode, or fully private Ollama. Drafts only - you stay compliant." \
  --description "$DESC_2" \
  --custom-receipt "$RECEIPT" \
  --refund-period 14 --refund-fine-print "$REFUND" \
  --tag "${TAGS[0]}" --tag "${TAGS[1]}" --tag "${TAGS[2]}" \
  --tag "${TAGS[3]}" --tag "${TAGS[4]}" --tag "${TAGS[5]}" \
  --tag ai-outreach --tag ollama \
  --custom-permalink "ai-outreach-pack" \
  --yes --quiet

echo "Creating draft 3/4: n8n Intake Blueprint"
gumroad products create \
  --name "n8n One-Page Intake Blueprint - form, Sheet, Discord, welcome email" \
  --price 19.99 --currency usd --type digital \
  --file "dist-packages/03-n8n-intake-blueprint-v1.0.zip" \
  --file-name "03-n8n-intake-blueprint-v1.0.zip" \
  --file-description "The Intake Blueprint package - unzip and double-click START-HERE" \
  --custom-summary "Import one JSON, get the whole intake pipeline. Built for one-page-site sellers. 10-minute setup, free stack." \
  --description "$DESC_3" \
  --custom-receipt "$RECEIPT" \
  --refund-period 14 --refund-fine-print "$REFUND" \
  --tag "${TAGS[0]}" --tag "${TAGS[1]}" --tag "${TAGS[2]}" \
  --tag "${TAGS[3]}" --tag "${TAGS[4]}" --tag "${TAGS[5]}" \
  --tag n8n --tag automation \
  --custom-permalink "n8n-intake-blueprint" \
  --yes --quiet

echo "Creating draft 4/4: Complete DIY Toolbox"
gumroad products create \
  --name "Complete DIY Toolbox - scraper + AI outreach + intake blueprint" \
  --price 29.99 --currency usd --type digital \
  --file "dist-packages/complete-toolbox-v1.0.zip" \
  --file-name "complete-toolbox-v1.0.zip" \
  --file-description "The Complete Toolbox - all three products, unzip and double-click START-HERE in any folder" \
  --custom-summary "All three tools, one download. Bought separately \$44.97 - you save 33%. The full \$0/month local-marketing stack." \
  --description "$DESC_4" \
  --custom-receipt "$RECEIPT" \
  --refund-period 14 --refund-fine-print "$REFUND" \
  --tag "${TAGS[0]}" --tag "${TAGS[1]}" --tag "${TAGS[2]}" \
  --tag "${TAGS[3]}" --tag "${TAGS[4]}" --tag "${TAGS[5]}" \
  --tag bundle \
  --custom-permalink "complete-diy-toolbox" \
  --yes --quiet

echo
echo "All four drafts created. Review at https://gumroad.com/products"
echo "Publish manually when you're ready: gumroad products publish <id>"
