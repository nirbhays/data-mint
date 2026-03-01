# Changelog

All notable changes to DataMint will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-15

### Added

- QA pair generation from source text using templates
- Adversarial prompt generation across 4 categories (21 templates)
- Tabular data generation from JSON schema using Faker (11 column types)
- CLI with `generate` command supporting qa, adversarial, and tabular presets
- Output formats: JSON, JSONL, CSV
- Seed-based reproducibility for all generators
- Built-in sample text for zero-config demos
