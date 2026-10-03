#!/usr/bin/env bash
# One-time setup: a local venv with a bundled ffmpeg and Pillow. Needs macOS (`say`) and Google Chrome.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
command -v say >/dev/null || { echo "macOS 'say' not found (TTS requires macOS)"; exit 1; }
[ -x "${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}" ] || { echo "Google Chrome not found; set CHROME=/path/to/chrome"; exit 1; }
[ -d "$ROOT/.venv" ] || python3 -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/pip" install -q --disable-pip-version-check -r "$ROOT/requirements.txt"
"$ROOT/.venv/bin/python" -c "import imageio_ffmpeg, PIL; print('ok: ffmpeg', imageio_ffmpeg.get_ffmpeg_exe().split('/')[-1])"
