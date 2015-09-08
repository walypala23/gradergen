#!/usr/bin/env python2

import sys
import re # per controllare che le variabili e i nomi delle funzioni siano in formato accettabile

types_c = {'int':'int', 'l':'long int', 'll':'long long int', 'ull':'unsigned long long int', 'char':'char', 'double':'double', 'float':'float'}
stdio_types = {'int':'d', 'l':'ld', 'll':'lld', 'ull':'llu', 'char':'c', 'double':'lf', 'float':'f'}		
grader_c = open("grader.cpp", "w")
		
variables = {}
arrays = {}


def DeclareVariable(var):
	grader_c.write("static " + var["type"] + " " + var["name"] + ";\n");
	
def DeclareArray(arr):
	grader_c.write("static " + arr["type"] + ( "*" * len(arr["dim"]) ) + " " + arr["name"] + ";\n" )


grader_c.write("#include <stdio.h>\n")
grader_c.write("#include <assert.h>\n")
grader_c.write("#include <stdlib.h>\n\n")
grader_c.write("static FILE *fr, *fw;\n\n");

var = open("variabili", "r")
lines = var.read().splitlines()
var.close()

for li in lines:
	li.strip()
	if not li.startswith("#") and len(li) != 0:
		new_var = re.split('[ \[\]]', li)
		new_var = [x for x in new_var if x]
		
		if not new_var[0] in types_c:
			sys.exit("Tipo non esistente") # Controllare se questo modo di dare gli errori è sensato
		
		if not re.match("^[a-zA-Z_$][0-9a-zA-Z_$]*$", new_var[1]):
			sys.exit("Il nome di una variabile contiene dei caratteri non ammessi")
		
		if len(new_var) == 2:
			if new_var[1] in variables:
				sys.exit("Nome della variabile già utilizzata")
			var = {"name":new_var[1], "type":new_var[0], "read":0}
			variables[new_var[1]] = var			
			DeclareVariable(var)
		else:
			dim = len(new_var)-2
			if new_var[1] in arrays:
				sys.exit("Nome dell'array già utilizzato")
			if dim == 0:
				sys.exit("Dimensioni dell'array non specificate")
			for num in new_var[2:]:
				if not num in variables:
					sys.exit("Dimensione dell'array non definita")
			arr = {"name":new_var[1], "type":new_var[0], "dim":new_var[2:]}
			arrays[new_var[1]] = arr
			DeclareArray(arr)
			
grader_c.write("\nint main() {\n")
grader_c.write("\tfr = fopen(\"input.txt\", \"r\");\n");

InputFormat = open("InputFormat.txt","r")
lines = InputFormat.read().splitlines()

for li in lines:
	li.strip()
	if not li.startswith("#") and len(li) != 0:
		if "[" in li:
			#~ print(li)
			ReadArr = re.sub("[\[\]]", "", li)
			#~ print(ReadArr)
			ReadArr = [x for x in re.split(" ", ReadArr) if x]
			
			for name in ReadArr:
				if name not in arrays:
					sys.exit("Un array da leggere non esiste")
				
				arr = arrays[name]
				if arr["dim"] != arrays[ReadArr[0]]["dim"]:
					sys.exit("Array da leggere insieme devono avere le stesse dimensioni")
				
				for var in arr["dim"]:
					if variables[var]["read"] == 0:
						sys.exit("Quando si legge un array devono essere note le dimensioni")
						
				ArrLen = len(arr["dim"])
				for i in range(0, ArrLen):
					grader_c.write("\t"*i)
					if i != 0:
						it = "i" + str(i-1)
						grader_c.write("for (int " + it + " = 0; " + it + " < " + arr['dim'][i-1] + "; " + it + "++) {\n")
					
					grader_c.write("\t"*(i+1))
					grader_c.write(name)
					for j in range(0, i):
						grader_c.write("[i" + str(j) + "]")
					grader_c.write(" = (")
					grader_c.write(arr["type"] + " " + ("*" * (ArrLen-i)));
					grader_c.write(")malloc(" + arr["dim"][i] + " * sizeof(")
					grader_c.write(arr["type"] + ("*" * (ArrLen-i-1)))
					grader_c.write("));\n");
				
				for i in range(0, ArrLen - 1):
					grader_c.write("\t" * (ArrLen - i - 1)+ "}\n");
				
				grader_c.write("\n")
					
			AllDim = arrays[ReadArr[0]]["dim"]
			for i in range(0, len(AllDim)):
				grader_c.write('\t' * (i+1))
				it = "i" + str(i)
				grader_c.write("for (int " + it + " = 0; " + it + " < " + AllDim[i] + "; " + it + "++) {\n")
			
			
			grader_c.write("\t" * (len(AllDim)+1))
			grader_c.write("fscanf(fr, \"")
						
			for name in ReadArr:
				grader_c.write("%" + stdio_types[arrays[name]["type"]] + " ")
			
			grader_c.write("\"")
			
			indexes = ""
			for i in range(0, len(AllDim)):
				indexes += "[i" + str(i) + "]"
			for name in ReadArr:
				grader_c.write(", &" + name + indexes)
			grader_c.write(");\n")
				
			for i in range(0, len(AllDim)):
				grader_c.write("\t" * (len(AllDim) - i)+ "}\n");
			
			
		else:
			ReadVar = [x for x in re.split(" ", li) if x]
			#~ print(ReadVar)
			
			grader_c.write("\tfscanf(fr, \"");
			
			for var in ReadVar:
				if var not in variables:
					sys.exit("Una variabile da leggere non esiste")
				variables[var]['read'] = 1
				grader_c.write("%" + stdio_types[variables[var]["type"]] + " ")
			
			grader_c.write("\" ")
			
			for var in ReadVar:
				grader_c.write(", &" + var)
			
			grader_c.write(");\n")
			grader_c.write("\n")
grader_c.write("}\n")
