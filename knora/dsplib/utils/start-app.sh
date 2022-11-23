#! /bin/bash
set -u  # exit if an uninitialised variable is used (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)
set -e  # exit if any statement returns a non-true return value (https://www.davidpashley.com/articles/writing-robust-shell-scripts/)

# check the dependencies with a timeout
check_dependencies () {
    echo "check for outdated dependencies..."
    if echo -e "GET http://google.com HTTP/1.0\n\n" | nc google.com 80 -w 10 > /dev/null 2>&1; then
        # # don't make network calls if there is no internet connection
        [[ "$(npm -g outdated)" =~ .*@angular/cli.* ]] || printf "\e[33mWARNING: You have outdated npm packages. List them with 'npm -g outdated' and update them with \"npm update -g (package)\"\e[0m\n"
    fi
}
export -f check_dependencies


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
    echo "git reset --hard HEAD ..." 2>&1 | tee -a "$logfile"
    git reset --hard HEAD >>"$logfile" 2>&1
    echo "git checkout main ..." 2>&1 | tee -a "$logfile"
    git checkout main >>"$logfile" 2>&1
    echo "git pull ..." 2>&1 | tee -a "$logfile"
    git pull >>"$logfile" 2>&1
fi

set +e
timeout --preserve-status 10s bash -c check_dependencies
set -e

echo "npm i ..." 2>&1 | tee -a "$logfile"
npm i >>"$logfile" 2>&1
echo "ng s ..." 2>&1 | tee -a "$logfile"
npm run ng s 2>&1 | tee -a "$logfile"
