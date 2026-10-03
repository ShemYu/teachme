"""Small ElevenLabs REST helpers (free calls only): plan usage and voice lookup. Synthesis lives in common.Narrator."""
import json, time, urllib.error, urllib.request

API = "https://api.elevenlabs.io"


def _get(key, path):
    req = urllib.request.Request(f"{API}{path}", headers={"xi-api-key": key})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def subscription(key):
    """Plan and character usage, or None if the key lacks the user_read permission. Raises ValueError on a bad key."""
    try:
        d = _get(key, "/v1/user/subscription")
        return {"tier": d.get("tier"), "used": d.get("character_count"), "limit": d.get("character_limit"),
                "reset_unix": d.get("next_character_count_reset_unix")}
    except urllib.error.HTTPError as e:
        if e.code == 401 and "invalid_api_key" in e.read().decode("utf-8", "replace"):
            raise ValueError("ElevenLabs rejected this key (invalid_api_key)")
        return None
    except urllib.error.URLError:
        return None


def describe(s):
    if not s:
        return "plan usage: unavailable (key may lack the user_read permission; TTS can still work)"
    reset = time.strftime("%Y-%m-%d", time.localtime(s["reset_unix"])) if s.get("reset_unix") else "?"
    return f"plan: {s['tier']} · {s['used']:,} / {s['limit']:,} characters used · resets {reset}"


def voice_name(key, voice_id):
    """Name of the voice if this key can use it, else None."""
    try:
        return _get(key, f"/v1/voices/{voice_id}").get("name") or voice_id
    except urllib.error.HTTPError:
        return None


def voices(key):
    return _get(key, "/v1/voices")["voices"]
