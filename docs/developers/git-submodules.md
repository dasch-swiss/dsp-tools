[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Git Submodules

This repository embeds 
[https://github.com/dasch-swiss/00A1-import-scripts](https://github.com/dasch-swiss/00A1-import-scripts) 
as a Git submodule in `src/dsp_tools/import_scripts`. That means that `src/dsp_tools/import_scripts` has no contents, but
only a reference to a certain commit in the main branch of `00A1-import-scripts`. When you clone DSP-TOOLS from GitHub 
as usual, `src/dsp_tools/import_scripts` will be empty.



## Rationale to Use a Git Submodule

The code of the `00A1-import-scripts` repository is closely related to the documentation of the `excel2xml` module. 
When something changes in `excel2xml`, the changes need not only be reflected in the docs, but also in 
`00A1-import-scripts`. This can easily be forgotten. The decision to embed it as a submodule is meant to bring 
`00A1-import-scripts` closer to the attention of the developers of DSP-TOOLS. For example, a repo-wide search for a 
string or the usage of a method will also yield results from `00A1-import-scripts`.

The example project [rosetta](https://github.com/dasch-swiss/082E-rosetta-scripts) is a similar case. Changes in 
DSP-TOOLS sometimes need to be reflected in rosetta. But since rosetta is not embedded as submodule, the developers 
have to take care not to forget rosetta.

The contents of `src/dsp_tools/import_scripts` need not be part of the distribution, because the users of DSP-TOOLS 
will access these files via GitHub, and not via the distributed code. For this reason, this folder is excluded in 
`pyproject.toml`.



## Passively Using the Contents of the Submodule

If you don't have a clone of DSP-TOOLS yet, clone it with 

```bash
git clone --recurse-submodules https://github.com/dasch-swiss/dsp-tools.git
```

After cloning it that way, and after some time has passed, you might want to get the latest changes from GitHub:

```bash
cd dsp-tools
git pull --recurse-submodules
```

These two commands take care of the submodule, so that its contents are cloned/pulled as well. 

In case you have an old clone of DSP-TOOLS, without the submodule, and you want to update it, you have to proceed 
differently: 

```bash
cd dsp-tools
git pull
git submodule update --init --recursive
```

Some notes:

- `git clone --recurse-submodules <repo>` is shorthand for `git clone <repo>; cd <repo>; git submodule update --init --recursive`
- `git pull --recurse-submodules` is shorthand for `git pull; git submodule update --init --recursive`
- `--init` is necessary if you don't have the submodule `src/dsp_tools/import_scripts` yet. In all successive calls, 
  when the submodule is already on your machine, the flag `--init` can be omitted.
- `--recursive` is optional, in case there would be more than one (nested) submodules in the repository. 
- Since Git 2.15, you can tell Git to use `--recurse-submodules` for all commands that support it (except `clone`), 
  with `git config submodule.recurse true`.
- These explanations rely on [the Git Submodules documentation](https://git-scm.com/book/en/v2/Git-Tools-Submodules)



## Renaming a Parent Directory of the Submodule

Renaming a parent directory of the submodule should be done with `git mv old-name new-name`, so that git won't be 
confused that the path to the submodule changed. If this doesn't help, it might be necessary to manually modify: 

- the `gitdir` in `src/dsptools/import_scripts/.git`,
- the `path` in `.gitmodules`, and the name of the submodule in the title of that file,
- the `worktree` entry in `.git/modules/knora/dsplib/import_scripts/config` and the affected folder names in 
  the path containing that file.


## Actively Working with the Contents of the Submodule

After retrieving the contents of a submodule as described in the paragraph above, 
it is in "detached HEAD" state. 
Before committing to it, 
the `main` branch needs to be checked out. 
The order how to proceed is the following:

```bash
cd src/dsp_tools/import_scripts
git checkout main                     # check out main branch of 00A1-import-scripts
# (modify contents of submodule)
git add .
git commit -m "modify submodule"
git push origin main                  # push to origin of 00A1-import-scripts
cd ../../..
git add src/dsp_tools/import_scripts
git commit -m "modify submodule"
git push origin feature-branch        # push to origin of dsp-tools
```

When switching between branches, there are two options:

1. By default, (`submodule.recurse` is false AND branches are switched with `git checkout <branch>`), the contents of 
   submodules will not be updated.
2. If `submodule.recurse` has been set to true, OR if branches are switched with `git checkout <branch> 
    --recurse-submodules`, the contents of submodules will be updated according to the commit recorded in the 
   super-project. If local modifications in a submodule would be overwritten, the checkout will fail.

To quickly switch between branches when you have uncommitted work in the submodule, the first option might be 
preferable. After merging a Pull Request and switching back to the main branch, the second option might be more 
suitable. Read more about the checkout options in 
[the official documentation](https://git-scm.com/docs/git-checkout#Documentation/git-checkout.txt---recurse-submodules)
