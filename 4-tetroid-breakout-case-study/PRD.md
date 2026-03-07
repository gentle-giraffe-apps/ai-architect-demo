# Tetroid Breakout — Product Requirements Document (PRD)

## Overview

Tetroid Breakout is a small arcade-style game that combines elements of **Breakout** and **Tetris**.

The player controls a paddle at the bottom of the screen and bounces a ball upward to destroy blocks.  
Unlike traditional Breakout, the blocks appear as **Tetris tetromino pieces** that spawn from the top and gradually fill the playfield.

The objective is to **survive as long as possible by clearing blocks before the stack reaches the paddle area**.

This project is designed primarily as a **case study for iterative AI-assisted development using a Ralph Loop workflow**.

The game itself is intentionally simple so that it can be implemented in incremental steps and tested quickly.

---

# Goals

## Primary Goal

Create a **simple, playable Python arcade game** that demonstrates:

- iterative development
- small composable features
- fast test cycles

This supports a case study showing how a **Ralph Loop development workflow** can build non-trivial software through successive improvements.

## Secondary Goals

The project should also:

- be easy to run locally
- fit in a **single Python file**
- avoid complex dependencies
- demonstrate clear game architecture
- be understandable for beginner-to-intermediate developers

---

# Non-Goals

The following are intentionally **out of scope**:

- complex graphics
- full Tetris physics or rotation systems
- multiplayer
- mobile support
- advanced physics engines
- game engines such as Unity

This project prioritizes **clarity and iteration speed** over production-level polish.

---

# Target Audience

Primary audience:

- software developers
- meetup participants
- engineers learning AI-assisted workflows

The game is meant to be:

- simple to understand
- quick to demonstrate
- visually engaging enough for presentations

---

# Technology Stack

Language:

Python 3

Library:

pygame

Installation requirement:

```bash
pip install pygame
