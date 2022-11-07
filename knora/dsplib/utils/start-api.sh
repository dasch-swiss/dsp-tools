#! /bin/bash
# make this file executable with chmod u+x (filename).sh
set -u  # exit if an uninitialised variable is used (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)
set -e  # exit if any statement returns a non-true return value (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)

# only allow to run this command if Docker is running
[[ $(docker stats --no-stream 2>/dev/null ) == "" ]] && printf "\e[31mERROR: Please start Docker before running DSP-API.\e[0m\n" && return

# check dependencies
echo "check for outdated dependencies..."
[[ "$(brew outdated)" != "" ]] && printf "\e[31mWARNING: Some of your Homebrew formulas/casks are outdated. Please execute \"brew upgrade\"\e[0m\n"
shopt -s nocasematch
[[ "$(java --version)" =~ $? ]] || printf "\e[31mWARNING: Your JDK seems to be outdated. Please install JDK 17 Temurin.\e[0m\n"
if echo -e "GET http://google.com HTTP/1.0\n\n" | nc google.com 80 -w 10 > /dev/null 2>&1; then
    # pip should only be called if there is an internet connection
    outdated_pip_packages="$(pip list --outdated)"
    [[ "$outdated_pip_packages" =~ .*dsp-tools.* ]] && printf "\e[31mWARNING: Your version of dsp-tools is outdated. Please update it with \"pip install --upgrade dsp-tools\"\e[0m\n"
    [[ "$outdated_pip_packages" != "" ]] && printf "\e[31mWARNING: Some of your pip packages are outdated. List them with \"pip list --outdated\" and consider updating them with \"pip install --upgrade (package)\"\e[0m\n"
fi

logfile="../dsp-api-stackup.log"

cd ~
mkdir -p .dsp-tools
cd .dsp-tools
if [[ ! -d dsp-api ]]; then
    echo "git clone https://github.com/dasch-swiss/dsp-api.git" 2>&1 | tee -a "$logfile"
    git clone https://github.com/dasch-swiss/dsp-api.git >>"$logfile" 2>&1
fi
cd dsp-api
rm -f "$logfile"
echo "make stack-down-delete-volumes..." 2>&1 | tee -a "$logfile"
make stack-down-delete-volumes >>"$logfile" 2>&1
if echo -e "GET http://google.com HTTP/1.0\n\n" | nc google.com 80 -w 10 > /dev/null 2>&1; then
    # only pull if there is an internet connection
    echo "git pull ..." 2>&1 | tee -a "$logfile"
    git pull >>"$logfile" 2>&1
fi
echo "make init-db-test..." 2>&1 | tee -a "$logfile"
make init-db-test >>"$logfile" 2>&1
echo "make stack-up..." 2>&1 | tee -a "$logfile"
make stack-up >>"$logfile" 2>&1
echo "DSP-API is up and running."   # due to "set -e", this will only be printed if everything went well
