# Stickman Assassin

A refined, modular rebuild of the original single-file prototype: same core
idea (stealth vs. combat stickman game), now organized so it's actually
maintainable and extendable.

## Run it

```bash
pip install -r requirements.txt
python main.py
```

## Controls

| Key            | Action                                           |
|----------------|---------------------------------------------------|
| A/D or ←/→     | Move                                              |
| SPACE / W / ↑  | Jump                                              |
| J              | Attack                                            |
| C              | Enter stealth                                     |
| E              | Assassinate (hidden + close + enemy not alerted)  |
| R              | Restart after death                               |
| ESC            | Quit                                              |

## Project structure

```
stickman_assassin/
├── main.py                 # entry point only — creates the window, starts Game
├── requirements.txt
└── src/
    ├── settings.py          # every tunable number/color lives here
    ├── audio.py              # procedurally synthesized sound effects
    ├── effects.py             # particles + screen shake (VFX)
    ├── ui.py                  # HUD drawing (health bar, messages, game over)
    ├── game.py                # main loop: wires input -> update -> draw
    └── entities/
        ├── player.py
        └── enemy.py
```

**Why split it up this way:** the original file mixed physics, drawing,
input, and game state into two classes and a loop. That's fine at 300 lines,
but every feature you add after this (a second weapon, a level system, a
menu) makes a single file harder to reason about. Splitting by
responsibility (entities vs. effects vs. audio vs. UI vs. orchestration)
means you can open exactly one file to change exactly one thing.

## What changed from the original, and why

- **Real enemy attacks.** Enemies used to just walk at you forever with no
  way to hurt you — "combat" had no stakes. Now an alerted enemy that gets
  close winds up (telegraphed by a color flash) and hits you for damage.
  This makes stealth a genuine tradeoff against fighting head-on, not just
  a bonus animation.
- **Procedural audio (no asset files).** `audio.py` synthesizes every sound
  effect from scratch with numpy (sine/noise/sweep waveforms + envelopes),
  cached at startup. That means zero missing-file bugs and nothing to
  license — and if you later want real recorded SFX, you only need to
  change `AudioManager._build_all`; nothing else in the game calls sounds
  by anything other than name (`audio.play("hit")`).
- **Particle VFX + screen shake** (`effects.py`) for slashes, hit sparks, the
  assassination burst, and landing dust — all driven by the same small
  `Particle` class so new effects are just new particle presets.
- **Player has real health and can die** (it previously had a `health`
  field that nothing ever touched). There's a game-over screen and a
  restart key.
- **Dependency injection for Audio/Effects.** `Player` and `Enemy` receive
  their `AudioManager`/`EffectsManager` instances instead of importing
  global singletons. This is what keeps them testable in isolation (see
  how the game was verified below) and avoids hidden global state.
- **`settings.py`** centralizes every magic number and color so balancing
  (jump height, damage, colors) never requires touching gameplay code.

## Design language

Dark, minimalist background with a subtle grid — kept a clean, professional
feel rather than a busy arcade look. Red is reserved for danger/damage/
alert states; pale green is reserved for stealth and the assassination
payoff, so the palette also communicates game state at a glance.

## Verified

The full update/draw loop, enemy alert → attack → damage sequence, and the
stealth → assassination → death-fade sequence were run headlessly (SDL
dummy video/audio drivers) for several hundred simulated frames with no
exceptions, confirming the refactor didn't just move bugs around.

## Natural next steps (not built, to keep this a review-able diff)

- A second enemy type or a ranged enemy to give stealth more purpose across
  a full level.
- A simple level/wave system instead of two fixed enemies.
- Swap procedural SFX for mixed/recorded ones once you have an art pass —
  the `audio.py` interface won't need to change.
