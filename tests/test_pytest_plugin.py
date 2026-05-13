"""Tests for the DataMint pytest fixtures."""

from __future__ import annotations

from datamint.core import AdversarialPrompt, QAPair


def test_synthetic_qa_dataset_fixture(synthetic_qa_dataset: list[QAPair]) -> None:
    assert len(synthetic_qa_dataset) == 5
    assert all(isinstance(pair, QAPair) for pair in synthetic_qa_dataset)
    assert all(pair.question and pair.answer for pair in synthetic_qa_dataset)


def test_adversarial_prompts_fixture(adversarial_prompts: list[AdversarialPrompt]) -> None:
    assert len(adversarial_prompts) == 5
    assert all(isinstance(prompt, AdversarialPrompt) for prompt in adversarial_prompts)
    assert all(prompt.text for prompt in adversarial_prompts)

