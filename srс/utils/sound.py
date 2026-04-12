import sys, os, threading, math, struct, logging

_log = logging.getLogger("hero_siege_stats")
_SOUNDS = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'sounds'))

_BEEPS = {
    "Satanic": (880, 400), "Angelic": (660, 350),
    "Unholy":  (660, 350), "Heroic":  (523, 300), "Mail": (440, 200),
}
_WAV_FILES = {
    "Satanic": "drop_satanic.wav", "Angelic": "drop_angelic.wav",
    "Unholy":  "drop_angelic.wav", "Heroic":  "drop_heroic.wav", "Mail": "mail.wav",
}


def _make_beep(freq: int, ms: int) -> bytes:
    sr, n = 22050, int(22050 * ms / 1000)
    amp = 16000
    pcm = struct.pack(f"<{n}h", *(
        max(-32768, min(32767, int(amp * (1-i/n) * math.sin(2*math.pi*freq*i/sr))))
        for i in range(n)
    ))
    ds = len(pcm)
    return struct.pack("<4sI4s4sIHHIIHH4sI",
        b"RIFF", 36+ds, b"WAVE", b"fmt ", 16, 1, 1,
        sr, sr*2, 2, 16, b"data", ds) + pcm


def play(event: str, enabled: bool = True):
    if not enabled or sys.platform != "win32":
        return
    threading.Thread(target=_play, args=(event,), daemon=True).start()


def _play(event: str):
    try:
        import winsound
        # Custom WAV first
        custom = os.path.join(_SOUNDS, f"custom_{event.lower()}.wav")
        if os.path.exists(custom):
            winsound.PlaySound(custom, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return
        # Standard WAV
        wav = os.path.join(_SOUNDS, _WAV_FILES.get(event, ""))
        if os.path.exists(wav):
            winsound.PlaySound(wav, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return
        # Generated beep
        freq, dur = _BEEPS.get(event, (440, 300))
        winsound.PlaySound(_make_beep(freq, dur), winsound.SND_MEMORY)
    except Exception as e:
        _log.debug(f"Sound error for {event}: {e}")
