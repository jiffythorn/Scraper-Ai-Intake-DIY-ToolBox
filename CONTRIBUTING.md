# Contributing

Thanks for helping make the DIY Toolbox better. Two kinds of contributions
land here — and one of them is the secret sauce of the whole business.

## 1. Client Custom Work Feeds the Commons

When a client hires [Mr T's Computers](https://www.mrtscomputers.com) to
customize one of these tools, the engagement agreement asks (never forces)
one thing: **let us publish the reusable, generic parts back to this
repository.**

How it works in practice:

- The client owns their deliverable outright — their config, their niche
  data, their copy, their secrets.
- What comes back here is the **generalized mechanism** with client-specific
  details stripped out. Example: we build a scraper variant tuned for a
  roofer's 40-mile radius → the reusable part is "configurable multi-region
  dedupe," contributed here; the roofer's actual targeting stays theirs.
- Clients get public credit (optional) and every future user gets a better
  free tool. Clients are told this up front, before signing. Improvements
  published here reach past clients through normal future releases —
  there is no perpetual free-updates promise attached to custom work.

**Why clients say yes:** improvements here are improvements to the tool they
run — they can pick them up in future releases or maintenance plans.

## 2. Community Contributions

Good first contributions:

- **Prompt improvements** — better output quality, better compliance guardrails
- **New vertical presets** — `presets/` entries for trades we don't cover yet
- **Bug fixes** — especially around polite rate-limiting and error handling
- **Docs** — if you had to figure something out, the next person shouldn't have to
- **Workflow blueprints** — new n8n JSONs that follow the patterns in
  `03-n8n-intake-blueprint/`

Ground rules:

1. **MIT-in, MIT-out.** Your contribution is licensed MIT like everything else.
2. **Politeness is not optional.** Anything that scrapes must keep
   rate-limits, robots.txt respect, and caching. PRs that remove the brakes
   get closed.
3. **No secrets, ever.** No API keys, no client data, no real leads in
   examples. Sample data must be obviously fake.
4. **Self-hosted stays self-hosted.** No contributions that phone home,
   require accounts with us, or add telemetry.
5. **Compliance-friendly by default.** Outreach features must include opt-out
   and identification handling.

## 3. Reporting Problems

- Bugs & feature ideas → open an issue in the repo
- Security issues → please don't file a public issue; contact us via
  <https://www.mrtscomputers.com>
- "I want this but customized for me" → that's a service:
  <https://www.mrtscomputers.com>
