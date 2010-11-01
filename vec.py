
class vec(object):

	__slots__ = ("x", "y", "z")

	def __init__(self, x=0, y=0, z=0):
		self.x = x
		self.y = y
		self.z = z

	def __len__(self):
		return 3

	def __repr__(self):
		return "vec(%s, %s, %s)" % (self.x, self.y, self.z)

	def __iter__(self):
		class Iter:
			def __init__(self, v):
				self.v = v
				self.i = 0
			def next(self):
				try:
					v = self.v[self.i]
					self.i += 1
					return v
				except:
					raise StopIteration
			def __iter__(self):
				return self
		return Iter(self)

	def __getitem__(self, i):
		return (self.x, self.y, self.z)[i]

	def __setitem__(self, i, value):
		if i == 0: self.x = value
		elif i == 1: self.y = value
		elif i == 2: self.z = value
		else: raise IndexError

	def __neg__(self):
		return vec(-self.x, -self.y, -self.z)

	def __add__(self, other):
		return vec(
			self.x + other.x,
			self.y + other.y,
			self.z + other.z)

	def __iadd__(self, other):
		self.x += other.x
		self.y += other.y
		self.z += other.z
		return self

	def __sub__(self, other):
		return vec(
			self.x - other.x,
			self.y - other.y,
			self.z - other.z)

	def __isub__(self, other):
		self.x -= other.x
		self.y -= other.y
		self.z -= other.z
		return self

	def __mul__(self, factor):
		return vec(
			self.x * factor,
			self.y * factor,
			self.z * factor)

	def __rmul__(self, factor):
		return vec(
			self.x * factor,
			self.y * factor,
			self.z * factor)

	def __imul__(self, factor):
		self.x *= factor;
		self.y *= factor;
		self.z *= factor;
		return self

	def dot(self, other):
		return self.x * other.x + self.y * other.y + self.z * other.z

	def cross(self, other):
		return vec(
			self.y * other.z - self.z * other.y,
			self.z * other.x - self.x * other.z,
			self.x * other.y - self.y * other.x)

	def length(self):
		return (self.x * self.x + self.y * self.y + self.z * self.z) ** 0.5

	def normalize(self):
		self *= 1 / self.length()
		return self




