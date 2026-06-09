# Neovim Projects

A collection of Python projects built while learning Neovim and LazyVim. Each project starts simple and grows as new skills are learned.

> **Why Neovim?** This entire repository was created, edited, and managed entirely within Neovim — no VS Code, no mouse, just keyboard-driven development.

---

## Projects

### 1. Hello World

The very first project — a classic introduction.

- **What it is:** A simple Python script that prints a greeting
- **What I learned:** Basic Neovim navigation, file creation, and running Python from the terminal
- **Tech:** Python 3

```bash
cd "hello world"
python3 hello.py
```

**Output:**
```
Hello, World!
Welcome to my first Neovim project!
```

---

### 2. Password Generator

An MSP-focused password generator that evolved from a CLI tool into a full web application.

#### CLI Version
A command-line tool for generating cryptographically secure passwords.

```bash
cd "password generator"
python3 password_generator.py -c 3 -l 20
```

| Flag | Description |
|------|-------------|
| `-l, --length` | Password length (default: 16) |
| `-c, --count` | Number of passwords (default: 1) |
| `--no-uppercase` | Exclude uppercase letters |
| `--no-lowercase` | Exclude lowercase letters |
| `--no-digits` | Exclude numbers |
| `--no-symbols` | Exclude special characters |

#### Web App Version
A Flask-based web application designed for Managed Service Providers (MSPs).

**Features:**
- **Company-specific password schemes** — Each client gets their own rules
- **No database** — Schemes stored in a simple JSON file
- **Passwords never saved** — Generated on-the-fly, displayed once
- **Add/Remove companies** — Manage client schemes dynamically
- **Dark, professional UI** — Built for MSP workflows

**Run it:**
```bash
cd "password generator"
pip install -r requirements.txt
python3 app.py
```

Then open **http://localhost:5000** in your browser.

**Default companies:**
| Company | Scheme |
|---------|--------|
| **Acme Corp** | 12-16 chars, all types |
| **Globex Industries** | 14-20 chars, `GLB-` prefix, no ambiguous chars |
| **Initech** | 10-12 chars, no symbols, `!IT` suffix |

**Tech:** Python 3, Flask, HTML/CSS/JS

---

### 3. Flappy Bird Clone ([standalone repo](https://github.com/DavidH1ll/flappy-bird))

A feature-rich Flappy Bird clone built with Pygame — now a standalone repository.

- **Features:** Day/night mode, bird colors, 3 difficulty levels, medals, persistent leaderboard
- **What I learned:** Pygame animation, pixel-perfect collision, game state management
- **Tech:** Python 3, Pygame

---

### 4. Godot 2D Platformer

A complete 2D platformer built in Godot 4 with pixel art assets created via Python scripting.

- **Features:** CharacterBody2D physics, one-way platforms, TileMap level, spikes, coins, parallax background
- **What I learned:** GDScript, Godot engine, tilemap design, 2D physics
- **Tech:** Godot 4.6, GDScript

```bash
cd godot-platformer
godot project.godot
```

---

### 5. Rogue Shooter (Pygame)

A top-down roguelike shooter with procedural generation, multiple weapon types, and boss fights.

- **Features:** Procedural room generation, enemy waves, boss encounters, weapon pickups, audio system
- **What I learned:** Advanced Pygame patterns, procedural level design, audio management
- **Tech:** Python 3, Pygame

```bash
cd rogue-shooter-pygame
pip install -r requirements.txt
python3 src/main.py
```

---

## Tools & Workflow

This repository is a living document of my Neovim learning journey.

### Editor
- **Neovim** with LazyVim distribution
- Terminal integration via `Ctrl + /` (Snacks.nvim floating terminal)
- Session management with `auto-session` plugin

### Development
- All code written entirely in Neovim
- Git operations via terminal and `vim-fugitive`
- File navigation with `neo-tree` and `telescope`

### Languages
- Python 3 (primary)
- HTML / CSS / JavaScript (for the web app)

---

## Repository Structure

```
neovim-projects/
├── hello world/
│   ├── hello.py           # Hello World script
│   └── README.md          # Project docs
├── password generator/
│   ├── app.py             # Flask web app
│   ├── password_generator.py   # CLI version
│   ├── companies.json     # Company schemes (no DB!)
│   ├── requirements.txt   # Python deps
│   ├── templates/
│   │   └── index.html     # Web UI
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css  # Dark theme
│   │   └── js/
│   │       └── app.js     # Frontend logic
│   └── README.md          # Project docs
├── godot-platformer/
│   ├── project.godot      # Godot project file
│   ├── scenes/            # Game scenes (player, level, UI)
│   ├── scripts/           # GDScript game logic
│   ├── assets/            # Pixel art sprites & backgrounds
│   └── README.md          # Project docs
├── rogue-shooter-pygame/
│   ├── src/               # Python source (player, enemy, boss, etc.)
│   ├── assets/            # Sprites, audio (music + SFX)
│   └── README.md          # Project docs
├── rogue-shooter-assets/  # Asset references
├── opencode images/       # Screenshots
├── .gitignore
└── README.md              # You are here
```

---

## Upcoming Ideas

- [ ] **Todo List CLI** — Persistent tasks with JSON storage
- [ ] **File Organizer** — Auto-sort Downloads folder by file type
- [ ] **Log Analyzer** — Parse and visualize web server logs
- [ ] **API Client** — REST API tester in the terminal
- [ ] **Markdown Note Taker** — Neovim-integrated note system

---

## Why This Exists

I started learning Neovim and realized the best way to get comfortable was to **build real things** with it. Every project in this repo was created from scratch using only Neovim — from the first line of code to the final `git push`.

No IDEs. No GUI file managers. Just Neovim, a terminal, and a lot of `:w`.

---

## License

MIT — Feel free to use, fork, or learn from these projects.

---

*Built with Neovim. Powered by coffee.*
