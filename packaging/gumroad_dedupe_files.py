#!/usr/bin/env python3
"""
Deduplicate Gumroad product files: repeated `products update --file` calls
ADD versions instead of replacing, so products can end up with several
near-identical zips. This script keeps ONLY the file whose size matches the
current local zip in dist-packages/ (with a sanity check), prunes the rest
from the product content doc, and reports what it did.

    python3 packaging/gumroad_dedupe_files.py            # do it
    python3 packaging/gumroad_dedupe_files.py --dry-run  # preview only
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUMROAD = str(Path.home() / ".local/bin/gumroad")

PRODUCTS = {
    "tML_5GZeUeMILesCZa6wig==": "01-lead-scraper-v1.0.zip",
    "e9_DOpjUj-Uv61flIApzCQ==": "02-ai-outreach-pack-v1.0.zip",
    "veK6XKQ__6e43e1fqTuhMA==": "03-n8n-intake-blueprint-v1.0.zip",
    "LJex-_hZVt3IQrobmniSCA==": "complete-toolbox-v1.0.zip",
}


def gum(*args: str) -> dict:
    out = subprocess.run([GUMROAD, *args], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"gumroad {' '.join(args[:3])} failed: "
                           f"{out.stderr.strip()[:200]}")
    return json.loads(out.stdout)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    for pid, zipname in PRODUCTS.items():
        local = ROOT / "dist-packages" / zipname
        if not local.exists():
            print(f"[!] {zipname}: local zip missing — skipping")
            continue
        local_size = local.stat().st_size

        content = gum("products", "content", "get", pid, "--json")
        pages = content if isinstance(content, list) else content.get("pages",
                                                                      [content])
        changed = False
        for page in pages:
            nodes = page.get("description", {}).get("content", [])
            embeds = [n for n in nodes if n.get("type") == "fileEmbed"]
            if len(embeds) <= 1:
                print(f"[=] {zipname}: {len(embeds)} file embed — clean")
                continue
            # need file sizes: match embed ids to the files list
            view = gum("products", "view", pid, "--json")["product"]
            files = view.get("files", [])
            by_id = {f["id"]: f for f in files}
            keep = None
            for e in embeds:
                fid = e["attrs"]["id"]
                f = by_id.get(fid)
                if f and f.get("size") == local_size:
                    keep = e
                    break
            if keep is None:
                print(f"[!] {zipname}: NO uploaded file matches local size "
                      f"{local_size} — re-upload needed, skipping prune")
                continue
            keep_id = keep["attrs"]["id"]
            kept_file = by_id[keep_id]
            removed = [by_id[e["attrs"]["id"]]["size"] for e in embeds
                       if e["attrs"]["id"] != keep_id
                       and e["attrs"]["id"] in by_id]
            page["description"]["content"] = [n for n in nodes
                                              if not (n.get("type") ==
                                                      "fileEmbed"
                                                      and n["attrs"]["id"]
                                                      != keep_id)]
            print(f"[*] {zipname}: keeping {kept_file['size']} B "
                  f"(matches local), pruning {len(removed)} stale versions "
                  f"{sorted(removed)}")
            changed = True
            if not args.dry_run:
                tmp = ROOT / "dist-packages" / f"content-{pid}.json"
                # content set requires the PAGES LIST shape (an array),
                # not a single page object
                tmp.write_text(json.dumps(pages), encoding="utf-8")
                subprocess.run([GUMROAD, "products", "content", "set", pid,
                                str(tmp), "--yes", "--quiet"],
                               check=True, capture_output=True, text=True)
                tmp.unlink()
                print(f"    → saved")
        if not changed:
            continue
        # verify
        view = gum("products", "view", pid, "--json")["product"]
        n = len(view.get("files", []))
        print(f"[✓] {zipname}: product now lists {n} file(s)")
    print("Done.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[!] {e}", file=sys.stderr)
        sys.exit(1)
