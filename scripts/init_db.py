from database.db import SessionLocal, engine
from database.models import Base, Feature, User  # noqa: F401

INITIAL_FEATURES = [
    {
        "code": "dashboard",
        "name": "Dashboard",
        "category": "core",
        "description": "Authenticated landing page for logged-in users.",
    },
    {
        "code": "read_lesson",
        "name": "Read Lesson",
        "category": "lesson",
        "description": "Allows a user to read lesson content.",
    },
    {
        "code": "create_lesson",
        "name": "Create Lesson",
        "category": "lesson",
        "description": "Allows an admin to create and manage lessons.",
    },
]


def seed_features() -> None:
    with SessionLocal() as db:
        existing_codes = {code for (code,) in db.query(Feature.code).all()}
        for feature in INITIAL_FEATURES:
            if feature["code"] in existing_codes:
                continue
            db.add(Feature(**feature))
        db.commit()


Base.metadata.create_all(bind=engine)
seed_features()

print("Database created")
