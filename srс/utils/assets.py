import os

_base = os.path.dirname(os.path.abspath(__file__))
_root = os.path.normpath(os.path.join(_base, '..', '..'))

assets_path = os.path.join(_root, 'assets')
fonts_path  = os.path.join(_root, 'assets', 'fonts')
hud_path    = os.path.join(_root, 'assets', 'hud')
icons_path  = os.path.join(_root, 'assets', 'icons')
sounds_path = os.path.join(_root, 'assets', 'sounds')

def _n(p): return p.replace('\\', '/')
def path(f):  return _n(os.path.join(assets_path, f))
def font(f):  return _n(os.path.join(fonts_path, f))
def hud(f):   return _n(os.path.join(hud_path, f))
def icon(f):  return _n(os.path.join(icons_path, f))
def sound(f): return _n(os.path.join(sounds_path, f))
