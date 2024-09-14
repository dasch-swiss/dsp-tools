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
    -v $PWD:/workdir ghcr.io/igorshubovych/markdownlint-cli:latest \
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


# Run the legacy end-to-end tests (needs a running stack)
[no-exit-message]
legacy-e2e-tests *FLAGS:
    uv run pytest test/legacy_e2e/ {{FLAGS}}


# Calculate the post-release number and write it into pyproject.toml (used for dev-releases)
[no-exit-message]
bump-version:
    # get current version, append ".postN" (N=no. of commits since last release), write back into pyproject.toml
    LATEST_TAG=$(git describe --tags --abbrev=0)          # get the latest release tag from git history (e.g. "v9.0.2")
    COMMIT_CNT=$(git rev-list --count main ^$LATEST_TAG)  # get the number of commits since the last release (e.g. "5")
    if [ $COMMIT_CNT -eq 0 ]; then exit 0; fi             # if this CI run was triggered by a release, do nothing
    COMMIT_CNT=$((COMMIT_CNT - 1))                        # e.g. 5 -> 4 (N in ".postN" is zero-based)
    NEW_VERSION=${LATEST_TAG:1}.post$COMMIT_CNT           # e.g. "9.0.2.post4" (no leading v in pyproject.toml)
    OLD_TOML_LINE_RGX="version ?= ?\"${LATEST_TAG:1}\""   # e.g. 'version ?= ?"9.0.2"'
    sed -E -i "" "1,20s/$OLD_TOML_LINE_RGX/version = \"$NEW_VERSION\"/g" pyproject.toml  # write back into pyproject.toml


# Remove artifact files
[no-exit-message]
clean:
    rm -rf ./**/*.pyc
    rm -rf ./**/__pycache__
    rm -rf ./**/.pytest_cache
    rm -rf ./**/.mypy_cache
    rm -rf ./*id2iri_mapping*.json
    rm -f warnings.log
    rm -rf testdata/e2e/tmp-dsp-ingest/
    rm -rf testdata/e2e/images/
    rm -f mapping-????.csv
