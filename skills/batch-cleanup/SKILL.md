---
name: batch-cleanup
description: Use after every release, after any worktree/branch is merged, once a change looks stable, after a batch of parallel agents, after a deploy, when free disk drops below ~10 GB, or before pausing a session - removes finished worktrees, merged branches, regenerable build output, the project's unused container images/volumes and temp files, and reports space freed
---

# Batch Cleanup

## Overview

Agent worktrees, merged branches, build caches, container images and temp files pile up fast. Dozens of worktrees and tens of GB of images are normal after a few days of parallel work. That slows the machine, fills the disk and confuses later agents.

**Core principle:** clean up after every batch, only what is provably finished, only what belongs to this project.

**When (do not let it pile up):** after every release, every time a worktree is merged, and as soon as the work looks stable - not only at the end of a batch. Do it before starting heavy work again if the disk is low or the load is high.

## The Process

1. **Dry run:** `"${CLAUDE_PLUGIN_ROOT}/scripts/batch-cleanup"`. Read every line.
2. **Apply:** `"${CLAUDE_PLUGIN_ROOT}/scripts/batch-cleanup" --apply`.
3. **Hand check** the items under "Beyond the Script".
4. **Report** in the batch summary: what was removed, disk freed, free disk now, and the list of KEEP and ASK items with their reasons (unmerged, uncommitted changes, running agent) so the user can decide.

## What It Removes (and what it never touches)

| Removed | Only when |
|---|---|
| Worktrees | Clean (no changes, no untracked files) AND merged into the default branch. Never `--force`. |
| Local branches of removed worktrees | Merged (`git branch -d`, never `-D`) |
| Container images / volumes | Match the project's `cleanup.dockerImages` / `cleanup.dockerVolumes` globs AND unused |
| Temp files | Match the project's `cleanup.tmpGlobs` AND owned by the current user |
| Regenerable build output (build dirs, derived data, archives) | Listed in the project's `cleanup.dirs`, older than its `minAgeMinutes`, and no configured heavy job (build/test) is running. An entry with `"ask": true` is only listed (ASK), never removed |

Without a project config it only touches worktrees and branches. It never touches other projects' worktrees, containers or files, and never runs global prune commands.

## Beyond the Script (check by hand, then report)

The script only removes what the config names. After a release or merge also look for the following, and either add it to `cleanup.dirs` (regenerable) or ask the user (not regenerable):
- Simulators/emulators created for this work and no longer needed (delete only the ones no running agent uses).
- Intermediate output of media or video builds once the final export is verified.
- Downloaded or generated assets from external services that the user wants removed (list them, ask before deleting anything remote).
- Large device-support or symbol caches: list and ask; they are slow to regenerate.

**Before removing a worktree that holds untracked reports or screenshots, copy them to an archive folder** (for example `_archive/worktree-leftovers-<date>/`) so nothing of value is lost, then remove it.

Never touch a worktree, simulator or directory that a running agent is using; list it as KEEP.

## Setting Up a Project

If the project has no `.jamie-superpowers.json`, propose one to the user (it is committed with the project) with:
- `repos`: sub-repositories, if the project is a multi-repo workspace
- `cleanup.dockerImages` / `dockerVolumes`: only patterns this project creates
- `cleanup.tmpGlobs`: the project's temp prefixes
- `cleanup.dirs`: regenerable build output, as `{"glob": "...", "minAgeMinutes": 30, "ask": false}`; relative globs apply inside every repo, absolute or `~` globs as written

## Rules

- Uncommitted work is never removed. If a worktree has changes, list it, and if it looks abandoned, ask the user.
- Stop or let finish any agent using a worktree before cleanup.
- Clean up the build daemons/caches your own agents started only when the project's tooling has a documented stop command.

## Red Flags

- "I'll force-remove, it's probably fine" → no. KEEP and report.
- "Prune all dangling images" → that hits other projects. Use the project's patterns only.
