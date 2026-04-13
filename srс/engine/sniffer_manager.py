import logging
import threading

from src.engine import Engine
from src.engine.backend import Backend, _FALLBACK_FILTER
from src.consts.logger import LOGGING_NAME
from src.engine import sniffer_filter_thread

from scapy.sendrecv import AsyncSniffer
from src.consts.enums import ConnectionError


class SnifferManager:
    def __init__(self, packet_callback):
        self.logger = logging.getLogger(LOGGING_NAME)
        self.iface   = Backend.get_connection_interface()

        # Начальный фильтр: точный если игра уже запущена, иначе широкий
        initial = Backend.get_packet_filter()
        self.filter = initial if initial else _FALLBACK_FILTER
        self.logger.info(f"Initial filter: {self.filter}")

        self.callback = packet_callback
        self._create_sniffer()
        self._start_filter_thread()

    def _create_sniffer(self):
        try:
            if self.iface == ConnectionError.InterfaceNotFound:
                raise Exception("No network interface found")
            self.sniffer = AsyncSniffer(
                iface=self.iface,
                filter=self.filter,
                prn=self.callback,
                store=False,
            )
            self.sniffer.start()
            self.logger.info(f"Sniffer started: iface={self.iface} filter={self.filter}")
        except Exception as e:
            self.logger.error(f"Sniffer init failed: {e}")
            self.sniffer = ConnectionError.InterfaceNotFound

    def change_sniffer_filter(self, new_filter: str):
        try:
            if hasattr(self.sniffer, "stop_cb"):
                self.sniffer.stop()
            self.filter = new_filter
            from src.engine.message_parser import MessageParser
            MessageParser.reset_packet_buffers()
            self._create_sniffer()
        except Exception as e:
            self.logger.error(f"change_sniffer_filter failed: {e}")

    def _start_filter_thread(self):
        t = threading.Thread(
            target=sniffer_filter_thread.observe_changing_ips,
            args=(self,),
            daemon=True,
        )
        t.start()


sniffer_manager = SnifferManager(Engine.queue_an_event)
