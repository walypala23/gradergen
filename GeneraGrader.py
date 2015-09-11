#!/usr/bin/env python3

import sys
import re # regexp, used to check variables and functions names.

from structures import Variable, Array, Function
from languages import serializer, C

all_languages = serializer.Language({"C": C.Language()})
types = ['', 'int', 'l', 'll', 'ull', 'char', 'double', 'float']

variables = {}
arrays = {}
functions = []

all_languages.insert_headers()

variables_file = open("variables.txt", "r")
lines = variables_file.read().splitlines()
variables_file.close()

all_languages.wc("dec_var")
# Parsing variables.txt
for line in lines:
	line = line.strip()
	if not line.startswith("#") and len(line) != 0: # Ignore empty lines and comments
		var = re.split('[ \[\]]', line) # Split line by square brackets and space
		var = [x for x in var if x] # Remove empty chunks
		
		if not var[0] in types:
			sys.exit("Tipo non esistente")
		
		if not re.match("^[a-zA-Z_$][0-9a-zA-Z_$]*$", var[1]):
			sys.exit("Il nome di una variabile contiene dei caratteri non ammessi")
		
		if len(var) == 2:
			if var[1] in variables or var[1] in arrays:
				sys.exit("Nome della variabile già utilizzata")
			var_obj = Variable(var[1], var[0])
			variables[var[1]] = var_obj
					
			all_languages.DeclareVariable(var_obj)
			
		else:
			dim = len(var)-2
			if var[1] in variables or var[1] in arrays:
				sys.exit("Nome dell'array già utilizzato")
			if dim == 0:
				sys.exit("Dimensioni dell'array non specificate")
			for num in var[2:]:
				if num not in variables:
					sys.exit("Dimensione dell'array non definita")
			arr_obj = Array(var[1], var[0], var[2:])
			arrays[var[1]] = arr_obj
			
			all_languages.DeclareArray(arr_obj)

all_languages.wc("dec_fun")			
# Parsing functions.txt
functions_file = open("functions.txt", "r")
lines = functions_file.read().splitlines()
functions_file.close()

for line in lines:
	line = line.strip()
	if not line.startswith("#") and len(line) != 0:
		fun_obj = Function()
		
		fun = re.split("=", line)
		if len(fun) > 2:
			sys.exit("La descrizione di una funzione ha troppi caratteri '='")
		elif len(fun) == 2:
			var = fun[0].strip()
			if var not in variables:
				sys.exit("Variabile di ritorno di una funzione non definita")
			
			fun_obj.return_var = variables[var]
			fun = fun[1].strip()
		else:
			fun_obj.type = ""
			fun = fun[0]
		
		fun = re.split("[\(\)]", fun)
		if len(fun) != 3:
			sys.exit("La descrizione di una funzione ha un numero errato di parentesi")
		else:
			name = fun[0].strip()
			if name in variables or name in arrays:
				sys.exit("Il nome di una funzione è già usato")
			
			fun_obj.name = name
			
			fun_obj.parameters = []
			parameters = re.split(",", fun[1])
			for param in parameters:
				param = param.strip()
				
				if param in variables:
					fun_obj.parameters.append(variables[param])
				elif param in arrays:
					fun_obj.parameters.append(arrays[param])
				else:
					sys.exit("Parametro di funzione non definito")
					
		functions.append(fun_obj)
		all_languages.DeclareFunction(fun_obj)


all_languages.insert_main()

all_languages.wc("input", 1)
InputFormat_file = open("InputFormat.txt","r")
lines = InputFormat_file.read().splitlines()
InputFormat_file.close()

# Parsing InputFormat.txt
for line in lines:
	line = line.strip()
	if not line.startswith("#") and len(line) != 0:
		if "[" in line: # Read arrays
			all_arrs = re.sub("[\[\]]", "", line) # Remove square brackets
			all_arrs = re.split(" ", all_arrs) # Split line by spaces
			all_arrs = [x for x in all_arrs if x] # Remove empty chuncks
			
			for name in all_arrs:
				if name not in arrays:
					sys.exit("Un array da leggere non esiste")
				
				arr = arrays[name]
				if arr.sizes != arrays[all_arrs[0]].sizes:
					sys.exit("Array da leggere insieme devono avere le stesse dimensioni")
				
				for var in arr.sizes:
					if variables[var].read == False:
						sys.exit("Quando si legge un array devono essere note le dimensioni")
						
				all_languages.AllocateArray(arr)
					
			all_languages.ReadArrays([arrays[name] for name in all_arrs])
			
		else: # Read variables
			all_vars = re.split(" ", line) # Split line by spaces
			all_vars = [x for x in all_vars if x] # Remove empty chuncks
			for name in all_vars:
				if name not in variables:
					sys.exit("Una variabile da leggere non esiste")
				variables[name].read = True
			
			all_languages.ReadVariables([variables[name] for name in all_vars])

all_languages.wc("call_fun", 1)
for fun in functions:
	all_languages.CallFunction(fun)


all_languages.wc("output", 1)

OutputFormat_file = open("OutputFormat.txt","r")
lines = OutputFormat_file.read().splitlines()
OutputFormat_file.close()

# Parsing OutputFormat.txt
for line in lines:
	line = line.strip()
	if not line.startswith("#") and len(line) != 0:
		if "[" in line: # Write arrays
			all_arrs = re.sub("[\[\]]", "", line) # Remove square brackets
			all_arrs = re.split(" ", all_arrs) # Split line by spaces
			all_arrs = [x for x in all_arrs if x] # Remove empty chuncks
			
			for name in all_arrs:
				if name not in arrays:
					sys.exit("Un array da scrivere non esiste")
					
				if arrays[name].sizes != arrays[all_arrs[0]].sizes:
					sys.exit("Array da scrivere insieme devono avere le stesse dimensioni")
					
			all_languages.WriteArrays([arrays[name] for name in all_arrs])
			
		else: # Write variables
			all_vars = re.split(" ", line) # Split line by spaces
			all_vars = [x for x in all_vars if x] # Remove empty chuncks
			
			for name in all_vars:
				if name not in variables:
					sys.exit("Una variable da scrivere non esiste")
			
			all_languages.WriteVariables([variables[name] for name in all_vars])

all_languages.insert_footers()

all_languages.write_grader({"C": "grader.cpp"})

