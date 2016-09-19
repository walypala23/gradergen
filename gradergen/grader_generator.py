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
DESCRIPTION_FILE = "task.spec"
TASK_YAML = "task.yaml"

class DataManager:
    __init__(self):
        self.variables = {} # name: variable
        self.prototypes = {} # name: proto
        # The ending _ does not mean that this are private, it is used 
        # because input is a reserved word in python.
        self.input_ = [] 
        self.calls = []
        self.output = []
        used_names = set()
    
    add_variable(self, var):
        name = var.name
        if name in used_names:
            sys.exit("Names of variables, arrays and functions must be all different")
        used_names.add(name)
        self.variables[name] = var
    
    add_prototype(self, proto):
        name = proto.name
        if name in used_names:
            sys.exit("Names of variables, arrays and functions must be all different")
        used_names.add(name)
        self.prototypes[name] = var
    
    get_variable(self, name):
        if name not in self.variables:
            sys.exit("One of the variables used has not been declared")
        return self.variables[name]
    
    get_prototype(self, name):
        if name not in self.prototypes:
            sys.exit("One of the function used has not been declared")
        return self.prototypes[name]
    
    make_copy(self):
        return copy.deepcopy({
            "variables": self.variables.values(),
            "prototypes": self.prototypes.values(),
            "input": self.input_,
            "calls": self.calls,
            "output": self.output,        
        })

# variables is used in parsing functions and must be global (only get_variable refers to it)
variables = []
# prototypes is used in parsing calls and must be global (only match_call refers to it)
prototypes = []

using_include_grader = False # Non sarebbe meglio passarlo alle funzioni che lo usano?
using_include_callable = False # Is it really used?

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

# Returns true if the given variable matches the parameter
def match_parameter(variable, parameter):
    if variable.type != parameter.type:
        return False
        
    if type(variable) == Array:
        if variable.dim != parameter.dim:
            return False
    elif parameter.dim != 0:
        return False
    
    return True

# Check whether the call matches one of the prototypes.
# If the call is matched, sets call.proto to the matched prototype. Moreover
# the by_ref boolean of the parameters are also set (deducting them from the
# prototype).
def match_call(call):
    global prototypes
    global variables
    
    for proto in prototypes:
        if proto.name == call.name:
            if len(proto.parameters) != len(call.parameters):
                return False
            
            if proto.type:
                if call.return_var is None:
                    return False 
                if proto.type != call.return_var.type:
                    return False
            elif call.return_var is not None:
                return False
            
            if not all(match_parameter(call.parameters[i][0], proto.parameters[i]) for i in range(len(call.parameters))):
                return False
            
            # Setting by_ref
            for i in range(len(call.parameters)):
                call.parameters[i] = (call.parameters[i][0], proto.parameters[i].by_ref)
            # Setting the prototype
            call.prototypes = proto
            return True
    
    return False


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
    
    after_location_parsing = line
    if "{" in line: # Owner is defined
        location_split = re.split("[\{\}]", line)
        if len(location_split) != 3:
            sys.exit("La descrizione di un prototipo ha un numero errato di parentesi graffe")
        
        if location_split[1] not in ["solution", "grader"]:
            sys.exit("La locazione (tra graffe) di un prototipo deve essere 'solution' o 'grader'")
        
        if location_split[1] == "grader":
            global using_include_grader
            if not using_include_grader:
                sys.exit("Un prototipo non può avere come locazione (tra graffe) il 'grader' se non si sta usando include_grader")
        proto_obj.location = location_split[1]
        after_location_parsing = location_split[0].strip()
    
    first_split = re.split("[\(\)]", after_location_parsing)
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
                parameter = get_variable(param)
                
                if type(parameter) == Array:
                    if not all((expr.var is None or expr.var.known) for expr in parameter.sizes):
                        sys.exit("The sizes of an array passed to a function must be known")
            
                fun_obj.parameters.append((parameter, False))
    
    if not match_call(fun_obj):
        sys.exit("One of the calls doesn't match any prototype.")
        
    for param, by_ref in fun_obj.parameters:
        if not by_ref and not param.known:
            sys.exit("Parameters passed (not by reference) to a function must be known")
    
    # After execution return value and reference parameters are known.
    if fun_obj.return_var is not None:
        fun_obj.return_var.known = True
    for param, by_ref in fun_obj.parameters:
        if by_ref:
            param.known = True
    
    return fun_obj

def parse_input(line):
    if "[" in line: # Read arrays
        all_arrs = re.sub("[\[\]]", "", line) # Remove square brackets
        all_arrs = re.split(" ", all_arrs) # Split line by spaces
        all_arrs = [get_array_variable(name) for name in all_arrs if name] # Remove empty chuncks

        for arr in all_arrs:
            if arr.sizes != all_arrs[0].sizes:
                sys.exit("Array da leggere insieme devono avere le stesse dimensioni")
            
            if not all((expr.var is None or expr.var.known) for expr in arr.sizes):
                sys.exit("Quando si legge un array devono essere note le dimensioni")
            
            arr.known = True
        input_line = IOline("Array", all_arrs, all_arrs[0].sizes)
        return input_line

    else: # Read variables
        all_vars = re.split(" ", line) # Split line by spaces
        all_vars = [get_primitive_variable(name) for name in all_vars if name] # Remove empty chuncks
        for var in all_vars:
            var.known = True

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
                if expr.var is not None and expr.var.known == False:
                    sys.exit("Quando si scrive un array devono essere note le dimensioni")

        input_line = IOline("Array", all_arrs, all_arrs[0].sizes)
        return input_line

    else: # Write variables
        all_vars = re.split(" ", line) # Split line by spaces
        all_vars = [get_primitive_variable(name) for name in all_vars if name] # Remove empty chuncks

        input_line = IOline("Variable", all_vars)
        return input_line


# Parsing grader description file
def parse_description(lines):
    sections = {"variables": [], "prototypes": [], "calls": [], "input": [], "output": []}
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
    global prototypes

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
    
    # Searching for include_grader and include_callable
    include_dir = os.path.dirname(args.task_spec)
    if args.include_dir is not None:
        include_dir = args.include_dir

    include_grader = {}
    for lang, grader_name, template_name in chosen_languages:
        ext = EXTENSIONS_LIST[lang]
        try:
            with open(os.path.join(include_dir, "include_grader." + ext)) as f:
                include_grader[lang] = f.read()
        except IOError:
            pass
        
        
    if include_grader:
        global using_include_grader
        using_include_grader = True
        if len(include_grader) != len(chosen_languages):
            sys.exit("The include_grader file has to exist for all or for none of the chosen languages.")
    
    include_callable = {}
    for lang, grader_name, template_name in chosen_languages:
        ext = EXTENSIONS_LIST[lang]
        try:
            with open(os.path.join(include_dir, "include_callable." + ext)) as f:
                include_callable[lang] = f.read()
        except IOError:
            pass
    
    if include_callable:
        global using_include_callable
        using_include_callable = True
        if len(include_callable) != len(chosen_languages):
            sys.exit("The include_callable file has to exist for all or for none of the chosen languages.")
    

    # Parsing specication file (task.spec)
    with open(args.task_spec, "r") as task_spec:
        lines = task_spec.read().splitlines()
        section_lines = parse_description(lines)
        
    # Here all the data is parsed from task.spec using regex_parser and inserted
    # in data_manager. All compilation-like checks are done by the constructor
    # of each object so as to not have to check anything here.
    regex_parser = RegexParser()
    data_manager = DataManager()    

    # TODO: ERRORS SHOULD BE HANDLED WITH try, except
    # Parsing variables
    for line in section_lines["variables"]:
        if regex_parser.FullMatch("variable", line):
            match_tree = regex_parser.MatchTree("variable", line)
            new_variable = Variable(match_tree)
            data_manager.add_variable(new_variable)
        elif regex_parser.FullMatch(line, "array"):
            match_tree = regex_parser.MatchTree("array", line)
            new_array = Array(match_tree, data_manager)
            data_manager.add_variable(new_array)
        else:
            sys.exit("The following line, in the variables section, could not be parsed:",
                     line)

    # Parsing prototypes
    for line in section_lines["prototypes"]:
        if regex_parser.FullMatch("prototype", line):
            match_tree = regex_parser.MatchTree("prototype", line)
            new_proto = Prototype(match_tree)
            data_manager.add_prototype(new_proto)
        else:
            sys.exit("The following line, in the prototypes section, could not be parsed:",
                     line)

    # Parsing input
    for line in section_lines["input"]:
        if regex_parser.FullMatch("IO_variables", line):
            match_tree = regex_parser.MatchTree("IO_variables", line)
            new_input = IOVariables(match_tree, data_manager, "input")
            data_manager.input_.append(new_input)
            for var in new_input.variables:
                var.known = True
        elif regex_parser.FullMatch("IO_arrays", line):
            match_tree = regex_parser.MatchTree("IO_arrays", line)
            new_input = IOArrays(match_tree, "input")
            data_manager.input_.append(new_input)
            for arr in new_input.arrays:
                arr.known = True
        else:
            sys.exit("The following line, in the input section, could not be parsed:",
                     line)

    # Parsing calls
    for line in section_lines["calls"]:
        if regex_parser.FullMatch("call", line):
            match_tree = regex_parser.MatchTree("call", line)
            new_call = Call(match_tree, data_manager)
            data_manager.calls.append(new_call)
            for param, by_ref in call.parameters:
                if by_ref:
                    param.known = True
        else:
            sys.exit("The following line, in the calls section, could not be parsed:",
                     line)

    # Parsing output
    for line in section_lines["output"]:
        if regex_parser.FullMatch("IO_variables", line):
            match_tree = regex_parser.MatchTree("IO_variables", line)
            new_output = IOVariables(match_tree, data_manager, "output")
            data_manager.output.append(new_output)
        elif regex_parser.FullMatch("IO_arrays", line):
            match_tree = regex_parser.MatchTree("IO_arrays", line)
            new_output = IOArrays(match_tree, data_manager, "output")
            data_manager.output.append(new_output)
        else:
            sys.exit("The following line, in the output section, could not be parsed:",
                     line)

    # End of parsing specification file

    for lang, grader_name, template_name in chosen_languages:
        print(grader_name, template_name)

        data = {
            **data_manager.make_copy(),
            "task_name": task_name,
            "input_file": input_file,
            "output_file": output_file,
        }
        if lang in include_grader:
            data["include_grader"] = include_grader[lang]
        if lang in include_callable:
            data["include_callable"] = include_callable[lang]

        LangClass, fast_io = CLASSES_LIST[lang]
        LangClass(fast_io, data).write_files(grader_name, template_name)
