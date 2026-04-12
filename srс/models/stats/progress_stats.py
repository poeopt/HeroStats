class ProgressStats:
    def __init__(self):
        self.chaos_cleared:    int = 0
        self.chaos_bosses:     int = 0
        self.wormhole_levels:  list = [0] * 8
        self.wormhole_zone:    list = [0] * 8
        self.best_wormhole:    int = 0
        self.total_wormhole:   int = 0
        self._chaos_baseline:  int = -1

    @property
    def chaos_session(self) -> int:
        if self._chaos_baseline < 0:
            return 0
        return max(0, self.chaos_cleared - self._chaos_baseline)

    def update(self, msg) -> None:
        if self._chaos_baseline < 0:
            self._chaos_baseline = msg.chaos_towers_cleared
        self.chaos_cleared = msg.chaos_towers_cleared
        self.chaos_bosses  = msg.chaos_tower_boss_kills
        lvl = list(msg.wormhole_levels or [])[:8]
        zon = list(msg.wormhole_zone   or [])[:8]
        while len(lvl) < 8: lvl.append(0)
        while len(zon) < 8: zon.append(0)
        self.wormhole_levels = lvl
        self.wormhole_zone   = zon
        self.best_wormhole   = max(lvl)
        self.total_wormhole  = sum(lvl)

    def reset_session(self) -> None:
        self._chaos_baseline = self.chaos_cleared
