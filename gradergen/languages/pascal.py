import pkg_resources
import sys
import os
from gradergen import structures
from gradergen.structures import Variable, Array, Parameter, Prototype, Call, IOline, Expression


class LanguagePascal(object):
	def __init__(self, fast_io, data):
		self.data = data

		self.grader = ""
		self.template = ""
		if fast_io == 1:
			self.fast_io = True
		else:
			self.fast_io = False

	types = {'': '', 'int':'Longint', 'longint':'Int64', 'char':'Char', 'real':'Double'}
	
	template_types = {'':'', 'int':'1', 'longint':'123456789123', 'char':'\'f\'', 'real':'123.456'}

	headers = """\
uses %(the_name_of_the_task)s;

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
uses %(the_name_of_the_task)s, Classes, sysutils;
"""
	headers_fast_io2 = """\
var	\
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
		"dec_fun": "",
		"dec_help": "Declaring helper functions",
		"input": "Reading input",
		"call_fun": "Calling functions",
		"output": "Writing output",
	}

	# Print the string corresponding to a parameter
	def print_parameter(self, param):
		printed_param = ("var " if param.by_ref else "") + param.name + ": "
		if param.dim == 0:
			printed_param += self.types[param.type]
		elif param.dim == 1:
			printed_param += self.at(param.type, param.dim)
		else:
			printed_param += param.type + "matrix"
		
		return printed_param

	# array type
	def at(self, type, dim):
		return "array of "*dim + self.types[type]

	# write line
	def write_line(self, line, tabulation = 0):
		self.grader += "\t"*tabulation + line + "\n"

	# write comment
	def write_comment(self, short_description, tabulation = 0):
		if len(self.comments[short_description]) > 0:
			self.grader += "\n" + ("\t"*tabulation) + "{ " + self.comments[short_description] +" }\n"

	def declare_variable(self, var):
		self.write_line("{0} : {1};".format(var.name, self.types[var.type]), 1)
		if var.type == "real" and self.fast_io:
			print("WARNING: pascal doesn't support fast input of floating point variables")

	def declare_array(self, arr):
		self.write_line("{0} : {1};".format(arr.name, self.at(arr.type, arr.dim)), 1)
		if arr.type == "real" and self.fast_io:
			print("WARNING: pascal doesn't support fast output of floating point variables")

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
				self.write_line("{0} := fast_read_{1}();".format(arr.name + indexes, arr.type), all_dim+1)
		else:
			# pointers = ", ".join(arr.name + indexes for arr in all_arrs)
			# self.write_line("read(fr, {0});".format(pointers), all_dim+1)
			for arr in all_arrs:
				if arr.type == 'char':
					self.write_line("{0} := read_char_skip_whitespaces();".format(arr.name + indexes), all_dim+1)
				else:
					self.write_line("read(fr, {0});".format(arr.name + indexes), all_dim+1)

		for i in range(all_dim):
			self.write_line("end;", all_dim - i)

	def read_variables(self, all_vars):
		if self.fast_io:
			for var in all_vars:
				self.write_line("{0} := fast_read_{1}();".format(var.name, var.type), 1)
		else:
			for var in all_vars:
				if var.type == 'char':
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

	def write_arrays(self, all_arrs):
		all_dim = all_arrs[0].dim
		all_sizes = all_arrs[0].sizes

		for i in range(all_dim):
			self.write_line("for {0} := 0 to {1}-1 do".format("i" + str(i), all_sizes[i].to_string()), i+1)
			self.write_line("begin", i+1)

		indexes = "".join("[i" + str(x) + "]" for x in range(all_dim))
		if self.fast_io:
			for arr in all_arrs:
				self.write_line("fast_write_{0}({1});".format(arr.type, arr.name + indexes), all_dim + 1)
				if arr != all_arrs[-1]:
					self.write_line("fast_write_char(' ');", all_dim + 1)
			if len(all_arrs) > 1:
				self.write_line("fast_write_char(chr(10));", all_dim + 1)
			elif all_arrs[0].type != 'char':
				self.write_line("fast_write_char(' ');", all_dim + 1)
		else:
			antipointers = ", ".join(arr.name + indexes for arr in all_arrs)
			if len(all_arrs) > 1:
				self.write_line("writeln(fw, {0});".format(antipointers), all_dim+1)
			elif all_arrs[0].type != 'char':
				self.write_line("write(fw, {0}, ' ');".format(antipointers), all_dim+1)
			else:
				self.write_line("write(fw, {0});".format(antipointers), all_dim+1)

		for i in range(all_dim):
			self.write_line("end;", all_dim - i)
			if i == 0 and len(all_arrs) == 1:
				if self.fast_io:
					self.write_line("fast_write_char(chr(10));", all_dim - i)
				else:
					self.write_line("writeln(fw);", all_dim - i)

	def write_variables(self, all_vars):
		if self.fast_io:
			for var in all_vars:
				self.write_line("fast_write_{0}({1});".format(var.type, var.name), 1)
				if var != all_vars[-1]:
					self.write_line("fast_write_char(' ');", 1)
			self.write_line("fast_write_char(chr(10));", 1)
		else:
			antipointers = ", ' ', ".join(var.name for var in all_vars)
			self.write_line("writeln(fw, {0});".format(antipointers), 1)

	def insert_headers(self):
		if self.data["task_name"] is "the_name_of_the_task":
			print("warning: Nella prima riga del grader pascal deve essere inserito il nome del file scritto dal contestant")

		if self.fast_io:
			self.grader += self.headers_fast_io1 % {"the_name_of_the_task": self.data["task_name"]}
			fast_io_file = open(pkg_resources.resource_filename("gradergen.languages", "fast_input.pas"), "r")
			self.grader += "\n" + fast_io_file.read()
			fast_io_file.close()
			fast_io_file = open(pkg_resources.resource_filename("gradergen.languages", "fast_output.pas"), "r")
			self.grader += "\n" + fast_io_file.read()
			fast_io_file.close()
			self.grader += self.headers_fast_io2
		else:
			self.grader += self.headers % {"the_name_of_the_task": self.data["task_name"]}

	def insert_main(self):
		self.write_line("\n{ iterators used in for loops }")
		
		max_dim = max(arr.dim for arr in self.data["variables"] if type(arr) == Array)
		if max_dim > 0:
			self.write_line(", ".join("i" + str(x) for x in range(max_dim)) + ": Longint;", 1)

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

	def write_files(self, grader_name, template_name, use_helper):
		self.write_grader()
		self.write(grader_name, self.grader)
		
		self.write_template()
		self.write(template_name, self.template)
		
		if use_helper:
			self.write(self.data["task_name"] + "lib.pas", self.data["helper_data"])

	def write_grader(self):
		self.grader = ""
		self.insert_headers()

		self.write_comment("dec_var")
		for var in self.data["variables"]:
			if type(var) == Variable:
				self.declare_variable(var)
			else:
				self.declare_array(var)

		self.write_comment("dec_fun")
		for fun in self.data["prototypes"]:
			self.declare_prototype(fun)

		self.insert_main()
		self.write_comment("input", 1)
		for input_line in self.data["input"]:
			if input_line.type == "Array":
				for arr in input_line.list:
					self.allocate_array(arr)
					arr.allocated = True
				self.read_arrays(input_line.list)

			elif input_line.type == "Variable":
				self.read_variables(input_line.list)

		self.write_comment("call_fun", 1)
		for fun in self.data["calls"]:
			for (var, by_ref) in fun.parameters:
				if type(var) == Array and var.allocated == False:
					if not all((expr.var is None or expr.var.read) for expr in var.sizes):
						sys.exit("Devono essere note le dimensioni degli array passati alle funzioni dell'utente")
					self.allocate_array(var)
					var.allocated = True
				if type(var) == Variable and not var.read and not by_ref:
					sys.exit("I parametri non passati per reference alle funzioni dell'utente devono essere noti")

			self.call_function(fun)
			if fun.return_var:
				fun.return_var.read = True

			# Variables passed by reference are "read"
			for var, by_ref in fun.parameters:
				if type(var) == Variable and by_ref:
					var.read = True

		self.write_comment("output", 1)
		for output_line in self.data["output"]:
			if output_line.type == "Array":
				self.write_arrays(output_line.list)
			elif output_line.type == "Variable":
				self.write_variables(output_line.list)

		self.insert_footers()

	def write_template(self):
		self.template = "unit {0};\n\n".format(self.data["task_name"])
		self.template += "interface\n\n"
		
		
		matrix_types = []
		for fun in self.data["prototypes"]:
			for param in fun.parameters:
				if type(param) == structures.Array:
					if param.dim == 2:
						matrix_types.append(param.type)
					elif param.dim > 2:
						print("WARNING: pascal doesn't support multidimensional array of dimension > 2 passed as argument")
		
		if len(matrix_types) > 0:
			self.template += "type\n"
			for matrix_type in set(matrix_types):
				self.template += "\t{0}matrix = array of array of {0};\n".format(matrix_type)
			self.template += "\n"
		
		for fun in self.data["prototypes"]:
			printed_parameters = [self.print_parameter(param) for param in fun.parameters]
			if fun.type == '':
				self.template += "procedure {0}({1});\n\n".format(fun.name, "; ".join(printed_parameters))
			else:
				self.template += "function {0}({1}): {2};\n\n".format(fun.name, "; ".join(printed_parameters), self.types[fun.type])
						
		self.template += "implementation\n\n"		
		
		for fun in self.data["prototypes"]:
			printed_parameters = [self.print_parameter(param) for param in fun.parameters]
			if fun.type == '':
				self.template += "procedure {0}({1});\n".format(fun.name, "; ".join(printed_parameters))
			else:
				self.template += "function {0}({1}): {2};\n".format(fun.name, "; ".join(printed_parameters), self.types[fun.type])
			
			self.template += "begin\n"
			
			# Variables passed by ref are filled
			for param in fun.parameters:
				if param.by_ref:
					if param.dim == 0:
						self.template += "\t{0} := {1};\n".format(param.name, self.template_types[param.type])
					else:
						self.template += "\t{0}{1} := {2};\n".format(param.name, "[0]"*param.dim, self.template_types[param.type])
			
			if fun.type == '':
				self.template += "\t\n"
			else:
				self.template += "\t{0} := {1};\n".format(fun.name, self.template_types[fun.type])
			
			self.template += "end;\n\n"
			
		
		self.template += "end.\n"

	def write(self, filename, source):
		# Unlink is used to avoid following symlink
		try:
			os.unlink(filename)
		except OSError:
			pass
		
		with open(filename, "w") as f:
			f.write(source)
