# Stickman Assassin

A modular, mobile-first stealth/combat stickman game built with Python + Pygame. The game is designed around phone touch controls, while the full keyboard controls remain available for fast development and laptop testing.

## Run it

```bash
pip install -r requirements.txt
python main.py
```

## Controls

### Mobile / Touch

- Left / Right — move
- JUMP — jump
- ATK — sword attack
- DASH — quick evasive dash
- HIDE — enter stealth
- ASSASSINATE — instant takedown when hidden and close to an unaware enemy

The touch buttons are drawn directly into the game world and use the same gameplay actions as keyboard input.

### Laptop / Desktop

| Key | Action |
|---|---|
| A/D or ←/→ | Move |
| SPACE / W / ↑ | Jump |
| J | Attack |
| L | Dash |
| C | Enter stealth |
| E | Assassinate |
| R | Restart after death |
| ESC | Quit |

You can also **click the on-screen mobile buttons with a mouse** to test the mobile layout on a laptop.

## Current game features

- Original animated assassin hero model with hood, scarf, armor and katana
- Stealth mode with visual feedback and timer
- Sword combat with hit detection and VFX
- Assassination mechanic
- Enemy detection, alert and attacks
- Player health and game-over state
- Dash with a short invulnerability window
- Procedural sound effects
- Hit particles, assassination effects and screen shake
- Layered night-fortress environment with moon, castle, bridge, banners, trees, mist and lanterns
- Responsive mobile-oriented touch HUD

## Architecture

```text
stickman_assassin/
├── main.py
├── requirements.txt
└── src/
    ├── settings.py
    ├── audio.py
    ├── effects.py
    ├── ui.py
    ├── game.py
    └── entities/
        ├── player.py
        └── enemy.py
```

Gameplay input is intentionally unified: keyboard, mouse and touch all produce the same action names. This makes it easier to keep the mobile and laptop versions consistent as new mechanics are added.

## Next development phase

The next major pass will move the prototype toward a full mobile game experience:

1. Home screen with Play, Heroes, Settings and Progression
2. Level-selection map with locked/unlocked stages
3. Multiple environments and handcrafted levels
4. More enemy types and minibosses
5. Combos, heavy attacks and abilities
6. Better hit reactions and animation states
7. Coins, upgrades and equipment
8. Boss fights and cinematic assassination moments
9. Save/progression system
10. Mobile packaging and performance optimization
