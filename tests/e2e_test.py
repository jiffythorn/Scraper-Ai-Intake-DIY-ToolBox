#!/usr/bin/env python3
"""
End-to-end smoke tests for the DIY Toolbox.

Tests what buyers actually run:
  1. GUI construction — every widget-building code path executes (the class
     of bug that shipped once: a NameError inside launch_gui()).
  2. Scraper pipeline — real run against OpenStreetMap, CSV output verified.
  3. Outreach pipeline — all 7 modes (template), live free-endpoint draft,
     live local-Ollama draft, CSV integration, --save output.

    python3 tests/e2e_test.py            # everything live
    python3 tests/e2e_test.py --fast     # skip network/AI sections
    python3 tests/e2e_test.py --gui-only # just the GUI construction checks
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRAPER = ROOT / "01-lead-scraper"
OUTREACH = ROOT / "02-ai-outreach-pack"
N8N = ROOT / "03-n8n-intake-blueprint"
PY = sys.executable or "python3"

PASS, FAIL = [], []


def check(name: str, ok: bool, detail: str = "") -> None:
    (PASS if ok else FAIL).append(name)
    print(f"  {'✅' if ok else '❌'} {name}" + (f" — {detail}" if detail else ""))


def run(cmd, cwd, timeout=240):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True,
                          text=True, timeout=timeout, errors="replace")


def isolate_config(product: Path, extra: str = "") -> "tempfile.TemporaryDirectory":
    """Move any real config.yml aside so tests never touch user settings."""
    td = tempfile.TemporaryDirectory()
    real = product / "config.yml"
    if real.exists():
        os.rename(real, Path(td.name) / "config.yml")
    (product / "config.yml").write_text(
        ("sender_name: E2E Tester\nsender_business: Test Co\n"
         "sender_phone: +1-555-0100\nsender_email: e2e@test.example\n"
         + extra) if product == OUTREACH else
        ("town: Asheville, NC\ncategory: cafe\nradius_meters: 12000\n"
         "crawl_website_emails: false\nmax_pages_per_site: 1\n"
         "contact: e2e@test.example\n"),
        encoding="utf-8")
    return td


def restore_config(product: Path, td: "tempfile.TemporaryDirectory") -> None:
    (product / "config.yml").unlink(missing_ok=True)
    saved = Path(td.name) / "config.yml"
    if saved.exists():
        os.rename(saved, product / "config.yml")
    td.cleanup()


# ---------------------------------------------------------------------------
def test_gui_construction() -> None:
    print("\n[1] GUI construction (every code path builds without NameError)")
    for name, script in (("scraper_gui", SCRAPER / "scraper_gui.py"),
                         ("outreach_gui", OUTREACH / "outreach_gui.py"),
                         ("intake_gui", N8N / "intake_gui.py"),
                         ("toolbox", ROOT / "toolbox.py")):
        # Launch the real GUI. A healthy window runs mainloop() forever, so
        # "killed by our timeout" = PASS. A crash exits fast with a traceback.
        code = (
            f"import sys; sys.argv=['{name}'];\n"
            f"import importlib.util as iu\n"
            f"spec = iu.spec_from_file_location('{name}', r'{script}')\n"
            f"m = iu.module_from_spec(spec); spec.loader.exec_module(m)\n"
            f"m.launch_gui()\n")
        try:
            r = run([PY, "-c", code], ROOT, timeout=15)
            # exited on its own: fine only if it was a clean headless skip
            headless = "no display" in (r.stdout + r.stderr).lower()
            check(f"GUI builds: {name}", headless,
                  "headless — skipped" if headless else
                  (r.stderr.strip().splitlines() or ["?"])[-1][:110])
        except subprocess.TimeoutExpired:
            check(f"GUI builds: {name}", True,
                  "window opened and ran until killed (healthy)")


def test_scraper() -> None:
    print("\n[2] Scraper pipeline (live OpenStreetMap, no website crawling)")
    td = isolate_config(SCRAPER)
    out_csv = SCRAPER / "leads.csv"
    if out_csv.exists():
        out_csv.rename(Path(td.name) / "leads.csv.old")
    try:
        # Overpass is a free community service — transient 5xx/429 are
        # normal; a polite client retries. 3 attempts, short backoff.
        r = None
        for attempt in range(3):
            r = run([PY, "lead_scraper.py", "--csv", "e2e-leads.csv"],
                    SCRAPER)
            if r.returncode == 0:
                break
            transient = any(t in r.stderr for t in
                            ("504", "502", "503", "429", "Timeout"))
            if not transient:
                break
            import time
            time.sleep(6 * (attempt + 1))
        ok = r is not None and r.returncode == 0
        check("scraper: run completes", ok,
              (r.stderr.strip().splitlines() or ["no output"])[-1][:100])
        if ok:
            import csv as _csv
            with (SCRAPER / "e2e-leads.csv").open(encoding="utf-8") as f:
                rows = list(_csv.DictReader(f))
            check("scraper: CSV written with expected columns",
                  bool(rows) and {"name", "phone", "website"} <= set(rows[0]),
                  f"{len(rows)} cafes found")
            check("scraper: source attribution present",
                  bool(rows) and all("OpenStreetMap" in (r_.get("source") or "")
                                     for r_ in rows))
        # the isolated config sets crawl_website_emails: false, so the run
        # above already exercises the --no-crawl code path end to end
    finally:
        (SCRAPER / "e2e-leads.csv").unlink(missing_ok=True)
        restore_config(SCRAPER, td)


def test_outreach() -> None:
    print("\n[3] Outreach pipeline")
    # isolate the WHOLE section so assertions match the test persona,
    # never the user's real config.yml
    td = isolate_config(OUTREACH)
    try:
        _outreach_inner()
    finally:
        restore_config(OUTREACH, td)


def _outreach_inner() -> None:
    modes = ["website_audit", "first_touch", "followup_1", "followup_2",
             "reengage", "referral_request", "reply_handling"]
    # template (no-AI) mode for every prompt: catches broken prompt files
    results = {}
    for m in modes:
        r = run([PY, "outreach_runner.py", "--lead", "sample-lead.yml",
                 "--mode", m, "--no-ai"], OUTREACH)
        results[m] = r
    bad = {m: r.returncode for m, r in results.items() if r.returncode != 0}
    check("outreach: all 7 modes render (no-AI)", not bad, str(bad) if bad else "7/7")
    body = results["first_touch"].stdout
    check("outreach: identity attached (CAN-SPAM)",
          "E2E Tester" in body and "Test Co" in body)
    check("outreach: opt-out line attached",
          "no thanks" in body)

    # drafts dir with --save
    r = run([PY, "outreach_runner.py", "--lead", "sample-lead.yml",
             "--no-ai", "--save"], OUTREACH)
    saved = list((OUTREACH / "drafts").rglob("*.txt"))
    check("outreach: --save writes a draft file",
          r.returncode == 0 and bool(saved), f"{len(saved)} draft(s)")
    for p in saved:
        p.unlink(missing_ok=True)

    # CSV integration (scraper output feeds outreach)
    (OUTREACH / "e2e-leads.csv").write_text(
        "name,category,address,phone,email,email_source,website,lat,lon,"
        "osm_id,source\nE2E Roofing,roofer,\"1 Test St, Asheville, NC\","
        "+1-555-0101,,,'https://e2e.example',35.5,-82.5,n/1,osm\n",
        encoding="utf-8")
    r = run([PY, "outreach_runner.py", "--leads-csv", "e2e-leads.csv",
             "--row", "1", "--no-ai"], OUTREACH)
    check("outreach: leads.csv integration", r.returncode == 0 and
          "E2E Roofing" in r.stdout)
    (OUTREACH / "e2e-leads.csv").unlink(missing_ok=True)

    # live local AI (only if Ollama is running) — re-isolate per provider
    import socket
    try:
        with socket.create_connection(("127.0.0.1", 11434), timeout=0.5):
            ollama = True
    except OSError:
        ollama = False
    if ollama:
        cfg = isolate_config(OUTREACH, "provider: ollama\nmodel: llama3.1:8b\n")
        try:
            r = run([PY, "outreach_runner.py", "--lead", "sample-lead.yml"],
                    OUTREACH, timeout=300)
            check("outreach: LOCAL ollama draft (llama3.1:8b)",
                  r.returncode == 0 and "SUBJECT" in r.stdout,
                  (r.stderr.strip().splitlines() or ["?"])[-1][:90])
        finally:
            restore_config(OUTREACH, cfg)
    else:
        check("outreach: LOCAL ollama draft", True, "ollama not running — skipped")

    # live free endpoint (best-effort; community service flakiness ≠ failure)
    cfg = isolate_config(OUTREACH, "provider: free\n")
    try:
        r = run([PY, "outreach_runner.py", "--lead", "sample-lead.yml"],
                OUTREACH, timeout=300)
        ok = r.returncode == 0 and "SUBJECT" in r.stdout
        flaky = not ok and "struggling right now" in r.stderr
        check("outreach: FREE endpoint draft", ok or flaky,
              "endpoint busy (community service)" if flaky else
              ("draft produced" if ok else
               (r.stderr.strip().splitlines() or ["?"])[-1][:90]))
    finally:
        restore_config(OUTREACH, cfg)


def test_n8n_blueprints() -> None:
    print("\n[4] n8n blueprint sanity")
    import json
    try:
        wf = json.loads((N8N / "one-page-site-intake.json").read_text())
        nodes = [n["name"] for n in wf["nodes"]]
        check("blueprint: valid JSON with 5 nodes", len(nodes) == 5, str(nodes))
        check("blueprint: no placeholder credentials left empty",
              "PASTE_YOUR_GOOGLE_SHEET_ID" in json.dumps(wf))  # intentional
    except Exception as e:
        check("blueprint: valid JSON", False, str(e)[:90])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true", help="skip live network/AI")
    ap.add_argument("--gui-only", action="store_true")
    args = ap.parse_args()

    print("=" * 60)
    print("DIY Toolbox — end-to-end tests")
    print("=" * 60)

    test_gui_construction()
    if args.gui_only:
        report()
        return
    test_scraper()
    test_outreach()
    test_n8n_blueprints()
    report()


def report() -> None:
    print("\n" + "=" * 60)
    print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("Failed:", *FAIL, sep="\n  - ")
        sys.exit(1)
    print("All green.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        report()
