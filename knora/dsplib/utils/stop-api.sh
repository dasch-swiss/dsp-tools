#! /bin/bash
set -u  # exit if an uninitialised variable is used (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)
set -e  # exit if any statement returns a non-true return value (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)

[[ $(docker stats --no-stream 2>/dev/null ) == "" ]] && printf "\e[31mERROR: Docker is not running, so there is no DSP-API to shut down.\e[0m\n" && exit 1

logfile="../dsp-api-stackdown.log"

cd ~
[[ ! -d .dsp-tools/dsp-api ]] && printf "\e[31mERROR: ~/.dsp-tools/dsp-api is not a directory, so there is no DSP-API to shut down.\e[0m\n" && exit 1
cd .dsp-tools/dsp-api
rm -f "$logfile"
echo "make stack-down-delete-volumes ..." 2>&1 | tee -a "$logfile"
make stack-down-delete-volumes >>"$logfile" 2>&1
echo "make clean-sipi-tmp ..." 2>&1 | tee -a "$logfile"
make clean-sipi-tmp >>"$logfile" 2>&1
echo "make clean-sipi-projects ..." 2>&1 | tee -a "$logfile"
make clean-sipi-projects >>"$logfile" 2>&1
