#!/usr/bin/env python3
"""
toolbox_common — shared plumbing for the per-package GUIs.

Kept tiny on purpose: each package GUI stays self-readable, and
packaging/make_packages.py copies this file into every distributable zip.
"""

import os
import shutil
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path


def log(msg: str = "") -> None:
    print(msg, flush=True)


def python_exe() -> str:
    return sys.executable or "python3"


def open_url(url: str) -> None:
    webbrowser.open(url)


def open_in_editor(path: Path) -> None:
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-t", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception as e:
        log(f"[!] Could not open editor: {e}")


def open_folder(path: Path) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
        if sys.platform.startswith("win"):
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception as e:
        log(f"[!] Could not open folder: {e}")


def ensure_config(product_dir: Path) -> tuple[Path, bool]:
    """Copy config.example.yml -> config.yml if missing. (path, created)"""
    cfg = product_dir / "config.yml"
    example = product_dir / "config.example.yml"
    if not cfg.exists() and example.exists():
        shutil.copyfile(example, cfg)
        return cfg, True
    return cfg, False


def find_doc(here: Path, *names: str) -> Path | None:
    """Locate a doc/legal file whether we run inside the repo or a
    packaged zip (docs may sit next to the GUI or one level up)."""
    for name in names:
        for base in (here, here.parent):
            for sub in ("", "legal"):
                p = base / sub / name if sub else base / name
                if p.exists():
                    return p
    return None


def run_stream(cmd: list[str], cwd: Path, on_line=None, on_done=None) -> None:
    """Run a command, streaming combined stdout/stderr line by line."""
    def worker():
        try:
            proc = subprocess.Popen(
                cmd, cwd=str(cwd), stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True, bufsize=1,
                errors="replace")
            assert proc.stdout is not None
            for line in proc.stdout:
                if on_line:
                    on_line(line.rstrip("\n"))
            code = proc.wait()
            if on_done:
                on_done(code)
        except Exception as e:
            if on_line:
                on_line(f"[!] {e.__class__.__name__}: {e}")
            if on_done:
                on_done(1)

    threading.Thread(target=worker, daemon=True).start()


def show_text_viewer(parent, title: str, path: Path) -> None:
    """Readable in-app viewer for the markdown docs and legal files:
    headings, bullets, code blocks, clickable links."""
    import re
    import tkinter as tk
    from tkinter import scrolledtext, font as tkfont

    win = tk.Toplevel(parent)
    win.title(f"{title} — Mr T's DIY Toolbox")
    win.geometry("860x640")
    txt = scrolledtext.ScrolledText(win, wrap="word", borderwidth=0,
                                    padx=18, pady=14)
    txt.pack(fill="both", expand=True)

    base = tkfont.nametofont("TkTextFont")
    mono = tkfont.nametofont("TkFixedFont")
    txt.tag_configure("h1", font=(base.actual("family"), 16, "bold"),
                      spacing1=10, spacing3=6)
    txt.tag_configure("h2", font=(base.actual("family"), 13, "bold"),
                      spacing1=10, spacing3=4)
    txt.tag_configure("h3", font=(base.actual("family"), base.cget("size"),
                                  "bold"), spacing1=8)
    txt.tag_configure("code", font=mono, background="#f2f2ee",
                      lmargin1=14, lmargin2=14, spacing1=2, spacing3=2)
    txt.tag_configure("bullet", lmargin1=14, lmargin2=14)

    text = path.read_text(encoding="utf-8", errors="replace")
    in_code = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            txt.insert("end", line + "\n", "code")
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            txt.insert("end", m.group(2) + "\n",
                       {1: "h1", 2: "h2", 3: "h3"}[len(m.group(1))])
            continue
        if re.match(r"^\s*[-*]\s+", line):
            txt.insert("end", "  • " + re.sub(r"^\s*[-*]\s+", "", line)
                       + "\n", "bullet")
            continue
        if not line.strip():
            txt.insert("end", "\n")
            continue
        pos = 0
        for lm in re.finditer(r"\[([^\]]+)\]\((https?://[^)\s]+)\)"
                              r"|(https?://[^\s)>\]]+)", line):
            if lm.start() > pos:
                txt.insert("end", line[pos:lm.start()])
            label, url = ((lm.group(1), lm.group(2)) if lm.group(1)
                          else (lm.group(3), lm.group(3)))
            tag = f"link-{abs(hash((path.name, url, txt.index('end'))))}"
            txt.tag_configure(tag, foreground="#0a58ca", underline=True)
            txt.tag_bind(tag, "<Button-1>",
                         lambda _e, u=url: webbrowser.open(u))
            txt.tag_bind(tag, "<Enter>",
                         lambda _e: txt.config(cursor="hand2"))
            txt.tag_bind(tag, "<Leave>", lambda _e: txt.config(cursor=""))
            txt.insert("end", label, tag)
            pos = lm.end()
        if pos < len(line):
            txt.insert("end", line[pos:])
        txt.insert("end", "\n")

    txt.config(state="disabled")
    bar = tk.Frame(win)
    bar.pack(fill="x")
    tk.Button(bar, text="Open in my default editor",
              command=lambda: open_in_editor(path)).pack(side="left",
                                                         padx=8, pady=6)
    tk.Button(bar, text="Close", command=win.destroy).pack(side="right",
                                                           padx=8, pady=6)


SITE = "https://www.mrtscomputers.com"
# Deep link to the site's tip section (works once the section carries
# id="tips"; without it, browsers land at the top of the homepage where
# the floating tip button is visible anyway).
TIPS_URL = "https://www.mrtscomputers.com/#tips"


def support_bar(parent) -> None:
    """Slim footer for every GUI: custom-help link + tip call-to-action.
    The tip target is the site's tip section (Gumroad, Ko-fi, Cash App,
    Venmo, BTC/ETH/LTC)."""
    from tkinter import ttk
    bar = ttk.Frame(parent)
    bar.pack(fill="x", pady=(6, 0))
    tip = ttk.Label(bar, text="💚 Tip — keeps the free stuff coming",
                    foreground="#1a7f37", cursor="hand2")
    tip.pack(side="right")
    tip.bind("<Button-1>", lambda _e: open_url(TIPS_URL))
    help_lbl = ttk.Label(bar, text="Custom builds & help: mrtscomputers.com",
                         foreground="#0a58ca", cursor="hand2")
    help_lbl.pack(side="right", padx=(0, 14))
    help_lbl.bind("<Button-1>", lambda _e: open_url(SITE))


def floating_tip(root) -> None:
    """Always-visible floating 💚 Tip button on the window's left edge —
    mirrors the floating tip button on mrtscomputers.com."""
    import tkinter as tk
    btn = tk.Button(root, text="💚 Tip", command=lambda: open_url(TIPS_URL),
                    bg="#1a7f37", fg="white", activebackground="#166534",
                    activeforeground="white", relief="flat", cursor="hand2",
                    borderwidth=0, padx=10, pady=6,
                    font=("TkDefaultFont", 10, "bold"))
    btn.place(relx=0.0, rely=0.5, anchor="w", x=4)
    btn.lift()


def gui_doc_buttons(parent, here: Path, items: list[tuple[str, list[str]]],
                    root_win) -> None:
    """Row of buttons opening docs via the viewer. items = (label, [filenames])"""
    import tkinter as tk
    from tkinter import ttk
    frame = ttk.Frame(parent)
    frame.pack(fill="x", pady=4)
    col = 0
    for label, names in items:
        path = find_doc(here, *names)
        if path is None:
            continue
        ttk.Button(frame, text=label, width=30,
                   command=lambda p=path, t=label:
                   show_text_viewer(root_win, t, p)
                   ).grid(row=col // 3, column=col % 3, sticky="we",
                          padx=3, pady=3)
        col += 1
    for c in range(3):
        frame.columnconfigure(c, weight=1)
