#!/usr/bin/env python3

import sys
import re # regexp, used to check variables and functions names.

class CLanguage:
	def __init__(self):
		self.out = ""
	
	types = {'': 'void', 'int':'int', 'l':'long int', 'll':'long long int', 'ull':'unsigned long long int', 'char':'char', 'double':'double', 'float':'float'}
	
	stdio_types = {'int':'d', 'l':'ld', 'll':'lld', 'ull':'llu', 'char':'c', 'double':'lf', 'float':'f'}
	
	headers = """\
#include <stdio.h>
#include <assert.h>
#include <stdlib.h>

static FILE *fr, *fw;
"""
	
	main_function = """\

int main() {
	#ifdef EVAL
		fr = fopen("input.txt", "r");
		fw = fopen("output.txt", "w");
	#else
		fr = stdin;
		fw = stdout;
	#endif
"""
	
	footers = """\
	
	fclose(fr);
	fclose(fw);
	return 0;
}
"""
	
	comments = {
		"dec_var": "Declaring variables", 
		"dec_fun": "Declaring functions", 
		"input": "Reading input", 
		"call_fun": "Calling functions", 
		"output": "Writing output", 
	}
	
	# array type
	def at(self, _type, dim):
		return self.types[_type] + "*"*dim
	
	# write line
	def wl(self, line, tabulation = 0):
		self.out += "\t"*tabulation + line + "\n"
	
	# write comment
	def wc(self, short_description, tabulation = 0):
		self.out += "\n" + ("\t"*tabulation) + "// " + self.comments[short_description] +"\n"
	
	def DeclareVariable(self, var):
		self.wl("static {0} {1};".format(self.types[var.type], var.name))
		
	def DeclareArray(self, arr):
		self.wl("static {0} {1};".format(self.at(arr.type, arr.dim), arr.name) )
	
	def DeclareFunction(self, fun):
		typed_parameters = []
		for param in fun.parameters:
			if type(param) == Variable:
				typed_parameters.append(self.types[param.type] + " " + param.name)
			elif type(param) == Array:
				typed_parameters.append(self.at(param.type, param.dim) + " " + param.name)
		self.wl("{0} {1}({2});".format(self.types[fun.type], fun.name, ", ".join(typed_parameters)))
	
	def AllocateArray(self, arr):
		for i in range(0, arr.dim):
			if i != 0:
				self.wl("for (int {0} = 0; {0} < {1}; {0}++) {{".format("i" + str(i-1), arr.sizes[i-1]), i)
				
			indexes = "".join("[i" + str(x) + "]" for x in range(0,i))
			self.wl("{0}{1} = ({2}*)malloc({3} * sizeof({2}));".format(arr.name, indexes, self.at(arr.type, arr.dim-i-1), arr.sizes[i]), i+1)
			
		for i in range(0, arr.dim - 1):
			self.wl("}", arr.dim - i - 1)
	
	def ReadArrays(self, ReadArr):
		all_dim = ReadArr[0].dim
		all_sizes = ReadArr[0].sizes
		for i in range(0, all_dim):
			self.wl("for (int {0} = 0; {0} < {1}; {0}++) {{".format("i" + str(i), all_sizes[i]), i+1)
			
		format_string = " ".join("%" + self.stdio_types[arr.type] for arr in ReadArr)
		indexes = "".join("[i" + str(x) + "]" for x in range(0, all_dim))
		pointers = ", ".join("&" + arr.name + indexes for arr in ReadArr)
		self.wl("fscanf(fr, \"{0}\", {1});".format(format_string, pointers), all_dim+1)
			
		for i in range(0, all_dim):
			self.wl("}", all_dim - i)
	
	def ReadVariables(self, ReadVar):
		format_string = " ".join("%" + self.stdio_types[var.type] for var in ReadVar)
		pointers = ", ".join("&" + var.name for var in ReadVar)
		self.wl("fscanf(fr, \"{0}\", {1});".format(format_string, pointers), 1)
	
	def CallFunction(self, fun):
		parameters = ', '.join([param.name for param in fun.parameters])
		if fun.type == "":
			self.wl("{0}({1});".format(fun.name, parameters), 1)
		else:
			self.wl("{2} = {0}({1});".format(fun.name, parameters, fun.return_var.name), 1)
	
	def WriteArrays(self, WriteArr):
		all_dim = WriteArr[0].dim
		all_sizes = WriteArr[0].sizes
		
		for i in range(0, all_dim):
			self.wl("for (int {0} = 0; {0} < {1}; {0}++) {{".format("i" + str(i), all_sizes[i]), i+1)
		
		format_string = " ".join("%" + self.stdio_types[arr.type] for arr in WriteArr)
		indexes = "".join("[i" + str(x) + "]" for x in range(0, all_dim))
		antipointers = ", ".join(arr.name + indexes for arr in WriteArr)
		if len(WriteArr) > 1:
			self.wl("fprintf(fw, \"{0}\\n\", {1});".format(format_string, antipointers), all_dim+1)
		else:
			self.wl("fprintf(fw, \"{0}\", {1});".format(format_string, antipointers), all_dim+1)
		
		for i in range(0, all_dim):
			self.wl("}", all_dim - i)
			if i == all_dim-1 and len(WriteArr) > 1:
				self.wl("fprintf(fw, \"\\n\");", all_dim - i)

	def WriteVariables(self, WriteVar):
		format_string = " ".join("%" + self.stdio_types[var.type] for var in WriteVar)
		antipointers = ", ".join(var.name for var in WriteVar)
		self.wl("fprintf(fw, \"{0}\\n\", {1});".format(format_string, antipointers), 1)
	
	def insert_headers(self):
		self.out += self.headers
		
	def insert_main(self):
		self.out += self.main_function
	
	def insert_footers(self):
		self.out += self.footers
	
	def GraderFile(self):
		grader = open("grader.cpp", "w")
		grader.write(self.out)
		grader.close()


languages = {"C": CLanguage()}
types = ['', 'int', 'l', 'll', 'ull', 'char', 'double', 'float']

class Variable:
	def __init__(self, n, t):
		self.name = n
		self.type = t
		self.read = False
		

class Array:
	def __init__(self, n, t, s):
		self.name = n
		self.type = t
		self.dim = len(s)
		self.sizes = s

class Function:
	def __init__(self, n = None, p = None, r = None):
		self.name = n
		self.parameters = p
		if r != None:
			self.type = r.type
			self.return_var = r
		else:
			self.type = ""
			self.return_var = None

variables = {}
arrays = {}
functions = []

for lang in languages:
	languages[lang].insert_headers()

variables_file = open("variables.txt", "r")
lines = variables_file.read().splitlines()
variables_file.close()

for lang in languages:
	languages[lang].wc("dec_var")
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
					
			for lang in languages:
				languages[lang].DeclareVariable(var_obj)
			
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
			
			for lang in languages:
				languages[lang].DeclareArray(arr_obj)

for lang in languages:
	languages[lang].wc("dec_fun")			
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
		for lang in languages:
			languages[lang].DeclareFunction(fun_obj)


for lang in languages:
	languages[lang].insert_main()

for lang in languages:
	languages[lang].wc("input", 1)
InputFormat_file = open("InputFormat.txt","r")
lines = InputFormat_file.read().splitlines()
InputFormat_file.close()

# Parsing InputFormat.txt
for line in lines:
	line = line.strip()
	if not line.startswith("#") and len(line) != 0:
		if "[" in line: # Read arrays
			ReadArr = re.sub("[\[\]]", "", line) # Remove square brackets
			ReadArr = re.split(" ", ReadArr) # Split line by spaces
			ReadArr = [x for x in ReadArr if x] # Remove empty chuncks
			
			for name in ReadArr:
				if name not in arrays:
					sys.exit("Un array da leggere non esiste")
				
				arr = arrays[name]
				if arr.sizes != arrays[ReadArr[0]].sizes:
					sys.exit("Array da leggere insieme devono avere le stesse dimensioni")
				
				for var in arr.sizes:
					if variables[var].read == False:
						sys.exit("Quando si legge un array devono essere note le dimensioni")
						
				for lang in languages:
					languages[lang].AllocateArray(arr)
					
			for lang in languages:
				languages[lang].ReadArrays([arrays[name] for name in ReadArr])
			
		else: # Read variables
			ReadVar = re.split(" ", line) # Split line by spaces
			ReadVar = [x for x in ReadVar if x] # Remove empty chuncks
			for name in ReadVar:
				if name not in variables:
					sys.exit("Una variabile da leggere non esiste")
				variables[name].read = True
			
			for lang in languages:
				languages[lang].ReadVariables([variables[name] for name in ReadVar])

for lang in languages:
	languages[lang].wc("call_fun", 1)
for fun in functions:
	for lang in languages:
		languages[lang].CallFunction(fun)


for lang in languages:
	languages[lang].wc("output", 1)

OutputFormat_file = open("OutputFormat.txt","r")
lines = OutputFormat_file.read().splitlines()
OutputFormat_file.close()

# Parsing OutputFormat.txt
for line in lines:
	line = line.strip()
	if not line.startswith("#") and len(line) != 0:
		if "[" in line: # Write arrays
			WriteArr = re.sub("[\[\]]", "", line) # Remove square brackets
			WriteArr = re.split(" ", WriteArr) # Split line by spaces
			WriteArr = [x for x in WriteArr if x] # Remove empty chuncks
			
			for name in WriteArr:
				if name not in arrays:
					sys.exit("Un array da scrivere non esiste")
					
				if arrays[name].sizes != arrays[WriteArr[0]].sizes:
					sys.exit("Array da scrivere insieme devono avere le stesse dimensioni")
					
			for lang in languages:
				languages[lang].WriteArrays([arrays[name] for name in WriteArr])
			
		else: # Write variables
			WriteVar = re.split(" ", line) # Split line by spaces
			WriteVar = [x for x in WriteVar if x] # Remove empty chuncks
			
			for name in WriteVar:
				if name not in variables:
					sys.exit("Una variable da scrivere non esiste")
			
			for lang in languages:
				languages[lang].WriteVariables([variables[name] for name in WriteVar])

for lang in languages:
	languages[lang].insert_footers()

for lang in languages:
	languages[lang].GraderFile()
