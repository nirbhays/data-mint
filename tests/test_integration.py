"""Integration tests for the DataMint CLI."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from datamint.cli import main


runner = CliRunner()


class TestCLIQAPreset:
    """Integration tests for the qa preset."""

    def test_qa_builtin_sample(self) -> None:
        result = runner.invoke(main, ["generate", "--preset", "qa"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "question" in data[0]
        assert "answer" in data[0]
        assert "context" in data[0]
        assert "difficulty" in data[0]

    def test_qa_with_source_file(self, tmp_path: Path) -> None:
        src = tmp_path / "input.txt"
        src.write_text(
            "Rust is a systems programming language. "
            "It guarantees memory safety without a garbage collector. "
            "Cargo is the Rust package manager.",
            encoding="utf-8",
        )
        result = runner.invoke(
            main, ["generate", "--preset", "qa", "--source", str(src)]
        )
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) > 0

    def test_qa_count(self) -> None:
        result = runner.invoke(
            main, ["generate", "--preset", "qa", "--count", "2"]
        )
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 2

    def test_qa_output_file(self, tmp_path: Path) -> None:
        out = tmp_path / "out.json"
        result = runner.invoke(
            main,
            ["generate", "--preset", "qa", "--count", "2", "--output", str(out)],
        )
        assert result.exit_code == 0
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert len(data) == 2


class TestCLIAdversarialPreset:
    """Integration tests for the adversarial preset."""

    def test_adversarial_default(self) -> None:
        result = runner.invoke(main, ["generate", "--preset", "adversarial"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 20

    def test_adversarial_custom_count(self) -> None:
        result = runner.invoke(
            main, ["generate", "--preset", "adversarial", "--count", "5"]
        )
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 5

    def test_adversarial_categories_present(self) -> None:
        result = runner.invoke(
            main, ["generate", "--preset", "adversarial", "--count", "50", "--seed", "42"]
        )
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        categories = {item["category"] for item in data}
        assert len(categories) > 1  # multiple categories present


class TestCLITabularPreset:
    """Integration tests for the tabular preset."""

    def test_tabular_with_schema(self, tmp_path: Path) -> None:
        schema = {
            "columns": [
                {"name": "id", "type": "integer", "min": 1, "max": 100},
                {"name": "email", "type": "email"},
            ]
        }
        sf = tmp_path / "schema.json"
        sf.write_text(json.dumps(schema), encoding="utf-8")
        result = runner.invoke(
            main,
            ["generate", "--preset", "tabular", "--schema", str(sf), "--count", "10"],
        )
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 10
        assert "id" in data[0]
        assert "email" in data[0]

    def test_tabular_missing_schema_errors(self) -> None:
        result = runner.invoke(main, ["generate", "--preset", "tabular"])
        assert result.exit_code != 0


class TestOutputFormats:
    """Test JSON, JSONL, and CSV output formats."""

    def test_json_format(self) -> None:
        result = runner.invoke(
            main,
            ["generate", "--preset", "qa", "--count", "2", "--format", "json"],
        )
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)

    def test_jsonl_format(self) -> None:
        result = runner.invoke(
            main,
            ["generate", "--preset", "qa", "--count", "3", "--format", "jsonl"],
        )
        assert result.exit_code == 0
        lines = [ln for ln in result.stdout.strip().split("\n") if ln.strip()]
        assert len(lines) == 3
        for line in lines:
            obj = json.loads(line)
            assert "question" in obj

    def test_csv_format(self) -> None:
        result = runner.invoke(
            main,
            ["generate", "--preset", "qa", "--count", "2", "--format", "csv"],
        )
        assert result.exit_code == 0
        lines = result.stdout.strip().split("\n")
        # header + 2 data rows
        assert len(lines) >= 3
        assert "question" in lines[0]


class TestVersionFlag:
    """Test --version flag."""

    def test_version(self) -> None:
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
