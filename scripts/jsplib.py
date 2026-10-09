"""Shared helpers for the jamie-superpowers scripts (python3, stdlib only)."""
import json
import os
import subprocess
import sys
import tempfile

CONFIG_NAME = ".jamie-superpowers.json"
STATE_NAME = ".jamie-superpowers"

DEFAULTS = {
    "heavyJobs": {},
    "loadFactor": 1.5,
    "cleanup": {"dockerImages": [], "dockerVolumes": [], "tmpGlobs": []},
    "needsConsent": [],
    "sensitivePaths": [],
    "handoffDir": ".",
    "handoffGlob": "HANDOFF-*.md",
    "cacheResumeMinutes": 45,
}


class ConfigError(Exception):
    pass


def run(args, cwd=None, timeout=15):
    """Run a command; return (returncode, stdout, stderr). Never raises."""
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except (OSError, subprocess.SubprocessError):
        return 127, "", ""


def git(cwd, *args):
    """Stdout of a git command (stripped), or None if it failed."""
    rc, out, _ = run(["git", "-C", cwd] + list(args))
    return out.rstrip() if rc == 0 else None


def project_root(cwd=None):
    """Directory holding the project config / state.

    The git toplevel; if it has no config file, the nearest parent directory
    that does (a workspace folder holding several repos); else the toplevel
    (or cwd when not inside a git repository).
    """
    cwd = os.path.realpath(cwd or os.getcwd())
    top = git(cwd, "rev-parse", "--show-toplevel")
    if top:
        top = os.path.realpath(top)
        if os.path.isfile(os.path.join(top, CONFIG_NAME)):
            return top
        d = os.path.dirname(top)
    else:
        d = cwd
    while True:
        if os.path.isfile(os.path.join(d, CONFIG_NAME)):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return top or cwd
        d = parent


def config_path(root):
    return os.path.join(root, CONFIG_NAME)


def state_dir(root):
    return os.path.join(root, STATE_NAME)


def _merge(base, over):
    out = dict(base)
    for k, v in over.items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def default_repos(root):
    found = []
    if os.path.exists(os.path.join(root, ".git")):
        found.append(".")
    try:
        names = sorted(os.listdir(root))
    except OSError:
        names = []
    for n in names:
        if n.startswith(".") or n == "node_modules":
            continue
        if os.path.exists(os.path.join(root, n, ".git")):
            found.append(n)
    return found


def load_config(root):
    """Project config merged over defaults. `repos` is always present."""
    path = config_path(root)
    user = {}
    if os.path.isfile(path):
        try:
            with open(path, encoding="utf-8") as f:
                user = json.load(f)
        except (OSError, ValueError) as e:
            raise ConfigError("invalid %s: %s" % (path, e))
        if not isinstance(user, dict):
            raise ConfigError("invalid %s: top level must be an object" % path)
    cfg = _merge(DEFAULTS, user)
    if "repos" not in user:
        cfg["repos"] = default_repos(root)
    return cfg


def load_config_safe(root):
    """Like load_config but falls back to defaults (for hooks)."""
    try:
        return load_config(root)
    except ConfigError:
        cfg = dict(DEFAULTS)
        cfg["repos"] = default_repos(root)
        return cfg


def repo_paths(root, cfg):
    return [os.path.normpath(os.path.join(root, r)) for r in cfg.get("repos", [])]


def dotted_get(obj, key):
    """Return (found, value) for a dotted key; list items by integer index."""
    cur = obj
    for part in key.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return False, None
    return True, cur


def fmt(value):
    """Plain text for scalars, JSON for containers."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def user_home():
    return os.environ.get("JSP_HOME") or os.path.join(os.path.expanduser("~"), ".claude", "jamie-superpowers")


def load_prefs():
    try:
        with open(os.path.join(user_home(), "prefs.json"), encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_prefs(prefs):
    home = user_home()
    os.makedirs(home, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=home, prefix=".prefs-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, os.path.join(home, "prefs.json"))


def wants_help(argv):
    return any(a in ("-h", "--help") for a in argv)


def die(msg, code=2):
    sys.stderr.write(msg + "\n")
    sys.exit(code)
