"""List ElevenLabs voices available to your key (id, name, labels), to pick ELEVENLABS["voice_id"].

usage: .venv/bin/python scripts/tts_voices.py [filter]      (key from the secret registry: see keys.py)
"""
import sys
from secret_store import ELEVENLABS, get_secret
from elevenlabs_api import voices

key = get_secret(ELEVENLABS)[0] or sys.exit("no ElevenLabs key: run scripts/keys.py set")
want = (sys.argv[1] if len(sys.argv) > 1 else "").lower()
for v in voices(key):
    labels = ", ".join(f"{k}={x}" for k, x in (v.get("labels") or {}).items())
    line = f"{v['voice_id']}  {v['name']:<24} {labels}"
    if want in line.lower():
        print(line)
