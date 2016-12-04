#!/usr/bin/env python3

import sys
import os
import re # regexp, used to check variables and functions names
import argparse # to parse command line arguments
import copy # to avoid making too many / too few "array allocations" in the grader
import yaml # parse task.yaml

from gradergen.RegexParser import RegexParser
from gradergen.structures import Variable, Array, Parameter, Prototype, Call, IOVariables, IOArrays, Expression
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
    def __init__(self):
        self.variables = {} # name: variable
        self.prototypes = {} # name: proto
        # The ending _ does not mean that this are private, it is used 
        # because input is a reserved word in python.
        self.input_ = [] 
        self.calls = []
        self.output = []
        self.used_names = set()

    def add_new_name(self, name):
        if name in self.used_names:
            raise ValueError("Names of variables, arrays and functions must be "
                             "all different. The name {0} was already used."
                                 .format(name))
        self.used_names.add(name)
        
    def add_variable(self, var):
        name = var.name
        self.add_new_name(name)
        self.variables[name] = var
    
    def add_prototype(self, proto):
        name = proto.name
        self.add_new_name(name)
        self.prototypes[name] = proto
    
    def get_variable(self, name):
        if name not in self.variables:
            raise NameError("The variable {0} was used without being declared."
                                .format(name))
        return self.variables[name]
    
    def get_prototype(self, name):
        if name not in self.prototypes:
            raise NameError("The function {0} was used without being declared."
                                .format(name))
        return self.prototypes[name]
    
    def make_copy(self):
        return copy.deepcopy({
            "variables": list(self.variables.values()),
            "prototypes": list(self.prototypes.values()),
            "input": self.input_,
            "calls": self.calls,
            "output": self.output,        
        })

# Parsing grader description file
def parse_specification_file(lines):
    sections = {"variables": [], "prototypes": [], "calls": [], "input": [], "output": []}
    section_lines = {}
    act_section = None
    for line_number in range(len(lines)):
        line = lines[line_number]
        line = line.strip()
        line = re.sub(" +", " ", line) # remove multiple spaces

        if line.startswith("#") or len(line) == 0:
            continue

        is_section_title = False
        for section in sections:
            if line == "***" + section + "***":
                if sections[section]:
                    raise SyntaxError("The specification file (task.spec) "
                                      "contains twice the same section.")
                is_section_title = True
                sections[section] = True
                act_section = section
                section_lines[section] = []
                break

        if not is_section_title:
            if not act_section:
                raise SyntaxError("The specification file (task.spec) has to "
                                  "start with a section header.")
            section_lines[act_section].append((line_number, line))
    return section_lines

def raise_parsing_error(section, line_number, line):
    raise SyntaxError("The line {1}, in the {0} section, could not be parsed: {2}"
                          .format(section, line_number, line))

def main():
    global languages_serializer
    global DESCRIPTION_FILE
    global variables
    global prototypes

    parser = argparse.ArgumentParser(description = "Automatically generate graders and templates in various languages")
    parser.add_argument(\
        "--task_spec",
        metavar = "task_spec", action = "store", nargs = "?",
        help = "the file describing the grader"
    )
    parser.add_argument(\
        "--task_yaml",
        metavar = "task_yaml", action = "store", nargs = "?",
        help = "the yaml file describing the task"
    )
    parser.add_argument(\
        "--include_dir",
        metavar = "include_dir", action = "store", nargs="?",
        help = "the folder containing include_callable and include_grader"
    )
    parser.add_argument(\
        "--debug",
        action = "store_true", default = False,
        help = "whether to show the backtrace when an exception is raised"
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
        help = "create graders and templates in all supported languages following "
               "oii's standard (sol/ and att/)"
    )
    group.add_argument(\
        "--stage",
        nargs = "?",
        metavar = "IO_type",
        const = "normal",
        default = False,
        help = "create graders and templates in C++ following stages' standard "
               "(sol/ and att/), IO_type (can be 'normal' or 'fast') decides "
               "whether graders in sol/ must have fastIO or not"
    )

    args = parser.parse_args()

    # Hiding backtrace if --debug is not set
    if not args.debug:
        def NoBacktraceExpectionHandler(exception_type, exception, traceback):
            print("{0}: {1}".format(exception_type.__name__, exception),
                  file=sys.stderr)
        sys.excepthook = NoBacktraceExpectionHandler
    
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
        raise FileNotFoundError("The {0} file cannot be found."
                                    .format(DESCRIPTION_FILE))

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
        raise FileNotFoundError("The {0} file cannot be found."
                                    .format(TASK_YAML))


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
            raise ValueError("The argument of --stage must be `normal`, "
                             "`fast` or empty.")
    
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
            raise NotImplementedError("One of the specified languages is not "
                                      "currently supported.")

        # grader.extension is the standard name for graders
        if len(lang_options) <= 1:
            grader_name = "{0}grader.{1}".format("fast_" if ("fast" in lang) else "", EXTENSIONS_LIST[lang])
            lang_options.append(grader_name)

        # template_lang.extension is the standard name for templates
        if len(lang_options) <= 2:
            template_name = "template_{0}.{1}".format(lang, EXTENSIONS_LIST[lang])
            lang_options.append(template_name)

        if len(lang_options) > 3:
            raise ValueError("For each language you can specify, at most, the "
                             "names of grader and template.")

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
        
        
    if include_grader and len(include_grader) != len(chosen_languages):
        raise FileNotFoundError("The include_grader file has to exist for "
                                "all or for none of the chosen languages.")
    
    include_callable = {}
    for lang, grader_name, template_name in chosen_languages:
        ext = EXTENSIONS_LIST[lang]
        try:
            with open(os.path.join(include_dir, "include_callable." + ext)) as f:
                include_callable[lang] = f.read()
        except IOError:
            pass
    
    if include_callable and len(include_callable) != len(chosen_languages):
        raise FileNotFoundError("The include_callable file has to exist for "
                                "all or for none of the chosen languages.")
    

    # Parsing specication file (task.spec)
    with open(args.task_spec, "r") as task_spec:
        lines = task_spec.read().splitlines()
        section_lines = parse_specification_file(lines)
        
    # Here all the data is parsed from task.spec using regex_parser and inserted
    # in data_manager. All compilation-like checks are done by the constructor
    # of each object so as to not have to check anything here.
    regex_parser = RegexParser()
    data_manager = DataManager()    

    try:
        # Parsing variables
        for line_number, line in section_lines["variables"]:
            if regex_parser.FullMatch("variable", line):
                match_tree = regex_parser.MatchTree("variable", line)
                new_variable = Variable(match_tree)
                data_manager.add_variable(new_variable)
            elif regex_parser.FullMatch("array", line):
                match_tree = regex_parser.MatchTree("array", line)
                new_array = Array(match_tree, data_manager)
                data_manager.add_variable(new_array)
            else:
                raise_parsing_error("variables", line_number, line)

        # Parsing prototypes
        for line_number, line in section_lines["prototypes"]:
            if regex_parser.FullMatch("prototype", line):
                match_tree = regex_parser.MatchTree("prototype", line)
                new_proto = Prototype(match_tree, include_grader)
                data_manager.add_prototype(new_proto)
            else:
                raise_parsing_error("prototypes", line_number, line)

        # Parsing input
        for line_number, line in section_lines["input"]:
            if regex_parser.FullMatch("IO_variables", line):
                match_tree = regex_parser.MatchTree("IO_variables", line)
                new_input = IOVariables(match_tree, data_manager, "input")
                data_manager.input_.append(new_input)
                for var in new_input.variables:
                    var.known = True
            elif regex_parser.FullMatch("IO_arrays", line):
                match_tree = regex_parser.MatchTree("IO_arrays", line)
                new_input = IOArrays(match_tree, data_manager, "input")
                data_manager.input_.append(new_input)
                for arr in new_input.arrays:
                    arr.known = True
            else:
                raise_parsing_error("input", line_number, line)

        # Parsing calls
        for line_number, line in section_lines["calls"]:
            if regex_parser.FullMatch("call", line):
                match_tree = regex_parser.MatchTree("call", line)
                new_call = Call(match_tree, data_manager)
                data_manager.calls.append(new_call)
                for param, by_ref in new_call.parameters:
                    if by_ref:
                        param.known = True
                if new_call.return_var is not None:
                    new_call.return_var.known = True
            else:
                raise_parsing_error("calls", line_number, line)

        # Parsing output
        for line_number, line in section_lines["output"]:
            if regex_parser.FullMatch("IO_variables", line):
                match_tree = regex_parser.MatchTree("IO_variables", line)
                new_output = IOVariables(match_tree, data_manager, "output")
                data_manager.output.append(new_output)
            elif regex_parser.FullMatch("IO_arrays", line):
                match_tree = regex_parser.MatchTree("IO_arrays", line)
                new_output = IOArrays(match_tree, data_manager, "output")
                data_manager.output.append(new_output)
            else:
                raise_parsing_error("output", line_number, line)
    except Exception as e:
        error_message = \
            "{2}\nError at line {0}: {1}".format(line_number, line, str(e))
        raise type(e)(error_message).with_traceback(sys.exc_info()[2])
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
