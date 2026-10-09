---
name: session-handoff
description: Use at milestones, before long waits, when the user pauses or ends a session ("stop here", "pause", "update handoff"), and when starting a session that should continue earlier work - writes and reads the handoff file and memory so any fresh session can continue
---

# Session Handoff

## Overview

The handoff is the single source of truth for "where are we". It must let a fresh session (or a teammate) continue without the transcript.

## File

`<handoffDir>/HANDOFF-<YYYY-MM-DD>.md` (`handoffDir` from project config, default the project root). One file per day of work; append "update" sections during the day instead of creating many files. Write it in the user's output language.

## Template

```
# Handoff <date> — <one-line state>

Read with: <previous handoff, key plan/spec paths>

## 1. Done
| Item | Result (commit/PR/build, where it is deployed) |

## 2. Waiting on the user
Numbered, each with the exact decision or action needed.

## 3. In progress
Running agents (id, model, worktree, task), stashes, unmerged branches, what is half-done and how to resume it.

## 4. Traps / lessons
Things that cost time and how to avoid them next time.

## 5. Next steps
Ordered; first item is what to do on resume.

## 6. Operating rules for this project
Resource limits, consent list, account/tool quirks.
```

## Pausing a Session ("stop here")

1. Let running agents finish their current step, or stop them; record their state.
2. Park unfinished work: commit to a WIP branch or `git stash push -m "<what, why>"`. Never leave uncommitted work only in a worktree you are about to clean.
3. Run batch-cleanup (dry run, then apply).
4. Write/update the handoff.
5. Update memory: one pointer entry to the handoff, plus any durable user preference learned this session.
6. Tell the user in 3–5 lines what is done, what waits on them, and where the handoff is.

## Resuming

Read the newest handoff (and the newest checkpoint if the session was compacted). Verify its claims cheaply (`git status`, branch heads, CI status) before building on them. State the first next step and start.

## Rules

- Facts only, with commit SHAs, paths and numbers. No narrative.
- Never put secrets in a handoff. Name the file that holds them instead.
- Convert relative dates to absolute dates.
