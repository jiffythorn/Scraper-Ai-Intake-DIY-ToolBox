#!/usr/bin/env python3
"""
Mr T's AI Outreach Runner — local-model outreach drafting, zero cloud.

Feeds a lead + your business context into a structured prompt and gets a
draft email back. Runs against OLLAMA on YOUR machine by default — your
prompts and leads never leave your computer. No Ollama? --no-ai falls back
to the built-in template in each prompt file, so you can start instantly.

Prefer a cloud model? Set provider: openai_compatible (OpenAI, Groq,
OpenRouter, Google Gemini, DeepSeek, Mistral, ...) or provider: anthropic
in config.yml — one API key, no SDKs, everything else identical.
Cloud mode sends YOUR lead data to THAT provider — your choice, your
account, your responsibility (see ../legal/DISCLAIMER.md).

This tool DRAFTS ONLY. It never sends email. You paste, review, and send
from your own mail client — one human-reviewed email at a time.

    python3 outreach_runner.py --list
    python3 outreach_runner.py --lead sample-lead.yml
    python3 outreach_runner.py --lead sample-lead.yml --mode website_audit
    python3 outreach_runner.py --leads-csv ../01-lead-scraper/leads.csv --row 1
    python3 outreach_runner.py --lead sample-lead.yml --save   # write draft file
    python3 outreach_runner.py --lead sample-lead.yml --no-ai  # template only

YOU are the sender. Comply with CAN-SPAM / CASL / GDPR: identify yourself,
stay truthful, honor opt-outs. See ../legal/DISCLAIMER.md.
Want it wired into your real lead flow? https://www.mrtscomputers.com
"""

import argparse
import csv
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
PROMPTS_DIR = Path(__file__).parent / "prompts"
DRAFTS_DIR = Path(__file__).parent / "drafts"

MODES = ["website_audit", "first_touch", "followup_1", "followup_2",
         "reengage", "referral_request", "reply_handling"]


def log(msg: str) -> None:
    """UTF-8-safe console logging: some Windows consoles choke on box chars."""
    try:
        print(msg, file=sys.stderr, flush=True)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"),
              file=sys.stderr, flush=True)


# --- same tiny flat config reader as the scraper (one format everywhere) ---
def load_kv(path: Path) -> dict:
    cfg = {}
    if not path.exists():
        return cfg
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        cfg[key.strip().lower()] = value.split(" #")[0].strip()
    return cfg


def split_prompt_file(text: str) -> tuple[str, str, str]:
    """Extract (system, user_template, fallback) sections from a prompt file."""
    def section(name: str) -> str:
        m = re.search(rf"^## {re.escape(name)}\s*$(.*?)(?=^## |\Z)",
                      text, re.M | re.S)
        return m.group(1).strip() if m else ""
    return (section("PROMPT (system)"), section("USER MESSAGE TEMPLATE"),
            section("TEMPLATE FALLBACK"))


def fill(template: str, values: dict) -> str:
    out = template
    for key, val in values.items():  # {{key}} style
        out = out.replace("{{" + key + "}}", str(val))
    for key, val in values.items():  # {key} style too
        out = out.replace("{" + key + "}", str(val))
    return out


def missing_placeholders(filled: str) -> list[str]:
    return sorted(set(re.findall(r"\{\{(\w+)\}\}", filled)))


def lead_from_csv(csv_path: str, row_no: int) -> dict:
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit(f"[!] No rows in {csv_path}")
    if not 1 <= row_no <= len(rows):
        raise SystemExit(f"[!] --row must be 1..{len(rows)}")
    r = rows[row_no - 1]
    return {
        "business_name": r.get("name", ""), "category": r.get("category", ""),
        "town": "", "their_website": r.get("website", ""),
        "their_phone": r.get("phone", ""), "notes": "From leads.csv row "
        f"{row_no}: {r.get('address', '')}",
    }


def ask_ollama(model: str, system: str, user_prompt: str,
               temperature: float) -> str:
    payload = json.dumps({
        "model": model, "prompt": user_prompt, "system": system,
        "stream": False, "options": {"temperature": temperature},
    }).encode()
    req = urllib.request.Request(OLLAMA_URL, data=payload, headers={
        "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read().decode("utf-8")).get("response", "")


def resolve_api_key(value: str) -> str:
    """api_key may be a literal or 'env:VARNAME' (recommended: keeps the
    secret out of the config file)."""
    if not value:
        return ""
    if value.lower().startswith("env:"):
        return os.environ.get(value[4:], "").strip()
    return value.strip()


def ask_openai_compatible(base_url: str, api_key: str, model: str,
                          system: str, user_prompt: str,
                          temperature: float) -> str:
    """Any OpenAI-style /chat/completions endpoint. Covers OpenAI, Groq,
    OpenRouter, Google Gemini's OpenAI-compatible endpoint, DeepSeek,
    Mistral, Together, Fireworks, LM Studio, vLLM, and friends."""
    url = base_url.rstrip("/") + "/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user_prompt}],
        "temperature": temperature,
    }).encode()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, data=payload, headers=headers)
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def ask_anthropic(base_url: str, api_key: str, model: str, system: str,
                  user_prompt: str, temperature: float) -> str:
    """Anthropic Messages API (Claude) — direct, no SDK."""
    url = base_url.rstrip("/") + "/messages"
    payload = json.dumps({
        "model": model, "max_tokens": 1024, "temperature": temperature,
        "system": system,
        "messages": [{"role": "user", "content": user_prompt}],
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json", "x-api-key": api_key,
        "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return "".join(block.get("text", "")
                   for block in data.get("content", []))


def fetch_json(url: str, headers: dict | None = None,
               timeout: int = 30):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_model_ids(payload) -> list[str]:
    """Model ids from OpenAI shape ({data:[{id}]}), array shapes
    ([{name}|{id}|{model}] — Pollinations) or plain ["m1", "m2"]."""
    entries: list = []
    if isinstance(payload, dict):
        entries = payload.get("data", payload.get("models", [])) or []
    elif isinstance(payload, list):
        entries = payload
    ids = []
    for e in entries:
        if isinstance(e, str):
            ids.append(e)
        elif isinstance(e, dict):
            mid = e.get("id") or e.get("name") or e.get("model")
            if mid:
                ids.append(str(mid))
    return ids


def model_available(model: str, ids: list[str]) -> bool:
    """Exact match, or ollama-style tag equivalence (foo == foo:latest)."""
    m = model.lower()
    return any(i.lower() == m or i.lower().startswith(m + ":") or
               m.startswith(i.lower() + ":") for i in ids)


def pick_fallback_model(ids: list[str], provider: str) -> str | None:
    """Prefer free/cheap/community models when auto-selecting."""
    if not ids:
        return None
    pairs = [(m, m.lower()) for m in ids]
    for hint in ("free", "community"):
        for m, l in pairs:
            if hint in l:
                return m
    if provider in ("anthropic", "claude"):
        for m, l in pairs:
            if "haiku" in l:
                return m
    for hint in ("mini", "flash", "small", "nano"):
        for m, l in pairs:
            if hint in l:
                return m
    return ids[0]


def available_models(provider: str, base: str, api_key: str) -> list[str]:
    """Fetch the provider's CURRENT model list, live. Returns [] when we
    can't tell (discovery never blocks a run)."""
    try:
        if provider == "ollama":
            data = fetch_json(base.rstrip("/") + "/api/tags")
            return [m["name"] for m in data.get("models", [])
                    if m.get("name")]
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        if provider in ("anthropic", "claude"):
            headers = {"x-api-key": api_key,
                       "anthropic-version": "2023-06-01"}
        try:
            return extract_model_ids(
                fetch_json(base.rstrip("/") + "/models", headers))
        except Exception:
            # community endpoints sometimes serve /models at the origin
            if "/openai" in base:
                origin = base.split("/openai")[0]
                return extract_model_ids(
                    fetch_json(origin + "/models", headers))
            raise
    except Exception:
        return []


def generate(provider: str, base: str, api_key: str, model: str,
             system: str, user_prompt: str, temperature: float) -> str:
    if provider == "ollama":
        return ask_ollama(model, system, user_prompt, temperature)
    if provider in ("anthropic", "claude"):
        return ask_anthropic(base, api_key, model, system, user_prompt,
                             temperature)
    return ask_openai_compatible(base, api_key, model, system, user_prompt,
                                 temperature)


def save_draft(mode: str, business: str, subject: str, body: str) -> Path:
    out_dir = DRAFTS_DIR / mode
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", business.lower()).strip("-") or "lead"
    path = out_dir / f"{slug}.txt"
    path.write_text(f"# Draft — {mode} — {business}\n"
                    f"# REVIEW BEFORE SENDING. This tool never sends email.\n\n"
                    f"{subject}\n\n{body}\n", encoding="utf-8")
    return path


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Draft outreach emails with a LOCAL AI model (Ollama). "
                    "Drafts only — never sends.")
    ap.add_argument("--lead", help="lead file (same key: value format)")
    ap.add_argument("--leads-csv", help="leads.csv from the lead scraper")
    ap.add_argument("--row", type=int, default=1,
                    help="1-based row number when using --leads-csv")
    ap.add_argument("--mode", default="first_touch", choices=MODES)
    ap.add_argument("--list", action="store_true", help="list modes & exit")
    ap.add_argument("--save", action="store_true",
                    help="write the draft to drafts/<mode>/")
    ap.add_argument("--no-ai", action="store_true",
                    help="skip the model; use the built-in template")
    ap.add_argument("--model", help="override config model (e.g. llama3.1:8b)")
    args = ap.parse_args()

    if args.list:
        log("Available modes:")
        for m in MODES:
            p = PROMPTS_DIR / f"{m}.md"
            purpose = ""
            if p.exists():
                pm = re.search(r"^Purpose:\s*(.+)$",
                               p.read_text(encoding="utf-8"), re.M)
                purpose = " — " + pm.group(1) if pm else ""
            log(f"  {m:18s}{purpose}")
        return

    cfg = load_kv(Path("config.yml"))
    if not cfg:
        log("[!] No config.yml — copy config.example.yml first "
            "(your business info + compliance lines go there).")
        sys.exit(1)

    if args.leads_csv:
        lead = lead_from_csv(args.leads_csv, args.row)
    elif args.lead:
        lead = load_kv(Path(args.lead))
    else:
        raise SystemExit("[!] Give me a lead: --lead sample-lead.yml "
                         "or --leads-csv leads.csv --row 3")

    prompt_path = PROMPTS_DIR / f"{args.mode}.md"
    system, user_tpl, fallback = split_prompt_file(
        prompt_path.read_text(encoding="utf-8"))

    sender = {
        "sender_name": cfg.get("sender_name", ""),
        "sender_business": cfg.get("sender_business", ""),
        "sender_phone": cfg.get("sender_phone", ""),
        "sender_email": cfg.get("sender_email", ""),
        "opt_out_line": cfg.get("opt_out_line",
                                "Not relevant? Reply \"no thanks\" and I "
                                "won't email again."),
        "model": args.model or cfg.get("model", "llama3.1:8b"),
        "tone": cfg.get("tone", "friendly, plain-spoken, no hype"),
    }
    values = {**{k: v for k, v in lead.items()}, **sender,
              "today": date.today().isoformat()}
    values = {k: (v if v else f"[MISSING:{k}]") for k, v in values.items()}

    user_prompt = fill(user_tpl, values)

    if args.no_ai:
        log("[*] --no-ai: using built-in template (no model needed)")
        subject = fill(f"Quick idea for {values['business_name']}", values)
        body = fill(fallback, values)
    else:
        provider = cfg.get("provider", "ollama").lower().strip()
        api_key = resolve_api_key(cfg.get("api_key", ""))
        temperature = float(cfg.get("temperature", "0.7"))

        # Resolve provider endpoint + requested model
        if provider in ("free", "pollinations"):
            base = cfg.get("base_url", "https://text.pollinations.ai/openai")
            requested = args.model or cfg.get("model", "openai")
        elif provider == "ollama":
            base = "http://localhost:11434"
            requested = args.model or cfg.get("model", "llama3.1:8b")
        elif provider in ("openai", "openai_compatible",
                          "openai-compatible"):
            base = cfg.get("base_url", "https://api.openai.com/v1")
            requested = args.model or cfg.get("model", "gpt-4o-mini")
            if not api_key:
                raise SystemExit(
                    "[!] provider: openai_compatible needs api_key: in "
                    "config.yml (literal, or api_key: env:OPENAI_API_KEY)")
        elif provider in ("anthropic", "claude"):
            base = cfg.get("base_url", "https://api.anthropic.com/v1")
            requested = args.model or cfg.get("model",
                                              "claude-3-5-haiku-latest")
            if not api_key:
                raise SystemExit(
                    "[!] provider: anthropic needs api_key: in config.yml "
                    "(literal, or api_key: env:ANTHROPIC_API_KEY)")
        else:
            raise SystemExit(
                f"[!] Unknown provider '{provider}' — use free, ollama, "
                "openai_compatible, or anthropic")

        # LIVE MODEL DISCOVERY — fetch the provider's current model list on
        # every run. Keep the user's choice if it still exists; otherwise
        # auto-pick a free/available one. Discovery failing never blocks us.
        ids = available_models(provider, base, api_key)
        chosen, fallback = requested, None
        if ids:
            if model_available(requested, ids):
                log(f"[*] Model '{requested}' confirmed available "
                    f"({len(ids)} models listed)")
            else:
                fallback = pick_fallback_model(ids, provider)
                if fallback:
                    log(f"[!] '{requested}' is not offered anymore — "
                        f"auto-selecting '{fallback}' from "
                        f"{len(ids)} live models")
                    chosen = fallback
                else:
                    log(f"[!] Could not verify '{requested}' — trying it "
                        "anyway")
        else:
            log(f"[*] Live model list unavailable — using '{requested}' "
                "as configured")

        log(f"[*] Asking {provider} model '{chosen}' (mode: {args.mode})")
        if provider in ("free", "pollinations"):
            log("    (shared community service — never send real people's "
                "personal data here)")

        def call_model(m: str) -> str:
            return generate(provider, base, api_key, m, system,
                            user_prompt, temperature)

        try:
            body = call_model(chosen)
        except urllib.error.HTTPError as e:
            # Transient provider trouble (rate limit / capacity / hiccup):
            # retry the chain: auto-picked alternative, then the user's
            # original choice (endpoints often accept working aliases that
            # aren't in their published model list).
            if e.code in (429, 500, 502, 503, 504):
                attempts = []
                alt = fallback or (pick_fallback_model(ids, provider)
                                   if ids else None)
                if alt and alt != chosen:
                    attempts.append(alt)
                if requested not in (chosen, alt):
                    attempts.append(requested)
                body = None
                for attempt in attempts:
                    log(f"[!] HTTP {e.code} from provider — retrying with "
                        f"model '{attempt}' ...")
                    try:
                        body = call_model(attempt)
                        break
                    except Exception as e2:
                        code2 = getattr(e2, "code", None)
                        if code2 not in (429, 500, 502, 503, 504):
                            log(f"[!] Retry failed "
                                f"({e2.__class__.__name__}).")
                            break
                        e = e2  # try the next candidate against same error
                if body is None:
                    log(f"[!] {provider} is struggling right now "
                        "(HTTP " + str(getattr(e, 'code', '?')) + ").")
                    log("    Free/community endpoints get overloaded — "
                        "wait a few minutes and re-run, switch provider "
                        "in config.yml (e.g. provider: ollama), or run "
                        "with --no-ai for the built-in template.")
                    sys.exit(2)
            else:
                hint = ("check your api_key and model name"
                        if e.code in (401, 403, 404)
                        else "provider may be down, rate-limiting, or the "
                             "model name may be wrong")
                log(f"[!] {provider} API returned HTTP {e.code} — {hint}")
                log("    Or run with --no-ai to use the built-in template.")
                sys.exit(2)
        except Exception as e:
            log(f"[!] Could not reach the {provider} endpoint "
                f"({e.__class__.__name__}: {e})")
            if provider == "ollama":
                log("    Fix:  1) install https://ollama.com   "
                    "2) ollama pull llama3.1:8b   3) ollama serve")
            log("    Or run with --no-ai to use the built-in template.")
            sys.exit(2)
        subject = fill(cfg.get("subject_template",
                               "Quick idea for {business_name}"), values)

    # Compliance guardrail: identification + opt-out always attached
    if "Subject:" in body:
        subject_line, _, rest = body.partition("\n")
        subject = subject_line.replace("Subject:", "").strip() or subject
        body = rest.strip()

    if missing_placeholders(body):
        log(f"[!] Unfilled placeholders in output: "
            f"{', '.join(missing_placeholders(body))} — check config.yml")

    print("\n" + "=" * 62)
    print(f"SUBJECT: {subject}")
    print("=" * 62)
    print(body)
    print("=" * 62)
    log(f"[*] Drafts only — review, paste into YOUR mail client, send as YOU. "
        f"Never bulk-send unreviewed AI output. You accept the Terms of Use")
    log(f"    (../legal/) — no guarantees of results; third-party AI providers "
        f"are your responsibility.")
    if args.save:
        path = save_draft(args.mode, values["business_name"], subject, body)
        log(f"[+] Saved: {path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n[!] Cancelled.")
        sys.exit(130)
