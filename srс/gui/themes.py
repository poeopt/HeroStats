"""Система тем. Все стили — ТОЛЬКО через глобальный QSS по objectName."""
from typing import Literal

ThemeName = Literal["dark", "dark_red", "light", "light_blue"]

_P: dict[str, dict] = {
    "dark": {
        "name_ru": "Тёмная", "name_en": "Dark",
        "bg0": "#0a0707", "bg1": "#100808", "bg2": "#181212", "bg3": "#0f0e0d",
        "border1": "#1a0e0e", "border2": "#2a1414", "border3": "#3a1a1a",
        "text1": "#C3AF75", "text2": "#7a5030", "text3": "#4a2a1a", "text4": "#3a2010",
        "accent": "#CA1717", "mail_on": "#F6C94E", "mail_off": "#2a1a10",
        "scroll_bg": "#0a0808", "scroll_h": "#3a1414", "btn_brd2": "#5a1a1a",
    },
    "dark_red": {
        "name_ru": "Тёмно-красная", "name_en": "Dark Red",
        "bg0": "#080404", "bg1": "#0d0505", "bg2": "#140808", "bg3": "#0c0808",
        "border1": "#200808", "border2": "#3a0e0e", "border3": "#5a1010",
        "text1": "#E8A060", "text2": "#8a4030", "text3": "#5a2010", "text4": "#4a1a10",
        "accent": "#FF3030", "mail_on": "#FFD060", "mail_off": "#3a0808",
        "scroll_bg": "#080404", "scroll_h": "#5a0a0a", "btn_brd2": "#8a1010",
    },
    "light": {
        "name_ru": "Светлая", "name_en": "Light",
        "bg0": "#d0c8b8", "bg1": "#c8c0b0", "bg2": "#f0ede8", "bg3": "#e8e4dc",
        "border1": "#c0b8a8", "border2": "#b0a898", "border3": "#a09888",
        "text1": "#2a1a08", "text2": "#5a4020", "text3": "#8a6840", "text4": "#a08060",
        "accent": "#A02010", "mail_on": "#c06010", "mail_off": "#b0a080",
        "scroll_bg": "#d0c8b8", "scroll_h": "#9a9080", "btn_brd2": "#808070",
    },
    "light_blue": {
        "name_ru": "Синяя", "name_en": "Blue",
        "bg0": "#c0c8d8", "bg1": "#b8c0d0", "bg2": "#e8ecf4", "bg3": "#dde2ee",
        "border1": "#a8b4c8", "border2": "#9098b0", "border3": "#7880a0",
        "text1": "#0a1828", "text2": "#304060", "text3": "#607090", "text4": "#8090a8",
        "accent": "#1850A0", "mail_on": "#1060c0", "mail_off": "#8090b0",
        "scroll_bg": "#c0c8d8", "scroll_h": "#8090b8", "btn_brd2": "#5060a0",
    },
}

_current: ThemeName = "dark"

def set_theme(name: ThemeName) -> None:
    global _current
    _current = name

def get_theme() -> ThemeName:
    return _current

def get_theme_names() -> list[tuple[str, str, str]]:
    return [(k, v["name_ru"], v["name_en"]) for k, v in _P.items()]

def build_style(theme: ThemeName = None) -> str:
    p = _P.get(theme or _current, _P["dark"])
    return f"""
QWidget {{
    font-family: "CookieRun Bold";
    font-size: 13px;
    color: {p['text1']};
    background: transparent;
}}
/* ── Main ── */
QWidget#MainWidget  {{ background: {p['bg2']}; }}
QWidget#InnerWidget {{ background: {p['bg2']}; }}

/* ── Toolbar ── */
QWidget#Toolbar {{ background: {p['bg0']}; border-bottom: 1px solid {p['border1']}; }}
QPushButton#TbBtn {{
    background: {p['bg0']}; border: none; border-left: 1px solid {p['border1']};
    color: {p['text4']}; font-size: 10px; padding: 0 7px; min-height: 22px;
}}
QPushButton#TbBtn:hover   {{ background: {p['bg1']}; color: {p['text1']}; }}
QPushButton#TbBtn:checked {{ background: {p['bg1']}; color: {p['accent']}; }}
QPushButton#TbBtnDiscord {{
    background: {p['bg0']}; border: none; border-left: 1px solid {p['border1']};
    color: {p['text3']}; font-size: 10px; padding: 0 7px; min-height: 22px;
}}
QPushButton#TbBtnDiscord:hover {{ color: {p['text1']}; }}
QPushButton#TbBtnMin, QPushButton#TbBtnClose {{
    background: {p['bg0']}; border: none; border-left: 1px solid {p['border1']};
    font-size: 11px; min-width: 22px; min-height: 22px; color: {p['text4']};
}}
QPushButton#TbBtnMin:hover   {{ background: {p['bg1']}; color: {p['text1']}; }}
QPushButton#TbBtnClose:hover {{ background: {p['bg1']}; color: {p['accent']}; }}

/* ── HUD cells ── */
QFrame#GroupBox, QFrame#GroupBoxXL {{
    background: {p['bg3']};
    border: 1px solid {p['border2']};
    border-top: 1px solid {p['bg2']};
    border-bottom: 2px solid {p['border3']};
}}
QFrame#GroupBox QLabel, QFrame#GroupBoxXL QLabel {{
    background: transparent; color: {p['text1']};
}}

/* ── Character card ── */
QWidget#CharCard {{
    background: {p['bg0']}; border-bottom: 1px solid {p['border1']};
}}
QLabel#CharClass {{ color: {p['text3']}; font-size: 9px;  }}
QLabel#CharName  {{ color: {p['text1']}; font-size: 13px; }}
QLabel#CharLevel {{ color: {p['text3']}; font-size: 10px; }}
QLabel#Badge {{
    color: {p['text3']}; background: {p['bg1']};
    border: 1px solid {p['border2']}; border-radius: 3px; padding: 1px 6px;
}}

/* ── Session row ── */
QWidget#SessionRow {{ background: {p['bg2']}; border-bottom: 1px solid {p['border1']}; }}
QLabel#MailActive   {{ color: {p['mail_on']};  font-size: 12px; }}
QLabel#MailInactive {{ color: {p['mail_off']}; font-size: 10px; }}
QLabel#DeathLabel   {{ color: {p['accent']};   font-size: 10px; }}

/* ── Buttons ── */
QPushButton#ResetButton {{
    background: {p['bg1']}; border: 1px solid {p['border2']};
    border-bottom: 2px solid {p['btn_brd2']}; border-radius: 2px;
    color: {p['text1']}; font-size: 11px; padding: 1px 8px;
}}
QPushButton#ResetButton:hover {{ border-color: {p['accent']}; }}
QPushButton#CopyButton {{
    background: {p['bg1']}; border: 1px solid {p['border2']};
    border-radius: 2px; color: {p['text3']}; font-size: 11px; padding: 1px 5px;
}}
QPushButton#CopyButton:hover {{ color: {p['text1']}; }}

/* ── Collapsible ── */
QPushButton#CollapseBtn {{
    background: {p['bg1']}; border: none; border-top: 1px solid {p['border1']};
    color: {p['text3']}; font-size: 9px; letter-spacing: 1px;
    text-align: left; padding: 2px 8px; min-height: 15px;
}}
QPushButton#CollapseBtn:hover {{ color: {p['text2']}; }}
QWidget#CollapseBody {{ background: {p['bg2']}; }}

/* ── Zone panel ── */
QFrame#ZonePanel {{ background: {p['bg1']}; border-top: 1px solid {p['border1']}; border-bottom: 1px solid {p['border2']}; }}
QLabel#ZName  {{ color: {p['accent']}; font-size: 12px; font-weight: bold; }}
QLabel#BName  {{ color: {p['text1']}; font-size: 11px; }}
QLabel#BDesc  {{ color: {p['text3']}; font-size: 10px; }}
QLabel#NoZone {{ color: {p['text4']}; font-size: 10px; }}

/* ── ALL sub-windows ── */
QWidget#DropLogWindow, QWidget#ZoneWindow,
QWidget#ChaosWindow,   QWidget#SettingsWindow,
QWidget#FaqWindow {{
    background: {p['bg2']};
}}
QWidget#WinHeader {{
    background: {p['bg0']}; border-bottom: 1px solid {p['border1']};
}}
QLabel#WinTitle {{ color: {p['text3']}; font-size: 9px; letter-spacing: 1px; }}

/* ── Drop Log rows ── */
QWidget#DropRow {{ background: {p['bg3']}; border-bottom: 1px solid {p['border1']}; }}
QWidget#DropRow:hover {{ background: {p['bg1']}; }}

/* ── Zone window ── */
QWidget#ZoneRow {{ background: {p['bg3']}; border-bottom: 1px solid {p['border1']}; }}
QWidget#ZoneRowBest {{ background: {p['bg1']}; border-left: 3px solid {p['accent']}; border-bottom: 1px solid {p['border1']}; }}

/* ── Settings ── */
QPushButton#SettingsBtn {{
    background: {p['bg1']}; border: 1px solid {p['border2']};
    color: {p['text3']}; font-size: 10px; padding: 2px 10px; border-radius: 2px;
}}
QPushButton#SettingsBtn:hover {{ color: {p['text1']}; border-color: {p['text1']}; }}
QPushButton#SettingsBtn[active="true"] {{
    background: {p['bg1']}; border: 2px solid {p['accent']}; color: {p['accent']};
}}
QCheckBox#SettingsCb {{
    color: {p['text2']}; font-size: 11px; spacing: 6px;
}}
QCheckBox#SettingsCb::indicator {{
    width: 13px; height: 13px;
    border: 1px solid {p['border2']}; background: {p['bg3']}; border-radius: 2px;
}}
QCheckBox#SettingsCb::indicator:checked {{
    background: {p['accent']}88; border-color: {p['accent']};
}}

/* ── Scrollbars ── */
QScrollBar:vertical {{
    background: {p['scroll_bg']}; width: 5px; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {p['scroll_h']}; border-radius: 2px; min-height: 16px;
}}
QScrollBar::handle:vertical:hover {{ background: {p['accent']}88; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ height: 5px; background: {p['scroll_bg']}; }}
QScrollBar::handle:horizontal {{ background: {p['scroll_h']}; border-radius: 2px; }}

/* ── Inputs ── */
QLineEdit {{
    background: {p['bg3']}; border: 1px solid {p['border2']};
    color: {p['text2']}; font-size: 10px; padding: 1px 4px; border-radius: 2px;
}}
QLineEdit:focus {{ border-color: {p['accent']}; color: {p['text1']}; }}

QSlider#VolumeSlider::groove:horizontal {{ background: {p['border2']}; height: 4px; border-radius: 2px; }}
QSlider#VolumeSlider::handle:horizontal {{ background: {p['accent']}; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; }}
QSlider#VolumeSlider::sub-page:horizontal {{ background: {p['accent']}; border-radius: 2px; }}

QToolTip {{
    background: {p['bg1']}; color: {p['text1']};
    border: 1px solid {p['border2']}; padding: 4px 7px; font-size: 11px; border-radius: 2px;
}}
QProgressBar {{ background: {p['bg3']}; border: none; border-radius: 2px; }}
"""
