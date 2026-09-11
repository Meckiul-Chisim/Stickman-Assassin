"""Stickman Assassin entry point with level results/progression."""

import math
import pygame

from src import settings
from src.game import Game


class LevelGame(Game):
    """Mobile-friendly level flow layered over the existing combat game."""

    def __init__(self, screen):
        # Game.__init__ calls _spawn_world(), so level must exist first.
        self.level = 1
        self.level_complete = False
        self.stars = 0
        super().__init__(screen)

    def _spawn_world(self):
        from src.entities.player import Player
        from src.entities.enemy import Enemy
        self.player = Player(180, settings.GROUND_Y, self.audio, self.effects)
        count = min(2 + self.level - 1, 5)
        positions = [620, 820, 1010, 1140, 470]
        self.enemies = [Enemy(positions[i], settings.GROUND_Y, self.audio, self.effects) for i in range(count)]
        for enemy in self.enemies:
            enemy.max_health = settings.ENEMY_MAX_HEALTH + (self.level - 1) * 10
            enemy.health = enemy.max_health
            enemy.speed = settings.ENEMY_SPEED + (self.level - 1) * 0.08

    def restart(self):
        super().restart()
        self.level_complete = False
        self.stars = 0

    def next_level(self):
        self.level += 1
        self.restart()

    def _rating(self):
        hp = self.player.health / self.player.max_health
        return 3 if hp >= 0.80 else 2 if hp >= 0.45 else 1

    def _result_button(self, pos):
        replay = pygame.Rect(settings.WIDTH // 2 - 275, 500, 250, 70)
        next_btn = pygame.Rect(settings.WIDTH // 2 + 25, 500, 250, 70)
        if replay.collidepoint(pos):
            return "replay"
        if next_btn.collidepoint(pos):
            return "next"
        return None

    def handle_events(self):
        if not self.level_complete:
            return super().handle_events()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key in (pygame.K_n, pygame.K_RETURN, pygame.K_SPACE):
                    self.next_level()
                elif event.key in (pygame.K_r, pygame.K_p):
                    self.restart()
            elif event.type == pygame.FINGERDOWN:
                pos = (int(event.x * settings.WIDTH), int(event.y * settings.HEIGHT))
                action = self._result_button(pos)
                if action == "next":
                    self.next_level()
                elif action == "replay":
                    self.restart()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                action = self._result_button(event.pos)
                if action == "next":
                    self.next_level()
                elif action == "replay":
                    self.restart()
        return True

    def update(self):
        if self.level_complete:
            self.effects.update()
            return
        super().update()
        if self.player.alive and not self.enemies:
            self.level_complete = True
            self.stars = self._rating()

    def _star(self, cx, cy, radius, filled):
        points = []
        for i in range(10):
            angle = -math.pi / 2 + i * math.pi / 5
            r = radius if i % 2 == 0 else radius * 0.43
            points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
        color = settings.COLOR_GOLD if filled else (65, 70, 80)
        pygame.draw.polygon(self.screen, color, points)
        pygame.draw.polygon(self.screen, settings.COLOR_TEXT_DIM, points, 2)

    def _button(self, rect, label, border):
        pygame.draw.rect(self.screen, (20, 27, 38), rect, border_radius=14)
        pygame.draw.rect(self.screen, border, rect, 2, border_radius=14)
        font = pygame.font.Font(None, 30)
        text = font.render(label, True, settings.COLOR_TEXT)
        self.screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

    def _draw_results(self):
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 8, 14, 225))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Rect(settings.WIDTH // 2 - 350, 90, 700, 535)
        pygame.draw.rect(self.screen, settings.COLOR_PANEL, panel, border_radius=20)
        pygame.draw.rect(self.screen, settings.COLOR_PANEL_BORDER, panel, 2, border_radius=20)

        title_font = pygame.font.Font(None, 62)
        big_font = pygame.font.Font(None, 42)
        small_font = pygame.font.Font(None, 25)

        title = title_font.render("LEVEL COMPLETE", True, settings.COLOR_ACCENT_GREEN)
        self.screen.blit(title, (settings.WIDTH // 2 - title.get_width() // 2, 125))
        mission = small_font.render(f"MISSION {self.level} CLEARED", True, settings.COLOR_TEXT_DIM)
        self.screen.blit(mission, (settings.WIDTH // 2 - mission.get_width() // 2, 190))

        for i in range(3):
            self._star(settings.WIDTH // 2 - 110 + i * 110, 265, 42, i < self.stars)

        score = big_font.render(f"ASSASSINATIONS  {self.kills}", True, settings.COLOR_TEXT)
        self.screen.blit(score, (settings.WIDTH // 2 - score.get_width() // 2, 350))

        self._button(pygame.Rect(settings.WIDTH // 2 - 275, 500, 250, 70), "PLAY AGAIN", settings.COLOR_PANEL_BORDER)
        self._button(pygame.Rect(settings.WIDTH // 2 + 25, 500, 250, 70), "NEXT LEVEL", settings.COLOR_ACCENT_GREEN)

        hint = small_font.render("N / ENTER = Next   •   R / P = Replay", True, settings.COLOR_TEXT_DIM)
        self.screen.blit(hint, (settings.WIDTH // 2 - hint.get_width() // 2, 590))

    def draw(self):
        super().draw()
        if self.level_complete:
            self._draw_results()
            pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Stickman Assassin")
    LevelGame(screen).run()


if __name__ == "__main__":
    main()
