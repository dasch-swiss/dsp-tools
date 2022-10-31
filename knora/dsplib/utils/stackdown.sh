#! /bin/bash
# make this file executable with chmod u+x (filename).sh
set -u  # exit if an uninitialised variable is used (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)
set -e  # exit if any statement returns a non-true return value (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)

cd ~
[[ ! -d .dsp-tools/dsp-api ]] && return
cd .dsp-tools/dsp-api
echo "make stack-down-delete-volumes ..."
make stack-down-delete-volumes >../dsp-api-stackdown.log
echo "make clean-sipi-tmp ..."
make clean-sipi-tmp >../dsp-api-stackdown.log
echo "make clean-sipi-projects ..."
make clean-sipi-projects >../dsp-api-stackdown.log
