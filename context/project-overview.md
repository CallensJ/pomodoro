# Focus Timer Project Specifications

🍅 A compact Pomodoro desktop widget for Linux and Windows, built entirely with
Python and Qt.

## Problem

Long development sessions easily dissolve into distraction. Most productivity
tools add accounts, dashboards and configuration before helping the user focus.

Focus Timer provides one small desktop window for starting a focused session,
listening to a local concentration playlist and taking regular breaks.

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

### Local Music Player

- Let the user choose a local folder to use as a concentration playlist
- Scan the chosen folder (non-recursive) for `.mp3` files
- Play back through an OS-native player process, not QtMultimedia — both
  `QSoundEffect` and `QMediaPlayer` were found to block the calling thread
  for many seconds on some audio backends, which is unacceptable on the UI
  thread
- Playback is fully manual and independent of the timer: the timer never
  starts, stops or pauses the player, and the player never affects the timer
- A track that finishes naturally advances to the next, wrapping after the
  last track; a manual "Next" control is also available
- Keep the player optional and collapsible
- Store the last selected folder locally
- Show a useful error if the folder has no `.mp3` files or no supported
  audio player is installed on the system

No network access is involved; only local files are read.

### Local Preferences

Store with `QSettings`:

- focus, short-break and long-break durations;
- timer mode and total sessions;
- custom-cycle break duration and end action;
- alarm enabled;
- auto-start next phase;
- always-on-top preference;
- last selected music folder.

## Out of Scope for MVP

- Accounts, authentication or cloud sync
- Statistics dashboard or calendar integration
- Website and application blocking
- Multiple themes or complex animations
- System tray behavior
- Auto-start with the operating system
- Database, telemetry or automatic updates
- Streaming, downloading or scraping from any external music service

## Timer Rules

1. The initial phase is `FOCUS` and the timer is stopped.
2. Starting creates a monotonic deadline; UI ticks only update the display.
3. Pausing stores the remaining duration and pauses music playback.
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
│   ├── music_library.py
│   └── local_music_player.py
├── presentation/
│   ├── main_window.py
│   ├── settings_dialog.py
│   ├── music_player_widget.py
│   └── styles.qss
└── assets/
    └── alarm.wav
tests/
requirements.txt
```

- `domain` contains timer state and phase-transition rules without Qt widgets.
- `TimerController` coordinates the monotonic clock, domain and UI signals.
- `presentation` renders state and forwards user intent without business rules.
- `infrastructure` isolates Qt settings, audio, notifications and local
  music playback details.
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
- **Dependency Inversion:** core timer rules must not depend on Qt widgets or
  the music player.

SOLID is a decision guide, not a requirement to create an interface for every
class. Simple direct dependencies are preferred until a real boundary exists.

## Tech Stack

| Category | Choice |
| --- | --- |
| Language | Python 3.12+ |
| Desktop UI | PySide6 / Qt 6 |
| Music playback | OS-native player process (ffplay/VLC on Linux, MCI on Windows) |
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
- Player collapsed by default when no music folder is configured
- Window can optionally remain above other windows
- Keyboard shortcuts: Space start/pause, R reset, S skip

## Definition of Done

- The complete focus/short-break/long-break cycle works
- A custom `2 × 40 minutes / 10-minute break / stop` cycle works
- Pause, reset and skip follow the documented rules
- The timer does not drift when the UI thread is briefly delayed
- Alarm and notification occur at phase completion
- A chosen music folder's `.mp3` files load into the player
- Playback follows focus, pause and break states
- A track finishing naturally advances to the next, wrapping after the last
- Preferences survive an application restart
- A folder with no `.mp3` files, or no supported audio player installed,
  produces a user-facing error and no crash
- App launches successfully on Linux and Windows
