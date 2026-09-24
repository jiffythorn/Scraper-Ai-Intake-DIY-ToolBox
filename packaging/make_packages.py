#!/usr/bin/env python3
"""
Package the toolbox for distribution — pure stdlib, any OS.

Creates in  dist-packages/ :

    01-lead-scraper-v<VER>.zip       ← product 1 alone
    02-ai-outreach-pack-v<VER>.zip   ← product 2 alone
    03-n8n-intake-blueprint-v<VER>.zip
    complete-toolbox-v<VER>.zip      ← everything, one download

Each individual zip is self-sufficient: the product folder, its START-HERE
launchers, the shared GUI helper, the guides, and the full legal/ pack.

    python3 packaging/make_packages.py            # build all
    python3 packaging/make_packages.py --version 2.1
"""

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist-packages"

VERSION = "1.0"

EXCLUDE_DIRS = {"__pycache__", "drafts", "node_modules", ".git", ".vscode",
                ".idea", "build", "dist", "dist-packages", ".freebuff"}
EXCLUDE_FILES = {"config.yml", "leads.csv", ".DS_Store", "Thumbs.db"}
EXCLUDE_SUFFIX = {".pyc", ".pyo", ".spec", ".log"}

# shared files that go into EVERY individual package
SHARED_FILES = ["toolbox_common.py", "WALKTHROUGH.md", "GETTING-STARTED.md",
                "README.md", "SERVICES.md"]
LEGAL_FILES = ["LICENSE", "DISCLAIMER.md", "TERMS-OF-USE.md", "PRIVACY.md",
               "SCRAPING-101.md", "THIRD-PARTY-NOTICES.md"]

PRODUCTS = [
    ("01-lead-scraper",
     ["01-lead-scraper"]),
    ("02-ai-outreach-pack",
     ["02-ai-outreach-pack"]),
    ("03-n8n-intake-blueprint",
     ["03-n8n-intake-blueprint"]),
]


def iter_files(base: Path) -> "list[Path]":
    """Yield paths RELATIVE to the project root (that's what the zip
    filters and arcnames expect)."""
    for path in sorted(base.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if path.name in EXCLUDE_FILES or path.suffix.lower() in EXCLUDE_SUFFIX:
            continue
        yield rel


def write_zip(zip_path: Path, include_prefixes: "list[str]",
              extra_root_files: "list[str]") -> int:
    """Zip everything under ROOT whose top-level dir/file matches
    include_prefixes, plus named root files. Returns file count."""
    count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in iter_files(ROOT):
            top = rel.parts[0]
            if top in include_prefixes or str(rel) in extra_root_files:
                zf.write(ROOT / rel, arcname=str(rel))
                count += 1
        # legal/ goes into every individual package so each is self-sufficient
        if "legal" not in include_prefixes:
            for name in LEGAL_FILES:
                src = ROOT / "legal" / name
                if src.exists():
                    zf.write(src, arcname=f"legal/{name}")
                    count += 1
        # START-HERE note at zip root for buyers
        note = ROOT / "packaging" / "PACKAGE-README.txt"
        if note.exists():
            zf.write(note, arcname="START-HERE.txt")
            count += 1
    return count


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default=VERSION)
    args = ap.parse_args()
    ver = args.version

    OUT.mkdir(exist_ok=True)
    print(f"Packaging v{ver} → {OUT}\n" + "-" * 56)

    built = []
    for name, prefixes in PRODUCTS:
        zpath = OUT / f"{name}-v{ver}.zip"
        n = write_zip(zpath, prefixes, SHARED_FILES)
        kb = zpath.stat().st_size / 1024
        print(f"  {zpath.name:44s} {n:4d} files  {kb:8.1f} KB")
        built.append(zpath)

    # complete bundle = everything tracked, no re-listing needed
    all_prefixes = [p for _n, ps in PRODUCTS for p in ps] + ["legal",
                                                             "packaging"]
    zpath = OUT / f"complete-toolbox-v{ver}.zip"
    n = write_zip(zpath, all_prefixes, SHARED_FILES + ["CONTRIBUTING.md",
                                                       ".gitignore"])
    kb = zpath.stat().st_size / 1024
    print(f"  {zpath.name:44s} {n:4d} files  {kb:8.1f} KB")
    built.append(zpath)

    print("-" * 56)
    print("Done. Ship the individual zips as products and the complete zip "
          "as the bundle. Buyers double-click START-HERE.bat (Windows) or "
          "START-HERE.sh (Mac/Linux) inside the product folder.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
