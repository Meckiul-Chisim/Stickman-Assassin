"""
Stickman Assassin — entry point.

Run with:
    python main.py

Controls:
    A / D or Left / Right   Move
    SPACE / W / Up          Jump
    J                       Attack
    C                       Enter stealth
    E                       Assassinate (while hidden and close to an unaware enemy)
    R                       Restart (after death)
    ESC                     Quit
"""

import pygame

from src import settings
from src.game import Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Stickman Assassin")

    Game(screen).run()


if __name__ == "__main__":
    main()
