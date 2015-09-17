#!/bin/sh

taskname='nome_sorgente_contestant'

FILES='c fast_c cpp fast_cpp pascal fast_pascal'

run_test() {
    pushd $1

    for name in grader fast_grader
    do
        rm -f $name.c $name.cpp $name.pas $name.o $name.ppu
    done

    # If needed, delete the input file
    if [ -f input.py ]; then
        rm -f input.txt
    fi
    if [ -f input.cpp ]; then
        rm -f input.txt
        rm -f input
    fi

    for name in $FILES
    do
        echo $name

        rm -f $name.time
        rm -f $name.out
        rm -f $name
    done

    popd
}


TESTS=$(find . -name "test*" -type d | sort -V)

for i in $TESTS
do
    run_test $i
done

tree -C