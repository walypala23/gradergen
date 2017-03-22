#!/bin/sh
# Execute this script and then run 'workon gradergen-dev'.
# The first time you execute this, add the flag --first_time.
set -e    # Exit when any command fails

source /usr/bin/virtualenvwrapper.sh

CreateVirtualenv() {
    mkvirtualenv -p python3 gradergen-dev
    workon gradergen-dev
    pip install -r requirements
    pip install virtualenvwrapper
}

InstallGradergen() {
    workon gradergen-dev
    rm -r build/ dist/ gradergen.egg-info/
    python setup.py install
}

if test $# -gt 0; then
    case "$1" in
        --first_time)
            CreateVirtualenv
            ;;
        *)
            echo -e "Unrecognized option. The only possible option is --first_time"
            exit 1
            ;;
    esac
fi

InstallGradergen
