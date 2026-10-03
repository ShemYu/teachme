# Contributing

1. `scripts/setup.sh`, then `pip install -r requirements-dev.txt` into the same venv.
2. Run `pytest -q tests` (no Chrome, `say`, or network needed). Add a test for any bug you fix.
3. If you change output (scripts, theme, player, SKILL.md), rebuild `lessons/agentic-video-understanding` and `lessons/coding-interview-patterns` with `--validate` and look at the previews.
4. Bump `VERSION` (semver) and add a `CHANGELOG.md` entry.

New secret stores and input methods are one registered class or function each: see `scripts/secret_store.py` and `scripts/keys.py`. New visual components go in `scripts/visuals.py` (HTML) and `assets/theme.css` (styles), documented in `references/authoring.md` §6.
