"""
Backend — поиск сетевого интерфейса и IP-адреса игрового сервера.

ВАЖНО: максимально близко к оригиналу GuilhermeFaga/hero-siege-stats.
Оригинал работал на Win10/11. Мы добавляем только минимальные fallback-ы.
"""
import logging
import socket
import subprocess
import psutil

from scapy.interfaces import get_working_ifaces
from scapy.interfaces import NetworkInterface

from src.consts.enums import ConnectionError
from src.consts.logger import LOGGING_NAME
from src.consts.connectivity_test_hosts import (
    CONNECTIVITY_HOSTS, CONNECTIVITY_TEST_PORT, CONNECTION_TIMEOUT
)

# Используется в message_parser.py — НЕ УДАЛЯТЬ
PROTOCOL_SIGNATURES = {
    "json_start":    "{",
    "special_start": "x",
    "min_length":    30,
    "excluded_keys": ["inventory_charms", "steam"],
}

_FALLBACK_FILTER = "tcp and len > 30"


class Backend:

    @staticmethod
    def get_open_connections_from_process() -> set:
        """
        Оригинальная логика + fallback через netstat.
        Возвращает set IP-адресов игрового сервера.
        """
        logger = logging.getLogger(LOGGING_NAME)
        pid: int = 0
        hs_ips: set = set()

        # Шаг 1: найти PID процесса (оригинальная логика)
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                name = proc.info.get("name") or ""
                if name == "Hero_Siege.exe":
                    pid = proc.info["pid"]
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if pid == 0:
            logger.debug("Hero_Siege.exe not found in process list")
            return hs_ips

        logger.info(f"Found Hero_Siege.exe PID={pid}")

        # Шаг 2: ОРИГИНАЛЬНЫЙ метод — psutil.net_connections глобально
        # Работает на Win10/11 при запуске от администратора
        try:
            connections = psutil.net_connections(kind="inet")
            for conn in connections:
                if conn.pid == pid and conn.raddr:
                    hs_ips.add(conn.raddr.ip)
                    logger.info(f"[net_connections] IP: {conn.raddr.ip}:{conn.raddr.port}")
        except psutil.AccessDenied as e:
            logger.warning(f"net_connections AccessDenied: {e}")
        except Exception as e:
            logger.warning(f"net_connections error: {e}")

        # Шаг 3: fallback через netstat если шаг 2 не дал результатов
        # netstat работает без особых прав на обеих версиях Windows
        if not hs_ips:
            logger.info("Trying netstat fallback...")
            try:
                result = subprocess.run(
                    ["netstat", "-n", "-o"],
                    capture_output=True, text=True, timeout=5,
                    creationflags=0x08000000,  # CREATE_NO_WINDOW
                )
                pid_str = str(pid)
                for line in result.stdout.splitlines():
                    parts = line.split()
                    # netstat -n -o: Proto Local Foreign State PID
                    if len(parts) >= 5 and parts[-1] == pid_str and "ESTABLISHED" in line:
                        foreign = parts[2]
                        # Убираем порт: 1.2.3.4:9000 → 1.2.3.4
                        ip = foreign.rsplit(":", 1)[0].strip("[]")
                        if ip and not ip.startswith("0.") and not ip.startswith("127."):
                            hs_ips.add(ip)
                            logger.info(f"[netstat] IP: {ip}")
            except Exception as e:
                logger.warning(f"netstat fallback error: {e}")

        if hs_ips:
            logger.info(f"Game server IPs: {hs_ips}")
        else:
            logger.warning(
                f"Hero_Siege.exe found (PID {pid}) but no server IPs detected. "
                "Make sure the program runs as Administrator."
            )

        return hs_ips

    @staticmethod
    def get_packet_filter() -> str:
        hs_ips = Backend.get_open_connections_from_process()
        if not hs_ips:
            # Пустая строка = не менять текущий фильтр (sniffer_filter_thread проверяет это)
            return ""
        f = f"(host {' or host '.join(hs_ips)}) and len > 30"
        logging.getLogger(LOGGING_NAME).info(f"BPF filter: {f}")
        return f

    @staticmethod
    def get_interfaces() -> list[NetworkInterface]:
        return get_working_ifaces()

    @staticmethod
    def check_internet_connection() -> str | None:
        logger = logging.getLogger(LOGGING_NAME)
        for host in CONNECTIVITY_HOSTS:
            try:
                with socket.create_connection(
                    (host, CONNECTIVITY_TEST_PORT), timeout=CONNECTION_TIMEOUT
                ) as s:
                    ip = s.getsockname()[0]
                    logger.info(f"Internet check OK, local IP: {ip}")
                    return ip
            except (TimeoutError, socket.gaierror, OSError) as e:
                logger.debug(f"Internet check via {host} failed: {e}")
        logger.error("All internet connectivity checks failed")
        return None

    @staticmethod
    def get_connection_interface() -> str | ConnectionError:
        logger = logging.getLogger(LOGGING_NAME)
        connection_iface_ip = Backend.check_internet_connection()

        if connection_iface_ip is None:
            return ConnectionError.NoInternet

        interfaces = Backend.get_interfaces()

        def is_valid_physical_interface(iface: NetworkInterface) -> bool:
            return (
                "OK" in iface.flags
                and iface.ip
                and "Virtual"  not in iface.description
                and "Hyper-V"  not in iface.description
            )

        # Точное совпадение IP
        for iface in interfaces:
            if is_valid_physical_interface(iface) and iface.ip == connection_iface_ip:
                logger.info(f"Found matching interface: {iface.description}")
                return iface.description

        # Любой физический
        for iface in interfaces:
            if is_valid_physical_interface(iface):
                logger.info(f"Using physical interface: {iface.description}")
                return iface.description

        # Fallback — любой рабочий
        for iface in interfaces:
            if "OK" in iface.flags and iface.ip:
                logger.warning(f"Fallback interface: {iface.description}")
                return iface.description

        logger.error("No suitable network interface found")
        return ConnectionError.InterfaceNotFound
