"""Tetroid Breakout - A Breakout + Tetris hybrid arcade game."""

import pygame
import random
import sys
import math

# --- Constants ---
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRID_COLS = 10
CELL_SIZE = SCREEN_WIDTH // GRID_COLS  # 40
GRID_TOP_Y = 40  # offset from top for title area
PADDLE_AREA_HEIGHT = 130  # space for paddle + ball + score
GRID_BOTTOM_Y = SCREEN_HEIGHT - PADDLE_AREA_HEIGHT  # 520
VISIBLE_ROWS = (GRID_BOTTOM_Y - GRID_TOP_Y) // CELL_SIZE  # 12
GRID_ROWS = VISIBLE_ROWS  # grid matches visible area

PADDLE_WIDTH = 80
PADDLE_HEIGHT = 10
PADDLE_Y = SCREEN_HEIGHT - 50  # 550
PADDLE_SPEED = 8

BALL_RADIUS = 6
BALL_SPEED_INITIAL = 5.0
BALL_SPEED_MAX = 9.0

FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRID_LINE_COLOR = (50, 50, 50)

# Tetromino colors
COLORS = {
    "I": (0, 240, 240),    # cyan
    "O": (240, 240, 0),    # yellow
    "T": (160, 0, 240),    # purple
    "S": (0, 240, 0),      # green
    "Z": (240, 0, 0),      # red
    "L": (240, 160, 0),    # orange
    "J": (0, 0, 240),      # blue
}

# Tetromino shapes (row, col offsets)
TETROMINOES = {
    "I": [(0, 0), (0, 1), (0, 2), (0, 3)],
    "O": [(0, 0), (0, 1), (1, 0), (1, 1)],
    "T": [(0, 0), (0, 1), (0, 2), (1, 1)],
    "S": [(0, 1), (0, 2), (1, 0), (1, 1)],
    "Z": [(0, 0), (0, 1), (1, 1), (1, 2)],
    "L": [(0, 0), (0, 1), (0, 2), (1, 0)],
    "J": [(0, 0), (0, 1), (0, 2), (1, 2)],
}

# Spawn timing (frames)
SPAWN_INTERVAL_INITIAL = 300  # 5 seconds at 60fps
SPAWN_INTERVAL_MIN = 90       # 1.5 seconds minimum

# Falling piece speed (frames per row drop)
FALL_SPEED_INITIAL = 8  # drops one row every 8 frames
FALL_SPEED_MIN = 3



class Grid:
    """Manages the grid of blocks."""

    def __init__(self, cols=GRID_COLS, rows=GRID_ROWS):
        self.cols = cols
        self.rows = rows
        self.cells = [[None for _ in range(cols)] for _ in range(rows)]

    def place_tetromino(self, shape_name, top_row, left_col):
        """Place a tetromino at a specific position. Returns True if successful."""
        offsets = TETROMINOES[shape_name]
        color = COLORS[shape_name]

        for dr, dc in offsets:
            r = top_row + dr
            c = left_col + dc
            if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
                return False
            if self.cells[r][c] is not None:
                return False

        for dr, dc in offsets:
            self.cells[top_row + dr][left_col + dc] = color
        return True

    def stack_tetromino(self, shape_name, left_col):
        """Place a tetromino at the lowest available position from the top.
        Pieces accumulate from the top of the grid downward.
        Returns the top_row placed at, or -1 if can't place."""
        offsets = TETROMINOES[shape_name]
        max_dr = max(dr for dr, dc in offsets)

        # Find the lowest valid row (highest row index) where piece fits
        best_row = -1
        for top_row in range(self.rows - max_dr):
            valid = True
            for dr, dc in offsets:
                r = top_row + dr
                c = left_col + dc
                if c < 0 or c >= self.cols:
                    valid = False
                    break
                if self.cells[r][c] is not None:
                    valid = False
                    break
            if valid:
                best_row = top_row
            else:
                break  # Can't go lower, use previous valid row

        if best_row >= 0:
            color = COLORS[shape_name]
            for dr, dc in offsets:
                self.cells[best_row + dr][left_col + dc] = color
        return best_row

    def clear_cell(self, row, col):
        color = self.cells[row][col]
        self.cells[row][col] = None
        return color

    def clear_full_rows(self):
        """Clear filled rows. Shifts blocks ABOVE down to fill gaps."""
        cleared = 0
        new_cells = []
        for row in range(self.rows):
            if all(cell is not None for cell in self.cells[row]):
                cleared += 1
            else:
                new_cells.append(self.cells[row])
        # Add empty rows at top (blocks shift down)
        for _ in range(cleared):
            new_cells.insert(0, [None for _ in range(self.cols)])
        self.cells = new_cells
        return cleared

    def apply_gravity(self):
        """Drop floating blocks down to fill gaps below them."""
        for col in range(self.cols):
            non_empty = []
            for row in range(self.rows - 1, -1, -1):
                if self.cells[row][col] is not None:
                    non_empty.append(self.cells[row][col])
            for row in range(self.rows - 1, -1, -1):
                if non_empty:
                    self.cells[row][col] = non_empty.pop(0)
                else:
                    self.cells[row][col] = None

    def get_lowest_occupied_row(self):
        """Bottom-most row index with any blocks, or -1 if empty."""
        for r in range(self.rows - 1, -1, -1):
            for c in range(self.cols):
                if self.cells[r][c] is not None:
                    return r
        return -1

    def get_highest_occupied_row(self):
        """Topmost row index with any blocks, or rows if empty."""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.cells[r][c] is not None:
                    return r
        return self.rows

    def is_cell_occupied(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.cells[row][col] is not None
        return False

    def count_blocks(self):
        count = 0
        for row in self.cells:
            for cell in row:
                if cell is not None:
                    count += 1
        return count


class FallingPiece:
    """A tetromino that falls from the top of the grid."""

    def __init__(self, shape_name, target_col, grid):
        self.shape_name = shape_name
        self.color = COLORS[shape_name]
        self.offsets = TETROMINOES[shape_name]
        self.col = target_col
        self.row = -max(dr for dr, dc in self.offsets)  # start above grid
        self.fall_timer = 0
        self.fall_speed = FALL_SPEED_INITIAL
        self.landed = False
        self.grid = grid

    def can_move_to(self, row, col):
        """Check if piece can occupy the given position."""
        for dr, dc in self.offsets:
            r = row + dr
            c = col + dc
            if c < 0 or c >= self.grid.cols:
                return False
            if r >= self.grid.rows:
                return False
            if r >= 0 and self.grid.cells[r][c] is not None:
                return False
        return True

    def update(self):
        """Advance the falling piece. Returns True when it locks in place."""
        if self.landed:
            return True

        self.fall_timer += 1
        if self.fall_timer >= self.fall_speed:
            self.fall_timer = 0
            if self.can_move_to(self.row + 1, self.col):
                self.row += 1
            else:
                self._lock()
                return True
        return False

    def _lock(self):
        """Lock the piece into the grid."""
        self.landed = True
        for dr, dc in self.offsets:
            r = self.row + dr
            c = self.col + dc
            if 0 <= r < self.grid.rows and 0 <= c < self.grid.cols:
                self.grid.cells[r][c] = self.color

    def get_cells(self):
        """Return list of (row, col) positions for drawing."""
        return [(self.row + dr, self.col + dc) for dr, dc in self.offsets]


class Ball:
    def __init__(self, x, y, speed=BALL_SPEED_INITIAL):
        self.x = float(x)
        self.y = float(y)
        self.speed = speed
        angle = random.uniform(-math.pi / 3, -2 * math.pi / 3)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.radius = BALL_RADIUS
        self.active = True

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def bounce_x(self):
        self.vx = -self.vx

    def bounce_y(self):
        self.vy = -self.vy

    def set_speed(self, new_speed):
        current_speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if current_speed > 0:
            factor = new_speed / current_speed
            self.vx *= factor
            self.vy *= factor
            self.speed = new_speed


class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = SCREEN_WIDTH / 2 - self.width / 2
        self.y = PADDLE_Y
        self.speed = PADDLE_SPEED

    def move_left(self):
        self.x = max(0, self.x - self.speed)

    def move_right(self):
        self.x = min(SCREEN_WIDTH - self.width, self.x + self.speed)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Game:
    def __init__(self, headless=False):
        self.headless = headless
        self.grid = Grid()
        self.paddle = Paddle()
        self.ball = None
        self.score = 0
        self.level = 1
        self.game_over = False
        self.ball_launched = False
        self.spawn_timer = 0
        self.spawn_interval = SPAWN_INTERVAL_INITIAL
        self.blocks_destroyed = 0
        self.level_threshold = 20

        if not headless:
            pygame.init()
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Tetroid Breakout")
            self.clock = pygame.time.Clock()
            self.font_small = pygame.font.SysFont("arial", 16)
            self.font_medium = pygame.font.SysFont("arial", 24, bold=True)
            self.font_large = pygame.font.SysFont("arial", 40, bold=True)
            self.font_title = pygame.font.SysFont("arial", 28, bold=True)

        self.reset()

    def reset(self):
        self.grid = Grid()
        self.paddle = Paddle()
        self.score = 0
        self.level = 1
        self.game_over = False
        self.ball_launched = False
        self.spawn_timer = 0
        self.spawn_interval = SPAWN_INTERVAL_INITIAL
        self.blocks_destroyed = 0
        self.falling_pieces = []  # active falling tetrominoes
        self.fall_speed = FALL_SPEED_INITIAL
        self._spawn_ball()
        # Spawn initial tetrominoes
        for _ in range(3):
            self._spawn_tetromino()

    def _spawn_ball(self):
        self.ball = Ball(
            self.paddle.x + self.paddle.width / 2,
            self.paddle.y - BALL_RADIUS - 2,
        )
        self.ball.vy = -abs(self.ball.vy)
        self.ball_launched = False

    def _spawn_tetromino(self):
        """Spawn a falling tetromino from the top of the grid."""
        shape_name = random.choice(list(TETROMINOES.keys()))
        offsets = TETROMINOES[shape_name]
        max_col = max(dc for _, dc in offsets)
        left_col = random.randint(0, self.grid.cols - max_col - 1)
        piece = FallingPiece(shape_name, left_col, self.grid)
        piece.fall_speed = self.fall_speed
        self.falling_pieces.append(piece)
        return True

    def grid_row_to_screen_y(self, grid_row):
        return GRID_TOP_Y + grid_row * CELL_SIZE

    def screen_y_to_grid_row(self, screen_y):
        return int((screen_y - GRID_TOP_Y) // CELL_SIZE)

    def _handle_ball_block_collision(self):
        ball_grid_row = self.screen_y_to_grid_row(self.ball.y)
        ball_grid_col = int(self.ball.x // CELL_SIZE)

        hit = False
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                r = ball_grid_row + dr
                c = ball_grid_col + dc
                if 0 <= r < self.grid.rows and 0 <= c < self.grid.cols:
                    if self.grid.cells[r][c] is not None:
                        cell_screen_y = self.grid_row_to_screen_y(r)
                        cell_screen_x = c * CELL_SIZE
                        cell_rect = pygame.Rect(
                            cell_screen_x, cell_screen_y, CELL_SIZE, CELL_SIZE
                        )
                        ball_rect = pygame.Rect(
                            self.ball.x - self.ball.radius,
                            self.ball.y - self.ball.radius,
                            self.ball.radius * 2,
                            self.ball.radius * 2,
                        )
                        if ball_rect.colliderect(cell_rect):
                            self.grid.clear_cell(r, c)
                            self.score += 10
                            self.blocks_destroyed += 1
                            hit = True

        if hit:
            self.ball.bounce_y()

    def _handle_ball_paddle_collision(self):
        paddle_rect = self.paddle.get_rect()
        ball_rect = pygame.Rect(
            self.ball.x - self.ball.radius,
            self.ball.y - self.ball.radius,
            self.ball.radius * 2,
            self.ball.radius * 2,
        )

        if ball_rect.colliderect(paddle_rect) and self.ball.vy > 0:
            hit_pos = (self.ball.x - self.paddle.x) / self.paddle.width
            hit_pos = max(0.0, min(1.0, hit_pos))
            angle = math.pi + (hit_pos - 0.5) * (math.pi / 3)
            self.ball.vx = math.cos(angle) * self.ball.speed
            self.ball.vy = -abs(math.sin(angle) * self.ball.speed)

    def _handle_ball_walls(self):
        if self.ball.x - self.ball.radius <= 0:
            self.ball.x = self.ball.radius
            self.ball.bounce_x()
        if self.ball.x + self.ball.radius >= SCREEN_WIDTH:
            self.ball.x = SCREEN_WIDTH - self.ball.radius
            self.ball.bounce_x()
        if self.ball.y - self.ball.radius <= GRID_TOP_Y:
            self.ball.y = GRID_TOP_Y + self.ball.radius
            self.ball.bounce_y()

    def _check_ball_lost(self):
        if self.ball.y + self.ball.radius > SCREEN_HEIGHT:
            self._spawn_ball()

    def _check_game_over(self):
        """Game over if blocks fill the grid so no new pieces can spawn (top rows full)."""
        # Check if the top 2 rows are blocked - can't place new pieces
        for row in range(2):
            occupied = sum(1 for c in range(self.grid.cols) if self.grid.cells[row][c] is not None)
            if occupied >= self.grid.cols - 1:
                self.game_over = True
                return

    def _update_level(self):
        new_level = (self.blocks_destroyed // self.level_threshold) + 1
        if new_level > self.level:
            self.level = new_level
            new_speed = min(
                BALL_SPEED_INITIAL + (self.level - 1) * 0.5, BALL_SPEED_MAX
            )
            self.ball.set_speed(new_speed)
            self.spawn_interval = max(
                SPAWN_INTERVAL_MIN,
                SPAWN_INTERVAL_INITIAL - (self.level - 1) * 30,
            )
            self.fall_speed = max(
                FALL_SPEED_MIN,
                FALL_SPEED_INITIAL - (self.level - 1),
            )

    def update(self):
        if self.game_over:
            return

        if not self.ball_launched:
            self.ball.x = self.paddle.x + self.paddle.width / 2
            self.ball.y = self.paddle.y - BALL_RADIUS - 2
            return

        self.ball.update()

        self._handle_ball_walls()
        self._handle_ball_paddle_collision()
        self._handle_ball_block_collision()
        self._check_ball_lost()

        rows_cleared = self.grid.clear_full_rows()
        if rows_cleared > 0:
            self.score += rows_cleared * 100

        # Update falling pieces
        self.falling_pieces = [p for p in self.falling_pieces if not p.landed]
        for piece in self.falling_pieces:
            piece.update()

        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self._spawn_tetromino()

        self._check_game_over()
        self._update_level()

    def handle_input(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle.move_right()
        if keys[pygame.K_SPACE] and not self.ball_launched:
            self.ball_launched = True

    def draw(self):
        if self.headless:
            return

        self.screen.fill(BLACK)

        # Grid lines
        for col in range(self.grid.cols + 1):
            x = col * CELL_SIZE
            pygame.draw.line(
                self.screen, GRID_LINE_COLOR, (x, GRID_TOP_Y), (x, GRID_BOTTOM_Y)
            )
        for row_idx in range(VISIBLE_ROWS + 1):
            y = GRID_TOP_Y + row_idx * CELL_SIZE
            pygame.draw.line(
                self.screen, GRID_LINE_COLOR, (0, y), (SCREEN_WIDTH, y)
            )

        # Blocks
        for grid_row in range(self.grid.rows):
            for col in range(self.grid.cols):
                color = self.grid.cells[grid_row][col]
                if color is not None:
                    x = col * CELL_SIZE
                    y = GRID_TOP_Y + grid_row * CELL_SIZE
                    pygame.draw.rect(
                        self.screen, color,
                        (x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)
                    )
                    highlight = tuple(min(255, c + 40) for c in color)
                    pygame.draw.line(
                        self.screen, highlight,
                        (x + 1, y + 1), (x + CELL_SIZE - 2, y + 1)
                    )
                    pygame.draw.line(
                        self.screen, highlight,
                        (x + 1, y + 1), (x + 1, y + CELL_SIZE - 2)
                    )

        # Falling pieces
        for piece in self.falling_pieces:
            for row, col in piece.get_cells():
                if 0 <= row < self.grid.rows and 0 <= col < self.grid.cols:
                    x = col * CELL_SIZE
                    y = GRID_TOP_Y + row * CELL_SIZE
                    pygame.draw.rect(
                        self.screen, piece.color,
                        (x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)
                    )
                    highlight = tuple(min(255, c + 40) for c in piece.color)
                    pygame.draw.line(
                        self.screen, highlight,
                        (x + 1, y + 1), (x + CELL_SIZE - 2, y + 1)
                    )
                    pygame.draw.line(
                        self.screen, highlight,
                        (x + 1, y + 1), (x + 1, y + CELL_SIZE - 2)
                    )

        # Paddle
        pygame.draw.rect(
            self.screen, WHITE,
            (self.paddle.x, self.paddle.y, self.paddle.width, self.paddle.height),
            border_radius=3,
        )

        # Ball
        pygame.draw.circle(
            self.screen, WHITE,
            (int(self.ball.x), int(self.ball.y)),
            self.ball.radius,
        )

        # Score bar
        score_text = self.font_small.render(f"SCORE: {self.score}", True, WHITE)
        level_text = self.font_small.render(f"LEVEL: {self.level}", True, WHITE)
        self.screen.blit(score_text, (10, SCREEN_HEIGHT - 30))
        self.screen.blit(level_text, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 30))

        # Title
        title_text = self.font_title.render("TETROID", True, (240, 0, 0))
        subtitle_text = self.font_small.render("BREAKOUT", True, (240, 160, 0))
        self.screen.blit(title_text, (10, 5))
        self.screen.blit(subtitle_text, (12, 28))

        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        go_text = self.font_large.render("GAME OVER", True, (240, 0, 0))
        go_rect = go_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40))
        self.screen.blit(go_text, go_rect)

        score_text = self.font_medium.render(
            f"FINAL SCORE: {self.score}", True, WHITE
        )
        score_rect = score_text.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 10)
        )
        self.screen.blit(score_text, score_rect)

        restart_text = self.font_small.render(
            "PRESS SPACE TO RESTART", True, WHITE
        )
        restart_rect = restart_text.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)
        )
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        if self.headless:
            return

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_SPACE and self.game_over:
                        self.reset()

            if not self.game_over:
                keys = pygame.key.get_pressed()
                self.handle_input(keys)

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
