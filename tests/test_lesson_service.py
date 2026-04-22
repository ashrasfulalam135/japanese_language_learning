from __future__ import annotations

import unittest
from unittest.mock import patch

from database.models import Conversation, Grammar, Lesson, Vocabulary
from features.lessons.services import lesson_service as service
from tests.test_helpers import create_test_session_local, seed_user


class LessonServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session_local = create_test_session_local()
        self.session_patcher = patch.object(
            service,
            "SessionLocal",
            self.session_local,
        )
        self.session_patcher.start()
        self.user_id = seed_user(
            self.session_local,
            username="author@example.com",
            role="admin",
        )

    def tearDown(self) -> None:
        self.session_patcher.stop()

    def test_create_lesson_persists_lesson_and_related_content(self) -> None:
        lesson = service.create_lesson_from_inputs(
            lesson_level="N5",
            lesson_number=1,
            title="Self Introduction",
            created_by=self.user_id,
            updated_by=self.user_id,
            conversations=[
                {
                    "line_number": 1,
                    "speaker": "A",
                    "english": "Nice to meet you.",
                    "japanese_romaji": "Hajimemashite.",
                },
                {
                    "line_number": 2,
                    "speaker": "B",
                    "english": "I am Yuki.",
                    "japanese_romaji": "Watashi wa Yuki desu.",
                },
            ],
            vocabularies=[
                {
                    "vocabulary_id": 1,
                    "english": "I / me",
                    "japanese_romaji": "watashi",
                },
                {
                    "vocabulary_id": 2,
                    "english": "student",
                    "japanese_romaji": "gakusei",
                },
            ],
            grammars=[
                {
                    "grammar_id": 1,
                    "grammar_pattern": "~ desu",
                    "explanation": "Used for polite statements.",
                    "example_english": "I am Yuki.",
                },
                {
                    "grammar_id": 2,
                    "grammar_pattern": "~ wa ~ desu",
                    "explanation": "Used to identify something politely.",
                    "example_english": "This is a book.",
                },
            ],
        )

        self.assertIsNotNone(lesson.id)

        with self.session_local() as db:
            self.assertEqual(db.query(Lesson).count(), 1)
            self.assertEqual(db.query(Conversation).count(), 2)
            self.assertEqual(db.query(Vocabulary).count(), 2)
            self.assertEqual(db.query(Grammar).count(), 2)

    def test_create_lesson_rejects_duplicate_conversation_line_numbers(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "line_number values must be unique",
        ):
            service.create_lesson_from_inputs(
                lesson_level="N5",
                lesson_number=1,
                title="Duplicate Lines",
                created_by=self.user_id,
                updated_by=self.user_id,
                conversations=[
                    {"line_number": 1, "english": "First line"},
                    {"line_number": 1, "english": "Second line"},
                ],
            )

    def test_create_lesson_rejects_duplicate_vocabulary_ids(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "vocabulary_id values must be unique",
        ):
            service.create_lesson_from_inputs(
                lesson_level="N5",
                lesson_number=1,
                title="Duplicate Vocabulary IDs",
                created_by=self.user_id,
                updated_by=self.user_id,
                vocabularies=[
                    {"vocabulary_id": 1, "english": "one"},
                    {"vocabulary_id": 1, "english": "two"},
                ],
            )

    def test_create_lesson_rejects_duplicate_grammar_ids(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "grammar_id values must be unique",
        ):
            service.create_lesson_from_inputs(
                lesson_level="N5",
                lesson_number=1,
                title="Duplicate Grammar IDs",
                created_by=self.user_id,
                updated_by=self.user_id,
                grammars=[
                    {"grammar_id": 1, "explanation": "First"},
                    {"grammar_id": 1, "explanation": "Second"},
                ],
            )

    def test_create_lesson_rejects_empty_required_text(self) -> None:
        with self.assertRaisesRegex(ValueError, "title cannot be empty"):
            service.create_lesson_from_inputs(
                lesson_level="N5",
                lesson_number=1,
                title="   ",
                created_by=self.user_id,
                updated_by=self.user_id,
            )

    def test_create_lesson_rejects_duplicate_lesson_level_and_number(
        self,
    ) -> None:
        service.create_lesson_from_inputs(
            lesson_level="N5",
            lesson_number=1,
            title="Lesson One",
            created_by=self.user_id,
            updated_by=self.user_id,
        )

        with self.assertRaisesRegex(
            ValueError,
            "Lesson could not be created because of a duplicate lesson",
        ):
            service.create_lesson_from_inputs(
                lesson_level="N5",
                lesson_number=1,
                title="Lesson One Again",
                created_by=self.user_id,
                updated_by=self.user_id,
            )


if __name__ == "__main__":
    unittest.main()
