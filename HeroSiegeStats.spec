# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('assets', 'assets/'), ('src', 'src/')]
binaries = []
hiddenimports = ['scapy.all', 'scapy.layers.all', 'scapy.layers.inet', 'scapy.sendrecv', 'scapy.arch', 'scapy.arch.windows', 'scapy.arch.windows.native', 'src.utils.single_instance', 'src.utils.config', 'src.utils.sound', 'src.utils.session_saver', 'src.consts.i18n', 'src.consts.classes', 'src.consts.satanic_buffs', 'src.models.stats.drop_log', 'src.models.stats.zone_stats', 'src.models.stats.account', 'src.gui.components.zone_panel', 'src.gui.components.collapsible', 'src.gui.components.progress_panel', 'src.gui.windows.drop_log_window', 'src.gui.windows.zone_window', 'src.gui.windows.settings_window', 'src.gui.windows.faq_window', 'src.gui.widgets.toast']
tmp_ret = collect_all('scapy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('psutil')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['hero-siege-stats.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='HeroSiegeStats',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\icons\\logo.ico'],
)
