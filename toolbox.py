#!/usr/bin/env python3
"""
Mr T's DIY Toolbox — one-stop launcher + setup doctor.

One window (tkinter ships inside Python — nothing to install) that ties the
toolbox together:

  * HOME    — where to start
  * SETUP   — the DOCTOR: checks every dependency and offers one-click
              fixes (configs, Ollama, Node/n8n, model pulls, launches)
  * LAUNCH  — run the scraper, draft outreach, wire the n8n intake
  * READ    — every guide and all legal files in a built-in viewer
  * LINKS   — help + MrTsComputers.com

No tkinter (rare Linux)? Falls back to a text menu with the same powers.

    python3 toolbox.py            # GUI (auto-opens Setup tab on first run)
    python3 toolbox.py --doctor   # print dependency report, exit
    python3 toolbox.py --cli      # text menu
    python3 toolbox.py --check    # short environment status, exit

You are the operator. Read the Legal tab first. https://www.mrtscomputers.com
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

ROOT = Path(__file__).resolve().parent
SCRAPER_DIR = ROOT / "01-lead-scraper"
OUTREACH_DIR = ROOT / "02-ai-outreach-pack"
N8N_DIR = ROOT / "03-n8n-intake-blueprint"
LEGAL_DIR = ROOT / "legal"
SITE = "https://www.mrtscomputers.com"
LOCAL_MODEL = "llama3.1:8b"


def log(msg: str = "") -> None:
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# helpers (shared by GUI and CLI)
# ---------------------------------------------------------------------------
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


def ollama_installed() -> bool:
    return shutil.which("ollama") is not None


def ollama_running() -> bool:
    try:
        with socket.create_connection(("127.0.0.1", 11434), timeout=0.6):
            return True
    except OSError:
        return False


def node_installed() -> bool:
    return shutil.which("npx") is not None or shutil.which("node") is not None


def ollama_install_cmd() -> str:
    if sys.platform.startswith("win"):
        return "winget install --id Ollama.Ollama -e"
    if sys.platform == "darwin":
        return "brew install --cask ollama"
    return "curl -fsSL https://ollama.com/install.sh | sh"


def node_install_cmd() -> str:
    if sys.platform.startswith("win"):
        return "winget install --id OpenJS.NodeJS.LTS -e"
    if sys.platform == "darwin":
        return "brew install node"
    return "# Linux: install Node.js LTS from https://nodejs.org " \
           "(or your package manager, e.g. sudo apt install nodejs npm)"


def start_ollama() -> None:
    if not ollama_installed():
        log("[!] Ollama is not installed yet — use the install button first.")
        return
    if ollama_running():
        log("[*] Ollama is already running.")
        return
    try:
        if sys.platform.startswith("win"):
            subprocess.Popen(["ollama", "serve"],
                             creationflags=subprocess.DETACHED_PROCESS)
        else:
            subprocess.Popen(["ollama", "serve"],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             start_new_session=True)
        log("[*] Starting Ollama in the background... give it ~5 seconds.")
    except Exception as e:
        log(f"[!] Could not start Ollama automatically ({e}). "
            "Run 'ollama serve' in a Terminal.")


def launch_n8n(on_ready=None) -> None:
    if not node_installed():
        log("[!] Node.js not found — install it first (Setup tab).")
        return
    try:
        kwargs: dict = {}
        if sys.platform.startswith("win"):
            kwargs["creationflags"] = subprocess.DETACHED_PROCESS
        else:
            kwargs["start_new_session"] = True
        env = dict(os.environ)
        env.update({"npm_config_loglevel": "error",
                    "npm_config_fund": "false",
                    "npm_config_audit": "false",
                    "npm_config_update_notifier": "false",
                    # skip n8n's AI-Assistant sandbox onboarding (unused)
                    "N8N_DISABLED_MODULES": "instance-ai"})
        subprocess.Popen(["npx", "--yes", "n8n"], cwd=str(N8N_DIR),
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, env=env, **kwargs)
        log("[*] n8n is starting in the background (first run downloads a "
            "lot — be patient)...")
        log("[*] Opening http://localhost:5678 in ~15 seconds...")

        def opener():
            import time
            time.sleep(15)
            open_url("http://localhost:5678")
            if on_ready:
                on_ready()
        threading.Thread(target=opener, daemon=True).start()
    except Exception as e:
        log(f"[!] Could not launch n8n ({e}). Run 'npx --yes n8n' in a "
            "Terminal.")


# ---------------------------------------------------------------------------
# THE DOCTOR — every dependency, one honest list
# ---------------------------------------------------------------------------
def doctor_report() -> list[tuple[str, str, str]]:
    """(item, status: ok/warn/missing/info, detail)"""
    items: list[tuple[str, str, str]] = []

    ver = tuple(int(x) for x in sys.version.split()[0].split(".")[:2])
    items.append(("Python 3.9+", "ok" if ver >= (3, 9) else "warn",
                  f"found {sys.version.split()[0]}"))

    try:
        import tkinter  # noqa: F401
        items.append(("GUI (tkinter)", "ok", "built-in"))
    except Exception:
        items.append(("GUI (tkinter)", "info",
                      "absent — text menu will be used "
                      "(Linux: install 'python3-tk')"))

    for label, d in (("Scraper config", SCRAPER_DIR),
                     ("Outreach config", OUTREACH_DIR)):
        cfg = d / "config.yml"
        items.append((label, "ok" if cfg.exists() else "missing",
                      "ready" if cfg.exists()
                      else "not created yet (one-click below)"))

    items.append(("leads.csv (scraper output)",
                  "info" if (SCRAPER_DIR / "leads.csv").exists()
                  else "info",
                  "exists" if (SCRAPER_DIR / "leads.csv").exists()
                  else "none yet — run the scraper"))

    if ollama_installed():
        if ollama_running():
            items.append(("Ollama (local AI)", "ok", "installed & running"))
            try:
                out = subprocess.run(["ollama", "list"],
                                     capture_output=True, text=True,
                                     timeout=10).stdout
                models = [ln.split()[0] for ln in out.splitlines()[1:]
                          if ln.strip()]
                if models:
                    items.append(("Local AI model", "ok",
                                  ", ".join(models[:3])))
                else:
                    items.append((f"Local AI model ({LOCAL_MODEL})",
                                  "missing",
                                  "no models pulled yet (one-click below)"))
            except Exception:
                items.append(("Local AI model", "info",
                              "could not read model list"))
        else:
            items.append(("Ollama (local AI)", "warn",
                          "installed but not running (Start button below)"))
    else:
        items.append(("Ollama (local AI)", "missing",
                      "not installed — optional; 'free' provider works "
                      "without it"))

    if node_installed():
        items.append(("Node.js (for n8n)", "ok", "found"))
    else:
        items.append(("Node.js (for n8n)", "missing",
                      "not installed — needed only for product 3"))

    return items


def env_status() -> list[str]:
    lines = [f"Python       : {sys.version.split()[0]}  ({python_exe()})"]
    for item, status, detail in doctor_report():
        icon = {"ok": "[ok]     ", "warn": "[warn]   ",
                "missing": "[missing]", "info": "[info]   "}[status]
        lines.append(f"{icon} {item:28s} {detail}")
    return lines


# ---------------------------------------------------------------------------
# generic streaming runner
# ---------------------------------------------------------------------------
def run_stream(cmd: list[str], cwd: Path, on_line=None, on_done=None) -> None:
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


def run_tool(product_dir: Path, args: list[str],
             on_line=None, on_done=None) -> None:
    script = product_dir / ("lead_scraper.py" if product_dir == SCRAPER_DIR
                            else "outreach_runner.py")
    run_stream([python_exe(), str(script), *args], product_dir,
               on_line, on_done)


# ---------------------------------------------------------------------------
# tiny markdown viewer
# ---------------------------------------------------------------------------
def show_text_viewer(parent, title: str, path: Path):
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
            txt.tag_bind(tag, "<Enter>", lambda _e: txt.config(cursor="hand2"))
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


# ---------------------------------------------------------------------------
# the GUI
# ---------------------------------------------------------------------------
DOCS = [
    ("WALKTHROUGH — zero to first success (start here)", ROOT / "WALKTHROUGH.md"),
    ("GETTING-STARTED — install on your OS", ROOT / "GETTING-STARTED.md"),
    ("README — the toolbox overview", ROOT / "README.md"),
    ("SERVICES — or hire us to do it for you", ROOT / "SERVICES.md"),
]
LEGAL = [
    ("TERMS OF USE — the agreement (read once)", LEGAL_DIR / "TERMS-OF-USE.md"),
    ("DISCLAIMER — responsibilities & no-guarantees", LEGAL_DIR / "DISCLAIMER.md"),
    ("PRIVACY — what we collect (nothing)", LEGAL_DIR / "PRIVACY.md"),
    ("SCRAPING-101 — read before the scraper", LEGAL_DIR / "SCRAPING-101.md"),
    ("THIRD-PARTY NOTICES — licenses & bundling", LEGAL_DIR / "THIRD-PARTY-NOTICES.md"),
    ("LICENSE — MIT", LEGAL_DIR / "LICENSE"),
]


def launch_gui() -> None:
    import tkinter as tk
    from tkinter import scrolledtext, ttk

    root = tk.Tk()
    root.title("Mr T's DIY Toolbox")
    root.geometry("920x680")
    root.minsize(780, 580)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure("Big.TButton", font=("TkDefaultFont", 11, "bold"),
                    padding=8)

    header = ttk.Frame(root, padding=(14, 12, 14, 4))
    header.pack(fill="x")
    ttk.Label(header, text="Mr T's DIY Toolbox",
              font=("TkDefaultFont", 16, "bold")).pack(side="left")
    link = ttk.Label(header, text=SITE, foreground="#0a58ca",
                     cursor="hand2")
    link.pack(side="right")
    link.bind("<Button-1>", lambda _e: webbrowser.open(SITE))

    nb = ttk.Notebook(root, padding=8)
    nb.pack(fill="both", expand=True, padx=10, pady=8)

    consoles: dict[str, scrolledtext.ScrolledText] = {}
    stop_btns: dict[str, ttk.Button] = {}
    LAST_PROC: dict[str, subprocess.Popen] = {}
    q: "queue.Queue[tuple[str, str]]" = queue.Queue()

    def console(tab_key: str, frame):
        out = scrolledtext.ScrolledText(frame, height=14, state="disabled",
                                        font=("TkFixedFont", 9),
                                        background="#101418",
                                        foreground="#d8dee9")
        out.pack(fill="both", expand=True, pady=(8, 0))
        consoles[tab_key] = out
        return out

    def write(tab_key: str, line: str):
        out = consoles[tab_key]
        out.config(state="normal")
        out.insert("end", line + "\n")
        out.see("end")
        out.config(state="disabled")

    def poll_queue():
        try:
            while True:
                tab_key, line = q.get_nowait()
                write(tab_key, line)
        except queue.Empty:
            pass
        root.after(120, poll_queue)

    def spawn(tab_key: str, cmd: list[str], cwd: Path):
        proc = LAST_PROC.get(tab_key)
        if proc is not None and proc.poll() is None:
            write(tab_key, "[!] Already running — press Stop first.")
            return
        out = consoles[tab_key]
        out.config(state="normal")
        out.delete("1.0", "end")
        out.config(state="disabled")
        write(tab_key, "[*] Running: " + " ".join(cmd))

        def on_line(line):
            q.put((tab_key, line))

        def on_done(code):
            q.put((tab_key, f"{'[OK]' if code == 0 else '[exit ' + str(code) + ']'} finished."))

        def worker():
            try:
                p = subprocess.Popen(
                    cmd, cwd=str(cwd), stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, text=True, bufsize=1,
                    errors="replace")
                LAST_PROC[tab_key] = p
                assert p.stdout is not None
                for line in p.stdout:
                    on_line(line.rstrip("\n"))
                code = p.wait()
                on_done(code)
            except Exception as e:
                on_line(f"[!] {e.__class__.__name__}: {e}")
                on_done(1)

        threading.Thread(target=worker, daemon=True).start()

    def start_tool(tab_key: str, product_dir: Path, args: list[str]):
        script = product_dir / ("lead_scraper.py"
                                if product_dir == SCRAPER_DIR
                                else "outreach_runner.py")
        spawn(tab_key, [python_exe(), str(script), *args], product_dir)

    def stop(tab_key: str):
        proc = LAST_PROC.get(tab_key)
        if proc is not None and proc.poll() is None:
            proc.terminate()
            write(tab_key, "[!] Stopped by user.")

    def big(parent, text, cmd):
        ttk.Button(parent, text=text, command=cmd,
                   style="Big.TButton").pack(side="left", padx=(0, 10),
                                             pady=6, fill="x", expand=True)

    # ---- HOME tab ---------------------------------------------------------
    home = ttk.Frame(nb, padding=16)
    nb.add(home, text=" Home ")

    ttk.Label(home, text="Welcome! Three tools, one window, zero subscriptions.",
              font=("TkDefaultFont", 12)).pack(anchor="w")
    ttk.Label(home, text="Everything runs on YOUR machine. First time? "
                         "Start with Setup & Doctor — it installs and "
                         "connects everything.").pack(anchor="w", pady=(2, 12))

    row = ttk.Frame(home)
    row.pack(fill="x", pady=4)
    big(row, "① Lead Scraper", lambda: nb.select(2))
    big(row, "② AI Outreach", lambda: nb.select(3))
    big(row, "③ n8n Intake", lambda: nb.select(4))

    row2 = ttk.Frame(home)
    row2.pack(fill="x", pady=4)
    big(row2, "Setup & Doctor (check + install everything)",
        lambda: nb.select(1))
    big(row2, "Read the Walkthrough",
        lambda: show_text_viewer(root, "WALKTHROUGH",
                                 ROOT / "WALKTHROUGH.md"))

    status = tk.Text(home, height=9, font=("TkFixedFont", 9),
                     background="#f5f5f0", borderwidth=0, padx=10, pady=8)
    status.pack(fill="both", expand=True, pady=(12, 0))

    def refresh_status():
        status.config(state="normal")
        status.delete("1.0", "end")
        status.insert("end", "Environment check\n" + "-" * 44 + "\n")
        for line in env_status():
            status.insert("end", line + "\n")
        status.config(state="disabled")

    refresh_status()

    # ---- SETUP & DOCTOR tab -------------------------------------------------
    setup = ttk.Frame(nb, padding=14)
    nb.add(setup, text=" Setup & Doctor ")
    setup_rows: list[ttk.Frame] = []

    ttk.Label(setup, text="What your computer has, what it's missing, and "
                          "one-click fixes. Re-run after any change.",
              wraplength=800).pack(anchor="w", pady=(0, 8))

    def refresh_doctor():
        for w in setup_rows:
            for c in w.winfo_children():
                c.destroy()
        for i, (item, st, detail) in enumerate(doctor_report()):
            color = {"ok": "#1a7f37", "warn": "#9a6700",
                     "missing": "#cf222e", "info": "#57606a"}[st]
            lbl = ttk.Label(setup_rows[i],
                            text=f"{st.upper():8s} {item:32s} {detail}")
            lbl.pack(side="left")
            lbl.configure(foreground=color)
            add_fix_buttons(setup_rows[i], item, st)
        if "setup" in consoles:
            write("setup", "[*] Doctor re-run complete.")

    def add_fix_buttons(rowf, item, st):
        def btn(text, cmd):
            ttk.Button(rowf, text=text, padding=(6, 0)).pack(side="right",
                                                             padx=2)
            # bind command after pack via lambda wrapper
            rowf.winfo_children()[-1].configure(command=cmd)

        if "config" in item.lower() and st == "missing":
            d = SCRAPER_DIR if "Scraper" in item else OUTREACH_DIR
            btn("Create & edit", lambda: (ensure_config(d),
                                          open_in_editor(d / "config.yml"),
                                          refresh_doctor()))
        elif item.startswith("Ollama") and st == "missing":
            btn("Copy install command",
                lambda: copy_clip(f"Install Ollama:\n    {ollama_install_cmd()}\n"
                                  "    (run it in a Terminal, then re-run "
                                  "the Doctor)"))
            btn("ollama.com", lambda: open_url("https://ollama.com"))
        elif item.startswith("Ollama") and st == "warn":
            btn("Start Ollama", lambda: (start_ollama(), refresh_doctor()))
        elif item.startswith("Local AI model") and st == "missing":
            btn(f"Pull {LOCAL_MODEL}",
                lambda: (start_ollama(),
                         spawn("setup", ["ollama", "pull", LOCAL_MODEL],
                               ROOT)))
        elif item.startswith("Node.js") and st == "missing":
            btn("Copy install command",
                lambda: copy_clip(f"Install Node.js LTS:\n    {node_install_cmd()}\n"
                                  "    then re-run the Doctor"))
            btn("nodejs.org", lambda: open_url("https://nodejs.org"))

    def copy_clip(text: str):
        root.clipboard_clear()
        root.clipboard_append(text)
        write("setup", "[*] Copied to clipboard:\n" + text)
        write("setup", "    → paste it into a Terminal (Win: PowerShell, "
                       "Mac: Terminal.app), press Enter, then re-run the "
                       "Doctor.")

    for _ in range(len(doctor_report())):
        setup_rows.append(ttk.Frame(setup))
        setup_rows[-1].pack(fill="x", pady=2)
    refresh_doctor()

    bar = ttk.Frame(setup)
    bar.pack(fill="x", pady=(10, 4))
    ttk.Button(bar, text="Re-run the Doctor",
               command=refresh_doctor).pack(side="left", padx=(0, 8))
    ttk.Button(bar, text="Create BOTH configs & open them",
               command=lambda: first_time_configs()).pack(side="left",
                                                          padx=(0, 8))
    ttk.Button(bar, text="Launch n8n now",                command=lambda: (spawn("setup", ["npx", "--yes", "n8n"],
                                       N8N_DIR),
                                root.after(15000, lambda:
                                           open_url("http://localhost:5678")))
               ).pack(side="left", padx=(0, 8))
    ttk.Button(bar, text="Read the Walkthrough",
               command=lambda: show_text_viewer(root, "WALKTHROUGH",
                                                ROOT / "WALKTHROUGH.md")
               ).pack(side="left")

    def first_time_configs():
        made = []
        for d in (SCRAPER_DIR, OUTREACH_DIR):
            cfg, created = ensure_config(d)
            made.append(f"{'created' if created else 'found'} {cfg.name} "
                        f"in {d.name}")
            if created:
                open_in_editor(cfg)
        write("setup", "[*] " + "; ".join(made) +
              "\n    Edit + save each one (town/category; your name & "
              "business), then press 'Re-run the Doctor'.")
        refresh_doctor()

    console("setup", setup)
    write("setup", "[*] Welcome! This Doctor checks: Python, tkinter, "
                   "configs, Ollama + local AI model, Node.js for n8n.\n"
                   "    Red items are one click away from fixed.")

    # ---- SCRAPER tab ---------------------------------------------------------
    t1 = ttk.Frame(nb, padding=14)
    nb.add(t1, text=" 1 · Lead Scraper ")
    c1 = ttk.Frame(t1)
    c1.pack(fill="x")
    no_crawl = tk.BooleanVar(value=False)
    ttk.Checkbutton(c1, text="Skip website emails (--no-crawl, faster)",
                    variable=no_crawl).pack(side="left")
    b1 = ttk.Frame(t1)
    b1.pack(fill="x", pady=8)
    ttk.Button(b1, text="Edit config",
               command=lambda: (ensure_config(SCRAPER_DIR),
                                open_in_editor(SCRAPER_DIR / "config.yml"))
               ).pack(side="left", padx=(0, 8))
    ttk.Button(b1, text="Run scraper", style="Big.TButton",
               command=lambda: start_tool("scraper", SCRAPER_DIR,
                                          (["--no-crawl"]
                                           if no_crawl.get() else []))
               ).pack(side="left", padx=(0, 8))
    stop_btns["scraper"] = ttk.Button(b1, text="Stop",
                                      command=lambda: stop("scraper"))
    stop_btns["scraper"].pack(side="left", padx=(0, 8))
    ttk.Button(b1, text="Open leads.csv",
               command=lambda: (open_in_editor(SCRAPER_DIR / "leads.csv")
                                if (SCRAPER_DIR / "leads.csv").exists()
                                else write("scraper",
                                           "[!] No leads.csv yet — run "
                                           "the scraper first"))
               ).pack(side="left", padx=(0, 8))
    ttk.Button(b1, text="Open folder",
               command=lambda: open_folder(SCRAPER_DIR)).pack(side="left")
    console("scraper", t1)
    ttk.Label(t1, text="Output: leads.csv in 01-lead-scraper/. You are the "
                       "data controller — see the Legal tab "
                       "(SCRAPING-101) before your first run.")\
        .pack(anchor="w", pady=(6, 0))

    # ---- OUTREACH tab ----------------------------------------------------------
    t2 = ttk.Frame(nb, padding=14)
    nb.add(t2, text=" 2 · AI Outreach ")
    c2 = ttk.Frame(t2)
    c2.pack(fill="x")
    ttk.Label(c2, text="AI provider:").pack(side="left", padx=(0, 4))
    provider = tk.StringVar(value="free")
    ttk.Combobox(c2, textvariable=provider, width=10, state="readonly",
                 values=["free", "ollama", "no-ai"]).pack(side="left",
                                                          padx=(0, 14))
    ttk.Label(c2, text="Lead:").pack(side="left", padx=(0, 4))
    lead_mode = tk.StringVar(value="sample lead")
    ttk.Combobox(c2, textvariable=lead_mode, width=12, state="readonly",
                 values=["sample lead", "leads.csv row"]).pack(side="left",
                                                               padx=(0, 4))
    row_no = tk.StringVar(value="1")
    ttk.Spinbox(c2, from_=1, to=999, width=4,
                textvariable=row_no).pack(side="left")

    def outreach_args():
        a = []
        if provider.get() == "no-ai":
            a.append("--no-ai")
        if lead_mode.get() == "leads.csv row":
            a += ["--leads-csv", str(SCRAPER_DIR / "leads.csv"),
                  "--row", row_no.get()]
        else:
            a += ["--lead", "sample-lead.yml"]
        a.append("--save")
        return a

    b2 = ttk.Frame(t2)
    b2.pack(fill="x", pady=8)
    ttk.Button(b2, text="Edit config",
               command=lambda: (ensure_config(OUTREACH_DIR),
                                open_in_editor(OUTREACH_DIR / "config.yml"))
               ).pack(side="left", padx=(0, 8))
    ttk.Button(b2, text="Draft email", style="Big.TButton",
               command=lambda: start_tool("outreach", OUTREACH_DIR,
                                          outreach_args())
               ).pack(side="left", padx=(0, 8))
    stop_btns["outreach"] = ttk.Button(b2, text="Stop",
                                       command=lambda: stop("outreach"))
    stop_btns["outreach"].pack(side="left", padx=(0, 8))
    ttk.Button(b2, text="Open drafts folder",
               command=lambda: open_folder(OUTREACH_DIR / "drafts")
               ).pack(side="left", padx=(0, 8))
    console("outreach", t2)
    ttk.Label(t2, text="Drafts only — it never sends. Review, paste into "
                       "YOUR mail client, send as YOU.\n'free' = no signup "
                       "· 'ollama' = fully private (local AI) · 'no-ai' = "
                       "plain templates. Model availability is checked "
                       "live every run.")\
        .pack(anchor="w", pady=(6, 0))

    # ---- n8n tab -----------------------------------------------------------
    t3 = ttk.Frame(nb, padding=14)
    nb.add(t3, text=" 3 · n8n Intake ")
    ttk.Label(t3, text="The blueprint is a file you import into n8n "
                       "(free). Three steps:\n"
                       "1) Install n8n (Setup tab can launch it)  "
                       "2) Import one-page-site-intake.json  "
                       "3) Follow SETUP.md",
              justify="left").pack(anchor="w")
    b3 = ttk.Frame(t3)
    b3.pack(fill="x", pady=10)
    ttk.Button(b3, text="Read SETUP.md (step by step)",
               command=lambda: show_text_viewer(root, "SETUP",
                                                N8N_DIR / "SETUP.md")
               ).pack(side="left", padx=(0, 8))
    ttk.Button(b3, text="Open blueprint folder",
               command=lambda: open_folder(N8N_DIR)).pack(side="left",
                                                          padx=(0, 8))
    ttk.Button(b3, text="Launch n8n",
               command=lambda: nb.select(1)).pack(side="left", padx=(0, 8))
    ttk.Button(b3, text="n8n website",
               command=lambda: open_url("https://n8n.io")).pack(side="left")
    console("n8n", t3)

    # ---- DOCS & LEGAL tab -----------------------------------------------------
    t4 = ttk.Frame(nb, padding=14)
    nb.add(t4, text=" Docs & Legal ")

    def doc_buttons(parent, items, label):
        lf = ttk.Labelframe(parent, text=label, padding=8)
        lf.pack(fill="x", pady=6)
        inner = ttk.Frame(lf)
        inner.pack(fill="x")
        col = 0
        for text, path in items:
            if not Path(path).exists():
                continue
            ttk.Button(inner, text=text, width=44,
                       command=lambda p=Path(path), t=text:
                       show_text_viewer(root, t.split(" — ")[0], p)
                       ).grid(row=col // 2, column=col % 2, sticky="we",
                              padx=4, pady=3)
            col += 1
        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(1, weight=1)

    doc_buttons(t4, DOCS, "Guides & reading")
    doc_buttons(t4, LEGAL, "Legal & licenses (read once — it protects you)")
    ttk.Label(t4, text="Plain-English deal: the tools are MIT and yours; "
                       "you are the operator; disputes go to binding "
                       "arbitration; the most we could ever owe is a "
                       "refund of the purchase price.",
              wraplength=780).pack(anchor="w", pady=(10, 0))
    site_lbl = ttk.Label(t4, text="Custom setup or 'just do it for me': "
                                  + SITE, foreground="#0a58ca",
                         cursor="hand2")
    site_lbl.pack(anchor="w", pady=(4, 0))
    site_lbl.bind("<Button-1>", lambda _e: webbrowser.open(SITE))

    # stop-button state watcher
    def watch_procs():
        for key, btn in stop_btns.items():
            proc = LAST_PROC.get(key)
            running = proc is not None and proc.poll() is None
            btn.config(state="normal" if running else "disabled")
        root.after(500, watch_procs)

    watch_procs()

    def on_close():
        for proc in LAST_PROC.values():
            try:
                if proc.poll() is None:
                    proc.terminate()
            except Exception:
                pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    # FIRST RUN: nothing configured yet? Drop the user on the Doctor.
    first_run = not (SCRAPER_DIR / "config.yml").exists() and \
        not (OUTREACH_DIR / "config.yml").exists()
    if first_run:
        nb.select(1)

    poll_queue()
    root.mainloop()


# ---------------------------------------------------------------------------
# CLI fallback (no tkinter) — same powers, numbered menu
# ---------------------------------------------------------------------------
def run_and_stream(product_dir: Path, args: list[str]) -> None:
    done = threading.Event()
    run_tool(product_dir, args, on_line=lambda l: log(l),
             on_done=lambda c: (log(f"\n[exit {c}]"), done.set()))
    done.wait()


def print_doctor() -> None:
    log("\nSETUP DOCTOR — what your machine has and what it's missing")
    log("-" * 62)
    for item, status, detail in doctor_report():
        log(f"  [{status:7s}] {item:30s} {detail}")
    log("-" * 62)
    if any(s == "missing" and "Ollama" in i for i, s, _ in doctor_report()):
        log(f"  Ollama install  : {ollama_install_cmd()}")
    if any(s == "missing" and "Node.js" in i for i, s, _ in doctor_report()):
        log(f"  Node.js install : {node_install_cmd()}")
    log("")


def launch_cli() -> None:
    first_run = not (SCRAPER_DIR / "config.yml").exists()
    if first_run:
        print_doctor()
        log("First run detected. Suggested order:")
        log("  12) run the doctor fix-ups  →  3) edit scraper config  →  1) run it")
    while True:
        log("\n" + "=" * 58)
        log("Mr T's DIY Toolbox — text menu")
        log("=" * 58)
        log("""
   1) Run the LEAD SCRAPER
   2) Scraper, skipping website emails (faster)
   3) Edit scraper config
   4) Open leads.csv
   5) DRAFT outreach email (sample lead, free AI)
   6) DRAFT outreach email (no-AI template)
   7) Edit outreach config
   8) Open drafts folder
   9) Start local AI (Ollama) + pull model
  10) Launch n8n (intake automation)
  11) Read WALKTHROUGH
  12) SETUP DOCTOR (check dependencies & get install commands)
  13) Open LEGAL pack (terms, privacy, disclaimer, scraping-101)
   0) Quit""")
        choice = input("\nChoose a number: ").strip()
        try:
            if choice == "1":
                run_and_stream(SCRAPER_DIR, [])
            elif choice == "2":
                run_and_stream(SCRAPER_DIR, ["--no-crawl"])
            elif choice == "3":
                open_in_editor(ensure_config(SCRAPER_DIR)[0])
            elif choice == "4":
                open_in_editor(SCRAPER_DIR / "leads.csv")
            elif choice == "5":
                run_and_stream(OUTREACH_DIR,
                               ["--lead", "sample-lead.yml", "--save"])
            elif choice == "6":
                run_and_stream(OUTREACH_DIR,
                               ["--lead", "sample-lead.yml", "--save",
                                "--no-ai"])
            elif choice == "7":
                open_in_editor(ensure_config(OUTREACH_DIR)[0])
            elif choice == "8":
                open_folder(OUTREACH_DIR / "drafts")
            elif choice == "9":
                start_ollama()
                if ollama_installed():
                    done = threading.Event()
                    run_stream(["ollama", "pull", LOCAL_MODEL], ROOT,
                               on_line=lambda l: log(l),
                               on_done=lambda c: done.set())
                    done.wait()
            elif choice == "10":
                launch_n8n()
            elif choice == "11":
                open_in_editor(ROOT / "WALKTHROUGH.md")
            elif choice == "12":
                print_doctor()
            elif choice == "13":
                for f in ("TERMS-OF-USE.md", "DISCLAIMER.md", "PRIVACY.md",
                          "SCRAPING-101.md", "THIRD-PARTY-NOTICES.md",
                          "LICENSE"):
                    p = LEGAL_DIR / f
                    if p.exists():
                        open_in_editor(p)
                log("[*] Opened all legal files in your editor.")
            elif choice == "0":
                return
            else:
                log("[!] Pick a number from the list.")
        except KeyboardInterrupt:
            return


def main() -> None:
    if "--check" in sys.argv:
        for line in env_status():
            log(line)
        return
    if "--doctor" in sys.argv:
        print_doctor()
        return
    if "--cli" in sys.argv:
        launch_cli()
        return
    try:
        launch_gui()
    except ImportError:
        log("[*] tkinter not available — using the text menu instead "
            "(Linux tip: install 'python3-tk' for the GUI).")
        launch_cli()
    except KeyboardInterrupt:
        log("\n[!] Bye.")


if __name__ == "__main__":
    main()
