# Security

## Reporting a vulnerability

Please report security issues privately through GitHub's **Report a vulnerability** button (Security → Advisories) on this repository, not in a public issue. Include steps to reproduce and the version from `VERSION`.

## How secrets are handled

- API keys are read from the environment or an OS keychain via `scripts/secret_store.py`; they are never written to files in the repo, never passed on a command line (stores receive them on stdin), and never printed in full.
- `keys.py set` reads the value from a hidden terminal prompt or a native password dialog, so a coding agent that runs it never sees the value.
- A key inside `lesson.py` is refused at build time.
- The only network calls go to `https://api.elevenlabs.io`, and only when you build with `--tts elevenlabs`.

## Trust model

`lesson.py` and `focus_cues.py` are Python and run with your permissions when you build; the player inlines lesson HTML. Only build lessons you trust.
