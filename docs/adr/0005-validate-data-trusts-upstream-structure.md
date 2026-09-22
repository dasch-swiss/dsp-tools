---
status: accepted
date: 2026-09-22
---

# validate-data trusts XSD validation and dsp-tools' own value structuring

`validate-data` does not re-validate what upstream already checked: it assumes the input XML passed XSD
schema validation, and that `dsp-tools` itself built `Values` with the correct structure. If `dsp-tools`
were to start producing incorrectly structured `Values`, `validate-data` may not catch it and could emit
misleading validation results.

Enforced by: none (docs-only)
