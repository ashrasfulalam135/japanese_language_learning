# JLPT Study App 🇯🇵

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)  
![Streamlit](https://img.shields.io/badge/Streamlit-1.25-orange?logo=streamlit)  
![License](https://img.shields.io/badge/License-Personal-green)  
![Build](https://img.shields.io/github/actions/workflow/status/ashrafulalam135/japanese_language_learning/ci.yml?branch=main)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Tech Stack](#tech-stack)
5. [Installation](#installation)
6. [Database Setup](#database-setup)
7. [Running the App](#running-the-app)
8. [Development Workflow](#development-workflow)
9. [Future Roadmap](#future-roadmap)
10. [Author](#author)
11. [License](#license)

---

## Project Overview

**JLPT Study App** is a personal Japanese learning platform built using **Streamlit**.  
It is designed to prepare for **JLPT exams (N5 → N1)** with:

-   Vocabulary and kanji practice
-   Grammar explanations
-   Conversation and reading exercises
-   Flashcard-based learning

**Sprint 1** goal: establish a **professional, scalable environment**.

Completed in Sprint 1:

✔ Project environment setup  
✔ SQLite database  
✔ Streamlit app skeleton  
✔ GitHub repository with CI pipeline  
✔ Code quality tools (Black, Flake8, pre-commit hooks)  
✔ Package structure and DB migration setup

---

## Architecture
```
jlpt-study-app/
│
├── app.py                 # Streamlit entry point
├── config.py              # Environment variables
├── requirements.txt       # Python dependencies
├── database/
│   ├── db.py              # SQLAlchemy engine/session
│   ├── models.py          # Base models
│   └── __init__.py
├── scripts/
│   ├── init_db.py         # DB initialization script
│   └── __init__.py
├── modules/               # Feature modules (lessons, flashcards, etc.)
├── auth/                  # Authentication modules (Sprint 2)
├── pages/                 # Streamlit multi-page content
├── tests/                 # Unit tests (future)
└── .github/workflows/     # CI/CD pipeline
```
---

**Flow:**

1. Streamlit runs → `app.py`
2. Database via SQLAlchemy → `jlpt.db`
3. Future migrations managed via Alembic
4. CI pipeline ensures code quality on push

---

## Features (Sprint 1)

-   ✅ Project skeleton and folder structure
-   ✅ Virtual environment setup
-   ✅ SQLite database initialization
-   ✅ Streamlit “Hello World” page
-   ✅ GitHub repo with CI pipeline
-   ✅ Black code formatter & Flake8 linting
-   ✅ Pre-commit hooks for automated quality checks

---

## Tech Stack

| Layer           | Technology                |
| --------------- | ------------------------- |
| Frontend        | Streamlit                 |
| Backend         | Python 3.11+              |
| Database        | SQLite                    |
| ORM             | SQLAlchemy                |
| Code Quality    | Black, Flake8, pre-commit |
| Version Control | Git, GitHub               |
| CI/CD           | GitHub Actions            |

---

## Installation

### 1. Clone repo

```bash
git clone https://github.com/ashrafulalam135/japanese_language_learning.git
cd jlpt-study-app
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
# venv\Scripts\activate    # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Database Setup

Initialize SQLite database:

```bash
python -m scripts.init_db
```

Database jlpt.db will be created in the project root.

---

## Running the App

Start Streamlit:

```bash
streamlit run app.py
```

Open browser:

```bash
http://localhost:8501
```

---

## Development Workflow

### Code Formatting

```bash
black .
```

### Linting

```bash
flake8
```

### Pre-commit checks

```bash
pre-commit run --all-files
```

### CI Pipeline

-   GitHub Actions runs on every push to `main`
-   Installs dependencies and checks code formatting & linting

---

## Future Roadmap

**Sprint 2** → Authentication & Authorization

-   User registration/login
-   Role-based access (Admin/User)

**Sprint 3+** → Learning modules

-   Vocabulary, Kanji, Grammar, Flashcards
-   Progress tracking, JLPT-level content

**Long-term goals**

-   100–200 users
-   Mobile friendly UI
-   Migration to PostgreSQL
-   Deployment via AWS
-   AI-assisted quiz generation

---

## Author

**Ashraful Alam**

-   ADAS Product Owner & Data Engineer in a japanese car manufacturing company

---

## License

Personal project – educational purposes only.
