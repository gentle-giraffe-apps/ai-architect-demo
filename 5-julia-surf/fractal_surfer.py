"""Fractal Surfer - An arcade-style Julia set exploration game."""

import pygame
import numpy as np
import math
import random
import sys
from collections import deque

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
GRID_W, GRID_H = 400, 400
TILE = 2
WIN_W, WIN_H = GRID_W * TILE, GRID_H * TILE
TITLE_HEIGHT = 36
HUD_HEIGHT = 48
SCREEN_W = WIN_W
SCREEN_H = TITLE_HEIGHT + WIN_H + HUD_HEIGHT
FPS = 60
MAX_ITER = 28

# Fractal viewport in complex plane
FRAC_RANGE = 1.5

# Player
PLAYER_SPEED = 1.8
DASH_SPEED = 5.0
DASH_DURATION = 8
DASH_COOLDOWN = 60
TRAIL_LENGTH = 20

# Energy
MAX_ENERGY = 100.0
BASE_DRAIN = 0.02
CHAOS_DRAIN = 0.08
STABLE_RESTORE = 2.0
NODE_RESTORE = 25.0

# Scoring
BOUNDARY_BONUS = 5
TIME_SCORE = 1

# Difficulty
DIFFICULTY_INTERVAL = 120.0

# Colors
COL_BG = (6, 4, 16)
COL_HUD_BG = (10, 8, 24)
COL_HUD_BORDER = (60, 40, 120)
COL_TITLE = (0, 220, 255)
COL_SCORE = (255, 255, 80)
COL_TIME = (80, 255, 180)
COL_ENERGY_HIGH = (0, 255, 120)
COL_ENERGY_MED = (255, 255, 0)
COL_ENERGY_LOW = (255, 40, 40)
COL_ENERGY_BG = (30, 20, 50)
COL_ENERGY_BORDER = (100, 80, 160)
COL_WHITE = (255, 255, 255)
COL_GAMEOVER = (255, 60, 60)


def _lerp_color(c1, c2, f):
    return (
        int(c1[0] + (c2[0] - c1[0]) * f),
        int(c1[1] + (c2[1] - c1[1]) * f),
        int(c1[2] + (c2[2] - c1[2]) * f),
    )


def build_palette(size=256):
    """Build a cosmic nebula palette matching the concept art."""
    stops = [
        (0.00, (2, 1, 12)),
        (0.04, (8, 4, 40)),
        (0.10, (15, 8, 70)),
        (0.16, (40, 15, 120)),
        (0.22, (80, 10, 160)),
        (0.28, (30, 60, 180)),
        (0.34, (10, 120, 200)),
        (0.40, (0, 180, 230)),
        (0.46, (10, 220, 180)),
        (0.52, (60, 250, 100)),
        (0.58, (180, 255, 40)),
        (0.64, (255, 240, 20)),
        (0.70, (255, 180, 10)),
        (0.76, (255, 100, 10)),
        (0.82, (255, 40, 40)),
        (0.88, (220, 20, 120)),
        (0.94, (140, 10, 160)),
        (1.00, (2, 1, 12)),
    ]
    palette = []
    for i in range(size):
        t = i / size
        for si in range(len(stops) - 1):
            if stops[si][0] <= t <= stops[si + 1][0]:
                span = stops[si + 1][0] - stops[si][0]
                f = (t - stops[si][0]) / span if span > 0 else 0
                color = _lerp_color(stops[si][1], stops[si + 1][1], f)
                palette.append(color)
                break
        else:
            palette.append(stops[-1][1])
    return palette


PALETTE = build_palette(256)
INSIDE_COLOR = (3, 1, 10)

# Build numpy palette lookup table (256 x 3)
PALETTE_ARRAY = np.array(PALETTE, dtype=np.uint8)
INSIDE_ARRAY = np.array(INSIDE_COLOR, dtype=np.uint8)

# Precompute grid coordinates in complex plane
_gx = np.arange(GRID_W, dtype=np.float64)
_gy = np.arange(GRID_H, dtype=np.float64)
GRID_ZR = (_gx / GRID_W - 0.5) * 2 * FRAC_RANGE  # shape (GRID_W,)
GRID_ZI = (_gy / GRID_H - 0.5) * 2 * FRAC_RANGE  # shape (GRID_H,)
# Full 2D grids: ZR_GRID[y, x], ZI_GRID[y, x]
ZR_GRID, ZI_GRID = np.meshgrid(GRID_ZR, GRID_ZI)


def julia_escape(zr, zi, cr, ci, max_iter):
    """Return smooth escape iteration count (0 = inside set).

    Scalar version used for single-point terrain queries.
    """
    for n in range(max_iter):
        zr2 = zr * zr
        zi2 = zi * zi
        if zr2 + zi2 > 4.0:
            mag = zr2 + zi2
            smooth = n + 1 - math.log(math.log(mag)) / math.log(2)
            return max(smooth, 0.001)
        zi = 2.0 * zr * zi + ci
        zr = zr2 - zi2 + cr
    return 0


def julia_escape_numpy(cr, ci, max_iter):
    """Vectorized Julia set computation over the entire grid.

    Returns a float64 array of shape (GRID_H, GRID_W) with smooth escape values.
    0 means inside the set.
    """
    zr = ZR_GRID.copy()
    zi = ZI_GRID.copy()
    escape = np.zeros((GRID_H, GRID_W), dtype=np.float64)
    alive = np.ones((GRID_H, GRID_W), dtype=bool)

    for n in range(max_iter):
        zr2 = zr * zr
        zi2 = zi * zi
        mag = zr2 + zi2

        # Points that just escaped this iteration
        escaped = alive & (mag > 4.0)
        if np.any(escaped):
            log_mag = np.log(np.maximum(mag[escaped], 1e-10))
            smooth = n + 1 - np.log(np.maximum(log_mag, 1e-10)) / np.log(2)
            escape[escaped] = np.maximum(smooth, 0.001)
            alive[escaped] = False

        if not np.any(alive):
            break

        # Iterate: z = z^2 + c
        zi_new = 2.0 * zr * zi + ci
        zr_new = zr2 - zi2 + cr
        zr[alive] = zr_new[alive]
        zi[alive] = zi_new[alive]

    return escape


class EnergyNode:
    def __init__(self, gx, gy):
        self.gx = gx
        self.gy = gy
        self.alive = True
        self.pulse = random.random() * math.pi * 2


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Fractal Surfer")
        self.clock = pygame.time.Clock()
        self.fractal_surface = pygame.Surface((GRID_W, GRID_H))
        self.font_title = pygame.font.Font(None, 42)
        self.font_big = pygame.font.Font(None, 36)
        self.font_med = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)
        # Build star field for inside-set regions
        self._star_mask = np.zeros((GRID_H, GRID_W), dtype=bool)
        for _ in range(200):
            sx = random.randint(0, GRID_W - 1)
            sy = random.randint(0, GRID_H - 1)
            self._star_mask[sy, sx] = True
        self.reset()

    def reset(self):
        self.player_x = GRID_W / 2.0
        self.player_y = GRID_H / 2.0
        self.energy = MAX_ENERGY
        self.score = 0
        self.time_alive = 0.0
        self.game_over = False
        self.anim_time = 8.0
        self.difficulty = 1.0
        self.trail = deque(maxlen=TRAIL_LENGTH)
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.dash_dx = 0
        self.dash_dy = 0
        self.nodes = []
        self.node_timer = 0
        self.frame_count = 0
        self.color_offset = 0.0
        self._escape_grid = None
        self._spawn_initial_nodes()

    def _spawn_initial_nodes(self):
        for _ in range(8):
            self._spawn_node()

    def _spawn_node(self):
        gx = random.randint(5, GRID_W - 6)
        gy = random.randint(5, GRID_H - 6)
        self.nodes.append(EnergyNode(gx, gy))

    def _get_c(self):
        t = self.anim_time
        speed = 0.015 * self.difficulty
        r = 0.7885 + 0.06 * math.sin(t * speed * 2.7)
        cr = r * math.cos(t * speed)
        ci = r * math.sin(t * speed * 0.87)
        return (cr, ci)

    def _terrain_value(self, gx, gy):
        gxi, gyi = int(gx), int(gy)
        if 0 <= gxi < GRID_W and 0 <= gyi < GRID_H and self._escape_grid is not None:
            return self._escape_grid[gyi, gxi]
        return 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if self.game_over:
            if keys[pygame.K_r]:
                self.reset()
            return

        dx, dy = 0.0, 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if keys[pygame.K_SPACE] and self.dash_timer == 0 and self.dash_cooldown == 0 and (dx != 0 or dy != 0):
            self.dash_timer = DASH_DURATION
            self.dash_cooldown = DASH_COOLDOWN
            self.dash_dx = dx
            self.dash_dy = dy

        if self.dash_timer > 0:
            self.dash_timer -= 1
            mx = self.dash_dx * DASH_SPEED
            my = self.dash_dy * DASH_SPEED
        else:
            mx = dx * PLAYER_SPEED
            my = dy * PLAYER_SPEED

        self.player_x = max(1, min(GRID_W - 2, self.player_x + mx))
        self.player_y = max(1, min(GRID_H - 2, self.player_y + my))

    def update(self, dt):
        if self.game_over:
            return

        self.anim_time += dt
        self.time_alive += dt
        self.frame_count += 1
        self.color_offset += dt * 12

        self.difficulty = 1.0 + self.time_alive / DIFFICULTY_INTERVAL * 0.15

        self.trail.append((self.player_x, self.player_y))

        escape_val = self._terrain_value(self.player_x, self.player_y)

        if escape_val == 0:
            # Inside the set — stable region, restore energy
            self.energy += STABLE_RESTORE * self.difficulty
        elif escape_val > MAX_ITER * 0.7:
            # High iteration count — near boundary, bonus scoring zone
            self.energy -= BASE_DRAIN * self.difficulty
            self.score += BOUNDARY_BONUS
        else:
            # Low iteration count — escaped quickly, chaotic outer region
            self.energy -= CHAOS_DRAIN * self.difficulty

        self.energy -= BASE_DRAIN * 0.5 * self.difficulty

        if self.frame_count % 10 == 0:
            self.score += TIME_SCORE

        self.energy = max(0, min(MAX_ENERGY, self.energy))

        px, py = int(self.player_x), int(self.player_y)
        for node in self.nodes:
            if node.alive:
                dist = abs(node.gx - px) + abs(node.gy - py)
                if dist < 24:
                    node.alive = False
                    self.energy = min(MAX_ENERGY, self.energy + NODE_RESTORE)
                    self.score += 500

        self.nodes = [n for n in self.nodes if n.alive]
        self.node_timer += 1
        if self.node_timer > 180 and len(self.nodes) < 10:
            self._spawn_node()
            self.node_timer = 0

        if self.energy <= 0:
            self.energy = 0
            self.game_over = True

    def render_fractal(self):
        cr, ci = self._get_c()
        color_off = int(self.color_offset) % 256

        # Compute escape values for the entire grid using numpy
        self._escape_grid = julia_escape_numpy(cr, ci, MAX_ITER)

        # Build RGB pixel array
        pixels = np.zeros((GRID_H, GRID_W, 3), dtype=np.uint8)

        inside = self._escape_grid == 0
        outside = ~inside

        # Inside set — dark with occasional stars
        pixels[inside] = INSIDE_ARRAY

        # Stars twinkle
        star_inside = inside & self._star_mask
        if np.any(star_inside):
            # Use grid x-coords for phase variation
            star_ys, star_xs = np.where(star_inside)
            bright = 30 + (20 * np.sin(self.color_offset * 0.3 + star_xs * 0.5)).astype(np.int32)
            bright = np.clip(bright, 0, 255).astype(np.uint8)
            pixels[star_inside, 0] = bright
            pixels[star_inside, 1] = bright
            pixels[star_inside, 2] = np.clip(bright + 10, 0, 255).astype(np.uint8)

        # Outside set — palette lookup
        if np.any(outside):
            norm = self._escape_grid[outside] / MAX_ITER
            idx = ((norm * 512 + color_off) % 256).astype(np.int32)
            pixels[outside] = PALETTE_ARRAY[idx]

        # Blit to surface
        pygame.surfarray.blit_array(self.fractal_surface, pixels.transpose(1, 0, 2))

    def render(self):
        self.screen.fill(COL_BG)

        # --- Title bar ---
        pygame.draw.rect(self.screen, COL_HUD_BG, (0, 0, SCREEN_W, TITLE_HEIGHT))
        pygame.draw.line(self.screen, COL_HUD_BORDER, (0, TITLE_HEIGHT - 1), (SCREEN_W, TITLE_HEIGHT - 1), 2)
        title = self.font_title.render("FRACTAL SURFER", True, COL_TITLE)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 4))

        # --- Fractal field ---
        self.render_fractal()
        scaled = pygame.transform.scale(self.fractal_surface, (WIN_W, WIN_H))
        self.screen.blit(scaled, (0, TITLE_HEIGHT))

        field_y = TITLE_HEIGHT

        # Border around fractal
        pygame.draw.rect(self.screen, COL_HUD_BORDER, (0, field_y, WIN_W, WIN_H), 2)

        # Energy nodes
        for node in self.nodes:
            if node.alive:
                node.pulse += 0.08
                brightness = int(180 + 75 * math.sin(node.pulse))
                sx = int(node.gx * TILE + TILE / 2)
                sy = int(node.gy * TILE + TILE / 2) + field_y
                glow_surf = pygame.Surface((TILE * 8, TILE * 8), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (brightness, brightness, 0, 60), (TILE * 4, TILE * 4), TILE * 4)
                self.screen.blit(glow_surf, (sx - TILE * 4, sy - TILE * 4))
                pygame.draw.circle(self.screen, (brightness, brightness, 40), (sx, sy), 8)
                pygame.draw.circle(self.screen, (255, 255, 200), (sx, sy), 4)

        # Trail
        if len(self.trail) > 1:
            for i in range(1, len(self.trail)):
                alpha = i / len(self.trail)
                x1 = int(self.trail[i - 1][0] * TILE + TILE / 2)
                y1 = int(self.trail[i - 1][1] * TILE + TILE / 2) + field_y
                x2 = int(self.trail[i][0] * TILE + TILE / 2)
                y2 = int(self.trail[i][1] * TILE + TILE / 2) + field_y
                width = max(1, int(alpha * 3))
                col = (int(100 + 155 * alpha), int(200 + 55 * alpha), 255)
                pygame.draw.line(self.screen, col, (x1, y1), (x2, y2), width)

        # Player ship
        px = int(self.player_x * TILE + TILE / 2)
        py = int(self.player_y * TILE + TILE / 2) + field_y

        # Glow
        glow_surf = pygame.Surface((44, 44), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (80, 160, 255, 40), (22, 22), 20)
        pygame.draw.circle(glow_surf, (140, 210, 255, 70), (22, 22), 12)
        self.screen.blit(glow_surf, (px - 22, py - 22))

        # Ship triangle
        dx, dy = 0, 0
        if len(self.trail) >= 2:
            dx = self.trail[-1][0] - self.trail[-2][0]
            dy = self.trail[-1][1] - self.trail[-2][1]
        if abs(dx) < 0.01 and abs(dy) < 0.01:
            dx = 1

        angle = math.atan2(dy, dx)
        size = 8
        p1 = (px + int(math.cos(angle) * size), py + int(math.sin(angle) * size))
        p2 = (px + int(math.cos(angle + 2.5) * size * 0.6), py + int(math.sin(angle + 2.5) * size * 0.6))
        p3 = (px + int(math.cos(angle - 2.5) * size * 0.6), py + int(math.sin(angle - 2.5) * size * 0.6))
        pygame.draw.polygon(self.screen, COL_WHITE, [p1, p2, p3])
        pygame.draw.circle(self.screen, (200, 230, 255), (px, py), 2)

        # Dash ring
        if self.dash_timer > 0:
            ring = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(ring, (100, 200, 255, 120), (15, 15), 14, 2)
            self.screen.blit(ring, (px - 15, py - 15))

        # --- HUD ---
        hud_y = TITLE_HEIGHT + WIN_H
        pygame.draw.rect(self.screen, COL_HUD_BG, (0, hud_y, SCREEN_W, HUD_HEIGHT))
        pygame.draw.line(self.screen, COL_HUD_BORDER, (0, hud_y), (SCREEN_W, hud_y), 2)

        # Score
        score_text = self.font_med.render(f"SCORE: {self.score:,}", True, COL_SCORE)
        self.screen.blit(score_text, (12, hud_y + 14))

        # Energy bar
        bar_x = SCREEN_W // 2 - 80
        bar_w = 160
        bar_h = 16
        bar_y = hud_y + 16
        pygame.draw.rect(self.screen, COL_ENERGY_BG, (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2))
        energy_pct = self.energy / MAX_ENERGY
        if energy_pct > 0.5:
            bar_col = COL_ENERGY_HIGH
        elif energy_pct > 0.25:
            bar_col = COL_ENERGY_MED
        else:
            bar_col = COL_ENERGY_LOW
        pygame.draw.rect(self.screen, bar_col, (bar_x, bar_y, int(bar_w * energy_pct), bar_h))
        pygame.draw.rect(self.screen, COL_ENERGY_BORDER, (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2), 1)
        energy_label = self.font_small.render("ENERGY", True, COL_WHITE)
        self.screen.blit(energy_label, (bar_x + bar_w // 2 - energy_label.get_width() // 2, bar_y - 14))

        # Time
        minutes = int(self.time_alive) // 60
        seconds = int(self.time_alive) % 60
        time_text = self.font_med.render(f"TIME: {minutes:02d}:{seconds:02d}", True, COL_TIME)
        self.screen.blit(time_text, (SCREEN_W - time_text.get_width() - 12, hud_y + 14))

        # Game over
        if self.game_over:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            self.screen.blit(overlay, (0, 0))

            go_text = self.font_big.render("GAME OVER", True, COL_GAMEOVER)
            self.screen.blit(go_text, (SCREEN_W // 2 - go_text.get_width() // 2, SCREEN_H // 2 - 40))

            score_text = self.font_med.render(f"Final Score: {self.score:,}", True, COL_SCORE)
            self.screen.blit(score_text, (SCREEN_W // 2 - score_text.get_width() // 2, SCREEN_H // 2))

            time_text = self.font_med.render(f"Survived: {minutes:02d}:{seconds:02d}", True, COL_TIME)
            self.screen.blit(time_text, (SCREEN_W // 2 - time_text.get_width() // 2, SCREEN_H // 2 + 30))

            restart_text = self.font_small.render("Press R to restart", True, COL_WHITE)
            self.screen.blit(restart_text, (SCREEN_W // 2 - restart_text.get_width() // 2, SCREEN_H // 2 + 70))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            self.handle_input()
            self.update(dt)
            self.render()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
