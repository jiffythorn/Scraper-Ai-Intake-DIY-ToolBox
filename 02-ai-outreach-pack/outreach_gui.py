#!/usr/bin/env python3
"""
Mr T's AI Outreach — package GUI.

Start button, provider picker (free / ollama / no-ai), lead source picker,
drafts folder, and in-app guides + legal viewer.

    python3 outreach_gui.py          # GUI
    python3 outreach_gui.py --check  # text status, exit
    python3 outreach_gui.py --cli    # text menu fallback
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

from toolbox_common import (support_bar,
                            ensure_config, find_doc, gui_doc_buttons,
                            log, open_folder, open_in_editor, open_url,
                            python_exe, show_text_viewer)  # noqa: E402

SCRIPT = HERE / "outreach_runner.py"
SITE = "https://www.mrtscomputers.com"


def set_config_provider(value: str) -> None:
    """Point config.yml at the provider chosen in the GUI (free/ollama)."""
    cfg = HERE / "config.yml"
    if not cfg.exists():
        return
    lines = cfg.read_text(encoding="utf-8").splitlines()
    out, done = [], False
    for ln in lines:
        if ln.strip().startswith("provider:"):
            out.append(f"provider: {value}")
            done = True
        else:
            out.append(ln)
    if not done:
        out.append(f"provider: {value}")
    cfg.write_text("\n".join(out) + "\n", encoding="utf-8")


def status_lines() -> list[str]:
    lines = [f"Python: {sys.version.split()[0]}"]
    cfg = HERE / "config.yml"
    lines.append("Config: ready" if cfg.exists()
                 else "Config: not set up (click START)")
    drafts = HERE / "drafts"
    n = sum(1 for _ in drafts.rglob("*.txt")) if drafts.exists() else 0
    lines.append(f"Saved drafts: {n}")
    return lines


def run_checks_cli() -> None:
    for line in status_lines():
        log(line)


def run_cli() -> None:
    while True:
        log("\n=== Mr T's AI Outreach ===")
        for line in status_lines():
            log("  " + line)
        log("""
  1) Start (create config if needed, then draft for sample lead)
  2) Edit config (set YOUR name/business — required by law)
  3) Draft with no-AI template (test plumbing)
  4) Open drafts folder
  5) Read guides / legal
  0) Quit""")
        c = input("\nChoose: ").strip()
        if c in ("1", "3"):
            ensure_config(HERE)
            args = [python_exe(), str(SCRIPT), "--lead",
                    "sample-lead.yml", "--save"]
            if c == "3":
                args.append("--no-ai")
            done = threading.Event()
            subprocess_done = {"code": 0}

            def on_done(code):
                subprocess_done["code"] = code
                done.set()
            from toolbox_common import run_stream
            run_stream(args, HERE, on_line=log, on_done=on_done)
            done.wait()
        elif c == "2":
            open_in_editor(ensure_config(HERE)[0])
        elif c == "4":
            open_folder(HERE / "drafts")
        elif c == "5":
            for name in ("WALKTHROUGH.md", "DISCLAIMER.md",
                         "TERMS-OF-USE.md", "PRIVACY.md"):
                p = find_doc(HERE, name)
                if p:
                    open_in_editor(p)
        elif c == "0":
            return


def launch_gui() -> None:
    import tkinter as tk
    from tkinter import scrolledtext, ttk

    root = tk.Tk()
    root.title("Mr T's AI Outreach")
    root.geometry("820x640")
    root.minsize(700, 560)

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
    ttk.Label(header, text="Mr T's AI Outreach",
              font=("TkDefaultFont", 15, "bold")).pack(side="left")
    lk = ttk.Label(header, text="help & custom builds", foreground="#0a58ca",
                   cursor="hand2")
    lk.pack(side="right")
    lk.bind("<Button-1>", lambda _e: open_url(SITE))

    body = ttk.Frame(root, padding=(14, 0, 14, 14))
    body.pack(fill="both", expand=True)

    opts = ttk.Frame(body)
    opts.pack(fill="x", pady=(0, 6))
    ttk.Label(opts, text="AI provider:").pack(side="left")
    provider = tk.StringVar(value="free")
    ttk.Combobox(opts, textvariable=provider, width=9, state="readonly",
                 values=["free", "ollama", "no-ai"]).pack(side="left",
                                                          padx=(4, 14))
    ttk.Label(opts, text="Lead:").pack(side="left")
    lead_mode = tk.StringVar(value="sample lead")
    ttk.Combobox(opts, textvariable=lead_mode, width=12, state="readonly",
                 values=["sample lead", "leads.csv row"]).pack(side="left",
                                                               padx=(4, 4))
    row_no = tk.StringVar(value="1")
    ttk.Spinbox(opts, from_=1, to=999, width=4,
                textvariable=row_no).pack(side="left")

    def build_args() -> list[str]:
        a = [python_exe(), str(SCRIPT)]
        if provider.get() == "no-ai":
            a.append("--no-ai")
        if lead_mode.get() == "leads.csv row":
            a += ["--leads-csv", "../01-lead-scraper/leads.csv",
                  "--row", row_no.get()]
        else:
            a += ["--lead", "sample-lead.yml"]
        a.append("--save")
        return a

    big_row = ttk.Frame(body)
    big_row.pack(fill="x", pady=(0, 8))
    start_btn = ttk.Button(big_row, text="START — draft email",
                           style="Big.TButton")
    start_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))
    stop_btn = ttk.Button(big_row, text="Stop", state="disabled")
    stop_btn.pack(side="left", padx=(0, 8))
    cfg_btn = ttk.Button(big_row, text="Edit config (your info — required)")
    cfg_btn.pack(side="left")

    out = scrolledtext.ScrolledText(body, height=15, state="disabled",
                                    font=("TkFixedFont", 9),
                                    background="#101418",
                                    foreground="#d8dee9")
    out.pack(fill="both", expand=True, pady=(4, 8))

    def write(line: str):
        q.put(line)

    def on_done(code):
        write(f"{'[OK]' if code == 0 else '[exit ' + str(code) + ']'} done."
              "  Draft saved under drafts/ — REVIEW before sending anything.")
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
            write("[*] First run: created config.yml — opening it.")
            write("    Fill in YOUR name/business/phone/email (it's the "
                  "law), save, then press START again.")
            open_in_editor(cfg)
            return
        if provider.get() != "no-ai":
            set_config_provider(provider.get())
        if lead_mode.get() == "leads.csv row" and \
                not Path(HERE.parent / "01-lead-scraper" / "leads.csv").exists() \
                and not Path(HERE / "leads.csv").exists():
            write("[!] No leads.csv found — run the Lead Scraper first, "
                  "or use the sample lead.")
            return
        out.config(state="normal")
        out.delete("1.0", "end")
        out.config(state="disabled")
        start_btn.config(state="disabled")
        stop_btn.config(state="normal")
        cmd = build_args()
        write("[*] " + " ".join(cmd[1:]))
        proc["p"] = subprocess.Popen(
            cmd, cwd=str(HERE), stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, bufsize=1,
            errors="replace")
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
    cfg_btn.config(command=lambda: (ensure_config(HERE),
                                    open_in_editor(HERE / "config.yml")))

    drafts_row = ttk.Frame(body)
    drafts_row.pack(fill="x", pady=(0, 6))
    ttk.Button(drafts_row, text="Open drafts folder",
               command=lambda: open_folder(HERE / "drafts")).pack(side="left")
    ttk.Label(drafts_row, text="  The tool NEVER sends. You review, paste "
                               "into your own mail client, send as YOU. "
                               "One sequence, then stop.",
              wraplength=520).pack(side="left")

    docs = ttk.LabelFrame(body, text="Read in-app (opens a viewer window)")
    docs.pack(fill="x")
    gui_doc_buttons(docs, HERE, [
        ("WALKTHROUGH", ["WALKTHROUGH.md"]),
        ("README", ["README.md"]),
        ("TERMS OF USE", ["TERMS-OF-USE.md"]),
        ("DISCLAIMER", ["DISCLAIMER.md"]),
        ("PRIVACY", ["PRIVACY.md"]),
        ("LICENSE (MIT)", ["LICENSE"]),
    ], root)

    support_bar(body)
    status = ttk.Label(body, text=" | ".join(status_lines()), wraplength=700)
    status.pack(anchor="w", pady=(8, 0))

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
