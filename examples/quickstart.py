#!/usr/bin/env python3
"""DataMint quickstart example -- library API usage.

Run this script directly:

    python examples/quickstart.py

It demonstrates each of the three generators and prints the results using
Rich tables.
"""

from __future__ import annotations

import json

from rich.console import Console
from rich.table import Table

from datamint.core import (
    AdversarialCategory,
    AdversarialGenerator,
    QAGenerator,
    TabularGenerator,
)

console = Console()


def demo_qa_generator() -> None:
    """Generate QA pairs from a short text passage."""
    console.rule("[bold cyan]QA Generator Demo[/bold cyan]")

    text = (
        "Natural language processing enables computers to understand human language. "
        "Tokenization breaks text into smaller units called tokens. "
        "Named entity recognition identifies real-world objects in text such as "
        "people, organizations, and locations. "
        "Sentiment analysis determines whether a piece of text expresses a "
        "positive, negative, or neutral opinion."
    )

    gen = QAGenerator(seed=42)
    pairs = gen.generate(text=text, count=4)

    table = Table(title="Generated QA Pairs")
    table.add_column("Question", style="cyan", max_width=50)
    table.add_column("Answer", style="green", max_width=50)
    table.add_column("Difficulty", style="magenta")

    for pair in pairs:
        table.add_row(pair.question, pair.answer[:80] + "...", pair.difficulty.value)

    console.print(table)
    console.print()


def demo_adversarial_generator() -> None:
    """Generate adversarial prompts for red-teaming."""
    console.rule("[bold red]Adversarial Generator Demo[/bold red]")

    gen = AdversarialGenerator(
        categories=[AdversarialCategory.PROMPT_INJECTION, AdversarialCategory.JAILBREAK],
        seed=7,
    )
    prompts = gen.generate(count=6)

    table = Table(title="Adversarial Prompts")
    table.add_column("Category", style="yellow")
    table.add_column("Severity", style="red")
    table.add_column("Prompt", style="white", max_width=70)

    for p in prompts:
        table.add_row(p.category.value, p.severity.value, p.text[:90])

    console.print(table)
    console.print()


def demo_tabular_generator() -> None:
    """Generate synthetic tabular data from a schema."""
    console.rule("[bold green]Tabular Generator Demo[/bold green]")

    schema = {
        "columns": [
            {"name": "user_id", "type": "integer", "min": 1, "max": 10000},
            {"name": "email", "type": "email"},
            {"name": "name", "type": "name"},
            {"name": "score", "type": "float", "min": 0.0, "max": 1.0},
            {"name": "active", "type": "boolean"},
        ]
    }

    gen = TabularGenerator(seed=42)
    rows = gen.generate(schema=schema, count=8)

    table = Table(title="Synthetic Users")
    for col in schema["columns"]:
        table.add_column(col["name"])

    for row in rows:
        table.add_row(*[str(v) for v in row.values()])

    console.print(table)
    console.print()

    # Also show raw JSON for the first two rows
    console.print("[dim]Raw JSON (first 2 rows):[/dim]")
    console.print(json.dumps(rows[:2], indent=2, default=str))


if __name__ == "__main__":
    console.print()
    console.print("[bold]DataMint Quickstart[/bold]", justify="center")
    console.print()

    demo_qa_generator()
    demo_adversarial_generator()
    demo_tabular_generator()

    console.print()
    console.rule("[bold]Done[/bold]")
