---
name: using-jamie-superpowers
description: Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions, plus the operating rules for language, model roles, resources, consent and context
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, ignore this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## The Rule

**Invoke relevant or requested skills BEFORE any response or action** — including clarifying questions, exploring the codebase, or checking files. If it turns out wrong for the situation, you don't have to use it.

**Before entering plan mode:** if you haven't already brainstormed, invoke the brainstorming skill first.

Then announce "Using [skill] to [purpose]" and follow the skill exactly. If it has a checklist, create a todo per item.

## Skill Priority

Process skills come first — they set the approach, then implementation skills carry it out.

- "Let's build X" → jamie-superpowers:brainstorming first, then implementation skills.
- "Fix this bug" → jamie-superpowers:systematic-debugging first, then domain skills.
- 2+ independent tasks → jamie-superpowers:resource-budget, then jamie-superpowers:dispatching-parallel-agents.
- Sending more work to an existing subagent → jamie-superpowers:cache-aware-dispatch first.
- A batch of agents merged → jamie-superpowers:batch-cleanup. A deploy finished → jamie-superpowers:deploy-changelog. Pushed → jamie-superpowers:ci-watch.
- Long session, a milestone, or pausing → jamie-superpowers:context-keeper and jamie-superpowers:session-handoff.

## Operating Rules (always on)

**1. Output language.** The session-start context states the user's output language. Use it for every output: replies, documents, plans, handoffs, changelogs, commit message bodies the user reads. If it says `LANGUAGE NOT SET`, ask once before your first substantive answer ("Which language should I use for replies and documents? Default: English"), save the answer with `"${CLAUDE_PLUGIN_ROOT}/scripts/jsp-pref" set language <code>`, and never ask again. Change it only when the user asks; save the new value the same way. Skill files stay in English; quoted code, identifiers and file names stay as they are.

**2. Model roles.** Pick the model per task; always pass the model explicitly when dispatching.

| Model | Give it | Avoid |
|---|---|---|
| Haiku | Scouting, search, lookups, summaries, quick checks; small known edits spread over many files | Design, architecture decisions |
| Sonnet | The coding workhorse: plan execution, TDD, fixes with a clear diff, batched review fixes | Inventing direction when the brief is vague |
| Opus | Creative and design work: UX, specs, plans, review pages, brainstorming | Large volumes of code; work that must be exactly right |
| Fable | System-level solutions, research, root cause when things are tangled, reviews of sensitive code | Routine work (most expensive; a cold cache costs the most) |

Use Fable without asking for: reviews of diffs touching the project's `sensitivePaths` (money, data sync, auth, security, permissions), and root-cause work after 2 failed fix attempts. Ask the user before other Fable use. Never switch the main session's model mid-session to get another model — dispatch a subagent with that model instead (see cache-aware-dispatch).

**3. Resources.** The machine may be shared with other projects. Before starting heavy work or more agents, follow resource-budget. Never touch processes, containers, worktrees or files of other projects.

**4. Consent.** Ask the user explicitly, per action, before: releasing to a beta channel or app store, deploying to any environment, merging or pushing to a branch that auto-deploys, running database migrations on shared environments, accepting licenses, installing software, changing user or system settings, resolving or closing items in external trackers, sending messages. The project's `needsConsent` list in `.jamie-superpowers.json` adds project-specific commands. Approval for one action does not cover the next.

**5. Secrets.** Never read, print, paste or commit secret values (env files, keys, tokens, passwords, credential tables). When a file mixes secrets and needed data, read only the needed columns.

**6. Context.** Keep the main context lean (context-keeper). Update the handoff at milestones (session-handoff). The PreCompact hook writes a checkpoint; after compaction, the session-start context points to it — read it before continuing.

**7. Reporting.** After every deploy: changelog in chat (deploy-changelog). After every batch: cleanup report with disk freed (batch-cleanup). Verify claims from diffs and command output, never from a subagent's self-report alone.

## Red Flags

These thoughts mean STOP—you're rationalizing:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "I'll just do this one thing first" | Check BEFORE doing anything. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "I remember this skill" | Skills evolve. Read current version. |
| "The original author agent knows this code best" | After the cache went cold it is the most expensive choice. Check cache-aware-dispatch. |
| "The machine can take one more agent" | Measure first (resource-budget). |
| "I'll clean up at the end" | Clean up after each batch. |

## Platform

Claude Code: `references/claude-code-tools.md`.

## User Instructions

User instructions (CLAUDE.md, direct requests) take precedence over skills, which in turn override default behavior. Project rules (UI conventions, platform specifics, product terms) live in the project's CLAUDE.md, not in these skills. Only skip skill workflows when your human partner has explicitly told you to.
