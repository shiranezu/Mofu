# Mofu — Study & Productivity Planner

A personal study planner and productivity tracker built with Django. Mofu helps you organise your schedule, track study sessions, manage tasks, and stay consistent.

## Features

- **Timetable Planner** — Create weekly timetables with timeslots and subjects, with Mon–Fri or full-week view
- **Task Manager** — Organise tasks across boards with priorities, due dates, and status tracking
- **Study Timer** — Track study sessions with categories, tags, and productivity ratings
- **Pomodoro Timer** — Configurable 25/5 focus and break cycles
- **Countdown Timer** — Set a target duration and count down to it
- **Statistics** — Visualise daily study time and category breakdowns with Chart.js
- **Study Streaks** — Track consecutive study days and your longest streak
- **Study Goals** — Set daily or weekly hour targets with live progress
- **Study Resources** — Save links organised by category
- **Session Notes** — Document what you studied after each session
- **Notes** — Rich-text note editor powered by Quill
- **Schedule** — Calendar for one-off events and entries
- **Dictionary** — In-app word lookup powered by the Free Dictionary API
- **Data Export / Import** — Download all your data as JSON and re-import it
- **Dark Mode** — Fully themed, persisted via localStorage
- **Onboarding Checklist** — Guides new users through first-time setup

## Tech Stack

- **Backend** — Django 4.2.5, Python 3
- **Database** — SQLite (local) / PostgreSQL (production)
- **Static files** — WhiteNoise with compressed manifest storage
- **PDF export** — ReportLab
- **Rich text** — Quill 2.0
- **Charts** — Chart.js 4

## Local Setup

### Prerequisites

- Python 3.8+
- pip

### Steps

1. Clone the repository

```bash
git clone https://github.com/yourusername/mofu.git
cd mofu
```

2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Create your `.env` file

```bash
cp .env.example .env
```

5. Generate a secret key and add it to `.env`

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

6. Run migrations

```bash
python manage.py migrate
```

7. Start the development server

```bash
python manage.py runserver
```

8. Visit `http://localhost:8000`

## Deployment (Railway)

1. Push the repo to GitHub
2. Create a new Railway project and connect the repo
3. Add a PostgreSQL plugin — Railway sets `DATABASE_URL` automatically
4. Set these environment variables in Railway's dashboard:

| Variable | Value |
|---|---|
| `SECRET_KEY` | A long random string (generate one locally) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `yourdomain.up.railway.app` |
| `CSRF_TRUSTED_ORIGINS` | `https://yourdomain.up.railway.app` |
| `DATABASE_URL` | Set automatically by Railway |
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` |
| `DEFAULT_FROM_EMAIL` | `Mofu <noreply@yourdomain.com>` |
| `CONTACT_EMAIL` | Your email address |

5. Railway will run `python manage.py migrate && python manage.py collectstatic --no-input` automatically on each deploy (via the `release` command in the Procfile)

## License

Released under the Apache License, Version 2.0.

## Credits

Designed and developed by Ari — Powered by Ari Tech™