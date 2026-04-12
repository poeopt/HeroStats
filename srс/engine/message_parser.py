import json
import logging
import re

from scapy.all import Packet
from scapy.layers.inet import IP
from scapy.layers.inet import TCP

from src.consts.logger import LOGGING_NAME
from src.models.events.base import BaseEvent
from src.models.events.gold import GoldEvent
from src.models.events.xp import XPEvent
from src.models.events.account import AccountEvent
from src.models.events.mail import MailEvent
from src.models.events.added_item import AddedItemEvent
from src.models.events.satanic_zone import SatanicZoneEvent

from src.models.messages.gold import GoldMessage
from src.models.messages.xp import XPMessage
from src.models.messages.account import AccountMessage
from src.models.messages.mail import MailMessage
from src.models.messages.added_item import AddedItemMessage
from src.models.messages.satanic_zone import SatanicZoneMessage

from src.consts import events as consts
from src.engine.backend import PROTOCOL_SIGNATURES


_continuos_packets: dict[str, list[str]] = {}
_last_src_ack: dict[str, str] = {}


class MessageParser:
    @staticmethod
    def capture(message, src, dst):
        logger = logging.getLogger(LOGGING_NAME)
        try:
            match = re.search("{.+}", str(message))
            if match is None:
                if len(message) <= 100:
                    return None
                if message[0] != PROTOCOL_SIGNATURES["special_start"]:
                    return None
                truncated_message = message[3:]
                try:
                    import base64
                    if "[INV]" in truncated_message:
                        jwt_token = truncated_message.split("[INV]")[1]
                        decoded = base64.b64decode(jwt_token)
                        return json.loads(decoded)
                    elif "&" not in truncated_message:
                        decoded = base64.b64decode(truncated_message)
                        return json.loads(decoded)
                    else:
                        from urllib.parse import parse_qs
                        parsed = parse_qs(truncated_message)
                        return {k: v[0] for k, v in parsed.items()}
                except Exception as e:
                    logger.debug(f"Message parsing failed: {e}")
                    return None
            msg = match.group(0)
            try:
                parsed = json.loads(msg)
                if any(key in parsed for key in PROTOCOL_SIGNATURES["excluded_keys"]):
                    return None
                return parsed
            except json.JSONDecodeError:
                return None
        except Exception as e:
            logger.error(f"Error in Capture: {e}")
            return None

    @staticmethod
    def message_to_event(msg_list: list):
        logger = logging.getLogger(LOGGING_NAME)
        try:
            if not msg_list:
                return None
            events: list[BaseEvent] = []
            for msg_dict in msg_list:
                try:
                    event_name = MessageParser.identify_event(msg_dict)
                    if event_name is None:
                        continue
                    # FIX: if/elif вместо if/if/if — только одна ветка срабатывает
                    if event_name == consts.EvNameUpdateGold:
                        events.append(GoldEvent(GoldMessage(msg_dict)))
                    elif event_name == consts.EvNameUpdateXP:
                        events.append(XPEvent(XPMessage(msg_dict)))
                    elif event_name == consts.EvNameUpdateAccount:
                        events.append(AccountEvent(AccountMessage(msg_dict)))
                    elif event_name == consts.EvNameUpdateMail:
                        events.append(MailEvent(MailMessage(msg_dict)))
                    elif event_name == consts.EvNameItemAdded:
                        events.append(AddedItemEvent(AddedItemMessage(msg_dict)))
                    elif event_name == consts.EvNameUpdateSatanicZone:
                        events.append(SatanicZoneEvent(SatanicZoneMessage(msg_dict)))
                except Exception as e:
                    logger.warning(f"Error processing message: {e}")
                    continue
            return events if events else None
        except Exception as e:
            logger.error(f"Error in message_to_event: {e}")
            return None

    @staticmethod
    def identify_event(msg_dict: dict):
        logger = logging.getLogger(LOGGING_NAME)
        try:
            if not isinstance(msg_dict, dict):
                return None
            if "steam" in msg_dict:
                return None
            if "currencyData" in msg_dict or "currency_data" in msg_dict:
                return consts.EvNameUpdateGold
            elif "totalGuildXp" in msg_dict:
                return consts.EvNameUpdateXP
            elif "mail" in msg_dict.get("message", ""):
                return consts.EvNameUpdateMail
            elif "addedItemObject" in msg_dict:
                return consts.EvNameItemAdded
            elif "satanicZoneName" in msg_dict:
                return consts.EvNameUpdateSatanicZone
            elif "experience" in msg_dict:
                return consts.EvNameUpdateAccount
            return None
        except Exception as e:
            logger.error(f"Error identifying event: {e}")
            return None

    @staticmethod
    def packet_to_event(packet: Packet):
        logger = logging.getLogger(LOGGING_NAME)
        try:
            if IP not in packet or TCP not in packet:
                return None
            try:
                packet.load
            except AttributeError:
                return None

            result_messages = []
            packet_src = str(packet[IP].src)
            packet_key = str(packet[TCP].ack)

            try:
                _last_src_ack.setdefault(packet_src, packet_key)
                _continuos_packets.setdefault(packet_key, [])
                _continuos_packets[packet_key].append(str(packet.load))

                if packet_key != _last_src_ack[packet_src]:
                    old_key = _last_src_ack[packet_src]
                    if old_key in _continuos_packets:
                        load = "".join(_continuos_packets.pop(old_key))
                        load = load.replace("'b'", "")
                        for possible_msg in load.split("\\"):
                            msg = MessageParser.capture(possible_msg, packet_src, packet[IP].dst)
                            if msg is not None:
                                result_messages.append(msg)
                    else:
                        logger.debug(f"Missing packet buffer key: {old_key}")
                _last_src_ack[packet_src] = packet_key
            except Exception as e:
                logger.error(f"Error assembling packet: {e}")
                return None

            if not result_messages:
                return None
            return MessageParser.message_to_event(result_messages)
        except Exception as e:
            logger.error(f"Error in packet_to_event: {e}")
            return None

    @staticmethod
    def reset_packet_buffers():
        global _continuos_packets, _last_src_ack
        _continuos_packets.clear()
        _last_src_ack.clear()
