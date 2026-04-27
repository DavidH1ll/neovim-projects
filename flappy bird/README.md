# Flappy Bird Clone — Enhanced Edition

A faithful clone of the classic Flappy Bird game built with Pygame, with lots of extra features.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Pygame](https://img.shields.io/badge/Pygame-2.5+-green)

## Features

### Classic Gameplay
- **Tap to flap**, avoid pipes, don't hit the ground
- **Smooth Animations** — Bird flapping animation, scrolling background and ground
- **Score System** — Earn points by passing through pipes
- **Pixel-Perfect Collision** — Uses Pygame masks for accurate collision detection
- **Sound Effects** — Wing flap, scoring, hit, and death sounds
- **Three Game States** — Get Ready, Playing, Game Over

### Enhancements
- **2x Display Size** — Crisp pixel art at 576×1024 (internally rendered at 288×512 and scaled up)
- **Night Mode** — Press `N` to toggle day/night background anytime
- **Bird Color Selector** — Press `C` to cycle between Yellow, Red, and Blue birds
- **Pause Button** — Press `P` to pause and resume mid-game
- **Difficulty Levels** — Press `D` to cycle Easy / Normal / Hard:
  - **Easy** — Wider pipe gaps (120px), slower scroll, longer spawn interval
  - **Normal** — Classic settings (100px gap)
  - **Hard** — Narrow gaps (80px), faster scroll, rapid spawns
- **Day/Night Cycle** — Background automatically switches every 10 points scored
- **Persistent Leaderboard** — Top 10 scores saved to `leaderboard.json` with difficulty and bird color
- **Medal System** — Bronze (1+), Silver (5+), Gold (10+)

## Controls

| Input | Action |
|-------|--------|
| `Space` / `↑` / `Click` | Flap / Start / Restart |
| `P` | Pause / Resume |
| `N` | Toggle Night Mode |
| `C` | Change Bird Color (Yellow → Red → Blue) |
| `D` | Change Difficulty (Easy → Normal → Hard) |
| `L` | View Leaderboard |
| `R` | Restart (on game over) |
| `Esc` | Quit |

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
| `yellowbird-*.png` | Default bird animation frames |
| `redbird-*.png` | Red bird variant |
| `bluebird-*.png` | Blue bird variant |
| `pipe-green.png` | Obstacle pipes |
| `background-day.png` | Daytime background |
| `background-night.png` | Nighttime background |
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
├── leaderboard.json        # Persistent high scores (auto-created)
├── assets/
│   ├── sprites/            # Image assets
│   └── audio/              # Sound effects
└── README.md
```

## Game Mechanics

- **Gravity:** The bird constantly falls downward
- **Flap:** Pressing space gives the bird upward velocity
- **Pipes:** Spawn from the right, move left at a constant speed
- **Scoring:** +1 point for each pipe pair successfully passed
- **Death:** Hitting a pipe or the ground ends the game
- **Day/Night Cycle:** Every 10 points, the background switches between day and night
- **Difficulty Presets:**

| Mode | Gap Size | Scroll Speed | Spawn Interval |
|------|----------|-------------|----------------|
| Easy | 120px | 1.5 | 1500ms |
| Normal | 100px | 2.0 | 1200ms |
| Hard | 80px | 2.8 | 900ms |

## Technical Details

- **Internal Resolution:** 288×512 (authentic to the original)
- **Display Resolution:** 576×1024 (2× scale for crisp pixel art)
- **Frame Rate:** 60 FPS
- **Collision Detection:** Pixel-perfect mask collision
- **Scrolling:** Two-layer parallax (background + ground)
- **Pipe Spawning:** Configurable interval with random gap positions
- **Leaderboard:** JSON file persistence, sorted by score

## About

This is the third project in the [Neovim Projects](https://github.com/DavidH1ll/neovim-projects) learning journey. The entire game was written entirely in Neovim.

## License

Game code: MIT
Assets: [MIT](https://github.com/samuelcust/flappy-bird-assets/blob/master/LICENSE) (by Samuel Custodio)
