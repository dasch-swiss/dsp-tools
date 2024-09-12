RUFF_CHECK := "ruff check . --ignore=A002,D101,D102,PLR0913,PLR2004"

# List all recipes
default:
    @just --list

# Run the ruff linter to detect bad Python coding habits
ruff-check:
    {{ RUFF_CHECK }}

# Run the ruff linter, with an output format suitable for GitHub runners
ruff-check-github:
    {{ RUFF_CHECK }} --output-format=github

# Check the formatting of the Python files
ruff-format-check:
    ruff format --check .

# Check the type annotations in Python files for correctness
mypy:
    mypy .

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
unittests:
    pytest test/unittests/

# Run the integration tests
integration-tests:
    pytest test/integration/

# Run the end-to-end tests (with testcontainers)
e2e-tests:
    pytest test/e2e/

# Run the legacy end-to-end tests (needs a running stack)
legacy-e2e-tests:
    pytest test/legacy_e2e/

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
