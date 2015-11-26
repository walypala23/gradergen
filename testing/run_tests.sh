#!/bin/sh

taskname='nome_sorgente_contestant'

RED='\033[0;31m'
ORANGE='\033[0;33m'
NC='\033[0m' # No Color
OK='\033[92m✓\033[0m'
NOTOK='\033[91m✗\033[0m'

FILES='c fast_c cpp fast_cpp pascal fast_pascal'

run_test() {
    pushd $1
    gradergen --all 2> $1.errors

    exitcode=$?
    if [ $exitcode != "0" ]
    then
        for name in $FILES
        do
            cat $1.errors > $name.out
        done
        popd
        return
    fi

    # If needed, create the input file
    if [ -f input.py ]; then
        python input.py > input.txt
    fi
    if [ -f input.cpp ]; then
        g++ input.cpp -O2 -o input >/dev/null 2>/dev/null && ./input > input.txt
    fi

    echo -n "Compiling stuff... "

    (gcc -Wall -DEVAL -O2 grader.c $taskname.c -o c >/dev/null 2>/dev/null \
      && gcc -Wall -DEVAL -O2 fast_grader.c $taskname.c -o fast_c >/dev/null 2>/dev/null \
      && g++ -Wall -DEVAL -O2 grader.cpp $taskname.cpp -o cpp >/dev/null 2>/dev/null \
      && g++ -Wall -DEVAL -O2 fast_grader.cpp $taskname.cpp -o fast_cpp >/dev/null 2>/dev/null \
      && fpc -dEVAL grader.pas -opascal >/dev/null 2>/dev/null \
      && fpc -dEVAL fast_grader.pas -ofast_pascal >/dev/null 2>/dev/null \
      && echo -e $OK) || echo -e $NOTOK

    for name in $FILES
    do
        echo -n "Running $name... "

        #'time' -f "%e" ./$name 2> $name.time
        (./$name && echo -e $OK) || echo -e $NOTOK
        # echo "x.xx" > $name.time

        mv output.txt $name.out
    done

    popd
}


if [ -z "$1" ]
then
    TESTS=$(find . -name "test*" -type d | sort -V)
else
    TESTS=(test$1)
fi

# Ensure that gradergen is installed
pushd ..
echo -n "Installation of gradergen... "
((python setup.py install >/dev/null 2>/dev/null || sudo python setup.py install >/dev/null 2>/dev/null) && echo -e $OK) || echo -e $NOTOK
popd

for i in $TESTS
do
    for j in $FILES
    do
        rm -f $i/$j
        rm -f $i/$j.out
        # rm -f $i/$j.time
    done

    run_test $i
done

chosen_color=$RED

for i in $TESTS
do
    printf "${chosen_color}"
    for j in $FILES
    do
        # echo -n "("$(cat $i/$j.time)"s) "
        md5sum $i/$j.out
    done
    cat $i/correct.md5

    printf "${NC}"

    if [ "$chosen_color" == "$RED" ]; then
        chosen_color=$ORANGE;
    else
        chosen_color=$RED;
    fi
done
