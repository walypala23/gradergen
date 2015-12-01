#!/bin/sh

taskname='nome_sorgente_contestant'

FILES='c fast_c cpp fast_cpp pascal fast_pascal'

run_test() {
    pushd $1 > /dev/null
    
    mkdir ../TempDir
    cp task.spec task.yaml soluzione.* helper_data.* correct.md5 ../TempDir/ > /dev/null 2> /dev/null
    
    # Save input or input generator
    if [ -f input.py ]
    then
        cp input.py ../TempDir/input.py
    elif [ -f input.cpp ]
    then
        cp input.cpp ../TempDir/input.cpp
    elif [ -f input.txt ]
    then
		cp input.txt ../TempDir/input.txt
    fi
    
    rm *
	
	cp ../TempDir/* .
	rm -r ../TempDir
	
    popd > /dev/null
}


TESTS=$(find . -name "*_test" -type d | sort -V)

for i in $TESTS
do
    run_test $i
done

# If quiet flag is passed, tree is not showed
if [[ "$#" -eq 0 ]] || [ "$1" != "-q" ]
then
	tree -C
fi

