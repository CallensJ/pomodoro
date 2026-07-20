# Focus Timer Project Specifications

🍅 A compact Pomodoro desktop widget for Linux and Windows, built entirely with
Python and Qt.

## Problem

Long development sessions easily dissolve into distraction. Most productivity
tools add accounts, dashboards and configuration before helping the user focus.

Focus Timer provides one small desktop window for starting a focused session,
listening to a YouTube concentration playlist and taking regular breaks.

## Primary User

A developer or remote worker who wants:

- a timer visible without occupying much screen space;
- minimal interaction between work sessions;
- optional background music;
- local settings with no account or cloud dependency.

## MVP Scope

### Timer Modes

**Classic Pomodoro** uses 25-minute focus sessions, 5-minute short breaks and a
15-minute long break after 4 completed sessions.

**Custom Cycle** configures focus and break durations, total focus sessions,
optional long-break duration and the end action: stop, long break or repeat.

Example: `2 × 40 minutes`, with a `10-minute` break between sessions, then stop.

Both modes provide:

- Start, pause/resume, reset and skip controls
- Remaining time, current phase and `session x/total` displayed
- Accurate elapsed-time calculation even if UI refreshes are delayed

Classic defaults must always be available through a reset action.

### Current Task

- Optional short text describing the task being worked on
- The current task remains visible below the timer
- Empty task text is allowed

### Alarm and Notifications

- Play a local sound when a phase ends
- Display a desktop notification when supported
- Allow sound to be enabled or disabled
- Allow automatic or manual start of the next phase
- Alarm failure must never break the timer cycle

### YouTube Concentration Player

- Accept a YouTube video or playlist URL
- Validate and normalize supported `youtube.com` and `youtu.be` URLs
- Embed playback inside the app with `QWebEngineView`
- Start or resume playback when a focus session starts
- Pause playback when the timer is paused or a break begins
- Keep the player optional and collapsible
- Store the last valid URL locally
- Show a useful error if a video cannot be embedded or the device is offline

The app must not download, scrape or bypass YouTube restrictions. Some videos
may disallow embedded playback. Manual player controls remain available.

### Local Preferences

Store with `QSettings`:

- focus, short-break and long-break durations;
- timer mode and total sessions;
- custom-cycle break duration and end action;
- alarm enabled;
- auto-start next phase;
- always-on-top preference;
- last valid YouTube URL.

## Out of Scope for MVP

- Accounts, authentication or cloud sync
- Statistics dashboard or calendar integration
- Website and application blocking
- Multiple themes or complex animations
- System tray behavior
- Auto-start with the operating system
- Database, telemetry or automatic updates
- YouTube downloading or audio extraction

## Timer Rules

1. The initial phase is `FOCUS` and the timer is stopped.
2. Starting creates a monotonic deadline; UI ticks only update the display.
3. Pausing stores the remaining duration and pauses YouTube playback.
4. A completed focus phase increments the session counter.
5. Intermediate focus sessions lead to the configured short/custom break.
6. At the cycle limit, the configured end action stops, starts a long break or repeats.
7. A completed intermediate break returns to the next focus session.
8. Reset restores the full duration of the current phase.
9. Skip changes phase without counting the skipped focus session as completed.
10. The displayed time never becomes negative.

## Architecture

Use a small layered architecture. Dependencies point inward: presentation and
infrastructure may depend on the application/domain, never the reverse.

```text
src/
├── main.py
├── domain/
│   ├── timer.py
│   └── timer_state.py
├── application/
│   └── timer_controller.py
├── infrastructure/
│   ├── settings_store.py
│   ├── audio_player.py
│   ├── notification_service.py
│   └── youtube_url.py
├── presentation/
│   ├── main_window.py
│   ├── settings_dialog.py
│   ├── youtube_player.py
│   └── styles.qss
└── assets/
    └── alarm.wav
tests/
requirements.txt
```

- `domain` contains timer state and phase-transition rules without Qt widgets.
- `TimerController` coordinates the monotonic clock, domain and UI signals.
- `presentation` renders state and forwards user intent without business rules.
- `infrastructure` isolates Qt settings, audio, notifications and YouTube details.
- Dependencies are passed explicitly through constructors where useful.
- No dependency-injection framework, repository layer or speculative abstraction.

### Clean Code Boundaries

- One module has one clear responsibility.
- Prefer files below 200 lines; split a file before it exceeds 300 lines.
- UI files may reach 350 lines only when layout code cannot be separated cleanly.
- Prefer functions below 25 lines; 40 lines is a warning to extract responsibilities.
- A class should describe one concept and normally remain below 200 lines.
- Avoid generic helper dumps and never mix timer rules, widgets and integrations.

### SOLID, Proportionately Applied

- **Single Responsibility:** timer rules, orchestration, persistence and UI remain separate.
- **Open/Closed:** phase behavior is explicit and extendable without rewriting widgets.
- **Liskov Substitution:** do not introduce inheritance unless implementations are interchangeable.
- **Interface Segregation:** use small protocols only when multiple implementations or testing requires them.
- **Dependency Inversion:** core timer rules must not depend on Qt widgets or YouTube.

SOLID is a decision guide, not a requirement to create an interface for every
class. Simple direct dependencies are preferred until a real boundary exists.

## Tech Stack

| Category | Choice |
| --- | --- |
| Language | Python 3.12+ |
| Desktop UI | PySide6 / Qt 6 |
| YouTube player | PySide6.QtWebEngineWidgets |
| Timer refresh | QTimer |
| Time source | `time.monotonic()` |
| Preferences | QSettings |
| Tests | pytest + pytest-qt |
| Quality | Ruff |
| Packaging | PyInstaller, after MVP |

## UI / UX

- Dark, restrained interface
- Compact default window around 340 × 430 px
- Large remaining-time display
- Current phase and task immediately readable
- Primary start/pause control visually dominant
- Player collapsed by default when no URL is configured
- Window can optionally remain above other windows
- Keyboard shortcuts: Space start/pause, R reset, S skip

## Definition of Done

- The complete focus/short-break/long-break cycle works
- A custom `2 × 40 minutes / 10-minute break / stop` cycle works
- Pause, reset and skip follow the documented rules
- The timer does not drift when the UI thread is briefly delayed
- Alarm and notification occur at phase completion
- A supported YouTube URL loads in the embedded player
- Playback follows focus, pause and break states where YouTube permits autoplay
- Preferences survive an application restart
- Invalid URLs produce a user-facing error and no crash
- App launches successfully on Linux and Windows
