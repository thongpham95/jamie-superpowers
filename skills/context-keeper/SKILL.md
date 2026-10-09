---
name: context-keeper
description: Use throughout long sessions, when the context meter passes 50%, before long waits, and whenever about to read large files or logs - keeps the main context lean, saves state before compaction, and tells the user when to compact
---

# Context Keeper

## Overview

A long session degrades in two ways: the context fills with material nobody needs again, and compaction loses the thread. Neither the model nor a skill can trigger `/compact`. Auto-compact, the PreCompact hook and the user can. So keep the context lean, keep state on disk, and ask the user to compact at the right moment.

## Habits (always)

| Instead of | Do |
|---|---|
| Reading many files to find something | Dispatch a search subagent (Haiku); keep only its conclusion |
| Dumping full command output | Filter: `| tail -30`, `grep -E 'FAIL|error'`, `--quiet`, counts |
| Reading a whole large file | Read the relevant range |
| Polling a long job every minute | Background it with a completion notification / Monitor |
| Reading a subagent's transcript | Read its report file |
| Pasting history into dispatches | File paths + the brief |
| Keeping big tables in replies | Put them in a file or page; link it |

## Milestones → write state to disk

At each milestone (a batch merged, a deploy, a decision, before a long wait), update the handoff (session-handoff) and memory. A checkpoint must let a fresh session continue without the transcript.

## Compaction

- **Meter:** with the plugin's statusline, the context % is visible. Yellow ≥ 50%, red ≥ 70% (configurable).
- **At yellow:** tighten habits. Finish the current step, update the handoff.
- **At red, or before a long wait with a heavy context:** update the handoff, then give the user a ready-to-paste command:
  `/compact Keep: current goal, open tasks, running agents and their ids, decisions and pending approvals, file paths. Drop: logs, file contents, finished work details.`
- **The PreCompact hook** writes `.jamie-superpowers/checkpoints/<time>.md` (repos, uncommitted changes, worktrees, stashes, open agents) automatically, for manual and auto compaction.
- **After compaction**, the session-start context names the newest checkpoint and handoff. Read them before acting. Do not redo finished work, and re-check the state of background agents.
- **Earlier auto-compaction** is configured by the user (`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`, a lower threshold only). Suggest it, never set it yourself.

## Red Flags

- "I'll just cat the whole log" → filter it.
- "I'll remember where I was" → write it down; compaction will not.
- "Let me re-read all the handoffs" → read the newest checkpoint and the newest handoff only.
