satanic_buffs = {
    "Loot Goblin I":     {"EN": "+1 Maximum Loot from Enemy Killed",           "RU": "+1 макс. лут с убитого врага"},
    "Loot Goblin II":    {"EN": "+2 Maximum Loot from Enemy Killed",           "RU": "+2 макс. лут с убитого врага"},
    "Rune Master":       {"EN": "15%+(2.5%/sublvl) Rune Drop Chance",         "RU": "15%+(2.5%/ур.) шанс дропа рун"},
    "Gold Hunger":       {"EN": "Gold from kills +40%+(8.75%/sublvl)",         "RU": "Золото с убийств +40%+(8.75%/ур.)"},
    "Heroic Windfall":   {"EN": "Heroic drop +3%+(3%/sublvl)",                "RU": "Героич. дроп +3%+(3%/ур.)"},
    "Angelic Fortune":   {"EN": "Angelic drop +25%+(7.5%/sublvl)",            "RU": "Ангел. дроп +25%+(7.5%/ур.)"},
    "Zephys Grace":      {"EN": "Movement Speed +50%",                        "RU": "Скорость передвижения +50%"},
    "Zephy's Grace":     {"EN": "Movement Speed +50%",                        "RU": "Скорость передвижения +50%"},
    "Fury of Tempest":   {"EN": "Attack Speed +60%",                          "RU": "Скорость атаки +60%"},
    "Rapid Casting":     {"EN": "Cast Rate +60%",                             "RU": "Скорость каста +60%"},
    "Onslaught":         {"EN": "Attack Damage +100%",                        "RU": "Урон атаки +100%"},
    "Nether Surge":      {"EN": "Magic Skill Damage +40%",                    "RU": "Урон магии +40%"},
    "Relic Keepers":     {"EN": "Ancient monsters 2% chance to drop relic",   "RU": "Древние 2% шанс дропа реликвии"},
    "Goblin's Greed":    {"EN": "Champions+ 0.5% summon Treasure Goblin",     "RU": "Чемпионы+ 0.5% призыв гоблина"},
    "Artifact Digger":   {"EN": "+55% Magic Find+(5%/sublvl)",                "RU": "+55% Магич. поиск+(5%/ур.)"},
    "Artifact Seeker":   {"EN": "+110% Magic Find+(10%/sublvl)",              "RU": "+110% Магич. поиск+(10%/ур.)"},
    "Artifact Excavator":{"EN": "+170% Magic Find+(20%/sublvl)",              "RU": "+170% Магич. поиск+(20%/ур.)"},
    "Recruit":           {"EN": "+10% Experience+(2.5%/sublvl)",              "RU": "+10% Опыт+(2.5%/ур.)"},
    "Combat Training":   {"EN": "+15% Experience+(3.75%/sublvl)",             "RU": "+15% Опыт+(3.75%/ур.)"},
    "Battle Scarred":    {"EN": "+20% Experience+(5%/sublvl)",                "RU": "+20% Опыт+(5%/ур.)"},
    "Clairvoyance":      {"EN": "All recovery +100%",                         "RU": "Всё восстановление +100%"},
    "Aftermath":         {"EN": "Monsters 3% spawn Legion version on death",  "RU": "Монстры 3% призывают легиона при смерти"},
    "Deep Cuts":         {"EN": "Critical Strike damage +200%",               "RU": "Урон крита +200%"},
    "Old Town":          {"EN": "+15% chance for Ancient Packs",              "RU": "+15% шанс Древних стай"},
    "Terror Zone":       {"EN": "+25% chance for Ancient Packs",              "RU": "+25% шанс Древних стай"},
    "Fields of Carnage": {"EN": "+30% chance for Ancient Packs",              "RU": "+30% шанс Древних стай"},
    "Card Collector":    {"EN": "Increased Fortune Card drop chance",         "RU": "Повышен шанс карт Фортуны"},
    "Relic Feast":       {"EN": "Increased Relic drop chance",                "RU": "Повышен шанс реликвий"},
    "Spelunker":         {"EN": "Increased hidden area chance",               "RU": "Повышен шанс скрытых зон"},
    "Riftwalker":        {"EN": "Increased Rift Portal spawn",                "RU": "Повышен шанс порталов разлома"},
    "Experienced":       {"EN": "Increased Incarnation XP",                  "RU": "Повышен опыт Инкарнации"},
    "Land of Chaos":     {"EN": "Chaos Tower modifiers increased",            "RU": "Усилены модификаторы Башни Хаоса"},
    "Mimicry":           {"EN": "Monsters mimic player skills",               "RU": "Монстры копируют навыки игрока"},
    "Chaos Density":     {"EN": "More monsters in Chaos Tower",               "RU": "Больше монстров в Башне Хаоса"},
}


def get_buff_description(buff_name: str, lang: str = "EN") -> str:
    entry = satanic_buffs.get(buff_name, {})
    if isinstance(entry, dict):
        return entry.get(lang, entry.get("EN", ""))
    return str(entry)
