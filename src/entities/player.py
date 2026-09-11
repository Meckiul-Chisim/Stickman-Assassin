"""Stylized, animated assassin hero model."""

import math
import pygame
from .. import settings


class Player:
    def __init__(self, x, y, audio, effects):
        self.x = float(x); self.y = float(y)
        self.width = settings.PLAYER_WIDTH; self.height = settings.PLAYER_HEIGHT
        self.facing = 1
        self.velocity_y = 0.0; self.on_ground = False; self._was_on_ground = True
        self.attacking = False; self.attack_timer = 0; self.attack_cooldown = 0
        self.attack_has_hit: set[int] = set()
        self.hidden = False; self.stealth_timer = 0
        self.health = settings.PLAYER_MAX_HEALTH; self.max_health = settings.PLAYER_MAX_HEALTH
        self.invuln_timer = 0; self.alive = True
        self.anim_time = 0.0
        self.audio = audio; self.effects = effects

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.width / 2), int(self.y - self.height), self.width, self.height)

    def handle_input(self, keys):
        if not self.alive: return
        dx = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= settings.PLAYER_SPEED; self.facing = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += settings.PLAYER_SPEED; self.facing = 1
        self.x = max(25, min(settings.WIDTH - 25, self.x + dx))
        wants_jump = keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]
        if wants_jump and self.on_ground:
            self.velocity_y = settings.PLAYER_JUMP_POWER; self.on_ground = False; self.audio.play("jump")

    def update(self, keys):
        if not self.alive: return
        self.anim_time += 0.18 if self.on_ground else 0.28
        self.handle_input(keys)
        self._was_on_ground = self.on_ground
        self.velocity_y += settings.PLAYER_GRAVITY; self.y += self.velocity_y
        if self.y >= settings.GROUND_Y:
            self.y = settings.GROUND_Y; self.velocity_y = 0; self.on_ground = True
        else: self.on_ground = False
        if self.on_ground and not self._was_on_ground:
            self.effects.dust_step(self.x, self.y); self.audio.play("land")
        if self.attack_cooldown > 0: self.attack_cooldown -= 1
        if self.attack_timer > 0: self.attack_timer -= 1
        else: self.attacking = False
        if self.stealth_timer > 0: self.stealth_timer -= 1
        else: self.hidden = False
        if self.invuln_timer > 0: self.invuln_timer -= 1

    def attack(self):
        if not self.alive or self.attack_cooldown > 0: return
        self.attacking = True; self.attack_timer = settings.ATTACK_DURATION; self.attack_cooldown = settings.ATTACK_COOLDOWN
        self.attack_has_hit.clear(); self.hidden = False; self.stealth_timer = 0
        self.audio.play("swing"); self.effects.slash_effect(self.x + self.facing * 26, self.y - 52, self.facing)

    def enter_stealth(self):
        if self.alive and not self.attacking and self.on_ground and not self.hidden:
            self.hidden = True; self.stealth_timer = settings.STEALTH_DURATION; self.audio.play("stealth_on")

    def take_damage(self, amount):
        if not self.alive or self.invuln_timer > 0: return
        self.health = max(0, self.health - amount); self.invuln_timer = settings.INVULNERABILITY_FRAMES
        self.audio.play("player_hurt")
        if self.health <= 0: self.alive = False

    def get_attack_rect(self):
        if not self.attacking: return pygame.Rect(0, 0, 0, 0)
        if self.facing == 1: return pygame.Rect(int(self.x + 5), int(self.y - 62), settings.ATTACK_RANGE, settings.ATTACK_HEIGHT)
        return pygame.Rect(int(self.x - 5 - settings.ATTACK_RANGE), int(self.y - 62), settings.ATTACK_RANGE, settings.ATTACK_HEIGHT)

    def _line(self, s, color, a, b, width):
        pygame.draw.line(s, color, a, b, width)

    def draw(self, surface):
        x, bottom = int(self.x), int(self.y)
        if self.invuln_timer > 0 and (self.invuln_timer // 4) % 2 == 0: return
        dark = (7, 11, 17); armor = (29, 38, 50); armor_hi = (66, 79, 94)
        red = settings.COLOR_ACCENT_RED; green = settings.COLOR_ACCENT_GREEN
        # Ground contact shadow and character glow.
        shadow = pygame.Surface((120, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 120), (8, 12, 104, 20))
        surface.blit(shadow, (x - 60, bottom - 10))
        if self.hidden:
            glow = pygame.Surface((190, 190), pygame.SRCALPHA)
            for r, a in ((82, 12), (64, 22), (48, 34)):
                pygame.draw.circle(glow, (*green, a), (95, 95), r)
            surface.blit(glow, (x - 95, bottom - 130))
        # Animation bob / running stride.
        moving = self.on_ground and not self.attacking
        stride = math.sin(self.anim_time) * (5 if moving else 0)
        crouch = 4 if self.hidden else 0
        head_y = bottom - 77 + crouch
        hip_y = bottom - 35 + crouch
        shoulder_y = bottom - 58 + crouch
        # Scarf with two flowing tails.
        tail = -self.facing
        scarf = [(x - self.facing * 4, head_y + 10), (x + tail * 26, head_y + 8),
                 (x + tail * (49 + int(abs(stride))), head_y + 22), (x + tail * 29, head_y + 30),
                 (x + self.facing * 5, head_y + 19)]
        pygame.draw.polygon(surface, red, scarf)
        pygame.draw.line(surface, (255, 104, 111), scarf[1], scarf[2], 2)
        # Hood and face.
        pygame.draw.circle(surface, dark, (x, head_y), 18)
        hood = [(x - 17, head_y + 2), (x - 10, head_y - 17), (x + 11, head_y - 17),
                (x + 18, head_y + 1), (x + 11, head_y + 16), (x - 12, head_y + 16)]
        pygame.draw.polygon(surface, armor, hood)
        # Bright eye slit makes the hero readable at a distance.
        ex = x + self.facing * 5
        pygame.draw.line(surface, settings.COLOR_TEXT, (ex - self.facing * 2, head_y), (ex + self.facing * 11, head_y - 3), 4)
        pygame.draw.line(surface, red, (ex - self.facing * 1, head_y + 5), (ex + self.facing * 9, head_y + 3), 1)
        # Neck, shoulder plates and torso.
        self._line(surface, armor_hi, (x, head_y + 14), (x, shoulder_y + 7), 11)
        pygame.draw.polygon(surface, armor, [(x - 15, shoulder_y), (x + 15, shoulder_y), (x + 12, hip_y), (x - 12, hip_y)])
        pygame.draw.polygon(surface, (20, 28, 39), [(x - 9, shoulder_y + 3), (x + 9, shoulder_y + 3), (x + 7, hip_y - 2), (x - 7, hip_y - 2)])
        self._line(surface, red, (x - 12, hip_y - 3), (x + 12, hip_y - 3), 3)
        pygame.draw.circle(surface, green if self.hidden else red, (x, shoulder_y + 13), 3)
        # Arms / gauntlets.
        if self.attacking:
            front = (x + self.facing * 28, shoulder_y - 4); back = (x - self.facing * 19, shoulder_y + 15)
            self._line(surface, settings.COLOR_PLAYER, (x, shoulder_y + 3), front, 7)
            self._line(surface, settings.COLOR_PLAYER, (x, shoulder_y + 5), back, 6)
            pygame.draw.circle(surface, armor_hi, front, 6)
        else:
            left = (x - 20, shoulder_y + 17 + int(stride)); right = (x + 20, shoulder_y + 17 - int(stride))
            self._line(surface, settings.COLOR_PLAYER, (x - 7, shoulder_y + 3), left, 6)
            self._line(surface, settings.COLOR_PLAYER, (x + 7, shoulder_y + 3), right, 6)
        # Legs and armored boots.
        if self.attacking: stride = 0
        lfoot = (x - 16 + int(stride), bottom); rfoot = (x + 16 - int(stride), bottom)
        self._line(surface, settings.COLOR_PLAYER, (x - 6, hip_y), lfoot, 7)
        self._line(surface, settings.COLOR_PLAYER, (x + 6, hip_y), rfoot, 7)
        self._line(surface, dark, lfoot, (lfoot[0] - self.facing * 13, bottom + 1), 7)
        self._line(surface, dark, rfoot, (rfoot[0] - self.facing * 13, bottom + 1), 7)
        # Utility pouches and belt.
        pygame.draw.rect(surface, armor_hi, (x - 17, hip_y - 3, 8, 11), border_radius=2)
        pygame.draw.rect(surface, armor_hi, (x + 9, hip_y - 3, 8, 11), border_radius=2)
        # Katana: sheath at rest, glowing motion blade during attack.
        if not self.attacking:
            sx = x - self.facing * 7
            self._line(surface, (126, 87, 49), (sx, bottom - 38), (sx - self.facing * 18, bottom - 69), 6)
            self._line(surface, (210, 216, 222), (sx - self.facing * 16, bottom - 67), (sx - self.facing * 45, bottom - 97), 3)
            self._line(surface, red, (sx - self.facing * 12, bottom - 66), (sx - self.facing * 20, bottom - 74), 3)
        else:
            hx, hy = x + self.facing * 30, bottom - 53
            tip = (hx + self.facing * 62, hy - 35)
            glow = pygame.Surface((180, 120), pygame.SRCALPHA)
            pygame.draw.line(glow, (255, 55, 70, 45), (20, 85), (145, 20), 16)
            surface.blit(glow, (x - 20, bottom - 110))
            self._line(surface, (214, 220, 226), (hx, hy), tip, 6)
            self._line(surface, (255, 255, 255), (hx + self.facing * 7, hy - 4), tip, 2)
            # Dynamic slash arc.
            arc_rect = pygame.Rect(x - 72, bottom - 126, 144, 110)
            start = math.radians(205 if self.facing == 1 else -25)
            end = math.radians(335 if self.facing == 1 else 155)
            pygame.draw.arc(surface, red, arc_rect, start, end, 5)
        if self.hidden:
            pygame.draw.arc(surface, green, (x - 35, bottom - 112, 70, 82), math.radians(25), math.radians(155), 3)
