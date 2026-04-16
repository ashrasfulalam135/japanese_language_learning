# JLPT Study App

Personal Japanese learning platform built with Streamlit.

## Overview

The app currently includes:

- pre-auth pages for `Home`, `Login`, and `Register`
- email verification for newly registered users
- database-backed user storage with SQLite + SQLAlchemy
- role-based access
  - `admin` can access all current features
  - `user` can access only allowed features
- lesson pages
  - `Read Lesson`
  - `Create Lesson` for admin only

## Current Routes

The app uses Streamlit path-based routing:

- `/`
- `/login`
- `/register`
- `/dashboard`
- `/read-lesson`
- `/create-lesson`

## Current Structure

```text
japanese_language_learning/
├── app.py
├── config.py
├── requirements.txt
├── auth_config.yaml
├── auth/
│   ├── db_auth.py
│   ├── login_page.py
│   ├── login_view.py
│   ├── register_page.py
│   ├── register_view.py
│   └── verification.py
├── core/
│   └── auth_state.py
├── dashboard/
│   ├── dashboard_page.py
│   └── dashboard_view.py
├── home/
│   ├── home_page.py
│   └── home_view.py
├── lesson_pages/
│   ├── create_lesson.py
│   └── read_lesson.py
├── database/
│   ├── db.py
│   └── models.py
└── scripts/
    └── init_db.py
```

## Tech Stack

- Frontend: Streamlit
- Backend: Python 3.10+
- Database: SQLite
- ORM: SQLAlchemy
- Authentication UI/Session: `streamlit-authenticator`
- Email: SMTP

## Authentication Design

`auth_config.yaml` is now used mainly for cookie/auth app settings and as a bootstrap source for legacy users.

Active user data is stored in the database:

- username
- email
- first name
- last name
- password hash
- role
- allowed features
- verification token
- verification expiry
- verification status

On first run with an empty `users` table, existing users from `auth_config.yaml` are imported into the database.

## Environment Variables

Create a `.env` file in the project root.

Example:

```env
APP_ENV=dev
DATABASE_URL=sqlite:///jlpt.db

APP_BASE_URL=http://localhost:8501

SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
SMTP_USE_STARTTLS=true
EMAIL_FROM=admin@jlpt.local

VERIFICATION_EXPIRY_HOURS=24
```

## Installation

```bash
git clone https://github.com/ashrafulalam135/japanese_language_learning.git
cd japanese_language_learning
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Database Setup

Initialize the database manually if needed:

```bash
python -m scripts.init_db
```

This creates the SQLite database and tables.

## Run the App

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## Current Access Rules

- before login: no sidebar is shown
- after login: sidebar navigation is shown
- sidebar includes:
  - `Dashboard`
  - `Lesson`
    - `Read Lesson`
    - `Create Lesson` for admin only
  - `Logout`

## Development Notes

- newly registered users are created with role `user`
- new users must verify their email before login is allowed
- the app currently uses SQLite locally
- the DB auth layer was introduced after an earlier YAML-only auth version

## Quality Commands

Format:

```bash
black .
```

Run pre-commit:

```bash
pre-commit run --all-files
```

## Future Improvements

- proper DB migrations with Alembic instead of local schema repair logic
- forgot password flow
- admin UI for assigning feature access to users
- richer lesson management UI
- PostgreSQL support for deployment

## Author

Ashraful Alam

## License

Personal project for learning and development.
