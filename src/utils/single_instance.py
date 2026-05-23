import sys, logging
_mutex = None
_NAME = "Global\\HeroSiegeStats_SingleInstance"


def ensure_single_instance() -> bool:
    global _mutex
    if sys.platform != "win32":
        return True
    try:
        import ctypes
        _mutex = ctypes.windll.kernel32.CreateMutexW(None, True, _NAME)
        return ctypes.windll.kernel32.GetLastError() != 183  # 183 = already exists
    except Exception:
        return True


def release():
    global _mutex
    if _mutex and sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.kernel32.CloseHandle(_mutex)
        except Exception:
            pass
