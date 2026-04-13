"""
Звуки уведомлений.
- Кастомные WAV: assets/sounds/custom_{event}.wav (макс 5 сек)
- Стандартные WAV: assets/sounds/{event}.wav
- Fallback: генерация beep в памяти без внешних файлов
"""
import sys
import os
import threading
import math
import struct
import logging

_log = logging.getLogger("hero_siege_stats")

_SOUNDS_DIR = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'sounds'
))

# Стандартные WAV файлы
_WAV_FILES = {
    "Satanic": "drop_satanic.wav",
    "Angelic":  "drop_angelic.wav",
    "Unholy":   "drop_angelic.wav",
    "Heroic":   "drop_heroic.wav",
    "Mythic":   "drop_mythic.wav",
    "Mail":     "mail.wav",
}

# Параметры генерации beep для каждого события
# (частота Hz, длительность ms, тип волны)
_BEEPS = {
    "Satanic": (880, 500, "square"),   # Высокий резкий — самое редкое
    "Angelic":  (660, 400, "sine"),    # Яркий
    "Unholy":   (660, 400, "sine"),
    "Heroic":   (523, 350, "sine"),    # Средний
    "Mythic":   (740, 450, "square"),  # Особый
    "Mail":     (440, 250, "sine"),    # Мягкий
    "Common":   (300, 150, "sine"),    # Тихий
}


def _make_wav(freq: int, ms: int, wave: str = "sine") -> bytes:
    """Генерирует WAV в памяти — не нужны файлы."""
    sr = 22050
    n  = int(sr * ms / 1000)
    amp = 14000

    samples = []
    for i in range(n):
        t = i / sr
        decay = max(0.0, 1.0 - i / n)
        if wave == "square":
            raw = amp * (1 if math.sin(2 * math.pi * freq * t) >= 0 else -1)
        else:  # sine
            raw = amp * math.sin(2 * math.pi * freq * t)
        samples.append(max(-32767, min(32767, int(raw * decay))))

    pcm = struct.pack(f"<{n}h", *samples)
    ds  = len(pcm)
    hdr = struct.pack("<4sI4s4sIHHIIHH4sI",
        b"RIFF", 36 + ds, b"WAVE",
        b"fmt ", 16, 1, 1,
        sr, sr * 2, 2, 16,
        b"data", ds)
    return hdr + pcm


def play(event: str, enabled: bool = True) -> None:
    """Воспроизвести звук события. event = Satanic / Angelic / Heroic / Mail / ..."""
    if not enabled or sys.platform != "win32":
        return
    threading.Thread(target=_play_async, args=(event,), daemon=True).start()


def _play_async(event: str) -> None:
    try:
        import winsound

        # 1. Кастомный звук пользователя
        custom = os.path.join(_SOUNDS_DIR, f"custom_{event.lower()}.wav")
        if os.path.exists(custom):
            winsound.PlaySound(custom, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return

        # 2. Стандартный WAV файл
        wav_name = _WAV_FILES.get(event)
        if wav_name:
            wav_path = os.path.join(_SOUNDS_DIR, wav_name)
            if os.path.exists(wav_path):
                winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                return

        # 3. Генерируем beep в памяти
        freq, ms, wave = _BEEPS.get(event, (440, 200, "sine"))
        winsound.PlaySound(_make_wav(freq, ms, wave), winsound.SND_MEMORY)

    except Exception as e:
        _log.debug(f"Sound error [{event}]: {e}")
