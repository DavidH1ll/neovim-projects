# MSP Password Generator

A web-based password generator built for Managed Service Providers (MSPs). Generate secure, company-specific passwords with custom schemes — no passwords are ever saved.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3+-green)

## Features

- **Company-Specific Schemes** — Each client can have their own password rules
- **Secure Generation** — Uses Python's `secrets` module for cryptographically strong passwords
- **No Database** — Company schemes stored in a simple JSON file
- **Passwords Never Saved** — Generated on-the-fly and displayed only to you
- **Dark Mode UI** — Professional MSP-themed interface
- **Add / Remove Companies** — Manage client schemes on the fly
- **Copy to Clipboard** — One-click password copying
- **Strength Indicator** — Visual feedback on password strength

## Password Scheme Options

Per company, you can configure:

| Option | Description |
|--------|-------------|
| Min/Max Length | Password length range |
| Uppercase (A-Z) | Require uppercase letters |
| Lowercase (a-z) | Require lowercase letters |
| Digits (0-9) | Require numbers |
| Symbols (!@#) | Require special characters |
| No Ambiguous | Exclude `0`, `O`, `1`, `l`, `I` |
| Custom Prefix | e.g., `ACME-` |
| Custom Suffix | e.g., `-2024` |

## Quick Start

### 1. Install Dependencies

```bash
cd "password generator"
pip install -r requirements.txt
```

### 2. Run the App

```bash
python app.py
```

### 3. Open in Browser

Navigate to: **http://localhost:5000**

## Default Companies

The app ships with 3 example companies to demonstrate the scheme system:

- **Acme Corp** — Standard 12-16 char complex password
- **Globex Industries** — 14-20 chars, no ambiguous characters, `GLB-` prefix
- **Initech** — 10-12 chars, no symbols, `!IT` suffix

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/companies` | List all companies |
| POST | `/api/companies` | Add a new company |
| DELETE | `/api/companies/<id>` | Remove a company |
| POST | `/api/generate` | Generate a password |

## Project Structure

```
password generator/
├── app.py                  # Flask backend
├── companies.json          # Company schemes storage
├── requirements.txt        # Python dependencies
├── password_generator.py   # Original CLI version
├── templates/
│   └── index.html          # Web interface
├── static/
│   ├── css/
│   │   └── style.css       # Dark theme styles
│   └── js/
│       └── app.js          # Frontend logic
└── README.md
```

## Why This Exists

As an MSP, you manage passwords for dozens of clients. Each client has different compliance requirements, legacy systems, or security policies. This tool lets you:

- Standardize password generation per client
- Ensure compliance with client-specific rules
- Never worry about passwords being leaked from a database
- Generate passwords quickly during onboarding or resets

## Security Notes

- Passwords are generated using `secrets.SystemRandom()` (CSPRNG)
- No password is ever written to disk or logged
- Company schemes are the only persistent data (JSON file)
- For production, run behind a reverse proxy (nginx/traefik) with HTTPS

## About

This project started as a simple CLI password generator and was upgraded to a web app for MSP use. It's part of the [Neovim Projects](https://github.com/DavidH1ll/neovim-projects) learning journey.
