import logging
from src.models.messages.base import BaseMessage
from src.consts.satanic_buffs import satanic_buffs
from src.consts.satanic_zone_names import satanic_zone_names
from src.utils import assets
from src.consts import assets as assets_const

_logger = logging.getLogger("hero_siege_stats")
_buff_names = list(satanic_buffs.keys())


class SzBuff:
    def __init__(self, sz_buff: int):
        idx = sz_buff - 1
        if 0 <= idx < len(_buff_names):
            self.buff_name = _buff_names[idx]
            entry = satanic_buffs.get(self.buff_name, {})
            # satanic_buffs может быть dict[str, str] или dict[str, dict]
            if isinstance(entry, dict):
                self.buff_description_en = entry.get("EN", "")
                self.buff_description_ru = entry.get("RU", "")
            else:
                self.buff_description_en = str(entry)
                self.buff_description_ru = str(entry)
        else:
            _logger.warning(f"Unknown buff id {sz_buff}")
            self.buff_name = f"Buff {sz_buff}"
            self.buff_description_en = ""
            self.buff_description_ru = ""

        try:
            buff_icon_name = assets_const.get_buff_icon(f"IcBuff_{sz_buff}")
        except (KeyError, AttributeError):
            buff_icon_name = assets_const.IcBuffDefault
        self.buff_icon = assets.icon(buff_icon_name)

    def get_description(self, lang: str = "EN") -> str:
        if lang == "RU" and self.buff_description_ru:
            return self.buff_description_ru
        return self.buff_description_en


class SzInfo:
    buffs: list
    satanic_zone: str

    def __init__(self, sz_zone: str, sz_buffs: str):
        self.buffs = []
        for buff_token in sz_buffs.split("|"):
            buff_token = buff_token.strip()
            if not buff_token:
                continue
            try:
                self.buffs.append(SzBuff(int(buff_token)))
            except (ValueError, Exception) as e:
                _logger.warning(f"Bad buff token '{buff_token}': {e}")

        parts = sz_zone.split("_")
        if len(parts) >= 3:
            try:
                sz_act = int(parts[1])
                sz_zone_id = int(parts[2])
                zone_names = satanic_zone_names.get(sz_act, [])
                if 1 <= sz_zone_id <= len(zone_names):
                    self.satanic_zone = f"Act {sz_act} : {zone_names[sz_zone_id - 1]}"
                else:
                    self.satanic_zone = sz_zone
            except (ValueError, IndexError):
                self.satanic_zone = sz_zone
        else:
            self.satanic_zone = sz_zone


class SatanicZoneMessage(BaseMessage):
    def __init__(self, msg_dict: dict):
        super().__init__(msg_dict)
        self.satanic_info = SzInfo(msg_dict['satanicZoneName'], msg_dict['buffs'])
