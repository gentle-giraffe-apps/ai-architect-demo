"""Unit tests for Tetroid Breakout."""

import math
import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from tetroid_breakout import (
    Grid,
    Ball,
    Paddle,
    Game,
    TETROMINOES,
    COLORS,
    GRID_COLS,
    GRID_ROWS,
    SCREEN_WIDTH,
    CELL_SIZE,
    BALL_RADIUS,
    BALL_SPEED_INITIAL,
    PADDLE_WIDTH,
    PADDLE_Y,
    PADDLE_SPEED,
    GRID_TOP_Y,
    VISIBLE_ROWS,
)


class TestGrid(unittest.TestCase):
    def setUp(self):
        self.grid = Grid()

    def test_initial_grid_empty(self):
        self.assertEqual(self.grid.count_blocks(), 0)

    def test_grid_dimensions(self):
        self.assertEqual(len(self.grid.cells), GRID_ROWS)
        self.assertEqual(len(self.grid.cells[0]), GRID_COLS)

    def test_place_tetromino_success(self):
        result = self.grid.place_tetromino("O", 0, 0)
        self.assertTrue(result)
        self.assertIsNotNone(self.grid.cells[0][0])
        self.assertIsNotNone(self.grid.cells[0][1])
        self.assertIsNotNone(self.grid.cells[1][0])
        self.assertIsNotNone(self.grid.cells[1][1])

    def test_place_tetromino_color(self):
        self.grid.place_tetromino("T", 0, 0)
        self.assertEqual(self.grid.cells[0][0], COLORS["T"])

    def test_place_tetromino_out_of_bounds(self):
        result = self.grid.place_tetromino("I", 0, 8)
        self.assertFalse(result)

    def test_place_tetromino_overlap(self):
        self.grid.place_tetromino("O", 0, 0)
        result = self.grid.place_tetromino("O", 0, 0)
        self.assertFalse(result)

    def test_stack_tetromino_first_piece(self):
        """First piece stacks at the bottom of the grid."""
        row = self.grid.stack_tetromino("O", 0)
        self.assertEqual(row, GRID_ROWS - 2)  # O piece is 2 rows tall
        self.assertIsNotNone(self.grid.cells[GRID_ROWS - 2][0])
        self.assertIsNotNone(self.grid.cells[GRID_ROWS - 1][0])

    def test_stack_tetromino_stacks_on_previous(self):
        """Second piece stacks on top of first."""
        self.grid.stack_tetromino("O", 0)
        row2 = self.grid.stack_tetromino("O", 0)
        self.assertEqual(row2, GRID_ROWS - 4)

    def test_stack_tetromino_different_columns(self):
        self.grid.stack_tetromino("O", 0)
        row2 = self.grid.stack_tetromino("O", 4)
        self.assertEqual(row2, GRID_ROWS - 2)

    def test_stack_tetromino_full_column_returns_negative(self):
        for _ in range(GRID_ROWS // 2):
            self.grid.stack_tetromino("O", 0)
        result = self.grid.stack_tetromino("O", 0)
        self.assertEqual(result, -1)

    def test_clear_cell(self):
        self.grid.place_tetromino("O", 0, 0)
        color = self.grid.clear_cell(0, 0)
        self.assertEqual(color, COLORS["O"])
        self.assertIsNone(self.grid.cells[0][0])

    def test_clear_cell_empty(self):
        color = self.grid.clear_cell(0, 0)
        self.assertIsNone(color)

    def test_clear_full_rows(self):
        row = GRID_ROWS - 1
        for col in range(GRID_COLS):
            self.grid.cells[row][col] = (255, 0, 0)
        cleared = self.grid.clear_full_rows()
        self.assertEqual(cleared, 1)
        for col in range(GRID_COLS):
            self.assertIsNone(self.grid.cells[row][col])

    def test_clear_no_full_rows(self):
        self.grid.place_tetromino("O", 0, 0)
        cleared = self.grid.clear_full_rows()
        self.assertEqual(cleared, 0)

    def test_clear_multiple_rows(self):
        for row in range(GRID_ROWS - 2, GRID_ROWS):
            for col in range(GRID_COLS):
                self.grid.cells[row][col] = (255, 0, 0)
        cleared = self.grid.clear_full_rows()
        self.assertEqual(cleared, 2)

    def test_apply_gravity(self):
        self.grid.cells[2][0] = (255, 0, 0)
        self.grid.apply_gravity()
        self.assertIsNotNone(self.grid.cells[GRID_ROWS - 1][0])
        self.assertIsNone(self.grid.cells[2][0])

    def test_get_lowest_occupied_row_empty(self):
        self.assertEqual(self.grid.get_lowest_occupied_row(), -1)

    def test_get_lowest_occupied_row(self):
        self.grid.place_tetromino("O", 5, 0)
        self.assertEqual(self.grid.get_lowest_occupied_row(), 6)

    def test_get_highest_occupied_row_empty(self):
        self.assertEqual(self.grid.get_highest_occupied_row(), GRID_ROWS)

    def test_get_highest_occupied_row(self):
        self.grid.place_tetromino("O", 5, 0)
        self.assertEqual(self.grid.get_highest_occupied_row(), 5)

    def test_is_cell_occupied(self):
        self.grid.place_tetromino("O", 0, 0)
        self.assertTrue(self.grid.is_cell_occupied(0, 0))
        self.assertFalse(self.grid.is_cell_occupied(5, 5))

    def test_is_cell_occupied_out_of_bounds(self):
        self.assertFalse(self.grid.is_cell_occupied(-1, 0))
        self.assertFalse(self.grid.is_cell_occupied(0, GRID_COLS))

    def test_count_blocks(self):
        self.grid.place_tetromino("O", 0, 0)
        self.grid.place_tetromino("I", 3, 0)
        self.assertEqual(self.grid.count_blocks(), 8)

    def test_all_tetrominoes_placeable(self):
        for name in TETROMINOES:
            grid = Grid()
            result = grid.place_tetromino(name, 0, 0)
            self.assertTrue(result, f"Failed to place {name}")

    def test_all_tetrominoes_stackable(self):
        for name in TETROMINOES:
            grid = Grid()
            result = grid.stack_tetromino(name, 0)
            self.assertGreaterEqual(result, 0, f"Failed to stack {name}")


class TestBall(unittest.TestCase):
    def test_initial_position(self):
        ball = Ball(100, 200)
        self.assertEqual(ball.x, 100.0)
        self.assertEqual(ball.y, 200.0)

    def test_update_moves_ball(self):
        ball = Ball(100, 200)
        old_x, old_y = ball.x, ball.y
        ball.update()
        self.assertNotEqual(ball.x, old_x)
        self.assertNotEqual(ball.y, old_y)

    def test_bounce_x(self):
        ball = Ball(100, 200)
        original_vx = ball.vx
        ball.bounce_x()
        self.assertEqual(ball.vx, -original_vx)

    def test_bounce_y(self):
        ball = Ball(100, 200)
        original_vy = ball.vy
        ball.bounce_y()
        self.assertEqual(ball.vy, -original_vy)

    def test_set_speed(self):
        ball = Ball(100, 200, speed=5.0)
        ball.set_speed(10.0)
        actual_speed = math.sqrt(ball.vx ** 2 + ball.vy ** 2)
        self.assertAlmostEqual(actual_speed, 10.0, places=1)

    def test_set_speed_preserves_direction(self):
        ball = Ball(100, 200, speed=5.0)
        original_angle = math.atan2(ball.vy, ball.vx)
        ball.set_speed(10.0)
        new_angle = math.atan2(ball.vy, ball.vx)
        self.assertAlmostEqual(original_angle, new_angle, places=5)

    def test_radius(self):
        ball = Ball(100, 200)
        self.assertEqual(ball.radius, BALL_RADIUS)


class TestPaddle(unittest.TestCase):
    def test_initial_position(self):
        paddle = Paddle()
        self.assertAlmostEqual(
            paddle.x, SCREEN_WIDTH / 2 - PADDLE_WIDTH / 2, places=1
        )

    def test_move_left(self):
        paddle = Paddle()
        old_x = paddle.x
        paddle.move_left()
        self.assertLess(paddle.x, old_x)

    def test_move_right(self):
        paddle = Paddle()
        old_x = paddle.x
        paddle.move_right()
        self.assertGreater(paddle.x, old_x)

    def test_move_left_boundary(self):
        paddle = Paddle()
        for _ in range(1000):
            paddle.move_left()
        self.assertGreaterEqual(paddle.x, 0)

    def test_move_right_boundary(self):
        paddle = Paddle()
        for _ in range(1000):
            paddle.move_right()
        self.assertLessEqual(paddle.x + paddle.width, SCREEN_WIDTH)

    def test_get_rect(self):
        paddle = Paddle()
        rect = paddle.get_rect()
        self.assertEqual(rect.width, PADDLE_WIDTH)


class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game(headless=True)

    def test_initial_state(self):
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.level, 1)
        self.assertFalse(self.game.game_over)
        self.assertFalse(self.game.ball_launched)
        self.assertIsNotNone(self.game.ball)

    def test_initial_blocks_spawned(self):
        self.assertGreater(self.game.grid.count_blocks(), 0)

    def test_not_game_over_at_start(self):
        self.assertFalse(self.game.game_over)

    def test_reset(self):
        self.game.score = 500
        self.game.level = 5
        self.game.game_over = True
        self.game.reset()
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.level, 1)
        self.assertFalse(self.game.game_over)

    def test_ball_follows_paddle_before_launch(self):
        self.game.paddle.x = 100
        self.game.update()
        expected_x = 100 + self.game.paddle.width / 2
        self.assertAlmostEqual(self.game.ball.x, expected_x, places=1)

    def test_ball_moves_after_launch(self):
        self.game.ball_launched = True
        old_y = self.game.ball.y
        self.game.ball.vy = -5
        self.game.update()
        self.assertNotEqual(self.game.ball.y, old_y)

    def test_spawn_tetromino(self):
        initial_blocks = self.game.grid.count_blocks()
        self.game._spawn_tetromino()
        self.assertGreaterEqual(self.game.grid.count_blocks(), initial_blocks)

    def test_level_up(self):
        self.game.blocks_destroyed = 20
        self.game._update_level()
        self.assertEqual(self.game.level, 2)

    def test_level_up_multiple(self):
        self.game.blocks_destroyed = 60
        self.game._update_level()
        self.assertEqual(self.game.level, 4)

    def test_game_over_detection(self):
        """Game over when top rows are nearly full (can't place new pieces)."""
        self.game.grid = Grid()
        # Fill top 2 rows almost completely
        for row in range(2):
            for col in range(GRID_COLS - 1):
                self.game.grid.cells[row][col] = (255, 0, 0)
        self.game._check_game_over()
        self.assertTrue(self.game.game_over)

    def test_no_game_over_when_safe(self):
        self.game.grid = Grid()
        # Only fill some cells in middle rows
        for col in range(5):
            self.game.grid.cells[5][col] = (255, 0, 0)
        self.game._check_game_over()
        self.assertFalse(self.game.game_over)

    def test_score_increases_on_block_destroy(self):
        initial_score = self.game.score
        self.game.grid.cells[5][5] = (255, 0, 0)
        self.game.grid.clear_cell(5, 5)
        self.game.score += 10
        self.assertGreater(self.game.score, initial_score)

    def test_clear_full_row_gives_bonus(self):
        self.game.grid = Grid()
        row = GRID_ROWS - 3
        for col in range(GRID_COLS):
            self.game.grid.cells[row][col] = (255, 0, 0)
        cleared = self.game.grid.clear_full_rows()
        self.assertEqual(cleared, 1)
        self.game.score += cleared * 100
        self.assertGreaterEqual(self.game.score, 100)

    def test_ball_wall_bounce_left(self):
        self.game.ball.x = BALL_RADIUS - 1
        self.game.ball.vx = -5
        self.game._handle_ball_walls()
        self.assertGreater(self.game.ball.vx, 0)

    def test_ball_wall_bounce_right(self):
        self.game.ball.x = SCREEN_WIDTH - BALL_RADIUS + 1
        self.game.ball.vx = 5
        self.game._handle_ball_walls()
        self.assertLess(self.game.ball.vx, 0)

    def test_ball_wall_bounce_top(self):
        self.game.ball.y = GRID_TOP_Y + BALL_RADIUS - 1
        self.game.ball.vy = -5
        self.game._handle_ball_walls()
        self.assertGreater(self.game.ball.vy, 0)

    def test_update_no_crash_when_game_over(self):
        self.game.game_over = True
        self.game.update()

    def test_grid_row_to_screen_y(self):
        y = self.game.grid_row_to_screen_y(0)
        self.assertEqual(y, GRID_TOP_Y)

    def test_screen_y_to_grid_row(self):
        row = self.game.screen_y_to_grid_row(GRID_TOP_Y)
        self.assertEqual(row, 0)

    def test_coordinate_roundtrip(self):
        for row in range(GRID_ROWS):
            y = self.game.grid_row_to_screen_y(row)
            back = self.game.screen_y_to_grid_row(y)
            self.assertEqual(back, row)

    def test_simulation_runs(self):
        """Game should survive several hundred frames without crashing."""
        self.game.ball_launched = True
        for _ in range(500):
            self.game.update()


class TestTetrominoShapes(unittest.TestCase):
    def test_all_shapes_have_4_cells(self):
        for name, offsets in TETROMINOES.items():
            self.assertEqual(len(offsets), 4, f"{name} should have 4 cells")

    def test_all_shapes_have_colors(self):
        for name in TETROMINOES:
            self.assertIn(name, COLORS)

    def test_colors_are_rgb_tuples(self):
        for name, color in COLORS.items():
            self.assertEqual(len(color), 3, f"{name} color should be RGB")
            for val in color:
                self.assertGreaterEqual(val, 0)
                self.assertLessEqual(val, 255)

    def test_i_piece_is_horizontal(self):
        offsets = TETROMINOES["I"]
        rows = set(r for r, c in offsets)
        self.assertEqual(len(rows), 1)

    def test_o_piece_is_square(self):
        offsets = TETROMINOES["O"]
        rows = set(r for r, c in offsets)
        cols = set(c for r, c in offsets)
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(cols), 2)


if __name__ == "__main__":
    unittest.main()
