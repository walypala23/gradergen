from structures import Variable, Array, Function

class Language:
	def __init__(self):
		self.out = ""
	
	types = {'': 'void', 'int':'int', 'l':'long int', 'll':'long long int', 'ull':'unsigned long long int', 'char':'char', 'double':'double', 'float':'float'}
	
	stdio_types = {'int':'d', 'l':'ld', 'll':'lld', 'ull':'llu', 'char':'c', 'double':'lf', 'float':'f'}
	
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
		self.out += "\n" + ("\t"*tabulation) + "// " + self.comments[short_description] +"\n"
	
	def DeclareVariable(self, var):
		self.wl("static {0} {1};".format(self.types[var.type], var.name))
		
	def DeclareArray(self, arr):
		self.wl("static {0} {1};".format(self.at(arr.type, arr.dim), arr.name) )
	
	def DeclareFunction(self, fun):
		typed_parameters = []
		for param in fun.parameters:
			if type(param) == Variable:
				typed_parameters.append(self.types[param.type] + " " + param.name)
			elif type(param) == Array:
				typed_parameters.append(self.at(param.type, param.dim) + " " + param.name)
		self.wl("{0} {1}({2});".format(self.types[fun.type], fun.name, ", ".join(typed_parameters)))
	
	def AllocateArray(self, arr):
		for i in range(0, arr.dim):
			if i != 0:
				self.wl("for (int {0} = 0; {0} < {1}; {0}++) {{".format("i" + str(i-1), arr.sizes[i-1]), i)
				
			indexes = "".join("[i" + str(x) + "]" for x in range(0,i))
			self.wl("{0}{1} = ({2}*)malloc({3} * sizeof({2}));".format(arr.name, indexes, self.at(arr.type, arr.dim-i-1), arr.sizes[i]), i+1)
			
		for i in range(0, arr.dim - 1):
			self.wl("}", arr.dim - i - 1)
	
	def ReadArrays(self, all_arrs):
		all_dim = all_arrs[0].dim
		all_sizes = all_arrs[0].sizes
		for i in range(0, all_dim):
			self.wl("for (int {0} = 0; {0} < {1}; {0}++) {{".format("i" + str(i), all_sizes[i]), i+1)
			
		format_string = " ".join("%" + self.stdio_types[arr.type] for arr in all_arrs)
		indexes = "".join("[i" + str(x) + "]" for x in range(0, all_dim))
		pointers = ", ".join("&" + arr.name + indexes for arr in all_arrs)
		self.wl("fscanf(fr, \"{0}\", {1});".format(format_string, pointers), all_dim+1)
			
		for i in range(0, all_dim):
			self.wl("}", all_dim - i)
	
	def ReadVariables(self, all_vars):
		format_string = " ".join("%" + self.stdio_types[var.type] for var in all_vars)
		pointers = ", ".join("&" + var.name for var in all_vars)
		self.wl("fscanf(fr, \"{0}\", {1});".format(format_string, pointers), 1)
	
	def CallFunction(self, fun):
		parameters = ', '.join([param.name for param in fun.parameters])
		if fun.type == "":
			self.wl("{0}({1});".format(fun.name, parameters), 1)
		else:
			self.wl("{2} = {0}({1});".format(fun.name, parameters, fun.return_var.name), 1)
	
	def WriteArrays(self, all_arrs):
		all_dim = all_arrs[0].dim
		all_sizes = all_arrs[0].sizes
		
		for i in range(0, all_dim):
			self.wl("for (int {0} = 0; {0} < {1}; {0}++) {{".format("i" + str(i), all_sizes[i]), i+1)
		
		format_string = " ".join("%" + self.stdio_types[arr.type] for arr in all_arrs)
		indexes = "".join("[i" + str(x) + "]" for x in range(0, all_dim))
		antipointers = ", ".join(arr.name + indexes for arr in all_arrs)
		if len(all_arrs) > 1:
			self.wl("fprintf(fw, \"{0}\\n\", {1});".format(format_string, antipointers), all_dim+1)
		else:
			self.wl("fprintf(fw, \"{0}\", {1});".format(format_string, antipointers), all_dim+1)
		
		for i in range(0, all_dim):
			self.wl("}", all_dim - i)
			if i == all_dim-1 and len(all_arrs) > 1:
				self.wl("fprintf(fw, \"\\n\");", all_dim - i)

	def WriteVariables(self, all_vars):
		format_string = " ".join("%" + self.stdio_types[var.type] for var in all_vars)
		antipointers = ", ".join(var.name for var in all_vars)
		self.wl("fprintf(fw, \"{0}\\n\", {1});".format(format_string, antipointers), 1)
	
	def insert_headers(self):
		self.out += self.headers
		
	def insert_main(self):
		self.out += self.main_function
	
	def insert_footers(self):
		self.out += self.footers