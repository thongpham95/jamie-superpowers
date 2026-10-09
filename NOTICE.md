# Notice

jamie-superpowers is a fork of [obra/superpowers](https://github.com/obra/superpowers)
version 6.4.1, Copyright (c) 2025 Jesse Vincent, released under the MIT License (see `LICENSE`).
The original skills, structure and ideas are his work; all credit for them belongs to him.

## What changed (high level)

- Renamed the plugin and its entry skill (`using-jamie-superpowers`); Claude Code only.
- Per-project configuration file (`.jamie-superpowers.json`) instead of project-specific
  text in skills; per-user preferences (output language, status line thresholds).
- Resource-aware parallel agents: `machine-budget` verdicts and `jsp-slot` slots for
  heavy jobs, plus an agent ledger (`jsp-agents`) for cache-aware resume-or-restart decisions.
- Batch cleanup of merged worktrees, container images and temp files (`batch-cleanup`).
- Deploy changelog skeleton from git history (`changes-since`).
- Context keeping: SessionStart state injection, PreCompact checkpoints, a context
  status line.
- A neutrality linter so a shared plugin stays free of personal or project data.
- Adjusted skill texts to use the above.
