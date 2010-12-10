#! /usr/bin/python
# -*- coding: utf-8 -*-

"""enigmake
Dependency resolution
"""
# Ignore this class for now
class Param(object): # There must be some better way
	def __init__(self):
		object.__setattr__(self, "_deps", {})
	def __call__(self):
		return self._deps
	def __getattr__(self, name):
		try:
			return self._deps[name]
		except KeyError:
			raise AttributeError
	def __setattr__(self, name, value):
		self._deps[name] = value

#FIXME: Modification times have to be taken into account
class Target(object): # DOCME
	"""Encapsulates a piece of data calculated with other data. By declaring dependencies on the other data, a target automatically knows if it has to recalculate its data if a dependency changes its data.
	Call the object to retrieve its data or enforce its calculation (for example as an idle task).
	Parameters: calc_data is a function that takes no parameters and produces the actual data.
	dependencies is the list of all Target instances that are known to contain data which is needed by calc_data.
	Setting calc_now = True means roughly calculating the data immediately after construction."""
	def __init__(self, calc_data, dependencies = None, calc_now = False):
		if not dependencies:
			dependencies = []
		self.dependencies = dependencies			
		self._dirty = True
		self.calc_data = calc_data
		self.hold = False # This prevents the data being recalculated, even it the target is dirty.
		if calc_now:
			self()
	@property
	def dirty(self):
		return self._dirty or self.dep_dirty()
	def dep_dirty(self):
		"""Can be subclassed for more intelligent and efficient lookups, for example looking up first if calc_data returns a different value than the one stored, and only then return True."""
		return reduce(lambda x, y: x or y, [target.dirty for target in self.dependencies], False)
	@dirty.setter
	def dirty(self, value):
		"""A possibility to set the dirty flag manually if e.g. some parameter or external influence changed the output of calc_data."""
		self._dirty = value
	def __call__(self):
		print "Accessing", self, "data"
		if not self.hold:
			while self.dirty:
				print "Dirty"
				#~ for target in self.dependencies:
					#~ target() # Actually not necessary if the user worked flawlessly, because his calc_data will call target() or target would not be needed as dependency. If these calculations take to long, this could even be harmful, since the dependencies could get dirty in the meantime.
				self.data = self.calc_data()
				self._dirty = False
			return self.data

#Tests here

def calc_data1():
	return 3

target1 = Target(calc_data1)


def calc_data2():
	return target1()**4

target2 = Target(calc_data2, [target1])

print target1()
print target2()
target1._dirty = True
print target2()
