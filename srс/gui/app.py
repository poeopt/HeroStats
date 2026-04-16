import logging, sys
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QIcon
from scapy.sendrecv import AsyncSniffer

from src.gui.widgets.main import MainWidget
from src.gui.messages.error import ErrorMessages
from src.gui.messages.version import VersionMessages
from src.consts.enums import ConnectionError
from src.consts import assets as ac
from src.consts.logger import LOGGING_NAME
from src.utils import assets
from src.utils.version import current_version as cur_ver
from src.utils.version import latest_version  as lat_ver
from src.utils.icon_fix import icon_fix


def _check_npcap_on_start() -> bool:
    """Тихая проверка Npcap при старте. Показывает предупреждение если не найден."""
    import os, subprocess
    try:
        paths = [r"C:\Windows\System32\Npcap", r"C:\Windows\SysWOW64\Npcap"]
        for p in paths:
            if os.path.exists(p):
                return True
        result = subprocess.run(
            ["sc", "query", "npcap"],
            capture_output=True, text=True, timeout=3,
            creationflags=0x08000000)
        return "RUNNING" in result.stdout or "STOPPED" in result.stdout
    except:
        return False


def run():
    log = logging.getLogger(LOGGING_NAME)
    icon_fix()
    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont(assets.font("cookierunbold.ttf"))
    QFontDatabase.addApplicationFont(assets.font("otsutomefont.ttf"))
    app.setStyle("fusion")

    ico = QIcon()
    ico.addFile(assets.icon(ac.IcLogo16),  QSize(16,16))
    ico.addFile(assets.icon(ac.IcLogo24),  QSize(24,24))
    ico.addFile(assets.icon(ac.IcLogo256), QSize(256,256))
    app.setWindowIcon(ico)

    # Проверяем Npcap (особенно важно для Win11 LTSC/IoT)
    if sys.platform == "win32" and not _check_npcap_on_start():
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setWindowTitle("Hero Siege Stats — Зависимость не найдена")
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(
            "Npcap не установлен!\n\n"
            "Hero Siege Stats требует Npcap для перехвата сетевого трафика.\n\n"
            "Нажмите OK чтобы перейти на страницу загрузки,\n"
            "или Cancel чтобы продолжить (программа не будет получать данные)."
        )
        msg.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        if msg.exec() == QMessageBox.StandardButton.Ok:
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl("https://npcap.com/#download"))

    widget = MainWidget()
    widget.setWindowTitle("Hero Siege Stats")
    widget.show()

    try:
        cv = cur_ver(); lv = lat_ver()
        if lv and cv != lv:
            VersionMessages.outdated_version(widget)
    except Exception:
        pass

    from src.engine.sniffer_manager import sniffer_manager
    if isinstance(sniffer_manager.sniffer, ConnectionError):
        log.error(f"Sniffer error: {sniffer_manager.sniffer}")
        if sniffer_manager.sniffer == ConnectionError.InterfaceNotFound:
            ErrorMessages.get_message(widget, sniffer_manager.sniffer)
        # NoInternet — продолжаем, версия не критична

    try:
        sys.exit(app.exec())
    except SystemExit as e:
        log.info(f"Exit {e.code}")
    finally:
        log.info("Shutdown")
        try:
            from src.engine.sniffer_manager import sniffer_manager as sm
            if isinstance(sm.sniffer, AsyncSniffer) and sm.sniffer.running:
                sm.sniffer.stop()
        except Exception:
            pass
