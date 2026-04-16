from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.exc import IntegrityError

from database.db import SessionLocal
from database.models import Conversation, Grammar, Lesson, Vocabulary


@dataclass(slots=True)
class ConversationInput:
    line_number: int
    english: str
    speaker: str | None = None
    japanese_romaji: str | None = None
    japanese_kana: str | None = None
    japanese_kanji: str | None = None


@dataclass(slots=True)
class VocabularyInput:
    vocabulary_id: int
    english: str
    japanese_romaji: str | None = None
    japanese_kana: str | None = None
    japanese_kanji: str | None = None


@dataclass(slots=True)
class GrammarInput:
    grammar_id: int
    explanation: str
    grammar_pattern: str | None = None
    example_romaji: str | None = None
    example_kana: str | None = None
    example_kanji: str | None = None
    example_english: str | None = None


@dataclass(slots=True)
class LessonCreateInput:
    lesson_level: str
    lesson_number: int
    title: str
    created_by: int | None = None
    updated_by: int | None = None
    conversations: list[ConversationInput | dict[str, Any]] = field(
        default_factory=list
    )
    vocabularies: list[VocabularyInput | dict[str, Any]] = field(
        default_factory=list,
    )
    grammars: list[GrammarInput | dict[str, Any]] = field(default_factory=list)


def _require_text(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} cannot be empty")
    return cleaned


def _validate_unique_ids(items: list[int], field_name: str) -> None:
    if len(items) != len(set(items)):
        raise ValueError(f"{field_name} values must be unique within a lesson")


def _normalize_conversations(
    items: list[ConversationInput | dict[str, Any]],
) -> list[ConversationInput]:
    normalized = []
    for item in items:
        if isinstance(item, ConversationInput):
            normalized.append(item)
        else:
            normalized.append(ConversationInput(**item))
    return normalized


def _normalize_vocabularies(
    items: list[VocabularyInput | dict[str, Any]],
) -> list[VocabularyInput]:
    normalized = []
    for item in items:
        if isinstance(item, VocabularyInput):
            normalized.append(item)
        else:
            normalized.append(VocabularyInput(**item))
    return normalized


def _normalize_grammars(
    items: list[GrammarInput | dict[str, Any]],
) -> list[GrammarInput]:
    normalized = []
    for item in items:
        if isinstance(item, GrammarInput):
            normalized.append(item)
        else:
            normalized.append(GrammarInput(**item))
    return normalized


def _normalize_payload(payload: LessonCreateInput) -> LessonCreateInput:
    payload.conversations = _normalize_conversations(payload.conversations)
    payload.vocabularies = _normalize_vocabularies(payload.vocabularies)
    payload.grammars = _normalize_grammars(payload.grammars)
    return payload


def _validate_lesson_input(payload: LessonCreateInput) -> None:
    _normalize_payload(payload)
    payload.lesson_level = _require_text(payload.lesson_level, "lesson_level")
    payload.title = _require_text(payload.title, "title")

    if payload.lesson_number <= 0:
        raise ValueError("lesson_number must be greater than 0")

    _validate_unique_ids(
        [item.line_number for item in payload.conversations],
        "line_number",
    )
    _validate_unique_ids(
        [item.vocabulary_id for item in payload.vocabularies],
        "vocabulary_id",
    )
    _validate_unique_ids(
        [item.grammar_id for item in payload.grammars],
        "grammar_id",
    )

    for item in payload.conversations:
        if item.line_number <= 0:
            raise ValueError("line_number must be greater than 0")
        item.english = _require_text(item.english, "conversation english")

    for item in payload.vocabularies:
        if item.vocabulary_id <= 0:
            raise ValueError("vocabulary_id must be greater than 0")
        item.english = _require_text(item.english, "vocabulary english")

    for item in payload.grammars:
        if item.grammar_id <= 0:
            raise ValueError("grammar_id must be greater than 0")
        item.explanation = _require_text(
            item.explanation,
            "grammar explanation",
        )


def create_lesson(payload: LessonCreateInput) -> Lesson:
    _validate_lesson_input(payload)

    with SessionLocal() as db:
        lesson = Lesson(
            lesson_level=payload.lesson_level,
            lesson_number=payload.lesson_number,
            title=payload.title,
            created_by=payload.created_by,
            updated_by=payload.updated_by,
        )
        db.add(lesson)

        try:
            db.flush()

            for item in payload.conversations:
                db.add(
                    Conversation(
                        lesson_id=lesson.id,
                        line_number=item.line_number,
                        speaker=item.speaker,
                        japanese_romaji=item.japanese_romaji,
                        japanese_kana=item.japanese_kana,
                        japanese_kanji=item.japanese_kanji,
                        english=item.english,
                        created_by=payload.created_by,
                        updated_by=payload.updated_by,
                    )
                )

            for item in payload.vocabularies:
                db.add(
                    Vocabulary(
                        lesson_id=lesson.id,
                        vocabulary_id=item.vocabulary_id,
                        japanese_romaji=item.japanese_romaji,
                        japanese_kana=item.japanese_kana,
                        japanese_kanji=item.japanese_kanji,
                        english=item.english,
                        created_by=payload.created_by,
                        updated_by=payload.updated_by,
                    )
                )

            for item in payload.grammars:
                db.add(
                    Grammar(
                        lesson_id=lesson.id,
                        grammar_id=item.grammar_id,
                        grammar_pattern=item.grammar_pattern,
                        explanation=item.explanation,
                        example_romaji=item.example_romaji,
                        example_kana=item.example_kana,
                        example_kanji=item.example_kanji,
                        example_english=item.example_english,
                        created_by=payload.created_by,
                        updated_by=payload.updated_by,
                    )
                )

            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise ValueError(
                "Lesson could not be created because of a duplicate lesson, "
                "conversation, vocabulary, or grammar identifier."
            ) from exc
        except Exception:
            db.rollback()
            raise

        db.refresh(lesson)
        return lesson


def create_lesson_from_inputs(
    *,
    lesson_level: str,
    lesson_number: int,
    title: str,
    created_by: int | None = None,
    updated_by: int | None = None,
    conversations: list[dict[str, Any]] | None = None,
    vocabularies: list[dict[str, Any]] | None = None,
    grammars: list[dict[str, Any]] | None = None,
) -> Lesson:
    return create_lesson(
        LessonCreateInput(
            lesson_level=lesson_level,
            lesson_number=lesson_number,
            title=title,
            created_by=created_by,
            updated_by=updated_by,
            conversations=conversations or [],
            vocabularies=vocabularies or [],
            grammars=grammars or [],
        )
    )
