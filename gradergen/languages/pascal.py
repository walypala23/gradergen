import pkg_resources
from os import unlink
from gradergen import structures
from gradergen.structures import PrimitiveType, Location, Variable, Array, Parameter, Prototype, Call, IOVariables, IOArrays, Expression


class LanguagePascal(object):
    def __init__(self, fast_io, data):
        self.data = data

        self.grader = ""
        self.template = ""
        if fast_io == 1:
            self.fast_io = True
        else:
            self.fast_io = False

    types_names = {
        PrimitiveType.VOID: '', 
        PrimitiveType.INT: 'longint', 
        PrimitiveType.LONGINT: 'int64', 
        PrimitiveType.CHAR: 'char', 
        PrimitiveType.REAL: 'double'
    }

    template_values = {
        PrimitiveType.VOID: '',
        PrimitiveType.INT: '1', 
        PrimitiveType.LONGINT: '123456789123', 
        PrimitiveType.CHAR: '\'f\'', 
        PrimitiveType.REAL: '123.456'
    }

    headers = """\
uses %(task_name)s;

var
    fr, fw : text;

{ used to read char ignoring whitespaces (space, newline, tab...) }
function read_char_skip_whitespaces() : char;
var
   c : char;
begin
   read(fr, c);
   while (ord(c) = $0020) or (ord(c) = $0009) or
         (ord(c) = $000a) or (ord(c) = $000b) or
         (ord(c) = $000c) or (ord(c) = $000d) do
       read(fr, c);

   read_char_skip_whitespaces := c;
end;

var
"""

    headers_fast_io1 = """\
uses %(task_name)s, Classes, sysutils;
"""
    headers_fast_io2 = """\
var    \
"""
    main_function = """\

begin
    %(input)s
    %(output)s
    reset(fr);
    rewrite(fw);
"""
    main_function_fast_io = """\

begin
    init_fast_input('input.txt');
    init_fast_output('output.txt');
"""

    footers = """\

    close(fr);
    close(fw);
end.
"""
    footers_fast_io = """\

    close_fast_input();
    close_fast_output();
end.
"""

    comments = {
        "dec_var": "Declaring variables",
        "loop_iters": "Declaring iterators used in for loops",
        "prototypes": "",
        "include_grader": "Functions ad-hoc for this grader",
        "include_callable": "Functions called by the contestant solution",
        "input": "Reading input",
        "call_fun": "Calling functions",
        "output": "Writing output",
    }

    # Print the string corresponding to a parameter
    def print_parameters(self, params):
        parameters_string = []
        
        i = 0
        while i  < len(params):
            j = i+1
            while j < len(params) and params[i].type == params[j].type and params[i].by_ref == params[j].by_ref and params[i].dim == params[j].dim:
                j += 1
            
            param = params[i]
            printed_param = ("var " if param.by_ref else "") + ', '.join([params[k].name for k in range(i, j)]) + ": "
            # param.dim > 2 is not supported and an error is raised before
            # arriving in this function.
            assert(param.dim <= 2)
            if param.dim == 0:
                printed_param += self.types_names[param.type]
            elif param.dim == 1:
                printed_param += self.at(param.type, param.dim)
            elif param.dim == 2:
                printed_param += self.types_names[param.type] + "matrix"
            parameters_string.append(printed_param)
            
            i = j
        
        return "; ".join(parameters_string)

    # array type
    def at(self, type, dim):
        return "array of "*dim + self.types_names[type]

    # write line
    def write_line(self, line = "", tabulation = 0):
        self.grader += "\t"*tabulation + line + "\n"

    # write comment
    def write_comment(self, short_description, tabulation = 0):
        if len(self.comments[short_description]) > 0:
            self.grader += "\n" + ("\t"*tabulation) + "{ " + self.comments[short_description] +" }\n"

    def declare_variable(self, var):
        self.write_line("{0} : {1};".format(var.name, self.types_names[var.type]), 1)
        if var.type == PrimitiveType.REAL and self.fast_io:
            raise NotImplementedError("In pascal fast input of floating point "
                                      "variables is not supported.")

    def declare_array(self, arr):
        self.write_line("{0} : {1};".format(arr.name, self.at(arr.type, arr.dim)), 1)
        if arr.type == PrimitiveType.REAL and self.fast_io:
            raise NotImplementedError("In pascal fast output of floating point "
                                      "variables is not supported.")

    def declare_prototype(self, fun):  # In pascal it is not needed to declare user functions in grader.pas
        pass

    def allocate_array(self, arr):
        self.write_line("Setlength({0}, {1});".format(arr.name, ", ".join([expr.to_string() for expr in arr.sizes])), 1)

    def read_arrays(self, all_arrs):
        all_dim = all_arrs[0].dim
        all_sizes = all_arrs[0].sizes
        for i in range(all_dim):
            self.write_line("for {0} := 0 to {1}-1 do".format("i" + str(i), all_sizes[i].to_string()), i+1)
            self.write_line("begin", i+1)

        indexes = "".join("[i" + str(x) + "]" for x in range(all_dim))
        if self.fast_io:
            for arr in all_arrs:
                self.write_line("{0} := fast_read_{1}();".format(arr.name + indexes, arr.type.value), all_dim+1)
        else:
            # pointers = ", ".join(arr.name + indexes for arr in all_arrs)
            # self.write_line("read(fr, {0});".format(pointers), all_dim+1)
            for arr in all_arrs:
                if arr.type == PrimitiveType.CHAR:
                    self.write_line("{0} := read_char_skip_whitespaces();".format(arr.name + indexes), all_dim+1)
                else:
                    self.write_line("read(fr, {0});".format(arr.name + indexes), all_dim+1)

        for i in range(all_dim):
            self.write_line("end;", all_dim - i)

    def read_variables(self, all_vars):
        if self.fast_io:
            for var in all_vars:
                self.write_line("{0} := fast_read_{1}();".format(var.name, var.type.value), 1)
        else:
            for var in all_vars:
                if var.type == PrimitiveType.CHAR:
                    self.write_line("{0} := read_char_skip_whitespaces();".format(var.name), 1)
                else:
                    self.write_line("read(fr, {0});".format(var.name), 1)
            # pointers = ", ".join(var.name for var in all_vars)
            # self.write_line("readln(fr, {0});".format(pointers), 1)

    def call_function(self, fun):
        parameters = ', '.join([var.name for (var, by_ref) in fun.parameters])

        if fun.return_var is None:
            self.write_line("{0}({1});".format(fun.name, parameters), 1)
        else:
            self.write_line("{2} := {0}({1});".format(fun.name, parameters, fun.return_var.name), 1)

    def write_single_array(self, arr):
        dim = arr.dim

        for i in range(dim):
            self.write_line("for {0} := 0 to {1}-1 do".format("i" + str(i), arr.sizes[i].to_string()), i+1)
            self.write_line("begin", i+1)

        indexes = "".join("[i" + str(x) + "]" for x in range(dim))
        if self.fast_io:
            self.write_line("fast_write_{0}({1});".format(arr.type.value, arr.name + indexes), dim + 1)
            if arr.type != PrimitiveType.CHAR:
                self.write_line("fast_write_char(' ');", dim + 1)
            self.write_line("end;", dim - i)
            self.write_line("fast_write_char(chr(10));", dim - i)
        else:
            antipointers = arr.name + indexes
            if arr.type != PrimitiveType.CHAR:
                self.write_line("write(fw, {0}, ' ');".format(antipointers), dim+1)
            else:
                self.write_line("write(fw, {0});".format(antipointers), dim+1)
            self.write_line("end;", dim - i)
            self.write_line("writeln(fw);", dim - i)

        for i in range(1, dim):
            self.write_line("end;", dim - i)
    
    def write_many_arrays(self, all_arrs):
        all_dim = all_arrs[0].dim
        all_sizes = all_arrs[0].sizes

        for i in range(all_dim):
            self.write_line("for {0} := 0 to {1}-1 do".format("i" + str(i), all_sizes[i].to_string()), i+1)
            self.write_line("begin", i+1)

        indexes = "".join("[i" + str(x) + "]" for x in range(all_dim))
        if self.fast_io:
            for arr in all_arrs:
                self.write_line("fast_write_{0}({1});".format(arr.type.value, arr.name + indexes), all_dim + 1)
                if arr != all_arrs[-1]:
                    self.write_line("fast_write_char(' ');", all_dim + 1)
            self.write_line("fast_write_char(chr(10));", all_dim + 1)
        else:
            antipointers = ", ' ', ".join(arr.name + indexes for arr in all_arrs)
            self.write_line("writeln(fw, {0});".format(antipointers), all_dim+1)

        for i in range(all_dim):
            self.write_line("end;", all_dim - i)

    def write_variables(self, all_vars):
        if self.fast_io:
            for var in all_vars:
                self.write_line("fast_write_{0}({1});".format(var.type.value, var.name), 1)
                if var != all_vars[-1]:
                    self.write_line("fast_write_char(' ');", 1)
            self.write_line("fast_write_char(chr(10));", 1)
        else:
            antipointers = ", ' ', ".join(var.name for var in all_vars)
            self.write_line("writeln(fw, {0});".format(antipointers), 1)

    def insert_headers(self):
        if self.fast_io:
            self.grader += self.headers_fast_io1 % {"task_name": self.data["task_name"]}
            fast_io_file = open(pkg_resources.resource_filename("gradergen.languages", "fast_input.pas"), "r")
            self.grader += "\n" + fast_io_file.read()
            fast_io_file.close()
            fast_io_file = open(pkg_resources.resource_filename("gradergen.languages", "fast_output.pas"), "r")
            self.grader += "\n" + fast_io_file.read()
            fast_io_file.close()
            self.grader += self.headers_fast_io2
        else:
            self.grader += self.headers % {"task_name": self.data["task_name"]}

    def insert_main(self):
        if self.fast_io:
            self.grader += self.main_function_fast_io
        else:
            self.grader += self.main_function % {
                "input": "fr := input;" if self.data["input_file"] == "" else "assign(fr, '" + self.data["input_file"] + "');",
                "output": "fw := output;" if self.data["output_file"] == "" else "assign(fw, '" + self.data["output_file"] + "');",
            }

    def insert_footers(self):
        if self.fast_io:
            self.grader += self.footers_fast_io
        else:
            self.grader += self.footers

    def write_files(self, grader_name, template_name):
        self.write_grader()
        self.write(grader_name, self.grader)

        self.write_template()
        self.write(template_name, self.template)

        if "include_callable" in self.data:
            self.write(self.data["task_name"] + "lib.pas", self.data["include_callable"])

    def write_grader(self):
        self.grader = ""
        self.insert_headers()

        self.write_comment("dec_var")
        for var in self.data["variables"]:
            if type(var) == Variable:
                self.declare_variable(var)
            else:
                self.declare_array(var)

        # Declaring iterator used in for loops
        max_dim = max(arr.dim for arr in self.data["variables"] if type(arr) == Array)
        if max_dim > 0:
            self.write_comment("loop_iters")
            self.write_line(", ".join("i" + str(x) for x in range(max_dim)) + ": longint;", 1)

        self.write_comment("prototypes")
        for fun in self.data["prototypes"]:
            self.declare_prototype(fun)

        if "include_grader" in self.data:
            self.write_comment("include_grader")
            self.grader += self.data["include_grader"]
            self.write_line()

        self.insert_main()
        self.write_comment("input", 1)
        for input_line in self.data["input"]:
            if type(input_line) == IOArrays:
                for arr in input_line.arrays:
                    self.allocate_array(arr)
                    arr.allocated = True
                self.read_arrays(input_line.arrays)

            elif type(input_line) == IOVariables:
                self.read_variables(input_line.variables)

        self.write_comment("call_fun", 1)
        for fun in self.data["calls"]:
            for (var, by_ref) in fun.parameters:
                if type(var) == Array and var.allocated == False:
                    self.allocate_array(var)
                    var.allocated = True

            self.call_function(fun)

        self.write_comment("output", 1)
        for output_line in self.data["output"]:
            if type(output_line) == IOArrays:
                if len(output_line.arrays) > 1:
                    self.write_many_arrays(output_line.arrays)
                else:
                    self.write_single_array(output_line.arrays[0])
            elif type(output_line) == IOVariables:
                self.write_variables(output_line.variables)

        self.insert_footers()

    def write_template(self):
        self.template = "unit {0};\n\n".format(self.data["task_name"])
        self.template += "interface\n\n"

        
        # Checking multidimensional arrays, as they have to be defined ad-hoc.
        matrix_types = []
        for fun in self.data["prototypes"]:
            if fun.location == Location.GRADER: # Skipping prototypes defined in include_grader
                continue
            for param in fun.parameters:
                if param.dim == 2:
                    matrix_types.append(param.type)
                elif param.dim > 2:
                    raise NotImplementedError(
                        "In pascal multidimensional arrays of dimension > 2 "
                        "passed as arguments of functions are not supported.")

        # Defining ad-hoc matrices
        if len(matrix_types) > 0:
            self.template += "type\n"
            for matrix_type in matrix_types:
                self.template += "\t{0}matrix = array of array of {0};\n".format(self.types_names[matrix_type])
            self.template += "\n"
        
        # Declarations
        for fun in self.data["prototypes"]:
            if fun.location == Location.GRADER: # Skipping prototypes defined in include_grader
                continue
            printed_parameters = self.print_parameters(fun.parameters)
            if fun.type == PrimitiveType.VOID:
                self.template += "procedure {0}({1});\n\n".format(fun.name, printed_parameters)
            else:
                self.template += "function {0}({1}): {2};\n\n".format(fun.name, printed_parameters, self.types_names[fun.type])

        self.template += "implementation\n\n"

        if "include_callable" in self.data:
            self.template += "uses {0}lib;\n\n".format(self.data["task_name"])

        # Definitions
        for fun in self.data["prototypes"]:
            if fun.location == Location.GRADER: # Skipping prototypes defined in include_grader
                continue
            printed_parameters = self.print_parameters(fun.parameters)
            if fun.type == PrimitiveType.VOID:
                self.template += "procedure {0}({1});\n".format(fun.name, printed_parameters)
            else:
                self.template += "function {0}({1}): {2};\n".format(fun.name, printed_parameters, self.types_names[fun.type])

            self.template += "begin\n"

            # Variables passed by ref are filled in the template
            for param in fun.parameters:
                if param.by_ref:
                    if param.dim == 0:
                        self.template += "\t{0} := {1};\n".format(param.name, self.template_values[param.type])
                    else:
                        self.template += "\t{0}{1} := {2};\n".format(param.name, "[0]"*param.dim, self.template_values[param.type])

            if fun.type == PrimitiveType.VOID:
                self.template += "\t\n"
            else:
                self.template += "\t{0} := {1};\n".format(fun.name, self.template_values[fun.type])

            self.template += "end;\n\n"


        self.template += "end.\n"

    def write(self, filename, source):
        # Unlink is used to avoid following symlink
        try:
            unlink(filename)
        except OSError:
            pass

        with open(filename, "w") as f:
            f.write(source)
