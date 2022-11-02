#! /bin/bash
# make this file executable with chmod u+x (filename).sh
set -u  # exit if an uninitialised variable is used (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)
set -e  # exit if any statement returns a non-true return value (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)

[[ ! "$OSTYPE" == "darwin"* ]] && printf "\e[31mERROR: This command can only be run on a Mac. You don't seem to use a Mac.\e[0m\n" && return
[[ $(docker stats --no-stream 2>/dev/null ) == "" ]] && printf "\e[31mERROR: Docker is not running, so there is no DSP-API to shut down.\e[0m\n" && return

logfile="../dsp-api-stackdown.log"

cd ~
[[ ! -d .dsp-tools/dsp-api ]] && return
cd .dsp-tools/dsp-api
rm -f "$logfile"
echo "make stack-down-delete-volumes ..." 2>&1 | tee -a "$logfile"
make stack-down-delete-volumes >>"$logfile" 2>&1
echo "make clean-sipi-tmp ..." 2>&1 | tee -a "$logfile"
make clean-sipi-tmp >>"$logfile" 2>&1
echo "make clean-sipi-projects ..." 2>&1 | tee -a "$logfile"
make clean-sipi-projects >>"$logfile" 2>&1
