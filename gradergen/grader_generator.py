#!/usr/bin/env python3

import sys
import os
import re # regexp, used to check variables and functions names
import argparse # to parse command line arguments

from gradergen.structures import Variable, Array, Function, IOline, Expression
from gradergen.languages import serializer, C, CPP, pascal

LANGUAGES_LIST = ["C", "fast_C", "CPP", "fast_CPP", "pascal", "fast_pascal"]
TYPES = ["", "int", "longint", "char", "real"]
DESCRIPTION_FILE = "grader_description.txt"

standard_grader_names = {
	"C": "grader.c",
	"fast_C": "fast_grader.c",
	"CPP": "grader.cpp",
	"fast_CPP": "fast_grader.cpp",
	"pascal": "grader.pas",
	"fast_pascal": "fast_grader.pas"
}

# Global variables used in parsing functions
variables = {}
arrays = {}
functions = {}

def util_is_integer(s):
	try:	
		n = int(s)
	except:	
		return False
	
	return True

def parse_expression(s):
	splitted = re.split('[\*\+]', s)
	splitted = [x.strip() for x in splitted if x.strip()]
	if not 1 <= len(splitted) <= 3:
		sys.exit("Un'espressione è malformata (si supportano solo quelle delle forma a*var+b)")
	
	a = 1
	var = None
	b = 0
	
	for i in range(len(splitted)):
		if util_is_integer(splitted[i]):
			splitted[i] = int(splitted[i])
		elif splitted[i] not in variables:
			sys.exit("Le variabili nelle espressioni devono essere dichiarate")
		else:
			splitted[i] = variables[splitted[i]]
	
	
	if len(splitted) == 1:
		if type(splitted[0]) == int:
			return Expression(None, 1, splitted[0])
		else:
			return Expression(splitted[0], 1, 0)
	
	if len(splitted) == 2:
		if type(splitted[0]) == int:
			return Expression(splitted[1], splitted[0], 0)
		else:
			return Expression(splitted[0], 1, splitted[1])
	
	if len(splitted) == 3:
		return Expression(splitted[1], splitted[0], splitted[2])
		
def parse_variable(line):
	global variables, arrays, functions
	
	var = re.split('[ \[\]]', line) # Split line by square brackets and space
	var = [x for x in var if x] # Remove empty chunks
	
	if not var[0] in TYPES:
		sys.exit("Tipo non esistente")
	
	if not re.match("^[a-zA-Z_$][0-9a-zA-Z_$]*$", var[1]):
		sys.exit("Il nome di una variabile contiene dei caratteri non ammessi")
	
	if len(var) == 2:
		if var[1] in variables or var[1] in arrays:
			sys.exit("Nome della variabile già utilizzata")
		var_obj = Variable(var[1], var[0])
		return var_obj;
		
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
		return arr_obj
	
def parse_function(line):
	global variables, arrays, functions
	
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
				
	return fun_obj
	
def parse_input(line):
	global variables, arrays, functions
	
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
				
		input_line = IOline("Array", [arrays[name] for name in all_arrs], arrays[all_arrs[0]].sizes)
		return input_line
		
	else: # Read variables
		all_vars = re.split(" ", line) # Split line by spaces
		all_vars = [x for x in all_vars if x] # Remove empty chuncks
		for name in all_vars:
			if name not in variables:
				sys.exit("Una variabile da leggere non esiste")
			variables[name].read = True
		
		input_line = IOline("Variable", [variables[name] for name in all_vars])
		return input_line
		
def parse_output(line):
	global variables, arrays, functions
	
	if "[" in line: # Write arrays
		all_arrs = re.sub("[\[\]]", "", line) # Remove square brackets
		all_arrs = re.split(" ", all_arrs) # Split line by spaces
		all_arrs = [x for x in all_arrs if x] # Remove empty chuncks
		
		for name in all_arrs:
			if name not in arrays:
				sys.exit("Un array da scrivere non esiste")
				
			if arrays[name].sizes != arrays[all_arrs[0]].sizes:
				sys.exit("Array da scrivere insieme devono avere le stesse dimensioni")
				
		output_line = IOline("Array", [arrays[name] for name in all_arrs], arrays[all_arrs[0]].sizes)
		return output_line
		
	else: # Write variables
		all_vars = re.split(" ", line) # Split line by spaces
		all_vars = [x for x in all_vars if x] # Remove empty chuncks
		
		for name in all_vars:
			if name not in variables:
				sys.exit("Una variable da scrivere non esiste")
		
		output_line = IOline("Variable", [variables[name] for name in all_vars])
		return output_line


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
	global DESCRIPTION_FILE
	global variables, arrays, functions
	
	declarations_order = []
	input_order = []
	output_order = []
	functions_order = []
	
	parser = argparse.ArgumentParser(description = "Automatically generate grader files in various languages")
	parser.add_argument(\
		"grader_description", 
		metavar="grader_description", 
		action="store", nargs="?",
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
	if args.grader_description is None:
		# Search for a DESCRIPTION_FILE
		directory = os.getcwd()
		while True:
			description = os.path.join(directory, DESCRIPTION_FILE)

			if os.path.isfile(description):
				args.grader_description = description
				break

			if os.path.dirname(directory) == directory:
				break
			else:
				directory = os.path.dirname(directory)

	if args.grader_description is None:
		sys.exit("The " + DESCRIPTION_FILE + " file cannot be found.")

	with open(args.grader_description, "r") as grader_description:
		lines = grader_description.read().splitlines()
		section_lines = parse_description(lines)

	grader_files = args.languages
	if args.all:
		grader_files = [[lang] for lang in LANGUAGES_LIST]
		
	# Parsing variables
	for line in section_lines["variables"]:
		parsed = parse_variable(line)
		if type(parsed) == Variable:
			variables[parsed.name] = parsed
			declarations_order.append(parsed)
		elif type(parsed) == Array:
			arrays[parsed.name] = parsed
			declarations_order.append(parsed)
			
	# Parsing functions
	for line in section_lines["functions"]:
		parsed = parse_function(line)
		functions[parsed.name] = parsed
		functions_order.append(parsed)

	# Parsing input
	for line in section_lines["input"]:
		parsed = parse_input(line)
		input_order.append(parsed)

	# Parsing output
	for line in section_lines["output"]:
		parsed = parse_output(line)
		output_order.append(parsed)
	
	# End of parsing
	
	data = {
		"task_name": args.task_name,
		"variables": variables,
		"arrays": arrays,
		"functions": functions,
		"helpers": [parse_function(x) for x in section_lines["helpers"]] if "helpers" in section_lines else None
	}
	
	# All languages are initializated (not all are written to file)
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
		if el[0] not in LANGUAGES_LIST:
			sys.exit("Uno dei linguaggi non è supportato")
		if len(el) == 1:
			el.append(standard_grader_names[el[0]])
		elif len(el) > 2:
			sys.exit("Per ogni linguaggio si può indicare soltanto il nome del grader")
		
		chosed_languages[el[0]] = language_classes[el[0]]
	
	languages_serializer = serializer.Language(chosed_languages)
	
	languages_serializer.insert_headers()

	languages_serializer.wc("dec_var")
	for decl in declarations_order:
		if type(decl) == Variable:
			languages_serializer.declare_variable(decl)
		else:
			languages_serializer.declare_array(decl)

	languages_serializer.wc("dec_fun")
	for fun in functions_order:
		languages_serializer.declare_function(fun)
		
	languages_serializer.insert_main()
	languages_serializer.wc("input", 1)
	for input_line in input_order:
		if input_line.type == "Array":
			for arr in input_line.list:
				languages_serializer.allocate_array(arr)
				arrays[arr.name].allocated = True
			languages_serializer.read_arrays(input_line.list)
			
		elif input_line.type == "Variable":
			languages_serializer.read_variables(input_line.list)

	languages_serializer.wc("call_fun", 1)
	for fun in functions_order:
		for i in range(len(fun.parameters)):
			param = fun.parameters[i]
			if type(param) == Array and param.allocated == False:
				if not all(variables[name].read for name in param.sizes):
					sys.exit("Devono essere note le dimensioni degli array passati alle funzioni dell'utente")
				languages_serializer.allocate_array(param)
				param.allocated = True
			if type(param) == Variable and not param.read and not fun.by_ref[i]:
				sys.exit("I parametri non passati per reference alle funzioni dell'utente devono essere noti")
				
		languages_serializer.call_function(fun)
		if fun.return_var:
			fun.return_var.read = True
			
		# Variables passed by reference are "read"
		for i in range(len(fun.parameters)):
			param = fun.parameters[i]
			if type(param) == Variable and fun.by_ref[i]:
				param.read = True
	
	languages_serializer.wc("output", 1)
	for output_line in output_order:
		if output_line.type == "Array":
			languages_serializer.write_arrays(output_line.list)
		elif output_line.type == "Variable":
			languages_serializer.write_variables(output_line.list)
	
	languages_serializer.insert_footers()
	languages_serializer.write_grader(grader_files)
