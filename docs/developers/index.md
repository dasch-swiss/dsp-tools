[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Developers Documentation

These pages contain important background information 
for developers of the DSP-TOOLS code repository, 
as well as Architectural Decision Records.

Please read the [README](https://github.com/dasch-swiss/dsp-tools#readme) first.

# Custom Set-Up

## Log File Location 

The log files are by default saved in `~/.dsp-tools/logs/`, 
if you want to have a copy of the log file in the current working directory as well, 
set the following variable in an `.env` file.

Example `.env` file content:

  ```env
  SAVE_ADDITIONAL_LOG_FILE_IN_CWD=true
  ```
