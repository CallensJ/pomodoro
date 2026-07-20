# Current Feature

## Feature Name

Pomodoro MVP with optional YouTube concentration playlist

## Status

In Progress — MVP4 (YouTube Concentration Player) complete, ready for MVP5.

## MVP Roadmap

Work is split into sequential MVPs, each gated by a success-criteria
checklist. Full checklists live in the approved plan; this section tracks
status only.

- [x] MVP0 — Project Initialization (`chore/project-init`)
- [x] MVP1 — Domain Timer Core (`feature/domain-timer`)
- [x] MVP2 — Application Shell + Working Timer UI (`feature/timer-shell`)
- [x] MVP3 — Alarm, Notifications, Settings Persistence (`feature/alarm-settings`)
- [x] MVP4 — YouTube Concentration Player (`feature/youtube-player`)
- [ ] MVP5 — Final Verification & Definition of Done (`chore/final-verification`)

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

### Priority 4 — YouTube Player

- [x] Add a field for a YouTube video or playlist URL
- [x] Validate and convert supported URLs to official embed URLs
- [x] Load the result in a collapsible `QWebEngineView`
- [x] Start/resume playback for focus sessions when permitted
- [x] Pause playback when the timer pauses or a break starts
- [x] Preserve manual player controls
- [x] Handle offline, invalid and embedding-disabled cases without crashing
- [x] Save the last valid URL

### Priority 5 — Verification

- [ ] Test URL parsing and phase transitions
- [ ] Run `pytest`
- [ ] Run `ruff check .`
- [ ] Run `ruff format --check .`
- [ ] Review file sizes, function sizes and responsibility boundaries
- [ ] Confirm domain tests run without creating Qt widgets
- [ ] Manually complete a shortened focus/break cycle
- [ ] Manually verify the app on Linux and Windows

## Acceptance Criteria

- A user can complete a full Pomodoro cycle without reopening the app
- Pause/resume does not lose or add time
- Reset and skip follow the documented timer rules
- Alarm or YouTube failure never stops timer operation
- Valid video and playlist URLs open in the embedded player
- Music stops during pauses and breaks where the player API allows it
- Invalid URLs display a clear error
- Preferences survive restart
- Domain rules remain independent from widgets, audio, settings and YouTube
- No handwritten Python module exceeds 300 lines without documented justification

## Notes

- Packaging with PyInstaller is a separate feature after MVP validation.
- `QtWebEngine` increases installation and executable size substantially.
- YouTube autoplay may require one initial user interaction.
- Some videos and playlists cannot be embedded due to owner or regional rules.
- If automated playback is unreliable, keep the embedded manual controls and
  record player automation as deferred rather than delaying the timer MVP.

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
