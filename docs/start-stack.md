[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Run the DSP Stack on Your Local Machine 

DSP-API is the heart of the DaSCH service platform. 
It is a server application for archiving data from the Humanities. 
DSP-APP is a generic user interface for the user to look at and work with data stored in DSP-API. 
It's a server application, too. 
For testing purposes, it is sometimes necessary to run DSP-API and DSP-APP on a local machine. 
There are two ways to do this:

- simple: run [`dsp-tools start-stack`](./cli-commands.md#start-stack)
- advanced: execute commands from within the DSP-API/DSP-APP repositories

Here's an overview of the two ways:

|                             | simple                                    | advanced                                                                 |
| --------------------------- | ----------------------------------------- | ------------------------------------------------------------------------ |
| target group                | researchers, RDU employees                | developers of DSP-API or DSP-APP                                         |
| how it works                | run `dsp-tools start-stack`               | execute commands from within locally cloned DSP-API/DSP-APP repositories |
| software dependencies       | Docker, Python, DSP-TOOLS                 | XCode command line tools, Docker, sbt, Java, Angular, node, yarn         |
| mechanism in the background | run pre-built Docker images               | build DSP-API and DSP-APP from a branch in the repository                |
| available versions          | latest released version, or `main` branch | any branch, or locally modified working tree                             |
| caveats                     |                                           | dependencies must be kept up to date                                     |

!!! note "Login credentials for DSP-APP"

    To gain system administration rights inside a locally running DSP-APP, 
    login with username `root@example.com` and password `test`.


## The Simple Way: `dsp-tools start-stack`

The [`start-stack`](./cli-commands.md#start-stack) command runs Docker images 
with the latest released versions of DSP-API and DSP-APP, 
i.e. the versions that are running on [https://app.dasch.swiss](https://app.dasch.swiss).
(Optionally, you can specify to run the latest development version of DSP-API, from the `main` branch.)

The only prerequisite for this is that Docker is running, 
and that you have Python and DSP-TOOLS installed.

Some notes:

- As long as you want to keep the data in the database, don't execute `dsp-tools stop-stack`. 
- It is possible to leave DSP-API up for a long time. 
  If you want to save power, you can pause Docker. 
  When you resume it, DSP-API will still be running, in the state how you left it.
- You can also send your computer to sleep while the DSP stack is running. 
  For this, you don't even need to pause Docker.



### When Should I Restart the DSP-API?

After creating a data model and adding some data into your local DSP stack, 
you can work on DSP as if it was the live platform. 
But there are certain actions that are irreversible or can only be executed once, 
e.g. uploading the same JSON project file. 
If you edit your data model in the JSON file, 
and you want to upload it a second time, 
DSP-API will refuse to create the same project again. 
So, you might want to restart the stack and start over again from a clean setup.

It is possible, however, to modify the XML data file and upload it again and again. 
But after some uploads, DSP is cluttered with data, so you might want to restart the stack.



## The Advanced Way

If you want to run a specific branch of DSP-API / DSP-APP, or to modify them yourself, you need to:

- install the dependencies: 
  follow the instructions on [https://github.com/dasch-swiss/dsp-api](https://github.com/dasch-swiss/dsp-api)
  and [https://github.com/dasch-swiss/dsp-das](https://github.com/dasch-swiss/dsp-das)
- keep the dependencies up to date (keep in mind that dependencies might be replaced over time)
- clone the repositories from GitHub
- keep them up to date with `git pull`
- execute commands from within the repositories (`just` for DSP-API, `angular` for DSP-APP)
- take care that the repositories don't get cluttered with old data over time
