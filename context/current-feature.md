# Current Feature

## Feature Name

Pomodoro MVP with optional local music concentration playlist

## Status

MVP0–MVP5 complete. The original YouTube Concentration Player (MVP4) was
replaced post-MVP5 with a Local Music Player after the YouTube embed proved
non-functional on real hardware, not just the sandbox — see History for the
full diagnosis and the pivot. A Linux `.deb` package is now available
(`packaging/build_deb.sh`); Windows packaging and general Windows
verification remain open follow-ups.

## MVP Roadmap

Work is split into sequential MVPs, each gated by a success-criteria
checklist. Full checklists live in the approved plan; this section tracks
status only.

- [x] MVP0 — Project Initialization (`chore/project-init`)
- [x] MVP1 — Domain Timer Core (`feature/domain-timer`)
- [x] MVP2 — Application Shell + Working Timer UI (`feature/timer-shell`)
- [x] MVP3 — Alarm, Notifications, Settings Persistence (`feature/alarm-settings`)
- [x] MVP4 — YouTube Concentration Player (`feature/youtube-player`)
- [x] MVP5 — Final Verification & Definition of Done (`chore/final-verification`)

## Goals

Implement the smallest useful cross-platform desktop application.

### Priority 1 — Application Shell

- [x] Create the documented project structure
- [x] Keep domain, application, infrastructure and presentation separated
- [x] Wire dependencies explicitly in `main.py`
- [x] Add PySide6, PySide6-WebEngine, pytest, pytest-qt and Ruff dependencies
- [x] Create a compact dark main window
- [x] Display current phase, remaining time, task and session count

### Priority 2 — Timer

- [x] Implement `FOCUS`, `SHORT_BREAK` and `LONG_BREAK` phases
- [x] Use a monotonic deadline to avoid timer drift
- [x] Implement start, pause/resume, reset and skip
- [x] Increment the counter only after a completed focus session
- [x] Select a long break after four completed focus sessions
- [x] Add Space, R and S keyboard shortcuts

### Priority 3 — Alarm and Settings

- [x] Play a bundled local alarm when a phase ends
- [x] Attempt a desktop notification without blocking the timer
- [x] Store durations and preferences with `QSettings`
- [x] Add alarm, auto-start and always-on-top options

### Priority 4 — Local Music Player

- [x] Let the user choose a local folder as the concentration playlist
- [x] Scan the folder (non-recursive) for `.mp3` files
- [x] Play back via a non-blocking OS-native player (not QtMultimedia)
- [x] Playback is fully manual and independent of the timer (no auto
      start/pause tied to timer phase or status)
- [x] Auto-advance on natural track completion (wrapping after the last
      track), plus a manual Next control
- [x] Preserve manual player controls (collapsible, Play/Pause/Next)
- [x] Handle "no mp3 files" and "no audio player installed" cases without
      crashing
- [x] Save the last selected folder

### Priority 5 — Verification

- [x] Test URL parsing and phase transitions
- [x] Run `pytest`
- [x] Run `ruff check .`
- [x] Run `ruff format --check .`
- [x] Review file sizes, function sizes and responsibility boundaries
- [x] Confirm domain tests run without creating Qt widgets
- [x] Manually complete a shortened focus/break cycle
- [x] Manually verify the app on Linux (Windows: pending, no environment available here)

## Acceptance Criteria

- A user can complete a full Pomodoro cycle without reopening the app
- Pause/resume does not lose or add time
- Reset and skip follow the documented timer rules
- Alarm or music playback failure never stops timer operation
- A chosen folder's `.mp3` files play back through the player
- Music pauses during timer pauses and breaks, resumes on focus
- A folder with no mp3 files, or no supported player installed, displays a
  clear error
- Preferences survive restart
- Domain rules remain independent from widgets, audio, settings and the
  music player
- No handwritten Python module exceeds 300 lines without documented justification

## Notes

- Packaging with PyInstaller is a separate feature after MVP validation.
- The music player relies on an external OS player (`ffplay`/`cvlc` on
  Linux) being installed; if none is found, the app shows a clear inline
  message and the timer keeps working normally.
- `PySide6-Addons` (QtWebEngine/QtMultimedia) is no longer a dependency —
  dropped when the YouTube player was replaced, shrinking the install
  significantly.

## History

- Project documentation initialized
- MVP scope defined
- YouTube playlist support added to the specification
- Agile MVP roadmap (MVP0–MVP5) planned and approved
- MVP0 complete: git repo initialized, remote `origin` set to
  `https://github.com/CallensJ/pomodoro.git`, documented folder structure
  created, dependencies pinned to Python 3.14-compatible versions
  (PySide6 6.10.3) and installed, `ruff check`, `ruff format --check` and
  `pytest` all run clean
- MVP1 complete: `src/domain/timer_state.py` (`Phase`, `TimerStatus`,
  `EndAction`, `CycleConfig` with a `classic()` preset) and
  `src/domain/timer.py` (`PomodoroTimer`, pure Python, injectable monotonic
  clock, no Qt) implement all ten documented timer rules for both Classic
  and Custom cycles. 16 unit tests cover start/pause/resume accuracy,
  session counting, classic long-break-then-repeat behavior, all three
  custom end actions (stop, long break, repeat), reset, skip semantics and
  invalid-config validation. `pytest`, `ruff check` and `ruff format --check`
  all pass
- MVP2 complete: `src/application/timer_controller.py` (`TimerController`)
  wires `PomodoroTimer` to a `QTimer` refresh loop and exposes
  `phase_changed`/`status_changed`/`remaining_changed`/`session_changed`
  signals; `src/presentation/main_window.py` (`MainWindow`) renders a
  compact 340x430 dark window (`src/presentation/styles.qss`) with phase,
  countdown, session counter, task input, start/pause/reset/skip controls,
  and Space/R/S shortcuts guarded so typing in the task field never
  triggers them; `src/main.py` wires the layers explicitly. Verified by
  launching the real app (screenshots of idle and running states) and by
  a `QTest`-driven script confirming all three shortcuts and the
  focus-guard behavior. 24 automated tests (8 new) pass, including
  pytest-qt controller and widget tests; `ruff check` and
  `ruff format --check` pass
- MVP3 complete: `src/infrastructure/audio_player.py` (`AudioPlayer`, using
  `QSoundEffect`, plays a locally synthesized `assets/alarm.wav`, no
  external download); `src/infrastructure/notification_service.py`
  (`NotificationService`, non-blocking `subprocess.Popen`, `notify-send` on
  Linux and a PowerShell `NotifyIcon` balloon tip on Windows, best-effort
  and always caught); `src/infrastructure/settings_store.py`
  (`SettingsStore`, single `QSettings` wrapper for cycle config, alarm
  enabled, auto-start-next-phase, always-on-top); `TimerMode` enum added to
  `domain/timer_state.py`. `TimerController` gained optional
  `alarm_player`/`notifier`/`settings` collaborators (via small `Protocol`
  seams, keeping infrastructure out of the application layer) and now
  fires the alarm/notification only on natural phase completion (never on
  skip), auto-starts the next phase when enabled, and exposes
  `apply_new_config()`. `src/presentation/settings_dialog.py`
  (`SettingsDialog`) edits mode/durations/end action/toggles, validates
  before accepting, and a "Restore Classic Defaults" action. `MainWindow`
  gained a settings button and `set_always_on_top()`. Verified by driving
  the real running app end-to-end (open settings → switch to Custom →
  edit fields → save → confirm the live window/controller picks up the
  new 40 min/2-session config and always-on-top flag), with screenshots.
  47 automated tests pass (23 new); `ruff check` and `ruff format --check`
  pass. Windows notification path is implemented per documented behavior
  but unverified on real Windows (no Windows environment available here)
- MVP4 complete: `src/infrastructure/youtube_url.py` (`parse_youtube_url`)
  parses/validates `youtube.com` (watch, playlist, embed, www/m subdomains)
  and `youtu.be` URLs with `urllib.parse` (no monolithic regex), rejects
  host-spoofing attempts (e.g. `youtube.com.evil.com`) and malformed IDs,
  and normalizes to official `/embed/` URLs — 18 unit tests, no network
  calls. `src/presentation/youtube_player.py` (`YoutubePlayerWidget`) is a
  collapsible widget (collapsed by default) hosting a small local HTML
  page that loads the official YouTube IFrame Player API
  (`new YT.Player(...)`), giving real `playVideo()`/`pauseVideo()` control
  and an `onError` handler mapped to friendly messages; a token-guarded
  ready-check timeout (8s) reports a clear error for offline/never-loads
  cases without crashing. `MainWindow` wires `play()`/`pause()` to
  focus-running vs. paused/break states, persists the last valid URL via
  `SettingsStore.last_youtube_url()`, and restores/loads it on startup.
  80 automated tests pass in total (33 new); `ruff check` and
  `ruff format --check` pass.
  **Environment note:** verified end-to-end against the real app with a
  real display and real network access (confirmed `youtube.com`/`ytimg.com`
  reachable). URL parsing, error handling, collapse/expand, settings
  persistence and play/pause wiring all work correctly, including as
  observed live in this sandbox. Actual video rendering itself was
  rejected by YouTube (`Error 152/153: Video player configuration error`)
  specifically in this sandboxed QtWebEngine (Chromium 134) environment —
  confirmed independent of app code by testing three approaches (IFrame
  API wrapper, `origin` playerVar, raw embed URL with a standard desktop
  User-Agent override), all hitting the same YouTube-side rejection. The
  app degrades exactly as the spec requires: our own inline error message
  shows, the timer keeps running, and YouTube's own fallback overlay
  (with a "Watch video on YouTube" link) remains available inside the
  frame as a manual fallback. This should be re-verified on a real
  Linux/Windows desktop outside this sandbox before considering YouTube
  playback fully confirmed.
- MVP5 complete: full verification pass against the Definition of Done.
  File/function-size and responsibility review: no module exceeds 200
  lines (well under the 300-line limit), domain has zero Qt imports,
  `youtube_url.py` and `notification_service.py` have zero Qt dependency,
  `settings_dialog.py`'s `_build_ui` (53 lines) was split into
  `_build_cycle_fields`/`_build_toggle_fields`/`_build_actions`, and
  `youtube_player.py`'s HTML builder had its config-building logic
  extracted into `_build_player_config`. Manually verified end-to-end on
  Linux: a full classic-shaped cycle (focus → short break → focus → long
  break → repeat, session counter wrapping correctly), the documented
  custom `2×40min/10min break/stop` cycle, pause holding remaining time
  exactly across a real delay, resume continuing without gain/loss, skip
  not counting the session, and a deliberate-delay drift test showing
  0.0000s drift (confirming `remaining_seconds()` is deadline-based, not
  tick-counted). Preferences (cycle config, alarm, auto-start,
  always-on-top, last YouTube URL) verified to survive an actual process
  restart (two separate process launches sharing one `QSettings` file).
  **Critical fix found during verification:** `AudioPlayer` originally
  used `QSoundEffect` (QtMultimedia); on this machine's audio stack
  (PipeWire/PipeWire-Pulse) `QSoundEffect()` construction was found to
  block the calling thread for 15+ seconds — a direct violation of "never
  block the UI thread" and a risk of freezing the app on every phase
  completion. Reproduced independently three times, isolated to
  `QSoundEffect` construction specifically. Rewrote `AudioPlayer` to use
  non-blocking OS-native playback instead (Linux: `paplay`/`aplay` via
  `subprocess.Popen`, fire-and-forget; Windows: stdlib
  `winsound.PlaySound(..., SND_ASYNC)`), mirroring the already-reliable
  `NotificationService` pattern — construction dropped to ~0.02s and
  `play_alarm()` returns in ~0.001s. Alarm + real desktop notification
  reverified firing correctly at natural phase completion after the fix.
  Tests rewritten accordingly (no longer need a `QApplication`/`qapp`
  fixture at all). 83 automated tests pass; `ruff check` and
  `ruff format --check` pass. Windows launch/behavior remains unverified
  (no Windows environment available in this sandbox) — flagged as a
  follow-up for the user to confirm on a real Windows machine.
- **YouTube player replaced with a Local Music Player.** The user tested
  the app on their own real desktop and hit the same "Error 152/153: Video
  player configuration error" I'd seen in the sandbox — meaning it was not
  a sandbox artifact as I'd concluded in the MVP4 entry above. Re-diagnosed
  from scratch: queried the bundled Chromium's actual codec support via
  `canPlayType()` and found **H.264 and AAC are unsupported**, while
  VP9/VP8/Opus/AV1 all work — PySide6's official pip wheels ship
  QtWebEngine without the patent-licensed codecs. Confirmed this is
  specific to YouTube's embedded `/embed/` player (which doesn't fall back
  to VP9) by loading the regular `youtube.com/watch` page in the same
  browser, which rendered without error. This is a dependency/licensing
  limitation, not fixable in app code. The user asked to replace YouTube
  entirely with a local-folder MP3 player. While investigating the
  replacement, found `QMediaPlayer`/`QAudioOutput` (QtMultimedia) hang
  identically to the `QSoundEffect` bug fixed in MVP5 — QtMultimedia is
  unreliable on this audio stack entirely, confirmed by direct test.
  Removed `youtube_url.py`/`youtube_player.py` and their tests; added
  `src/infrastructure/music_library.py` (pure `scan_mp3_files()`, non-
  recursive, sorted) and `src/infrastructure/local_music_player.py`
  (`LocalMusicPlayer`, non-blocking OS-native playback — `QProcess`
  running `ffplay`/`cvlc` on Linux, paused/resumed via `SIGSTOP`/`SIGCONT`
  on the process PID, verified live that a suspended process survives and
  resumes cleanly; Windows uses `ctypes` + `winmm.dll` MCI commands with a
  1s poll for natural-completion detection — untestable here, structure
  verified via mocked unit tests only). Added
  `src/presentation/music_player_widget.py` (`MusicPlayerWidget`,
  collapsible, folder picker, Play/Pause/Next, auto-advance with wrap,
  inline errors) replacing `YoutubePlayerWidget` with the same public
  shape `MainWindow` already wires to (`play()`/`pause()`,
  `collapsed_changed`). `SettingsStore.last_youtube_url()` replaced with
  `last_music_folder()`. Dropped `PySide6-Addons` from `requirements.txt`
  entirely (nothing uses QtWebEngine or QtMultimedia anymore) and verified
  the app runs correctly with it uninstalled. Verified end-to-end with
  real generated MP3s and the real app: folder scan, auto-play on focus
  start, pause via `SIGSTOP` (confirmed via `ps` showing process state
  `T`), resume via `SIGCONT` (state back to `S`), manual Next, natural
  track-finish auto-advance with wrap-around, and folder persisted across
  a real two-process restart — all observed directly, not just asserted
  in tests. 84 automated tests pass; `ruff check` and `ruff format --check`
  pass. Windows MCI playback path remains unverified on a real Windows
  machine, same open follow-up as the rest of the Windows-specific code.
- **Linux `.deb` packaging added.** The app previously only ran via
  `python -m src.main` from an activated venv — not click-to-launch, and
  packaging was already documented as a post-MVP step. Scope: `.deb`
  only, no Windows `.exe` (the user has no Windows machine to build/test
  one on, and PyInstaller can't reliably cross-compile a Windows binary
  from Linux). Added `packaging/focus-timer.spec` (PyInstaller `--onedir`
  build — faster launch than `--onefile`, no per-run unpack to a temp
  dir), `packaging/build_deb.sh` (assembles a `/opt/focus-timer` +
  `/usr/bin` symlink + `.desktop` entry + icon layout, then
  `dpkg-deb --build`), `packaging/focus-timer.desktop`, and
  `packaging/icon.png` (the user's provided `pomodoro.png`, resized from
  1254×1254 to the standard 256×256). Added a top-level `VERSION` file
  (`0.1.0`) as the single source of truth for both the PyInstaller build
  and the Debian control file. Along the way, found and fixed a real
  bundling bug: `AudioPlayer.DEFAULT_ALARM_PATH` and `main.py`'s
  `STYLES_PATH` both derived their location from `Path(__file__)`, which
  doesn't reliably resolve the same way once bundled — made both
  frozen-aware (`sys._MEIPASS` when `sys.frozen`, unchanged behavior
  otherwise) and added `alarm.wav`/`styles.qss` to the PyInstaller
  `datas`. Verified by actually running the built binary directly out of
  `dist/focus-timer/` (not just inspecting `dpkg-deb --contents`) against
  the user's real desktop — dark theme rendered correctly, and the music
  player picked up the user's real `~/Music` folder and played a real
  track. **Note on verification method:** discovered mid-session that
  `DISPLAY=:0` in this environment is the user's actual live desktop, not
  an isolated sandbox as earlier assumed (explains why the MVP4 YouTube
  codec issue reproduced identically for the user, rather than being
  sandbox-specific as first concluded) — a full-screen screenshot taken
  during this verification was deleted immediately since it captured more
  of the user's screen than intended; window-only or log-based
  verification is used from here on. Did not run `sudo dpkg -i` on the
  user's real system — they explicitly asked to install it themselves.
  Deliverable: `dist/focus-timer_0.1.0_amd64.deb` (not committed to git;
  `dist/`, `build/` and `packaging/staging/` are gitignored — only the
  packaging *source* is tracked, so the build is reproducible via
  `bash packaging/build_deb.sh`). Added top-level `README.md` (didn't
  exist before) covering install and running from source.
- **Music player decoupled from the timer.** The user reported that
  starting a focus session auto-started music playback with no way to
  stop just the music without stopping the timer — `MainWindow` had a
  `_sync_player_playback` handler wired to both `controller.phase_changed`
  and `controller.status_changed` that force-called `music_player.play()`/
  `pause()` on every timer transition, overriding any manual pause. This
  superseded the original spec's "start on focus, pause on break/pause"
  behavior with an explicit requirement that the player be 100%
  independent and optional. Removed `_sync_player_playback` and its
  signal connections entirely from `src/presentation/main_window.py`;
  the player now only responds to its own Play/Pause/Next controls,
  never to timer state. Updated `project-overview.md` and this file's
  Priority 4 checklist to describe the player as fully manual. Replaced
  `test_player_plays_when_focus_starts_and_pauses_on_pause` with
  `test_player_is_independent_of_timer_start_and_pause`, asserting the
  player receives zero play/pause calls across start/pause/reset. 84
  automated tests pass; `ruff check` and `ruff format --check` pass.
