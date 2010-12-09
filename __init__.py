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


class Target(object):
	def __init__(self, calc_data, dependencies = None, calc_now = False):
		if not dependencies:
			dependencies = []
		self.dependencies = dependencies			
		self._dirty = True
		self.calc_data = calc_data
		if calc_now:
			self()
	@property
	def dirty(self):
		return self._dirty or reduce(lambda x, y: x or y, [target.dirty for target in self.dependencies], False)
	@dirty.setter
	def dirty(self, value):
		self._dirty = value
	def __call__(self):
		print "Accessing", self, "data"
		while self.dirty:
			print "Dirty"
			for target in self.dependencies:
				target() # Actually not necessary if the user worked flawlessly, because his calc_data will call target() or target would not be needed as dependency.
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
