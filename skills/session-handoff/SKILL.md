---
name: session-handoff
description: Use at milestones, before long waits, when the user pauses or ends a session ("stop here", "pause", "update handoff"), when the user asks for a timed run followed by a summary and review gate ("work until morning, then summarize, hand off, clean up and wait for me"), and when starting a session that should continue earlier work - writes and reads the handoff file and memory so any fresh session can continue
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

## Timed Run With a Review Gate ("work until X, then summarize and wait for me")

Applies to ANY kind of work and any project: an app (iOS, Android), web, backend, a research question, a migration, a document, or any other task. When the user asks for continuous work until a time and then a wrap-up, do this:

0. **Run the window.** Note the deadline (absolute date and time, from `date`) in the working ledger or handoff draft. Keep working through the plan. Never run past the window: when the deadline arrives, start no new task, let the running step finish (or stop it and record its state), then wrap up. Consent rules stay in force the whole time: no push, publish, deploy, upload, merge to a shared branch or other outward action unless the user already authorized it. Queue those for the review gate instead.
1. **Progress summary artifact (a "fast-forward").** Publish ONE reviewable page with the Artifact tool (load the `artifact-design` skill first; the page is private by default, give the user the link). It must show, for a reader who saw none of the session:
   - **Before → after as a fast-forward**: a compact, scannable comparison of the state at the start of the run versus now, shown as stepped frames or a timeline the reader can click through or scrub, not a wall of text. Illustrate with what fits the work: screenshots or mockups of the screens before and after (apps and web), request/response or architecture diagrams (backend), findings, charts and sources (research), diffs or metrics (anything else). Mark clearly which frames are real captures and which are illustrations.
   - **Problems this run prevents from coming back**: the bugs, rejections, regressions or past mistakes that were fixed or guarded against (for an app: store or review rejections, bugs already fixed on another platform; for other work: incidents, wrong assumptions, rework), each with how it is now guarded (test, check, rule).
   - **Status table**: tasks done, in progress, not started; branches and commits; what was verified (tests run, output) and what was not; open risks.
   - **Decisions I made on your behalf** (every `Ruling:` line) and **what waits on you** (decisions, approvals, outward actions queued).
   Keep it in the user's output language, facts only, with real numbers. If real captures would be misleading or impossible, say so and use labelled illustrations.
2. **Hand off and clean up.** Do the Pausing steps below (park unfinished work, `batch-cleanup` dry run then apply, write the handoff, update memory). Copy anything the summary page or the handoff still needs (screenshots, reports) out of any worktree before cleaning it. Report what was removed and the disk freed.
3. **Stop and wait for review.** After the summary, handoff and cleanup, do nothing further: no new tasks, no outward actions, no "while I wait" work. Tell the user in 3–5 lines where the summary page and handoff are and what waits on them. Resume only when the user reviews and says to continue; then follow Resuming.

## Resuming

Read the newest handoff (and the newest checkpoint if the session was compacted). Verify its claims cheaply (`git status`, branch heads, CI status) before building on them. State the first next step and start.

## Rules

- Facts only, with commit SHAs, paths and numbers. No narrative.
- Never put secrets in a handoff. Name the file that holds them instead.
- Convert relative dates to absolute dates.
