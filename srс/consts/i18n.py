from typing import Literal
Lang = Literal["RU", "EN"]
_current: Lang = "EN"

_S: dict[str, dict[str, str]] = {
    "waiting":          {"EN": "Waiting for game...",    "RU": "Ожидание игры..."},
    "no_mail":          {"EN": "No mail",                "RU": "Нет почты"},
    "mail":             {"EN": "Mail!",                  "RU": "Почта!"},
    "copy":             {"EN": "⎘ Copy",                 "RU": "⎘ Копия"},
    "copy_done":        {"EN": "✓ Done",                 "RU": "✓ Готово"},
    "reset":            {"EN": "Reset",                  "RU": "Сброс"},
    "win_drops":        {"EN": "Drop Log",               "RU": "Лог дропов"},
    "win_zones":        {"EN": "Zone Efficiency",        "RU": "Эффективность зон"},
    "win_settings":     {"EN": "Settings",               "RU": "Настройки"},
    "win_faq":          {"EN": "FAQ",                    "RU": "Справка"},
    "no_drops":         {"EN": "No drops yet",           "RU": "Дропов нет"},
    "no_zones":         {"EN": "Enter a Satanic Zone",   "RU": "Войдите в Satanic Zone"},
    "toast_satanic":    {"EN": "Satanic drop!",          "RU": "Сатанинский дроп!"},
    "toast_angelic":    {"EN": "Angelic drop!",          "RU": "Ангелический дроп!"},
    "toast_unholy":     {"EN": "Unholy drop!",           "RU": "Нечестивый дроп!"},
    "toast_heroic":     {"EN": "Heroic drop!",           "RU": "Героический дроп!"},
    "toast_mail":       {"EN": "✉ Mail arrived!",        "RU": "✉ Пришла почта!"},
    "lang":             {"EN": "Language",               "RU": "Язык"},
    "notifications":    {"EN": "Notifications",          "RU": "Уведомления"},
    "sound":            {"EN": "Sound",                  "RU": "Звук"},
    "save_sessions":    {"EN": "Save sessions",          "RU": "Сохранять сессии"},
    "history":          {"EN": "Session history",        "RU": "История сессий"},
    "gold":             {"EN": "Gold",                   "RU": "Золото"},
    "experience":       {"EN": "Experience",             "RU": "Опыт"},
    "items":            {"EN": "Angelic · Heroic · Satanic", "RU": "Ангел · Героич · Сатаник"},
    "zone":             {"EN": "Satanic Zone",           "RU": "Сатаническая Зона"},
    "chaos_tower":      {"EN": "Chaos Tower",            "RU": "Башня Хаоса"},
    "wormhole":         {"EN": "Wormhole",               "RU": "Вормхол"},
    "drops_btn":        {"EN": "Drops",                  "RU": "Дропы"},
    "zones_btn":        {"EN": "Zones",                  "RU": "Зоны"},
    "note_placeholder": {"EN": "Strategy note...",       "RU": "Заметка о стратегии..."},
    "clear":            {"EN": "clear",                  "RU": "очистить"},
    "total_time":       {"EN": "Total time",             "RU": "Всего времени"},
    "best":             {"EN": "Best zone",              "RU": "Лучшая зона"},
    "deaths":           {"EN": "Deaths",                 "RU": "Смертей"},
    "enter_zone":       {"EN": "Enter Satanic Zone to start tracking", "RU": "Войдите в Satanic Zone для отслеживания"},
}


def set_lang(lang: Lang) -> None:
    global _current
    _current = lang


def get_lang() -> Lang:
    return _current


def t(key: str) -> str:
    entry = _S.get(key)
    if entry is None:
        return key
    return entry.get(_current, entry.get("EN", key))
