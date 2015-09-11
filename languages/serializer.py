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
	
	def DeclareVariable(self, var):
		for lang in self.languages:
			self.languages[lang].DeclareVariable(var)
		
	def DeclareArray(self, arr):
		for lang in self.languages:
			self.languages[lang].DeclareArray(arr)
	
	def DeclareFunction(self, fun):
		for lang in self.languages:
			self.languages[lang].DeclareFunction(fun)
	
	def AllocateArray(self, arr):
		for lang in self.languages:
			self.languages[lang].AllocateArray(arr)
	
	def ReadArrays(self, all_arrs):
		for lang in self.languages:
			self.languages[lang].ReadArrays(all_arrs)
	
	def ReadVariables(self, all_vars):
		for lang in self.languages:
			self.languages[lang].ReadVariables(all_vars)
	
	def CallFunction(self, fun):
		for lang in self.languages:
			self.languages[lang].CallFunction(fun)
	
	def WriteArrays(self, all_arrs):
		for lang in self.languages:
			self.languages[lang].WriteArrays(all_arrs)

	def WriteVariables(self, all_vars):
		for lang in self.languages:
			self.languages[lang].WriteVariables(all_vars)
	
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
