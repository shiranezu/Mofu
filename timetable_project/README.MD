# Sachi - A Study Productivity App

A comprehensive study planner and productivity tracker built with Django.

## Features

- **Timetable Planner** - Create and manage weekly schedules
- **Task Manager** - Organize tasks with due dates
- **Study Timer** - Track study sessions with categories
- **Pomodoro Timer** - 25-minute focus sessions with breaks
- **Statistics Dashboard** - Visualize study patterns with charts
- **Study Streaks** - Track consecutive study days
- **Study Goals** - Set daily/weekly targets with progress tracking
- **Study Resources** - Quick access to study materials
- **Session Notes** - Document what you studied

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/sachi.git
cd sachi
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create `.env` file
```bash
cp .env.example .env
```

5. Generate a new SECRET_KEY and add it to `.env`
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

6. Run migrations
```bash
python manage.py migrate
```

7. Create a superuser
```bash
python manage.py createsuperuser
```

8. Run the development server
```bash
python manage.py runserver
```

9. Visit `http://localhost:8000` in your browser

## Usage

1. Register an account or login
2. Create your first timetable
3. Add timeslots and courses
4. Start tracking your study sessions with the timer
5. Set goals and track your progress

## Technologies Used

- Django 5.x
- SQLite (default database)
- Chart.js (for statistics visualization)
- ReportLab (PDF generation)
- Python-decouple (environment variables)

## Contributing

This is a personal project, but suggestions and feedback are welcome!

## License

Released under the Apache License, Version 2.0

## Credits

Designed and developed by Ari
Powered by Ari Tech™

## Contact

For inquiries, suggestions, or feedback:
- Email: aweleoluonye@gmail.com