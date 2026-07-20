# 🍅 Focus Timer

A compact Pomodoro desktop widget built with Python and PySide6 (Qt).

Long work sessions easily dissolve into distraction. Focus Timer is one
small, dark, always-optional window: start a focused session, optionally
play a local concentration playlist, and take regular breaks — no
accounts, no cloud, no dashboards.

**Currently available for Linux only.** Windows packaging is planned but
not yet built (no Windows machine to build/test it on).

## Features

- Classic Pomodoro (25/5/15 min) or a fully custom cycle (durations,
  session count, end action)
- Pause, reset, skip, with an accurate deadline-based timer that never
  drifts
- Local alarm sound and desktop notifications on phase completion
- Collapsible local music player: pick a folder, play its `.mp3` files
  as a concentration playlist, auto-play on focus / auto-pause on break
- All preferences saved locally and restored on restart
- Keyboard shortcuts: `Space` start/pause, `R` reset, `S` skip

## Install (Linux, .deb)

```bash
sudo dpkg -i focus-timer_<version>_amd64.deb
```

Then launch **Focus Timer** from your applications menu, or run
`focus-timer` from a terminal.

The music player needs an external audio player installed —
`ffplay` (from `ffmpeg`) or `cvlc` (from VLC), whichever is already on
your system. Desktop notifications use `notify-send`
(`libnotify-bin`); the alarm sound uses `paplay` or `aplay`
(`pulseaudio-utils`/`alsa-utils`). None of these are hard requirements —
Focus Timer keeps working without them, just without that feature.

To build the `.deb` yourself from source:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash packaging/build_deb.sh
```

This produces `dist/focus-timer_<version>_amd64.deb`.

## Running from source (development)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

Tests: `pytest`. Lint: `ruff check .`. Format check: `ruff format --check .`.

See `context/project-overview.md` and `context/coding-standards.md` for
the full project specification and conventions.
