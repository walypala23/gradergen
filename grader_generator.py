#!/usr/bin/env python3

import sys
import re # regexp, used to check variables and functions names
import argparse # to parse command line arguments

from structures import Variable, Array, Function
from languages import serializer, C

languages_list = ['C']

# All languages are generated (not all are written to file)
all_languages = serializer.Language({
	"C": C.Language()
})
standard_grader_names = {
	"C": "grader.c"
}

types = ['', 'int', 'l', 'll', 'ull', 'char', 'double', 'float']

variables = {}
arrays = {}
functions = []

def parse_variable(line):
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
	
def parse_function(line):
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
	
def parse_input(line):
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
		
def parse_output(line):
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


# Parsing grader description file
def parse_description(lines):
	sections = {"variables": False, "functions": False, "input": False, "output": False}
	section_lines = {}
	act_section = None
	for line in lines:
		line = line.strip()
	
		if line.startswith("#") or len(line) == 0:
			continue
			
		is_section_title = False
		for section in sections:
			if line == "***" + section + "***":
				if sections[section]:
					sys.exit("Il file di descrizione contiene due volte la stessa sezione")
				is_section_title = True
				sections[section] = True
				act_section = section
				section_lines[section] = []
				break
		
		if not is_section_title:
			if not act_section:
				sys.exit("Il file di descrizione deve specificare la sezione")
			section_lines[act_section].append(line)
	return section_lines


if __name__=='__main__':
	parser = argparse.ArgumentParser(description = "Automatically generate grader files in various languages")
	parser.add_argument(\
		"grader_description", 
		metavar="grader_description", 
		action="store", nargs=1, 
		help="the file describing the grader"
	)
	group = parser.add_mutually_exclusive_group(required=True)
	
	group.add_argument(\
		"-l","--lang",
		nargs = "+", 
		metavar = ("lang", "grader_filename"), 
		dest = "languages", 
		action = "append", 
		help="programming language and grader filename"
	)
	
	group.add_argument(\
		"-a", "--all", 
		action="store_true", 
		default=False,
		help="create grader (with filename 'grader.lang') in all supported languages"
	)
		
	args = parser.parse_args()
	
	grader_description = open(args.grader_description[0], "r")
	lines = grader_description.read().splitlines()
	grader_description.close()
	
	section_lines = parse_description(lines)
	
	all_languages.insert_headers()

	all_languages.wc("dec_var")
	# Parsing variables.txt
	for line in section_lines["variables"]:
		parse_variable(line)

	all_languages.wc("dec_fun")			
	# Parsing functions.txt
	for line in section_lines["functions"]:
		parse_function(line)

	all_languages.insert_main()

	all_languages.wc("input", 1)

	# Parsing InputFormat.txt
	for line in section_lines["input"]:
		parse_input(line)

	all_languages.wc("call_fun", 1)
	for fun in functions:
		all_languages.CallFunction(fun)

	all_languages.wc("output", 1)

	# Parsing OutputFormat.txt
	for line in section_lines["output"]:
		parse_output(line)

	all_languages.insert_footers()
	
	grader_files = args.languages
	if args.all:
		grader_files = [[lang] for lang in languages_list]
	
	for el in grader_files:
		if len(el) == 1:
			el.append(standard_grader_names[el[0]])
	
	all_languages.write_grader(grader_files)
	
	
