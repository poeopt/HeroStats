from src.consts.classes import CLASS_NAMES, get_difficulty_label, get_mode_label
from src.consts.i18n import get_lang


class Account:
    def __init__(self):
        self.name = "—"
        self.class_id = -1
        self.class_name = "—"
        self.level = 0
        self.hero_level = 0
        self.mode = ""
        self.mode_label = "—"
        self.difficulty = 0
        self.hell_sub = 0
        self.diff_label = "—"
        self.is_hardcore = False
        self.playtime = 0

    def update_from_message(self, msg) -> None:
        lang = get_lang()
        self.name       = msg.name
        self.class_id   = msg.class_id
        self.class_name = CLASS_NAMES.get(msg.class_id, f"Class {msg.class_id}")
        self.level      = msg.level
        self.hero_level = msg.herolevel
        self.difficulty = msg.difficulty
        self.hell_sub   = msg.hell_subdifficulty
        self.diff_label = get_difficulty_label(msg.difficulty, msg.hell_subdifficulty, lang)
        self.is_hardcore = bool(msg.hardcore)
        self.playtime   = getattr(msg, 'playtime', 0)
        raw_mode        = msg.get_current_season_mode()
        self.mode       = raw_mode
        self.mode_label = get_mode_label(raw_mode, lang)

    def retranslate(self) -> None:
        if self.class_id >= 0:
            lang = get_lang()
            self.diff_label = get_difficulty_label(self.difficulty, self.hell_sub, lang)
            self.mode_label = get_mode_label(self.mode, lang)


class ProgressStats:
    def __init__(self):
        self.chaos_cleared = 0
        self.chaos_bosses  = 0
        self.wormhole_lvls = [0] * 8
        self.best_worm     = 0
        self.total_worm    = 0
        self._baseline     = -1

    @property
    def chaos_session(self) -> int:
        if self._baseline < 0:
            return 0
        return max(0, self.chaos_cleared - self._baseline)

    def update(self, msg) -> None:
        if self._baseline < 0:
            self._baseline = msg.chaos_towers_cleared
        self.chaos_cleared = msg.chaos_towers_cleared
        self.chaos_bosses  = msg.chaos_tower_boss_kills
        raw = msg.wormhole_levels or []
        lvls = list(raw)[:8]
        while len(lvls) < 8:
            lvls.append(0)
        self.wormhole_lvls = lvls
        self.best_worm  = max(lvls)
        self.total_worm = sum(lvls)

    def reset_session(self):
        self._baseline = self.chaos_cleared
