from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
    allowed_features = Column(Text, nullable=False, default="[]")
    is_verified = Column(Boolean, nullable=False, default=False)
    verification_token = Column(String, nullable=True, unique=True)
    verification_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class Feature(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False, default="general")
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class RoleFeature(Base):
    __tablename__ = "role_features"
    __table_args__ = (
        UniqueConstraint("role", "feature_code", name="uq_role_feature_role_code"),
    )

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False, index=True)
    feature_code = Column(
        String,
        ForeignKey("features.code"),
        nullable=False,
        index=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (
        UniqueConstraint(
            "lesson_level", "lesson_number", name="uq_lesson_level_number"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    lesson_level = Column(String, nullable=False, index=True)
    lesson_number = Column(Integer, nullable=False, index=True)
    title = Column(String, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    conversation_lines = relationship(
        "Conversation",
        back_populates="lesson",
        cascade="all, delete-orphan",
        order_by="Conversation.line_number",
    )
    vocabularies = relationship(
        "Vocabulary",
        back_populates="lesson",
        cascade="all, delete-orphan",
        order_by="Vocabulary.vocabulary_id",
    )
    grammar_points = relationship(
        "Grammar",
        back_populates="lesson",
        cascade="all, delete-orphan",
        order_by="Grammar.grammar_id",
    )


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (
        UniqueConstraint(
            "lesson_id", "line_number", name="uq_conversation_lesson_line"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(
        Integer,
        ForeignKey("lessons.id"),
        nullable=False,
        index=True,
    )
    line_number = Column(Integer, nullable=False)
    speaker = Column(String, nullable=True)
    japanese_romaji = Column(Text, nullable=True)
    japanese_kana = Column(Text, nullable=True)
    japanese_kanji = Column(Text, nullable=True)
    english = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    lesson = relationship("Lesson", back_populates="conversation_lines")


class Vocabulary(Base):
    __tablename__ = "vocabularies"
    __table_args__ = (
        UniqueConstraint(
            "lesson_id",
            "vocabulary_id",
            name="uq_vocabulary_lesson_vocabulary_id",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(
        Integer,
        ForeignKey("lessons.id"),
        nullable=False,
        index=True,
    )
    vocabulary_id = Column(Integer, nullable=False)
    japanese_romaji = Column(String, nullable=True)
    japanese_kana = Column(String, nullable=True)
    japanese_kanji = Column(String, nullable=True)
    english = Column(String, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    lesson = relationship("Lesson", back_populates="vocabularies")


class Grammar(Base):
    __tablename__ = "grammars"
    __table_args__ = (
        UniqueConstraint(
            "lesson_id",
            "grammar_id",
            name="uq_grammar_lesson_grammar_id",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(
        Integer,
        ForeignKey("lessons.id"),
        nullable=False,
        index=True,
    )
    grammar_id = Column(Integer, nullable=False)
    grammar_pattern = Column(String, nullable=True)
    explanation = Column(Text, nullable=False)
    example_romaji = Column(Text, nullable=True)
    example_kana = Column(Text, nullable=True)
    example_kanji = Column(Text, nullable=True)
    example_english = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    lesson = relationship("Lesson", back_populates="grammar_points")
