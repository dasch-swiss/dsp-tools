#! /bin/bash
# make this file executable with chmod u+x (filename).sh
set -u  # exit if an uninitialised variable is used (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)
set -e  # exit if any statement returns a non-true return value (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)

[[ ! "$OSTYPE" == "darwin"* ]] && echo "This command can only be run on a Mac. You don't seem to use a Mac." && return
[[ $(docker stats --no-stream 2>/dev/null ) == "" ]] && echo "Is Docker running? You need to start it before running DSP-API" && return

echo "check for outdated dependencies..."
[[ "$(brew outdated)" != "" ]] && printf "\e[31mWARNING: Some of your Homebrew formulas/casks are outdated. Please execute \"brew upgrade\"\e[0m\n"
[[ "$JAVA_HOME" =~ .*temurin.*17.* ]] || printf "\e[31mWARNING: Your JDK seems to be outdated. Please install JDK 17 Temurin.\e[0m\n"
if [[ $(echo -e "GET http://google.com HTTP/1.0\n\n" | nc google.com 80 > /dev/null 2>&1) -eq 0 ]]; then
    # pip should only be called if there is an internet connection
    [[ "$(pip list --outdated)" =~ .*dsp-tools.* ]] && printf "\e[31mWARNING: Your version of dsp-tools is outdated. Please update it with \"pip install --upgrade dsp-tools\"\e[0m\n"
    [[ "$(pip list --outdated)" != "" ]] && printf "\e[31mWARNING: Some of your pip packages are outdated. List them with \"pip list --outdated\" and consider updating them with \"pip install --upgrade (package)\"\e[0m\n"
fi

logfile="../dsp-api-stackup.log"
rm -f "$logfile"

cd ~
mkdir -p .dsp-tools
cd .dsp-tools
if [[ ! -d dsp-api ]]; then
    echo "git clone https://github.com/dasch-swiss/dsp-api.git"
    git clone https://github.com/dasch-swiss/dsp-api.git >>"$logfile"
fi
cd dsp-api
echo "make stack-down-delete-volumes..."
make stack-down-delete-volumes >>"$logfile"
echo "git pull ..."
git pull >>"$logfile"
echo "make init-db-test-minimal..."
make init-db-test >>"$logfile"
echo "make stack-up..."
make stack-up >>"$logfile"
