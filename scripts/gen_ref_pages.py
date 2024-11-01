"""
Auto-generate API docs from docstrings.
This script generates markdown files containing syntax that is rendered by mkdocstrings.
The generated files are neither visible nor accessible in the file system, but can be seen by mkdocstrings.

Components/tools:
- mkdocstrings: triggered by dedicated instructions in markdown files, this tool reads docstrings and generates API docs
- mkdocs-gen-files: for every python file, automatically generates a markdown file with instructions for mkdocstrings
- mkdocs-literate-nav: generates the navigation bar, so that every API docs page appears in the nav bar
- mkdocs-section-index: instead of listing __init__.py files in the nav bar, extract their content and render it

See https://mkdocstrings.github.io/recipes/#automatic-code-reference-pages
"""  # noqa: INP001

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()  # type: ignore[attr-defined,no-untyped-call]

root = next(x for x in reversed(Path(__file__).parents) if x.name in ["dsp-docs", "dsp-tools"])
src = root / "src" if root.name == "dsp-tools" else root / "dsp/dsp-tools/src"
dsp_tools = src / "dsp_tools"
docstrings_build_target = Path("reference") if root.name == "dsp-tools" else Path("DSP-TOOLS/reference")

if root.name == "dsp-docs":
    (root / "dsp/__init__.py").touch()
    (root / "dsp/dsp-tools/__init__.py").touch()
    (root / "dsp/dsp-tools/src/__init__.py").touch()

for path in sorted(src.glob("dsp_tools/xmllib/**/*.py")):
    module_path = path.relative_to(src).with_suffix("")
    doc_path = path.relative_to(dsp_tools).with_suffix(".md")  # omit the "dsp_tools" level in the navigation bar
    full_doc_path = docstrings_build_target / doc_path

    parts = tuple(module_path.parts) if root.name == "dsp-tools" else tuple(path.relative_to(root).with_suffix("").parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] == "__main__":
        continue

    nav[parts[1:]] = doc_path.as_posix()  # omit the "dsp_tools" level in the navigation bar

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        fd.write(f"::: {ident}")

    # The 2nd parameter of mkdocs_gen_files.set_edit_path() is relative to mkdocs.yml > edit_uri.
    # See https://mkdocstrings.github.io/recipes/#generate-pages-on-the-fly
    mkdocs_gen_files.set_edit_path(full_doc_path, Path("../") / path)

with mkdocs_gen_files.open(docstrings_build_target / "xmllib-generated-api-doc.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
