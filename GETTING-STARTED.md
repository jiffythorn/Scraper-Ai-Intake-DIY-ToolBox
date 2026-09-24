# GETTING-STARTED — From Download to First Win (any OS)

Everything here is plain Python, plain markdown, and plain JSON. No
compilers, no build step, no accounts with us. Pick your path:

## OS Support Matrix (honest version)

| OS | Scraper (01) | Outreach (02) | Toolbox GUI | n8n Intake (03) |
|---|---|---|---|---|
| Windows 10/11 | ✅ | ✅ | ✅ (tkinter included) | ✅ via Node or Docker |
| macOS 12+ | ✅ | ✅ | ✅ | ✅ |
| Linux | ✅ | ✅ | ✅¹ | ✅ |
| ChromeOS | ✅ (Linux env) | ✅ | ✅¹ | ✅ |
| Android (Termux) | ✅ | ✅ | text menu only | ⚠️ painful |
| iOS / iPadOS | ❌ | ❌ | ❌ | ❌ — no real Python; use the [services route](https://www.mrtscomputers.com) |
| Windows 7/8 | ⚠️ needs old Python 3.8 | ⚠️ | ⚠️ | ⚠️ |

¹ Most Linux distros need the `python3-tk` package for the GUI
(`sudo apt install python3-tk`); without it, `toolbox.py` automatically
falls back to an identical text menu.

**Want zero-install executables** (no Python needed at all)? See
[`packaging/README.md`](packaging/README.md) — one-command PyInstaller
builds per OS.

---

## Windows 10/11

**Easiest — double-click:**
1. Unzip the download anywhere (e.g., `C:\Tools\mrts-toolbox`).
2. Open the `01-lead-scraper` folder.
3. Double-click **`run_windows.bat`** — first run creates your
   `config.yml` and opens it in Notepad for you to edit; save, and the
   scraper runs.

**Need Python?** Install from <https://www.python.org/downloads/> — during
setup, tick **"Add python.exe to PATH"**. That's the only checkbox that
matters. Windows 10/11 also offers Python via the Microsoft Store
(`python` command will offer to install it).

## macOS

1. Unzip anywhere. Open **Terminal** (⌘-Space, type "terminal").
2. `python3 --version` — macOS ships Python 3; if it's missing, the
   command offers the developer tools install, or grab it from
   <https://www.python.org/downloads/>.
3. ```bash
   cd Downloads/mrts-toolbox/01-lead-scraper
   ./run_mac_linux.sh
   ```
   (First run creates your `config.yml`; edit, save, re-run.)

If `./run_mac_linux.sh` complains about permissions:
`chmod +x run_mac_linux.sh` — once, ever.

## Linux

```bash
cd mrts-toolbox/01-lead-scraper
./run_mac_linux.sh
```
Python 3.9+ is already on virtually every distro. Done.

## ChromeOS / Android / iPad

The scraper and outreach runner are single files — they'll run anywhere
Python runs, including Termux (Android). On a Chromebook, enable the Linux
environment (Settings → Developers) and follow the Linux steps. On iPad,
use a Python IDE app that can run local scripts — or, honestly, let us
[run it for you](https://www.mrtscomputers.com).

## The n8n Blueprint (all OSes)

n8n itself runs on Windows/macOS/Linux via Node.js or Docker (see
[03-n8n-intake-blueprint/SETUP.md](03-n8n-intake-blueprint/SETUP.md) —
Option A is a single `npx --yes n8n` command). The blueprint JSON imports the
same on every OS.

## Local AI (optional, outreach pack)

[Ollama](https://ollama.com) has one-click installers for Windows, macOS,
and Linux. Then: `ollama pull llama3.1:8b`. No Ollama? `--no-ai` mode and
the keyless `provider: free` still work everywhere Python does.

## Which Python version?

Anything ≥ 3.9 (2020). The tools detect what they need and tell you in
plain English if something's missing. Check yours: `python3 --version`
(or `python --version` on Windows).

## Privacy recap (30 seconds)

Everything runs on **your** machine. No telemetry, no accounts with us,
nothing phones home. When you *choose* cloud/free AI providers, that's your
data going to *those* services — see
[legal/PRIVACY.md](legal/PRIVACY.md) and
[legal/DISCLAIMER.md](legal/DISCLAIMER.md).

---

**Stuck on any step? That's our favorite kind of problem —
[MrTsComputers.com](https://www.mrtscomputers.com)**
