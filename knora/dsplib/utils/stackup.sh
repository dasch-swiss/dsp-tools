#! /bin/bash
# make this file executable with chmod u+x (filename).sh
set -u  # exit if an uninitialised variable is used (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)
set -e  # exit if any statement returns a non-true return value (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)

[[ "$(brew outdated)" != "" ]] && printf "\e[31mWARNING: You seem to have outdated Homebrew formulas/casks. Please execute \"brew upgrade\"\e[0m\n"
[[ "$(pip list --outdated)" =~ .*dsp-tools.* ]] && printf "\e[31mWARNING: Your dsp-tools is outdated. Please update it with \"pip install --upgrade dsp-tools\"\e[0m\n"
[[ "$(pip list --outdated)" != "" ]] && printf "\e[31mWARNING: You seem to have outdated pip packages. List them with \"pip list --outdated\" and consider updating them with \"pip install --upgrade (package)\"\e[0m\n"
[[ "$JAVA_HOME" =~ .*temurin.*17.* ]] || printf "\e[31mWARNING: Your JDK seems to be outdated. Please install JDK 17 Temurin.\e[0m\n"

cd ~
mkdir -p .dsp-tools
cd .dsp-tools
if [[ ! -d dsp-api ]]; then
    git clone https://github.com/dasch-swiss/dsp-api.git >../dsp-api-stackup.log
fi
cd dsp-api
echo "make stack-down-delete-volumes ..."
make stack-down-delete-volumes >../dsp-api-stackup.log
echo "git pull ..."
git pull >../dsp-api-stackup.log
echo "make init-db-test-minimal ..."
make init-db-test >../dsp-api-stackup.log
echo "make stack-up ..."
make stack-up >../dsp-api-stackup.log
