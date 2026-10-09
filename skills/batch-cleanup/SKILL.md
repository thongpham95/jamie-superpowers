---
name: batch-cleanup
description: Use after a batch of parallel agents has merged, after a deploy, when free disk drops below ~10 GB, or before pausing a session - removes finished worktrees, merged branches, the project's unused container images/volumes and temp files, and reports space freed
---

# Batch Cleanup

## Overview

Agent worktrees, merged branches, build caches, container images and temp files pile up fast. Dozens of worktrees and tens of GB of images are normal after a few days of parallel work. That slows the machine, fills the disk and confuses later agents.

**Core principle:** clean up after every batch, only what is provably finished, only what belongs to this project.

## The Process

1. **Dry run:** `"${CLAUDE_PLUGIN_ROOT}/scripts/batch-cleanup"`. Read every line.
2. **Apply:** `"${CLAUDE_PLUGIN_ROOT}/scripts/batch-cleanup" --apply`.
3. **Report** in the batch summary: what was removed, disk freed, free disk now, and the list of KEEP items with their reasons (unmerged, uncommitted changes) so the user can decide.

## What It Removes (and what it never touches)

| Removed | Only when |
|---|---|
| Worktrees | Clean (no changes, no untracked files) AND merged into the default branch. Never `--force`. |
| Local branches of removed worktrees | Merged (`git branch -d`, never `-D`) |
| Container images / volumes | Match the project's `cleanup.dockerImages` / `cleanup.dockerVolumes` globs AND unused |
| Temp files | Match the project's `cleanup.tmpGlobs` AND owned by the current user |

Without a project config it only touches worktrees and branches. It never touches other projects' worktrees, containers or files, and never runs global prune commands.

## Setting Up a Project

If the project has no `.jamie-superpowers.json`, propose one to the user (it is committed with the project) with:
- `repos`: sub-repositories, if the project is a multi-repo workspace
- `cleanup.dockerImages` / `dockerVolumes`: only patterns this project creates
- `cleanup.tmpGlobs`: the project's temp prefixes

## Rules

- Uncommitted work is never removed. If a worktree has changes, list it, and if it looks abandoned, ask the user.
- Stop or let finish any agent using a worktree before cleanup.
- Clean up the build daemons/caches your own agents started only when the project's tooling has a documented stop command.

## Red Flags

- "I'll force-remove, it's probably fine" → no. KEEP and report.
- "Prune all dangling images" → that hits other projects. Use the project's patterns only.
