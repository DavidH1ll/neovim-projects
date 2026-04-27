# Flappy Bird Clone

A faithful clone of the classic Flappy Bird game built with Pygame.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.5+-green)

## Features

- **Classic Gameplay** — Tap to flap, avoid pipes, don't hit the ground
- **Smooth Animations** — Bird flapping animation, scrolling background and ground
- **Score System** — Earn points by passing through pipes
- **High Score Tracking** — Best score persists during the session
- **Medal System** — Bronze (1+), Silver (5+), Gold (10+)
- **Pixel-Perfect Collision** — Uses Pygame masks for accurate collision detection
- **Sound Effects** — Wing flap, scoring, hit, and death sounds
- **Three Game States** — Get Ready, Playing, Game Over
- **Mouse & Keyboard Support** — Click, Space, or Up arrow to play

## Controls

| Input | Action |
|-------|--------|
| `Space` / `Up Arrow` | Flap / Start game / Restart |
| `Left Click` | Flap / Start game / Restart |
| `R` | Restart (on game over) |
| `Escape` | Quit |

## Quick Start

### 1. Install Dependencies

```bash
cd "flappy bird"
pip install -r requirements.txt
```

### 2. Run the Game

```bash
python3 flappy_bird.py
```

## Assets

This game uses the [flappy-bird-assets](https://github.com/samuelcust/flappy-bird-assets) by [Samuel Custodio](https://github.com/samuelcust), licensed under MIT.

### Sprites Used

| Asset | Purpose |
|-------|---------|
| `yellowbird-*.png` | Bird animation frames (3 states) |
| `pipe-green.png` | Obstacle pipes |
| `background-day.png` | Parallax background |
| `base.png` | Scrolling ground |
| `message.png` | "Get Ready" start screen |
| `gameover.png` | Game over banner |
| `0-9.png` | Score number sprites |

### Audio Used

| Sound | Trigger |
|-------|---------|
| `wing.wav` | Bird flaps |
| `point.wav` | Pass through a pipe |
| `hit.wav` | Collide with pipe |
| `die.wav` | Hit the ground |
| `swoosh.wav` | Start/restart game |

## Project Structure

```
flappy bird/
├── flappy_bird.py          # Main game file
├── requirements.txt        # Python dependencies
├── assets/
│   ├── sprites/            # Image assets
│   │   ├── yellowbird-*.png
│   │   ├── pipe-green.png
│   │   ├── background-day.png
│   │   ├── base.png
│   │   ├── message.png
│   │   ├── gameover.png
│   │   └── 0.png ... 9.png
│   └── audio/              # Sound effects
│       ├── wing.wav
│       ├── point.wav
│       ├── hit.wav
│       ├── die.wav
│       └── swoosh.wav
└── README.md
```

## Game Mechanics

- **Gravity:** The bird constantly falls downward
- **Flap:** Pressing space gives the bird upward velocity
- **Pipes:** Spawn from the right, move left at a constant speed
- **Scoring:** +1 point for each pipe pair successfully passed
- **Death:** Hitting a pipe or the ground ends the game
- **Medals:**
  - Bronze — 1+ points
  - Silver — 5+ points
  - Gold — 10+ points

## Technical Details

- **Screen Resolution:** 288x512 (matches original Flappy Bird)
- **Frame Rate:** 60 FPS
- **Collision Detection:** Pixel-perfect mask collision
- **Scrolling:** Two-layer parallax (background + ground)
- **Pipe Spawning:** Every 1.2 seconds with random gap positions

## About

This is the third project in the [Neovim Projects](https://github.com/DavidH1ll/neovim-projects) learning journey. The entire game was written entirely in Neovim.

## License

Game code: MIT
Assets: [MIT](https://github.com/samuelcust/flappy-bird-assets/blob/master/LICENSE) (by Samuel Custodio)
