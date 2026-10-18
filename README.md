# jamie-superpowers

A fork of [obra/superpowers](https://github.com/obra/superpowers) (see `NOTICE.md`) that adds
resource-aware parallel agents, cache-aware dispatch, batch cleanup, deploy changelogs and
context keeping. It is project-neutral: everything specific to a project lives in that project's
`.jamie-superpowers.json`, and everything specific to you lives in your user directory.

## Install

As a plugin (Claude Code):

```bash
claude plugin marketplace add <path-or-url-of-a-marketplace-listing-this-plugin>
claude plugin install jamie-superpowers
```

Or from a clone:

```bash
git clone https://github.com/thongpham95/jamie-superpowers ~/.claude/skills/jamie-superpowers
```

or point Claude Code at the directory for a single session: `claude --plugin-dir /path/to/jamie-superpowers`.

Requirements: bash, python3 (3.8+, stdlib only), git. macOS or Linux. Docker is optional (only
used by `batch-cleanup` when you configure Docker globs).

### Keep the original superpowers disabled

Both plugins inject a session-start skill and share skill names, so loading both duplicates
instructions. Disable the original in `settings.json`:

```json
{ "enabledPlugins": { "superpowers@claude-plugins-official": false, "jamie-superpowers@<marketplace>": true } }
```

(or run `claude plugin disable superpowers`). Skills of this plugin are invoked as
`jamie-superpowers:<skill>`.

## Configuration

### Per project: `<project root>/.jamie-superpowers.json` (commit it)

Every key is optional.

```json
{
  "repos": ["services/api", "apps/web"],
  "heavyJobs": {
    "build": { "slots": 1, "match": ["compiler-daemon", "bundler"] },
    "test":  { "slots": 2, "match": ["test-runner"] }
  },
  "loadFactor": 1.5,
  "cleanup": {
    "dockerImages": ["myproject-*"],
    "dockerVolumes": ["myproject_*"],
    "tmpGlobs": ["/tmp/myproject-*"]
  },
  "needsConsent": ["deploy", "publish"],
  "sensitivePaths": ["**/.env*", "**/secrets/**"],
  "handoffDir": ".",
  "handoffGlob": "HANDOFF-*.md",
  "cacheResumeMinutes": 45
}
```

| Key | Default | Meaning |
|---|---|---|
| `repos` | project root plus child dirs that are git repos | Repos scanned by `batch-cleanup` and the pre-compact checkpoint |
| `heavyJobs.<kind>.slots` / `.match` | none / 1 slot | Concurrency slots per kind of heavy job; `match` are process command-line substrings counted by `machine-budget` |
| `loadFactor` | 1.5 | `machine-budget` says wait when load1 exceeds `loadFactor x cores` |
| `cleanup.dockerImages` / `dockerVolumes` / `tmpGlobs` | empty | The only Docker/temp things `batch-cleanup` may remove |
| `cleanup.dirs` | empty | Regenerable build output `batch-cleanup` may remove: `{glob, minAgeMinutes, ask}`; relative globs apply inside each repo; skipped while a heavy job runs; `ask: true` only lists |
| `needsConsent` | empty | Command substrings the skills treat as needing explicit user consent |
| `sensitivePaths` | empty | Globs the skills treat as never to be printed or committed |
| `handoffDir`, `handoffGlob` | `.`, `HANDOFF-*.md` | Where the session-start hook looks for the newest handoff file |
| `cacheResumeMinutes` | 45 | Idle time after which a sub-agent counts as COLD in `jsp-agents` |

The project root is the git toplevel; if that has no config file, the nearest parent directory
that has one (handy for a workspace folder holding several repos).

### Per project, ephemeral: `<project root>/.jamie-superpowers/` (gitignore it)

Checkpoints written by the pre-compact hook (`checkpoints/`, newest 20 kept). The hook never edits
your files; it warns inside the checkpoint if the directory is not ignored.

### Per user: `${JSP_HOME:-$HOME/.claude/jamie-superpowers}/`

`prefs.json` (e.g. `language`, `statusline.yellow`, `statusline.red`), `agents.jsonl` (agent ledger)
and `denylist.txt` (terms `neutrality-lint` must never find in the plugin; one per line, `#` comments).

## Scripts (`scripts/`)

All accept `--help`.

| Script | Purpose |
|---|---|
| `jsp-config get <key> [default]` / `path` / `root` / `repos` | Read the project config with defaults applied |
| `jsp-pref get\|set\|unset <key> [value]` | User preferences |
| `machine-budget [--json]` | Cores, RAM, load, disk, heavy processes; ends with `VERDICT: ok max_heavy=N max_agents=N` or `VERDICT: wait reason=...` (exit 3) |
| `jsp-slot <kind> -- <cmd...>` / `status` | Run a heavy command inside a per-kind slot; waits while slots are busy or the machine is loaded |
| `batch-cleanup [--apply]` | Dry run by default; removes merged clean worktrees and branches, plus only the configured Docker/temp/build-output items |
| `jsp-agents log\|touch\|done\|list\|check` | Ledger of dispatched agents; `check` returns warm (0) or cold (2) |
| `changes-since <ref>` | Markdown changelog skeleton grouped by commit type |
| `neutrality-lint [path]` | Fails on personal paths, emails, secrets and denylist terms |
| `context-statusline` | Claude Code status line command |

Hooks (`hooks/`): `session-start` (SessionStart: skill text plus language, newest checkpoint on
compact/resume, newest handoff file, config presence) and `pre-compact` (PreCompact: writes a
checkpoint of branches, status, recent commits, worktrees, stashes and open agents).

## Status line

In `settings.json`, replacing the path with where the plugin lives:

```json
{
  "statusLine": { "type": "command", "command": "/path/to/jamie-superpowers/scripts/context-statusline" }
}
```

It shows `model · folder · branch · NN%`, with the percentage green below 50, yellow below 70
and red from there (plus `→ /compact`). Change the thresholds with
`jsp-pref set statusline.yellow 40` and `jsp-pref set statusline.red 60`.

## Auto-compaction threshold

Claude Code compacts automatically when the context is nearly full. To compact earlier, set the
environment variable `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` to a percentage, for example in
`settings.json`:

```json
{ "env": { "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "70" } }
```

A value near the status line's red threshold lets the red state warn you shortly before it triggers.
The pre-compact hook then saves a checkpoint and the session-start hook restores the key state.

## Development

Run `scripts/neutrality-lint` before every commit or release. Add your own project, product and
account names to the denylist file so they can never leak into this shared plugin.

## License

MIT. See `LICENSE` and `NOTICE.md`.
