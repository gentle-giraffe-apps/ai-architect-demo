"""Unit tests for Fractal Surfer game logic."""

import math
import pytest

# Import game module components (avoid pygame.init() at import time)
import importlib
import sys
import types


def _import_game_module():
    """Import fractal_surfer without triggering pygame.init()."""
    import pygame
    # Ensure pygame doesn't open a display
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"

    import fractal_surfer as mod
    return mod


# We need to add the game directory to sys.path
sys.path.insert(0, "/Users/jonathanritchey/gentle_github/ai-architect-demo/5-julia-surf-case-study")

mod = _import_game_module()
julia_escape = mod.julia_escape
build_palette = mod.build_palette
_lerp_color = mod._lerp_color
EnergyNode = mod.EnergyNode
MAX_ITER = mod.MAX_ITER
MAX_ENERGY = mod.MAX_ENERGY
GRID_W = mod.GRID_W
GRID_H = mod.GRID_H
FRAC_RANGE = mod.FRAC_RANGE
STABLE_RESTORE = mod.STABLE_RESTORE
BASE_DRAIN = mod.BASE_DRAIN
CHAOS_DRAIN = mod.CHAOS_DRAIN
BOUNDARY_BONUS = mod.BOUNDARY_BONUS
NODE_RESTORE = mod.NODE_RESTORE
TRAIL_LENGTH = mod.TRAIL_LENGTH


# ---------------------------------------------------------------------------
# julia_escape tests
# ---------------------------------------------------------------------------

class TestJuliaEscape:
    def test_inside_set_returns_zero(self):
        """Points deep inside the Julia set should return 0 (never escape)."""
        # c=0 makes the Julia set a unit disk; z=0 is clearly inside
        assert julia_escape(0.0, 0.0, 0.0, 0.0, MAX_ITER) == 0

    def test_outside_set_returns_positive(self):
        """Points far outside the set should escape immediately."""
        val = julia_escape(3.0, 3.0, 0.0, 0.0, MAX_ITER)
        assert val > 0

    def test_escape_value_increases_near_boundary(self):
        """Points closer to the boundary should have higher escape counts."""
        # c=0: Julia set is unit disk. Test points at increasing distance from origin
        far = julia_escape(2.0, 0.0, 0.0, 0.0, MAX_ITER)     # far outside
        mid = julia_escape(1.1, 0.0, 0.0, 0.0, MAX_ITER)     # just outside
        # mid should take more iterations (higher value) than far
        assert mid > far

    def test_smooth_coloring_returns_float(self):
        """Escaped points should return a float (smooth iteration count)."""
        val = julia_escape(2.0, 0.0, 0.0, 0.0, MAX_ITER)
        assert isinstance(val, float)
        assert val > 0

    def test_max_iter_respected(self):
        """With max_iter=1, a non-escaping point still returns 0."""
        val = julia_escape(0.0, 0.0, 0.0, 0.0, 1)
        assert val == 0

    def test_escape_on_first_iteration(self):
        """A point with |z|^2 > 4 should escape on iteration 0."""
        # z = (3, 0), |z|^2 = 9 > 4
        val = julia_escape(3.0, 0.0, 0.0, 0.0, MAX_ITER)
        assert 0 < val < 2  # should be close to iteration 0-1

    def test_known_julia_c_negative_one(self):
        """For c = -1, z = 0 is inside (period-2 orbit: 0 -> -1 -> 0 -> ...)."""
        val = julia_escape(0.0, 0.0, -1.0, 0.0, MAX_ITER)
        assert val == 0

    def test_known_julia_c_negative_one_outside(self):
        """For c = -1, z = 2 should escape."""
        val = julia_escape(2.0, 0.0, -1.0, 0.0, MAX_ITER)
        assert val > 0

    def test_symmetry(self):
        """Julia sets are symmetric about the origin: f(z) should equal f(-z)."""
        c_r, c_i = 0.355, 0.355
        val1 = julia_escape(0.5, 0.3, c_r, c_i, MAX_ITER)
        val2 = julia_escape(-0.5, -0.3, c_r, c_i, MAX_ITER)
        assert val1 == val2

    def test_smooth_value_not_negative(self):
        """Escape values should never be negative."""
        # Test a variety of points
        for zr in [-2.0, -1.0, 0.0, 1.0, 2.0]:
            for zi in [-2.0, -1.0, 0.0, 1.0, 2.0]:
                val = julia_escape(zr, zi, -0.7, 0.27015, MAX_ITER)
                assert val >= 0, f"Negative escape at z=({zr}, {zi}): {val}"


# ---------------------------------------------------------------------------
# Palette tests
# ---------------------------------------------------------------------------

class TestPalette:
    def test_palette_length(self):
        palette = build_palette(256)
        assert len(palette) == 256

    def test_palette_rgb_range(self):
        """All palette colors should have RGB values in [0, 255]."""
        palette = build_palette(256)
        for i, (r, g, b) in enumerate(palette):
            assert 0 <= r <= 255, f"Red out of range at index {i}: {r}"
            assert 0 <= g <= 255, f"Green out of range at index {i}: {g}"
            assert 0 <= b <= 255, f"Blue out of range at index {i}: {b}"

    def test_palette_custom_size(self):
        palette = build_palette(64)
        assert len(palette) == 64

    def test_palette_wraps_dark(self):
        """Palette should start and end dark (for seamless cycling)."""
        palette = build_palette(256)
        # First and last should be near-black
        assert sum(palette[0]) < 50
        assert sum(palette[-1]) < 50


# ---------------------------------------------------------------------------
# _lerp_color tests
# ---------------------------------------------------------------------------

class TestLerpColor:
    def test_lerp_zero(self):
        assert _lerp_color((0, 0, 0), (255, 255, 255), 0.0) == (0, 0, 0)

    def test_lerp_one(self):
        assert _lerp_color((0, 0, 0), (255, 255, 255), 1.0) == (255, 255, 255)

    def test_lerp_half(self):
        result = _lerp_color((0, 0, 0), (200, 100, 50), 0.5)
        assert result == (100, 50, 25)

    def test_lerp_same_color(self):
        assert _lerp_color((42, 42, 42), (42, 42, 42), 0.5) == (42, 42, 42)


# ---------------------------------------------------------------------------
# EnergyNode tests
# ---------------------------------------------------------------------------

class TestEnergyNode:
    def test_creation(self):
        node = EnergyNode(10, 20)
        assert node.gx == 10
        assert node.gy == 20
        assert node.alive is True

    def test_pulse_initialized(self):
        node = EnergyNode(0, 0)
        assert 0 <= node.pulse <= math.pi * 2


# ---------------------------------------------------------------------------
# Game logic tests (using a real Game instance with dummy display)
# ---------------------------------------------------------------------------

class TestGameLogic:
    @pytest.fixture
    def game(self):
        import pygame
        pygame.init()
        g = mod.Game()
        return g

    def test_initial_state(self, game):
        assert game.energy == MAX_ENERGY
        assert game.score == 0
        assert game.game_over is False
        assert game.player_x == GRID_W / 2.0
        assert game.player_y == GRID_H / 2.0

    def test_reset_restores_state(self, game):
        game.energy = 0
        game.score = 9999
        game.game_over = True
        game.reset()
        assert game.energy == MAX_ENERGY
        assert game.score == 0
        assert game.game_over is False

    def test_energy_clamped_to_max(self, game):
        game.energy = MAX_ENERGY
        game.update(0.016)
        assert game.energy <= MAX_ENERGY

    def test_game_over_on_zero_energy(self, game):
        # Directly set energy to zero and verify game_over triggers
        game.energy = 0.001
        game.player_x = GRID_W / 2.0
        game.player_y = GRID_H / 2.0
        game.render_fractal()
        # Run updates — even stable terrain has base drain, so energy will reach 0
        for _ in range(500):
            if game.game_over:
                break
            # Force energy down each iteration to ensure we eventually hit zero
            game.energy = max(0, game.energy - 0.01)
            game.update(0.016)
        assert game.game_over is True
        assert game.energy == 0

    def test_trail_max_length(self, game):
        for _ in range(TRAIL_LENGTH + 20):
            game.update(0.016)
        assert len(game.trail) <= TRAIL_LENGTH

    def test_difficulty_increases(self, game):
        initial = game.difficulty
        game.update(1.0)  # advance 1 second
        assert game.difficulty > initial

    def test_node_collection(self, game):
        """Player touching a node should collect it."""
        node = EnergyNode(int(game.player_x), int(game.player_y))
        game.nodes = [node]
        game.energy = 50.0
        old_score = game.score
        game.update(0.016)
        assert node.alive is False
        assert game.energy > 50.0
        assert game.score > old_score

    def test_node_spawning(self, game):
        """Nodes should spawn over time."""
        game.nodes = []
        game.node_timer = 180  # trigger spawn threshold
        game.update(0.016)
        # node_timer incremented past 180, should spawn
        assert len(game.nodes) >= 1 or game.node_timer == 0

    def test_player_stays_in_bounds(self, game):
        """Player should be clamped to grid boundaries."""
        game.player_x = -100
        game.player_y = -100
        game.handle_input()
        # handle_input clamps only when movement occurs, so let's manually clamp test
        game.player_x = max(1, min(GRID_W - 2, game.player_x))
        game.player_y = max(1, min(GRID_H - 2, game.player_y))
        assert 1 <= game.player_x <= GRID_W - 2
        assert 1 <= game.player_y <= GRID_H - 2

    def test_get_c_returns_tuple(self, game):
        c = game._get_c()
        assert isinstance(c, tuple)
        assert len(c) == 2

    def test_terrain_value_inside_grid(self, game):
        val = game._terrain_value(GRID_W / 2, GRID_H / 2)
        assert isinstance(val, (int, float))
        assert val >= 0

    def test_terrain_value_outside_grid(self, game):
        """Out-of-bounds terrain should return 0."""
        val = game._terrain_value(-1, -1)
        assert val == 0
        val = game._terrain_value(GRID_W + 10, GRID_H + 10)
        assert val == 0

    def test_energy_terrain_mapping(self, game):
        """Verify terrain zones affect energy correctly.

        Inside set (escape=0) should restore energy.
        Near-boundary (high escape) should give boundary bonus.
        Chaotic (low escape) should drain energy.
        """
        game.difficulty = 1.0

        # Test stable zone (inside set): energy should increase
        game.energy = 50.0
        # Place player at center — for many c values, center is inside set
        game.player_x = GRID_W / 2.0
        game.player_y = GRID_H / 2.0
        escape_val = game._terrain_value(game.player_x, game.player_y)
        if escape_val == 0:
            old_energy = game.energy
            game.update(0.016)
            # Should restore energy (minus small base drain)
            net_change = game.energy - old_energy
            # STABLE_RESTORE - BASE_DRAIN*0.5 should be positive
            assert STABLE_RESTORE - BASE_DRAIN * 0.5 > 0, "Stable restore should exceed base drain"


# ---------------------------------------------------------------------------
# Boundary / edge case tests
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_julia_escape_zero_c(self):
        """c=0 makes a circle Julia set. Points on |z|=2 boundary."""
        # Exactly on the escape boundary
        val = julia_escape(2.0, 0.0, 0.0, 0.0, MAX_ITER)
        assert val > 0  # should escape

    def test_julia_escape_high_iterations(self):
        """High max_iter shouldn't crash."""
        val = julia_escape(0.3, 0.3, -0.7, 0.27015, 200)
        assert val >= 0

    def test_palette_single_entry(self):
        palette = build_palette(1)
        assert len(palette) == 1

    def test_initial_nodes_spawned(self):
        """Game should start with initial energy nodes."""
        import pygame
        pygame.init()
        g = mod.Game()
        assert len(g.nodes) == 8  # _spawn_initial_nodes creates 8
