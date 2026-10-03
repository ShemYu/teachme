"""Pluggable secret storage for teachme (registry pattern).

A *secret* is something the tools need (e.g. the ElevenLabs API key). A *backend* is a place secrets can live
(environment, macOS Keychain, …). Backends register themselves by name; lookups walk them in order.

    from secret_store import ELEVENLABS, get_secret
    value, where = get_secret(ELEVENLABS)          # (None, None) if no backend has it

Lookup order: $TEACHME_SECRET_BACKENDS (comma-separated names) if set, else DEFAULT_ORDER, skipping
backends that aren't available on this machine. `store_secret` writes to the first available writable backend.

Adding a backend (e.g. 1Password, Vault, AWS Secrets Manager) is one class:

    @register
    class OnePassword(SecretBackend):
        name, writable = "1password", False
        def available(self):  return shutil.which("op") is not None
        def get(self, secret):
            r = subprocess.run(["op", "read", f"op://Private/{secret.id}/credential"], capture_output=True, text=True)
            return (r.stdout.strip() or None) if r.returncode == 0 else None

then add its name to DEFAULT_ORDER (or to $TEACHME_SECRET_BACKENDS). Rules every backend must follow:
never print or log a value, and never pass one on a command line (argv is visible to other processes): use stdin.
"""
import os, re, shutil, subprocess, sys
from dataclasses import dataclass

APP = "teachme"


@dataclass(frozen=True)
class Secret:
    id: str                 # stable name, also the account/key name inside backends
    label: str              # human-readable, shown in prompts
    env: str                # environment variable that overrides every stored copy
    pattern: str = r"^[A-Za-z0-9_\-]{20,200}$"   # validation before storing; also keeps values shell/argv-safe

    def valid(self, value):
        return bool(value) and re.match(self.pattern, value) is not None


ELEVENLABS = Secret("elevenlabs", "ElevenLabs API key", "ELEVENLABS_API_KEY")
SECRETS = {s.id: s for s in (ELEVENLABS,)}


# ---------------------------------------------------------------- registry
REGISTRY = {}
DEFAULT_ORDER = ["env", "keychain", "secret-tool"]


def register(cls):
    REGISTRY[cls.name] = cls
    return cls


class SecretBackend:
    name = ""
    writable = False

    def available(self):
        return True

    def get(self, secret):
        raise NotImplementedError

    def set(self, secret, value):
        raise NotImplementedError(f"backend {self.name} is read-only")

    def delete(self, secret):
        raise NotImplementedError(f"backend {self.name} is read-only")

    def where(self, secret):
        return self.name


def backends():
    """Available backend instances, in lookup order."""
    order = [n.strip() for n in os.environ.get("TEACHME_SECRET_BACKENDS", "").split(",") if n.strip()] or DEFAULT_ORDER
    unknown = [n for n in order if n not in REGISTRY]
    if unknown:
        sys.exit(f"unknown secret backend(s) {unknown}; registered: {sorted(REGISTRY)}")
    return [b for b in (REGISTRY[n]() for n in order) if b.available()]


def get_secret(secret):
    """(value, where) from the first backend that has it, or (None, None)."""
    for b in backends():
        v = b.get(secret)
        if v:
            return v, b.where(secret)
    return None, None


def store_secret(secret, value, backend=None):
    if not secret.valid(value):
        raise ValueError(f"that doesn't look like a valid {secret.label}")
    target = next((b for b in backends() if b.writable and (backend is None or b.name == backend)), None)
    if not target:
        raise RuntimeError(f"no writable secret backend available{f' named {backend}' if backend else ''}; "
                           f"set {secret.env} in your environment instead")
    target.set(secret, value)
    return target.where(secret)


def delete_secret(secret):
    """Remove from every writable backend; returns where it was removed from."""
    return [b.where(secret) for b in backends() if b.writable and b.delete(secret)]


def mask(value):
    return f"{value[:3]}…{value[-4:]}" if value and len(value) > 10 else "…"


# ---------------------------------------------------------------- built-in backends
@register
class EnvBackend(SecretBackend):
    """Read-only: the secret's environment variable (CI, or a one-off override)."""
    name = "env"

    def get(self, secret):
        return os.environ.get(secret.env, "").strip() or None

    def where(self, secret):
        return f"env {secret.env}"


@register
class MacKeychain(SecretBackend):
    """macOS login Keychain via `security`. Writes go through `security -i` on stdin, never argv."""
    name, writable = "keychain", True

    def available(self):
        return sys.platform == "darwin" and shutil.which("security") is not None

    def get(self, secret):
        r = subprocess.run(["security", "find-generic-password", "-s", APP, "-a", secret.id, "-w"],
                           capture_output=True, text=True)
        return (r.stdout.strip() or None) if r.returncode == 0 else None

    def set(self, secret, value):
        assert secret.valid(value)            # the pattern guarantees no quotes/spaces can break the command
        cmd = f'add-generic-password -U -s {APP} -a {secret.id} -l "{APP} {secret.label}" -w "{value}"\n'
        r = subprocess.run(["security", "-i"], input=cmd, capture_output=True, text=True)
        if r.returncode != 0 or r.stderr.strip():
            raise RuntimeError(f"Keychain write failed: {r.stderr.strip() or r.returncode}")

    def delete(self, secret):
        return subprocess.run(["security", "delete-generic-password", "-s", APP, "-a", secret.id],
                              capture_output=True).returncode == 0

    def where(self, secret):
        return f"macOS Keychain ({APP}/{secret.id})"


@register
class SecretTool(SecretBackend):
    """Linux Secret Service (GNOME Keyring, KWallet) via libsecret's `secret-tool`; value passed on stdin.
    Not exercised by the macOS test run."""
    name, writable = "secret-tool", True

    def available(self):
        return sys.platform.startswith("linux") and shutil.which("secret-tool") is not None

    def get(self, secret):
        r = subprocess.run(["secret-tool", "lookup", "service", APP, "account", secret.id], capture_output=True, text=True)
        return (r.stdout.strip() or None) if r.returncode == 0 else None

    def set(self, secret, value):
        r = subprocess.run(["secret-tool", "store", f"--label={APP} {secret.label}", "service", APP, "account", secret.id],
                           input=value, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"secret-tool store failed: {r.stderr.strip()}")

    def delete(self, secret):
        return subprocess.run(["secret-tool", "clear", "service", APP, "account", secret.id],
                              capture_output=True).returncode == 0

    def where(self, secret):
        return f"Secret Service ({APP}/{secret.id})"
