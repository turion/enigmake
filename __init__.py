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

import time
class Target(object):
	"""Encapsulates a piece of data calculated with other data. By declaring dependencies on the other data, a target automatically knows if it has to recalculate its data if a dependency changes its data.
	Call the object to retrieve its data or enforce its calculation (for example as an idle task).
	Parameters: calc_data is a function that takes no parameters and produces the actual data.
	dependencies is the list of all Target instances that are known to contain data which is needed by calc_data.
	Setting calc_now = True means roughly calculating the data immediately after construction."""
	def __init__(self, calc_data, dependencies = None, calc_now = False):
		if not dependencies:
			dependencies = []
		self.dependencies = dependencies			
		self.calc_data = calc_data
		self.hold = False # This prevents the data being recalculated, even it the target is dirty.
		self.touch()
		if calc_now:
			self()
		self.first_time_dirty = True
	def dirty(self):
		"""Can be subclassed for more intelligent and efficient lookups, for example looking up first if calc_data returns a different value than the one stored, and only then return True."""
		return reduce(lambda x, y: x or y, [target.last_mod > self.last_mod for target in self.dependencies], False) or self.first_time_dirty
	def touch(self):
		self.last_mod = time.time()
	def __call__(self):
		if not self.hold:
			while self.dirty():
				for target in self.dependencies:
					target() # Actually not necessary if the user worked flawlessly, because his calc_data will call target() or target would not be needed as dependency. If one of the calculations take to long, this could even harm calculation time, since the other dependencies could get dirty in the meantime and more calculations are made in total than needed. But if the user did put a dependency into dependencies which is not called by calc_data, it will remain dirty forever, causing the loop to be infinite. This is why I leave this. Alternatively, I could run the loop only once.
				self.data = self.calc_data()
				self.touch()
				self.first_time_dirty = False # A bit UGLY
			return self.data

if __name__ == "__main__":
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
