---
name: cache-aware-dispatch
description: Use before sending follow-up work (fixes, review findings, questions) to an existing subagent, before switching models, and before long waits - decides between resuming an agent and dispatching a fresh one based on prompt-cache age and context size
---

# Cache-Aware Dispatch

## Overview

Every turn of an agent re-sends its whole context. While the prompt cache is warm, that context is billed at the cheap cache-read rate. Once the cache expires, the whole context is written again at the cache-write rate. For a large context the difference is 20–80× per turn, depending on the model.

A real case: review fixes were routed back to the original author agent after it had been idle for more than an hour with ~400K tokens of context. That single habit consumed about a third of a weekly quota.

**Core principle:** an agent's context is an asset only while its cache is warm. After that it is a liability; a fresh agent with a tight brief is cheaper and usually just as good.

## Facts to Reason With

- Cache lifetime in Claude Code is typically 1 hour (5 minutes in some overage situations), counted from the *start* of the previous request; each cache read refreshes it.
- Caches are per model. Switching the main session's model re-reads the entire context at write price.
- A fresh subagent starts with a small prefix; only its summary returns to you.
- Cost per turn ≈ context size × (read rate if warm, write rate if cold).

## Decision: resume or fresh?

Before sending anything to an existing agent, run `"${CLAUDE_PLUGIN_ROOT}/scripts/jsp-agents" check <id>`.

| Situation | Do |
|---|---|
| Warm (last activity < `cacheResumeMinutes`, default 45) AND the task is hard AND it needs the agent's full context | Resume the agent |
| Warm, but the fix is narrow and the diff/findings explain it | Fresh agent (cheaper model) with the brief |
| Cold | Fresh agent. Always. |
| Several narrow fixes from several review rounds | Batch them: hold briefly, then one fresh Sonnet (Haiku for uniform multi-file edits) gets all of them in one brief |

A fresh-agent brief contains: the goal in one line, file paths (not pasted contents), the findings verbatim, the diff or review-package path, constraints, and the report contract. Not the session history.

## Ledger

Track every dispatched agent so cache age is known, not guessed:

- On dispatch: `jsp-agents log <id> <model> <short description>`
- On each report or message: `jsp-agents touch <id>`
- When finished: `jsp-agents done <id>`
- `jsp-agents list` shows open agents and marks `COLD` ones. Mention long-idle agents to the user.

## Other Rules

- **Never switch the main session's model to get a different model's strengths.** Dispatch a subagent with that model.
- **Before a long wait** (CI, long agents, user away) with a heavy context: update the handoff and suggest `/compact` while the cache is still warm, so the next turn re-reads a small context.
- **Keep the prefix stable** in long sessions: do not toggle plugins/tools or rewrite CLAUDE.md mid-session.
- **Wide reading goes to subagents** — their context is discarded; only the summary stays in yours.

## Red Flags

| Thought | Reality |
|---|---|
| "It wrote the code, it knows it best" | If cold, you pay to re-read everything it knows. Fresh + diff. |
| "Just one small fix, send it back" | Small fixes are exactly what fresh cheap agents are for. |
| "Switch to the big model for this one question" | Subagent with that model, not `/model`. |
| "I'll dispatch each review finding as it arrives" | Batch narrow fixes. |
