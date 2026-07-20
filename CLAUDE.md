# Focus Timer

A small cross-platform Pomodoro desktop widget built with Python and Qt.

## Context Files

Read the following to get the full context of the project:

- @context/project-overview.md
- @context/coding-standards.md
- @context/ai-interaction.md
- @context/current-feature.md

## Commands

- **Create environment**: `python -m venv .venv`
- **Activate on Linux**: `source .venv/bin/activate`
- **Activate on Windows**: `.venv\\Scripts\\activate`
- **Install**: `pip install -r requirements.txt`
- **Run**: `python -m src.main`
- **Tests**: `pytest`
- **Lint**: `ruff check .`
- **Format check**: `ruff format --check .`

## Important

- Keep the MVP small enough to implement in about one focused hour.
- Do not add cloud services, accounts, analytics or a database.
- Do not commit without permission.
- Do not mention Claude or AI in commit messages.


# Context

These files provide the persistent project context referenced by `CLAUDE.md`.
Only the four root context files should be loaded at startup. Subfolders may be
added later for individual feature, fix and research specifications.

- `project-overview.md` - Product scope, behavior, architecture, stack and UI
- `coding-standards.md` - Python and Qt conventions to follow
- `ai-interaction.md` - Workflow and communication rules
- `current-feature.md` - Living specification for the active feature
- `features/` - Future feature specifications loaded on demand
- `fixes/` - Future bug-fix specifications loaded on demand
- `research/` - Technical research loaded on demand
- `screenshots/` - Optional UI references

Suggested project placement:

```text
focus-timer/
├── CLAUDE.md
└── context/
    ├── README.md
    ├── project-overview.md
    ├── coding-standards.md
    ├── ai-interaction.md
    └── current-feature.md
```

