#!/bin/sh
cd ..
python grader_generator.py grader_description.txt --all
for name in grader.c grader.cpp grader.pas fast_grader.c fast_grader.cpp fast_grader.pas
do
	mv $name testing/$name
done

cd testing

gcc -Wall -O2 grader.c nome_sorgente_contestant.c -o c
gcc -Wall -O2 fast_grader.c nome_sorgente_contestant.c -o fast_c
g++ -Wall -O2 grader.cpp nome_sorgente_contestant.cpp -o cpp
g++ -Wall -O2 fast_grader.cpp nome_sorgente_contestant.cpp -o fast_cpp
fpc grader.pas 
mv grader pascal
fpc fast_grader.pas
mv fast_grader fast_pascal

# ./c
# ./fast_c
# ./cpp
# ./fast_cpp
# ./pascal
# ./fast_pascal
