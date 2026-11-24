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
    uv sync --all-packages


# Run all linters in parallel (see https://just.systems/man/en/running-tasks-in-parallel.html)
[no-exit-message]
lint: uv-sync
    #!/usr/bin/env -S parallel --shebang --ungroup --jobs {{ num_cpus() }}
    just ruff-check
    just ruff-format-check
    just yamlfmt-check
    just yamllint
    just markdownlint
    just mypy
    just vulture
    just check-xmllib-docstring-links
    just check-schema-copy


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
    uv run ruff check . --ignore=D101,D102,PLR2004 {{FLAGS}}


# Check the formatting of the Python files
[no-exit-message]
ruff-format-check:
    uv run ruff format --check .


# Check type annotations of all packages
[no-exit-message]
mypy: mypy-dsp-tools mypy-vre mypy-scripts


# Check type annotations of dsp-tools. Autostart mypy daemon if necessary, autoshutdown daemon after 1 day of inactivity
[no-exit-message]
[working-directory: 'packages/dsp-tools']
mypy-dsp-tools:
    uv run dmypy run --timeout 86400 -- .


# Check that there are no dead links in the docs (configured in lychee.toml)
[no-exit-message]
check-links:
    lychee ./packages/dsp-tools/docs


# Check type annotations of dsp-vre
[no-exit-message]
[working-directory: 'packages/dsp-vre']
mypy-vre:
    uv run dmypy run --timeout 86400 -- .


# Check type annotations of the repository tooling in scripts/
[no-exit-message]
mypy-scripts:
    uv run dmypy run --timeout 86400 -- scripts


# Check that docstring links in xmllib are valid
[no-exit-message]
check-xmllib-docstring-links:
    uv run python scripts/validate_xmllib_docstring_links.py


# Check the docs for ambiguous Markdown syntax that could be wrongly rendered
[no-exit-message]
markdownlint:
    docker run \
    --rm \
    -v $PWD:/workdir \
    ghcr.io/igorshubovych/markdownlint-cli:v0.49.1 \
    --config .markdownlint.yml \
    --ignore "**/CHANGELOG.md" \
    "**/*.md"


# Run vulture, dead code analysis
[no-exit-message]
[working-directory: 'packages/dsp-tools']
vulture:
    uv run vulture


# Run the unit tests
[no-exit-message]
[working-directory: 'packages/dsp-tools']
unittests *FLAGS:
    uv run pytest test/unittests/ {{FLAGS}}


# Run the unit tests of dsp-vre
[no-exit-message]
[working-directory: 'packages/dsp-vre']
vre-unittests *FLAGS:
    uv run pytest test/unittests/ {{FLAGS}}


# Run the integration tests
[no-exit-message]
[working-directory: 'packages/dsp-tools']
integration-tests *FLAGS:
    uv run pytest test/integration/ {{FLAGS}}


# Run all the end-to-end tests with testcontainers
[no-exit-message]
[working-directory: 'packages/dsp-tools']
e2e-tests *FLAGS:
    # "--dist=loadfile" guarantees that all tests in a file are executed by the same worker
    # "-n=4" runs 4 workers in parallel. This is a tradeoff in order to not overload Docker Desktop.
    # see https://pytest-xdist.readthedocs.io/en/latest/distribution.html
    uv run pytest -n=4 --dist=loadfile test/e2e/ {{FLAGS}}


# Run the end-to-end tests for the ingest-xmlupload command (with testcontainers)
[no-exit-message]
[working-directory: 'packages/dsp-tools']
e2e-test-ingest-xmlupload *FLAGS:
    uv run pytest test/e2e/commands/ingest_xmlupload/ {{FLAGS}}


# Run the end-to-end tests for the validate-data command (with testcontainers)
[no-exit-message]
[working-directory: 'packages/dsp-tools']
e2e-test-validate-data *FLAGS:
    # "--dist=loadfile" guarantees that all tests in a file are executed by the same worker
    # see https://pytest-xdist.readthedocs.io/en/latest/distribution.html
    uv run pytest -n=4 --dist=loadfile test/e2e/commands/validate_data/ {{FLAGS}}


# Run the end-to-end tests for the xmlupload command (with testcontainers)
[no-exit-message]
[working-directory: 'packages/dsp-tools']
e2e-test-xmlupload *FLAGS:
    uv run pytest test/e2e/commands/xmlupload/ {{FLAGS}}


# Run the end-to-end tests for the create and get command (with testcontainers)
[no-exit-message]
[working-directory: 'packages/dsp-tools']
e2e-test-project *FLAGS:
    uv run pytest test/e2e/commands/project/ {{FLAGS}}


# Run the end-to-end tests for the mapping command (with testcontainers)
[no-exit-message]
[working-directory: 'packages/dsp-tools']
e2e-test-mapping *FLAGS:
    uv run pytest test/e2e/commands/mapping/ {{FLAGS}}


# Run the end-to-end tests for the create, get and xmlupload command (with testcontainers)
[no-exit-message]
[working-directory: 'packages/dsp-tools']
e2e-test-create-get-xmlupload *FLAGS:
    uv run pytest test/e2e/commands/test_create_get_xmlupload.py {{FLAGS}}


# Run the legacy end-to-end tests (needs a running stack)
[no-exit-message]
[working-directory: 'packages/dsp-tools']
legacy-e2e-tests *FLAGS:
    uv run pytest test/legacy_e2e/ {{FLAGS}}


# Run pytest for dsp-tools on the given paths, which can be relative to the repository root or to packages/dsp-tools/
[no-exit-message]
[positional-arguments]
dsp-tools-pytest *ARGS:
    just _package-pytest dsp-tools "$@"


# Run pytest for dsp-vre on the given paths, which can be relative to the repository root or to packages/dsp-vre/
[no-exit-message]
[positional-arguments]
vre-pytest *ARGS:
    just _package-pytest dsp-vre "$@"


# Run pytest in packages/PACKAGE/, with the paths in ARGS relative to that folder
[no-exit-message]
[positional-arguments]
_package-pytest PACKAGE *ARGS:
    #!/usr/bin/env bash
    set -euo pipefail
    shift  # the first positional argument is PACKAGE
    args=()
    for arg in "$@"; do args+=("${arg#packages/{{PACKAGE}}/}"); done
    cd "packages/{{PACKAGE}}"
    uv run pytest ${args[@]+"${args[@]}"}


# Run the tests of the repository tooling in scripts/
[no-exit-message]
scripts-tests *FLAGS:
    uv run pytest scripts/test/ {{FLAGS}}


schema_source := "packages/dsp-tools/src/dsp_tools/resources/schema/"
schema_copy := "src/dsp_tools/resources/schema/"


# Check that the copy of the schema files at the old URL path equals the packaged schema files
[no-exit-message]
check-schema-copy:
    #!/usr/bin/env bash
    set -euo pipefail
    if ! diff -r {{schema_copy}} {{schema_source}} --exclude=README.md; then
        echo "The copy in {{schema_copy}} differs from {{schema_source}}. Edit only the source, then run: just sync-schema-copy"
        exit 1
    fi


# Overwrite the copy of the schema files at the old URL path with the packaged schema files
[no-exit-message]
sync-schema-copy:
    rsync -a --delete --exclude=README.md {{schema_source}} {{schema_copy}}


# Remove artifact files
[no-exit-message]
clean:
    -find . -name "*.pyc" -exec rm -rf {} +
    -find . -name __pycache__ -exec rm -rf {} +
    -find . -name .ruff_cache -exec rm -rf {} +
    -find . -name .pytest_cache -exec rm -rf {} +
    -find . -name .mypy_cache -exec rm -rf {} +
    -cd packages/dsp-tools && uv run dmypy restart
    -cd packages/dsp-vre && uv run dmypy restart
    -rm -rf ./*id2iri_mapping*.json ./packages/dsp-tools/*id2iri_mapping*.json
    -rm -rf ./*id2iri_[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]*.json ./packages/dsp-tools/*id2iri_[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]*.json
    -rm -f ./warnings.log
    -rm -f ./packages/dsp-tools/warnings.log
    -rm -rf ./packages/dsp-tools/testdata/e2e/tmp-dsp-ingest/
    -rm -rf ./packages/dsp-tools/testdata/e2e/tmp-dsp-sipi/
    -rm -rf ./packages/dsp-tools/testdata/e2e/ingest-db/
    -rm -rf ./packages/dsp-tools/testdata/e2e/images/
    -rm -rf ./site
    -rm -f ./mapping-????.csv ./packages/dsp-tools/mapping-????.csv
