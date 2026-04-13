import time
import logging
from typing import TYPE_CHECKING
from src.engine.backend import Backend
from src.consts.logger import LOGGING_NAME

if TYPE_CHECKING:
    from src.engine.sniffer_manager import SnifferManager


def observe_changing_ips(sniffer_manager: "SnifferManager") -> None:
    """
    Оригинальная логика из GuilhermeFaga/hero-siege-stats.
    Периодически проверяет IP сервера и обновляет BPF фильтр.
    """
    logger = logging.getLogger(LOGGING_NAME)
    while True:
        try:
            new_filter = Backend.get_packet_filter()
            # Обновляем только если фильтр не пустой и изменился
            if new_filter and new_filter != sniffer_manager.filter:
                logger.info(f"Filter: {sniffer_manager.filter!r} → {new_filter!r}")
                sniffer_manager.change_sniffer_filter(new_filter)
        except Exception as e:
            logger.error(f"Filter thread error: {e}")
        time.sleep(1)
