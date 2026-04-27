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
├── .gitignore
└── README.md              # You are here
```

---

## Future Projects

Ideas for upcoming projects:

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
