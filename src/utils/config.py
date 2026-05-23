import json, os
from pathlib import Path

_DEFAULTS = {
    "lang": "EN",
    "theme": "dark",
    "volume": 80,
    "notify_satanic": True, "notify_angelic": True,
    "notify_heroic": True,  "sound_enabled": True,
    "save_sessions": True,
    "win_main":     {"x": -1, "y": -1},
    "win_drops":    {"x": -1, "y": -1},
    "win_zones":    {"x": -1, "y": -1},
    "win_settings": {"x": -1, "y": -1},
    "section_gold": True, "section_xp": True,
    "section_items": True, "section_zone": True,
    "section_chaos": False, "section_wormhole": False,
}
_cfg: dict = {}


def _path() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home())) / "HeroSiegeStats"
    else:
        base = Path.home() / ".HeroSiegeStats"
    base.mkdir(parents=True, exist_ok=True)
    return base / "config.json"


def _sessions_dir() -> Path:
    p = _path().parent / "sessions"
    p.mkdir(parents=True, exist_ok=True)
    return p


def load():
    global _cfg
    try:
        p = _path()
        if p.exists():
            _cfg = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        _cfg = {}
    for k, v in _DEFAULTS.items():
        if k not in _cfg:
            _cfg[k] = v


def save():
    try:
        _path().write_text(json.dumps(_cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def get(key: str):
    return _cfg.get(key, _DEFAULTS.get(key))


def set(key: str, value):
    _cfg[key] = value
    save()


def sessions_dir() -> Path:
    return _sessions_dir()
