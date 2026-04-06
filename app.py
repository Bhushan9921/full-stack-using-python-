from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "gym.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")





CLASSES = [
    {
        "name": "Strength Foundations",
        "level": "Beginner",
        "duration": "45 min",
        "coach": "Maya",
    },
    {
        "name": "HIIT Ignite",
        "level": "Intermediate",
        "duration": "30 min",
        "coach": "Jordan",
    },
    {
        "name": "Mobility Flow",
        "level": "All Levels",
        "duration": "40 min",
        "coach": "Sam",
    },
]


TRAINERS = [
    {
        "name": "Maya Rivera",
        "specialty": "Strength & Conditioning",
        "experience": "7 years",
    },
    {
        "name": "Jordan Lee",
        "specialty": "HIIT & Performance",
        "experience": "5 years",
    },
    {
        "name": "Sam Patel",
        "specialty": "Mobility & Recovery",
        "experience": "6 years",
    },
]


def init_db() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS contact_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                goal TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


@app.route("/")
def index() -> str:
    return render_template("index.html", classes=CLASSES, trainers=TRAINERS)


@app.route("/classes")
def classes() -> str:
    return render_template("classes.html", classes=CLASSES)


@app.route("/trainers")
def trainers() -> str:
    return render_template("trainers.html", trainers=TRAINERS)


@app.route("/contact", methods=["GET", "POST"])
def contact() -> str:
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        goal = request.form.get("goal", "").strip()
        message = request.form.get("message", "").strip()

        if not all([name, email, goal, message]):
            flash("Please complete every field so we can follow up with you.", "error")
            return redirect(url_for("contact"))

        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.execute(
                """
                INSERT INTO contact_requests (name, email, goal, message)
                VALUES (?, ?, ?, ?)
                """,
                (name, email, goal, message),
            )
            connection.commit()

        flash("Thanks for reaching out! We'll reply within one business day.", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")


@app.route("/api/classes")
def api_classes() -> tuple[str, int, dict[str, str]]:
    return jsonify({"classes": CLASSES}), 200, {"Cache-Control": "no-store"}

init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
