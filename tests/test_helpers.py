from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.models import Base, User


def create_test_session_local():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_user(
    session_local,
    *,
    username: str = "admin@example.com",
    email: str | None = None,
    first_name: str = "Admin",
    last_name: str = "User",
    password_hash: str = "hashed-password",
    role: str = "admin",
    allowed_features: str = '["read_lesson","create_lesson"]',
    is_verified: bool = True,
    verification_token: str | None = None,
    verification_expires_at=None,
) -> int:
    email = email or username
    with session_local() as db:
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=password_hash,
            role=role,
            allowed_features=allowed_features,
            is_verified=is_verified,
            verification_token=verification_token,
            verification_expires_at=verification_expires_at,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user.id
