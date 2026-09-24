# Packaging — build true double-click executables (optional)

The toolbox ships as plain, readable Python on purpose (open source means
*open*). But if you want **single-file executables** that run with NO
Python installed, this folder builds them with
[PyInstaller](https://pyinstaller.org).

## What you get

```
dist/
  Toolbox            (or Toolbox.exe)   ← one-stop GUI launcher
  lead_scraper       (or lead_scraper.exe)
  outreach_runner    (or outreach_runner.exe)
```

Buyers double-click `Toolbox` and everything else is one window: the
dependency doctor, launchers, configs, docs, and legal tabs.

## Build rules (read once)

- **Build ON the OS you target.** PyInstaller does not cross-compile:
  Windows build → run `build_windows.bat` on Windows; macOS/Linux build →
  run `./build_mac_linux.sh` on that OS. (For Mac distributions, building
  on the oldest Intel Mac you support gives the widest compatibility.)
- Everything stays MIT/open — PyInstaller is GPL-v2 with a special
  bootloader exception that permits commercial closed/app packaging of
  *your* code. You're shipping our MIT files plus Python runtime; no
  licensing trap. See `../legal/THIRD-PARTY-NOTICES.md`.
- macOS builds may need Gatekeeper approval: right-click the app → Open
  (unsigned binaries warn once). Proper code-signing/Apple-notarization
  is a service — https://www.mrtscomputers.com
- SmartScreen on Windows may warn on unsigned .exe the same way it warns
  on our .bat — buyers click "More info → Run anyway", or you sign it.

## One-time build prerequisites

PyInstaller needs Python + pip on the *build* machine only (buyers need
nothing):

```bash
python3 -m pip install --user pyinstaller
```

Then run the build script for your OS. Output lands in `dist/` — zip it,
sell it, ship it. The `*_source` folders stay for the MIT-source purists.
