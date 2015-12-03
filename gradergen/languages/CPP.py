import pkg_resources
import sys
import os
from gradergen import structures
from gradergen.structures import Variable, Array, Parameter, Prototype, Call, IOline, Expression
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
