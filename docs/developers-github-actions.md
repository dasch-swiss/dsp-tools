[![DSP-TOOLS](https://img.shields.io/github/v/release/dasch-swiss/dsp-tools?include_prereleases&label=DSP-TOOLS)](https://github.com/dasch-swiss/dsp-tools)

# GitHub actions

GitHub actions are workflows that are (remotely) run by GitHub 
if a certain event happens.
Actions are defined in YML files in the `.github/workflows` folder.
The YML files define 

- by what event an action is triggered
- what the action should do

The syntax of the YML files is documented 
on the [GitHub actions documentation page](https://docs.github.com/en/actions).

It can be defined in the [settings of the repository](https://github.com/dasch-swiss/dsp-tools/settings) 
what happens if an action fails,
e.g. an email is sent to the maintainer,
or a PR is blocked from being merged, etc.



## check-pr-title.yml

This action checks if the title of the PR complies with a certain regex.



## publish-to-pypi.yml

This action is triggered when a Release-Please-PR (see below) is merged.
Basically, this action calls `poetry build` and `poetry publish`.



## release-please.yml

When a PR is merged to main, this action creates a Release-Please-PR. 
This is a PR that increments the version number of DSP-TOOLS,
and adds a synopsis of the PRs merged since the last release to the changelog.
When this PR is merged, the `publish-to-pypi.yml` action is triggered.



## tests-on-push.yml

In the settings of the DSP-TOOLS repository, 
these tests are configured to be mandatory to pass before a PR can be merged.
Basically, this action checks that

- the docs can be built without errors or warnings
- there are no dead links in the docs
- the unit tests run without errors
- the end-to-end tests run without errors

Checking dead links is a non-trivial task. 
There are several tools for it, 
but the only one which works for our purpose is 
[markdown-link-validator](https://www.npmjs.com/package/markdown-link-validator).

There are some caveats, though:

Firstly, markdown-link-validator doesn't recognize internal links to files in the `docs/assets` folder.
These must be added as ignore patterns
(cf. the flag `-i \.assets\/.+` in the code snippet below).

Secondly, MkDocs requires that special characters (like `"` or `<`) in a title must be omitted 
when referring the title in an internal link, 
otherwise the link won't work on the rendered page. 
This is tricky, because some tools like PyCharm or markdown-link-validator require a placeholder in the internal link.
For example:

- Title: `### &lt;geometry-prop&gt;`
- MkDocs requires: `[internal link](./dsp-tools-xmlupload.md#geometry-prop)`
- markdown-link-validator requires: `[internal link](./dsp-tools-xmlupload.md#ltgeometry-propgt)`  

The only choice we have is to follow the MkDocs requirement, and to ignore PyCharm and markdown-link-validator errors.
For this reason, the code snippet below has the flags

- `-i \.\/dsp\-tools\-xmlupload\.md\#.+\-prop`
- `-i \.\/dsp\-tools\-xmlupload\.md\#bitstream`
- `-i \.\/dsp\-tools\-xmlupload\.md\#.+permissions\-element`

As you can see in the regex, 
the two flags only ignore such links if they start with `dsp-tools-xmlupload.md#`. 
For this reason, titles inside that file cannot be referenced like this: `[link]‌(#geometry-prop)`, 
but must be in the full form: `[link](./dsp-tools-xmlupload.md#geometry-prop)`.

Thirdly, external links to private pages raise an error, even though they are correct. 
An example is the link to `https://github.com/dasch-swiss/dsp-tools/settings` above.
To make markdown-link-validator work, the following flag is necessary: `-i .+github\.com\/dasch\-swiss\/dsp-tools\/settings`

So finally, the following call to markdown-link-validator works:

```bash
markdown-link-validator ./docs -i \.assets\/.+ -i \.\/dsp\-tools\-xmlupload\.md\#.+\-prop -i \.\/dsp\-tools\-xmlupload\.md\#bitstream -i \.\/dsp\-tools\-xmlupload\.md\#.+permissions\-element -i .+github\.com\/dasch\-swiss\/dsp-tools\/settings
```

As the documentation grows, and new titles are added,
it might be necessary to adapt this call!
