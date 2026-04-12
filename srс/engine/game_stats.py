import logging
from src.consts.logger import LOGGING_NAME
from src.consts.sets import ItemsRarity
from src.models.stats.stats import Stats
from src.models.stats.session import Session
from src.models.stats.account import Account, ProgressStats
from src.models.stats.gold import GoldStats
from src.models.stats.xp import XPStats
from src.models.stats.fortune import FortuneStats
from src.models.stats.added_items import AddedItemsStats
from src.models.stats.satanic_zone import SatanicZoneStats
from src.models.stats.drop_log import DropLog
from src.models.stats.zone_stats import ZoneEfficiency
from src.models.events.base import BaseEvent
from src.models.events.gold import GoldEvent
from src.models.events.xp import XPEvent
from src.models.events.account import AccountEvent
from src.models.events.mail import MailEvent
from src.models.events.added_item import AddedItemEvent
from src.models.events.satanic_zone import SatanicZoneEvent


class GameStats:
    def __init__(self):
        self._log = logging.getLogger(LOGGING_NAME)
        self._mail_cbs: list = []
        self._init()

    def _init(self):
        self.session      = Session()
        self.account      = Account()
        self.progress     = ProgressStats()
        self.gold         = GoldStats()
        self.xp           = XPStats()
        self.fortune      = FortuneStats()
        self.added_items  = AddedItemsStats()
        self.satanic_zone = SatanicZoneStats()
        self.drop_log     = DropLog()
        self.zone_eff     = ZoneEfficiency()
        self.season_mode: str | None = None
        self.death_count: int = 0

    def on_mail(self, cb):
        self._mail_cbs.append(cb)

    def process_event(self, event: BaseEvent):
        if isinstance(event, GoldEvent):
            self.gold.update(currencyData=event.value, season_mode=self.season_mode)

        elif isinstance(event, XPEvent):
            self.xp.add(event.value)

        elif isinstance(event, AccountEvent):
            msg = event.value
            self.account.update_from_message(msg)
            self.progress.update(msg)
            self.xp.update(total_xp=msg.experience)
            self.season_mode = msg.get_current_season_mode()

        elif isinstance(event, MailEvent):
            was = self.session.has_mail
            self.session.update(has_mail=bool(event.value))
            if not was and self.session.has_mail:
                for cb in self._mail_cbs:
                    try: cb()
                    except Exception: pass

        elif isinstance(event, AddedItemEvent):
            self.added_items.update(added_item_object=event.value)
            self.drop_log.add(event.value)
            rarity = ItemsRarity.get(str(event.value.rarity), "")
            self.zone_eff.add_drop(rarity)

        elif isinstance(event, SatanicZoneEvent):
            prev = self.satanic_zone.satanic_zone_info
            self.satanic_zone.update(event.value)
            new  = self.satanic_zone.satanic_zone_info
            prev_name = prev.satanic_zone if prev else None
            new_name  = new.satanic_zone  if new  else None
            if new_name and new_name != prev_name:
                self._log.info(f"Zone: {prev_name!r} → {new_name!r}")
                self.zone_eff.enter_zone(new_name, self.gold.total_gold, self.xp.total_xp)

    def reset(self):
        saved_account  = self.account
        saved_progress = self.progress
        saved_mode     = self.season_mode
        saved_log      = self.drop_log
        saved_mail_cbs = self._mail_cbs
        self._init()
        self.account      = saved_account
        self.progress     = saved_progress
        self.season_mode  = saved_mode
        self.drop_log     = saved_log
        self._mail_cbs    = saved_mail_cbs
        self.drop_log.reset()
        self.progress.reset_session()

    def update_hourly_stats(self):
        self.gold.update(
            gold_per_hour=self.session.calculate_value_per_hour(self.gold.total_gold_earned))
        self.xp.update(
            xp_per_hour=self.session.calculate_value_per_hour(self.xp.total_xp_earned))
        ph = {}
        for rid in ItemsRarity:
            ph[ItemsRarity[rid]] = self.session.calculate_value_per_hour(
                self.added_items.added_items[ItemsRarity[rid]]['total'])
        self.added_items.update(items_per_hour=ph)
        # Real-time zone snapshot
        self.zone_eff.snapshot(self.gold.total_gold, self.xp.total_xp)

    def get_stats(self) -> Stats:
        self.update_hourly_stats()
        return Stats(
            session=self.session, account=self.account, progress=self.progress,
            gold_stats=self.gold, xp_stats=self.xp, added_items=self.added_items,
            satanic_zone=self.satanic_zone, drop_log=self.drop_log,
            zone_eff=self.zone_eff, death_count=self.death_count,
        )
