#! /bin/bash
# make this file executable with chmod u+x (filename).sh
set -u  # exit if an uninitialised variable is used (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)
set -e  # exit if any statement returns a non-true return value (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)

[[ ! "$OSTYPE" == "darwin"* ]] && printf "\e[31mERROR: This command can only be run on a Mac. You don't seem to use a Mac.\e[0m\n" && return
[[ "$(npm -g outdated)" =~ .*@angular/cli.* ]] || printf "\e[31mWARNING: Your Angular seems to be outdated. Please update it with \"npm update -g @angular/cli\"\e[0m\n"

logfile="../dsp-app-startup.log"

cd ~
mkdir -p .dsp-tools
cd .dsp-tools
if [[ ! -d dsp-app ]]; then
    echo "git clone https://github.com/dasch-swiss/dsp-app.git" 2>&1 | tee -a "$logfile"
    git clone https://github.com/dasch-swiss/dsp-app.git >>"$logfile" 2>&1
fi
cd dsp-app
rm -f "$logfile"

if echo -e "GET http://google.com HTTP/1.0\n\n" | nc google.com 80 -w 10 > /dev/null 2>&1; then
    # only pull if there is an internet connection
    echo "git pull ..." 2>&1 | tee -a "$logfile"
    git checkout HEAD package-lock.json >>"$logfile" 2>&1
    git pull >>"$logfile" 2>&1
fi
echo "npm i --legacy-peer-deps ..." 2>&1 | tee -a "$logfile"
npm i --legacy-peer-deps >>"$logfile" 2>&1
echo "ng s ..." 2>&1 | tee -a "$logfile"
npm run ng s >>"$logfile" 2>&1
echo "DSP-APP is now available at https://localhost:4200/" 2>&1 | tee -a "$logfile"
