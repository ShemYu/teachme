"""Manage teachme secrets (API keys) safely.

usage: .venv/bin/python scripts/keys.py set [SECRET] [--backend NAME] [--input macos-dialog|tty|zenity]
       .venv/bin/python scripts/keys.py check [SECRET]     # where it's read from (masked) + provider status
       .venv/bin/python scripts/keys.py forget [SECRET]    # remove from every writable backend
       .venv/bin/python scripts/keys.py backends           # registered storage backends and input methods
SECRET defaults to "elevenlabs".

`set` asks for the value with the first usable input method: a hidden terminal prompt when there is a TTY;
otherwise (run by a coding agent: Claude Code, Cursor, Codex…) a native password dialog, so the value never
enters the agent's chat. Values are never printed in full, written to files, or passed on a command line.
Storage backends live in secret_store.py; input methods are registered below the same way.
"""
import argparse, getpass, shutil, subprocess, sys
import secret_store as ss

# ---------------------------------------------------------------- input methods (registry)
INPUTS = {}


def input_method(name, usable):
    def deco(fn):
        INPUTS[name] = (usable, fn); return fn
    return deco


@input_method("tty", lambda: sys.stdin.isatty())
def ask_tty(secret):
    return getpass.getpass(f"{secret.label} (input hidden): ")


@input_method("macos-dialog", lambda: sys.platform == "darwin" and shutil.which("osascript"))
def ask_macos(secret):
    script = f'''
set r to display dialog "Paste your {secret.label}.\\n\\nIt is stored by teachme's secret backend and never shown to the coding agent." ¬
  default answer "" with hidden answer with title "teachme · {secret.label}" with icon note ¬
  buttons {{"Cancel", "Save"}} default button "Save" cancel button "Cancel" giving up after 180
if gave up of r then error number -128
return text returned of r
'''
    print("opening a macOS dialog (waiting up to 3 minutes)…", flush=True)
    r = subprocess.run(["osascript", "-"], input=script, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("cancelled or timed out: nothing saved" if "-128" in r.stderr else f"dialog failed: {r.stderr.strip()}")
    return r.stdout


@input_method("zenity", lambda: sys.platform.startswith("linux") and shutil.which("zenity"))
def ask_zenity(secret):  # not exercised by the macOS test run
    r = subprocess.run(["zenity", "--password", f"--title=teachme · {secret.label}", "--timeout=180"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("cancelled or timed out: nothing saved")
    return r.stdout


def ask(secret, method=None):
    if method:
        usable, fn = INPUTS.get(method) or sys.exit(f"unknown input method {method!r}; have {sorted(INPUTS)}")
        return fn(secret).strip()
    for name, (usable, fn) in INPUTS.items():
        if usable():
            return fn(secret).strip()
    sys.exit(f"no way to ask for the value here: set {secret.env} in your environment instead")


# ---------------------------------------------------------------- provider status (verify a value before saving)
def status(secret, value):
    """One line about the value from its provider, or exit if the provider rejects it."""
    if secret is ss.ELEVENLABS:
        import elevenlabs_api as el
        try:
            s = el.subscription(value)
        except ValueError as e:
            sys.exit(str(e))
        return el.describe(s)
    return ""


def main():
    ap = argparse.ArgumentParser(description="Manage teachme secrets (API keys) safely.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, help_ in [("set", "ask for the value (hidden), verify it, store it"),
                        ("check", "show where the value is read from (masked) and its provider status"),
                        ("forget", "remove it from every writable backend")]:
        p = sub.add_parser(name, help=help_)
        p.add_argument("secret", nargs="?", default="elevenlabs", choices=sorted(ss.SECRETS))
        if name == "set":
            p.add_argument("--backend", help="store in this backend instead of the first writable one")
            p.add_argument("--input", choices=sorted(INPUTS), help="force an input method")
    sub.add_parser("backends", help="list storage backends and input methods")
    a = ap.parse_args()

    if a.cmd == "backends":
        avail = {b.name for b in ss.backends()}
        print("storage (lookup order):")
        for n, cls in ss.REGISTRY.items():
            print(f"  {n:<12} {'available' if n in avail else 'not available here':<20} {'read/write' if cls.writable else 'read-only'}")
        print("input methods:")
        for n, (usable, _) in INPUTS.items():
            print(f"  {n:<12} {'usable now' if usable() else 'not usable here'}")
        return
    secret = ss.SECRETS[a.secret]
    if a.cmd == "set":
        value = ask(secret, a.input)
        if not value:
            sys.exit("empty: nothing saved")
        if not secret.valid(value):
            sys.exit(f"that doesn't look like a valid {secret.label}: nothing saved")
        line = status(secret, value)                      # provider rejects a bad value here, before storing
        try:
            where = ss.store_secret(secret, value, a.backend)
        except (ValueError, RuntimeError) as e:
            sys.exit(str(e))
        print(f"saved {ss.mask(value)} to {where}" + (f"\n  {line}" if line else ""))
    elif a.cmd == "check":
        value, where = ss.get_secret(secret)
        if not value:
            sys.exit(f"no {secret.label}: run `keys.py set {secret.id}`, or export {secret.env}")
        print(f"{secret.label} {ss.mask(value)} from {where}")
        line = status(secret, value)
        if line:
            print(f"  {line}")
    elif a.cmd == "forget":
        gone = ss.delete_secret(secret)
        print(f"removed from {', '.join(gone)}" if gone else "nothing stored")


if __name__ == "__main__":
    main()
