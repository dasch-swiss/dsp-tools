# E2E Tests with Testcontainers

This directory contains end-to-end tests that run against a full DSP stack using testcontainers.
The tests verify the complete workflow of DSP-TOOLS commands against a real DSP server environment.

## Architecture Overview

### Testcontainers Setup

The e2e tests use [testcontainers](https://testcontainers.com/) to spin up a complete DSP stack:

1. **Fuseki** (Apache Jena Fuseki) - Triplestore database
2. **SIPI** (Simple Image Presentation Interface) - Image server
3. **Ingest** - File ingestion service
4. **API** (DSP-API) - Main DSP backend API

Each container runs in an isolated Docker network with dynamically allocated ports to allow parallel test execution.

### Key Components

#### Setup Module (`setup_testcontainers/`)

- **`setup.py`**: Main entry point that orchestrates container lifecycle
  - `get_containers()`: Context manager that creates and tears down all containers
  - Generates unique UUIDs for each test run to prevent conflicts
  - Reads image versions from `docker-compose.yml` to ensure version consistency

- **`containers.py`**: Container configuration and startup logic
  - `get_all_containers()`: Starts all four containers in the correct order
  - Each container has specific startup wait conditions (log messages)
  - Containers are networked together with internal service names
  - Creates admin user in Fuseki during startup

- **`ports.py`**: Dynamic port allocation system
  - `get_ports()`: Finds and reserves 4 available ports starting from 1025
  - Uses lockfiles in `testdata/e2e/testcontainer_port_lockfiles/` to prevent port conflicts
  - `release_ports()`: Cleans up port lockfiles after test completion
  - Enables parallel test execution with pytest-xdist

- **`artifacts.py`**: Manages temporary directories for container data
  - Creates unique directories for each test run: `sipi_images/`, `tmp-sipi/`, `tmp-ingest/`, `ingest-db/`
  - All directories are created under `testdata/e2e/` with UUID suffixes
  - `remove_artifact_dirs()`: Cleans up directories after test completion

### Fixture Hierarchy and Scope

#### Module-Scoped Fixtures (Critical for Performance)

All fixtures use `scope="module"` to maximize reuse and minimize container restarts:

**Base Fixtures (in `commands/conftest.py`):**

```python
@pytest.fixture(scope="module")
def container_ports() -> Iterator[ExternalContainerPorts]:
    """Starts all containers, yields ports, stops containers at module end"""
    with get_containers() as metadata:
        yield metadata.ports

@pytest.fixture(scope="module")
def creds(container_ports: ExternalContainerPorts) -> ServerCredentials:
    """Returns credentials for connecting to the DSP server"""
    return ServerCredentials(...)
```

**Project Creation Fixtures (in `commands/xmlupload/conftest.py`):**

```python
@pytest.fixture(scope="module")
def create_generic_project_9999(creds: ServerCredentials) -> None:
    """Creates project 9999 with generic ontology - SHARED across tests"""
    assert create_project(Path("testdata/validate-data/generic/project.json"), creds)

@pytest.fixture(scope="module")
def create_4125_e2e_project(creds: ServerCredentials) -> None:
    """Creates project 4125 with e2e test ontology - SHARED across tests"""
    assert create_project(Path("testdata/json-project/test-project-e2e.json"), creds)
```

**Data Upload Fixtures (in `commands/xmlupload/conftest.py`):**

```python
@pytest.fixture(scope="module")
def _xmlupload_minimal_correct_9999(create_generic_project_9999, creds) -> None:
    """Uploads minimal test data to project 9999 - SHARED across tests"""
    # Note: Uses TemporaryDirectory to avoid id2iri mapping conflicts with pytest-xdist
    absolute_xml_path = Path("testdata/validate-data/generic/minimal_correct.xml").absolute()
    original_cwd = Path.cwd()
    with TemporaryDirectory() as tmpdir:
        with pytest.MonkeyPatch.context() as m:
            m.chdir(tmpdir)
            assert xmlupload(absolute_xml_path, creds, str(original_cwd))
```

**Derived Fixtures:**

```python
@pytest.fixture(scope="module")
def project_iri_9999(create_generic_project_9999, creds: ServerCredentials) -> str:
    """Fetches and returns the project IRI - depends on project creation"""
    get_project_route = f"{creds.server}/admin/projects/shortcode/9999"
    project_iri: str = requests.get(get_project_route, timeout=3).json()["project"]["id"]
    return project_iri

@pytest.fixture(scope="module")
def auth_header(create_generic_project_9999, creds) -> dict[str, str]:
    """Gets authentication token - depends on project creation"""
    payload = {"email": creds.user, "password": creds.password}
    token: str = requests.post(f"{creds.server}/v2/authentication", json=payload, timeout=3).json()["token"]
    return {"Authorization": f"Bearer {token}"}
```

## Optimization Strategies

### 1. Module Scope for Maximum Reuse

**Rule:** ALWAYS use `scope="module"` for fixtures in e2e tests.

**Why:**
- Container startup, project creation and xmlupload take long
- With module scope, these expensive operations run ONCE per test module

**Example:**
```python
# GOOD: All tests in test_resources.py share the same containers and uploaded data
@pytest.fixture(scope="module")
def cls_with_everything_graph(_xmlupload_minimal_correct_9999, ...):
    return util_request_resources_by_class(...)

# BAD: Would restart containers and re-upload for every test
@pytest.fixture  # scope="function" is the default
def cls_with_everything_graph(_xmlupload_minimal_correct_9999, ...):
    return util_request_resources_by_class(...)
```

### 2. Shared Projects and Data

**Rule:** Create projects and upload data once per module, share across all tests.

**Two Main Projects:**
- **Project 9999** (`testdata/validate-data/generic/project.json`): Generic ontology for validation tests
- **Project 4125** (`testdata/json-project/test-project-e2e.json`): E2E test ontology for xmlupload tests

**Data Upload Fixtures:**
- `_xmlupload_minimal_correct_9999`: Minimal test data for project 9999
- `_xmlupload_text_parsing_9999`: Text parsing test data for project 9999
- `_xmlupload_4125_e2e_project`: Full e2e test data for project 4125

**Usage Pattern:**
```python
# Test only needs to read data, not upload it
@pytest.mark.usefixtures("_xmlupload_minimal_correct_9999")
def test_resource_no_values(cls_with_everything_graph, ...):
    # Data is already uploaded, just query and assert
    res_iri = util_get_res_iri_from_label(cls_with_everything_graph, "resource_no_values")
    assert ...
```

### 3. pytest-xdist Compatibility

**Rule:** Handle id2iri mapping conflicts in parallel execution.

**Problem:** Multiple workers might upload the same data simultaneously, causing id2iri mapping file conflicts
(the mapping file is named after shortcode and timestamp).

**Solution:** Use `TemporaryDirectory` and `pytest.MonkeyPatch` to change working directory:
```python
@pytest.fixture(scope="module")
def _xmlupload_minimal_correct_9999(create_generic_project_9999, creds: ServerCredentials) -> None:
    """
    If there is more than 1 module, pytest-xdist might execute this fixture for multiple modules at the same time.
    This can lead to the situation that multiple workers start the xmlupload of the same data at the same time.
    Then it can happen that they try to save the id2iri mapping at the same time,
    which fails, because the id2iri mapping is named after the shortcode and the timestamp.
    """
    absolute_xml_path = Path("testdata/validate-data/generic/minimal_correct.xml").absolute()
    original_cwd = Path.cwd()
    with TemporaryDirectory() as tmpdir:
        with pytest.MonkeyPatch.context() as m:
            m.chdir(tmpdir)
            assert xmlupload(absolute_xml_path, creds, str(original_cwd))
```

### 4. Fixture Dependency Chains

**Rule:** Build fixtures that depend on each other to ensure correct execution order.

**Example Dependency Chain:**
```
container_ports (starts containers)
    ↓
creds (creates credentials)
    ↓
create_generic_project_9999 (creates project)
    ↓
_xmlupload_minimal_correct_9999 (uploads data)
    ↓
cls_with_everything_graph (queries data)
    ↓
test_* (runs assertions)
```

**Implementation:**
```python
@pytest.fixture(scope="module")
def cls_with_everything_graph(
    _xmlupload_minimal_correct_9999,  # Ensures data is uploaded first
    class_with_everything_iri_9999,
    auth_header,
    project_iri_9999,
    creds
) -> Graph:
    return util_request_resources_by_class(class_with_everything_iri_9999, auth_header, project_iri_9999, creds)
```

### 5. Parallel Execution with pytest-xdist

**Rule:** Use `pytest -n=auto --dist=loadfile` for parallel execution.

**Configuration:** Run with `just e2e-tests` or:
```bash
pytest -n=auto --dist=loadfile test/e2e/
```

**How it works:**
- `--dist=loadfile`: Distributes entire test files to workers (not individual tests)
- Each worker gets its own set of containers with unique ports
- Port lockfiles prevent port conflicts between workers
- Module-scoped fixtures ensure each worker reuses containers efficiently

**Why loadfile distribution?**
- Module-scoped fixtures are shared within a file
- Distributing individual tests would break fixture reuse
- Entire modules run on the same worker, maximizing container reuse

## Writing New E2E Tests

### Template for New Test Module

```python
# mypy: disable-error-code="no-untyped-def"

import pytest
from pathlib import Path
from dsp_tools.cli.args import ServerCredentials

# If testing a new project, add fixture in conftest.py:
@pytest.fixture(scope="module")
def create_my_project(creds: ServerCredentials) -> None:
    """Create your project - will be shared across all tests in this module"""
    assert create_project(Path("testdata/my-project.json"), creds)

# If testing data upload, add fixture in conftest.py:
@pytest.fixture(scope="module")
def _xmlupload_my_data(create_my_project, creds: ServerCredentials) -> None:
    """Upload test data - will be shared across all tests in this module"""
    absolute_xml_path = Path("testdata/my-data.xml").absolute()
    original_cwd = Path.cwd()
    with TemporaryDirectory() as tmpdir:
        with pytest.MonkeyPatch.context() as m:
            m.chdir(tmpdir)
            assert xmlupload(absolute_xml_path, creds, str(original_cwd))

# Test using the uploaded data:
@pytest.mark.usefixtures("_xmlupload_my_data")
def test_my_feature(creds: ServerCredentials, auth_header: dict[str, str]) -> None:
    """Test that reads the uploaded data and makes assertions"""
    response = requests.get(f"{creds.server}/v2/resources/...", headers=auth_header, timeout=3)
    assert response.ok
    # Make assertions on the response
```

### Best Practices

1. **Always use module scope:** `@pytest.fixture(scope="module")`

2. **Reuse existing projects when possible:**
   - Project 9999: Generic ontology with all property types
   - Project 4125: E2E test ontology with specific test cases

3. **Create minimal test data:**
   - Upload only the data needed for your tests
   - Share uploaded data across tests in the same module

4. **Use `@pytest.mark.usefixtures()` for setup-only fixtures:**
   - When you don't need the return value, just the side effect

5. **Handle pytest-xdist conflicts:**
   - Use `TemporaryDirectory` + `MonkeyPatch` for xmlupload fixtures
   - Add explanatory docstrings about parallel execution

6. **Build fixture dependency chains:**
   - List dependencies as fixture parameters
   - pytest will execute them in the correct order

7. **Avoid function-scoped fixtures:**
   - Container restarts are expensive
   - Project creation is expensive
   - Data upload is expensive

## Running E2E Tests

### Run All E2E Tests (Parallel)
```bash
just e2e-tests
# or
pytest -n=auto --dist=loadfile test/e2e/
```

### Run Single Test Module (Faster Development)
```bash
pytest test/e2e/commands/xmlupload/test_resources.py -v
```

### Run Specific Test
```bash
pytest test/e2e/commands/xmlupload/test_resources.py::TestResources::test_class_with_everything_all_created -v
```

### Debug Mode (Sequential, Verbose)
```bash
pytest test/e2e/ -v -s
```

## Troubleshooting

### "Docker is not running properly"
- Ensure Docker is running: `docker ps`
- Check Docker daemon: `docker stats --no-stream`

### "Port already in use"
- Port lockfiles might be stale: `rm -rf testdata/e2e/testcontainer_port_lockfiles/*`
- Check for running containers: `docker ps`

### "Container failed to start"
- Check container logs: `docker logs <container_name>`
- Verify Docker has enough memory allocated (recommend 4GB+)

### "Tests pass individually but fail in parallel"
- Check for shared state issues (shouldn't happen with proper fixture scoping)
- Verify TemporaryDirectory usage in xmlupload fixtures
- Run with `--dist=loadfile` not `--dist=loadscope`

### "Containers not stopping after tests"
- Context manager should handle cleanup automatically
- Manual cleanup: `docker ps | grep testcontainer | awk '{print $1}' | xargs docker stop`

### "Artifact directories filling up disk"
- Cleanup should be automatic but may fail with permission errors
- Manual cleanup: `rm -rf testdata/e2e/images/* testdata/e2e/tmp-* testdata/e2e/ingest-db/*`

## Directory Structure

```
test/e2e/
├── CLAUDE.md                           # This file
├── setup_testcontainers/               # Testcontainer infrastructure
├── commands/                           # Command-specific tests
│   ├── conftest.py                     # Base fixtures (container_ports, creds)
│   ├── project/                        # dsp-tools create/get tests
│   ├── xmlupload/                      # dsp-tools xmlupload tests
│   ├── validate_data/                  # dsp-tools validate-data tests
│   └── ingest_xmlupload/               # New ingest workflow tests
```
