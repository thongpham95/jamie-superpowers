"""SessionStart hook: inject the using-jamie-superpowers skill plus per-session state.

Reads the hook JSON on stdin ({"source": startup|resume|clear|compact, "cwd": ...}) and prints
{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "..."}}.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
PLUGIN_ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PLUGIN_ROOT, "scripts"))
import jsplib as J  # noqa: E402

SKILL = os.path.join(PLUGIN_ROOT, "skills", "using-jamie-superpowers", "SKILL.md")


def read_input():
    if sys.stdin.isatty():
        return {}
    try:
        data = json.loads(sys.stdin.read() or "{}")
        return data if isinstance(data, dict) else {}
    except ValueError:
        return {}


def read_text(path, max_lines=None):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except OSError:
        return None
    return "\n".join(lines[:max_lines] if max_lines else lines)


def newest(paths, by_mtime=False):
    paths = [p for p in paths if os.path.isfile(p)]
    if not paths:
        return None
    return max(paths, key=os.path.getmtime) if by_mtime else max(paths)


def main():
    data = read_input()
    source = data.get("source") or "startup"
    cwd = data.get("cwd") or os.getcwd()
    root = J.project_root(cwd)
    cfg = J.load_config_safe(root)
    rel = lambda p: os.path.relpath(p, root)  # noqa: E731

    skill = read_text(SKILL) or "(skill file skills/using-jamie-superpowers/SKILL.md not found)"
    pref = os.path.join(PLUGIN_ROOT, "scripts", "jsp-pref")
    language = J.load_prefs().get("language")

    state = ["## Session state", "", "- Session source: %s" % source, "- Plugin root: %s" % PLUGIN_ROOT]
    if language:
        state.append("- Output language: %s. Write all outputs, including documents, in this language." % language)
    else:
        state.append(
            'LANGUAGE NOT SET: before your first substantive answer, ask the user which language to use for all '
            'outputs including documents (default English), then run "%s" set language <code>.' % pref)
    cfg_file = J.config_path(root)
    state.append("- Project config: %s" % (
        ".jamie-superpowers.json present" if os.path.isfile(cfg_file) else "none (defaults in use)"))

    if source in ("compact", "resume"):
        cp = newest(glob.glob(os.path.join(J.state_dir(root), "checkpoints", "*.md")))
        if cp:
            state += ["- Newest checkpoint: %s (first 40 lines below; read the file for the rest)" % rel(cp), "",
                      "~~~~", read_text(cp, 40) or "", "~~~~"]
        else:
            state.append("- Newest checkpoint: none")
    handoff = os.path.join(root, cfg["handoffDir"], cfg["handoffGlob"])
    ho = newest(glob.glob(handoff), by_mtime=True)
    state.append("- Newest handoff file: %s" % (rel(ho) if ho else "none"))

    context = (
        "<EXTREMELY_IMPORTANT>\nYou have jamie-superpowers.\n\n"
        "**Below is the full content of your 'jamie-superpowers:using-jamie-superpowers' skill - your introduction "
        "to using skills. For all other skills, use the 'Skill' tool:**\n\n%s\n\n%s\n</EXTREMELY_IMPORTANT>"
        % (skill, "\n".join(state)))
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}))


if __name__ == "__main__":
    main()
