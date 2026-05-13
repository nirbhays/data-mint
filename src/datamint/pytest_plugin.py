"""Pytest fixtures for DataMint-generated test data."""

from __future__ import annotations

import pytest

from datamint.core import AdversarialGenerator, AdversarialPrompt, QAGenerator, QAPair


@pytest.fixture
def synthetic_qa_dataset() -> list[QAPair]:
    """Return a deterministic small QA dataset for tests."""
    return QAGenerator(seed=42).generate(count=5)


@pytest.fixture
def adversarial_prompts() -> list[AdversarialPrompt]:
    """Return deterministic adversarial prompts for red-team tests."""
    return AdversarialGenerator(seed=42).generate(count=5)

