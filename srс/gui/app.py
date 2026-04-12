import logging, sys
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QIcon
from scapy.sendrecv import AsyncSniffer

from src.gui.widgets.main import MainWidget
from src.gui.messages.error import ErrorMessages
from src.gui.messages.version import VersionMessages
from src.gui.styling import style
from src.consts.enums import ConnectionError
from src.consts import assets as ac
from src.consts.logger import LOGGING_NAME
from src.utils import assets
from src.utils.version import current_version as cur_ver
from src.utils.version import latest_version  as lat_ver
from src.utils.icon_fix import icon_fix


def run():
    log = logging.getLogger(LOGGING_NAME)
    icon_fix()
    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont(assets.font("cookierunbold.ttf"))
    QFontDatabase.addApplicationFont(assets.font("otsutomefont.ttf"))
    app.setStyleSheet(style)
    app.setStyle("fusion")

    ico = QIcon()
    ico.addFile(assets.icon(ac.IcLogo16),  QSize(16,16))
    ico.addFile(assets.icon(ac.IcLogo24),  QSize(24,24))
    ico.addFile(assets.icon(ac.IcLogo256), QSize(256,256))
    app.setWindowIcon(ico)

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
