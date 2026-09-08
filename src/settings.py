"""
Central place for every tunable number and color in the game.

Why this file exists:
Hard-coded numbers scattered across gameplay files ("magic numbers") are the
#1 reason small games become painful to balance. Keeping them here means you
can tweak jump height, attack damage, or colors without hunting through
five files.
"""

# ---------------------------------------------------------------------------
# Window / timing
# ---------------------------------------------------------------------------
WIDTH = 1280
HEIGHT = 720
FPS = 60
GROUND_Y = HEIGHT - 80

# ---------------------------------------------------------------------------
# Color palette
# Dark, minimalist "assassin" theme with a pale-green stealth accent
# (matches a clean/professional look rather than a flashy arcade look).
# ---------------------------------------------------------------------------
COLOR_BG = (18, 20, 25)
COLOR_GRID = (26, 28, 34)
COLOR_GROUND = (42, 45, 52)
COLOR_GROUND_EDGE = (75, 78, 85)

COLOR_PLAYER = (225, 228, 235)
COLOR_ENEMY_IDLE = (150, 152, 158)
COLOR_ENEMY_ALERT = (222, 92, 92)

COLOR_ACCENT_RED = (196, 48, 68)      # attacks, damage, alert state
COLOR_ACCENT_GREEN = (129, 209, 156)  # stealth / assassination (pale green)
COLOR_TEXT = (222, 224, 230)
COLOR_TEXT_DIM = (140, 143, 150)
COLOR_PANEL = (40, 43, 50)
COLOR_PANEL_BORDER = (60, 63, 72)

# ---------------------------------------------------------------------------
# Player tuning
# ---------------------------------------------------------------------------
PLAYER_WIDTH = 34
PLAYER_HEIGHT = 76
PLAYER_SPEED = 5.0
PLAYER_JUMP_POWER = -13.0
PLAYER_GRAVITY = 0.65
PLAYER_MAX_HEALTH = 100

ATTACK_DURATION = 18          # frames the attack hitbox stays active
ATTACK_COOLDOWN = 28          # frames before you can attack again
ATTACK_DAMAGE = 25
ATTACK_RANGE = 48
ATTACK_HEIGHT = 38

STEALTH_DURATION = 90         # frames of stealth per activation (~1.5s)
ASSASSINATION_RANGE = 65
ASSASSINATION_DAMAGE = 9999   # instant kill

INVULNERABILITY_FRAMES = 45   # brief i-frames after getting hit

# ---------------------------------------------------------------------------
# Enemy tuning
# ---------------------------------------------------------------------------
ENEMY_WIDTH = 34
ENEMY_HEIGHT = 72
ENEMY_MAX_HEALTH = 100
ENEMY_SPEED = 1.25
ENEMY_DETECTION_RANGE = 270
ENEMY_ATTACK_RANGE = 46
ENEMY_ATTACK_DAMAGE = 12
ENEMY_ATTACK_COOLDOWN = 70
ENEMY_ATTACK_WINDUP = 20       # telegraph frames before the hit lands

# ---------------------------------------------------------------------------
# Audio (procedurally generated, see audio.py — no external asset files)
# ---------------------------------------------------------------------------
SAMPLE_RATE = 44100
MASTER_VOLUME = 0.5

# ---------------------------------------------------------------------------
# Particle / screen-shake tuning
# ---------------------------------------------------------------------------
SHAKE_ON_HIT = 4
SHAKE_ON_ASSASSINATION = 9
PARTICLE_GRAVITY = 0.25
