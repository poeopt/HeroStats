"""
check_requirements.py — проверка и установка необходимых компонентов.
Запускать от имени Администратора при первом запуске на чистой системе.
"""
import sys
import os
import subprocess
import urllib.request
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_npcap() -> bool:
    """Проверяет установлен ли Npcap."""
    paths = [
        r"C:\Windows\System32\Npcap",
        r"C:\Windows\SysWOW64\Npcap",
    ]
    for p in paths:
        if os.path.exists(p):
            return True
    # Проверяем через службы
    try:
        result = subprocess.run(
            ["sc", "query", "npcap"],
            capture_output=True, text=True, timeout=5,
            creationflags=0x08000000
        )
        return "RUNNING" in result.stdout or "STOPPED" in result.stdout
    except:
        return False

def check_vc_redist() -> bool:
    """Проверяет Visual C++ Redistributable."""
    try:
        import winreg
        paths = [
            r"SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\X64",
            r"SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\X64",
            r"SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64",
        ]
        for path in paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                installed, _ = winreg.QueryValueEx(key, "Installed")
                if installed == 1:
                    return True
            except:
                continue
    except:
        pass
    return False

def download_and_run(url: str, filename: str, args: list = None):
    print(f"Скачиваю {filename}...")
    path = os.path.join(os.environ.get("TEMP", "C:\\Temp"), filename)
    try:
        urllib.request.urlretrieve(url, path)
        print(f"Установка {filename}...")
        cmd = [path] + (args or [])
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def main():
    print("=" * 50)
    print("Hero Siege Stats — Проверка зависимостей")
    print("=" * 50)

    if sys.platform != "win32":
        print("Работает только на Windows.")
        return

    issues = []

    # 1. Npcap
    print("\n[1/2] Проверка Npcap...", end=" ")
    if check_npcap():
        print("✓ Установлен")
    else:
        print("✗ НЕ найден")
        issues.append("npcap")

    # 2. Visual C++ Redistributable
    print("[2/2] Проверка VC++ Redistributable...", end=" ")
    if check_vc_redist():
        print("✓ Установлен")
    else:
        print("✗ НЕ найден")
        issues.append("vcredist")

    if not issues:
        print("\n✓ Все зависимости установлены. Hero Siege Stats готов к запуску!")
        input("\nНажмите Enter для выхода...")
        return

    print(f"\nОбнаружены проблемы: {len(issues)}")

    if not is_admin():
        print("\n⚠ Для установки компонентов нужны права администратора.")
        print("Перезапустите check_requirements.py от имени Администратора.")
        input("\nНажмите Enter для выхода...")
        return

    install = input("\nУстановить недостающие компоненты? (да/нет): ").strip().lower()
    if install not in ("да", "yes", "y", "д"):
        print("Установка отменена.")
        input("\nНажмите Enter для выхода...")
        return

    if "npcap" in issues:
        print("\nУстановка Npcap (необходим для перехвата трафика)...")
        ok = download_and_run(
            "https://npcap.com/dist/npcap-1.79.exe",
            "npcap-1.79.exe",
            ["/S"]  # Silent install
        )
        if ok:
            print("✓ Npcap установлен")
        else:
            print("✗ Не удалось установить Npcap автоматически.")
            print("  Скачайте вручную: https://npcap.com/#download")

    if "vcredist" in issues:
        print("\nУстановка Visual C++ Redistributable...")
        ok = download_and_run(
            "https://aka.ms/vs/17/release/vc_redist.x64.exe",
            "vc_redist.x64.exe",
            ["/install", "/quiet", "/norestart"]
        )
        if ok:
            print("✓ VC++ Redistributable установлен")
        else:
            print("✗ Не удалось установить VC++ Redistributable автоматически.")

    print("\nГотово! Перезапустите Hero Siege Stats.")
    input("\nНажмите Enter для выхода...")


if __name__ == "__main__":
    main()
