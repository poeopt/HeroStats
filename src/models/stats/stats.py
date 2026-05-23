from src.models.stats.session import Session
from src.models.stats.account import Account, ProgressStats
from src.models.stats.gold import GoldStats
from src.models.stats.xp import XPStats
from src.models.stats.added_items import AddedItemsStats
from src.models.stats.satanic_zone import SatanicZoneStats
from src.models.stats.drop_log import DropLog
from src.models.stats.zone_stats import ZoneEfficiency


class Stats:
    def __init__(self, session=None, account=None, progress=None,
                 gold_stats=None, xp_stats=None, added_items=None,
                 satanic_zone=None, drop_log=None, zone_eff=None,
                 death_count: int = 0):
        self.session      = session      or Session()
        self.account      = account      or Account()
        self.progress     = progress     or ProgressStats()
        self.gold         = gold_stats   or GoldStats()
        self.xp           = xp_stats     or XPStats()
        self.added_items  = added_items  or AddedItemsStats()
        self.satanic_zone = satanic_zone or SatanicZoneStats()
        self.drop_log     = drop_log     or DropLog()
        self.zone_eff     = zone_eff     or ZoneEfficiency()
        self.death_count  = death_count
