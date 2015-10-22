import pkg_resources
from gradergen import structures
from gradergen.structures import Variable, Array, Function, IOline, Expression


class LanguagePascal(object):
	def __init__(self, fast_io, data):
		self.data = data

		self.out = ""
		if fast_io == 1:
			self.fast_io = True
		else:
			self.fast_io = False

	types = {'': 'void', 'int':'Longint', 'longint':'Int64', 'char':'Char', 'real':'Double'}

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
{$ifdef EVAL}
    assign(fr, 'input.txt');
    assign(fw, 'output.txt');
{$else}
    fr := input;
    fw := output;
{$endif}
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

	# array type
	def at(self, type, dim):
		return "array of "*dim + self.types[type]

	# write line
	def write_line(self, line, tabulation = 0):
		self.out += "\t"*tabulation + line + "\n"

	# write comment
	def write_comment(self, short_description, tabulation = 0):
		if len(self.comments[short_description]) > 0:
			self.out += "\n" + ("\t"*tabulation) + "{ " + self.comments[short_description] +" }\n"

	def declare_variable(self, var):
		self.write_line("{0} : {1};".format(var.name, self.types[var.type]), 1)
		if var.type == "real" and self.fast_io:
			print("WARNING: pascal doesn't support fast input of floating point variables")

	def declare_array(self, arr):
		self.write_line("{0} : {1};".format(arr.name, self.at(arr.type, arr.dim)), 1)
		if arr.type == "real" and self.fast_io:
			print("WARNING: pascal doesn't support fast output of floating point variables")

	def declare_function(self, fun):  # forse non serve dichiarare le funzioni
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
		parameters = ', '.join([param.name for param in fun.parameters])
		if fun.type == "":
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
			self.out += self.headers_fast_io1 % {"the_name_of_the_task": self.data["task_name"]}
			fast_io_file = open(pkg_resources.resource_filename("gradergen.languages", "fast_input.pas"), "r")
			self.out += "\n" + fast_io_file.read()
			fast_io_file.close()
			fast_io_file = open(pkg_resources.resource_filename("gradergen.languages", "fast_output.pas"), "r")
			self.out += "\n" + fast_io_file.read()
			fast_io_file.close()
			self.out += self.headers_fast_io2
		else:
			self.out += self.headers % {"the_name_of_the_task": self.data["task_name"]}

	def insert_main(self):
		self.write_line("\n{ iterators used in for loops }")
		if len(self.data["arrays"]) > 0:
			max_dim = max(arr.dim for name, arr in self.data["arrays"].items())
			self.write_line(", ".join("i" + str(x) for x in range(max_dim)) + ": Longint;", 1)

		if self.fast_io:
			self.out += self.main_function_fast_io
		else:
			self.out += self.main_function

	def insert_footers(self):
		if self.fast_io:
			self.out += self.footers_fast_io
		else:
			self.out += self.footers

	def write_files(self, grader_name, use_helper):
		self.write_grader()
		self.write(grader_name)

		if use_helper:
			self.write_helper()
			self.write(self.data["task_name"] + "lib.pas")

	def write_grader(self):
		self.out = ""
		self.insert_headers()

		self.write_comment("dec_var")
		for decl in self.data["declarations_order"]:
			if type(decl) == Variable:
				self.declare_variable(decl)
			else:
				self.declare_array(decl)

		self.write_comment("dec_fun")
		for fun in self.data["functions_order"]:
			self.declare_function(fun)

		self.insert_main()
		self.write_comment("input", 1)
		for input_line in self.data["input_order"]:
			if input_line.type == "Array":
				for arr in input_line.list:
					self.allocate_array(arr)
					self.data["arrays"][arr.name].allocated = True
				self.read_arrays(input_line.list)

			elif input_line.type == "Variable":
				self.read_variables(input_line.list)

		self.write_comment("call_fun", 1)
		for fun in self.data["functions_order"]:
			for i in range(len(fun.parameters)):
				param = fun.parameters[i]
				if type(param) == Array and param.allocated == False:
					if not all((expr.var is None or expr.var.read) for expr in param.sizes):
						sys.exit("Devono essere note le dimensioni degli array passati alle funzioni dell'utente")
					self.allocate_array(param)
					param.allocated = True
				if type(param) == Variable and not param.read and not fun.by_ref[i]:
					sys.exit("I parametri non passati per reference alle funzioni dell'utente devono essere noti")

			self.call_function(fun)
			if fun.return_var:
				fun.return_var.read = True

			# Variables passed by reference are "read"
			for i in range(len(fun.parameters)):
				param = fun.parameters[i]
				if type(param) == Variable and fun.by_ref[i]:
					param.read = True

		self.write_comment("output", 1)
		for output_line in self.data["output_order"]:
			if output_line.type == "Array":
				self.write_arrays(output_line.list)
			elif output_line.type == "Variable":
				self.write_variables(output_line.list)

		self.insert_footers()

	def write_helper(self):
		self.out = self.data["helper_data"]

	def write(self, filename):
		with open(filename, "w") as f:
			f.write(self.out)
