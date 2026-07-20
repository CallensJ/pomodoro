# Coding Standards

## Python

- Target Python 3.12 or newer
- Use type hints for public functions, methods and attributes
- Prefer standard-library types such as `list[str]` and `str | None`
- Use `Enum` for timer phases and explicit state values
- Use dataclasses for small data-only models where appropriate
- Never use mutable default arguments
- Prefer functions under 25 lines; review and split functions above 40 lines
- Avoid global mutable state
- A function should perform one level of abstraction and have one reason to change
- Prefer early returns over deeply nested conditionals
- Use descriptive names; avoid unexplained abbreviations and boolean flag arguments

## PySide6 / Qt

- Import only from PySide6; do not mix PyQt and PySide
- Use Qt signals and slots for communication between services and UI
- Keep business rules outside widgets
- Never block the UI thread with sleeps, network calls or long operations
- Use `QTimer` only as a refresh trigger, not as the authoritative clock
- Use `time.monotonic()` to calculate elapsed and remaining time
- Give parent objects to Qt objects when ownership is clear
- Update widgets from the main Qt thread only

## Architecture

- `domain` owns timer state and transition rules without UI dependencies
- `application` coordinates use cases and is the source of truth for a running session
- `presentation` displays state and emits intent; it contains no phase rules
- `infrastructure` contains settings, audio, notifications and YouTube adapters
- Keep YouTube URL parsing independent from `QWebEngineView`
- Access `QSettings` through one infrastructure wrapper
- Dependencies point toward the domain, never toward widgets
- Pass dependencies explicitly rather than constructing them throughout the code
- Prefer composition over inheritance
- Introduce a `Protocol` only for a real replaceable boundary or a useful test seam
- Do not introduce patterns, base classes or factories without a current need
- Do not use threads in the MVP

## SOLID Principles

- **SRP:** each module, class and function has one primary responsibility
- **OCP:** add behavior through focused collaborators, not growing conditional monoliths
- **LSP:** subclasses must honor the complete contract; prefer no inheritance when unsure
- **ISP:** expose small purpose-specific protocols instead of large service interfaces
- **DIP:** timer rules depend on simple values/contracts, not Qt widgets or web engines

Apply these principles to reduce coupling. Do not create empty abstractions merely
to claim SOLID compliance.

## YouTube Player

- Accept only `http` or `https` YouTube URLs
- Parse URLs with `urllib.parse`; do not validate with one large regex
- Support normal video, shortened video and playlist URLs
- Convert inputs to official YouTube embed URLs
- Do not execute JavaScript built from unsanitized user input
- Do not download media or bypass embed, region or age restrictions
- Treat autoplay and embedded-player errors as recoverable UI errors

## Naming

- Modules and files: `snake_case.py`
- Classes and enums: `PascalCase`
- Functions, methods and variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Signals: clear past-tense or event names such as `phase_changed`
- Private implementation details: leading underscore

## File Organization

- Timer entities and rules: `src/domain/`
- Use-case coordination: `src/application/`
- Qt/external adapters: `src/infrastructure/`
- Windows, dialogs and widgets: `src/presentation/`
- Local sounds and icons: `src/assets/`
- Tests mirror the source structure under `tests/`

## Size and Separation Limits

- Target fewer than 200 lines per Python module
- Split modules before 300 lines, excluding generated files
- Presentation modules may reach 350 lines only with a documented reason
- Target fewer than 200 lines per class
- Prefer functions below 25 lines and no more than 3 indentation levels
- Extract cohesive widgets, services or pure functions when limits are approached
- Never create a file containing unrelated functions only to reduce other files
- Never accumulate generic behavior in `utils.py`, `helpers.py` or `misc.py`
- Generated code, lock files and Qt resource output are exempt and must not be hand-edited

## Styling

- Keep visual styling in `src/presentation/styles.qss`
- Avoid large inline style-sheet strings in Python files
- Use Qt properties for state-dependent styling where useful
- Dark mode only for the MVP
- Prefer native layout managers; never position widgets with fixed coordinates
- Ensure controls remain readable at 100% and 150% scaling

## Error Handling

- Catch errors at external boundaries: settings, sound, notifications and web view
- Show short, user-friendly messages in the UI
- Log technical details with Python's `logging` module
- Never use a bare `except`
- Timer operation must continue if audio, notification or YouTube playback fails

## Testing

- Unit-test URL parsing and timer phase transitions
- Use short injected durations for timer tests
- Do not make real YouTube network requests in automated tests
- Manually verify alarm, notification and embedded playback on both platforms
- Run `pytest`, `ruff check .` and `ruff format --check .` before committing

## Code Quality

- No commented-out code unless explicitly requested
- No unused imports, variables or dead branches
- Use docstrings for public modules/classes only when they add useful context
- Comments explain why, not what the code already states
- Make the smallest change that completes the active feature
- Prefer duplication over the wrong abstraction; extract only after responsibility is clear
- Run a responsibility and file-size review before requesting a commit
