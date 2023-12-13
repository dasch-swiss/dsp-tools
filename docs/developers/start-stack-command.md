[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Maintaining the `start-stack` Command

The [start-stack command](../cli-commands.md#start-stack) 
starts Docker containers of DSP-API and DSP-APP, 
in the version that is running on [https://app.dasch.swiss](https://app.dasch.swiss/help). 
In addition to the containers, 
a number of files from the DSP-API GitHub repository is necessary. 
The version of the docker images and these files must be the same. 
The version is configured in the following files in `src/dsp_tools/resources/start-stack/`:

- `docker-compose.yml`: 
  The 5 variables `services/{app,db,sipi,api,ingest}/image` 
  must point to the DockerHub image of the last deployed version.
  The versions can be found in the
  [ops-deploy repo](https://github.com/dasch-swiss/ops-deploy/blob/main/roles/dsp-deploy/files/RELEASE.json)
- `start-stack-config.yml`: 
  The variable `DSP-API commit` 
  must be the commit hash of DSP-API 
  of the version that is running on [https://app.dasch.swiss](https://app.dasch.swiss/help).
  Just take the commit hash of the latest DSP-API release
  from the [DSP-API GitHub repo](https://github.com/dasch-swiss/dsp-api/commits/main)
