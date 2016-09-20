import pkg_resources
from os import unlink
from gradergen import structures
from gradergen.structures import PrimitiveType, Location, Variable, Array, Parameter, Prototype, Call, IOVariables, IOArrays, Expression
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
	byref_call = ""
	byref_access = ""
