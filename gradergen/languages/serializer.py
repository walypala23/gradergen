class Language:
	def __init__(self, languages):
		self.languages = languages
	
	# array type
	def at(self, type, dim):
		for lang in self.languages:
			self.languages[lang].at(type, dim)
	
	# write line
	def wl(self, line, tabulation = 0):
		for lang in self.languages:
			self.languages[lang].wl(line, tabulation)
	
	# write comment
	def wc(self, short_description, tabulation = 0):
		for lang in self.languages:
			self.languages[lang].wc(short_description, tabulation)
	
	def declare_variable(self, var):
		for lang in self.languages:
			self.languages[lang].declare_variable(var)
		
	def declare_array(self, arr):
		for lang in self.languages:
			self.languages[lang].declare_array(arr)
	
	def declare_function(self, fun):
		for lang in self.languages:
			self.languages[lang].declare_function(fun)
	
	def allocate_array(self, arr):
		for lang in self.languages:
			self.languages[lang].allocate_array(arr)
	
	def read_arrays(self, all_arrs):
		for lang in self.languages:
			self.languages[lang].read_arrays(all_arrs)
	
	def read_variables(self, all_vars):
		for lang in self.languages:
			self.languages[lang].read_variables(all_vars)
	
	def call_function(self, fun):
		for lang in self.languages:
			self.languages[lang].call_function(fun)
	
	def write_arrays(self, all_arrs):
		for lang in self.languages:
			self.languages[lang].write_arrays(all_arrs)

	def write_variables(self, all_vars):
		for lang in self.languages:
			self.languages[lang].write_variables(all_vars)
	
	def insert_headers(self):
		for lang in self.languages:
			self.languages[lang].insert_headers()
		
	def insert_main(self):
		for lang in self.languages:
			self.languages[lang].insert_main()
	
	def insert_footers(self):
		for lang in self.languages:
			self.languages[lang].insert_footers()
	
	def write_grader(self, grader_files):
		for [lang, grader_file] in grader_files:
			grader = open(grader_file, "w")
			grader.write(self.languages[lang].out)
			grader.close()
