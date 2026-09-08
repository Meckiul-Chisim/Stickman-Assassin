"""
The Player: movement, jumping, attacking, and stealth/assassination.
"""

import math
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
        self._was_on_ground = True

        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_has_hit: set[int] = set()

        self.hidden = False
        self.stealth_timer = 0

        self.health = settings.PLAYER_MAX_HEALTH
        self.max_health = settings.PLAYER_MAX_HEALTH
        self.invuln_timer = 0
        self.alive = True

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

    def draw(self, surface):
        x, bottom = int(self.x), int(self.y)

        if self.invuln_timer > 0 and (self.invuln_timer // 4) % 2 == 0:
            return

        body = settings.COLOR_PLAYER
        dark = (9, 13, 20)
        cloak = (23, 30, 41)
        cloak_hi = (43, 54, 67)
        red = settings.COLOR_ACCENT_RED
        green = settings.COLOR_ACCENT_GREEN

        # Ground shadow.
        shadow = pygame.Surface((82, 26), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 95), (0, 4, 82, 16))
        surface.blit(shadow, (x - 41, bottom - 8))

        # Stealth aura.
        if self.hidden:
            aura = pygame.Surface((150, 150), pygame.SRCALPHA)
            pygame.draw.circle(aura, (*green, 18), (75, 75), 58)
            pygame.draw.circle(aura, (*green, 85), (75, 75), 48, 2)
            surface.blit(aura, (x - 75, bottom - 95))

        # Flowing red scarf.
        tail = -self.facing
        scarf = [
            (x - self.facing * 3, bottom - 64),
            (x + tail * 28, bottom - 61),
            (x + tail * 45, bottom - 48),
            (x + tail * 23, bottom - 43),
            (x + self.facing * 4, bottom - 52),
        ]
        pygame.draw.polygon(surface, red, scarf)
        pygame.draw.line(surface, (241, 91, 98), scarf[1], scarf[2], 2)

        # Hood/head and eye slit.
        pygame.draw.circle(surface, dark, (x, bottom - 67), 13)
        hood_points = [
            (x - 12, bottom - 70), (x - 7, bottom - 80),
            (x + 7, bottom - 80), (x + 13, bottom - 69),
            (x + 7, bottom - 57), (x - 8, bottom - 57),
        ]
        pygame.draw.polygon(surface, cloak, hood_points)
        eye_y = bottom - 67
        eye_start = x + self.facing * 2
        eye_end = x + self.facing * 9
        pygame.draw.line(surface, (238, 245, 246), (eye_start, eye_y), (eye_end, eye_y - 2), 3)
        pygame.draw.line(surface, red, (eye_start, eye_y + 4), (eye_end, eye_y + 3), 1)

        # Neck and torso armor.
        pygame.draw.line(surface, cloak_hi, (x, bottom - 56), (x, bottom - 29), 9)
        pygame.draw.line(surface, body, (x, bottom - 56), (x, bottom - 30), 3)
        pygame.draw.line(surface, dark, (x - 6, bottom - 48), (x + 7, bottom - 43), 3)
        pygame.draw.circle(surface, green if self.hidden else red, (x, bottom - 47), 2)

        # Arms and bracers.
        arm_y = bottom - 48
        if self.attacking:
            pygame.draw.line(surface, body, (x, arm_y), (x + self.facing * 26, arm_y - 8), 5)
            pygame.draw.line(surface, body, (x, arm_y + 2), (x - self.facing * 15, arm_y + 13), 4)
            pygame.draw.line(surface, cloak_hi, (x + self.facing * 19, arm_y - 6), (x + self.facing * 27, arm_y - 8), 7)
        else:
            pygame.draw.line(surface, body, (x, arm_y), (x - 19, arm_y + 14), 5)
            pygame.draw.line(surface, body, (x, arm_y), (x + 19, arm_y + 14), 5)
            pygame.draw.line(surface, red, (x - 14, arm_y + 10), (x - 19, arm_y + 14), 3)

        # Belt and utility pouches.
        pygame.draw.line(surface, red, (x - 9, bottom - 32), (x + 9, bottom - 32), 3)
        pygame.draw.rect(surface, cloak_hi, (x - 15, bottom - 37, 7, 9), border_radius=2)
        pygame.draw.rect(surface, cloak_hi, (x + 8, bottom - 37, 7, 9), border_radius=2)

        # Legs and boots.
        pygame.draw.line(surface, body, (x, bottom - 29), (x - 15, bottom), 5)
        pygame.draw.line(surface, body, (x, bottom - 29), (x + 16, bottom), 5)
        pygame.draw.line(surface, dark, (x - 16, bottom), (x - 27, bottom), 5)
        pygame.draw.line(surface, dark, (x + 16, bottom), (x + 27, bottom), 5)

        # Katana sheath when idle, blade when attacking.
        if not self.attacking:
            sx = x - self.facing * 8
            pygame.draw.line(surface, (132, 91, 51), (sx, bottom - 40), (sx - self.facing * 10, bottom - 62), 4)
            pygame.draw.line(surface, (205, 211, 218), (sx - self.facing * 10, bottom - 62), (sx - self.facing * 35, bottom - 88), 2)
            pygame.draw.line(surface, red, (sx - self.facing * 9, bottom - 61), (sx - self.facing * 16, bottom - 68), 3)
        else:
            hand_x = x + self.facing * 28
            hand_y = bottom - 55
            pygame.draw.line(surface, (190, 196, 204), (hand_x, hand_y), (hand_x + self.facing * 38, hand_y - 22), 3)
            pygame.draw.line(surface, (244, 248, 250), (hand_x + self.facing * 5, hand_y - 3), (hand_x + self.facing * 38, hand_y - 22), 1)

        if self.hidden:
            pygame.draw.arc(
                surface, green,
                (x - 25, bottom - 88, 50, 62),
                math.radians(35), math.radians(145), 2,
            )
