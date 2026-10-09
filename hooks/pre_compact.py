"""PreCompact hook: write a checkpoint of the working state before the context is compacted.

Reads {"trigger": auto|manual, "custom_instructions": ..., "cwd": ...} on stdin and writes
<project root>/.jamie-superpowers/checkpoints/<UTC timestamp>-<trigger>.md (newest 20 kept).
Never edits project files and never fails the compaction.
"""
import datetime
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")
sys.path.insert(0, SCRIPTS)
import jsplib as J  # noqa: E402

KEEP = 20


def section(title, body):
    return ["### " + title, "```", body.strip() or "(none)", "```", ""]


def repo_report(repo, root):
    name = os.path.relpath(repo, root)
    lines = ["## Repo: %s" % name, ""]
    if not os.path.exists(os.path.join(repo, ".git")):
        return lines + ["(not a git repository)", ""]
    branch = J.git(repo, "branch", "--show-current") or "(detached) " + (J.git(repo, "rev-parse", "--short", "HEAD") or "?")
    status = (J.git(repo, "status", "--short") or "").splitlines()
    shown = "\n".join(status[:30]) + ("\n... %d more" % (len(status) - 30) if len(status) > 30 else "")
    lines += ["- Branch: `%s`" % branch, ""]
    lines += section("git status --short", shown)
    lines += section("Last 5 commits", J.git(repo, "log", "-5", "--oneline", "--decorate") or "")
    lines += section("Worktrees", J.git(repo, "worktree", "list") or "")
    lines += section("Stashes", J.git(repo, "stash", "list") or "")
    return lines


def main():
    data = {}
    if not sys.stdin.isatty():
        try:
            data = json.loads(sys.stdin.read() or "{}")
        except ValueError:
            pass
    if not isinstance(data, dict):
        data = {}
    trigger = "".join(c for c in str(data.get("trigger") or "manual") if c.isalnum()) or "manual"
    cwd = data.get("cwd") or os.getcwd()
    root = J.project_root(cwd)
    if not (os.path.exists(os.path.join(root, ".git")) or os.path.isfile(J.config_path(root))):
        return  # not a project: leave the directory untouched
    cfg = J.load_config_safe(root)
    now = datetime.datetime.now(datetime.timezone.utc)

    out = ["# Checkpoint %s (%s)" % (now.strftime("%Y-%m-%d %H:%M:%SZ"), trigger), "", "- Trigger: %s" % trigger]
    if data.get("custom_instructions"):
        out += ["- Custom instructions: %s" % str(data["custom_instructions"]).strip()]
    out.append("")
    for repo in J.repo_paths(root, cfg) or [root]:
        out += repo_report(repo, root)
    agents = os.path.join(SCRIPTS, "jsp-agents")
    _, listing, _ = J.run([sys.executable, agents, "list"], cwd=root)
    out += ["## Open agents", ""] + section("jsp-agents list", listing)

    d = os.path.join(J.state_dir(root), "checkpoints")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "%s-%s.md" % (now.strftime("%Y%m%dT%H%M%SZ"), trigger))
    if os.path.exists(os.path.join(root, ".git")):
        rc, _, _ = J.run(["git", "-C", root, "check-ignore", "-q", path])
        if rc != 0:
            out.insert(3, "- WARNING: .jamie-superpowers/ is not ignored by git in this repo; add it to .gitignore.")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    for old in sorted(glob.glob(os.path.join(d, "*.md")))[:-KEEP]:
        try:
            os.unlink(old)
        except OSError:
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # never block compaction
        sys.stderr.write("jamie-superpowers pre-compact: %s\n" % e)
    print("{}")
