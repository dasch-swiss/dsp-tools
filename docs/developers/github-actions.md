[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

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
These must be added as ignore patterns,
cf. the flag `-i \.assets\/.+` in the code snippet below.

Secondly, external links to private pages raise an error, even though they are correct. 
An example is the link to `https://github.com/dasch-swiss/dsp-tools/settings` above.
To make markdown-link-validator work, the following flag is necessary: 
`-i .+github\.com\/dasch\-swiss\/dsp-tools\/settings`

So finally, this is the call to markdown-link-validator:

```bash
markdown-link-validator ./docs -i \.assets\/.+ -i .+github\.com\/dasch\-swiss\/dsp-tools\/settings
```

As the documentation grows, and new titles are added,
it might be necessary to adapt this call!
