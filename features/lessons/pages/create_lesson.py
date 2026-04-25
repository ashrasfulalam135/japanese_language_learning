import streamlit as st

from features.auth.services.session_service import (
    build_authenticator,
    load_auth_config,
    require_login,
    require_role,
)
from features.auth.services.user_service import get_user_id
from features.lessons.services.lesson_service import create_lesson_from_inputs


def build_conversation_inputs(count: int) -> list[dict[str, str | int | None]]:
    conversations = []
    for index in range(count):
        line_number = index + 1
        speaker_col, english_col = st.columns([1, 3])
        with speaker_col:
            speaker = st.text_input(
                "Speaker",
                key=f"conversation_speaker_{index}",
                placeholder="A",
            )
        with english_col:
            english = st.text_input(
                "English",
                key=f"conversation_english_{index}",
                placeholder="Nice to meet you.",
            )
        _, romaji_col = st.columns([1, 3])
        with romaji_col:
            japanese_romaji = st.text_input(
                "Romaji",
                key=f"conversation_romaji_{index}",
            )
        _, kana_col = st.columns([1, 3])
        with kana_col:
            japanese_kana = st.text_input(
                "Kana",
                key=f"conversation_kana_{index}",
            )
        _, kanji_col = st.columns([1, 3])
        with kanji_col:
            japanese_kanji = st.text_input(
                "Kanji",
                key=f"conversation_kanji_{index}",
            )

        conversations.append(
            {
                "line_number": line_number,
                "speaker": speaker or None,
                "english": english,
                "japanese_romaji": japanese_romaji or None,
                "japanese_kana": japanese_kana or None,
                "japanese_kanji": japanese_kanji or None,
            }
        )
        if index < count - 1:
            st.divider()

    return conversations


def build_vocabulary_inputs(count: int) -> list[dict[str, str | int | None]]:
    vocabularies = []
    for index in range(count):
        vocabulary_id = index + 1
        kana_col, kanji_col, romaji_col, english_col = st.columns(4)
        with kana_col:
            japanese_kana = st.text_input(
                "Kana",
                key=f"vocabulary_kana_{index}",
            )
        with kanji_col:
            japanese_kanji = st.text_input(
                "Kanji",
                key=f"vocabulary_kanji_{index}",
            )
        with romaji_col:
            japanese_romaji = st.text_input(
                "Romaji",
                key=f"vocabulary_romaji_{index}",
            )
        with english_col:
            english = st.text_input(
                "English",
                key=f"vocabulary_english_{index}",
                placeholder="I / me",
            )

        vocabularies.append(
            {
                "vocabulary_id": vocabulary_id,
                "english": english,
                "japanese_romaji": japanese_romaji or None,
                "japanese_kana": japanese_kana or None,
                "japanese_kanji": japanese_kanji or None,
            }
        )
        if index < count - 1:
            st.divider()

    return vocabularies


def build_grammar_inputs(count: int) -> list[dict[str, str | int | None]]:
    grammars = []
    for index in range(count):
        grammar_id = index + 1
        st.markdown(f"**Grammar {grammar_id}**")
        grammar_pattern = st.text_input(
            "Grammar pattern",
            key=f"grammar_pattern_{index}",
            placeholder="~ desu",
        )
        explanation = st.text_area(
            "Explanation",
            key=f"grammar_explanation_{index}",
            placeholder="Used for polite statements.",
        )
        example_kana = st.text_input(
            "Example kana",
            key=f"grammar_example_kana_{index}",
        )
        example_kanji = st.text_input(
            "Example kanji",
            key=f"grammar_example_kanji_{index}",
        )
        example_romaji = st.text_input(
            "Example romaji",
            key=f"grammar_example_romaji_{index}",
        )
        example_english = st.text_input(
            "Example english",
            key=f"grammar_example_english_{index}",
        )

        grammars.append(
            {
                "grammar_id": grammar_id,
                "grammar_pattern": grammar_pattern or None,
                "explanation": explanation,
                "example_romaji": example_romaji or None,
                "example_kana": example_kana or None,
                "example_kanji": example_kanji or None,
                "example_english": example_english or None,
            }
        )
        if index < count - 1:
            st.divider()

    return grammars


config = load_auth_config()
authenticator = build_authenticator(config)
require_login(authenticator, config)
require_role("admin")

st.title("Create Lesson")
lesson_caption = (
    "Create a lesson with conversation, " "vocabulary, and grammar content."
)
st.caption(lesson_caption)

user_id = get_user_id(st.session_state.get("username"))
if user_id is None:
    st.error("We could not identify the logged-in user.")
    st.stop()

st.subheader("Lesson Setup")
setup_col_1, setup_col_2, setup_col_3 = st.columns(3)
with setup_col_1:
    lesson_level = st.selectbox(
        "Lesson level",
        options=["N5", "N4", "N3", "N2", "N1"],
        index=0,
    )
with setup_col_2:
    lesson_number = st.number_input(
        "Lesson number",
        min_value=1,
        step=1,
        value=1,
    )
with setup_col_3:
    title = st.text_input(
        "Lesson title",
        placeholder="Self Introduction",
    )

count_col_1, count_col_2, count_col_3 = st.columns(3)
with count_col_1:
    conversation_count = st.number_input(
        "Conversation lines",
        min_value=1,
        max_value=20,
        step=1,
        value=2,
    )
with count_col_2:
    vocabulary_count = st.number_input(
        "Vocabularies",
        min_value=1,
        max_value=50,
        step=1,
        value=3,
    )
with count_col_3:
    grammar_count = st.number_input(
        "Grammars",
        min_value=1,
        max_value=20,
        step=1,
        value=2,
    )

with st.form("create_lesson_form", clear_on_submit=False):
    st.subheader("Conversation")
    conversations = build_conversation_inputs(int(conversation_count))

    st.subheader("Vocabularies")
    vocabularies = build_vocabulary_inputs(int(vocabulary_count))

    st.subheader("Grammars")
    grammars = build_grammar_inputs(int(grammar_count))

    submitted = st.form_submit_button("Save lesson", use_container_width=True)

if submitted:
    try:
        lesson = create_lesson_from_inputs(
            lesson_level=lesson_level,
            lesson_number=int(lesson_number),
            title=title,
            created_by=user_id,
            updated_by=user_id,
            conversations=conversations,
            vocabularies=vocabularies,
            grammars=grammars,
        )
    except ValueError as exc:
        st.error(str(exc))
    except Exception:
        st.error("Something went wrong while saving the lesson.")
    else:
        st.success(
            (
                f"Lesson {lesson.lesson_level}-{lesson.lesson_number} "
                "was created successfully."
            )
        )
