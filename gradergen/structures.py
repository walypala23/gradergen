class Variable:
	def __init__(self, n, t):
		self.name = n
		self.type = t
		self.known = False # This is not used in any single language class, but only in the main parser.

class Array:
	def __init__(self, n, t, s):
		self.name = n
		self.type = t
		self.dim = len(s)
		self.sizes = s
		self.allocated = False # Handled only by single language classes. It is used to know when to allocate an array.
		self.known = False # This is not used in any single language class, but only in the main parser.
		
class Parameter:
	def __init__(self, n, t, d = 0, b = False):
		self.name = n
		self.type = t # One of the primitive types
		self.dim = d # This is the dimension, 0 means it is a simple variable
		self.by_ref = b

class Prototype:
	def __init__(self, n = "", p = None, t = "", o = "solution"):
		if p is None:
			p = []
		
		self.name = n
		self.parameters = p # List of Parameters
		self.type = t # One of the primitive types (array not supported)
		# Where this prototype should be defined. 
		# Can be 'solution', if this prototype has to be defined by the contestant
		# in his solution, or 'grader' if this prototype should be defined in
		# include_grader.
		# If the value is 'grader', then this prototype is not included in templates.
		self.location = o # TODO: Should be an enum
			
class Call:
	def __init__(self, n = "", p = None, r = None, proto = None):
		if p is None:
			p = []
		self.name = n
		self.parameters = p # List of (Variable/Array, by_ref). The by_ref is not parsed but deduced from the matched prototype.
		self.return_var = r # Cannot be an Array, must be a simple Variable.
		self.prototype = proto # The prototype matched by this call

class IOline:
	def __init__(self, t = None, l = None, s = None):
		self.type = t
		self.list = l
		if self.type == "Array":
			self.sizes = s

class Expression:
	# a*var+b
	def __init__(self, v = None, a = 1, b = 0):
		if type(a) != int or type(b) != int or (type(v) != Variable and v != None):
			sys.exit("I parametri passati per inizializzare un'espressione sono del tipo sbagliato")

		if a == 0:
			sys.exit("Il coefficiente di un'espressione non può essere 0")

		self.var = v
		self.a = a
		self.b = b

	def to_string(self):
		res = ""
		if self.var==None:
			res += str(self.b)
			return res

		if self.a == -1:
			res += "-"
		elif self.a != -1 and self.a != 1:
			res += str(self.a) + "*"

		res += self.var.name

		if self.b != 0:
			if self.b>0:
				res+="+" + str(self.b)
			else:
				res+=str(self.b)
		return res

	def __eq__(self, expr2):
		return (self.a == expr2.a and self.b == expr2.b and self.var == expr2.var)

	def __ne__(self, expr2):
		return not self.__eq__(expr2)
