#!/usr/bin/env python3
"""
Mr T's DIY Lead Scraper — local, polite, zero-dependency lead generation.

Finds local businesses from OpenStreetMap (a legal, open data source — NOT
Google Maps, whose scraping violates their ToS), optionally visits published
websites to collect publicly listed contact emails, and writes a clean CSV.

Runs 100% on YOUR machine. No accounts, no API keys, no telemetry.

    python3 lead_scraper.py                # uses config.yml
    python3 lead_scraper.py --no-crawl     # OSM data only, no website visits
    python3 lead_scraper.py --limit 25

YOU are the data controller. Be polite, obey robots.txt, comply with the
privacy/anti-spam laws where you operate. See ../legal/DISCLAIMER.md.
Prefer someone else run it? https://www.mrtscomputers.com
"""

import argparse
import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.robotparser
from pathlib import Path

# --------------------------------------------------------------------------
# Politeness constants — DO NOT LOWER THESE. They keep you welcome on the
# free, community-run services this tool depends on.
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
REQUEST_DELAY = 1.0          # seconds between website fetches (1 req/sec)
REQUEST_TIMEOUT = 20         # seconds per HTTP request
USER_AGENT = ("MrTsLeadScraper/1.0 (self-hosted DIY tool; polite; "
              "set contact= in config.yml to reach the operator)")

# OSM tag presets: category name -> "key=value" OSM tag
CATEGORIES = {
    "restaurant":   "amenity=restaurant",
    "cafe":         "amenity=cafe",
    "bakery":       "shop=bakery",
    "barber":       "shop=barber",
    "hairdresser":  "shop=hairdresser",
    "dentist":      "healthcare=dentist",
    "vet":          "amenity=veterinary",
    "gym":          "leisure=fitness_centre",
    "auto_repair":  "shop=car_repair",
    "plumber":      "craft=plumber",
    "electrician":  "craft=electrician",
    "builder":      "craft=builder",
    "roofer":       "craft=roofer",
    "landscaper":   "craft=gardener",
    "lawyer":       "office=lawyer",
    "real_estate":  "office=estate_agent",
}

# Email addresses we never want (junk / role / image false positives)
EMAIL_DENYLIST = ("sentry", "wixpress", "example.", "noreply", "no-reply",
                  "donotreply", "do-not-reply", "abuse@", "postmaster@",
                  "privacy@", "dpo@")
BAD_TLDS = {"png", "jpg", "jpeg", "gif", "webp", "svg", "css", "js", "mp4",
            "woff", "woff2", "ttf"}
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
MAILTO_RE = re.compile(r"mailto:([^\"'?>\s]+)", re.IGNORECASE)

CSV_COLUMNS = ["name", "category", "address", "phone", "email", "email_source",
               "website", "lat", "lon", "osm_id", "source"]


def log(msg: str) -> None:
    """UTF-8-safe console logging: some Windows consoles choke on box chars."""
    try:
        print(msg, file=sys.stderr, flush=True)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"),
              file=sys.stderr, flush=True)


# --------------------------------------------------------------------------
# Tiny flat config reader — no PyYAML needed. Format: "key: value" lines,
# '#' comments, blank lines ignored. That's the whole format, on purpose.
def load_config(path: Path) -> dict:
    cfg = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        cfg[key.strip().lower()] = value.split(" #")[0].strip()
    return cfg


def http_get(url: str, accept: str = "*/*") -> tuple[str, int]:
    """Polite GET. Returns (body_text, status_code). Raises on network error."""
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT, "Accept": accept,
        "Accept-Language": "en"})
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read(2_000_000).decode(charset, errors="replace"), resp.status


# --------------------------------------------------------------------------
def geocode(town: str, contact: str) -> tuple[float, float]:
    """Town name -> (lat, lon) via OpenStreetMap Nominatim (1 request)."""
    log(f"[*] Locating '{town}' via OpenStreetMap ...")
    url = NOMINATIM_URL + "?" + urllib.parse.urlencode(
        {"q": town, "format": "json", "limit": 1})
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT.replace("polite; ", f"contact: {contact}; ")})
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        results = json.loads(resp.read().decode("utf-8"))
    if not results:
        raise SystemExit(f"[!] Could not find '{town}' on OpenStreetMap. "
                         "Try adding state/region, e.g. 'Springfield, IL'.")
    lat, lon = float(results[0]["lat"]), float(results[0]["lon"])
    log(f"[+] Found: {results[0].get('display_name', town)} "
        f"({lat:.4f}, {lon:.4f})")
    return lat, lon


def query_overpass(osm_tag: str, lat: float, lon: float,
                   radius_m: int) -> list[dict]:
    """One Overpass query for businesses with the given tag near (lat, lon)."""
    q = (f"[out:json][timeout:60];"
         f"nwr[\"{osm_tag.split('=')[0]}\"=\"{osm_tag.split('=')[1]}\"]"
         f"(around:{radius_m},{lat},{lon});"
         f"out center;")
    log(f"[*] Querying Overpass API for {osm_tag} within {radius_m} m ...")
    data = urllib.parse.urlencode({"data": q}).encode()
    req = urllib.request.Request(OVERPASS_URL, data=data, headers={
        "User-Agent": USER_AGENT, "Content-Type":
            "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    elements = payload.get("elements", [])
    log(f"[+] Overpass returned {len(elements)} places")
    return elements


def element_to_record(el: dict, category: str) -> dict | None:
    tags = el.get("tags", {})
    name = tags.get("name", "").strip()
    if not name:
        return None  # unnamed places are useless as leads
    addr_parts = [tags.get(k, "") for k in
                  ("addr:housenumber", "addr:street", "addr:city",
                   "addr:postcode")]
    address = ", ".join(p for p in addr_parts if p)
    center = el.get("center", {})
    lat = el.get("lat") or center.get("lat", "")
    lon = el.get("lon") or center.get("lon", "")
    website = (tags.get("website") or tags.get("contact:website") or
               tags.get("url") or "").strip()
    return {
        "name": name,
        "category": category,
        "address": address,
        "phone": tags.get("phone") or tags.get("contact:phone") or
                 tags.get("contact:mobile") or "",
        "email": (tags.get("email") or tags.get("contact:email") or "").strip(),
        "email_source": "osm" if (tags.get("email") or
                                  tags.get("contact:email")) else "",
        "website": website,
        "lat": lat, "lon": lon,
        "osm_id": f"{el['type']}/{el['id']}",
        "source": "OpenStreetMap © OpenStreetMap contributors (ODbL)",
    }


# --------------------------------------------------------------------------
def robots_allowed(url: str, rp_cache: dict) -> bool:
    """robots.txt check, cached per host. Unreachable robots.txt => allowed."""
    host = urllib.parse.urlsplit(url).netloc
    if host not in rp_cache:
        rp = urllib.robotparser.RobotFileParser()
        robots_url = f"https://{host}/robots.txt" \
            if url.startswith("https") else f"http://{host}/robots.txt"
        try:
            body, status = http_get(robots_url, accept="text/plain")
            if status == 200 and body.strip():
                rp.parse(body.splitlines())
            else:  # 4xx / empty: no rules
                rp.allow_all = True
        except Exception:
            rp.allow_all = True
        rp_cache[host] = rp
    return rp_cache[host].can_fetch(USER_AGENT, url)


def extract_emails(html: str) -> list[str]:
    found = set()
    for m in MAILTO_RE.finditer(html):
        found.add(urllib.parse.unquote(m.group(1)))
    for m in EMAIL_RE.finditer(html):
        found.add(m.group(0))
    clean = set()
    for email in found:
        e = email.strip().strip(".").lower()
        if any(bad in e for bad in EMAIL_DENYLIST):
            continue
        tld = e.rsplit(".", 1)[-1]
        if tld in BAD_TLDS or len(tld) > 10:
            continue
        if len(e) > 60:  # base64 blobs and minified code fragments
            continue
        clean.add(e)
    return sorted(clean)


def same_domain_links(html: str, base_url: str) -> list[str]:
    out, seen = [], set()
    for href in re.findall(r'href=["\']([^"\'#]+)["\']', html, re.IGNORECASE):
        absolute = urllib.parse.urljoin(base_url, href)
        parts = urllib.parse.urlsplit(absolute)
        if parts.scheme not in ("http", "https"):
            continue
        if parts.netloc != urllib.parse.urlsplit(base_url).netloc:
            continue  # stay on the business's own site only
        path = parts.path.rstrip("/") or "/"
        if re.search(r"\.(jpg|jpeg|png|gif|webp|svg|pdf|zip|css|js|ico)$",
                     path, re.IGNORECASE):
            continue
        if path in ("/", "/index.html", "/index.htm", "/home"):
            continue
        key = parts.netloc + path
        if key not in seen:
            seen.add(key)
            out.append(f"{parts.scheme}://{parts.netloc}{path}")
    return out[:4]  # cap links per page


def crawl_site_for_email(start_url: str, max_pages: int,
                         rp_cache: dict) -> tuple[str, str]:
    """Visit up to max_pages of ONE site, politely. Returns (email, source)."""
    base = start_url if start_url.startswith("http") else "https://" + start_url
    queue, visited = [base], set()
    for i in range(max_pages):
        if i >= len(queue):
            break
        url = queue[i]
        if url in visited or not robots_allowed(url, rp_cache):
            continue
        visited.add(url)
        if i > 0:
            time.sleep(REQUEST_DELAY)  # 1 req/sec — keep it polite
        try:
            html, _ = http_get(url, accept="text/html")
        except Exception:
            continue
        emails = extract_emails(html)
        if emails:
            return emails[0], url
        queue.extend(same_domain_links(html, base))
    return "", ""


# --------------------------------------------------------------------------
def dedupe(records: list[dict]) -> list[dict]:
    seen_name, seen_email, out = set(), set(), []
    for r in records:
        key = (r["name"].lower().strip(),
               re.sub(r"\W+", "", r["address"].lower()))
        if key in seen_name:
            continue
        seen_name.add(key)
        if r["email"]:
            if r["email"] in seen_email:
                r["email"], r["email_source"] = "", ""
            else:
                seen_email.add(r["email"])
        out.append(r)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Polite local lead scraper (OpenStreetMap + published "
                    "website emails). Runs entirely on your machine.")
    ap.add_argument("--config", default="config.yml")
    ap.add_argument("--town", help="override config: e.g. 'Asheville, NC'")
    ap.add_argument("--category", help=f"override config. choices: "
                                       f"{', '.join(sorted(CATEGORIES))}")
    ap.add_argument("--limit", type=int, help="max leads to keep")
    ap.add_argument("--max-pages", type=int,
                    help="max pages crawled per website (default from config)")
    ap.add_argument("--no-crawl", action="store_true",
                    help="skip website visits; OSM data only")
    ap.add_argument("--csv", default="leads.csv", help="output CSV path")
    args = ap.parse_args()

    cfg_path = Path(args.config)
    cfg = load_config(cfg_path) if cfg_path.exists() else {}
    if not cfg_path.exists():
        log("[!] No config.yml found — using CLI args / defaults. "
            "Copy config.example.yml to config.yml for a real run.")

    town = args.town or cfg.get("town", "")
    category = (args.category or cfg.get("category", "restaurant")).lower()
    radius_m = int(cfg.get("radius_meters", "5000"))
    max_pages = args.max_pages or int(cfg.get("max_pages_per_site", "5"))
    crawl_enabled = not args.no_crawl and \
        cfg.get("crawl_website_emails", "true").lower() != "false"
    contact = cfg.get("contact", "operator@example.com")
    limit = args.limit

    if not town:
        raise SystemExit("[!] No town set. Use --town 'Yourtown, ST' or set "
                         "town: in config.yml")
    osm_tag = CATEGORIES.get(category, cfg.get("osm_tag", ""))
    if not osm_tag:
        raise SystemExit(f"[!] Unknown category '{category}'. Choose one of: "
                         + ", ".join(sorted(CATEGORIES)) +
                         "\n    or set osm_tag: key=value in config.yml")

    lat, lon = geocode(town, contact)
    elements = query_overpass(osm_tag, lat, lon, radius_m)

    records = [r for el in elements if (r := element_to_record(el, category))]
    log(f"[+] {len(records)} named places after cleanup")

    # Crawl websites for published emails (politely, robots-aware)
    if crawl_enabled:
        to_crawl = [r for r in records if r["website"] and not r["email"]]
        log(f"[*] Visiting {len(to_crawl)} published websites "
            f"(max {max_pages} pages each, 1 req/sec) ...")
        rp_cache: dict = {}
        for n, r in enumerate(to_crawl, 1):
            email, src = crawl_site_for_email(r["website"], max_pages, rp_cache)
            if email:
                r["email"], r["email_source"] = email, src
                log(f"    [{n}/{len(to_crawl)}] {r['name']}: {email}")
            else:
                log(f"    [{n}/{len(to_crawl)}] {r['name']}: no published "
                    "email found")
            if limit and sum(1 for x in records if x["email"]) >= limit:
                log("[*] Email limit reached — stopping crawl early")
                break

    records = dedupe(records)
    if not crawl_enabled:  # keep rows without emails only if nothing better
        pass
    if limit:
        records = records[:limit]

    out = Path(args.csv)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(records)

    with_email = sum(1 for r in records if r["email"])
    log(f"\n[OK] Wrote {len(records)} leads ({with_email} with email) "
        f"to {out}")
    log("    Remember: you are the data controller. Comply with CAN-SPAM /")
    log("    CASL / GDPR before contacting anyone. See ../legal/DISCLAIMER.md")
    log("    and ../legal/SCRAPING-101.md — by running this tool you accept")
    log("    full responsibility under those documents and the Terms of Use.")
    log("    Want it tuned, run, or maintained for you? "
        "https://www.mrtscomputers.com")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n[!] Stopped by user — partial results were not saved.")
        sys.exit(130)
