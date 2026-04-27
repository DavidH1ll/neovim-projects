#!/usr/bin/env python3
"""
MSP Password Generator Web App

A Flask web application for generating passwords based on company-specific schemes.
No database is used — company schemes are stored in a JSON file.
Passwords are generated on-the-fly and are never saved.
"""

import json
import os
import secrets
import string
from pathlib import Path

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

BASE_DIR = Path(__file__).parent
COMPANIES_FILE = BASE_DIR / "companies.json"

AMBIGUOUS_CHARS = "0O1lI"


def load_companies():
    """Load company schemes from JSON file."""
    if not COMPANIES_FILE.exists():
        return {"companies": []}
    with open(COMPANIES_FILE, "r") as f:
        return json.load(f)


def save_companies(data):
    """Save company schemes to JSON file."""
    with open(COMPANIES_FILE, "w") as f:
        json.dump(data, f, indent=2)


def generate_password(scheme):
    """Generate a password based on a company scheme."""
    length = secrets.randbelow(
        scheme["max_length"] - scheme["min_length"] + 1
    ) + scheme["min_length"]

    characters = ""
    required_chars = []

    if scheme["require_lowercase"]:
        pool = string.ascii_lowercase
        if scheme.get("exclude_ambiguous", False):
            pool = "".join(c for c in pool if c not in AMBIGUOUS_CHARS)
        characters += pool
        required_chars.append(secrets.choice(pool))

    if scheme["require_uppercase"]:
        pool = string.ascii_uppercase
        if scheme.get("exclude_ambiguous", False):
            pool = "".join(c for c in pool if c not in AMBIGUOUS_CHARS)
        characters += pool
        required_chars.append(secrets.choice(pool))

    if scheme["require_digits"]:
        pool = string.digits
        if scheme.get("exclude_ambiguous", False):
            pool = "".join(c for c in pool if c not in AMBIGUOUS_CHARS)
        characters += pool
        required_chars.append(secrets.choice(pool))

    if scheme["require_symbols"]:
        pool = string.punctuation
        characters += pool
        required_chars.append(secrets.choice(pool))

    if not characters:
        raise ValueError("At least one character type must be selected.")

    # Fill remaining length
    remaining = length - len(required_chars)
    for _ in range(remaining):
        required_chars.append(secrets.choice(characters))

    # Shuffle
    secrets.SystemRandom().shuffle(required_chars)
    password = "".join(required_chars)

    # Add prefix/suffix
    prefix = scheme.get("custom_prefix", "")
    suffix = scheme.get("custom_suffix", "")
    if prefix or suffix:
        password = prefix + password + suffix

    return password


def check_strength(password, scheme):
    """Evaluate password strength."""
    score = 0
    length = len(password)

    if length >= 16:
        score += 2
    elif length >= 12:
        score += 1

    if any(c.islower() for c in password):
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in string.punctuation for c in password):
        score += 1

    if score <= 2:
        return "Weak"
    elif score <= 4:
        return "Moderate"
    else:
        return "Strong"


@app.route("/")
def index():
    """Serve the main page."""
    return render_template("index.html")


@app.route("/api/companies", methods=["GET"])
def get_companies():
    """Get all company schemes."""
    data = load_companies()
    return jsonify(data["companies"])


@app.route("/api/companies", methods=["POST"])
def add_company():
    """Add a new company scheme."""
    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({"error": "Company name is required"}), 400

    companies_data = load_companies()
    companies = companies_data["companies"]

    # Generate a URL-safe ID from the name
    company_id = data["name"].lower().replace(" ", "-")
    # Ensure uniqueness
    base_id = company_id
    counter = 1
    while any(c["id"] == company_id for c in companies):
        company_id = f"{base_id}-{counter}"
        counter += 1

    new_company = {
        "id": company_id,
        "name": data["name"],
        "scheme": {
            "min_length": data.get("min_length", 12),
            "max_length": data.get("max_length", 16),
            "require_uppercase": data.get("require_uppercase", True),
            "require_lowercase": data.get("require_lowercase", True),
            "require_digits": data.get("require_digits", True),
            "require_symbols": data.get("require_symbols", True),
            "exclude_ambiguous": data.get("exclude_ambiguous", False),
            "custom_prefix": data.get("custom_prefix", ""),
            "custom_suffix": data.get("custom_suffix", ""),
        },
    }

    companies.append(new_company)
    save_companies(companies_data)

    return jsonify(new_company), 201


@app.route("/api/companies/<company_id>", methods=["DELETE"])
def delete_company(company_id):
    """Delete a company scheme."""
    companies_data = load_companies()
    companies = companies_data["companies"]

    company = next((c for c in companies if c["id"] == company_id), None)
    if not company:
        return jsonify({"error": "Company not found"}), 404

    companies.remove(company)
    save_companies(companies_data)

    return jsonify({"message": "Company deleted"})


@app.route("/api/generate", methods=["POST"])
def generate():
    """Generate a password for a selected company."""
    data = request.get_json()
    company_id = data.get("company_id")

    if not company_id:
        return jsonify({"error": "Company ID is required"}), 400

    companies_data = load_companies()
    company = next(
        (c for c in companies_data["companies"] if c["id"] == company_id), None
    )

    if not company:
        return jsonify({"error": "Company not found"}), 404

    password = generate_password(company["scheme"])
    strength = check_strength(password, company["scheme"])

    return jsonify({
        "password": password,
        "strength": strength,
        "company": company["name"],
        "scheme": company["scheme"],
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
