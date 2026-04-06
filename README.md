# PulseFit Gym

A full-stack Flask site for a modern gym, featuring class schedules, trainer bios, and a contact form that stores leads in SQLite.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:8000`.

## Project structure

- `app.py` - Flask app and SQLite persistence.
- `templates/` - Jinja templates for the site.
- `static/` - CSS and JavaScript assets.
- `gym.db` - SQLite database (created on first run).
