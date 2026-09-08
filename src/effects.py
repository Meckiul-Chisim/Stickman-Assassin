"""
Lightweight visual-effects layer: particles + screen shake.

Kept deliberately separate from the entities (Player/Enemy) so gameplay code
never has to know *how* an effect is drawn — it just calls
`effects.spark_burst(x, y)` and moves on. This separation is what lets you
swap in fancier effects later without touching Player/Enemy logic at all.
"""

import random
import pygame

from . import settings


class Particle:
    """A single short-lived dot/line used to build up bigger effects."""

    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "size", "shrink")

    def __init__(self, x, y, vx, vy, life, color, size=3, shrink=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.shrink = shrink

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += settings.PARTICLE_GRAVITY
        self.life -= 1

    @property
    def alive(self):
        return self.life > 0

    def draw(self, surface):
        t = self.life / self.max_life  # 1.0 -> 0.0 over its lifetime
        size = max(1, int(self.size * t)) if self.shrink else self.size
        alpha = max(0, min(255, int(255 * t)))

        # Draw onto a tiny per-particle surface so we can fade it (alpha).
        glow = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, alpha), (size, size), size)
        surface.blit(glow, (self.x - size, self.y - size))


class EffectsManager:
    """Owns every active particle plus the current screen-shake offset."""

    def __init__(self):
        self.particles: list[Particle] = []
        self._shake_timer = 0
        self._shake_strength = 0

    # -- screen shake ------------------------------------------------------
    def shake(self, strength: int, duration: int = 10):
        self._shake_strength = max(self._shake_strength, strength)
        self._shake_timer = max(self._shake_timer, duration)

    def get_shake_offset(self) -> tuple[int, int]:
        if self._shake_timer <= 0:
            return 0, 0
        magnitude = self._shake_strength * (self._shake_timer / 10)
        return (
            random.randint(-int(magnitude), int(magnitude)),
            random.randint(-int(magnitude), int(magnitude)),
        )

    # -- particle presets ----------------------------------------------------
    def slash_effect(self, x, y, facing):
        """Quick arc of bright particles in front of the player's weapon."""
        for _ in range(10):
            angle_spread = random.uniform(-0.5, 0.5)
            speed = random.uniform(4, 8)
            vx = facing * speed * (1 - abs(angle_spread))
            vy = speed * angle_spread
            self.particles.append(
                Particle(x, y, vx, vy, life=random.randint(8, 14), color=settings.COLOR_TEXT, size=3)
            )

    def hit_sparks(self, x, y):
        """Impact sparks when an attack lands on an enemy."""
        for _ in range(14):
            vx = random.uniform(-4, 4)
            vy = random.uniform(-5, 1)
            self.particles.append(
                Particle(x, y, vx, vy, life=random.randint(10, 20), color=settings.COLOR_ACCENT_RED, size=3)
            )
        self.shake(settings.SHAKE_ON_HIT)

    def assassination_burst(self, x, y):
        """Big pale-green burst for the stealth-kill payoff."""
        for _ in range(28):
            angle = random.uniform(0, 6.283)
            speed = random.uniform(2, 7)
            vx = speed * random.uniform(-1, 1)
            vy = speed * random.uniform(-1, 1)
            self.particles.append(
                Particle(x, y, vx, vy, life=random.randint(20, 34), color=settings.COLOR_ACCENT_GREEN, size=4)
            )
        self.shake(settings.SHAKE_ON_ASSASSINATION, duration=14)

    def dust_step(self, x, y):
        """Subtle dust puff — used for jump landings."""
        for _ in range(6):
            vx = random.uniform(-1.5, 1.5)
            vy = random.uniform(-1.5, -0.2)
            self.particles.append(
                Particle(x, y, vx, vy, life=random.randint(10, 16), color=settings.COLOR_TEXT_DIM, size=2)
            )

    # -- lifecycle -----------------------------------------------------------
    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]

        if self._shake_timer > 0:
            self._shake_timer -= 1

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
