#! /bin/bash
# make this file executable with chmod u+x (filename).sh
set -u  # exit if an uninitialised variable is used (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)
set -e  # exit if any statement returns a non-true return value (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)

[[ ! "$OSTYPE" == "darwin"* ]] && echo "This command can only be run on a Mac. You don't seem to use a Mac." && return
[[ "$(npm -g outdated)" =~ .*@angular/cli.* ]] || printf "\e[31mWARNING: Your Angular seems to be outdated. Please update it with \"npm update -g @angular/cli\"\e[0m\n"

logfile="../dsp-app-startup.log"
rm -f "$logfile"

cd ~
mkdir -p .dsp-tools
cd .dsp-tools
if [[ ! -d dsp-app ]]; then
    echo "git clone https://github.com/dasch-swiss/dsp-app.git"
    git clone https://github.com/dasch-swiss/dsp-app.git >>"$logfile"
fi
cd dsp-app

echo "git pull ..."
git checkout HEAD package-lock.json >>"$logfile"
git pull >>"$logfile"
echo "npm i --legacy-peer-deps ..."
npm i --legacy-peer-deps >>"$logfile"
echo "ng s ..."
npm run ng s >>"$logfile"
echo "DSP-APP is now available at https://localhost:4200/"
