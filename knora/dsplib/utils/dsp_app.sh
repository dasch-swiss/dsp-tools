#! /bin/bash
# make this file executable with chmod u+x (filename).sh
set -u  # exit if an uninitialised variable is used (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)
set -e  # exit if any statement returns a non-true return value (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)

[[ "$(npm -g outdated)" =~ .*@angular/cli.* ]] || printf "\e[31mWARNING: Your Angular seems to be outdated. Please update it with \"npm update -g @angular/cli\"\e[0m\n"

cd ~
mkdir -p .dsp-tools
cd .dsp-tools
if [[ ! -d dsp-app ]]; then
    git clone https://github.com/dasch-swiss/dsp-app.git
fi
cd dsp-app

echo "git pull ..."
git checkout HEAD package-lock.json >../dsp-app-startup.log
git pull >../dsp-app-startup.log
echo "npm i --legacy-peer-deps ..."
npm i --legacy-peer-deps >../dsp-app-startup.log
echo "ng s ..."
npm run ng s >../dsp-app-startup.log
echo "DSP-APP is now available at https://localhost:4200/"
