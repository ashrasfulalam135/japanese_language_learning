from __future__ import annotations

import json
from datetime import datetime

import streamlit_authenticator as stauth

from database.db import SessionLocal
from database.models import RoleFeature, User


def _serialize_allowed_features(value: list[str] | None) -> str:
    return json.dumps(value or [])


def _deserialize_allowed_features(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return []


def _user_to_auth_credentials(user: User) -> dict:
    return {
        "email": user.email,
        "name": f"{user.first_name} {user.last_name}".strip(),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "password": user.password_hash,
        "roles": [user.role],
    }


def get_user_record(username: str | None) -> dict:
    if not username:
        return {}

    with SessionLocal() as db:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return {}

        allowed_features = _deserialize_allowed_features(user.allowed_features)
        role_features = [
            feature_code
            for (feature_code,) in db.query(RoleFeature.feature_code)
            .filter(RoleFeature.role == user.role)
            .all()
        ]
        effective_features = sorted(set(role_features + allowed_features))
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "roles": [user.role],
            "allowed_features": allowed_features,
            "role_features": role_features,
            "effective_features": effective_features,
            "verified": user.is_verified,
            "verification_token": user.verification_token,
            "verification_expires_at": user.verification_expires_at,
        }


def get_user_id(username: str | None) -> int | None:
    return get_user_record(username).get("id")


def build_credentials() -> dict:
    with SessionLocal() as db:
        users = db.query(User).all()
        usernames = {}
        for user in users:
            usernames[user.username] = _user_to_auth_credentials(user)
        return {"usernames": usernames}


def register_user(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    verification_token: str,
    verification_expires_at,
    role: str = "user",
) -> tuple[str, str]:
    normalized_email = email.strip().lower()
    username = normalized_email

    with SessionLocal() as db:
        email_match = User.email == normalized_email
        username_match = User.username == username
        user_query = db.query(User)
        existing_user = user_query.filter(email_match | username_match).first()
        if existing_user:
            raise ValueError("Email already registered")

        user = User(
            username=username,
            email=normalized_email,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            password_hash=stauth.Hasher.hash(password.strip()),
            role=role,
            allowed_features=_serialize_allowed_features([]),
            is_verified=False,
            verification_token=verification_token,
            verification_expires_at=verification_expires_at,
        )
        db.add(user)
        db.commit()
        return normalized_email, username


def delete_user(username: str) -> None:
    with SessionLocal() as db:
        user = db.query(User).filter(User.username == username).first()
        if user:
            db.delete(user)
            db.commit()


def verify_user_by_token(token: str) -> bool:
    with SessionLocal() as db:
        user = db.query(User).filter(User.verification_token == token).first()
        if not user or not user.verification_expires_at:
            return False

        expiry = user.verification_expires_at
        if expiry.tzinfo is not None:
            expiry = expiry.replace(tzinfo=None)
        if datetime.utcnow() > expiry:
            return False

        user.is_verified = True
        user.verification_token = None
        user.verification_expires_at = None
        db.commit()
        return True
