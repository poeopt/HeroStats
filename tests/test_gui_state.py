import unittest
import sys
from unittest.mock import MagicMock

# Create dummy classes for Qt
class DummyQt:
    class WindowType:
        FramelessWindowHint = 1
        WindowStaysOnTopHint = 2
        Tool = 4
    class WidgetAttribute:
        WA_TranslucentBackground = 8
        WA_AlwaysShowToolTips = 16
        WA_TransparentForMouseEvents = 32
    class AlignmentFlag:
        AlignRight = 1
        AlignVCenter = 2
        AlignCenter = 4
    class MouseButton:
        LeftButton = 1

class DummyQWidget:
    def __init__(self, *args, **kwargs):
        pass
    def setObjectName(self, name):
        pass
    def setAttribute(self, attr, value):
        pass
    def setFixedSize(self, w, h):
        pass
    def setMinimumWidth(self, w):
        pass
    def setFixedHeight(self, h):
        pass
    def setWindowIcon(self, icon):
        pass
    def setWindowTitle(self, title):
        pass
    def setLayout(self, layout):
        pass
    def setStyleSheet(self, style):
        pass
    def show(self):
        pass
    def hide(self):
        pass
    def update(self):
        pass
    def move(self, x, y):
        pass
    def resize(self, w, h):
        pass
    def setWindowOpacity(self, o):
        pass
    def testAttribute(self, attr):
        return False
    def style(self):
        return MagicMock()
    def frameGeometry(self):
        m = MagicMock()
        m.topLeft.return_value = MagicMock()
        return m

# Mock PySide6 BEFORE importing our code
sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtCore'] = MagicMock()
sys.modules['PySide6.QtCore'].Qt = DummyQt
sys.modules['PySide6.QtWidgets'] = MagicMock()
sys.modules['PySide6.QtWidgets'].QWidget = DummyQWidget
sys.modules['PySide6.QtWidgets'].QMainWindow = DummyQWidget
sys.modules['PySide6.QtGui'] = MagicMock()

import src.gui.widgets.main as main_mod
import src.gui.windows.mini_overlay as mini_mod

class TestGUIHUDMode(unittest.TestCase):
    def test_mini_overlay_set_click_through(self):
        # We need to bypass __init__ because it calls a lot of things
        overlay = mini_mod.MiniOverlay.__new__(mini_mod.MiniOverlay)
        # Manually trigger what we need
        overlay.setAttribute = MagicMock()
        overlay.setWindowOpacity = MagicMock()
        overlay.update = MagicMock()

        overlay.set_click_through(True)
        overlay.setAttribute.assert_called_with(DummyQt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        overlay.setWindowOpacity.assert_called_with(0.8)

        overlay.set_click_through(False)
        overlay.setAttribute.assert_called_with(DummyQt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        overlay.setWindowOpacity.assert_called_with(1.0)

    def test_main_widget_toggle_lock(self):
        widget = main_mod.MainWidget.__new__(main_mod.MainWidget)
        widget.setAttribute = MagicMock()
        widget.update = MagicMock()
        widget._mo = MagicMock()
        widget._b_lock = MagicMock()

        widget._toggle_lock(True)
        self.assertTrue(widget._locked)
        widget.setAttribute.assert_called_with(DummyQt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        widget._mo.set_click_through.assert_called_with(True)

if __name__ == "__main__":
    unittest.main()
