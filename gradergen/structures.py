class Variable:
	def __init__(self, n, t):
		self.name = n
		self.type = t
		self.read = False

class Array:
	def __init__(self, n, t, s):
		self.name = n
		self.type = t
		self.dim = len(s)
		self.sizes = s
		self.allocated = False

class Function:
	def __init__(self, n = None, p = None, b = None, r = None):
		self.name = n
		self.parameters = p
		self.by_ref = b
		if r != None:
			self.type = r.type
			self.return_var = r
		else:
			self.type = ""
			self.return_var = None

class IOline:
	def __init__(self, t = None, l = None, s = None):
		self.type = t
		self.list = l
		if self.type == "Array":
			self.sizes = s

class Expression:
	# a*var+b
	def __init_(self, v = None, a = 1, b = 0):
		if type(a) != int or type(b) != int or (type(v) != Variable and v != None): 
			sys.exit("I parametri passati per inizializzare un'espressione sono del tipo sbagliato")
		
		if self.a == 0:
			sys.exit("Il coefficiente di un'espressione non può essere 0")
		
		self.var = v
		self.a = a
		self.b = b 
	
	def to_string():
		res = ""
		if self.var==None:
			res += self.b
			return res
		
		if self.a == -1:
			res += "-"
		elif self.a != -1 and self.a != 1:
			res += str(self.a) + " * "
		
		res += self.var.name
		
		if self.b != 0:
			if self.b>0:
				res+=" + " + str(self.b)
			else:
				res+=str(self.b)
