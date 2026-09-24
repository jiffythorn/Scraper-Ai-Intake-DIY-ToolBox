#!/usr/bin/env python3
"""
Mr T's n8n Intake Blueprint — package GUI.

Start button: checks Node.js, launches n8n, opens the blueprint folder and
the step-by-step SETUP.md. Guides + legal read in-app.

    python3 intake_gui.py           # GUI
    python3 intake_gui.py --check   # text status, exit
    python3 intake_gui.py --cli     # text menu fallback
"""

import os
import queue
import shutil
import socket
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
if (HERE.parent / "toolbox_common.py").exists():
    sys.path.insert(0, str(HERE.parent))

from toolbox_common import (floating_tip, support_bar,
                            find_doc, gui_doc_buttons, log, open_folder,
                            open_in_editor, open_url,
                            show_text_viewer)  # noqa: E402

BLUEPRINT = HERE / "one-page-site-intake.json"
SITE = "https://www.mrtscomputers.com"


def node_installed() -> bool:
    return shutil.which("npx") is not None or shutil.which("node") is not None


def n8n_running() -> bool:
    try:
        with socket.create_connection(("127.0.0.1", 5678), timeout=0.6):
            return True
    except OSError:
        return False


def status_lines() -> list[str]:
    lines = [
        f"Node.js: {'found' if node_installed() else 'NOT installed (needed)'}",
        f"Blueprint: {'ready' if BLUEPRINT.exists() else 'MISSING!'}",
        f"n8n: {'running at http://localhost:5678' if n8n_running() else 'not running'}",
    ]
    return lines


def run_checks_cli() -> None:
    for line in status_lines():
        log(line)


def node_install_hint() -> str:
    if sys.platform.startswith("win"):
        return "winget install --id OpenJS.NodeJS.LTS -e"
    if sys.platform == "darwin":
        return "brew install node"
    return "install Node.js LTS from https://nodejs.org"


def start_n8n(emit=log) -> None:
    if not node_installed():
        emit(f"[!] Node.js missing. Install: {node_install_hint()}")
        return
    if n8n_running():
        emit("[*] n8n is already running → opening http://localhost:5678")
        webbrowser.open("http://localhost:5678")
        return
    emit("[*] Launching n8n... (FIRST RUN downloads ~100 MB via npx —")
    emit("    expect 3–8 quiet minutes; progress appears below)")
    # Calm output: npm emits dozens of scary-but-harmless deprecation and
    # peer-dependency warnings while installing n8n. Hide them at the source
    # and filter as a belt-and-braces — buyers only need real errors.
    env = dict(os.environ)
    env.update({"npm_config_loglevel": "error",
                "npm_config_fund": "false",
                "npm_config_audit": "false",
                "npm_config_update_notifier": "false",
                # n8n's optional AI-Assistant preview demands a paid model
                # key + a Docker code sandbox and blocks first-run with an
                # onboarding screen. Our blueprint never uses it — disable
                # the module so buyers land straight in the editor.
                "N8N_DISABLED_MODULES": "instance-ai"})
    try:
        # --yes: npx otherwise asks "Ok to proceed? (y)" and hangs forever
        # when output is piped (GUI users can never answer it)
        proc = subprocess.Popen(
            ["npx", "--yes", "n8n"], cwd=str(HERE), stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, bufsize=1,
            errors="replace", env=env)
    except Exception as e:
        emit(f"[!] Could not launch n8n ({e}). Run 'npx n8n' in a Terminal.")
        return

    import time as _t

    def pump():
        counts = {"npm": 0, "migrations": 0, "noise": 0}
        for line in proc.stdout:
            line = line.rstrip()
            if not line:
                continue
            if line.startswith("npm warn"):
                counts["npm"] += 1
                continue
            if line.startswith("Starting migration"):
                counts["migrations"] += 1
                if counts["migrations"] == 1:
                    emit("    [n8n] First-run database setup (migrations) — "
                         "one-time only, don't close this window...")
                continue
            if line.startswith("Finished migration"):
                continue
            if ("Failed to load Custom API options" in line
                    or line.startswith("(node:")
                    or line.startswith(" - ")
                    or "DeprecationWarning" in line
                    or "trace-deprecation" in line
                    or "There are deprecations related" in line):
                counts["noise"] += 1
                continue
            emit("    [n8n] " + line[:160])
        summary = []
        if counts["npm"]:
            summary.append(f"{counts['npm']} npm dependency warnings")
        if counts["migrations"]:
            summary.append(f"{counts['migrations']} database migrations "
                           "(one-time)")
        if counts["noise"]:
            summary.append(f"{counts['noise']} harmless setup notices")
        if summary:
            emit("    [i] Condensed for readability: " + "; ".join(summary)
                 + " — all normal, nothing to fix")

    def watcher():
        start_ts = _t.time()
        for i in range(120):  # up to ~10 minutes
            if proc.poll() is not None:
                emit("[!] n8n exited early — run 'npx --yes n8n' in a "
                     "Terminal to see why.")
                return
            try:
                with socket.create_connection(("127.0.0.1", 5678),
                                              timeout=0.5):
                    emit("[OK] n8n is UP at http://localhost:5678 — "
                         "opening your browser.")
                    emit("    Import: Workflows → Create → ⋯ → Import from "
                         "File → one-page-site-intake.json")
                    emit("    Then follow SETUP.md step 2 (Sheet ID) — "
                         "the GUI's Read SETUP.md button has it all.")
                    webbrowser.open("http://localhost:5678")
                    return
            except OSError:
                pass
            if i and i % 3 == 0:  # heartbeat every 15s — never look frozen
                emit(f"    ... still downloading/starting n8n "
                     f"({int(_t.time() - start_ts)}s elapsed) — this is "
                     "normal on first run")
            _t.sleep(5)
        emit("[*] Still not up after 10 minutes — n8n will appear at "
             "http://localhost:5678 when ready. Check your internet "
             "speed, or run 'npx --yes n8n' in a Terminal to watch it "
             "directly.")

    threading.Thread(target=pump, daemon=True).start()
    threading.Thread(target=watcher, daemon=True).start()


def run_cli() -> None:
    while True:
        log("\n=== Mr T's n8n Intake Blueprint ===")
        for line in status_lines():
            log("  " + line)
        log("""
  1) START (launch n8n + open browser)
  2) Read SETUP.md (step by step)
  3) Open blueprint folder
  4) Install help for Node.js
  5) Read legal
  0) Quit""")
        c = input("\nChoose: ").strip()
        if c == "1":
            start_n8n()
        elif c == "2":
            open_in_editor(HERE / "SETUP.md")
        elif c == "3":
            open_folder(HERE)
        elif c == "4":
            log(f"    {node_install_hint()}")
        elif c == "5":
            for name in ("TERMS-OF-USE.md", "DISCLAIMER.md", "PRIVACY.md",
                         "THIRD-PARTY-NOTICES.md"):
                p = find_doc(HERE, name)
                if p:
                    open_in_editor(p)
        elif c == "0":
            return


def launch_gui() -> None:
    import tkinter as tk
    from tkinter import scrolledtext, ttk

    root = tk.Tk()
    root.title("Mr T's n8n Intake Blueprint")
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
    ttk.Label(header, text="Mr T's n8n Intake Blueprint",
              font=("TkDefaultFont", 15, "bold")).pack(side="left")
    lk = ttk.Label(header, text="help & custom builds", foreground="#0a58ca",
                   cursor="hand2")
    lk.pack(side="right")
    lk.bind("<Button-1>", lambda _e: open_url(SITE))

    body = ttk.Frame(root, padding=(14, 0, 14, 14))
    body.pack(fill="both", expand=True)

    ttk.Label(body, text="Form → Google Sheet → Discord ping → welcome "
                         "email. Import one JSON into free n8n; SETUP.md "
                         "walks every click.", wraplength=700)\
        .pack(anchor="w", pady=(0, 8))

    big_row = ttk.Frame(body)
    big_row.pack(fill="x", pady=(0, 8))
    start_btn = ttk.Button(big_row, text="START — launch n8n & open browser",
                           style="Big.TButton",
                           command=lambda: start_n8n(emit=write))
    start_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))
    setup_btn = ttk.Button(big_row, text="Read SETUP.md")
    setup_btn.pack(side="left")

    out = scrolledtext.ScrolledText(body, height=10, state="disabled",
                                    font=("TkFixedFont", 9),
                                    background="#101418",
                                    foreground="#d8dee9")
    out.pack(fill="both", expand=True, pady=(4, 8))

    def write(line: str):
        q.put(line)

    setup_btn.config(command=lambda: show_text_viewer(root, "SETUP",
                                                      HERE / "SETUP.md"))

    steps = ttk.LabelFrame(body, text="The 3 steps (after n8n is running)")
    steps.pack(fill="x")
    tk.Label(steps, justify="left", text=(
        "1. Import from File → one-page-site-intake.json\n"
        "2. Click the Google Sheets node → paste YOUR Sheet ID → sign in\n"
        "3. Toggle Active. Test the form. Done."
    )).pack(anchor="w", padx=8, pady=6)

    docs = ttk.LabelFrame(body, text="Read in-app (opens a viewer window)")
    docs.pack(fill="x")
    gui_doc_buttons(docs, HERE, [
        ("SETUP — step by step", ["SETUP.md"]),
        ("README", ["README.md"]),
        ("TERMS OF USE", ["TERMS-OF-USE.md"]),
        ("DISCLAIMER", ["DISCLAIMER.md"]),
        ("PRIVACY", ["PRIVACY.md"]),
        ("THIRD-PARTY NOTICES (n8n license!)", ["THIRD-PARTY-NOTICES.md"]),
        ("LICENSE (MIT)", ["LICENSE"]),
    ], root)

    support_bar(body)
    status = ttk.Label(body, text=" | ".join(status_lines()), wraplength=700)
    status.pack(anchor="w", pady=(8, 0))

    for line in status_lines():
        write(line)
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
