import pkg_resources
import sys
from gradergen import structures
from gradergen.structures import Variable, Array, Function, IOline, Expression
from gradergen.languages.C import LanguageC


class LanguageCPP(LanguageC):
	extension = "cpp"

	headers = """\
#include <cstdio>
#include <cassert>
#include <cstdlib>

static FILE *fr, *fw;
"""

	byref_symbol = " &"

	def call_function(self, fun):
		"""In C++ the byref passage does not require the & symbol.
		"""
		parameters = ', '.join([param.name for param in fun.parameters])
		if fun.type == "":
			self.write_line("{0}({1});".format(fun.name, parameters), 1)
		else:
			self.write_line("{2} = {0}({1});".format(fun.name, parameters, fun.return_var.name), 1)
