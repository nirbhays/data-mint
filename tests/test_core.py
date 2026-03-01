"""Unit tests for datamint.core generators."""

from __future__ import annotations

import pytest

from datamint.core import (
    AdversarialCategory,
    AdversarialGenerator,
    AdversarialPrompt,
    Difficulty,
    QAGenerator,
    QAPair,
    Severity,
    TabularGenerator,
    TabularSchema,
)


# ── QAGenerator ──────────────────────────────────────────────────────────


class TestQAGenerator:
    """Tests for QAGenerator."""

    def test_generates_qa_pairs_from_sample_text(self) -> None:
        gen = QAGenerator(seed=42)
        pairs = gen.generate()
        assert len(pairs) > 0
        for pair in pairs:
            assert isinstance(pair, QAPair)
            assert pair.question
            assert pair.answer
            assert pair.context
            assert pair.difficulty in Difficulty

    def test_generates_from_custom_text(self) -> None:
        text = (
            "Python is a programming language. It is widely used for web development. "
            "Django and Flask are popular Python web frameworks."
        )
        gen = QAGenerator(seed=0)
        pairs = gen.generate(text=text)
        assert len(pairs) > 0
        # All contexts should come from the provided text
        for pair in pairs:
            # Context chunks are derived from the source text
            assert any(word in pair.context for word in ["Python", "Django", "Flask"])

    def test_count_limits_output(self) -> None:
        gen = QAGenerator(seed=1)
        pairs = gen.generate(count=3)
        assert len(pairs) == 3

    def test_empty_input_returns_empty(self) -> None:
        gen = QAGenerator()
        assert gen.generate(text="") == []

    def test_single_sentence(self) -> None:
        gen = QAGenerator(seed=7)
        pairs = gen.generate(text="The quick brown fox jumps over the lazy dog.")
        assert len(pairs) > 0
        assert pairs[0].context.startswith("The quick")

    def test_reproducibility_with_seed(self) -> None:
        pairs_a = QAGenerator(seed=99).generate(count=5)
        pairs_b = QAGenerator(seed=99).generate(count=5)
        for a, b in zip(pairs_a, pairs_b):
            assert a.question == b.question
            assert a.answer == b.answer

    def test_whitespace_only_input(self) -> None:
        gen = QAGenerator()
        assert gen.generate(text="   \n\t  ") == []


# ── AdversarialGenerator ─────────────────────────────────────────────────


class TestAdversarialGenerator:
    """Tests for AdversarialGenerator."""

    def test_generates_default_count(self) -> None:
        gen = AdversarialGenerator(seed=42)
        prompts = gen.generate()
        assert len(prompts) == 20

    def test_correct_categories(self) -> None:
        gen = AdversarialGenerator(seed=42)
        prompts = gen.generate(count=50)
        categories_seen = {p.category for p in prompts}
        # With all categories enabled we should see all of them
        assert categories_seen == set(AdversarialCategory)

    def test_filter_by_category(self) -> None:
        gen = AdversarialGenerator(
            categories=[AdversarialCategory.JAILBREAK], seed=0
        )
        prompts = gen.generate(count=5)
        assert len(prompts) == 5
        for p in prompts:
            assert p.category == AdversarialCategory.JAILBREAK

    def test_severity_values(self) -> None:
        gen = AdversarialGenerator(seed=42)
        for p in gen.generate(count=30):
            assert p.severity in Severity

    def test_prompt_text_not_empty(self) -> None:
        gen = AdversarialGenerator(seed=0)
        for p in gen.generate(count=10):
            assert isinstance(p, AdversarialPrompt)
            assert len(p.text) > 10

    def test_encoding_attack_payloads_filled(self) -> None:
        gen = AdversarialGenerator(
            categories=[AdversarialCategory.ENCODING_ATTACK], seed=5
        )
        prompts = gen.generate(count=5)
        for p in prompts:
            # No unfilled placeholders
            assert "{payload}" not in p.text

    def test_pii_names_filled(self) -> None:
        gen = AdversarialGenerator(
            categories=[AdversarialCategory.PII_EXTRACTION], seed=3
        )
        prompts = gen.generate(count=5)
        for p in prompts:
            assert "{name}" not in p.text


# ── TabularGenerator ─────────────────────────────────────────────────────


class TestTabularGenerator:
    """Tests for TabularGenerator."""

    SCHEMA_DICT = {
        "columns": [
            {"name": "user_id", "type": "integer", "min": 1, "max": 10000},
            {"name": "email", "type": "email"},
            {"name": "name", "type": "name"},
            {"name": "score", "type": "float", "min": 0.0, "max": 1.0},
        ]
    }

    def test_generates_correct_number_of_rows(self) -> None:
        gen = TabularGenerator(seed=42)
        rows = gen.generate(schema=self.SCHEMA_DICT, count=50)
        assert len(rows) == 50

    def test_correct_columns(self) -> None:
        gen = TabularGenerator(seed=42)
        rows = gen.generate(schema=self.SCHEMA_DICT, count=5)
        expected_keys = {"user_id", "email", "name", "score"}
        for row in rows:
            assert set(row.keys()) == expected_keys

    def test_integer_range(self) -> None:
        gen = TabularGenerator(seed=42)
        rows = gen.generate(schema=self.SCHEMA_DICT, count=100)
        for row in rows:
            assert 1 <= row["user_id"] <= 10000

    def test_float_range(self) -> None:
        gen = TabularGenerator(seed=42)
        rows = gen.generate(schema=self.SCHEMA_DICT, count=100)
        for row in rows:
            assert 0.0 <= row["score"] <= 1.0

    def test_email_format(self) -> None:
        gen = TabularGenerator(seed=42)
        rows = gen.generate(schema=self.SCHEMA_DICT, count=10)
        for row in rows:
            assert "@" in row["email"]

    def test_empty_schema_returns_empty(self) -> None:
        gen = TabularGenerator()
        rows = gen.generate(schema={"columns": []}, count=10)
        assert rows == []

    def test_pydantic_schema_object(self) -> None:
        schema = TabularSchema.model_validate(self.SCHEMA_DICT)
        gen = TabularGenerator(seed=42)
        rows = gen.generate(schema=schema, count=5)
        assert len(rows) == 5

    def test_nullable_column(self) -> None:
        schema = {
            "columns": [
                {
                    "name": "optional_field",
                    "type": "string",
                    "nullable": True,
                    "null_probability": 1.0,
                }
            ]
        }
        gen = TabularGenerator(seed=42)
        rows = gen.generate(schema=schema, count=10)
        for row in rows:
            assert row["optional_field"] is None

    def test_choices_override(self) -> None:
        schema = {
            "columns": [
                {"name": "color", "type": "string", "choices": ["red", "green", "blue"]}
            ]
        }
        gen = TabularGenerator(seed=42)
        rows = gen.generate(schema=schema, count=20)
        for row in rows:
            assert row["color"] in ["red", "green", "blue"]

    def test_boolean_column(self) -> None:
        schema = {"columns": [{"name": "flag", "type": "boolean"}]}
        gen = TabularGenerator(seed=42)
        rows = gen.generate(schema=schema, count=20)
        for row in rows:
            assert isinstance(row["flag"], bool)
