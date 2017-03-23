#!/bin/sh

##### Set options #####

#set -e    # Exit when any command fails
#set -x    # Debug (print executed commands)

#### Check needed packages #####

command -v chronic >/dev/null 2>&1 || { echo "You must install the 'moreutils' package. Aborting." >&2; exit 1; }

##### Constants #####

RED="\033[91m"
GREEN="\033[92m"
BOLDW="\e[1;37m"
NC="\033[0m" # No Color
OK="$GREEN✓\033[0m"
NOTOK="$RED✗\033[0m"

LANGUAGES=(C fast_C CPP fast_CPP pascal fast_pascal)
FILES=(c fast_c cpp fast_cpp pascal fast_pascal)

CHECK() {
    (chronic "$@" && echo -e $OK) || (echo -e $NOTOK && exit 1)
}

#### Install gradergen; Enter test directory ####

PYTHONPATH="$(pwd)"

cd testing

echo -n "Cleaning testing directories... "
CHECK ./cleanup.sh -q

mkdir -p pip_modules/lib/python
PYTHONPATH="$PYTHONPATH:$(realpath ./pip_modules/lib/python)"
export PYTHONPATH

echo -n "Installation of gradergen dependencies... "
CHECK pip install -t ./pip_modules -r ../requirements.txt

echo -n "Creation of 'gradergen' binary inside 'testing' folder... "
CHECK python ../setup.py install --home ./pip_modules --install-scripts .

compile_stuff() {
    echo "Compiling solutions and templates... "

    if [ -f grader.c ]; then
        echo -n "Compiling C "
        CHECK gcc -Wall -DEVAL -O2 grader.c soluzione.c -o c
        chronic gcc -Wall -DEVAL -O2 grader.c template_C.c -o template_C || touch template_c.errors
    fi
    if [ -f fast_grader.c ]; then
        echo -n "Compiling fast_C "
        CHECK gcc -Wall -DEVAL -O2 fast_grader.c soluzione.c -o fast_c
        chronic gcc -Wall -DEVAL -O2 fast_grader.c template_fast_C.c -o template_fast_C || touch template_fast_c.errors
    fi
    if [ -f grader.cpp ]; then
        echo -n "Compiling CPP "
        CHECK g++ -Wall -DEVAL -O2 grader.cpp soluzione.cpp -o cpp
        chronic g++ -Wall -DEVAL -O2 grader.cpp template_CPP.cpp -o template_cpp || touch template_cpp.errors
    fi
    if [ -f fast_grader.cpp ]; then
        echo -n "Compiling fast_CPP "
        CHECK g++ -Wall -DEVAL -O2 fast_grader.cpp soluzione.cpp -o fast_cpp
        chronic g++ -Wall -DEVAL -O2 fast_grader.cpp template_fast_CPP.cpp -o template_fast_CPP || touch template_fast_cpp.errors
    fi
    if [ -f grader.pas ]; then
        echo -n "Compiling pascal "
        cp soluzione.pas $taskname.pas
        CHECK fpc -dEVAL grader.pas -opascal
        rm *.o *.ppu # Otherwise fpc seems to be non-deterministic.
        
        cp template_pascal.pas $taskname.pas
        chronic fpc -dEVAL grader.pas -otemplate_pascal || touch template_pascal.errors
        rm *.o *.ppu # Otherwise fpc seems to be non-deterministic.
    fi
    if [ -f fast_grader.pas ]; then
        echo -n "Compiling fast_pascal "
        cp soluzione.pas $taskname.pas
        CHECK fpc -dEVAL fast_grader.pas -ofast_pascal
        rm *.o *.ppu # Otherwise fpc seems to be non-deterministic.

        cp template_pascal.pas $taskname.pas
        chronic fpc -dEVAL fast_grader.pas -otemplate_fast_pascal || touch template_fast_pascal.errors
        rm *.o *.ppu # Otherwise fpc seems to be non-deterministic.
    fi
    
    rm -f $taskname.pas
}

prepare_test_folder() {
    for index in {0..5}
    do
        language=${LANGUAGES[$index]}
        name=${FILES[$index]}
        echo $language $name
        chronic ../gradergen --lang $language 2> $name.out
        if [ $? != "0" ]
        then
            md5sum $name.out | awk '{print $1}' > $name.out.md5
        fi
    done

    echo

    # If needed, create the input file
    if [ -f input.py ]; then
        python input.py > input.txt
    fi
    if [ -f input.cpp ]; then
        chronic g++ input.cpp -O2 -o input \
          && ./input > input.txt
    fi

    # iolibgen stuff
    ln -s ../../gradergen/iolibgen/gradergen_io_lib.py gradergen_io_lib.py
    cp ../test_iolibgen.py test_iolibgen.py
}

run_test() {
    pushd $1 > /dev/null

    echo -e "Testing $1... "

    taskname=$(grep "name" task.yaml | cut -d":" -f2)
    taskname=${taskname:1}
    infile=$(grep "infile" task.yaml | cut -d":" -f2)
    infile=${infile:1}
    outfile=$(grep "outfile" task.yaml | cut -d":" -f2)
    outfile=${outfile:1}

    prepare_test_folder

    compile_stuff

    for name in ${FILES[@]}
    do
        if [ -f $name ]; then
            echo -n "Running $name... "

            if [ $infile = '""' ];
            then
                (./$name < input.txt > output.txt && echo -e $OK) || echo -e $NOTOK
                mv output.txt $name.out
            elif [ $infile = "input.txt" ];
            then
                (./$name && echo -e $OK) || echo -e $NOTOK
                mv output.txt $name.out
            else
                ln -s input.txt $infile
                (./$name && echo -e $OK) || echo -e $NOTOK
                mv $outfile $name.out
                rm $infile
            fi

            md5sum $name.out | awk '{print $1}' > $name.out.md5
        fi
    done

    echo

    if [ -f input.txt ]; then
        echo -n "Testing iolibgen... "
        chronic ../gradergen --io_lib 2> iolibgen.out
        (python test_iolibgen.py 2> test_iolibgen.out && echo -e $OK) || echo -e $NOTOK 
    fi

    popd > /dev/null
}


if [[ $# -eq 0 ]]
then
    # biginput is not tested by default (it is slow)
    TESTS=$(find . -name "*_test" -type d ! -name "biginput*" | sort -V | sed 's|^./||')
else
    TESTS=()
    for name in "$@"
    do
        if [ -d "$name"_test ]
        then
            TESTS+=("$name"_test)
        fi
    done
fi

for test in ${TESTS[@]}
do
    run_test $test
done

printf "${BOLDW}"
echo
echo
echo "###################################################"
echo "###################################################"
echo "#################### RESULTS ######################"
echo "###################################################"
echo "###################################################"
echo
printf "${NC}" 
for test in ${TESTS[@]}
do
    echo
    printf "${BOLDW}"
    echo $test
    printf "${NC}"
    if [ -f "$test/comments.txt" ]
    then
        cat $test/comments.txt
    fi
    
    for name in ${FILES[@]}
    do
		echo -n "$name: "
        diff -q $test/correct.md5 $test/$name.out.md5 > /dev/null
        if [ $? -ne 0 ]
        then
            printf "${RED}"
            echo -n "grader "
            printf "${NC}"
        else
            printf "${GREEN}"
            echo -n "grader "
            printf "${NC}"
        fi
        
        if [ -f "$test/template_$name.errors" ]
        then
		    printf "${RED}"
            echo -n "template "
            printf "${NC}"
        else
			printf "${GREEN}"
            echo -n "template "
            printf "${NC}"
        fi
        
        echo
    done

    # Checking iolibgen.
    if [ -f $test/input.txt ]; then
        diff -q $test/iolibgen_input.txt $test/input.txt > /dev/null
        if [ $? -ne 0 ]
        then
            printf "${RED}"
            echo -n "iolibgen_input "
            printf "${NC}"
        else
            printf "${GREEN}"
            echo -n "iolibgen_input "
            printf "${NC}"
        fi

        diff -q $test/iolibgen_output.txt $test/c.out > /dev/null
        if [ $? -ne 0 ]
        then
            printf "${RED}"
            echo -n "iolibgen_output"
            printf "${NC}"
        else
            printf "${GREEN}"
            echo -n "iolibgen_output"
            printf "${NC}"
        fi
    else
        printf "${GREEN}"
        echo -n "iolibgen "
        printf "${NC}"
    fi
    echo
done
