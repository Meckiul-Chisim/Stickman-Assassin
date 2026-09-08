"""
The Game class wires everything together: entities, audio, effects, UI,
and the main update/draw loop. Nothing here draws pixels directly except
the background — that's delegated to UI/effects/entities so this file
stays readable as "what happens", not "how it looks".
"""

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
        self._message_color = color

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

    # -- draw ---------------------------------------------------------------------
    def _draw_background(self, surface):
        surface.fill(settings.COLOR_BG)
        for x in range(0, settings.WIDTH, 80):
            pygame.draw.line(surface, settings.COLOR_GRID, (x, 0), (x, settings.GROUND_Y), 1)
        for y in range(80, settings.GROUND_Y, 80):
            pygame.draw.line(surface, settings.COLOR_GRID, (0, y), (settings.WIDTH, y), 1)

        pygame.draw.rect(surface, settings.COLOR_GROUND, (0, settings.GROUND_Y, settings.WIDTH, 80))
        pygame.draw.line(
            surface, settings.COLOR_GROUND_EDGE, (0, settings.GROUND_Y), (settings.WIDTH, settings.GROUND_Y), 2
        )

    def draw(self):
        # Render the whole scene to a fixed-size buffer, then blit it with a
        # shake offset. This way the shake never reveals gaps at the edges.
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
            self.ui.draw_message(scene, self.message, getattr(self, "_message_color", None))

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
