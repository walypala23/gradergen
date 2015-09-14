#!/bin/sh

taskname='nome_sorgente_contestant'

cd ..
python grader_generator.py grader_description.txt --all --task-name $taskname
for name in grader.c grader.cpp grader.pas fast_grader.c fast_grader.cpp fast_grader.pas
do
	mv $name testing/$name
done

cd testing

gcc -Wall -DEVAL -O2 grader.c $taskname.c -o c
gcc -Wall -DEVAL -O2 fast_grader.c $taskname.c -o fast_c
g++ -Wall -DEVAL -O2 grader.cpp $taskname.cpp -o cpp
g++ -Wall -DEVAL -O2 fast_grader.cpp $taskname.cpp -o fast_cpp
fpc -dEVAL grader.pas -opascal
fpc -dEVAL fast_grader.pas -ofast_pascal

for name in c fast_c cpp fast_cpp pascal fast_pascal
do
	echo $name
	./$name
	mv output.txt $name.out
done
