# List all recipes
default:
    @just --list

# Run the ruff linter to detect bad Python coding habits
ruff-check *FLAGS:
    uv run ruff check . --ignore=A002,D101,D102,PLR0913,PLR2004 {{FLAGS}}

# Run the ruff linter, with an output format suitable for GitHub runners
ruff-check-github:
    uv run just ruff-check --output-format=github

# Check the formatting of the Python files
ruff-format-check:
    uv run ruff format --check .

# Check the type annotations in Python files for correctness
mypy:
    uv run mypy .

# Check completeness and correctness of python docstrings
darglint:
    find . -name "*.py" \
    -not -path "./src/dsp_tools/commands/project/models/*" \
    -not -path "./.git/*" \
    -not -path "./.venv/*" \
    | xargs uv run darglint -v 2\

# Check that there are no dead links in the docs
check-links:
    markdown-link-validator ./docs -i ./assets/.+

# Check the docs for ambiguous Markdown syntax that could be wrongly rendered
markdownlint:
    docker run \
    -v $PWD:/workdir ghcr.io/igorshubovych/markdownlint-cli:latest \
    --config .markdownlint.yml \
    --ignore CHANGELOG.md "**/*.md"

# Run the unit tests
unittests *FLAGS:
    uv run pytest test/unittests/ {{FLAGS}}

# Run the integration tests
integration-tests *FLAGS:
    uv run pytest test/integration/ {{FLAGS}}

# Run the end-to-end tests (with testcontainers)
e2e-tests *FLAGS:
    uv run pytest test/e2e/ {{FLAGS}}

# Run the legacy end-to-end tests (needs a running stack)
legacy-e2e-tests *FLAGS:
    uv run pytest test/legacy_e2e/ {{FLAGS}}

# Calculate the post-release number and write it into pyproject.toml (used for dev-releases)
bump-version:
    # get current version, append ".postN" (N=no. of commits since last release), write back into pyproject.toml
    version=$(git describe --tags --abbrev=0)
    commit_cnt=$(git rev-list --count main ^$version)
    commit_cnt=$((commit_cnt - 1))                        # N in ".postN" is zero-based
    if [ $commit_cnt -eq -1 ]; then exit 0; fi
    new_version=$(poetry version -s).post$commit_cnt      # pyproject.toml contains clean numbers, .postN isn't commited
    poetry version $new_version                           # write back into pyproject.toml

# Remove artifact files
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
