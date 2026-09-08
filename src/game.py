"""
The Game class wires everything together: entities, audio, effects, UI,
and the main update/draw loop.
"""

import math
import pygame

from . import settings
from .audio import AudioManager
from .effects import EffectsManager
from .entities.player import Player
from .entities.enemy import Enemy
from .ui import UI


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.audio = AudioManager()
        self.effects = EffectsManager()
        self.ui = UI()

        self.message = ""
        self.message_timer = 0
        self.kills = 0
        self._message_color = settings.COLOR_TEXT_DIM

        self._spawn_world()

    def _spawn_world(self):
        self.player = Player(260, settings.GROUND_Y, self.audio, self.effects)
        self.enemies = [
            Enemy(720, settings.GROUND_Y, self.audio, self.effects),
            Enemy(980, settings.GROUND_Y, self.audio, self.effects),
        ]

    def restart(self):
        self.effects = EffectsManager()
        self.kills = 0
        self.message = ""
        self.message_timer = 0
        self._spawn_world()

    # -- input ------------------------------------------------------------------
    def handle_events(self) -> bool:
        """Returns False when the game should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r and not self.player.alive:
                    self.restart()
                    continue
                if not self.player.alive:
                    continue
                if event.key == pygame.K_j:
                    self.player.attack()
                elif event.key == pygame.K_e:
                    self._try_assassination()
                elif event.key == pygame.K_c:
                    self.player.enter_stealth()
        return True

    def _try_assassination(self):
        for enemy in self.enemies:
            if enemy.can_be_assassinated(self.player):
                enemy.take_damage(enemy.max_health)
                self.kills += 1
                self.player.hidden = False
                self.player.stealth_timer = 0
                self.effects.assassination_burst(enemy.x, enemy.y - 40)
                self.audio.play("assassinate")
                self._show_message("ASSASSINATION", 70, settings.COLOR_ACCENT_GREEN)
                return
        self._show_message("Get closer while hidden", 55, settings.COLOR_TEXT_DIM)

    def _show_message(self, text, duration, color=None):
        self.message = text
        self.message_timer = duration
        self._message_color = color or settings.COLOR_TEXT_DIM

    # -- update -------------------------------------------------------------------
    def update(self):
        keys = pygame.key.get_pressed()
        self.player.update(keys)

        attack_rect = self.player.get_attack_rect()
        for enemy in self.enemies:
            enemy.update(self.player)
            if (
                self.player.attacking
                and enemy.id not in self.player.attack_has_hit
                and not enemy.dead
                and attack_rect.colliderect(enemy.rect)
            ):
                enemy.take_damage(settings.ATTACK_DAMAGE, hit_x=enemy.x, hit_y=enemy.y - 40)
                self.player.attack_has_hit.add(enemy.id)

        self.enemies = [e for e in self.enemies if not e.fully_gone]
        self.effects.update()

        if self.message_timer > 0:
            self.message_timer -= 1

    # -- cinematic background ----------------------------------------------------
    def _draw_background(self, surface):
        """Draw an original layered night-fortress scene with parallax depth."""
        w, h = settings.WIDTH, settings.HEIGHT

        # Vertical night gradient.
        for y in range(h):
            t = y / h
            color = (
                int(8 + 13 * t),
                int(16 + 17 * t),
                int(38 + 22 * t),
            )
            pygame.draw.line(surface, color, (0, y), (w, y))

        # Moon glow and moon.
        moon = pygame.Surface((260, 260), pygame.SRCALPHA)
        for radius, alpha in ((112, 10), (92, 16), (75, 28)):
            pygame.draw.circle(moon, (180, 215, 255, alpha), (130, 130), radius)
        pygame.draw.circle(moon, (220, 233, 244, 235), (130, 130), 58)
        pygame.draw.circle(moon, (197, 216, 233, 70), (110, 112), 12)
        pygame.draw.circle(moon, (197, 216, 233, 55), (145, 138), 8)
        surface.blit(moon, (890, 35))

        # Distant mountains.
        far = (31, 49, 78)
        pygame.draw.polygon(surface, far, [(0, 430), (170, 265), (330, 420), (505, 235), (700, 430), (870, 275), (1060, 420), (1210, 245), (1280, 340), (1280, 570), (0, 570)])
        near = (24, 38, 59)
        pygame.draw.polygon(surface, near, [(0, 495), (190, 340), (370, 485), (575, 300), (790, 490), (1000, 325), (1180, 470), (1280, 390), (1280, 590), (0, 590)])

        # Castle silhouette in the distance.
        self._draw_castle(surface, 915, 270, 0.9)

        # Waterfall beneath the fortress.
        pygame.draw.polygon(surface, (77, 116, 147), [(930, 390), (1015, 390), (995, 530), (958, 570), (943, 520)])
        pygame.draw.line(surface, (124, 169, 195), (970, 405), (970, 535), 3)

        # Bridge and distant buildings.
        pygame.draw.rect(surface, (19, 28, 40), (500, 470, 330, 16))
        pygame.draw.line(surface, (64, 87, 107), (500, 470), (585, 420), 3)
        pygame.draw.line(surface, (585, 420), (675, 470), 3)
        pygame.draw.line(surface, (675, 470), (760, 420), 3)
        pygame.draw.line(surface, (760, 420), (830, 470), 3)
        for x in (535, 615, 700, 785):
            pygame.draw.line(surface, (15, 24, 35), (x, 470), (x, 525), 5)

        # Foreground temple structure.
        pygame.draw.polygon(surface, (10, 15, 21), [(0, 215), (250, 215), (305, 265), (0, 265)])
        pygame.draw.rect(surface, (13, 18, 25), (0, 265, 305, 300))
        pygame.draw.line(surface, (76, 54, 38), (0, 267), (305, 267), 5)
        pygame.draw.rect(surface, (29, 25, 25), (35, 330, 85, 235))
        pygame.draw.rect(surface, (44, 36, 28), (50, 345, 55, 180))

        # Roof tiles.
        for x in range(-20, 310, 24):
            pygame.draw.line(surface, (48, 47, 53), (x, 220), (x + 35, 255), 5)

        # Lanterns and red banners.
        self._draw_lantern(surface, 215, 330, 1.0)
        self._draw_banner(surface, 360, 265, 115)
        self._draw_banner(surface, 1125, 300, 125)
        self._draw_banner(surface, 1215, 335, 100)

        # Foreground foliage for depth.
        self._draw_tree(surface, 90, settings.GROUND_Y, 1.1)
        self._draw_tree(surface, 1210, settings.GROUND_Y, 1.35)
        self._draw_tree(surface, 1090, settings.GROUND_Y, 0.75)

        # Atmospheric mist bands.
        mist = pygame.Surface((w, 170), pygame.SRCALPHA)
        for y in range(0, 170, 22):
            alpha = 14 if y < 90 else 8
            pygame.draw.ellipse(mist, (130, 160, 180, alpha), (-80 + y * 2, y, 620, 80))
            pygame.draw.ellipse(mist, (130, 160, 180, alpha), (690 - y, y + 18, 700, 80))
        surface.blit(mist, (0, 390))

        # Ground platform with stone blocks.
        pygame.draw.rect(surface, (22, 25, 29), (0, settings.GROUND_Y, w, 80))
        pygame.draw.line(surface, (102, 111, 112), (0, settings.GROUND_Y), (w, settings.GROUND_Y), 3)
        for x in range(0, w, 82):
            pygame.draw.line(surface, (39, 43, 47), (x, settings.GROUND_Y + 2), (x + 16, h), 2)
            pygame.draw.line(surface, (42, 45, 49), (x + 16, settings.GROUND_Y + 42), (x + 75, settings.GROUND_Y + 42), 2)

        # A subtle green horizon line reinforces the stealth identity.
        pygame.draw.line(surface, (53, 91, 72), (0, settings.GROUND_Y - 1), (w, settings.GROUND_Y - 1), 1)

    def _draw_castle(self, surface, x, y, scale):
        def r(rx, ry, rw, rh, color):
            pygame.draw.rect(surface, color, (int(x + rx * scale), int(y + ry * scale), int(rw * scale), int(rh * scale)))

        dark = (17, 27, 43)
        roof = (12, 21, 35)
        warm = (192, 137, 72)
        r(-85, 115, 250, 155, dark)
        r(-45, 55, 170, 210, dark)
        r(-15, -5, 110, 270, dark)
        for ry, rw, rx in ((112, 210, -65), (52, 145, -30), (-8, 100, -10)):
            pygame.draw.polygon(surface, roof, [(x + rx * scale, y + ry * scale), (x + (rx + rw) * scale, y + ry * scale), (x + (rx + rw - 25) * scale, y + (ry - 28) * scale), (x + (rx + 25) * scale, y + (ry - 28) * scale)])
        for row, yy in enumerate((92, 137, 180)):
            for xx in range(-35, 105, 28):
                if (xx + row) % 3 != 0:
                    r(xx, yy, 9, 13, warm)

    def _draw_lantern(self, surface, x, y, scale=1):
        pygame.draw.line(surface, (65, 49, 37), (x, y - 65 * scale), (x, y), max(1, int(2 * scale)))
        body = pygame.Rect(int(x - 11 * scale), int(y - 47 * scale), int(22 * scale), int(32 * scale))
        glow = pygame.Surface((int(90 * scale), int(90 * scale)), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 190, 90, 22), (int(45 * scale), int(45 * scale)), int(42 * scale))
        surface.blit(glow, (int(x - 45 * scale), int(y - 57 * scale)))
        pygame.draw.rect(surface, (85, 62, 40), body, max(1, int(2 * scale)))
        pygame.draw.rect(surface, (255, 192, 92), body.inflate(-7 * scale, -7 * scale))
        pygame.draw.line(surface, (105, 76, 44), (x - 15 * scale, y - 50 * scale), (x + 15 * scale, y - 50 * scale), 2)

    def _draw_banner(self, surface, x, y, length):
        pygame.draw.line(surface, (56, 44, 36), (x, y), (x, y + length), 3)
        pts = [(x + 3, y + 12), (x + 42, y + 12), (x + 37, y + length - 10), (x + 5, y + length), (x + 3, y + 12)]
        pygame.draw.polygon(surface, (105, 29, 39), pts)
        pygame.draw.circle(surface, (166, 55, 65), (x + 23, y + 52), 13, 2)

    def _draw_tree(self, surface, x, ground, scale):
        trunk = (18, 24, 27)
        pygame.draw.line(surface, trunk, (x, ground), (x - 16 * scale, ground - 145 * scale), max(3, int(7 * scale)))
        pygame.draw.line(surface, trunk, (x - 12 * scale, ground - 70 * scale), (x - 68 * scale, ground - 120 * scale), max(2, int(5 * scale)))
        pygame.draw.line(surface, trunk, (x - 5 * scale, ground - 95 * scale), (x + 55 * scale, ground - 145 * scale), max(2, int(5 * scale)))
        for dx, dy, r in ((-55, -135, 42), (-5, -155, 50), (42, -132, 45), (-25, -105, 38)):
            pygame.draw.circle(surface, (12, 24, 27), (int(x + dx * scale), int(ground + dy * scale)), int(r * scale))

    def draw(self):
        scene = pygame.Surface((settings.WIDTH, settings.HEIGHT))
        self._draw_background(scene)

        for enemy in self.enemies:
            enemy.draw(scene)
        self.player.draw(scene)
        self.effects.draw(scene)

        self.ui.draw_health_bar(scene, self.player)
        self.ui.draw_stealth_indicator(scene, self.player)
        self.ui.draw_kill_counter(scene, self.kills)
        self.ui.draw_controls_hint(scene)
        if self.message_timer > 0:
            self.ui.draw_message(scene, self.message, self._message_color)

        offset = self.effects.get_shake_offset()
        self.screen.fill(settings.COLOR_BG)
        self.screen.blit(scene, offset)

        if not self.player.alive:
            self.ui.draw_game_over(self.screen, self.kills)

        pygame.display.flip()

    # -- main loop ------------------------------------------------------------------
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(settings.FPS)
        pygame.quit()
