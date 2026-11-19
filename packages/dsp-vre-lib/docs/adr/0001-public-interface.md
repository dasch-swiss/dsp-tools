---
status: proposed
date: 2026-11-11
---

# ADR for the Python Package `dsp-vre-lib`

## Summary

`dsp-vre-lib` is a Python package for the DSP server.
DaSCH tools, DaSCH services and external researchers use it for all server interaction.
This ADR records the public interface of `dsp-vre-lib`: principles, package name, result model and domains.
The internals are out of scope.

## Context

Today, the server clients live in `src/dsp_tools/clients/`, and only `dsp-tools` uses them.
Other DaSCH services and researchers need the same server access, but they cannot use these clients.
The clients also show API concepts (routes, JSON-LD, the separate ingest service) to the caller.

The package has two user groups:

- DaSCH tools and services, which use the package for all server interaction.
- External researchers, who use the package in scripts and notebooks.

## Decision

### Scope of the Split

The split is complete when `dsp-vre-lib` supports all features of `dsp-tools`.
The exceptions are the features in the "Not Supported" table of each interface document.
Each row of the table gives the reason.
Each domain lists later capabilities under "Future work", for example the export of data.
If the interface of a future capability is known, the package has a stub with the final signature.
The stub cannot be called.
If the interface is not known, the documentation names the capability, and there is no stub.

### Principles

1. **Intent over procedure.**
   The user states the result, for example "create this data".
   The package decides the order, the batching and the retries.
   The user does not know that resources with circular links need two steps.
2. **No API concepts.**
   Routes, JSON-LD, API versions and the separate ingest service are not visible.
   The user sees one DSP server.
3. **Python objects in and out.**
   Input and output are typed, immutable dataclasses.
   File formats (JSON, XML, Excel) are not part of the package.
   A read returns separate read models, not the input dataclasses.
   The server can hold data that an input dataclass does not accept,
   for example a user without a password or a GUI element that the package does not support.
   A conversion from a read model to an input model reports the information that gets lost.
   The name of the read operation is not decided.
4. **Local references.**
   The user refers to items by their own ID, name or shortcode.
   The package returns the server IRIs as part of the result.
5. **One item or many.**
   Each operation accepts one item or a collection.
6. **Results, not exceptions per item.**
   A bulk operation returns a result with the created items and the failures.
7. **Each domain covers create, read, update and delete.**
   The names of the operations state the intent, for example `add_data_model` or `set_visibility`.
    - An operation that creates one kind of item fails if the item exists.
    - An aggregate operation, for example `set_up_project`, skips the items that exist.
      Its result reports the skipped items.
    - Update changes or adds to an item that exists.
    - Delete is possible for all items. On Data, delete marks an item as deleted and does not erase it.
8. **Long operations can continue.**
   An interrupted bulk operation returns a state that the user gives back to continue.
9. **Permissions through a user-friendly abstraction layer.**
   The interface gives easy-to-understand options for the permissions:
   the project roles read, write and admin, and a visibility on the items of the data model.
   The goal: the options cover all permission needs, without too much complexity.
   A user can also be a member of custom groups, as in `dsp-tools` today.
   A visibility does not refer to a group.
   The full DSP permission model (permission levels on groups) is future work.
10. **Rights are known before an operation.**
    A helper function returns an enum of the operations that the current user can do.
    As a result, a client can check the rights before it starts an operation.
11. **Functional error model.**
    Runtime conditions are results, for example a rejection by the server,
    an unreachable server, a partial success or a feature that the server does not support.
    Programming errors raise, for example a wrong type, invalid input or a call of a stub.
    The result is a union of dataclasses. Each variant holds only its own data.

### Package Name

The PyPI name is `dsp-vre-lib`. The import name is `dsp_vre_lib`.
The repository that holds the package at the end has the name `dsp-vre`.
Thus the package needs a different name.

### Synchronous Interface Only

The package has a synchronous interface only. The reasons are:

- Researchers use scripts and notebooks.
  Notebooks run their own event loop, thus an asynchronous interface is difficult to use there.
- Speed comes from parallel work inside the package (principle 1), not from the interface.
- An asynchronous interface can come later as a separate module, if a user needs it.

### Result Model

Each operation returns a result object for runtime conditions (principles 6, 8 and 11).
The result is a union of frozen dataclasses, one for each outcome:

```python
type Result = Success | PartialSuccess | Failure | Interrupted

match result:
    case Success():
        ...
    case PartialSuccess():
        ...
    case Failure():
        ...
    case Interrupted():
        ...
    case _:
        assert_never(result)
```

The fields of each variant are not decided.
The diagram shows the outcomes of one operation.

```mermaid
---
title: Outcomes of One Operation
---
stateDiagram-v2
    [*] --> Running
    Running --> Success
    Running --> PartialSuccess
    Running --> Failure
    Running --> Interrupted
    Interrupted --> Running: user gives back the continuation state
    Success --> [*]
    PartialSuccess --> [*]
    Failure --> [*]

    note right of PartialSuccess
        Result holds the created items
        and the failed items.
    end note
    note right of Interrupted
        Result holds the items that are not done
        and the ID-to-IRI map of the done items.
    end note
```

### Domains

The package has six domains.
The diagram shows which domain needs which other domain. An arrow points to the domain that is needed.
All domains need Connection through Projects.

```mermaid
---
title: Domains of dsp-vre-lib
---
flowchart LR
    connection["Connection<br/>credentials"]
    projects["Projects<br/>metadata, legal info,<br/>migration"]
    permissions["Permissions<br/>users, project roles,<br/>groups, rights"]
    datamodel["Data model<br/>ontologies, classes,<br/>properties, mappings"]
    vocabularies["Vocabularies<br/>lists, nodes"]
    data["Data<br/>create, validate"]

    projects --> connection
    permissions --> projects
    datamodel --> projects
    vocabularies --> projects
    data --> datamodel
    data --> vocabularies
    data -->|legal info| projects
    data -->|project roles| permissions
```

Each domain lists the capabilities in scope for the first release.
"Future work" lists the capabilities for later releases.

#### Connection

- Connect to a server with credentials.

Future work: none at this time.

#### Projects

- Project with metadata.
- Legal info: licenses, copyright holders, default authorship.
- Migration: export a project from one server and import it into another server.
  The export includes the data model and the admin data.

Future work:

- Embargo: data is hidden until an end date, with embargo metadata. Needs support in DSP-API first.
- Private project ("VRE mode"): the project is hidden entirely from non-members, including its data model.
  Needs support in DSP-API; until then, approximated with permissions.
- Access rights: the rights that apply once a project is in the archive. Needs support in DSP-API first.

#### Permissions

- Users, their project roles and their custom groups.
- Operations that the current user can do (principle 10).

#### Data Model

- Ontologies, classes, properties, cardinalities and their visibility.
- External mappings of classes and properties.

#### Vocabularies

- Lists and nodes.

Future work:

- Reorder nodes.
- Change labels and comments of nodes.

#### Data

- Create data: resources, values and files as one unit.
  The package selects the ingest strategy.
- Validate data against the data model on the server.
  The validation includes files and existing data.
  The validation runs in the package and does not change the server.

Future work:

- Add values to existing resources.
- Replace existing values and files.
- Change permissions of resources and values without versioning of the data.
- Export data as Python objects, for example by class.

## Consequences

Positive:

- DaSCH tools, DaSCH services and researchers use one server interface.
- API changes on the server affect `dsp-vre-lib` only, not its callers.
- File formats stay in `dsp-tools`. `dsp-vre-lib` stays free of JSON, XML and Excel parsing.

Negative:

- `dsp-tools` and `dsp-vre-lib` have two release cycles.
- `dsp-tools` depends on a pinned version range of `dsp-vre-lib`.
- `dsp-vre-lib` states the `dsp-api` versions that it supports.
- A synchronous interface can be too slow for callers that need many parallel operations.

## Open Decisions

### Progress, Reporting and Continuation

Status: not decided.

The topics below are different mechanisms. They do not compete with each other.
For each topic, the exact behaviour is not defined.

- **Callback.**
  The user gives an optional function to a long operation, for example `on_progress`.
  The package calls the function after each item with one progress event:
  items done, items total, current item, and failures so far.
- **Standard logging.**
  The package writes to a Python logger with the fixed name `dsp_vre_lib`.
  The caller configures handlers, formats and files.
  Levels: `INFO` for start, end and summary of an operation, `DEBUG` for each item, `WARNING` for failed items.
- **Continuation state.**
  An interrupted bulk operation returns a dataclass with the items that are not done,
  and the ID-to-IRI map of the items that are done.
  The package gives functions to save the state to a file and to read it from a file.
  The user gives the state back to the same operation, which does not create done items again.
- **Server-side state (long term).**
  Today, the client holds the state of a bulk operation.
  If the client stops, the user must keep the continuation state.
  Long term, the server can run the bulk operation and keep its state,
  for example with a streaming platform such as Kafka.
  The client then only sends the data and reads the progress from the server.
  This needs significant infrastructure work and an asynchronous interface in the package.
  It is out of scope for the first release.
- **Masking vs. Exposing.**
  In some cases, the package hides a behaviour, for example the creation of one resource after the other in `xmlupload`.
  In other cases, the package shows a granular behaviour for the medium term, but not for the long term.

Each topic gets evaluated against one real bulk-create use case before a decision.

## Related Documents

- [Map: `dsp-vre-lib` domains in `dsp-tools`](../../../../docs/dsp-tools-split/dsp-vre-lib-to-tools-map.md):
  which `dsp-tools` command uses which domain, with the `dsp-tools create` worked example.
- [Set-up for the split](../../../../docs/dsp-tools-split/dsp-tools-split-package-setup.md):
  repository layout, dependency direction and release timeline.
