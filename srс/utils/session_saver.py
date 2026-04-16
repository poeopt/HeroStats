import json, datetime, logging
from src.utils.config import sessions_dir


def save_session(stats) -> None:
    try:
        d = sessions_dir()
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        acc = stats.account
        items = stats.added_items.added_items
        data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "character": {"name": acc.name, "class": acc.class_name,
                          "level": acc.level, "hero_level": acc.hero_level,
                          "mode": acc.mode_label, "difficulty": acc.diff_label},
            "session": {"duration": stats.session.get_duration_str()},
            "gold": {"total": stats.gold.total_gold,
                     "earned": stats.gold.total_gold_earned,
                     "per_hour": stats.gold.gold_per_hour},
            "xp":   {"total": stats.xp.total_xp,
                     "earned": stats.xp.total_xp_earned,
                     "per_hour": stats.xp.xp_per_hour},
            "items": {r: {"total": items[r]["total"], "mf": items[r]["mf"]}
                      for r in items},
        }
        path = d / f"session_{ts}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        # Keep last 20
        for old in sorted(d.glob("session_*.json"))[:-20]:
            old.unlink(missing_ok=True)
    except Exception as e:
        logging.getLogger("hero_siege_stats").error(f"Save session failed: {e}")


def list_sessions() -> list[dict]:
    try:
        result = []
        for f in sorted(sessions_dir().glob("session_*.json"), reverse=True)[:10]:
            try:
                result.append(json.loads(f.read_text(encoding="utf-8")))
            except Exception:
                pass
        return result
    except Exception:
        return []


def export_csv(path: str = None) -> str:
    """Экспортирует историю сессий в CSV. Возвращает путь к файлу."""
    import csv, os
    sessions = list_sessions()
    if not sessions:
        return ""
    if path is None:
        path = str(sessions_dir().parent / "sessions_export.csv")
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Date", "Character", "Class", "Level",
                         "Mode", "Difficulty", "Duration",
                         "Gold Earned", "Gold/h",
                         "XP Earned", "XP/h",
                         "Satanic", "Angelic", "Heroic"])
            for s in sessions:
                acc  = s.get("character", {})
                g    = s.get("gold", {})
                x    = s.get("xp", {})
                itm  = s.get("items", {})
                w.writerow([
                    s.get("timestamp", "")[:16],
                    acc.get("name", ""),     acc.get("class", ""),
                    acc.get("level", ""),    acc.get("mode", ""),
                    acc.get("difficulty", ""),
                    s.get("session", {}).get("duration", ""),
                    g.get("earned", 0),      g.get("per_hour", 0),
                    x.get("earned", 0),      x.get("per_hour", 0),
                    itm.get("Satanic",  {}).get("total", 0),
                    itm.get("Angelic",  {}).get("total", 0),
                    itm.get("Heroic",   {}).get("total", 0),
                ])
        return path
    except Exception as e:
        logging.getLogger("hero_siege_stats").error(f"CSV export failed: {e}")
        return ""
