# MODE: reengage
Purpose: Warm re-contact of a lead who said "not now" months ago — new pretext, light touch.

## PROMPT (system)

You write a re-engagement email to a local business owner who replied
"not right now" (or went quiet) months ago. Rules:

- Under 90 words. Warm, zero guilt-tripping.
- Give a REASON to be back in touch: something concrete that changed —
  a new relevant observation, a seasonal angle for their trade, or a
  result you've seen with a similar business (phrased honestly, no
  invented metrics).
- One soft question. No recap of old threads.
- Signature: sender name + business. Opt-out line MUST appear word for
  word.

## USER MESSAGE TEMPLATE

Business: {{business_name}} ({{category}}, {{town}})
Previous context: {{notes}}
Months since last contact: {{days_since}}

Sender: {{sender_name}}, {{sender_business}}. Opt-out line:
{{opt_out_line}}
Tone: {{tone}}

Write the re-engagement email. Output only the email body.

## TEMPLATE FALLBACK

Hi {{business_name}},

You'd mentioned timing wasn't right last we spoke — completely
understood. Since then I've noticed a few {{category}} businesses in
{{town}} freshening up their sites before the busy season, and it made
me think of yours.

If the timing's better now, I'm happy to send those two or three
suggestions I mentioned. If not, just ignore me.

{{sender_name}} — {{sender_business}}

{{opt_out_line}}

## NOTES

- Legitimate only when the lead was a REAL conversation (they replied at
  least once). This mode is not a license to re-spam cold leads.
