# Neovim Platformer — Godot 2D Platformer

A complete 2D platformer built in Godot 4 while learning Neovim.

![Godot](https://img.shields.io/badge/Godot-4.6-blue)
![GDScript](https://img.shields.io/badge/GDScript-100%25-green)

## Features

### Player
- Smooth **CharacterBody2D** movement with acceleration and deceleration
- **Jump** with gravity and ground detection
- **Sprite flipping** based on movement direction
- **Idle / Jump** sprite states
- **3 Health** system with heart UI display
- **Invincibility frames** after taking damage (flash red)
- **Knockback** on damage
- **Death animation** (spin and fade)

### Level Design
- **TileMap** with custom tileset (ground, dirt, platforms)
- **One-way platforms** you can jump through from below
- **Spikes** that deal damage on contact
- **Coins** to collect with bobbing animation
- **Finish flag** to complete the level
- **Parallax background** (sky, mountains, clouds)
- **Camera2D** that follows the player with smooth drag margins

### Game Systems
- **Score tracking** (+100 per coin, +1000 for completion)
- **Coin counter** (collected / total)
- **Health bar** with red heart display
- **Game Over screen** with final score
- **Level Complete screen** with stats
- **Restart** with R key

### Controls

| Input | Action |
|-------|--------|
| `A` / `←` | Move Left |
| `D` / `→` | Move Right |
| `Space` / `W` / `↑` | Jump |
| `R` | Restart (after death or completion) |

## Quick Start

### 1. Open in Godot

```bash
cd godot-platformer
godot project.godot
```

Or open Godot and **Import** the `godot-platformer` folder.

### 2. Run the Game

Press **F5** or click the **Play** button in Godot.

## Project Structure

```
godot-platformer/
├── project.godot          # Godot project settings
├── scenes/
│   ├── main.tscn          # Main game scene
│   ├── player.tscn        # Player character
│   ├── coin.tscn          # Collectible coin
│   ├── spike.tscn         # Hazard spike
│   ├── flag.tscn          # Level finish flag
│   ├── level.tscn         # TileMap level
│   ├── background.tscn    # Parallax background
│   └── ui.tscn            # Game UI (score, health, screens)
├── scripts/
│   ├── player.gd          # Player controller
│   ├── coin.gd            # Coin pickup logic
│   ├── spike.gd           # Hazard damage logic
│   ├── flag.gd            # Level completion trigger
│   ├── game_manager.gd    # Game state & scoring
│   └── ui.gd              # UI updates & screens
├── assets/
│   ├── player/            # Player sprites
│   ├── tiles/             # Tileset images
│   ├── items/             # Coin, flag
│   ├── hazards/           # Spike
│   └── bg/                # Background layers
└── README.md
```

## Assets

All pixel art assets were generated with Python/Pillow specifically for this project:

| Asset | Size | Description |
|-------|------|-------------|
| `player_idle.png` | 32×32 | Blue character standing |
| `player_jump.png` | 32×32 | Blue character jumping |
| `ground_top.png` | 32×32 | Grass-topped dirt block |
| `ground_mid.png` | 32×32 | Dirt block |
| `platform.png` | 32×32 | Wooden one-way platform |
| `coin.png` | 24×24 | Gold coin with $ symbol |
| `spike.png` | 32×32 | Red triangular hazard |
| `flag.png` | 32×48 | Green finish flag |
| `sky.png` | 800×600 | Blue sky with clouds |
| `mountains.png` | 800×300 | Mountain silhouettes |
| `clouds.png` | 800×200 | Cloud layer |

## Level Layout

The level is approximately **2000 pixels wide** with:
- A flat ground floor with spikes placed periodically
- Multiple floating platforms at increasing heights
- Coins placed along a path leading upward
- A finish flag at the far right

## Technical Details

- **Engine:** Godot 4.6
- **Renderer:** Mobile (GLES3)
- **Physics:** Godot 2D physics
- **Collision:** Layer-based (World, Player, Hazards, Items)
- **Resolution:** 1280×720 with `canvas_items` stretch mode
- **Art Style:** Pixel art with nearest-neighbor filtering

## How It Works

### Player Physics
The player uses `CharacterBody2D` with:
- Horizontal velocity interpolated toward target speed
- Gravity applied every frame when not on floor
- Jump only allowed when `is_on_floor()` is true
- `move_and_slide()` handles all collision response

### TileMap
The level is built with Godot's `TileMap` node:
- Layer 0: "Ground" with collision shapes
- Platform tiles use **one-way collision** (jump through from below)
- Tile size: 32×32 pixels

### Camera
The `Camera2D` is a child of the player with:
- `position_smoothing_enabled` for smooth follow
- `drag_horizontal/vertical_enabled` for lazy camera
- Camera limits to keep the view inside the level bounds

### Parallax Background
Three layers with different `motion_scale`:
- Sky (0.0) — doesn't move
- Mountains (0.2) — moves slowly
- Clouds (0.4) — moves faster

## Expanding the Game

Ideas for taking this further:

- [ ] **More levels** — Add scene switching with a level select
- [ ] **Enemies** — Walking enemies with patrol paths
- [ ] **Power-ups** — Double jump, speed boost, invincibility
- [ ] **Checkpoints** — Respawn at mid-level flags
- [ ] **Timer** — Speed-run mode with best times
- [ ] **Sound** — Jump, coin, damage, and music
- [ ] **Particle effects** — Coin sparkles, dust when landing
- [ ] **AnimationPlayer** — Smooth transitions instead of instant sprite swaps
- [ ] **Save system** — Persist best scores and unlocked levels

## About

This is the fourth project in the [Neovim Projects](https://github.com/DavidH1ll/neovim-projects) learning journey. The entire project — GDScript code, scene files, and even the pixel art assets — was created entirely in Neovim.

## License

Code & assets: MIT
