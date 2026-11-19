# get — Quick Reference

Implements `dsp-tools get`: read a project from a DSP server and write it into a JSON project file.
It is the read-side counterpart of `create`.
The output must be a valid input for `create`.

## Entry point

`get_project(project_identifier, outfile_path, creds, verbose)` in `get.py`.
`cli/call_action_with_network.py` is its only caller in `src/`.
Flow:

1. Authenticate. Without valid credentials, `get` continues anonymously.
   It then writes a placeholder text into `default_permissions`.
   If the server refuses the users, `_get_users` returns `None` and the file has no `users` section.
2. `_create_project` resolves the identifier (shortcode, shortname or IRI) to a `Project`.
3. Read the project, then the ontologies, the default permissions, the groups, the users and the lists.
   `get_permissions.py` reads the permissions.
   Each other part comes from a class in `legacy_models/`, which calls the server
   and builds its own JSON section (`createDefinitionFileObj`).
4. `json.dump` writes the file at `outfile_path`. `get.py` is the only writer of this file.

## Files

- `get.py`: command entry point. It builds the `project` section itself
  and has a private helper for each of the groups, users, lists and ontologies.
- `get_permissions.py`: reads the default object access permissions (DOAPs) of the project
  and converts them into `default_permissions` and `default_permissions_overrule`.
- `get_permissions_legacy.py`: checks if the DOAPs match one of the two legacy patterns (`public`, `private`).
- `models/permissions_models.py`: `DoapCategories`, the DOAPs sorted by what they apply to.
- `exceptions.py`: `InvalidProjectIdentifierError`.
- `legacy_models/`: older CRUD classes (`Project`, `Ontology`, `Group`, `User`, `ListNode`, and others).
  `get` only reads with them.

## Code outside `get` that depends on its internals

`get_project` is the only public interface.
But other code imports from `legacy_models/` directly.
If you change a class in `legacy_models/`, examine these places too:

- `utils/request_utils.py` imports `Context` and `OntoIri` to serialize them to JSON.
- The top-level `legacy_models/projectContext.py` imports `Group` and `Project`.
- `create` reads back the `users` section that `User.createDefinitionFileObj` writes,
  in `_parse_one_user` (`create/parsing/parse_project.py`).
  This is a file-format contract, not an import.
  `test/unittests/commands/create/test_admin_account_check.py` imports `User` to test it.
- `test/integration/commands/test_get_project.py` and `test/unittests/commands/get/test_project_legacy.py`
  import `Project`. The legacy E2E tests under `test/legacy_e2e/commands/project/` import most of the other classes.
- `test/unittests/commands/get/test_get_permissions.py` and `test_get_permissions_legacy.py`
  import private helpers of `get_permissions.py`.
  If you rename or change one of them, update these tests.

## Tests

- Unit: `test/unittests/commands/get/`.
- Integration: `test/integration/commands/test_get_project.py`.
- E2E: `test/e2e/commands/project/test_get.py` and `test/e2e/commands/test_create_get_xmlupload.py`
  (round trip `create` → `get` → `xmlupload`).
