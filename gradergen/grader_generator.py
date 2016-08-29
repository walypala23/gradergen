#!/usr/bin/env python3

import sys
import os
import re # regexp, used to check variables and functions names
import argparse # to parse command line arguments
import copy # to avoid making too many / too few "array allocations" in the grader
import yaml # parse task.yaml

from gradergen.structures import Variable, Array, Parameter, Prototype, Call, IOline, Expression
from gradergen.languages.C import LanguageC
from gradergen.languages.CPP import LanguageCPP
from gradergen.languages.pascal import LanguagePascal

LANGUAGES_LIST = ["C", "fast_C", "CPP", "fast_CPP", "pascal", "fast_pascal"]
CLASSES_LIST = \
{
	"C": (LanguageC, 0),
	"fast_C": (LanguageC, 1),
	"CPP": (LanguageCPP, 0),
	"fast_CPP": (LanguageCPP, 1),
	"pascal": (LanguagePascal, 0),
	"fast_pascal": (LanguagePascal, 1),
}
EXTENSIONS_LIST = \
{
	"C": "c",
	"fast_C": "c",
	"CPP": "cpp",
	"fast_CPP": "cpp",
	"pascal": "pas",
	"fast_pascal": "pas",
}
TYPES = ["", "int", "longint", "char", "real"]
DESCRIPTION_FILE = "task.spec"
TASK_YAML = "task.yaml"

# variables is used in parsing functions and must be global (only get_variable refers to it)
variables = []

def get_variable(name):
	global variables
	for var in variables:
		if var.name == name:
			return var

	sys.exit("Una delle variabili a cui ci si riferisce non è stata dichiarata.")

def get_primitive_variable(name):
	var = get_variable(name)
	if type(var) == Array:
		sys.exit("Una variabile che deve essere primitiva è un array.")

	return var

def get_array_variable(name):
	var = get_variable(name)
	if type(var) == Variable:
		sys.exit("Una variabile che deve essere array è un tipo primitivo.")

	return var

# FIXME: Pascal is case-insensitive, so this function should be too.
def add_used_name(s):
	if s in add_used_name.names:
		sys.exit("I nomi delle variabili, degli array e delle funzioni non devono coincidere.")
	add_used_name.names.add(s)
add_used_name.names = set()

def util_is_integer(s):
	try:
		n = int(s)
	except:
		return False

	return True

# Parsing expressions like a*var+-b
def parse_expression(s):
	# FIXME: Dovrei usare global variables... ?
	a = 1
	var = None
	b = 0

	# Parsing a
	if "*" in s:
		splitted = re.split("\*", s)
		splitted = [x.strip() for x in splitted if x.strip()]
		if len(splitted) != 2:
			sys.exit("Un'espressione è malformata (si supportano solo quelle delle forma a*var+b)")
		if util_is_integer(splitted[0]):
			a = int(splitted[0])
		else:
			sys.exit("Le costanti nelle espressioni devono essere interi")

		s = splitted[1]

	# Parsing var
	temp_var = re.match("[a-zA-Z_][0-9a-zA-Z_]*", s)
	if temp_var:
		name = temp_var.group(0)
		var = get_primitive_variable(name)
		if var.type not in ["int", "longint"]:
			sys.exit("Le variabili nelle espressioni devono essere di tipo intero")

		s = s[len(name):]

	# Parsing b
	if len(s) > 0:
		if util_is_integer(s):
			b = int(s)
		else:
			sys.exit("Le costanti nelle espressioni devono essere interi")

	return Expression(var, a, b)

def parse_variable(line):
	var = re.split('[ \[\]]', line) # Split line by square brackets and space
	var = [x for x in var if x] # Remove empty chunks

	if not var[0] in TYPES:
		sys.exit("Tipo non esistente")

	if not re.match("^[a-zA-Z_$][0-9a-zA-Z_$]*$", var[1]):
		sys.exit("Il nome di una variabile contiene dei caratteri non ammessi")

	add_used_name(var[1])

	if len(var) == 2:
		var_obj = Variable(var[1], var[0])
		return var_obj;
	else:
		dim = len(var)-2
		if dim == 0:
			sys.exit("Dimensioni dell'array non specificate")
		sizes = [parse_expression(expr) for expr in var[2:]]

		arr_obj = Array(var[1], var[0], sizes)
		return arr_obj

def parse_prototype(line):
	proto_obj = Prototype()

	first_split = re.split("[\(\)]", line)
	if len(first_split) != 3:
		sys.exit("La descrizione di un prototipo ha un numero errato di parentesi tonde")

	type_name = re.split(" ", first_split[0].strip()) #type name or only name
	parameters = re.split(",", first_split[1]) # with reference

	if len(type_name) == 1:
		proto_obj.name = type_name[0]
	elif len(type_name) == 2:
		proto_obj.type = type_name[0]
		proto_obj.name = type_name[1]
	else:
		sys.exit("Uno dei prototipi è malformato.")

	if proto_obj.type not in TYPES:
		sys.exit("Il tipo di ritorno di un prototipo non esiste.")

	add_used_name(proto_obj.name)

	for param in parameters:
		param = param.strip()
		if len(param) == 0:
			continue

		by_ref = "&" in param
		dim = param.count("[]")

		param = re.sub("[&\[\]]", "", param)
		param = re.sub(" +", " ", param).strip()

		type_name = re.split(" ", param)

		if len(type_name) != 2:
			sys.exit("Uno dei prototipi è malformato")

		proto_obj.parameters.append(Parameter(type_name[1], type_name[0], dim, by_ref))

	return proto_obj

def parse_call(line):
	fun_obj = Call()

	line = re.split("=", line)
	if len(line) > 2:
		sys.exit("La descrizione di una funzione ha troppi caratteri '='")
	elif len(line) == 2:
		var = line[0].strip()
		fun_obj.return_var = get_primitive_variable(var)

		line = line[1].strip()
	else:
		line = line[0].strip()

	line = re.split("[\(\)]", line)
	if len(line) != 3:
		sys.exit("La descrizione di una funzione ha un numero errato di parentesi")
	else:
		name = line[0].strip()

		fun_obj.name = name # It is not added to used names, as it might already be declared or it might be in include_grader

		fun_obj.parameters = []

		if len(line[1].strip()) > 0:
			parameters = re.split(",", line[1])
			for param in parameters:
				param = param.strip()
				by_ref = False

				if param.startswith("&"):
					param = param[1:]
					by_ref = True

				fun_obj.parameters.append((get_variable(param), by_ref))

	return fun_obj

def parse_input(line):
	if "[" in line: # Read arrays
		all_arrs = re.sub("[\[\]]", "", line) # Remove square brackets
		all_arrs = re.split(" ", all_arrs) # Split line by spaces
		all_arrs = [get_array_variable(name) for name in all_arrs if name] # Remove empty chuncks

		for arr in all_arrs:
			if arr.sizes != all_arrs[0].sizes:
				sys.exit("Array da leggere insieme devono avere le stesse dimensioni")

			for expr in arr.sizes:
				if expr.var is not None and expr.var.read == False:
					sys.exit("Quando si legge un array devono essere note le dimensioni")

		input_line = IOline("Array", all_arrs, all_arrs[0].sizes)
		return input_line

	else: # Read variables
		all_vars = re.split(" ", line) # Split line by spaces
		all_vars = [get_primitive_variable(name) for name in all_vars if name] # Remove empty chuncks
		for var in all_vars:
			var.read = True

		input_line = IOline("Variable", all_vars)
		return input_line

def parse_output(line):
	global variables, arrays, functions

	if "[" in line: # Write arrays
		all_arrs = re.sub("[\[\]]", "", line) # Remove square brackets
		all_arrs = re.split(" ", all_arrs) # Split line by spaces
		all_arrs = [get_array_variable(name) for name in all_arrs if name] # Remove empty chuncks

		for arr in all_arrs:
			if arr.sizes != all_arrs[0].sizes:
				sys.exit("Array da scrivere insieme devono avere le stesse dimensioni")

			for expr in arr.sizes:
				if expr.var is not None and expr.var.read == False:
					sys.exit("Quando si scrive un array devono essere note le dimensioni")

		input_line = IOline("Array", all_arrs, all_arrs[0].sizes)
		return input_line

	else: # Write variables
		all_vars = re.split(" ", line) # Split line by spaces
		all_vars = [get_primitive_variable(name) for name in all_vars if name] # Remove empty chuncks
		for var in all_vars:
			var.read = True

		input_line = IOline("Variable", all_vars)
		return input_line


# Parsing grader description file
def parse_description(lines):
	sections = {"variables": False, "prototypes": False, "calls": False, "input": False, "output": False}
	section_lines = {}
	act_section = None
	for line in lines:
		line = line.strip()
		line = re.sub(" +", " ", line) # remove multiple spaces

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
	global variables

	parser = argparse.ArgumentParser(description = "Automatically generate graders and templates in various languages")
	parser.add_argument(\
		"--task_spec",
		metavar = "task_spec",
		action = "store", nargs="?",
		help = "the file describing the grader"
	)
	parser.add_argument(\
		"--task_yaml",
		metavar = "task_yaml",
		action = "store", nargs="?",
		help = "the yaml file describing the task"
	)
	parser.add_argument(\
		"--include_dir",
		metavar = "include_dir",
		action = "store", nargs="?",
		help = "the folder containing include_callable and include_grader"
	)

	group = parser.add_mutually_exclusive_group(required=True)

	group.add_argument(\
		"-l", "--lang",
		nargs = "+",
		metavar = ("lang", "filename"),
		dest = "languages",
		action = "append",
		help = "programming language, grader and template"
	)

	group.add_argument(\
		"-a", "--all",
		action = "store_true",
		default = False,
		help = "create graders and templates in all supported languages (with standard names)"
	)
	
	group.add_argument(\
		"--oii",
		action = "store_true",
		default = False,
		help = "create graders and templates in all supported languages following oii's standard (sol/ and att/)"
	)

	group.add_argument(\
		"--stage",
		nargs = "?",
		metavar = "IO_type",
		const = "normal",
		default = False,
		help = "create graders and templates in C++ following stages' standard (sol/ and att/), IO_type decide whether grader in sol/ must have fastIO or not"
	)

	args = parser.parse_args()
	if args.task_spec is None:
		# Search for a DESCRIPTION_FILE
		directory = os.getcwd()
		while True:
			description = os.path.join(directory, DESCRIPTION_FILE)

			if os.path.isfile(description):
				args.task_spec = description
				break

			if os.path.dirname(directory) == directory:
				break
			else:
				directory = os.path.dirname(directory)

	if args.task_spec is None:
		sys.exit("The " + DESCRIPTION_FILE + " file cannot be found.")

	if args.task_yaml is None:
		# Search for a TASK_YAML
		directory = os.getcwd()
		while True:
			task_yaml = os.path.join(directory, TASK_YAML)

			if os.path.isfile(task_yaml):
				args.task_yaml = task_yaml
				break

			if os.path.dirname(directory) == directory:
				break
			else:
				directory = os.path.dirname(directory)

	if args.task_yaml is None:
		sys.exit("The " + TASK_YAML + " file cannot be found.")


	# Parsing task.yaml
	task_yaml = yaml.safe_load(open(task_yaml, "rt", encoding="utf-8"))
	task_name = task_yaml["name"]
	input_file = task_yaml["infile"]
	output_file = task_yaml["outfile"]

	# End of parsing task.yaml

	# --all, --stage, --oii
	if args.all:
		args.languages = [[lang] for lang in LANGUAGES_LIST]


	if args.stage:
		args.include_dir = "gradergen"
		if args.stage == "fast":
			args.languages = [
				["CPP", "att/grader.cpp", "att/"+task_name+".cpp"],
				["fast_CPP", "sol/grader.cpp", "sol/template_cpp.cpp"]
			]
		elif args.stage == "normal":
			args.languages = [
				["CPP", "att/grader.cpp", "att/"+task_name+".cpp"],
				["CPP", "sol/grader.cpp", "sol/template_cpp.cpp"]
			]
		else:
			sys.exit("The argument of --stage must be `normal`, `fast` or empty.")
	
	if args.oii:
		args.include_dir = "gradergen"
		args.languages = [
			["CPP", "att/grader.cpp", "att/"+task_name+".cpp"],
			["fast_CPP", "sol/grader.cpp", "sol/template_cpp.cpp"],
			["C", "att/grader.c", "att/"+task_name+".c"],
			["fast_C", "sol/grader.c", "sol/template_c.c"],
			["pascal", "att/grader.pas", "att/"+task_name+".pas"],
			["fast_pascal", "sol/grader.pas", "sol/template_pascal.pas"],
		]

	
	# Searching for include_grader and include_callable

	include_dir = os.path.dirname(args.task_spec)
	if args.include_dir is not None:
		include_dir = args.include_dir

	include_grader = {}
	for lang in LANGUAGES_LIST:
		ext = EXTENSIONS_LIST[lang]
		try:
			with open(os.path.join(include_dir, "include_grader." + ext)) as f:
				include_grader[lang] = f.read()
		except IOError:
			pass

	include_callable = {}
	for lang in LANGUAGES_LIST:
		ext = EXTENSIONS_LIST[lang]
		try:
			with open(os.path.join(include_dir, "include_callable." + ext)) as f:
				include_callable[lang] = f.read()
		except IOError:
			pass


	# Parsing description file
	with open(args.task_spec, "r") as task_spec:
		lines = task_spec.read().splitlines()
		section_lines = parse_description(lines)

	# Parsing variables
	for line in section_lines["variables"]:
		parsed = parse_variable(line)
		variables.append(parsed)

	# Parsing prototypes
	prototypes = []
	for line in section_lines["prototypes"]:
		parsed = parse_prototype(line)
		prototypes.append(parsed)

	# Parsing calls
	calls = []
	for line in section_lines["calls"]:
		parsed = parse_call(line)
		calls.append(parsed)

	# Parsing input
	input_ = [] # the _ is needed as input is a builtin function (it would be bad to use a variable named input, even if possible)
	for line in section_lines["input"]:
		parsed = parse_input(line)
		input_.append(parsed)

	# Parsing output
	output =  []
	if "output" in section_lines:
		for line in section_lines["output"]:
			parsed = parse_output(line)
			output.append(parsed)

	# End of parsing description file

	data = {
		"task_name": task_name,
		"input_file": input_file,
		"output_file": output_file,
		"variables": variables,
		"prototypes": prototypes,
		"calls": calls,
		"input": input_,
		"output": output,
	}

	chosen_languages = []
	for lang_options in args.languages:
		lang = lang_options[0]
		if lang not in LANGUAGES_LIST:
			sys.exit("One of the specified languages is not currently supported")

		# grader.extension is the standard name for graders
		if len(lang_options) <= 1:
			grader_name = "{0}grader.{1}".format("fast_" if ("fast" in lang) else "", EXTENSIONS_LIST[lang])
			lang_options.append(grader_name)

		# template_lang.extension is the standard name for templates
		if len(lang_options) <= 2:
			template_name = "template_{0}.{1}".format(lang, EXTENSIONS_LIST[lang])
			lang_options.append(template_name)

		if len(lang_options) > 3:
			sys.exit("For each language you can specify, at most, the names of grader and template")

		chosen_languages.append((lang, lang_options[1], lang_options[2]))

	for lang, grader_name, template_name in chosen_languages:
		print(grader_name, template_name)

		data2 = copy.deepcopy(data)
		if lang in include_grader:
			data2["include_grader"] = include_grader[lang]
		if lang in include_callable:
			data2["include_callable"] = include_callable[lang]

		LangClass, fast_io = CLASSES_LIST[lang]
		LangClass(fast_io, data2).write_files(grader_name, template_name)
