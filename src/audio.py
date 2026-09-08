"""
Procedural sound effects.

Why generate sounds instead of loading .wav/.mp3 files:
This keeps the project completely self-contained — no missing-asset errors,
no licensing questions, nothing to download. Every sound is a short numpy
waveform (a sine/noise burst shaped by a volume envelope) built once at
startup and cached. This is a legitimate, common technique for small games
and game-jam projects.

If you later want "real" recorded SFX, drop .wav files into an `assets/sfx/`
folder and swap `pygame.sndarray.make_sound(wave)` for `pygame.mixer.Sound(path)`
in AudioManager._load_all — the rest of the game doesn't need to change,
because everything else just calls `audio.play("attack")` by name.
"""

import numpy as np
import pygame

from . import settings


def _envelope(n_samples: int, attack: float = 0.01, release: float = 0.5) -> np.ndarray:
    """Fade a raw tone in and out so it doesn't 'click' at the start/end."""
    attack_n = max(1, int(n_samples * attack))
    release_n = max(1, int(n_samples * release))
    env = np.ones(n_samples)
    env[:attack_n] = np.linspace(0, 1, attack_n)
    env[-release_n:] *= np.linspace(1, 0, release_n)
    return env


def _tone(freq: float, duration: float, wave: str = "sine", volume: float = 1.0) -> np.ndarray:
    """Build one mono waveform for a given frequency/duration/shape."""
    n = int(settings.SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)

    if wave == "sine":
        data = np.sin(2 * np.pi * freq * t)
    elif wave == "square":
        data = np.sign(np.sin(2 * np.pi * freq * t))
    elif wave == "noise":
        data = np.random.uniform(-1, 1, n)
    elif wave == "saw":
        data = 2 * (t * freq - np.floor(0.5 + t * freq))
    else:
        raise ValueError(f"Unknown waveform: {wave}")

    data *= _envelope(n) * volume
    return data


def _sweep(start_freq: float, end_freq: float, duration: float, volume: float = 1.0) -> np.ndarray:
    """A tone that slides from one frequency to another (good for whooshes)."""
    n = int(settings.SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    freq_curve = np.linspace(start_freq, end_freq, n)
    phase = 2 * np.pi * np.cumsum(freq_curve) / settings.SAMPLE_RATE
    data = np.sin(phase) * _envelope(n) * volume
    return data


def _mix(*layers: np.ndarray) -> np.ndarray:
    """Sum several waveforms of possibly different lengths into one."""
    length = max(len(layer) for layer in layers)
    out = np.zeros(length)
    for layer in layers:
        out[: len(layer)] += layer
    peak = np.max(np.abs(out))
    if peak > 1.0:
        out /= peak
    return out


def _to_pygame_sound(mono_wave: np.ndarray) -> pygame.mixer.Sound:
    """Convert a float [-1, 1] mono numpy array into a playable Sound."""
    stereo = np.column_stack([mono_wave, mono_wave])
    samples = np.ascontiguousarray((stereo * 32767).astype(np.int16))
    return pygame.sndarray.make_sound(samples)


class AudioManager:
    """Generates, caches, and plays every sound effect the game needs."""

    def __init__(self):
        self._enabled = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}

        try:
            pygame.mixer.init(frequency=settings.SAMPLE_RATE, size=-16, channels=2)
            self._enabled = True
            self._build_all()
        except pygame.error:
            # No audio device available (e.g. headless environment) — the
            # game should still run perfectly, just silently.
            self._enabled = False

    def _build_all(self):
        self.sounds["swing"] = _to_pygame_sound(
            _mix(
                _sweep(900, 220, 0.12, volume=0.5),
                _tone(180, 0.05, wave="noise", volume=0.15),
            )
        )
        self.sounds["hit"] = _to_pygame_sound(
            _mix(
                _tone(120, 0.08, wave="square", volume=0.5),
                _tone(90, 0.12, wave="noise", volume=0.35),
            )
        )
        self.sounds["assassinate"] = _to_pygame_sound(
            _mix(
                _sweep(700, 90, 0.35, volume=0.6),
                _tone(60, 0.4, wave="sine", volume=0.4),
            )
        )
        self.sounds["jump"] = _to_pygame_sound(_sweep(300, 520, 0.14, volume=0.35))
        self.sounds["land"] = _to_pygame_sound(_tone(140, 0.07, wave="noise", volume=0.25))
        self.sounds["stealth_on"] = _to_pygame_sound(_sweep(500, 900, 0.2, volume=0.3))
        self.sounds["stealth_off"] = _to_pygame_sound(_sweep(900, 500, 0.2, volume=0.3))
        self.sounds["alert"] = _to_pygame_sound(
            _mix(_tone(660, 0.1, wave="square", volume=0.25), _tone(880, 0.1, wave="square", volume=0.2))
        )
        self.sounds["player_hurt"] = _to_pygame_sound(_sweep(300, 130, 0.18, volume=0.45))
        self.sounds["enemy_attack"] = _to_pygame_sound(_sweep(400, 150, 0.1, volume=0.3))

    def play(self, name: str):
        if self._enabled and name in self.sounds:
            self.sounds[name].play()
