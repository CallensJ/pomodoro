# AI Interaction Guidelines

## Communication

- Be concise and direct
- Explain non-obvious technical decisions briefly
- Ask before large refactors or architectural changes
- Do not add features outside the specification
- Never delete files without clarification
- State clearly when YouTube or operating-system behavior cannot be guaranteed

## Workflow

Use this workflow for every feature or fix:

1. **Document** - Update `@context/current-feature.md` with requirements and acceptance criteria.
2. **Branch** - Create a branch named for the feature or fix.
3. **Implement** - Make the smallest complete implementation.
4. **Test** - Run automated checks and manually launch the desktop app.
5. **Iterate** - Fix observed problems without expanding scope.
6. **Review** - Check timer accuracy, UI responsiveness and failure handling.
7. **Commit** - Ask permission and commit only after checks pass.
8. **Merge** - Merge into main after approval.
9. **Clean up** - Ask before deleting the merged branch.
10. **Record** - Mark the feature complete and add it to History.

Do not commit without permission. If a check fails, fix it before asking to
commit or report the blocker clearly.

## One-Hour MVP Mode

- Prioritize a working timer over visual polish
- Implement requirements in the order listed in `current-feature.md`
- Stop adding architecture once responsibilities are clearly separated
- Postpone packaging until the application works from source
- If time becomes tight, retain manual YouTube controls before attempting fragile automation
- Record deferred work instead of silently implementing it

## Branching

- Features: `feature/[short-name]`
- Fixes: `fix/[short-name]`
- Chores: `chore/[short-name]`
- One branch should contain one focused change

## Commits

- Ask before committing
- Use conventional commits: `feat:`, `fix:`, `test:`, `docs:`, `chore:`
- Keep commits focused
- Never include AI attribution in a commit message

## When Stuck

- After two or three failed approaches, stop and explain the evidence
- Do not keep applying speculative fixes
- Ask for clarification when a requirement changes behavior materially
- Prefer a graceful fallback when audio, notification or YouTube integration fails

## Code Changes

- Preserve existing project patterns
- Do not refactor unrelated code
- Do not add optional libraries without explaining why they are required
- Never replace the monotonic timer with UI tick counting
- Do not add accounts, cloud sync, telemetry or a database
- Do not create files above 300 lines without stopping to justify and split them
- Do not create classes or functions that mix UI, timer rules and infrastructure
- Do not apply SOLID through speculative interfaces or empty abstraction layers

## Review Checklist

- Does the timer remain accurate after pausing and resuming?
- Are phase transitions and the long-break counter correct?
- Can external-service failures occur without stopping the timer?
- Are YouTube URLs parsed safely?
- Does the UI remain responsive?
- Do settings survive restart?
- Are Linux and Windows paths and behaviors handled portably?
- Does every changed module have one clear responsibility?
- Are functions, classes and files within the documented size limits?
- Do dependencies still point inward toward the domain?
