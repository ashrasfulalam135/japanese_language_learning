from __future__ import annotations

from dataclasses import dataclass

from database.db import SessionLocal
from database.models import Feature, RoleFeature, User
from features.auth.services.user_service import (
    _deserialize_allowed_features,
    _serialize_allowed_features,
)


@dataclass(slots=True)
class ManagedUser:
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_verified: bool
    allowed_features: list[str]
    role_features: list[str]
    effective_features: list[str]


@dataclass(slots=True)
class ManagedFeature:
    code: str
    name: str
    category: str
    description: str | None
    is_active: bool


@dataclass(slots=True)
class ManagedRole:
    name: str
    feature_codes: list[str]


def list_users() -> list[ManagedUser]:
    with SessionLocal() as db:
        users = db.query(User).order_by(User.role.desc(), User.email.asc()).all()
        role_feature_map = _load_role_feature_map(db)
        return [
            ManagedUser(
                id=user.id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role,
                is_verified=user.is_verified,
                allowed_features=_deserialize_allowed_features(user.allowed_features),
                role_features=role_feature_map.get(user.role, []),
                effective_features=sorted(
                    set(
                        role_feature_map.get(user.role, [])
                        + _deserialize_allowed_features(user.allowed_features)
                    )
                ),
            )
            for user in users
        ]


def get_user_by_id(user_id: int) -> ManagedUser | None:
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        role_feature_map = _load_role_feature_map(db)
        allowed_features = _deserialize_allowed_features(user.allowed_features)
        return ManagedUser(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            is_verified=user.is_verified,
            allowed_features=allowed_features,
            role_features=role_feature_map.get(user.role, []),
            effective_features=sorted(
                set(role_feature_map.get(user.role, []) + allowed_features)
            ),
        )


def _load_role_feature_map(db) -> dict[str, list[str]]:
    role_feature_map: dict[str, list[str]] = {}
    for role, feature_code in (
        db.query(RoleFeature.role, RoleFeature.feature_code)
        .order_by(RoleFeature.role.asc(), RoleFeature.feature_code.asc())
        .all()
    ):
        role_feature_map.setdefault(role, []).append(feature_code)
    return role_feature_map


def list_active_features() -> list[ManagedFeature]:
    with SessionLocal() as db:
        features = (
            db.query(Feature)
            .filter(Feature.is_active.is_(True))
            .order_by(Feature.category.asc(), Feature.name.asc())
            .all()
        )
        return [
            ManagedFeature(
                code=feature.code,
                name=feature.name,
                category=feature.category,
                description=feature.description,
                is_active=feature.is_active,
            )
            for feature in features
        ]


def list_roles() -> list[ManagedRole]:
    with SessionLocal() as db:
        m = _load_role_feature_map(db)

        db_roles = {
            role
            for (role,) in db.query(User.role).filter(User.role != "admin").distinct()
        }

        roles = sorted((set(m) | db_roles) - {"admin"})

        return [ManagedRole(name=r, feature_codes=m.get(r, [])) for r in roles]


def get_role(name: str) -> ManagedRole:
    roles = {role.name: role for role in list_roles()}
    return roles.get(name, ManagedRole(name=name, feature_codes=[]))


def update_role_features(role: str, feature_codes: list[str]) -> None:
    normalized_codes = sorted(set(feature_codes))
    with SessionLocal() as db:
        db.query(RoleFeature).filter(RoleFeature.role == role).delete()
        for code in normalized_codes:
            db.add(RoleFeature(role=role, feature_code=code))
        db.commit()


def update_user_access(
    user_id: int,
    *,
    role: str,
    allowed_features: list[str],
    is_verified: bool,
) -> None:
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        user.role = role
        user.is_verified = is_verified
        user.allowed_features = _serialize_allowed_features(
            sorted(set(allowed_features))
        )
        db.commit()
