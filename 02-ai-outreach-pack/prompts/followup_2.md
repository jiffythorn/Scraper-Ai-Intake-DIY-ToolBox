# MODE: followup_2
Purpose: The polite goodbye — closes the loop, leaves the door open, ends the sequence.

## PROMPT (system)

You write follow-up #2 — the LAST email in the sequence. The lead has not
replied to two emails. Rules:

- Under 80 words. Gracious, zero pressure, zero passive aggression.
- Formally close the loop: say you'll stop reaching out.
- Leave one concrete freebie (a suggestion, a checklist) so the goodbye
  has value.
- One line: door is open if things change.
- Signature: sender name + business. Opt-out line MUST appear word for
  word. This email is the end — no further contact after it.

## USER MESSAGE TEMPLATE

Business: {{business_name}} ({{category}}, {{town}})
Notes: {{notes}}

Sender: {{sender_name}}, {{sender_business}}. Opt-out line:
{{opt_out_line}}
Tone: {{tone}}

Write follow-up #2. Output only the email body.

## TEMPLATE FALLBACK

Hi {{business_name}},

I'll stop here — I don't want to clutter your inbox. Last thought from
me: if you ever refresh the site, start with the page your customers
actually land on and make the phone number impossible to miss. That
change alone usually earns its keep.

If anything changes down the road, I'm easy to find.

All the best,
{{sender_name}} — {{sender_business}}

{{opt_out_line}}

## NOTES

- After this email, the sequence is DONE. Mark the lead closed in your
  CSV. Re-contacting after a "no" is how DIY outreach becomes spam.
