[![DSP-TOOLS](https://img.shields.io/github/v/release/dasch-swiss/dsp-tools?include_prereleases&label=DSP-TOOLS)](https://github.com/dasch-swiss/dsp-tools)

# How to maintain the `start-stack` command

The [start-stack command](../cli-commands.md#start-stack-stop-stack) starts Docker containers of 
DSP-API and DSP-APP, in the version that is running on [https://admin.dasch.swiss](https://admin.dasch.swiss/help). 
In addition to the containers, a number of files from the DSP-API GitHub repository is necessary. The version of the 
docker images and these files must be the same. The version is hardcoded at the following places in the code:

- `src/dsp_tools/docker/docker-compose.yml`: The 4 variables `services/{app,db,sipi,api}/image` must point to the 
  DockerHub image of the last deployed version
- `src/dsp_tools/utils/stack_handling.py`: The variable `commit_of_used_api_version` must be the commit hash of DSP-API 
  of the version that is running on [https://admin.dasch.swiss](https://admin.dasch.swiss/help).
