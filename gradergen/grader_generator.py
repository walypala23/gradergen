#!/usr/bin/env python3

import sys
import re # regexp, used to check variables and functions names
import argparse # to parse command line arguments

from gradergen.structures import Variable, Array, Function, variables, arrays, functions
from gradergen.languages import serializer, C, CPP, pascal

languages_list = ["C", "fast_C", "CPP", "fast_CPP", "pascal", "fast_pascal"]

standard_grader_names = {
	"C": "grader.c",
	"fast_C": "fast_grader.c",
	"CPP": "grader.cpp",
	"fast_CPP": "fast_grader.cpp",
	"pascal": "grader.pas",
	"fast_pascal": "fast_grader.pas"
}

languages_serializer = {}
types = ["", "int", "longint", "char", "real"]

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
				
		languages_serializer.declare_variable(var_obj)
		
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
		
		languages_serializer.declare_array(arr_obj)
	
def parse_function(line):
	fun_obj = Function()
	
	fun = re.split("=", line)
	if len(fun) > 2:
		sys.exit("La descrizione di una funzione ha troppi caratteri '='")
	elif len(fun) == 2:
		var = fun[0].strip()
		if var not in variables:
			sys.exit("Variabile di ritorno di una funzione non definita")
		
		fun_obj.type = variables[var].type
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
		fun_obj.by_ref = []
		parameters = re.split(",", fun[1])
		for param in parameters:
			param = param.strip()
			
			if param.startswith("&"):
				param = param[1:]
				fun_obj.by_ref.append(True)
			else:
				fun_obj.by_ref.append(False)
			
			if param in variables:
				fun_obj.parameters.append(variables[param])
			elif param in arrays:
				fun_obj.parameters.append(arrays[param])
				if fun_obj.by_ref[-1]:
					sys.exit("Gli array non possono essere passati per reference")
			else:
				sys.exit("Parametro di funzione non definito")
				
	functions.append(fun_obj)
	languages_serializer.declare_function(fun_obj)
	
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
					
			languages_serializer.allocate_array(arr)
			arrays[name].allocated = True
				
		languages_serializer.read_arrays([arrays[name] for name in all_arrs])
		
	else: # Read variables
		all_vars = re.split(" ", line) # Split line by spaces
		all_vars = [x for x in all_vars if x] # Remove empty chuncks
		for name in all_vars:
			if name not in variables:
				sys.exit("Una variabile da leggere non esiste")
			variables[name].read = True
		
		languages_serializer.read_variables([variables[name] for name in all_vars])
		
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
				
		languages_serializer.write_arrays([arrays[name] for name in all_arrs])
		
	else: # Write variables
		all_vars = re.split(" ", line) # Split line by spaces
		all_vars = [x for x in all_vars if x] # Remove empty chuncks
		
		for name in all_vars:
			if name not in variables:
				sys.exit("Una variable da scrivere non esiste")
		
		languages_serializer.write_variables([variables[name] for name in all_vars])


# Parsing grader description file
def parse_description(lines):
	sections = {"variables": False, "functions": False, "input": False, "output": False, "helpers": False}
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
				sys.exit("Il file di descrizione deve specificare una sezione")
			section_lines[act_section].append(line)
	return section_lines


def main():
	global languages_serializer

	parser = argparse.ArgumentParser(description = "Automatically generate grader files in various languages")
	parser.add_argument(\
		"grader_description", 
		metavar="grader_description", 
		action="store", nargs=1, 
		help="the file describing the grader"
	)
	parser.add_argument(\
		"--task-name",
		metavar="task_name",
		action="store", nargs="?",
		default="the_name_of_the_task",
		help="the name of the task"
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

	with open(args.grader_description[0], "r") as grader_description:
		lines = grader_description.read().splitlines()
		section_lines = parse_description(lines)

	grader_files = args.languages
	if args.all:
		grader_files = [[lang] for lang in languages_list]

	data = {
		"task_name": args.task_name,
		"helpers": [parse_function(x) for x in section_lines["helpers"]] if "helpers" in section_lines else None
	}

	# All languages are generated (not all are written to file)
	language_classes = {
		"C": C.Language(0, data),
		"fast_C": C.Language(1, data),
		"CPP": CPP.Language(0, data),
		"fast_CPP": CPP.Language(1, data),
		"pascal": pascal.Language(0, data),
		"fast_pascal": pascal.Language(1, data)
	}
	
	chosed_languages = {}
	for el in grader_files:
		if el[0] not in languages_list:
			sys.exit("Uno dei linguaggi non è supportato")
		if len(el) == 1:
			el.append(standard_grader_names[el[0]])
		elif len(el) > 2:
			sys.exit("Per ogni linguaggio si può indicare soltanto il nome del grader")
		
		chosed_languages[el[0]] = language_classes[el[0]]

	languages_serializer = serializer.Language(chosed_languages)
	
	languages_serializer.insert_headers()

	languages_serializer.wc("dec_var")
	# Parsing variables.txt
	for line in section_lines["variables"]:
		parse_variable(line)

	languages_serializer.wc("dec_fun")			
	# Parsing functions.txt
	for line in section_lines["functions"]:
		parse_function(line)

	languages_serializer.insert_main()

	languages_serializer.wc("input", 1)

	# Parsing InputFormat.txt
	for line in section_lines["input"]:
		parse_input(line)

	languages_serializer.wc("call_fun", 1)
	for fun in functions:
		for param in fun.parameters:
			if type(param) == Array and param.allocated == False:
				if not all(variables[name].read for name in param.sizes):
					sys.exit("Devono essere note le dimensioni degli array passati alle funzioni dell'utente")
				languages_serializer.allocate_array(param)
				arrays[param.name].allocated = True
		languages_serializer.call_function(fun)
		if fun.return_var:
			fun.return_var.read = True
			
		# Variables passed by reference are "read"
		for i in range(0, len(fun.parameters)):
			param = fun.parameters[i]
			if type(param) == Variable and fun.by_ref[i]:
				param.read = True

	if not "helpers" in section_lines:
		languages_serializer.wc("output", 1)

		# Parsing OutputFormat.txt
		for line in section_lines["output"]:
			parse_output(line)

	languages_serializer.insert_footers()			
	
	languages_serializer.write_grader(grader_files)
	
	
