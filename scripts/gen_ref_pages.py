"""
Auto-generate API docs from docstrings, using mkdocs-gen-files and mkdocs-literate-nav.
This script generates md files containing syntax that is rendered by mkdocstrings.
The generated files are neither visible nor accessible in the file system, but can be seen by mkdocstrings.
"""  # noqa: INP001

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()  # type: ignore[attr-defined,no-untyped-call]

root = Path(__file__).parent.parent
src = root / "src"
dsp_tools = src / "dsp_tools"

for path in sorted(src.glob("dsp_tools/xmllib/**/*.py")):
    module_path = path.relative_to(src).with_suffix("")
    doc_path = path.relative_to(dsp_tools).with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
    elif parts[-1] == "__main__":
        continue

    nav[parts[1:]] = doc_path.as_posix()  # omit the "dsp_tools" level in the navigation bar

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        fd.write(f"::: {ident}")

    # The 2nd parameter of mkdocs_gen_files.set_edit_path() is relative to mkdocs.yml > edit_uri.
    # See https://mkdocstrings.github.io/recipes/#generate-pages-on-the-fly
    mkdocs_gen_files.set_edit_path(full_doc_path, Path("../") / path)

with mkdocs_gen_files.open("reference/xmllib-generated-api-doc.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
