# Fractal Surfer — Product Requirements Document (PRD)

## Overview

Fractal Surfer is a small arcade-style exploration game built in Python using pygame.

The game renders an evolving Julia set fractal field that the player navigates in real time.

The fractal acts as both the visual environment and the gameplay mechanic. Different fractal regions correspond to safe zones, energy zones, and chaotic hazards.

The fractal continuously evolves by animating the complex constant parameter c, creating an environment that never repeats and feels alive.

This project is designed as a case study for iterative AI-assisted development using a Ralph Loop workflow.

The game should remain small, understandable, and visually impressive enough to demonstrate live during a meetup or presentation.

---

## Goals

### Primary Goal

Create a visually captivating fractal-based arcade game where:

- the fractal evolves continuously
- the player explores an infinite mathematical landscape
- gameplay emerges from the fractal structure
- the system can be built incrementally using AI coding loops

The project should demonstrate how iterative prompting and rapid feedback can produce a working interactive system.

---

### Secondary Goals

The project should:

- run locally with minimal setup
- use a small and understandable codebase
- render smoothly at interactive frame rates
- demonstrate incremental AI-assisted development
- be suitable as a teaching example for developers

---

## Non-Goals

The following features are intentionally out of scope:

- deep fractal zoom exploration
- GPU-based rendering engines
- large-scale graphics frameworks
- multiplayer networking
- mobile device support
- advanced physics systems

The goal is clarity, speed of development, and visual impact.

---

## Target Audience

Primary audience:

- software engineers
- meetup participants
- developers interested in AI-assisted coding
- learners exploring procedural graphics

The project should be visually engaging enough to attract attention while remaining simple enough to understand quickly.

---

## Technology Stack

Language:

Python 3

Library:

pygame

Installation:

pip install pygame

Run command:

python fractal_surfer.py

The entire project should ideally run from a single Python file.

---

## Gameplay Overview

The screen displays a continuously evolving Julia set fractal field.

The player controls a small ship or cursor that moves across the fractal.

The fractal determines gameplay conditions:

- stable regions restore energy
- chaotic regions drain energy
- fractal boundaries offer high scoring potential

The goal is to survive as long as possible by navigating through favorable regions of the fractal field.

---

## Fractal System

### Fractal Type

Julia Set

Formula:

z(n+1) = z(n)^2 + c

Where:

- z is a complex number derived from the pixel coordinate
- c is a complex constant that changes slowly over time

Animating the parameter c causes the fractal to morph continuously.

Example animation:

c = complex(
    0.7885 * cos(time),
    0.7885 * sin(time)
)

This creates smooth evolving fractal patterns.

### Slow Zoom

The viewport slowly zooms into the fractal over time, revealing finer detail at deeper scales.

The zoom is implemented by gradually shrinking the complex-plane range visible on screen, while gently drifting the viewport center toward the player's position.

Parameters:

- zoom speed: ~0.3% smaller per second (barely perceptible frame-to-frame)
- viewport drift: very gentle (2% lerp per second toward player)
- minimum range: 0.05 (prevents floating-point precision issues at extreme depth)

The zoom creates a subtle sense of exploration and forward momentum without being disorienting. As the player zooms deeper, fractal structures become more intricate and fragmented, naturally increasing difficulty since safe zones become smaller and shift more rapidly.

A depth indicator in the title bar shows the current zoom level (e.g. "DEPTH: 3.2x").

---

## Rendering System

Resolution:

400 x 400 grid (vectorized with numpy)

Each grid cell represents a sample of the fractal.

Each frame:

1. Convert grid coordinate to complex plane coordinate
2. Run fractal iterations (approximately 20–30 iterations)
3. Determine escape speed
4. Convert escape value into color
5. draw pixel or tile

The grid is rendered at 800x800 pixels (TILE=2). Fractal computation is vectorized using numpy for interactive frame rates at high resolution.

---

## Visual Design

The fractal field should use a colorful gradient palette.

Suggested palette:

- deep blues for stable regions
- bright cyan and yellow for energy zones
- purple and red for chaotic areas

Color cycling over time is encouraged to increase visual motion.

The player should appear as a bright contrasting shape (white or neon).

---

## Player Mechanics

The player controls a small ship or cursor.

Movement:

- arrow keys or WASD move the player
- movement is continuous or tile-based

The player position is mapped into fractal coordinates.

---

## Energy System

The player has an energy meter.

Energy behavior:

- energy slowly drains over time
- entering stable fractal regions restores energy
- entering chaotic regions drains energy faster

If energy reaches zero, the player loses.

---

## Scoring System

Score increases based on survival and exploration.

Suggested scoring:

- time survived increases score
- staying near fractal boundaries grants bonus points
- collecting optional energy nodes increases score

---

## Difficulty Progression

Difficulty increases gradually through:

- faster fractal evolution
- increased energy drain
- reduced safe zones

This creates increasing pressure on the player.

---

## Game Loop

The game runs at approximately 60 FPS.

Each frame performs:

1. process keyboard input
2. update player position
3. update fractal animation parameter
4. compute fractal grid values
5. render fractal colors
6. evaluate terrain under player
7. update energy and score
8. check lose condition
9. render player and HUD

---

## Controls

Arrow Keys or WASD: move player

Space: optional dash or boost ability

Escape: quit game

R: restart game

---

## Lose Condition

The player loses when energy reaches zero.

This typically occurs when remaining too long in chaotic fractal regions.

---

## Win Condition

This is an endless survival game.

Success is measured by:

- total score
- time survived
- exploration distance

---

## File Structure

Example structure:

5-fractal-surfer-case-study/

PRD.md
README.md
fractal_surfer.py

The core implementation should remain small and easy to understand.

---

## Architecture

Suggested logical components:

Game
 ├─ Player
 ├─ FractalRenderer
 ├─ EnergySystem
 ├─ ScoreSystem
 └─ InputHandler

These may be implemented as simple classes or modules.

---

## Development Strategy

This project is intended to be developed incrementally using a Ralph Loop workflow.

Each iteration follows:

1. generate code
2. run the program
3. observe behavior
4. refine prompts
5. improve the implementation

---

## Suggested Development Phases

Phase 1  
Create game window and render a static fractal.

Phase 2  
Animate the fractal parameter.

Phase 3  
Add player movement.

Phase 4  
Sample fractal value under player.

Phase 5  
Add energy system.

Phase 6  
Add scoring system.

Phase 7  
Improve visuals and difficulty scaling.

Each phase should result in a playable program.

---

## Success Criteria

The project is successful if:

- the fractal renders smoothly
- the fractal evolves continuously
- the player can move across the fractal field
- energy mechanics work
- the game is playable and visually engaging
- the code can be built incrementally using AI assistance

---

## Future Enhancements

Possible optional improvements include:

- particle trails
- ~~fractal zoom exploration~~ (implemented — slow auto-zoom with viewport drift)
- enemy entities
- ~~power-ups~~ (implemented — energy nodes)
- sound effects
- leaderboard scoring

These features are not required for the initial case study.

---

## Case Study Purpose

This project exists primarily to demonstrate a practical example of building software using a Ralph Loop workflow.

It shows how:

- small prompts
- rapid feedback loops
- iterative improvement

can produce a visually compelling interactive program in a short period of time.

The emphasis is not on building a large game, but on demonstrating how AI-assisted development can accelerate creative software projects.
