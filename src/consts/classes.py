"""
Классы Hero Siege и система сложности.
Difficulty:
  0 = Normal
  1 = Nightmare (Кошмар)
  2 = Hell (Ад) — подуровни 1-5
  3 = Inferno (Инферно)

hell_subdifficulty: 0-5 для Hell
"""

CLASS_NAMES: dict[int, str] = {
    0:  "Ranger",        1:  "Witch Doctor",  2:  "Sorceress",
    3:  "Warrior",       4:  "Necromancer",   5:  "Nomad",
    6:  "Paladin",       7:  "Pirate",        8:  "Lich",
    9:  "Barbarian",     10: "Shaman",        11: "Warden",
    12: "Phantom",       13: "Viking",        14: "Samurai",
    15: "Pyromancer",    16: "Amazon",        17: "Illusionist",
    18: "Marauder",      19: "Shaman",        20: "Plague Doctor",
    21: "Prophet",       22: "White Mage",    23: "Shield Lancer",
    24: "Stormweaver",   25: "Demon Slayer",  26: "Exo",
    27: "Jotunn",        28: "Redneck",       29: "Marksman",
    30: "Butcher",
}

# Правильные названия сложностей Hero Siege
_DIFF_EN = {
    0: "Normal",
    1: "Nightmare",
    2: "Hell",
    3: "Inferno",
}
_DIFF_RU = {
    0: "Нормал",
    1: "Кошмар",
    2: "Ад",
    3: "Инферно",
}

MODE_LABELS = {
    "GSS": {"EN": "Season",      "RU": "Сезон"},
    "GSH": {"EN": "Season HC",   "RU": "Сезон HC"},
    "GNS": {"EN": "Normal",      "RU": "Обычный"},
    "GNH": {"EN": "Normal HC",   "RU": "Обычный HC"},
    "GBP": {"EN": "Blood Pact",  "RU": "Кровавый пакт"},
}


def get_difficulty_label(difficulty: int, hell_sub: int, lang: str = "EN") -> str:
    names = _DIFF_RU if lang == "RU" else _DIFF_EN
    base  = names.get(difficulty, f"Diff {difficulty}")
    # Hell имеет подуровни 1-5
    if difficulty == 2 and hell_sub > 0:
        return f"{base} {hell_sub}"
    return base


def get_mode_label(mode: str, lang: str = "EN") -> str:
    entry = MODE_LABELS.get(mode)
    if entry:
        return entry.get(lang, entry.get("EN", mode))
    return mode
