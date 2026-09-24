#!/usr/bin/env python3
"""
Mr T's Lead Scraper — package GUI.

The simple Start button for this package: check the machine, create/edit
the config, run, and open results. Guides and legal docs open in-app.

    python3 scraper_gui.py            # GUI
    python3 scraper_gui.py --check    # text status, exit
    python3 scraper_gui.py --cli      # text menu fallback
"""

import queue
import subprocess
import sys
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
if (HERE.parent / "toolbox_common.py").exists():
    sys.path.insert(0, str(HERE.parent))

from toolbox_common import (floating_tip, support_bar,
                            ensure_config, find_doc, gui_doc_buttons,
                            log, open_in_editor, open_url, python_exe,
                            run_stream, show_text_viewer)  # noqa: E402

SCRIPT = HERE / "lead_scraper.py"
SITE = "https://www.mrtscomputers.com"


def status_lines() -> list[str]:
    lines = [f"Python: {sys.version.split()[0]}"]
    cfg = HERE / "config.yml"
    lines.append("Config: ready" if cfg.exists()
                 else "Config: not set up (click START)")
    lines.append("Output: leads.csv " +
                 ("exists" if (HERE / "leads.csv").exists() else "— none yet"))
    return lines


def run_checks_cli() -> None:
    for line in status_lines():
        log(line)
    if not (HERE / "config.yml").exists():
        log("\nStart by double-clicking START-HERE "
            "(or: python3 scraper_gui.py).")


def run_cli() -> None:
    while True:
        log("\n=== Mr T's Lead Scraper ===")
        for line in status_lines():
            log("  " + line)
        log("""
  1) Start (create config if needed, then run)
  2) Edit config
  3) Open leads.csv
  4) Read SCRAPING-101 (responsibilities)
  5) Read WALKTHROUGH / guides
  0) Quit""")
        c = input("\nChoose: ").strip()
        if c == "1":
            ensure_config(HERE)
            input("Config ready. Press Enter to run (Ctrl+C to cancel) ")
            done = threading.Event()
            run_stream([python_exe(), str(SCRIPT)], HERE,
                       on_line=log,
                       on_done=lambda r: (log(f"[exit {r}]"), done.set()))
            done.wait()
            log("[*] Output: leads.csv")
        elif c == "2":
            open_in_editor(ensure_config(HERE)[0])
        elif c == "3":
            open_in_editor(HERE / "leads.csv")
        elif c == "4":
            p = find_doc(HERE, "SCRAPING-101.md")
            if p:
                open_in_editor(p)
        elif c == "5":
            for name in ("WALKTHROUGH.md", "GETTING-STARTED.md", "README.md"):
                p = find_doc(HERE, name)
                if p:
                    open_in_editor(p)
        elif c == "0":
            return


def launch_gui() -> None:
    import tkinter as tk
    from tkinter import scrolledtext, ttk

    root = tk.Tk()
    root.title("Mr T's Lead Scraper")
    root.geometry("760x600")
    root.minsize(640, 520)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure("Big.TButton", font=("TkDefaultFont", 11, "bold"),
                    padding=8)

    q: "queue.Queue[str]" = queue.Queue()
    proc: dict = {"p": None}

    def poll():
        try:
            while True:
                line = q.get_nowait()
                out.config(state="normal")
                out.insert("end", line + "\n")
                out.see("end")
                out.config(state="disabled")
        except queue.Empty:
            pass
        root.after(120, poll)

    header = ttk.Frame(root, padding=(14, 12, 14, 6))
    header.pack(fill="x")
    ttk.Label(header, text="Mr T's Lead Scraper",
              font=("TkDefaultFont", 15, "bold")).pack(side="left")
    lk = ttk.Label(header, text="help & custom builds", foreground="#0a58ca",
                   cursor="hand2")
    lk.pack(side="right")
    lk.bind("<Button-1>", lambda _e: open_url(SITE))

    body = ttk.Frame(root, padding=(14, 0, 14, 14))
    body.pack(fill="both", expand=True)

    big_row = ttk.Frame(body)
    big_row.pack(fill="x", pady=(0, 8))
    start_btn = ttk.Button(big_row, text="START — check, configure, run",
                           style="Big.TButton")
    start_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))
    stop_btn = ttk.Button(big_row, text="Stop", state="disabled")
    stop_btn.pack(side="left")

    out = scrolledtext.ScrolledText(body, height=16, state="disabled",
                                    font=("TkFixedFont", 9),
                                    background="#101418",
                                    foreground="#d8dee9")
    out.pack(fill="both", expand=True, pady=(4, 8))

    def write(line: str):
        q.put(line)

    def on_done(code):
        write(f"{'[OK]' if code == 0 else '[exit ' + str(code) + ']'} "
              "finished.  Output: leads.csv")
        start_btn.config(state="normal")
        stop_btn.config(state="disabled")
        proc["p"] = None

    def do_start():
        p = proc["p"]
        if p is not None and p.poll() is None:
            write("[!] Already running — press Stop first.")
            return
        cfg, created = ensure_config(HERE)
        if created:
            write("[*] First run: created config.yml — opening it for you.")
            write("    Set `town:` and `category:`, save, then press START "
                  "again.")
            open_in_editor(cfg)
            return
        out.config(state="normal")
        out.delete("1.0", "end")
        out.config(state="disabled")
        start_btn.config(state="disabled")
        stop_btn.config(state="normal")

        # direct spawn (not run_stream) so the Stop button owns the Popen
        proc["p"] = subprocess.Popen(
            [python_exe(), str(SCRIPT)], cwd=str(HERE),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            bufsize=1, errors="replace")
        assert proc["p"].stdout is not None

        def pump():
            for line in proc["p"].stdout:
                q.put(line.rstrip("\n"))
            code = proc["p"].wait()
            on_done(code)

        threading.Thread(target=pump, daemon=True).start()

    def do_stop():
        p = proc["p"]
        if p is not None and p.poll() is None:
            p.terminate()
            write("[!] Stopped by user.")

    start_btn.config(command=do_start)
    stop_btn.config(command=do_stop)

    docs = ttk.LabelFrame(body, text="Read in-app (opens a viewer window)")
    docs.pack(fill="x")
    gui_doc_buttons(docs, HERE, [
        ("SCRAPING-101 — read before first run", ["SCRAPING-101.md"]),
        ("WALKTHROUGH", ["WALKTHROUGH.md"]),
        ("GETTING-STARTED", ["GETTING-STARTED.md"]),
        ("README", ["README.md"]),
        ("TERMS OF USE", ["TERMS-OF-USE.md"]),
        ("DISCLAIMER", ["DISCLAIMER.md"]),
        ("PRIVACY", ["PRIVACY.md"]),
        ("LICENSE (MIT)", ["LICENSE"]),
        ("THIRD-PARTY NOTICES", ["THIRD-PARTY-NOTICES.md"]),
    ], root)

    support_bar(body)
    status = ttk.Label(body, text=" | ".join(status_lines()), wraplength=700)
    status.pack(anchor="w", pady=(8, 0))

    floating_tip(root)
    poll()
    root.mainloop()


def main() -> None:
    if "--check" in sys.argv:
        run_checks_cli()
        return
    if "--cli" in sys.argv:
        run_cli()
        return
    try:
        launch_gui()
    except ImportError:
        log("[*] No tkinter — text menu instead.")
        run_cli()


if __name__ == "__main__":
    main()
