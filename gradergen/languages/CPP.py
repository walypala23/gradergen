import pkg_resources
from gradergen import structures
from gradergen.structures import Variable, Array, Function, IOline, Expression


class Language:
	def __init__(self, fast_io, data):
		self.data = data

		self.out = ""
		if fast_io == 1:
			self.fast_io = True
		else:
			self.fast_io = False
	
	types = {'': 'void', 'int':'int', 'longint':'long long int', 'char':'char', 'real':'double'}
	
	stdio_types = {'int':'d', 'longint':'lld', 'char':'c', 'real':'lf'}
	
	headers = """\
#include <cstdio>
#include <cassert>
#include <cstdlib>

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
		"dec_help": "Declaring helper functions",
		"input": "Reading input", 
		"call_fun": "Calling functions", 
		"output": "Writing output", 
	}
	
	# array type
	def at(self, type, dim):
		return self.types[type] + "*"*dim
	
	# write line
	def wl(self, line, tabulation = 0):
		self.out += "\t"*tabulation + line + "\n"
	
	# write comment
	def wc(self, short_description, tabulation = 0):
		if len(self.comments[short_description]) > 0:
			self.out += "\n" + ("\t"*tabulation) + "// " + self.comments[short_description] +"\n"
	
	def declare_variable(self, var):
		self.wl("static {0} {1};".format(self.types[var.type], var.name))
		
	def declare_array(self, arr):
		self.wl("static {0} {1};".format(self.at(arr.type, arr.dim), arr.name) )
	
	def declare_function(self, fun):
		typed_parameters = []
		for i in range(len(fun.parameters)):
			param = fun.parameters[i]
			if type(param) == structures.Variable:
				if fun.by_ref[i]:
					typed_parameters.append(self.types[param.type] + " &" + param.name)
				else:
					typed_parameters.append(self.types[param.type] + " " + param.name)
			elif type(param) == structures.Array:
				typed_parameters.append(self.at(param.type, param.dim) + " " + param.name)
				
		self.wl("{0} {1}({2});".format(self.types[fun.type], fun.name, ", ".join(typed_parameters)))
	
	def allocate_array(self, arr):
		for i in range(arr.dim):
			if i != 0:
				self.wl("for (int {0} = 0; {0} < {1}; {0}++) {{".format("i" + str(i-1), arr.sizes[i-1].to_string()), i)
				
			indexes = "".join("[i" + str(x) + "]" for x in range(i))
			self.wl("{0}{1} = ({2}*)malloc(({3}) * sizeof({2}));".format(arr.name, indexes, self.at(arr.type, arr.dim-i-1), arr.sizes[i].to_string()), i+1)
			
		for i in range(arr.dim - 1):
			self.wl("}", arr.dim - i - 1)
	
	def read_arrays(self, all_arrs):
		all_dim = all_arrs[0].dim
		all_sizes = all_arrs[0].sizes
		for i in range(all_dim):
			self.wl("for (int {0} = 0; {0} < {1}; {0}++) {{".format("i" + str(i), all_sizes[i].to_string()), i+1)
			
		indexes = "".join("[i" + str(x) + "]" for x in range(0, all_dim))
		if self.fast_io:
			for arr in all_arrs:
				self.wl("{0} = fast_read_{1}();".format(arr.name + indexes, arr.type), all_dim+1)
		else:	
			format_string = " ".join("%" + self.stdio_types[arr.type] for arr in all_arrs)
			pointers = ", ".join("&" + arr.name + indexes for arr in all_arrs)
			# The space after the format_string is used to ignore all whitespaces
			self.wl("fscanf(fr, \"{0} \", {1});".format(format_string, pointers), all_dim+1)
					
		for i in range(all_dim):
			self.wl("}", all_dim - i)
	
	def read_variables(self, all_vars):
		if self.fast_io:
			for var in all_vars:
				self.wl("{0} = fast_read_{1}();".format(var.name, var.type), 1)
		else:
			format_string = " ".join("%" + self.stdio_types[var.type] for var in all_vars)
			pointers = ", ".join("&" + var.name for var in all_vars)
			# The space after the format_string is used to ignore all whitespaces
			self.wl("fscanf(fr, \"{0} \", {1});".format(format_string, pointers), 1)
	
	def call_function(self, fun):
		parameters = ', '.join([param.name for param in fun.parameters])
		if fun.type == "":
			self.wl("{0}({1});".format(fun.name, parameters), 1)
		else:
			self.wl("{2} = {0}({1});".format(fun.name, parameters, fun.return_var.name), 1)
	
	def write_arrays(self, all_arrs):
		all_dim = all_arrs[0].dim
		all_sizes = all_arrs[0].sizes
		
		for i in range(all_dim):
			self.wl("for (int {0} = 0; {0} < {1}; {0}++) {{".format("i" + str(i), all_sizes[i].to_string()), i+1)
		
		indexes = "".join("[i" + str(x) + "]" for x in range(all_dim))
		if self.fast_io:
			for arr in all_arrs:
				self.wl("fast_write_{0}({1});".format(arr.type, arr.name + indexes), all_dim + 1)
				if arr != all_arrs[-1]:
					self.wl("fast_write_char(' ');", all_dim + 1)
			if len(all_arrs) > 1:
				self.wl("fast_write_char('\\n');", all_dim + 1)
			elif all_arrs[0].type != 'char':
				self.wl("fast_write_char(' ');", all_dim + 1)
		else: 
			format_string = " ".join("%" + self.stdio_types[arr.type] for arr in all_arrs)
			antipointers = ", ".join(arr.name + indexes for arr in all_arrs)
			if len(all_arrs) > 1:
				self.wl("fprintf(fw, \"{0}\\n\", {1});".format(format_string, antipointers), all_dim+1)
			elif all_arrs[0].type != 'char':
				self.wl("fprintf(fw, \"{0} \", {1});".format(format_string, antipointers), all_dim+1)
			else:
				self.wl("fprintf(fw, \"{0}\", {1});".format(format_string, antipointers), all_dim+1)
		
		for i in range(all_dim):
			self.wl("}", all_dim - i)
			if i == 0 and len(all_arrs) == 1:
				if self.fast_io:
					self.wl("fast_write_char('\\n');", all_dim - i)
				else:
					self.wl("fprintf(fw, \"\\n\");", all_dim - i)

	def write_variables(self, all_vars):
		if self.fast_io:
			for var in all_vars:
				self.wl("fast_write_{0}({1});".format(var.type, var.name), 1)
				if var != all_vars[-1]:
					self.wl("fast_write_char(' ');", 1)
			self.wl("fast_write_char('\\n');", 1)
		else:
			format_string = " ".join("%" + self.stdio_types[var.type] for var in all_vars)
			antipointers = ", ".join(var.name for var in all_vars)
			self.wl("fprintf(fw, \"{0}\\n\", {1});".format(format_string, antipointers), 1)
	
	def insert_headers(self):
		self.out += self.headers
		
	def insert_main(self):
		if self.fast_io:
			fast_io_file = open(pkg_resources.resource_filename("gradergen.languages", "fast_io.cpp"), "r")
			self.out += "\n" + fast_io_file.read()
			fast_io_file.close()
		
		self.out += self.main_function
	
	def insert_footers(self):
		self.out += self.footers

	def write_files(self, grader_name, helper_name=None):
		self.write_grader(helper_name is not None)
		self.write(grader_name)

	def write_grader(self, use_helper):
		self.out = ""
		self.insert_headers()

		self.wc("dec_var")
		for decl in self.data["declarations_order"]:
			if type(decl) == Variable:
				self.declare_variable(decl)
			else:
				self.declare_array(decl)

		# __import__("pdb").set_trace()
		if use_helper:
			self.wc("dec_help")
			for fun in self.data["helpers_order"]:
				self.declare_function(fun)

		self.wc("dec_fun")
		for fun in self.data["functions_order"]:
			self.declare_function(fun)

		self.insert_main()
		self.wc("input", 1)
		for input_line in self.data["input_order"]:
			if input_line.type == "Array":
				for arr in input_line.list:
					self.allocate_array(arr)
					self.data["arrays"][arr.name].allocated = True
				self.read_arrays(input_line.list)

			elif input_line.type == "Variable":
				self.read_variables(input_line.list)

		self.wc("call_fun", 1)
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
		
		self.wc("output", 1)
		for output_line in self.data["output_order"]:
			if output_line.type == "Array":
				self.write_arrays(output_line.list)
			elif output_line.type == "Variable":
				self.write_variables(output_line.list)
		
		self.insert_footers()

	def write_helper(self):
		raise Exception("C/C++ can use in-place helpers so why not use them?")

	def write(self, filename):
		with open(filename, "w") as f:
			f.write(self.out)
