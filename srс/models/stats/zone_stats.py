import datetime
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ZoneNote:
    text: str
    time: str = field(default_factory=lambda: datetime.datetime.now().strftime("%H:%M"))


@dataclass
class ZoneRecord:
    name: str
    seconds: float = 0.0
    gold_earned: int = 0
    xp_earned: int = 0
    satanic: int = 0
    angelic: int = 0
    heroic: int = 0
    visits: int = 0
    notes: list = field(default_factory=list)
    _enter_time: datetime.datetime = field(default_factory=datetime.datetime.now)
    _gold_ref: int = 0
    _xp_ref: int = 0

    def gph(self) -> int:
        h = self.seconds / 3600
        return int(self.gold_earned / h) if h > 0.001 else 0

    def xph(self) -> int:
        h = self.seconds / 3600
        return int(self.xp_earned / h) if h > 0.001 else 0

    def sat_ph(self) -> float:
        h = self.seconds / 3600
        return round(self.satanic / h, 2) if h > 0.001 else 0.0

    def ang_ph(self) -> float:
        h = self.seconds / 3600
        return round(self.angelic / h, 2) if h > 0.001 else 0.0

    def minutes(self) -> float:
        return round(self.seconds / 60, 1)

    def score(self) -> float:
        return self.gph() / 1000.0 + self.xph() / 10000.0 + self.sat_ph() * 100


class ZoneEfficiency:
    def __init__(self):
        self._records: dict[str, ZoneRecord] = {}
        self._current_name: Optional[str] = None

    def enter_zone(self, name: str, gold: int, xp: int):
        # Finalise previous zone
        if self._current_name and self._current_name in self._records:
            rec = self._records[self._current_name]
            elapsed = (datetime.datetime.now() - rec._enter_time).total_seconds()
            rec.seconds += elapsed
            rec.gold_earned += max(0, gold - rec._gold_ref)
            rec.xp_earned   += max(0, xp   - rec._xp_ref)
        # Start new
        if name not in self._records:
            self._records[name] = ZoneRecord(name=name)
        rec = self._records[name]
        rec.visits += 1
        rec._enter_time = datetime.datetime.now()
        rec._gold_ref = gold
        rec._xp_ref   = xp
        self._current_name = name

    def snapshot(self, gold: int, xp: int):
        """Called every 500ms — updates current zone in real-time."""
        if not self._current_name or self._current_name not in self._records:
            return
        rec = self._records[self._current_name]
        elapsed = (datetime.datetime.now() - rec._enter_time).total_seconds()
        # Temporarily set for display — will be committed on next enter_zone
        rec._display_seconds     = elapsed
        rec._display_gold_earned = max(0, gold - rec._gold_ref)
        rec._display_xp_earned   = max(0, xp   - rec._xp_ref)

    def get_records(self) -> dict[str, ZoneRecord]:
        """Return records with live current-zone data merged in."""
        if not self._current_name or self._current_name not in self._records:
            return self._records
        rec = self._records[self._current_name]
        # Merge display values
        if hasattr(rec, '_display_seconds'):
            rec.seconds     = rec.seconds + rec._display_seconds if rec.visits > 1 else rec._display_seconds
            rec.gold_earned = rec.gold_earned + rec._display_gold_earned if rec.visits > 1 else rec._display_gold_earned
            rec.xp_earned   = rec.xp_earned + rec._display_xp_earned if rec.visits > 1 else rec._display_xp_earned
        return self._records

    def add_drop(self, rarity: str):
        if not self._current_name or self._current_name not in self._records:
            return
        rec = self._records[self._current_name]
        if rarity == "Satanic":   rec.satanic += 1
        elif rarity in ("Angelic","Unholy"): rec.angelic += 1
        elif rarity == "Heroic":  rec.heroic  += 1

    def add_note(self, zone_name: str, text: str):
        if zone_name in self._records and text.strip():
            self._records[zone_name].notes = [ZoneNote(text=text.strip())]

    def sorted_records(self, key: str = "score") -> list[ZoneRecord]:
        fn = {
            "score": lambda r: r.score(),
            "gph":   lambda r: r.gph(),
            "xph":   lambda r: r.xph(),
            "sat":   lambda r: r.sat_ph(),
            "time":  lambda r: r.minutes(),
        }.get(key, lambda r: r.score())
        return sorted(self.get_records().values(), key=fn, reverse=True)

    def reset(self):
        self._records.clear()
        self._current_name = None
