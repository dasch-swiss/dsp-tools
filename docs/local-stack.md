[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)


# Getting Started with a Local Stack

With the following commands can start and stop an entire DSP Stack locally with Docker Containers.


## `start-stack`


This command runs a local instance of DSP-API and DSP-APP.

!!! note "Login credentials for DSP-APP"

  To gain system administration rights inside a locally running DSP-APP, 
  login with username `root@example.com` and password `test`.


```bash
dsp-tools start-stack
```

DSP-TOOLS will ask you for permission to clean Docker with a `docker system prune`.
This will remove all unused containers, networks and images.
If you don't know what that means, just type `y` ("yes") and then `Enter`.

The most frequently used options are:

- `--max_file_size=int` (optional, default: `2000`): max. multimedia file size allowed, in MB (max: 100'000)
  If you attempt to upload a multimedia file bigger than `max_file_size`, it will be rejected.
- `--prune` (optional): execute `docker system prune` without asking
- `--no-prune` (optional): don't execute `docker system prune` (and don't ask)
- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

To see all possible options, type `dsp-tools start-stack --help`.

A note on the flag `--max_file_size`, if you start the stack with `dsp-tools start-stack --max_file_size=1000`, 
it will be possible to upload files that are up to 1 GB big. 
If a file bigger than `max_file_size` is uploaded, 
the upload will be rejected.

More help for this command can be found [here](./developers/start-stack.md).


## `stop-stack`

When your work is done, shut down DSP-API and DSP-APP with

```bash
dsp-tools stop-stack
```

The most frequently used option is:

- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)


To see all possible options, type `dsp-tools stop-stack --help`.

This deletes all Docker volumes, and removes all data that was in the database.
