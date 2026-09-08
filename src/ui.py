"""
All HUD drawing lives here, kept separate from gameplay logic so the visual
style (panels, fonts, spacing) can be restyled without touching Game/Player.
"""

import pygame

from . import settings


class UI:
    def __init__(self):
        self.font = pygame.font.Font(None, 26)
        self.font_small = pygame.font.Font(None, 20)
        self.font_big = pygame.font.Font(None, 46)
        self.font_title = pygame.font.Font(None, 64)

    def _panel(self, surface, rect, border=settings.COLOR_PANEL_BORDER):
        pygame.draw.rect(surface, settings.COLOR_PANEL, rect, border_radius=6)
        pygame.draw.rect(surface, border, rect, width=1, border_radius=6)

    def draw_health_bar(self, surface, player):
        pad = 24
        width, height = 220, 26
        rect = pygame.Rect(pad, pad, width, height)
        self._panel(surface, rect)

        inner_pad = 4
        max_fill = width - inner_pad * 2
        fill = int(max_fill * player.health / player.max_health)
        fill_color = settings.COLOR_ACCENT_RED if player.health > 25 else (235, 120, 90)
        if fill > 0:
            pygame.draw.rect(
                surface, fill_color,
                (rect.x + inner_pad, rect.y + inner_pad, fill, height - inner_pad * 2),
                border_radius=3,
            )

        label = self.font_small.render(f"HP  {player.health}/{player.max_health}", True, settings.COLOR_TEXT)
        surface.blit(label, (rect.x + 10, rect.y + 5))

    def draw_stealth_indicator(self, surface, player):
        if not player.hidden:
            return
        text = self.font.render("STEALTH", True, settings.COLOR_ACCENT_GREEN)
        x = settings.WIDTH // 2 - text.get_width() // 2
        surface.blit(text, (x, 22))

        # Small depleting bar under the label showing time remaining.
        bar_w = 90
        remaining = player.stealth_timer / settings.STEALTH_DURATION
        pygame.draw.rect(surface, settings.COLOR_PANEL, (settings.WIDTH // 2 - bar_w // 2, 48, bar_w, 4))
        pygame.draw.rect(
            surface, settings.COLOR_ACCENT_GREEN,
            (settings.WIDTH // 2 - bar_w // 2, 48, int(bar_w * remaining), 4),
        )

    def draw_kill_counter(self, surface, kills):
        text = self.font.render(f"Assassinations: {kills}", True, settings.COLOR_TEXT)
        surface.blit(text, (settings.WIDTH - text.get_width() - 24, 24))

    def draw_controls_hint(self, surface):
        text = self.font_small.render(
            "A/D Move   SPACE Jump   J Attack   C Stealth   E Assassinate   R Restart",
            True, settings.COLOR_TEXT_DIM,
        )
        surface.blit(text, (24, settings.HEIGHT - 34))

    def draw_message(self, surface, text, color=None):
        if not text:
            return
        color = color or settings.COLOR_TEXT
        rendered = self.font_big.render(text, True, color)
        x = settings.WIDTH // 2 - rendered.get_width() // 2
        surface.blit(rendered, (x, 110))

    def draw_game_over(self, surface, kills):
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 12, 190))
        surface.blit(overlay, (0, 0))

        title = self.font_title.render("YOU DIED", True, settings.COLOR_ACCENT_RED)
        surface.blit(title, (settings.WIDTH // 2 - title.get_width() // 2, settings.HEIGHT // 2 - 80))

        sub = self.font.render(f"Assassinations: {kills}", True, settings.COLOR_TEXT)
        surface.blit(sub, (settings.WIDTH // 2 - sub.get_width() // 2, settings.HEIGHT // 2 - 10))

        hint = self.font_small.render("Press R to restart", True, settings.COLOR_TEXT_DIM)
        surface.blit(hint, (settings.WIDTH // 2 - hint.get_width() // 2, settings.HEIGHT // 2 + 30))
