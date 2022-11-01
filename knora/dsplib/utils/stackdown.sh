#! /bin/bash
# make this file executable with chmod u+x (filename).sh
set -u  # exit if an uninitialised variable is used (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)
set -e  # exit if any statement returns a non-true return value (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)

[[ ! "$OSTYPE" == "darwin"* ]] && echo "This command can only be run on a Mac. You don't seem to use a Mac." && return
[[ $(docker stats --no-stream 2>/dev/null ) == "" ]] && echo "Docker is not running, so there is no DSP-API to shut down." && return

logfile="../dsp-api-stackdown.log"
rm -f "$logfile"

cd ~
[[ ! -d .dsp-tools/dsp-api ]] && return
cd .dsp-tools/dsp-api
echo "make stack-down-delete-volumes ..."
make stack-down-delete-volumes >>"$logfile"
echo "make clean-sipi-tmp ..."
make clean-sipi-tmp >>"$logfile"
echo "make clean-sipi-projects ..."
make clean-sipi-projects >>"$logfile"
