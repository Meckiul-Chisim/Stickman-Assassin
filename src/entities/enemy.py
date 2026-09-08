"""
The Enemy: patrol -> alert -> attack, plus death/assassination handling.

Improvement over the original version: enemies used to just walk at the
player forever with no way to actually hurt them, which meant "combat" had
no stakes. Now an alert enemy that gets in range winds up and swings back,
so avoiding detection (stealth) is an actual tradeoff against fighting
head-on, not just a bonus animation.
"""

import itertools
import pygame

from .. import settings

_id_counter = itertools.count()


class Enemy:
    def __init__(self, x, y, audio, effects):
        self.id = next(_id_counter)
        self.x = float(x)
        self.y = float(y)
        self.width = settings.ENEMY_WIDTH
        self.height = settings.ENEMY_HEIGHT

        self.health = settings.ENEMY_MAX_HEALTH
        self.max_health = settings.ENEMY_MAX_HEALTH

        self.alert = False
        self.dead = False
        self.death_timer = 30  # frames of fade-out before removal

        self.attack_windup = 0
        self.attack_cooldown = 0

        self.audio = audio
        self.effects = effects

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - self.width / 2),
            int(self.y - self.height),
            self.width,
            self.height,
        )

    @property
    def fully_gone(self) -> bool:
        return self.dead and self.death_timer <= 0

    # -- behaviour ------------------------------------------------------------
    def update(self, player):
        if self.dead:
            self.death_timer -= 1
            return

        distance = abs(player.x - self.x)
        was_alert = self.alert
        if not player.hidden and distance < settings.ENEMY_DETECTION_RANGE:
            self.alert = True
        if self.alert and not was_alert:
            self.audio.play("alert")

        if not self.alert:
            return

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.attack_windup > 0:
            self.attack_windup -= 1
            if self.attack_windup == 0:
                self._resolve_attack(player)
            return  # hold still mid-swing

        if distance <= settings.ENEMY_ATTACK_RANGE:
            if self.attack_cooldown == 0:
                self.attack_windup = settings.ENEMY_ATTACK_WINDUP
                self.attack_cooldown = settings.ENEMY_ATTACK_COOLDOWN
        else:
            speed = settings.ENEMY_SPEED
            if player.x < self.x:
                self.x -= speed
            else:
                self.x += speed

    def _resolve_attack(self, player):
        distance = abs(player.x - self.x)
        if distance <= settings.ENEMY_ATTACK_RANGE + 15 and player.alive:
            player.take_damage(settings.ENEMY_ATTACK_DAMAGE)
            self.audio.play("enemy_attack")

    def take_damage(self, amount, hit_x=None, hit_y=None):
        if self.dead:
            return
        self.health -= amount
        if hit_x is not None:
            self.effects.hit_sparks(hit_x, hit_y)
        self.audio.play("hit")
        if self.health <= 0:
            self.health = 0
            self.dead = True

    def can_be_assassinated(self, player) -> bool:
        return (
            not self.dead
            and player.hidden
            and abs(self.x - player.x) <= settings.ASSASSINATION_RANGE
            and not self.alert
        )

    # -- drawing --------------------------------------------------------------
    def draw(self, surface):
        if self.fully_gone:
            return

        x, bottom = int(self.x), int(self.y)

        if self.dead:
            self._draw_death_fade(surface, x, bottom)
            return

        color = settings.COLOR_ENEMY_ALERT if self.alert else settings.COLOR_ENEMY_IDLE
        if self.attack_windup > 0:
            # Telegraph the incoming swing by flashing brighter as it charges.
            flash = 1 - (self.attack_windup / settings.ENEMY_ATTACK_WINDUP)
            color = tuple(min(255, int(c + (255 - c) * flash * 0.6)) for c in color)

        pygame.draw.circle(surface, color, (x, bottom - 64), 10, 3)
        pygame.draw.line(surface, color, (x, bottom - 54), (x, bottom - 27), 4)
        pygame.draw.line(surface, color, (x, bottom - 46), (x - 18, bottom - 34), 4)
        pygame.draw.line(surface, color, (x, bottom - 46), (x + 18, bottom - 34), 4)
        pygame.draw.line(surface, color, (x, bottom - 27), (x - 15, bottom), 4)
        pygame.draw.line(surface, color, (x, bottom - 27), (x + 15, bottom), 4)

        bar_width = 46
        health_width = int(bar_width * self.health / self.max_health)
        pygame.draw.rect(surface, settings.COLOR_PANEL, (x - bar_width // 2, bottom - 90, bar_width, 5))
        pygame.draw.rect(surface, settings.COLOR_ACCENT_RED, (x - bar_width // 2, bottom - 90, health_width, 5))

        if self.alert:
            pygame.draw.circle(surface, settings.COLOR_ACCENT_RED, (x, bottom - 103), 4)

    def _draw_death_fade(self, surface, x, bottom):
        """Fade + collapse the stickman instead of just popping out of existence."""
        t = self.death_timer / 30  # 1.0 -> 0.0
        alpha = max(0, int(255 * t))
        drop = int((1 - t) * 14)

        ghost = pygame.Surface((80, 100), pygame.SRCALPHA)
        color = (*settings.COLOR_ENEMY_IDLE, alpha)
        cx, cy = 40, 50
        pygame.draw.circle(ghost, color, (cx, cy - 14 + drop), 10, 3)
        pygame.draw.line(ghost, color, (cx, cy - 4 + drop), (cx, cy + 23 + drop), 4)
        pygame.draw.line(ghost, color, (cx, cy + 23 + drop), (cx - 15, cy + 50 + drop), 4)
        pygame.draw.line(ghost, color, (cx, cy + 23 + drop), (cx + 15, cy + 50 + drop), 4)
        surface.blit(ghost, (x - 40, bottom - 100))
