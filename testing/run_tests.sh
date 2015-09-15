#!/bin/sh

taskname='nome_sorgente_contestant'

RED='\033[0;31m'
ORANGE='\033[0;33m'
NC='\033[0m' # No Color

FILES='c fast_c cpp fast_cpp pascal fast_pascal'

run_test() {
    pushd ..

    gradergen testing/$1/grader_description.txt --all --task-name $taskname
    for name in grader.c grader.cpp grader.pas fast_grader.c fast_grader.cpp fast_grader.pas
    do
        mv $name testing/$1/$name
    done

    popd
    pushd $1

    # If needed, create the input file
    if [ -f input.py ]; then
        python input.py > input.txt
    fi
    if [ -f input.cpp ]; then
        g++ input.cpp -O2 -o input && ./input > input.txt
    fi

    gcc -Wall -DEVAL -O2 grader.c $taskname.c -o c
    gcc -Wall -DEVAL -O2 fast_grader.c $taskname.c -o fast_c
    g++ -Wall -DEVAL -O2 grader.cpp $taskname.cpp -o cpp
    g++ -Wall -DEVAL -O2 fast_grader.cpp $taskname.cpp -o fast_cpp
    fpc -dEVAL grader.pas -opascal
    fpc -dEVAL fast_grader.pas -ofast_pascal

    for name in $FILES
    do
        echo $name

        #'time' -f "%e" ./$name 2> $name.time
        ./$name
        echo "x.xx" > $name.time

        mv output.txt $name.out
    done

    popd
}


TESTS=$(find . -name "test*" -type d | sort -V)

for i in $TESTS
do
    for j in $FILES
    do
        rm -f $i/$j
        rm -f $i/$j.out
    done

    run_test $i
done

chosen_color=$RED

for i in $TESTS
do
    printf "${chosen_color}"
    for j in $FILES
    do
        echo -n "("$(cat $i/$j.time)"s) "
        md5sum $i/$j.out
    done
    printf "${NC}"

    if [ "$chosen_color" == "$RED" ]; then
        chosen_color=$ORANGE;
    else
        chosen_color=$RED;
    fi
done
