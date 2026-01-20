# CLI Module

This file provides guidance for modifying the CLI (Command Line Interface) module of DSP-TOOLS.
This module handles argument parsing, command routing, and execution of user-requested actions.

## Module Overview

The CLI module is the entry point for all DSP-TOOLS commands.
It transforms user input from the command line into structured actions that are executed by the rest of the codebase.

### File Structure

- **entry_point.py** - Main entry point with version checking and orchestration
- **create_parsers.py** - Defines all CLI commands and their arguments using argparse
- **call_action.py** - Routes parsed arguments to the appropriate command handler
- **call_action_with_network.py** - Handlers for commands that require network access or Docker
- **call_action_files_only.py** - Handlers for commands that only work with local files
- **args.py** - Dataclass models for command configuration (credentials, validation config, etc.)
- **exceptions.py** - CLI-specific exceptions
- **utils.py** - Input validation helpers (path checking, network health checks, credential extraction)

### Data Flow

```
User runs command
  ↓
entry_point.py:main() → entry_point.py:run()
  ↓
create_parsers.py:make_parser() - Creates argument parser
  ↓
entry_point.py:_parse_arguments() - Parses user input
  ↓
call_action.py:call_requested_action() - Routes to appropriate handler
  ↓
call_action_with_network.py or call_action_files_only.py - Executes the command
  ↓
Returns success/failure status
```

## Common Modification Tasks

### Adding a New Argument to an Existing Command

To add a new argument/flag to an existing command, you need to modify the parser definition in `create_parsers.py`.

**Example**: Adding a `--timeout-seconds` argument to the `xmlupload` command

1. Locate the function that creates the parser for your command in `create_parsers.py`:

```python
def _add_xmlupload(
        subparsers: _SubParsersAction[ArgumentParser],
        default_dsp_api_url: str,
        root_user_email: str,
        root_user_pw: str,
) -> None:
    subparser = subparsers.add_parser(name="xmlupload", help="Upload data defined in an XML file to a DSP server")
    subparser.set_defaults(action="xmlupload")

    # Add your new argument here
    subparser.add_argument("--timeout-seconds", type=int, default=300, help="timeout for API requests in seconds")

    # ... existing arguments ...
```

2. The parsed argument will automatically be available in the `args` namespace passed to the command handler.

3. Update the command handler in `call_action_with_network.py` or `call_action_files_only.py` to use the new argument:

```python
def call_xmlupload(args: argparse.Namespace) -> bool:
    timeout = args.timeout_seconds  # Access the new argument
    # ... rest of implementation ...
```

**Argument Types**:

- Boolean flags: `subparser.add_argument("--flag", action="store_true", help="...")`
- Required arguments: `subparser.add_argument("--arg", required=True, help="...")`
- Positional arguments: `subparser.add_argument("argname", help="...")`
- Choice arguments: `subparser.add_argument("--choice", choices=["a", "b"], default="a", help="...")`

### Help Text Best Practices

Writing clear, consistent help text improves the user experience and makes commands discoverable.

**Required vs Default Values**:

- Use `required=True` sparingly - only for truly essential arguments
- Prefer sensible defaults when possible (especially for localhost development)
- Document defaults in help text when they're not obvious: "default: 300 seconds"

**Command-Level Help**:

When adding a new command, the help text appears in `dsp-tools --help`:

```python
subparser = subparsers.add_parser(
    name="xmlupload",
    help="Upload data defined in an XML file to a DSP server"  # Keep this brief - 1 line
)
```

### Modifying Command Handlers

Command handlers are located in:

- **call_action_with_network.py** - For commands that interact with servers or Docker
- **call_action_files_only.py** - For commands that only process local files

**Example**: Modifying the `create` command handler

```python
def call_create(args: argparse.Namespace) -> bool:
    """
    Handler for the 'create' command.
    Creates a project on a DSP server from a JSON file.
    """
    # 1. Extract configuration from args
    creds = get_creds(args)
    xml_file = Path(args.project_definition)

    # 2. Validate inputs
    check_input_dependencies(
        paths=PathDependencies(required_files=[xml_file]),
        network_dependencies=NetworkRequirements(api_url=creds.server),
    )

    # 3. Execute the command logic
    # Call the actual implementation from commands module
    result = project_create(
        project_file_as_path=xml_file,
        server=creds.server,
        user_mail=creds.user,
        password=creds.password,
        # ... other parameters ...
    )

    return result
```

**Pattern for command handlers**:

1. Extract configuration from `args` namespace
2. Validate inputs (paths, network, credentials)
3. Call the actual implementation from the `commands` module
4. Return success status (True/False)

### Error Handling and Exit Codes

Command handlers use a consistent error handling pattern that separates user-facing errors from internal errors.

**Return Value Convention**:

All command handlers return a boolean:

- `True` = command succeeded
- `False` = command failed

The entry point (`entry_point.py:83-85`) converts `False` returns into `sys.exit(1)` for the shell.

### Input Validation Patterns

The `utils.py` module provides helpers for validating user input before executing commands.
Always validate the input before calling the requested action.

**Path Validation**:

```python
from dsp_tools.cli.args import PathDependencies
from dsp_tools.cli.utils import check_input_dependencies

# Validate that required files exist
check_input_dependencies(
    paths=PathDependencies(
        required_files=[Path("data.xml"), Path("config.json")],
        required_directories=[Path("assets/")],
    )
)
```

**Network Validation**:

```python
from dsp_tools.cli.args import NetworkRequirements
from dsp_tools.cli.utils import check_input_dependencies

# Check that Docker is running and DSP-API is healthy
check_input_dependencies(
    network_dependencies=NetworkRequirements(
        api_url="http://0.0.0.0:3333",
        always_requires_docker=True,  # Set to True for commands that always need Docker
    )
)
```

**Credential Extraction**:

```python
from dsp_tools.cli.utils import get_creds

# Extract server credentials from parsed arguments
creds = get_creds(args)  # Returns ServerCredentials dataclass
# creds.server, creds.user, creds.password, creds.dsp_ingest_url
```

### Server URL Canonicalization

The CLI automatically transforms DSP server URLs to their canonical form:

- `localhost:3333` or `0.0.0.0:3333` → `http://0.0.0.0:3333` (API) + `http://0.0.0.0:3340` (ingest)
- `admin.dasch.swiss` or `api.dasch.swiss` → `https://api.dasch.swiss` (API) + `https://ingest.dasch.swiss` (ingest)

This happens in `entry_point.py:_derive_dsp_ingest_url()` before the command handler is called.

## Testing CLI Commands

### Unit Testing Argument Parsing

Test that your parser correctly parses command-line arguments:

In order for the check if files exist to pass you must reference existing test files.
At the top of the test file you have global variables that you can reuse.

```python
@patch("dsp_tools.cli.call_action_files_only.excel2lists")
def test_excel2lists(excel2lists: Mock) -> None:
    excel2lists.return_value = ([], True)
    out_file = "filename.json"
    args = f"excel2lists {EXCEL_FOLDER} {out_file}".split()
    entry_point.run(args)
    excel2lists.assert_called_once_with(
        excelfolder=EXCEL_FOLDER,
        path_to_output_file=out_file,
    )
```

### Mocking Network Calls

When testing commands that require network access, mock the API calls:

```python
    @patch("dsp_tools.cli.utils._check_network_health")
@patch("dsp_tools.cli.call_action_with_network.create_lists_only")
def test_lists_create(self, create_lists: Mock, check_docker: Mock) -> None:
    create_lists.return_value = True
    args = f"create --lists-only {PROJECT_JSON_PATH}".split()
    creds = ServerCredentials(server="http://0.0.0.0:3333", user="root@example.com", password="test")
    entry_point.run(args)
    create_lists.assert_called_once_with(
        project_file=PROJECT_JSON_PATH,
        creds=creds,
    )
```

## Configuration Dataclasses

The `args.py` module defines dataclass models for common configuration patterns:

- **ServerCredentials** - Server URL, username, password, ingest URL
- **ValidateDataConfig** - Configuration for data validation commands
- **PathDependencies** - Required files and directories for a command
- **NetworkRequirements** - Network/Docker requirements for a command

Use these dataclasses to pass configuration around instead of passing individual arguments.

## Adding a New Command

While modifying existing commands is more common, this section guides you through adding a new CLI command.

### Key Design Decisions

Before implementing, consider these architectural choices:

**1. Does the command require network access or Docker?**

- **Network/Docker required** → Handler goes in `call_action_with_network.py`
    - Examples: `create`, `xmlupload`, `validate-data`, `start-stack`
    - Needs to communicate with DSP-API server or manage Docker containers
    - Will use server credentials (user, password, server URL)

- **Files only** → Handler goes in `call_action_files_only.py`
    - Examples: `excel2json`, `id2iri`, `update-legal`
    - Pure local file transformations
    - No network dependencies

**2. What inputs does the command need?**

Design your argument interface thoughtfully:

- Keep it simple - avoid excessive flags and options
- Use sensible defaults where possible
- Consider whether inputs should be positional or optional
- Think about common use cases, not every possible scenario

**3. Where should validation happen?**

Separate CLI validation from business logic:

- **CLI level** (in handler): File existence, path validity, basic format checks
- **Command level** (in `commands/`): File content validation, business rules, data integrity

**4. What configuration objects are needed?**

Use dataclasses from `args.py` to group related parameters:

- `ServerCredentials` for server connection info
- `PathDependencies` for required files/directories
- `NetworkRequirements` for Docker/API requirements

### Implementation Steps

**Step 1: Design the command interface**

Determine the command name and its arguments. Document the intended CLI usage:

```bash
# Example: New command to validate JSON project files
dsp-tools validate-project <project_file> [--strict]
```

**Step 2: Add argument parser**

Create a parser function in `create_parsers.py`:

```python
def _add_validate_project(
        subparsers: _SubParsersAction[ArgumentParser],
) -> None:
    subparser = subparsers.add_parser(
        name="validate-project",
        help="Validate a JSON project file against the schema"
    )
    subparser.set_defaults(action="validate-project")

    # Add arguments
    subparser.add_argument("project_file", help="path to the JSON project file")
    subparser.add_argument("--strict", action="store_true",
        help="enable strict validation with additional checks")
```

Call it from `make_parser()`:

```python
def make_parser(...) -> ArgumentParser:
    # ... existing code ...
    _add_validate_project(subparsers)
    # ... rest of parsers ...
```

**Step 3: Create command handler**

Add handler in `call_action_files_only.py` (or `call_action_with_network.py`):

```python
def call_validate_project(args: argparse.Namespace) -> bool:
    """
    Handler for the 'validate-project' command.
    Validates a JSON project file against the schema.
    """
    # 1. Extract arguments
    project_file = Path(args.project_file)
    strict_mode = args.strict

    # 2. Validate inputs at CLI level
    check_input_dependencies(
        paths=PathDependencies(required_files=[project_file])
    )

    # 3. Call implementation from commands module
    result = validate_project_file(
        project_file=project_file,
        strict=strict_mode,
    )

    return result
```

**Step 4: Route the command**

Add a case in `call_action.py:call_requested_action()`:

```python
def call_requested_action(args: argparse.Namespace) -> bool:
    match args.action:
        # ... existing cases ...
        case "validate-project":
            result = call_validate_project(args)
        # ... rest of cases ...
```

**Step 5: Implement command logic**

Create implementation in `src/dsp_tools/commands/` (this is where the actual work happens):

```python
# In src/dsp_tools/commands/validate/validate_project.py
def validate_project_file(project_file: Path, strict: bool) -> bool:
    """
    Validate a JSON project file.
    This is the actual implementation, separate from CLI concerns.
    """
    # Implementation details...
    return True  # or False if validation fails
```

**Step 6: Add tests**

Add tests in `test/unittests/cli/`:

```python
@patch("dsp_tools.cli.call_action_files_only.validate_project_file")
def test_validate_project(validate_project_file: Mock) -> None:
    validate_project_file.return_value = True
    args = f"validate-project {PROJECT_JSON_PATH} --strict".split()
    entry_point.run(args)
    validate_project_file.assert_called_once_with(
        project_file=PROJECT_JSON_PATH,
        strict=True,
    )
```

### Integration Checklist

When adding a new command, verify:

- [ ] Parser function created in `create_parsers.py`
- [ ] Parser called from `make_parser()`
- [ ] Handler function in appropriate `call_action_*.py` file
- [ ] Case added to `call_action.py` match statement
- [ ] Implementation in `commands/` module
- [ ] Unit tests for CLI argument parsing
- [ ] Help text is clear and follows conventions

## Related Documentation

- Root `CLAUDE.md` - General project guidelines, coding standards, testing philosophy
- `src/dsp_tools/commands/` - Contains the actual implementation of CLI commands
- `pyproject.toml` - Entry point configuration (`[project.scripts]` section)
