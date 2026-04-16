import datetime
from dataclasses import dataclass
from src.models.messages.added_item import AddedItemObject
from src.consts.sets import ItemsRarity

_NOTIFY = {"Satanic", "Angelic", "Heroic", "Unholy"}
_MAX = 50
_DEDUP_MS = 300  # Игнорировать повторный дроп того же предмета в течение 300ms


@dataclass
class DropEntry:
    time:      str
    rarity:    str
    tier:      int
    quality:   int
    sockets:   int
    mf_drop:   bool
    rarity_id: int


class DropLog:
    def __init__(self):
        self.entries: list[DropEntry] = []
        self._cbs: list = []
        # Дедупликация: (rarity, tier, quality) → последний timestamp
        self._last_seen: dict = {}

    def on_notable_drop(self, cb):
        self._cbs.append(cb)

    def add(self, obj: AddedItemObject):
        rarity = ItemsRarity.get(str(obj.rarity), f"R{obj.rarity}")

        # Дедупликация — игнорируем повторный одинаковый предмет в течение 300ms
        key = (obj.rarity, obj.tier, obj.drop_quality)
        now = datetime.datetime.now()
        last = self._last_seen.get(key)
        if last is not None:
            delta_ms = (now - last).total_seconds() * 1000
            if delta_ms < _DEDUP_MS:
                return  # Дубль — пропускаем
        self._last_seen[key] = now

        entry = DropEntry(
            time=now.strftime("%H:%M:%S"),
            rarity=rarity,
            tier=obj.tier,
            quality=obj.drop_quality,
            sockets=obj.sockets,
            mf_drop=bool(obj.mf_drop),
            rarity_id=obj.rarity,
        )
        self.entries.insert(0, entry)
        if len(self.entries) > _MAX:
            self.entries = self.entries[:_MAX]

        if rarity in _NOTIFY:
            for cb in self._cbs:
                try:
                    cb(entry)
                except Exception:
                    pass

    def reset(self):
        self.entries.clear()
        self._last_seen.clear()
