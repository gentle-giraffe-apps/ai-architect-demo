# Fractal Surfer

An arcade-style exploration game where you navigate a continuously evolving Julia set fractal field, built with Python, pygame, and numpy.

## Requirements

- Python 3
- pygame
- numpy

## Install

```bash
pip install pygame numpy
```

## Run the Game

```bash
python3 fractal_surfer.py
```

## Controls

| Key | Action |
|-----|--------|
| Arrow Keys / WASD | Move player |
| Space | Dash |
| R | Restart |
| Escape | Quit |

## Run Tests

```bash
pytest test_fractal_surfer.py -v
```

## How It Works

- A Julia set fractal field renders and evolves continuously by animating the complex constant parameter `c`
- The viewport slowly zooms in, revealing finer fractal detail over time
- Stable fractal regions (blue) restore energy; chaotic regions (red/purple) drain it
- Navigate the fractal boundary for bonus points
- Collect energy nodes to replenish your energy
- Survive as long as possible — the game ends when energy reaches zero
