"""HUD and mobile-first touch controls."""

import math
import pygame
from . import settings


class UI:
    def __init__(self):
        self.font = pygame.font.Font(None, 26)
        self.font_small = pygame.font.Font(None, 20)
        self.font_big = pygame.font.Font(None, 46)
        self.font_title = pygame.font.Font(None, 64)
        self.touch_buttons = {}
        self._touch_center = (145, settings.HEIGHT - 122)
        self._build_touch_layout()

    def _build_touch_layout(self):
        s = settings.TOUCH_BUTTON_SIZE
        m = settings.TOUCH_MARGIN
        # Left thumb area: compact virtual D-pad/joystick.
        cx, cy = self._touch_center
        self.touch_buttons = {
            "left": pygame.Rect(cx - 112, cy - 39, s, s),
            "right": pygame.Rect(cx + 34, cy - 39, s, s),
            "jump": pygame.Rect(settings.WIDTH - 205, settings.HEIGHT - 170, s, s),
            "attack": pygame.Rect(settings.WIDTH - 112, settings.HEIGHT - 112, s, s),
            "dash": pygame.Rect(settings.WIDTH - 205, settings.HEIGHT - 76, s, s),
            "stealth": pygame.Rect(settings.WIDTH - 112, settings.HEIGHT - 205, s, s),
            "assassinate": pygame.Rect(settings.WIDTH - 300, settings.HEIGHT - 112, s + 10, s + 10),
        }

    def _panel(self, surface, rect, border=settings.COLOR_PANEL_BORDER):
        pygame.draw.rect(surface, settings.COLOR_PANEL, rect, border_radius=6)
        pygame.draw.rect(surface, border, rect, width=1, border_radius=6)

    def draw_health_bar(self, surface, player):
        pad = 24; width, height = 220, 26
        rect = pygame.Rect(pad, pad, width, height)
        self._panel(surface, rect)
        inner_pad = 4; max_fill = width - inner_pad * 2
        fill = int(max_fill * player.health / player.max_health)
        fill_color = settings.COLOR_ACCENT_RED if player.health > 25 else (235, 120, 90)
        if fill > 0:
            pygame.draw.rect(surface, fill_color, (rect.x + inner_pad, rect.y + inner_pad, fill, height - inner_pad * 2), border_radius=3)
        label = self.font_small.render(f"HP  {player.health}/{player.max_health}", True, settings.COLOR_TEXT)
        surface.blit(label, (rect.x + 10, rect.y + 5))

    def draw_stealth_indicator(self, surface, player):
        if not player.hidden: return
        text = self.font.render("STEALTH", True, settings.COLOR_ACCENT_GREEN)
        x = settings.WIDTH // 2 - text.get_width() // 2
        surface.blit(text, (x, 22))
        bar_w = 90; remaining = player.stealth_timer / settings.STEALTH_DURATION
        pygame.draw.rect(surface, settings.COLOR_PANEL, (settings.WIDTH // 2 - bar_w // 2, 48, bar_w, 4))
        pygame.draw.rect(surface, settings.COLOR_ACCENT_GREEN, (settings.WIDTH // 2 - bar_w // 2, 48, int(bar_w * remaining), 4))

    def draw_kill_counter(self, surface, kills):
        text = self.font.render(f"Assassinations: {kills}", True, settings.COLOR_TEXT)
        surface.blit(text, (settings.WIDTH - text.get_width() - 24, 24))

    def draw_controls_hint(self, surface):
        text = self.font_small.render("A/D Move   SPACE Jump   J Attack   C Stealth   E Assassinate   L Dash   R Restart", True, settings.COLOR_TEXT_DIM)
        surface.blit(text, (24, settings.HEIGHT - 34))

    def draw_touch_controls(self, surface, enabled=True):
        if not enabled:
            return
        # Subtle dark touch zones keep the world visible underneath.
        cx, cy = self._touch_center
        pygame.draw.circle(surface, (18, 24, 34), (cx, cy), settings.TOUCH_JOYSTICK_RADIUS, 2)
        pygame.draw.circle(surface, (80, 95, 112), (cx, cy), 23, 2)
        for action, rect in self.touch_buttons.items():
            radius = min(rect.width, rect.height) // 2
            center = rect.center
            fill = (24, 31, 43, 205)
            layer = pygame.Surface((rect.width + 12, rect.height + 12), pygame.SRCALPHA)
            pygame.draw.circle(layer, fill, (layer.get_width() // 2, layer.get_height() // 2), radius + 4)
            pygame.draw.circle(layer, (76, 91, 108, 220), (layer.get_width() // 2, layer.get_height() // 2), radius + 4, 2)
            surface.blit(layer, (center[0] - layer.get_width() // 2, center[1] - layer.get_height() // 2))
            labels = {"left":"<", "right":">", "jump":"JUMP", "attack":"ATK", "dash":"DASH", "stealth":"HIDE", "assassinate":"ASSASSINATE"}
            rendered = self.font_small.render(labels[action], True, settings.COLOR_TEXT)
            surface.blit(rendered, (center[0] - rendered.get_width() // 2, center[1] - rendered.get_height() // 2))

    def touch_action_at(self, pos):
        """Return a gameplay action for a touch/mouse position, or None."""
        for action, rect in self.touch_buttons.items():
            if rect.collidepoint(pos):
                return action
        # The center joystick zone supports direct left/right thumb movement.
        cx, cy = self._touch_center
        dx = pos[0] - cx
        dy = pos[1] - cy
        if math.hypot(dx, dy) <= settings.TOUCH_JOYSTICK_RADIUS:
            if dx < -18: return "left"
            if dx > 18: return "right"
        return None

    def draw_message(self, surface, text, color=None):
        if not text: return
        color = color or settings.COLOR_TEXT
        rendered = self.font_big.render(text, True, color)
        x = settings.WIDTH // 2 - rendered.get_width() // 2
        surface.blit(rendered, (x, 110))

    def draw_game_over(self, surface, kills):
        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 12, 190)); surface.blit(overlay, (0, 0))
        title = self.font_title.render("YOU DIED", True, settings.COLOR_ACCENT_RED)
        surface.blit(title, (settings.WIDTH // 2 - title.get_width() // 2, settings.HEIGHT // 2 - 80))
        sub = self.font.render(f"Assassinations: {kills}", True, settings.COLOR_TEXT)
        surface.blit(sub, (settings.WIDTH // 2 - sub.get_width() // 2, settings.HEIGHT // 2 - 10))
        hint = self.font_small.render("Press R or tap ATTACK to restart", True, settings.COLOR_TEXT_DIM)
        surface.blit(hint, (settings.WIDTH // 2 - hint.get_width() // 2, settings.HEIGHT // 2 + 30))
