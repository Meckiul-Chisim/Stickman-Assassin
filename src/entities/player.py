"""
The Player: movement, jumping, attacking, and stealth/assassination.

Design note: the player no longer knows *how* to play a sound or spawn a
particle — it just calls the AudioManager/EffectsManager it was given at
construction time. This is dependency injection in its simplest form, and
it's what keeps Player testable and reusable (you could run it with a fake
silent AudioManager in a unit test, for example).
"""

import pygame

from .. import settings


class Player:
    def __init__(self, x, y, audio, effects):
        self.x = float(x)
        self.y = float(y)
        self.width = settings.PLAYER_WIDTH
        self.height = settings.PLAYER_HEIGHT
        self.facing = 1

        self.velocity_y = 0.0
        self.on_ground = False
        self._was_on_ground = True  # used to detect landings, for dust VFX

        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_has_hit: set[int] = set()  # enemy ids already hit this swing

        self.hidden = False
        self.stealth_timer = 0

        self.health = settings.PLAYER_MAX_HEALTH
        self.max_health = settings.PLAYER_MAX_HEALTH
        self.invuln_timer = 0
        self.alive = True

        # Injected systems (see design note above).
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

    # -- input / physics ------------------------------------------------------
    def handle_input(self, keys):
        if not self.alive:
            return

        dx = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= settings.PLAYER_SPEED
            self.facing = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += settings.PLAYER_SPEED
            self.facing = 1
        self.x = max(25, min(settings.WIDTH - 25, self.x + dx))

        wants_jump = keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]
        if wants_jump and self.on_ground:
            self.velocity_y = settings.PLAYER_JUMP_POWER
            self.on_ground = False
            self.audio.play("jump")

    def update(self, keys):
        if not self.alive:
            return

        self.handle_input(keys)

        self._was_on_ground = self.on_ground
        self.velocity_y += settings.PLAYER_GRAVITY
        self.y += self.velocity_y

        if self.y >= settings.GROUND_Y:
            self.y = settings.GROUND_Y
            self.velocity_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        if self.on_ground and not self._was_on_ground:
            self.effects.dust_step(self.x, self.y)
            self.audio.play("land")

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.attack_timer > 0:
            self.attack_timer -= 1
        else:
            self.attacking = False

        if self.stealth_timer > 0:
            self.stealth_timer -= 1
        else:
            self.hidden = False

        if self.invuln_timer > 0:
            self.invuln_timer -= 1

    # -- actions ------------------------------------------------------------
    def attack(self):
        if not self.alive or self.attack_cooldown > 0:
            return
        self.attacking = True
        self.attack_timer = settings.ATTACK_DURATION
        self.attack_cooldown = settings.ATTACK_COOLDOWN
        self.attack_has_hit.clear()
        self.hidden = False
        self.stealth_timer = 0
        self.audio.play("swing")
        self.effects.slash_effect(self.x + self.facing * 20, self.y - 48, self.facing)

    def enter_stealth(self):
        if self.alive and not self.attacking and self.on_ground and not self.hidden:
            self.hidden = True
            self.stealth_timer = settings.STEALTH_DURATION
            self.audio.play("stealth_on")

    def take_damage(self, amount):
        if not self.alive or self.invuln_timer > 0:
            return
        self.health = max(0, self.health - amount)
        self.invuln_timer = settings.INVULNERABILITY_FRAMES
        self.audio.play("player_hurt")
        if self.health <= 0:
            self.alive = False

    def get_attack_rect(self) -> pygame.Rect:
        if not self.attacking:
            return pygame.Rect(0, 0, 0, 0)
        if self.facing == 1:
            return pygame.Rect(
                int(self.x + 5), int(self.y - 58), settings.ATTACK_RANGE, settings.ATTACK_HEIGHT
            )
        return pygame.Rect(
            int(self.x - 5 - settings.ATTACK_RANGE), int(self.y - 58),
            settings.ATTACK_RANGE, settings.ATTACK_HEIGHT,
        )

    # -- drawing --------------------------------------------------------------
    def draw(self, surface):
        x, bottom = int(self.x), int(self.y)

        # Flicker while invulnerable so a hit is readable without a health bar.
        if self.invuln_timer > 0 and (self.invuln_timer // 4) % 2 == 0:
            return

        color = settings.COLOR_PLAYER

        pygame.draw.circle(surface, color, (x, bottom - 67), 10, 3)
        pygame.draw.line(surface, color, (x, bottom - 57), (x, bottom - 28), 4)

        arm_y = bottom - 48
        if self.attacking:
            pygame.draw.line(surface, color, (x, arm_y), (x + self.facing * 27, arm_y - 7), 4)
            pygame.draw.line(surface, color, (x, arm_y + 2), (x - self.facing * 14, arm_y + 13), 4)
            pygame.draw.line(
                surface, settings.COLOR_ACCENT_RED,
                (x + self.facing * 27, arm_y - 7), (x + self.facing * 43, arm_y - 11), 3,
            )
        else:
            pygame.draw.line(surface, color, (x, arm_y), (x - 18, arm_y + 13), 4)
            pygame.draw.line(surface, color, (x, arm_y), (x + 18, arm_y + 13), 4)

        pygame.draw.line(surface, color, (x, bottom - 28), (x - 17, bottom), 4)
        pygame.draw.line(surface, color, (x, bottom - 28), (x + 17, bottom), 4)

        if self.hidden:
            ring = pygame.Surface((110, 110), pygame.SRCALPHA)
            pygame.draw.circle(ring, (*settings.COLOR_ACCENT_GREEN, 90), (55, 55), 48, 2)
            surface.blit(ring, (x - 55, bottom - 38 - 55))
