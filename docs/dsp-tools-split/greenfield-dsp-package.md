# Greenfield DSP Python Package: Public Interface

## Purpose

This document proposes the public interface of a Python package for the DSP server.
It is a basis for discussion. Internals are out of scope.

The package has two user groups:

- dsp-tools, which uses the package for all server interaction.
- External researchers, who use the package in scripts and notebooks.

The interface must cover all server capabilities that dsp-tools uses today.
It also outlines capabilities that researchers and RDU members need.
Sources:

- Wanted features: [Admin](1_admin.md), [Ontology](2_ontology.md), [Data](3_data.md).
- Server interaction of dsp-tools today: [dsp-tools Server Flows](https://claude.ai/artifact/BmDEynb57FEtmjt3uhFFQT).

## Principles

1. **Intent over procedure.**
   The user states the result, for example "create this data".
   The package decides the order, the batching and the retries.
   The user does not know that resources with circular links need two steps.
2. **No API concepts.**
   Routes, JSON-LD, API versions and the separate ingest service are not visible.
   The user sees one DSP server.
3. **Python objects in and out.**
   Input and output are typed, immutable dataclasses.
   File formats (JSON project file, XML data file, Excel) are not part of the package.
4. **Local references.**
   The user refers to items by their own ID, name or shortcode.
   The package returns the server IRIs as part of the result.
5. **One item or many.**
   Each operation accepts one item or a collection.
6. **Results, not exceptions per item.**
   A bulk operation returns a result with the created items and the failures.
7. **Same verbs in every domain.**
   Each domain has create, read, update and delete.
   Domain actions add to these verbs where necessary.
   - Create is only for new items. Create of an item that exists fails.
   - Update changes or adds to an item that exists.
   - Delete is possible for all items. Delete marks an item as deleted and does not erase it.
8. **Long operations can continue.**
   An interrupted bulk operation returns a state that the user gives back to continue.
9. **Full permission model.**
   The interface shows the full permission model, not only presets.
10. **Rights are known before an operation.**
    A helper function returns an enum of the operations that the current user can do.
    As a result, dsp-tools can check the rights before it starts a planned operation.

## Domains

The column "dsp-tools" marks the capabilities that dsp-tools needs.

| Domain       | Capabilities                                                                              | dsp-tools |
|--------------|-------------------------------------------------------------------------------------------|-----------|
| Connection   | Connect to a server with credentials                                                      | x         |
| Projects     | Project with metadata                                                                     | x         |
|              | Legal info: licenses, copyright holders, default authorship                               | x         |
|              | Embargo                                                                                   |           |
| Access       | Users, groups and memberships                                                             | x         |
|              | Default permissions of the project                                                        | x         |
|              | Admin permissions of users                                                                |           |
|              | Operations that the current user can do                                                   | x         |
| Data model   | Ontologies, classes, properties, cardinalities                                            | x         |
|              | External mappings of classes and properties                                               | x         |
|              | Default permissions per class and property                                                |           |
| Vocabularies | Lists and nodes                                                                           | x         |
|              | Reorder nodes, change labels and comments                                                 |           |
| Data         | Create data: resources, values and files as one unit                                      | x         |
|              | Add values to existing resources                                                          |           |
|              | Replace existing values and files                                                         |           |
|              | Change permissions of resources and values                                                |           |
|              | Export data, for example by class, as Python objects                                      |           |
| Validation   | Validate data against the server data model, incl. files and existing data without upload | x         |
| Migration    | Export a project from one server and import it into another                               | x         |

Notes:

- Create data replaces the dsp-tools workflows `xmlupload`, `upload-files`, `ingest-files`
  and `ingest-xmlupload`. The package selects the ingest strategy.
- Validation runs in the package. It does not change the server.

## Open Questions

- Name of the package.
- Repository: the long-term plan is to move the package into the dsp-api repository.
  Package and server versions then stay aligned. Where does the package live before the move?
- Synchronous or asynchronous interface.
- Progress reporting and continuation of long operations.
