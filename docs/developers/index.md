[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Developers Documentation

These pages contain important background information 
for developers of the DSP-TOOLS code repository, 
as well as Architectural Decision Records.

Please read the [README](https://github.com/dasch-swiss/dsp-tools#readme) first.

# Custom Set-Up

## Log File Location 

The log files are by default saved in `~/.dsp-tools/logs/`.
Every DSP-TOOLS run creates a new log file.
If you prefer 1 single log file across all DSP-TOOLS runs, in the current working directory, 
then set the following variable in an `.env` file:


  ```env
  DSP_TOOLS_SAVE_ADDITIONAL_LOG_FILE_IN_CWD=true
  ```
