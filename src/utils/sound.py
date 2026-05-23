"""
Звуки уведомлений с регулировкой громкости.
- Кастомные WAV: assets/sounds/custom_{event}.wav
- Стандартные WAV: assets/sounds/{event}.wav
- Fallback: генерация beep в памяти
- Громкость: 0-100 (из config)
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

_WAV_FILES = {
    "Satanic": "drop_satanic.wav",
    "Angelic":  "drop_angelic.wav",
    "Unholy":   "drop_angelic.wav",
    "Heroic":   "drop_heroic.wav",
    "Mythic":   "drop_mythic.wav",
    "Mail":     "mail.wav",
}

_BEEPS = {
    "Satanic": (880, 500, "square"),
    "Angelic":  (660, 400, "sine"),
    "Unholy":   (660, 400, "sine"),
    "Heroic":   (523, 350, "sine"),
    "Mythic":   (740, 450, "square"),
    "Mail":     (440, 250, "sine"),
}


def _get_volume() -> float:
    """Возвращает громкость 0.0–1.0 из config."""
    try:
        from src.utils.config import get as cfg_get
        v = cfg_get("volume")
        if v is None:
            return 0.8
        return max(0.0, min(1.0, int(v) / 100.0))
    except Exception:
        return 0.8


def _make_wav(freq: int, ms: int, wave: str, volume: float) -> bytes:
    """Генерирует WAV в памяти с нужной громкостью."""
    sr  = 22050
    n   = int(sr * ms / 1000)
    amp = int(14000 * volume)

    samples = []
    for i in range(n):
        t     = i / sr
        decay = max(0.0, 1.0 - i / n)
        if wave == "square":
            raw = amp * (1 if math.sin(2 * math.pi * freq * t) >= 0 else -1)
        else:
            raw = amp * math.sin(2 * math.pi * freq * t)
        samples.append(max(-32767, min(32767, int(raw * decay))))

    pcm = struct.pack(f"<{n}h", *samples)
    ds  = len(pcm)
    hdr = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", 36 + ds, b"WAVE",
        b"fmt ", 16, 1, 1,
        sr, sr * 2, 2, 16,
        b"data", ds,
    )
    return hdr + pcm


def _scale_wav_volume(wav_bytes: bytes, volume: float) -> bytes:
    """Масштабирует громкость существующего WAV файла."""
    if abs(volume - 1.0) < 0.01:
        return wav_bytes  # 100% — без изменений
    try:
        # WAV header = 44 bytes, дальше PCM данные
        header = wav_bytes[:44]
        pcm_raw = wav_bytes[44:]
        n = len(pcm_raw) // 2
        samples = struct.unpack(f"<{n}h", pcm_raw)
        scaled  = [max(-32767, min(32767, int(s * volume))) for s in samples]
        return header + struct.pack(f"<{n}h", *scaled)
    except Exception:
        return wav_bytes


def play(event: str, enabled: bool = True) -> None:
    if not enabled or sys.platform != "win32":
        return
    threading.Thread(target=_play_async, args=(event,), daemon=True).start()


def _play_async(event: str) -> None:
    try:
        import winsound
        vol = _get_volume()

        # 1. Кастомный звук пользователя
        custom = os.path.join(_SOUNDS_DIR, f"custom_{event.lower()}.wav")
        if os.path.exists(custom):
            if abs(vol - 1.0) < 0.01:
                winsound.PlaySound(custom, winsound.SND_FILENAME | winsound.SND_ASYNC)
            else:
                data = _scale_wav_volume(open(custom, "rb").read(), vol)
                winsound.PlaySound(data, winsound.SND_MEMORY)
            return

        # 2. Стандартный WAV
        wav_name = _WAV_FILES.get(event)
        if wav_name:
            wav_path = os.path.join(_SOUNDS_DIR, wav_name)
            if os.path.exists(wav_path):
                if abs(vol - 1.0) < 0.01:
                    winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                else:
                    data = _scale_wav_volume(open(wav_path, "rb").read(), vol)
                    winsound.PlaySound(data, winsound.SND_MEMORY)
                return

        # 3. Генерируем beep с нужной громкостью
        freq, ms, wave = _BEEPS.get(event, (440, 200, "sine"))
        winsound.PlaySound(_make_wav(freq, ms, wave, vol), winsound.SND_MEMORY)

    except Exception as e:
        _log.debug(f"Sound error [{event}]: {e}")
