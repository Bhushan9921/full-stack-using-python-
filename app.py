from __future__ import annotations

import json
import os
import sqlite3
from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "gym.db"
STATIC_DIR = BASE_DIR / "static"

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

CLASSES = [
    {"name": "Strength Foundations", "level": "Beginner", "duration": "45 min", "coach": "Maya"},
    {"name": "HIIT Ignite", "level": "Intermediate", "duration": "30 min", "coach": "Jordan"},
    {"name": "Mobility Flow", "level": "All Levels", "duration": "40 min", "coach": "Sam"},
]

TRAINERS = [
    {"name": "Maya Rivera", "specialty": "Strength & Conditioning", "experience": "7 years"},
    {"name": "Jordan Lee", "specialty": "HIIT & Performance", "experience": "5 years"},
    {"name": "Sam Patel", "specialty": "Mobility & Recovery", "experience": "6 years"},
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


def base_layout(content: str, flash: str = "") -> str:
    flash_html = f'<div class="container flash-area">{flash}</div>' if flash else ""
    return f"""<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <title>PulseFit Gym</title>
    <link rel=\"stylesheet\" href=\"/static/css/style.css\" />
  </head>
  <body>
    <header class=\"site-header\">
      <div class=\"container header-content\">
        <div class=\"logo\">PulseFit Gym</div>
        <nav class=\"nav-links\">
          <a href=\"/\">Home</a>
          <a href=\"/classes\">Classes</a>
          <a href=\"/trainers\">Trainers</a>
          <a href=\"/contact\">Contact</a>
        </nav>
        <a class=\"cta-button\" href=\"/contact\">Book a Tour</a>
      </div>
    </header>

    {flash_html}

    <main>{content}</main>

    <footer class=\"site-footer\">
      <div class=\"container footer-content\">
        <div>
          <h4>PulseFit Gym</h4>
          <p>Open daily · 5am - 10pm</p>
        </div>
        <div>
          <h4>Location</h4>
          <p>120 Energy Ave · Austin, TX</p>
        </div>
        <div>
          <h4>Follow</h4>
          <p>@pulsefitgym</p>
        </div>
      </div>
    </footer>

    <script src=\"/static/js/main.js\"></script>
  </body>
</html>
"""


def render_home() -> str:
    class_cards = "".join(
        f"""
        <div class=\"info-card\">
          <h3>{escape(item['name'])}</h3>
          <p>{escape(item['duration'])} · {escape(item['level'])}</p>
          <p class=\"muted\">Coach {escape(item['coach'])}</p>
        </div>
        """
        for item in CLASSES
    )
    trainer_cards = "".join(
        f"""
        <div class=\"info-card\">
          <h3>{escape(trainer['name'])}</h3>
          <p>{escape(trainer['specialty'])}</p>
          <p class=\"muted\">{escape(trainer['experience'])} of coaching</p>
        </div>
        """
        for trainer in TRAINERS
    )
    return f"""
<section class=\"hero\">
  <div class=\"container hero-content\">
    <div>
      <p class=\"tag\">Community-first training</p>
      <h1>Train smarter with a gym built for busy professionals.</h1>
      <p class=\"subtitle\">PulseFit blends strength, conditioning, and recovery so you can keep momentum all year.</p>
      <div class=\"hero-actions\">
        <a class=\"cta-button\" href=\"/contact\">Start your plan</a>
        <a class=\"secondary-button\" href=\"/classes\">View class schedule</a>
      </div>
    </div>
    <div class=\"hero-card\">
      <h3>Today's Highlights</h3>
      <ul>
        <li>5:30am · Strength Foundations</li>
        <li>12:00pm · HIIT Ignite</li>
        <li>6:15pm · Mobility Flow</li>
      </ul>
    </div>
  </div>
</section>
<section class=\"section\"><div class=\"container\"><div class=\"section-header\"><h2>Signature classes</h2></div><div class=\"card-grid\">{class_cards}</div></div></section>
<section class=\"section alt\"><div class=\"container\"><div class=\"section-header\"><h2>Meet your coaches</h2></div><div class=\"card-grid\">{trainer_cards}</div></div></section>
"""


def render_classes() -> str:
    cards = "".join(
        f"""
        <div class=\"info-card\">
          <h3>{escape(item['name'])}</h3>
          <p>{escape(item['duration'])} · {escape(item['level'])}</p>
          <p class=\"muted\">Led by Coach {escape(item['coach'])}</p>
          <button class=\"secondary-button\" type=\"button\">Reserve seat</button>
        </div>
        """
        for item in CLASSES
    )
    return f"""
<section class=\"page-hero\"><div class=\"container\"><h1>Weekly class schedule</h1></div></section>
<section class=\"section\"><div class=\"container\"><div class=\"card-grid\">{cards}</div></div></section>
"""


def render_trainers() -> str:
    cards = "".join(
        f"""
        <div class=\"info-card\">
          <h3>{escape(trainer['name'])}</h3>
          <p>{escape(trainer['specialty'])}</p>
          <p class=\"muted\">{escape(trainer['experience'])} experience</p>
        </div>
        """
        for trainer in TRAINERS
    )
    return f"""
<section class=\"page-hero\"><div class=\"container\"><h1>Coaches who coach with intention</h1></div></section>
<section class=\"section\"><div class=\"container\"><div class=\"card-grid\">{cards}</div></div></section>
"""


def render_contact() -> str:
    return """
<section class=\"page-hero\"><div class=\"container\"><h1>Book a tour or free consult</h1></div></section>
<section class=\"section\">
  <div class=\"container split\">
    <form class=\"contact-form\" method=\"post\" action=\"/contact\">
      <label>Full name<input type=\"text\" name=\"name\" required /></label>
      <label>Email address<input type=\"email\" name=\"email\" required /></label>
      <label>Training goal
        <select name=\"goal\" required>
          <option value=\"\">Choose a goal</option>
          <option value=\"Strength\">Build strength</option>
          <option value=\"Conditioning\">Improve conditioning</option>
          <option value=\"Recovery\">Prioritize recovery</option>
        </select>
      </label>
      <label>Message<textarea name=\"message\" rows=\"5\" required></textarea></label>
      <button class=\"cta-button\" type=\"submit\">Send request</button>
    </form>
  </div>
</section>
"""


class GymHandler(BaseHTTPRequestHandler):
    def _send_html(self, html: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, data: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", location)
        self.end_headers()

    def _serve_static(self, route_path: str) -> None:
        file_path = (BASE_DIR / route_path.lstrip("/")).resolve()
        if STATIC_DIR not in file_path.parents or not file_path.exists():
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        mime = "text/plain"
        if file_path.suffix == ".css":
            mime = "text/css"
        elif file_path.suffix == ".js":
            mime = "application/javascript"

        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        flash = parse_qs(parsed.query).get("flash", [""])[0]

        if parsed.path.startswith("/static/"):
            self._serve_static(parsed.path)
            return

        if parsed.path == "/":
            self._send_html(base_layout(render_home(), flash))
        elif parsed.path == "/classes":
            self._send_html(base_layout(render_classes(), flash))
        elif parsed.path == "/trainers":
            self._send_html(base_layout(render_trainers(), flash))
        elif parsed.path == "/contact":
            self._send_html(base_layout(render_contact(), flash))
        elif parsed.path == "/api/classes":
            self._send_json({"classes": CLASSES})
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/contact":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8")
        form = parse_qs(raw_body)

        name = form.get("name", [""])[0].strip()
        email = form.get("email", [""])[0].strip()
        goal = form.get("goal", [""])[0].strip()
        message = form.get("message", [""])[0].strip()

        if not all([name, email, goal, message]):
            self._redirect("/contact?flash=Please+complete+every+field.")
            return

        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.execute(
                "INSERT INTO contact_requests (name, email, goal, message) VALUES (?, ?, ?, ?)",
                (name, email, goal, message),
            )
            connection.commit()

        self._redirect("/contact?flash=Thanks+for+reaching+out!+We+will+reply+soon.")


def run() -> None:
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), GymHandler)
    print(f"PulseFit running on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run()
