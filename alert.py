"""
alert.py — Audio alert system for drowsiness detection
-------------------------------------------------------
Tries three backends in order of preference:
  1. pygame  (cross-platform, best)
  2. playsound (simple, works on most systems)
  3. OS-native beep (fallback, no audio file needed)
"""

import os
import sys
import threading

_alert_thread: threading.Thread | None = None
_stop_event   = threading.Event()
_backend      = None   # resolved once at import time


# ─── Backend resolution ───────────────────────────────────────────────────────

def _resolve_backend():
    global _backend
    try:
        import pygame
        pygame.mixer.init()
        _backend = "pygame"
        return
    except Exception:
        pass

    try:
        from playsound import playsound  # noqa: F401
        _backend = "playsound"
        return
    except Exception:
        pass

    _backend = "beep"


_resolve_backend()


# ─── Alert tone generation (pygame only) ──────────────────────────────────────

def _generate_beep_wav(path: str, freq: int = 880, duration_ms: int = 600):
    """Write a simple sine-wave WAV to *path* using only stdlib."""
    import struct, wave, math
    sample_rate = 44100
    n_samples   = int(sample_rate * duration_ms / 1000)
    amplitude   = 28000

    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(n_samples):
            # Gentle fade-in / fade-out envelope
            env = min(i, n_samples - i, sample_rate // 20) / (sample_rate // 20)
            val = int(amplitude * env * math.sin(2 * math.pi * freq * i / sample_rate))
            wf.writeframes(struct.pack("<h", val))


_WAV_PATH = os.path.join(os.path.dirname(__file__), "_alert_tone.wav")

if _backend == "pygame" and not os.path.exists(_WAV_PATH):
    try:
        _generate_beep_wav(_WAV_PATH)
    except Exception as e:
        print(f"[ALERT] Could not generate tone file: {e}")


# ─── Public API ───────────────────────────────────────────────────────────────

def _play_loop():
    """Continuously play the alert until _stop_event is set."""
    _stop_event.clear()

    if _backend == "pygame":
        import pygame
        try:
            sound = pygame.mixer.Sound(_WAV_PATH)
            while not _stop_event.is_set():
                sound.play()
                _stop_event.wait(timeout=0.7)
            sound.stop()
        except Exception as e:
            print(f"[ALERT] pygame error: {e}")

    elif _backend == "playsound":
        from playsound import playsound
        while not _stop_event.is_set():
            try:
                playsound(_WAV_PATH, block=True)
            except Exception:
                _stop_event.wait(timeout=0.5)

    else:
        # OS beep fallback
        while not _stop_event.is_set():
            if sys.platform == "win32":
                import winsound
                winsound.Beep(880, 600)
            else:
                sys.stdout.write("\a")
                sys.stdout.flush()
            _stop_event.wait(timeout=0.8)


def trigger_alert():
    """Start the alert in a background thread (non-blocking)."""
    global _alert_thread
    if _alert_thread and _alert_thread.is_alive():
        return   # already running

    print("[ALERT] ⚠️  DROWSINESS DETECTED — WAKE UP!")
    _stop_event.clear()
    _alert_thread = threading.Thread(target=_play_loop, daemon=True)
    _alert_thread.start()


def stop_alert():
    """Stop the alert if it is currently playing."""
    _stop_event.set()
    if _alert_thread:
        _alert_thread.join(timeout=1.5)