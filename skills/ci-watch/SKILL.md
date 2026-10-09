---
name: ci-watch
description: Use after every push or merge to a branch with CI, and whenever the user reports CI failure emails or red checks - follows the run to completion, collects the COMPLETE list of failures, classifies them, and fixes root causes so they do not recur
---

# CI Watch

## Overview

"Done" means CI is green after the push, not just local tests. Scheduled runs (nightly suites) fail days later for reasons local runs never see: different hardware, missing permissions, slower machines.

**Core principle:** get the full list of failures before fixing any. Fixing the first one you see and re-running wastes a CI cycle per failure.

## The Process

1. **Follow the run** with a background watcher (completion notification), not by polling in the foreground.
2. **On failure, collect everything:** download the full log, then list every failing test/step (e.g. grep all failure markers across the whole log, not the last 30 lines). Count them.
3. **Classify each failure:**
   | Class | Signs | Fix |
   |---|---|---|
   | Code | Fails locally too | Fix the code (systematic-debugging) |
   | Environment capability | Needs hardware/OS features the CI machine lacks (ML accelerators, file protection, GPU, devices) | Gate the test on a real capability probe, with a force-run override. Never delete or blanket-skip the test |
   | Timing | Thresholds tuned on a fast machine | Make the test measure relative, not absolute, timing, or widen it with a documented reason |
   | Infrastructure | Setup actions, SDK installs, runner images changed | Pin or replace the setup step; note it in the CI docs |
   | Flaky | Passes on rerun without changes | Find the race; condition-based waiting |
4. **Fix all classes in one change**, push, and watch the next run until green. For scheduled suites, trigger a manual run instead of waiting for the next night.
5. **Prevent recurrence:** document the rule (for example "tests needing X must use the capability gate") in the project's CI docs or CLAUDE.md.

## Rules

- Never disable a failing test to get green without the user's agreement.
- Never re-run blindly hoping for green; rerun only to classify flakiness.
- Report to the user: run link, failures by class, what changed, final status.
