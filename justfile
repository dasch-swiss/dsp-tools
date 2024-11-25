# List all recipes
default:
    @just --list


# Run the ruff linter to detect bad Python coding habits
[no-exit-message]
ruff-check *FLAGS:
    uv run ruff check . --ignore=A002,D101,D102,PLR0913,PLR2004 {{FLAGS}}


# Run the ruff linter, with an output format suitable for GitHub runners
[no-exit-message]
ruff-check-github:
    uv run just ruff-check --output-format=github


# Check the formatting of the Python files
[no-exit-message]
ruff-format-check:
    uv run ruff format --check .


# Check the type annotations in Python files for correctness
[no-exit-message]
mypy:
    uv run mypy .


# Check completeness and correctness of python docstrings
[no-exit-message]
darglint:
    find . -name "*.py" \
    -not -path "./src/dsp_tools/commands/project/models/*" \
    -not -path "./.git/*" \
    -not -path "./.venv/*" \
    | xargs uv run darglint -v 2\


# Check that there are no dead links in the docs
[no-exit-message]
check-links:
    markdown-link-validator ./docs -i ./assets/.+


# Check the docs for ambiguous Markdown syntax that could be wrongly rendered
[no-exit-message]
markdownlint:
    docker run \
    -v $PWD:/workdir ghcr.io/igorshubovych/markdownlint-cli:v0.42.0 \
    --config .markdownlint.yml \
    --ignore CHANGELOG.md "**/*.md"


# Run the unit tests
[no-exit-message]
unittests *FLAGS:
    uv run pytest test/unittests/ {{FLAGS}}


# Run the integration tests
[no-exit-message]
integration-tests *FLAGS:
    uv run pytest test/integration/ {{FLAGS}}


# Run the end-to-end tests (with testcontainers)
[no-exit-message]
e2e-tests *FLAGS:
    uv run pytest test/e2e/ {{FLAGS}}


# Run the end-to-end tests for the validate-data command (with testcontainers)
[no-exit-message]
e2e-validate-data-tests *FLAGS:
    uv run pytest test/e2e_validate_data/ {{FLAGS}}


# Run the legacy end-to-end tests (needs a running stack)
[no-exit-message]
legacy-e2e-tests *FLAGS:
    uv run pytest test/legacy_e2e/ {{FLAGS}}


# Remove artifact files
[no-exit-message]
clean:
    find . -name "*.pyc" -exec rm -rf {} \;
    find . -name .__pycache__ -exec rm -rf {} \;
    find . -name .ruff_cache -exec rm -rf {} \;
    find . -name .pytest_cache -exec rm -rf {} \;
    find . -name .mypy_cache -exec rm -rf {} \;
    rm -rf *id2iri_mapping*.json
    rm -f warnings.log
    rm -rf testdata/e2e/tmp-dsp-ingest/
    rm -rf testdata/e2e/tmp-dsp-sipi/
    rm -rf testdata/e2e/ingest-db/
    rm -rf testdata/e2e/images/
    rm -f mapping-????.csv
