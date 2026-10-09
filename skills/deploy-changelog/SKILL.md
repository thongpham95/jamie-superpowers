---
name: deploy-changelog
description: Use right after any deploy or release (beta channel, store submission, staging, production, backend functions) - posts a formatted changelog with emoji in the chat and appends it to the deploy log
---

# Deploy Changelog

## Overview

The user tracks progress in the chat and forwards release notes to testers. Every deploy gets a changelog immediately, in the user's output language, without being asked.

## The Process

1. **Collect:** `"${CLAUDE_PLUGIN_ROOT}/scripts/changes-since <last deployed ref>"` for each deployed component. It groups commits into buckets. Find the last deployed ref in `DEPLOYS.md` (project root or `handoffDir`), from tags, or ask.
2. **Rewrite for humans:** write each item as the user-visible effect, not the commit subject. Drop internal noise. Merge duplicates.
3. **Post in chat** using the template below, one block per component.
4. **Tester notes:** if the deploy goes to testers, add a short plain-text version (no internal details) that can be pasted into release notes.
5. **Log:** append the block, date and refs to `DEPLOYS.md` (commit with the next commit; never push to an auto-deploying branch just for this).

## Template

```
🚀 <component> <version> (build <n>) · <channel> · <date>

✨ New
  · <user-visible feature>
🐛 Fixes
  · <bug fixed, in user terms>
🔧 Infrastructure
  · <CI, build, cleanup: "removed 12 worktrees + 3 images → +18 GB">
⚠️ Good to know
  · <known issues, decisions pending>
🧪 Please test
  · <flows testers should try>
🔗 <short sha> · <short sha>
```

Translate the headers into the output language. Omit empty sections, except ⚠️ when anything is pending.

## Rules

- Only after the deploy actually succeeded (exit code, URL, build processed). If it partially failed, say so in ⚠️ first.
- Include the cleanup result of the batch if one ran.
- No secrets, internal hostnames or credentials in the changelog.
- No bots or external posting unless the user asks; the chat is the channel.
