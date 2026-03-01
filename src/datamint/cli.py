"""DataMint CLI - generate synthetic datasets from the command line.

Usage examples::

    datamint generate --preset qa
    datamint generate --preset qa --source notes.txt --output qa.json
    datamint generate --preset adversarial --count 20 --format jsonl
    datamint generate --preset tabular --schema schema.json --count 500
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any

import click

from datamint import __version__
from datamint.core import (
    AdversarialGenerator,
    QAGenerator,
    TabularGenerator,
    TabularSchema,
)


def _log(message: str) -> None:
    """Write an informational message to stderr so it never pollutes data output."""
    click.echo(message, err=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _serialize(records: list[dict[str, Any]], fmt: str) -> str:
    """Serialize a list of dicts to the requested format string."""
    if fmt == "json":
        return json.dumps(records, indent=2, ensure_ascii=False, default=str)

    if fmt == "jsonl":
        lines = [json.dumps(r, ensure_ascii=False, default=str) for r in records]
        return "\n".join(lines) + "\n"

    if fmt == "csv":
        if not records:
            return ""
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
        return buf.getvalue()

    raise click.BadParameter(f"Unknown format: {fmt}")


def _write_output(text: str, output: str | None) -> None:
    """Write *text* to *output* file or stdout."""
    if output:
        Path(output).write_text(text, encoding="utf-8")
        _log(f"Output written to {output}")
    else:
        click.echo(text)


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------

@click.group()
@click.version_option(version=__version__, prog_name="datamint")
def main() -> None:
    """DataMint -- synthetic evaluation data for LLM testing."""


# ---------------------------------------------------------------------------
# generate command
# ---------------------------------------------------------------------------

@main.command()
@click.option(
    "--preset",
    type=click.Choice(["qa", "adversarial", "tabular"], case_sensitive=False),
    required=True,
    help="Generation preset to use.",
)
@click.option(
    "--source",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Source text file (for qa preset).",
)
@click.option(
    "--schema",
    "schema_file",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="JSON schema file (for tabular preset).",
)
@click.option(
    "--count",
    type=int,
    default=None,
    help="Number of items to generate.",
)
@click.option(
    "--output",
    type=click.Path(dir_okay=False),
    default=None,
    help="Output file path. Defaults to stdout.",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["json", "jsonl", "csv"], case_sensitive=False),
    default="json",
    show_default=True,
    help="Output format.",
)
@click.option("--seed", type=int, default=None, help="Random seed for reproducibility.")
def generate(
    preset: str,
    source: str | None,
    schema_file: str | None,
    count: int | None,
    output: str | None,
    fmt: str,
    seed: int | None,
) -> None:
    """Generate synthetic data using a chosen preset."""
    records: list[dict[str, Any]]

    if preset == "qa":
        text: str | None = None
        if source:
            text = Path(source).read_text(encoding="utf-8")
            _log(f"Read source: {source}")
        else:
            _log("Using built-in sample text")

        gen = QAGenerator(seed=seed)
        pairs = gen.generate(text=text, count=count)
        records = [p.model_dump() for p in pairs]
        _log(f"Generated {len(records)} QA pair(s)")

    elif preset == "adversarial":
        effective_count = count if count is not None else 20
        gen_adv = AdversarialGenerator(seed=seed)
        prompts = gen_adv.generate(count=effective_count)
        records = [p.model_dump() for p in prompts]
        _log(f"Generated {len(records)} adversarial prompt(s)")

    elif preset == "tabular":
        if not schema_file:
            raise click.UsageError("--schema is required for the tabular preset.")
        raw = json.loads(Path(schema_file).read_text(encoding="utf-8"))
        schema = TabularSchema.model_validate(raw)
        effective_count = count if count is not None else 100
        gen_tab = TabularGenerator(seed=seed)
        records = gen_tab.generate(schema=schema, count=effective_count)
        _log(f"Generated {len(records)} row(s)")

    else:
        raise click.UsageError(f"Unknown preset: {preset}")

    serialized = _serialize(records, fmt)
    _write_output(serialized, output)


if __name__ == "__main__":
    main()
