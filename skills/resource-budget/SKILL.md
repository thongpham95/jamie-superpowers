---
name: resource-budget
description: Use before starting heavy work (builds, large test suites, browser E2E, virtual devices, media processing) or before dispatching more than one agent - measures the machine and sizes parallelism so it is never overloaded
---

# Resource Budget

## Overview

Parallel agents only speed things up while the machine has headroom. Past that point every job slows down, timing-sensitive work (recordings, UI tests, benchmarks) produces garbage, and other projects on the same machine suffer.

**Core principle:** measure, then size. Never guess how many heavy jobs the machine can take.

## When to Use

- Before dispatching 2+ agents, or one agent that will build/test heavily
- Before any job the project config lists under `heavyJobs`, or anything obviously heavy (compilers, full test suites, browsers, emulators, video)
- When something is unexpectedly slow or flaky — check load before debugging the code

## The Process

1. **Measure:** run `"${CLAUDE_PLUGIN_ROOT}/scripts/machine-budget"`. It prints cores, RAM, load, free disk, running heavy jobs per kind, and a verdict:
   - `VERDICT: ok max_heavy=<n> max_agents=<n>` → size your batch to at most those numbers.
   - `VERDICT: wait reason=...` (exit 3) → do not start heavy work. Find out who is using the machine (`ps`), and if it is another project, wait; never kill it.
2. **Size the batch:** agents = min(independent tasks, `max_agents`). Count heavy *jobs*, not agents: two agents that both compile hold two build slots.
3. **Gate heavy commands with slots:** run them through `"${CLAUDE_PLUGIN_ROOT}/scripts/jsp-slot" <kind> -- <command>`. Slot counts come from `heavyJobs.<kind>.slots` in `.jamie-superpowers.json` (default 1). The script waits while slots are busy or load is too high, and always releases.
4. **Put the rules in every dispatch brief:** the slot command to use, "never start a second virtual device", "if load is high, wait instead of retrying", and the scope of test runs (only the modules touched).
5. **Re-measure between batches.** Load from other sessions changes quickly.

## Defaults (overridable in project config)

| Setting | Default |
|---|---|
| Wait threshold | 1-minute load > `loadFactor` (1.5) × cores |
| Free RAM floor | 1.5 GB |
| Free disk floor | 10 GB (run batch-cleanup if below) |
| Slots per heavy kind | 1 |
| Timing-sensitive work (recording, perf tests) | run alone, load < cores |

## Common Mistakes

| Mistake | Fix |
|---|---|
| Starting 4 build agents because there are 4 tasks | Tasks ≠ capacity. Use `max_agents` and slots. |
| Recording or benchmarking while builds run | Timing-sensitive work runs alone. |
| Killing a heavy process you did not start | Never. It may belong to another project or the user. Wait. |
| Running the full suite in every agent | Each agent tests only what it touched; one full run before merge. |
| Ignoring disk | Below 10 GB free, clean up first (batch-cleanup). |

## Red Flags

- "The machine looked fine an hour ago" → measure now.
- "It's only one more agent" → it is one more set of builds.
- Flaky timeouts appearing across agents → overload, not code. Stop dispatching.
