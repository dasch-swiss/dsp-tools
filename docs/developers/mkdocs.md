[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# MkDocs and Link Checking

The documentation of DSP-TOOLS is built with MkDocs (see [README](https://github.com/dasch-swiss/dsp-tools#readme)).
Please consider the following caveats:



## Who Checks Which Links

Two separate mechanisms check the links in `docs/`, and they are deliberately not interchangeable:

| Mechanism | Checks | Runs |
|---|---|---|
| `mkdocs build --strict` | internal links between docs, `#heading` anchors, `nav` completeness | on every PR, as the required `check-docs` status check |
| [lychee](https://github.com/lycheeverse/lychee) (`just check-links`) | external `http(s)` links | weekly, in `check-external-links.yml`, and on demand |

Internal links and anchors are validated offline by MkDocs itself,
via the `validation:` block in `mkdocs.yml`.
Because MkDocs slugifies the headings with the very algorithm that produces the published site,
its verdict on an anchor is authoritative.

External links are *not* a required check.
They depend on roughly forty third-party hosts staying reachable
and not rate-limiting the GitHub runners,
so as a merge gate they fail for reasons that have nothing to do with the pull request under test.
A weekly run catches link rot just as well, since links rot with time rather than with commits.



## Handling False Positives of the External Link Check

If a link is correct but lychee cannot reach it —
typically a host that answers `403` to any non-browser client —
add an exclusion pattern to `lychee.toml`, with a comment saying why.
Retries and rate-limit tolerance are already configured there,
so reach for an exclusion only after confirming by hand that the link is fine.

If your link is in a code block, and isn't intended to be used as link,
you can also add an invisible Unicode character, like in the examples below.



## No Duplicate Headings, No Special Characters in Headings

When linking to a heading, the heading name is slugified.
Unfortunately, there are different flavors of Markdown, and different slug algorithms.
As long as the heading is unique in the document, and doesn't contain special characters, there is no problem.

But consider a document like this:

```markdown
# Heading / Title
First heading with this name

# Heading / Title
Second heading with this name

# Further down in the document
[link to second heading]⁣(#heading-title_1)    <!--the syntax MkDocs generates-->
```

Different IDEs use different slug algorithms, too,
which might lead to misleading hints from the IDE.
`mkdocs build --strict` is the arbiter: with `validation.anchors` enabled it fails the build
on an anchor that does not exist on the published site,
so a link of this kind cannot reach `https://docs.dasch.swiss/` unnoticed.


### The Best Solution How to Deal With This

- **give a unique name to every heading within the same document**
- **don't use special characters in headings**


### A Short Overview of Markdown Tools and Slug Algorithms

- MkDocs uses [Python Markdown](https://python-markdown.github.io/) to translate Markdown files into HTML
  (see [here](https://www.mkdocs.org/user-guide/configuration/#markdown_extensions)).
- Python Markdown's default slugify transliterates Extended Latin to ASCII (`žlutý` becomes `zluty`),
  drops what it cannot transliterate, and strips punctuation
  (see [here](https://facelessuser.github.io/pymdown-extensions/extras/slugs/)).
- VS Code targets the CommonMark Markdown specification using the 
  [markdown-it](https://github.com/markdown-it/markdown-it) library
  (see [here](https://code.visualstudio.com/docs/languages/markdown#_does-vs-code-support-github-flavored-markdown)). 

Another useful reading is [here](https://github.com/yzhang-gh/vscode-markdown/issues/807).
