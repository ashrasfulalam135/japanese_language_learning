from database.db import SessionLocal, engine
from database.models import Base, Feature, RoleFeature, User  # noqa: F401

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
    {
        "code": "user_management",
        "name": "User Management",
        "category": "admin",
        "description": "Allows an admin to manage user roles and feature access.",
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


def seed_role_features() -> None:
    with SessionLocal() as db:
        existing = {
            (role, feature_code)
            for role, feature_code in db.query(
                RoleFeature.role,
                RoleFeature.feature_code,
            ).all()
        }
        default_role_features = [
            ("admin", "dashboard"),
            ("admin", "read_lesson"),
            ("admin", "create_lesson"),
            ("admin", "user_management"),
        ]
        for role, feature_code in default_role_features:
            if (role, feature_code) in existing:
                continue
            db.add(RoleFeature(role=role, feature_code=feature_code))
        db.commit()


Base.metadata.create_all(bind=engine)
seed_features()
seed_role_features()

print("Database created")
