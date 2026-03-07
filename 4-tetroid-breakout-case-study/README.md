# Tetroid Breakout

A Breakout + Tetris hybrid arcade game built with Python and pygame.

Tetromino pieces spawn and stack in the grid while you bounce a ball off a paddle to destroy them. Survive as long as possible before the blocks fill the screen.

## Requirements

- Python 3
- pygame

## Install

```bash
pip install pygame
```

## Run the Game

```bash
python3 tetroid_breakout.py
```

## Controls

| Key | Action |
|-----|--------|
| Left Arrow / A | Move paddle left |
| Right Arrow / D | Move paddle right |
| Space | Launch ball / Restart after game over |
| Escape | Quit |

## Run Tests

```bash
python3 -m unittest test_tetroid_breakout -v
```

## How It Works

- Tetromino pieces drop into the grid and stack from the bottom up
- Bounce the ball off your paddle to destroy blocks (10 points each)
- Complete rows clear automatically for a 100 point bonus
- The game speeds up as you level up (every 20 blocks destroyed)
- Game over when blocks fill the grid to the top
