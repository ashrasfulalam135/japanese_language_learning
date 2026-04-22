# JLPT Study App

A Streamlit-based Japanese learning app with DB-backed authentication, email verification, role-based access, and modular lesson management.

## What It Does

Current features:

- pre-auth pages:
  - `Home`
  - `Login`
  - `Register`
- email verification for newly registered users
- DB-backed user storage with SQLite + SQLAlchemy
- role-based access:
  - `admin` can access all current features
  - `user` can access only the features assigned to them
- lesson features:
  - `Read Lesson`
  - `Create Lesson` for admin
- lesson creation supports:
  - lesson metadata
  - multiple conversation lines
  - multiple vocabularies
  - multiple grammar entries

## Current Routes

The app uses Streamlit path-based routing:

- `/`
- `/login`
- `/register`
- `/dashboard`
- `/read-lesson`
- `/create-lesson`

## Project Structure

The project now follows a feature-first structure.

```text
japanese_language_learning/
├── app.py
├── config.py
├── auth_config.yaml
├── requirements.txt
├── jlpt.db
├── database/
│   ├── db.py
│   └── models.py
├── features/
│   ├── auth/
│   │   ├── pages/
│   │   ├── services/
│   │   └── views/
│   ├── dashboard/
│   │   ├── pages/
│   │   └── views/
│   ├── home/
│   │   ├── pages/
│   │   └── views/
│   └── lessons/
│       ├── pages/
│       └── services/
├── scripts/
│   └── init_db.py
└── tests/
    ├── test_auth_state.py
    ├── test_db_auth.py
    ├── test_helpers.py
    ├── test_lesson_service.py
    └── test_verification.py
```

## Tech Stack

- UI: Streamlit
- Backend: Python 3.10+
- Database: SQLite
- ORM: SQLAlchemy
- Auth UI/session layer: `streamlit-authenticator`
- Email verification: SMTP
- Tests: `unittest`

## Authentication Design

User data is stored in the database, not in YAML.

`auth_config.yaml` is used only for auth-related app config such as cookie settings.

User records currently store:

- `username`
- `email`
- `first_name`
- `last_name`
- `password_hash`
- `role`
- `allowed_features`
- `is_verified`
- `verification_token`
- `verification_expires_at`
- timestamps

Registration flow:

1. User registers from `/register`
2. User is created in the DB with role `user`
3. User starts as unverified
4. Verification email is sent
5. User can log in only after verification

## Authorization Model

Current roles:

- `admin`
- `user`

Current access behavior:

- before login: no sidebar is shown
- after login: sidebar is shown
- sidebar contains:
  - `Dashboard`
  - `Lesson`
    - `Read Lesson`
    - `Create Lesson` for admin only
  - `Logout`

The app also supports `allowed_features` on users for future finer-grained access control.

## Lesson Data Model

Lessons are stored in separate normalized tables so the content can be reused later for things like flashcards and quizzes.

Main tables:

- `lessons`
- `conversations`
- `vocabularies`
- `grammars`
- `users`
- `features`

Current lesson creation saves:

- lesson level
- lesson number
- lesson title
- conversation lines
- vocabularies
- grammar items

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

## Setup

```bash
git clone https://github.com/ashrafulalam135/japanese_language_learning.git
cd japanese_language_learning
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Initialize The Database

```bash
python -m scripts.init_db
```

This creates the database tables and seeds the initial feature records.

## Run The App

```bash
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## Run Tests

Using the project virtual environment:

```bash
./venv/bin/python -m unittest discover -s tests -v
```

Current test coverage includes:

- auth session and access guards
- DB auth helpers
- verification helpers and email sending behavior
- lesson creation service and validation rules

## Run Pre-commit Checks

Run all configured checks locally with:

```bash
./venv/bin/pre-commit run --all-files
```

## Development Notes

- feature code is modularized under `features/`
- page entry files live inside each feature package
- business logic is kept in feature services
- the current app uses SQLite locally
- the current lesson reading page is still a placeholder
- quiz generation is planned for later

## Next Likely Improvements

- admin UI for assigning features to users
- richer lesson read/manage screens
- forgot password flow
- AI-generated lesson quizzes
- Alembic migrations for safer schema evolution
- PostgreSQL support for deployment

## Author

Ashraful Alam

## License

Personal project for learning and development.
