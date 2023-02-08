[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Documentation with mkdocs

## Styling constraints in the documentation

In our GitHub actions, we check PRs for dead links in the documentation. 
Our tool markdown-link-validator is only able to check internal links
if they start with `./`. For example:

- `[prefixes](./dsp-tools-create.md#prefixes-object)` instead of `[prefixes](dsp-tools-create.md#prefixes-object)`
- `![Colors_en](./assets/images/img-list-english-colors.png)` instead of `![Colors_en](assets/images/img-list-english-colors.png)`

It is okay, however, to make an internal link to a title of the current document: `[prefixes](#prefixes-object)`

Please follow this constraint, so that markdown-link-validator can check the internal links.

| <center>Hint</center>                                                                                                                                                                      |
|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| If your links are correct, but markdown-link-validator doesn't recognize them, it might be necessary to adapt the call to markdown-link-validator in `.github/workflows/tests-on-push.yml` |



## Internal links to headings that appear twice in the same document

The documentation of DSP-TOOLS contains a constellation which is slightly suboptimal:
Documents that contain the same heading several times.
The file `docs/file-formats/json-project/ontologies.md`, for example, 
contains 3 times a `### Name`.

This becomes problematic when making an internal link to one of these headings.
Different implementations of Markdown have incompatible solutions, 
as can be seen in this example:

file.md:

```
# Heading
First heading with this name

# Heading
Second heading with this name
```

other-file.md:

```
[Second Heading](file.md#heading_1)    <!--mkdocs supports only this syntax-->
[Second Heading](file.md#heading-1)    <!--npm markdown-link-validator supports only this syntax-->
```

VS Code supports both syntaxes, whereas PyCharm supports only the one with `heading-1`.
By standard means, it is thus impossible to create links that work everywhere.
The real danger is that mkdocs doesn't complain if you use the `heading-1` syntax, 
not even when using the `--strict` flag.

The solution is to add an anchor to the problematic headings:

```
# Heading <a id="id"></a>
Second heading with this name, with HTML anchor

<a href="file#id1">heading</a>
```

| <center>LOOK OUT!</center>                                                                                                         |
|:-----------------------------------------------------------------------------------------------------------------------------------|
| Developers might get lured into using the `heading-1` syntax, which will pass on GitHub CI, but break on https://docs.dasch.swiss! |
