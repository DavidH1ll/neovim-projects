# Password Generator

A secure command-line password generator written in Python.

## Features

- Uses Python's `secrets` module for **cryptographically secure** randomness
- Customizable password length
- Toggle character types (uppercase, lowercase, digits, symbols)
- Generates multiple passwords at once
- Built-in password strength checker

## Usage

### Basic usage

```bash
python password_generator.py
```

### Generate a longer password

```bash
python password_generator.py -l 20
```

### Generate multiple passwords

```bash
python password_generator.py -c 5
```

### Exclude symbols

```bash
python password_generator.py --no-symbols
```

### Full customization

```bash
python password_generator.py -l 24 -c 3 --no-symbols --no-digits
```

## Options

| Flag | Description |
|------|-------------|
| `-l`, `--length` | Password length (default: 16) |
| `-c`, `--count` | Number of passwords (default: 1) |
| `--no-uppercase` | Exclude uppercase letters |
| `--no-lowercase` | Exclude lowercase letters |
| `--no-digits` | Exclude numbers |
| `--no-symbols` | Exclude special characters |

## Example Output

```
========================================
       Generated Passwords
========================================

  [1] k9#mP2$vLqRwXz!N
      Strength: Strong

========================================
Done! Keep your passwords safe.
========================================
```

## Why `secrets` instead of `random`?

The `random` module is **not** suitable for security purposes. The `secrets` module is designed for generating cryptographically strong random numbers, making it ideal for passwords, tokens, and secrets.

## About

This is the second project in the Neovim learning journey.
