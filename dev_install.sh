#!/bin/sh
# Execute this script and then run 'workon gradergen-dev'.
# The first time you execute this, add the flag --first_time.
# The second time add the flag --second_time.
# The reason is that executing virtualenvwrapper commands seems to
# terminate the script.
set -e    # Exit when any command fails

export WORKON_HOME=~/.virtualenvs
source /usr/bin/virtualenvwrapper.sh

CreateVirtualenv() {
    mkvirtualenv -p python3 gradergen-dev
}

InstallRequirements() {
    source ~/.virtualenvs/gradergen-dev/bin/activate
    pip install -r requirements.txt
    pip install virtualenvwrapper
}

InstallGradergen() {
    source ~/.virtualenvs/gradergen-dev/bin/activate
    rm -r build/ dist/ gradergen.egg-info/
    python setup.py install
}

if test $# -gt 0; then
    case "$1" in
        --first_time)
            CreateVirtualenv
            ;;
        --second_time)
            InstallRequirements
            ;;
        *)
            echo -e "Unrecognized option. The only possible option is --first_time"
            exit 1
            ;;
    esac
else
    InstallGradergen
fi
