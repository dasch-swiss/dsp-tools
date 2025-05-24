# List all recipes
default:
    @just --list


# Run all autoformattings
[no-exit-message]
format:
    ruff format .
    just ruff-check --fix
    yamlfmt .


# Rebuild the virtual environment (must be run before `just lint`, otherwise several tools will try to do it in parallel)
[no-exit-message]
uv-sync:
    uv sync


# Run all linters in parallel (see https://just.systems/man/en/running-tasks-in-parallel.html)
[no-exit-message]
lint: uv-sync
    #!/usr/bin/env -S parallel --shebang --ungroup --jobs {{ num_cpus() }}
    just ruff-check
    just ruff-format-check
    just yamlfmt-check
    just yamllint
    just markdownlint
    just darglint
    just mypy
    uv run scripts/markdown_link_validator.py


# Detect anti-patterns in YAML files
[no-exit-message]
yamllint:
    uv run yamllint .


# Check the formatting of YAML files
[no-exit-message]
yamlfmt-check:
    yamlfmt -lint .


# Run the ruff linter to detect bad Python coding habits
[no-exit-message]
ruff-check *FLAGS:
    uv run ruff check . --ignore=A002,D101,D102,PLR0913,PLR2004 {{FLAGS}}


# Check the formatting of the Python files
[no-exit-message]
ruff-format-check:
    uv run ruff format --check .


# Check type annotations. Autostart mypy daemon if necessary, autoshutdown daemon after 1 day of inactivity
[no-exit-message]
mypy:
    uv run dmypy run --timeout 86400 -- .


# Check completeness and correctness of python docstrings
[no-exit-message]
darglint:
    uv run darglint -v 2 ./src/dsp_tools/xmllib/**/*.py


# Check that there are no dead links in the docs
[no-exit-message]
check-links:
    markdown-link-validator ./docs -i ./assets/.+


# Check the docs for ambiguous Markdown syntax that could be wrongly rendered
[no-exit-message]
markdownlint:
    docker run \
    --rm \
    -v $PWD:/workdir \
    ghcr.io/igorshubovych/markdownlint-cli:v0.45.0 \
    --config .markdownlint.yml \
    --ignore CHANGELOG.md \
    --ignore README.md \
    "**/*.md"

# Run vulture, dead code analysis
[no-exit-message]
vulture:
    uv run vulture

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
    # "--dist=loadfile" guarantees that all tests in a file are executed by the same worker
    # see https://pytest-xdist.readthedocs.io/en/latest/distribution.html
    uv run pytest -n=auto --dist=loadfile test/e2e/ {{FLAGS}}


# Run the legacy end-to-end tests (needs a running stack)
[no-exit-message]
legacy-e2e-tests *FLAGS:
    uv run pytest test/legacy_e2e/ {{FLAGS}}


# Remove artifact files
[no-exit-message]
clean:
    -find . -name "*.pyc" -exec rm -rf {} +
    -find . -name __pycache__ -exec rm -rf {} +
    -find . -name .ruff_cache -exec rm -rf {} +
    -find . -name .pytest_cache -exec rm -rf {} +
    -find . -name .mypy_cache -exec rm -rf {} +
    -uv run dmypy restart
    -rm -rf ./*id2iri_mapping*.json
    -rm -rf ./*id2iri_[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]*.json
    -rm -f ./warnings.log
    -rm -rf ./testdata/e2e/tmp-dsp-ingest/
    -rm -rf ./testdata/e2e/tmp-dsp-sipi/
    -rm -rf ./testdata/e2e/ingest-db/
    -rm -rf ./testdata/e2e/images/
    -rm -rf ./site
    -rm -f ./mapping-????.csv
