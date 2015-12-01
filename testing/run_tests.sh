#!/bin/sh
RED="\033[91m"
GREEN="\033[92m"
BOLDW="\e[1;37m"
NC="\033[0m" # No Color
OK="$GREEN✓\033[0m"
NOTOK="$RED✗\033[0m"

FILES='c fast_c cpp fast_cpp pascal fast_pascal'

run_test() {
    pushd $1 > /dev/null
    
    echo -e "Testing $1"
    
    taskname=$(grep "name" task.yaml | cut -d":" -f2)
	taskname=${taskname:1}
    infile=$(grep "infile" task.yaml | cut -d":" -f2)
	infile=${infile:1}
	outfile=$(grep "outfile" task.yaml | cut -d":" -f2)
	outfile=${outfile:1}
    
    gradergen --all 2> $1.errors
    
    if [ $? != "0" ]
    then
        for name in $FILES
        do
            cat $1.errors > $name.out
            md5sum $name.out | awk '{print $1}' > $name.out.md5
        done
        popd
        return
    fi
	
	echo 
	
    # If needed, create the input file
    if [ -f input.py ]; then
        python input.py > input.txt
    fi
    if [ -f input.cpp ]; then
        g++ input.cpp -O2 -o input >/dev/null 2>/dev/null && ./input > input.txt
    fi

    echo -n "Compiling stuff... "
	
	cp soluzione.pas $taskname.pas
	
    (gcc -Wall -DEVAL -O2 grader.c soluzione.c -o c >/dev/null 2>/dev/null \
      && gcc -Wall -DEVAL -O2 fast_grader.c soluzione.c -o fast_c >/dev/null 2>/dev/null \
      && g++ -Wall -DEVAL -O2 grader.cpp soluzione.cpp -o cpp >/dev/null 2>/dev/null \
      && g++ -Wall -DEVAL -O2 fast_grader.cpp soluzione.cpp -o fast_cpp >/dev/null 2>/dev/null \
      && fpc -dEVAL grader.pas -opascal >/dev/null 2>/dev/null \
      && fpc -dEVAL fast_grader.pas -ofast_pascal >/dev/null 2>/dev/null \
      && echo -e $OK) || echo -e $NOTOK
	
	rm $taskname.pas
	
    for name in $FILES
    do
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
    done

	 echo -n "Compiling templates... "
	
	
	
	cp template_pascal.pas $taskname.pas
	rm *.o *.ppu # Otherwise fpc seems to be non-deterministic...
	
    (gcc -Wall -DEVAL -O2 grader.c template_C.c -o template_C >template_C.out 2>template_CPP.out \
      && gcc -Wall -DEVAL -O2 fast_grader.c template_fast_C.c -o template_fast_C >template_fast_C.out 2>template_fast_C.out \
      && g++ -Wall -DEVAL -O2 grader.cpp template_CPP.cpp -o template_cpp >template_CPP.out 2>template_CPP.out \
      && g++ -Wall -DEVAL -O2 fast_grader.cpp template_fast_CPP.cpp -o template_fast_CPP >template_fast_CPP.out 2>template_fast_CPP.out \
      && fpc -dEVAL grader.pas -otemplate_pascal >template_pascal.out 2>template_pascal.out \
      && fpc -dEVAL fast_grader.pas -otemplate_fast_pascal >template_fast_pascal.out 2>template_fast_pascal.out \
      && echo -e $OK) || (cat template_*.out > template.errors && echo -e $NOTOK)
	
	
	rm $taskname.pas 
	
	echo
	
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

# Ensure that gradergen is installed
pushd .. > /dev/null
echo -n "Installation of gradergen... "
((python setup.py install >/dev/null 2>/dev/null || sudo python setup.py install >/dev/null 2>/dev/null) && echo -e $OK) || echo -e $NOTOK
popd > /dev/null

echo -n "Cleaning testing directories... "
(./cleanup.sh -q && echo -e $OK) || echo -e $NOTOK

for test in ${TESTS[@]}
do
    run_test $test
done

for test in ${TESTS[@]}
do
    echo
    printf "${BOLDW}"
    echo $test
    for j in $FILES
    do
        # echo -n "("$(cat $i/$j.time)"s) "
        #echo $j
        diff -q $test/correct.md5 $test/$j.out.md5 >/dev/null
        if [ $? -ne 0 ]
        then
            printf "${RED}"
            echo $j
            printf "${NC}"
            head -c2k $test/$j.out | head -c -1
            echo
        else
            printf "${GREEN}"
            echo $j
            printf "${NC}"
        fi
    done
    
    echo 
    
    if [ -f $test/template.errors ]
	then
		printf "${RED}"
		echo "template"
		printf "${NC}"
		head -c2k $test/template.errors | head -c -1
		echo
	else
		printf "${GREEN}"
		echo "template"
		printf "${NC}"
	fi
done
