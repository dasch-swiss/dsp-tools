[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# MkDocs and markdown-link-validator

The documentation of DSP-TOOLS is built with MkDocs (see [README](https://github.com/dasch-swiss/dsp-tools#readme)).
Please consider the following caveats:



## Styling Constraints in the Documentation

In our GitHub actions, we check PRs for dead links in the documentation. 
Our tool [markdown-link-validator](https://github.com/webhintio/markdown-link-validator) is only able to check internal links
if they start with `./`. For example:

- `[prefixes]⁣(./dsp-tools-create.md#prefixes-object)` instead of  
  `[prefixes](dsp-tools-create.md#prefixes-object)`
- `![Colors_en]⁣(./assets/images/img-list-english-colors.png)` instead of  
  `![Colors_en](assets/images/img-list-english-colors.png)`

It is okay, however, to make an internal link to a title of the current document:
`[prefixes]⁣(#prefixes-object)`

Please follow this constraint, so that markdown-link-validator can check the internal links.



## Handling False Positives of markdown-link-validator

What can be done if your links are correct, but markdown-link-validator doesn't recognize them?
One solution is to add an "ignore" pattern 
to the call to markdown-link-validator in `.github/workflows/tests-on-push.yml`.

If your link is in a code block, and isn't intended to be used as link,
you can also add an invisible Unicode character, like in the examples above.



## No Duplicate Headings, No Special Characters in Headings

When linking to a heading, the name heading is slugified.
Unfortunately, there are different flavors of Markdown, and different slug algorithms.
As long as the heading is unique in the document, and doesn't contain special characters, there is no problem.

But consider a document like this:

```markdown
# Heading / Title
First heading with this name

# Heading / Title
Second heading with this name

# Further down in the document
[link to second heading]⁣(#heading-title_1)    <!--MkDocs supports only this syntax-->
[link to second heading]⁣(#heading--title-1)   <!--npm markdown-link-validator supports only this syntax-->
```

To make things worse, different IDEs use different slug algorithms, too, 
which might lead to misleading hints from the IDE.

The real danger lies within MkDocs: while it doesn't support the `heading--title-1` syntax, 
it doesn't complain if you use it, not even when using the `--strict` flag.
This can lead to broken links on [https://docs.dasch.swiss/](https://docs.dasch.swiss/), 
without anyone noticing.


### The Best Solution How to Deal With This

- **give a unique name to every heading within the same document**
- **don't use special characters in headings**


### A Short Overview of Markdown Tools and Slug Algorithms

- MkDocs uses [Python Markdown](https://python-markdown.github.io/) to translate Markdown files into HTML
  (see [here](https://www.mkdocs.org/user-guide/configuration/#markdown_extensions)).
- Python Markdown's default slugify used to strip out all Unicode chars
  (see [here](https://facelessuser.github.io/pymdown-extensions/extras/slugs/)).
- markdown-link-validator uses [uslug](https://www.npmjs.com/package/uslug) to create the slugs 
  (see [here](https://github.com/webhintio/markdown-link-validator/blob/main/src/lib/mdfile.ts)).
- VS Code targets the CommonMark Markdown specification using the 
  [markdown-it](https://github.com/markdown-it/markdown-it) library
  (see [here](https://code.visualstudio.com/docs/languages/markdown#_does-vs-code-support-github-flavored-markdown)). 

Another useful reading is [here](https://github.com/yzhang-gh/vscode-markdown/issues/807).
