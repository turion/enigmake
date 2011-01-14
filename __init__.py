#! /usr/bin/python
# -*- coding: utf-8 -*-

"""enigmake
Dependency resolution
"""

# TODO:
# Vielleicht calc_data in rule umbenennen?
# Wenn Spaß besteht: dirty (wahlweise?) auch als target programmieren, damit es nicht so oft rekursiv aufgerufen wird


import time
import operator
import numbers

class EnigmakeError(StandardError):
	pass

class NotAvailableError(EnigmakeError):
	"""Should be raised whenever data is called that is not available and can't be made available for some reason, e.g. a missing file or an intentional not_available as calc_data."""

def not_available():
	raise NotAvailableError


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

class PreTarget(object): # beautifyme? TESTME
	"""Subclass this and implement __call__ and last_mod to get something that can be a dependency of a target and (potentially) can be used with operators."""
	last_mod = NotImplemented
	def __init__(self, title=None):
		self.title = title
	def __call__(self):
		return NotImplemented
	def dirty(self):
		return False
	def __str__(self):
		if self.title:
			return str(type(self)) + '"' + self.title + '"'
		else:
			return object.__str__(self) # Don't know how to get super working

class TouchPreTarget(PreTarget):
	def touch(self):
		self.last_mod = time.time()
	

class Target(TouchPreTarget):
	"""Encapsulates a piece of data calculated with other data. By declaring dependencies on the other data, a target automatically knows if it has to recalculate its data if a dependency changes its data.
	Call the object to retrieve its data or enforce its calculation (for example as an idle task).
	Parameters: calc_data is a function that takes no parameters and produces the actual data.
	dependencies is the list of all Target instances that are known to contain data which is needed by calc_data.
	Setting calc_now = True means roughly calculating the data immediately after construction."""
	def __init__(self, calc_data, dependencies = None, calc_now = False, first_time_dirty = True, title = None):
		if dependencies == None:
			dependencies = []
		self.dependencies = dependencies			
		self.calc_data = calc_data
		self.hold = False # This prevents the data being recalculated, even it the target is dirty.
		self.touch()
		if calc_now:
			self()
		self.first_time_dirty = first_time_dirty
		TouchPreTarget.__init__(self, title = title)
	def dirty(self):
		"""Can be subclassed for more intelligent and efficient lookups, for example looking up first if calc_data returns a different value than the one stored, and only then return True."""
		return not all([target.last_mod <= self.last_mod and not target.dirty() for target in self.dependencies]) or self.first_time_dirty # TESTME
	def __call__(self, hold=False, dirty=False):
		"""Since there is no easy way to detect whether the code of calc_data was changed by the user, there is the possibility to manually set the dirty flag to true for one calculation."""
		if not self.hold or hold:
			while self.dirty() or dirty:
				for target in self.dependencies:
					target() # Actually not necessary if the user worked flawlessly, because his calc_data will call target() or target would not be needed as dependency. If one of the calculations take to long, this could even harm calculation time, since the other dependencies could get dirty in the meantime and more calculations are made in total than needed. But if the user did put a dependency into dependencies which is not called by calc_data, it will remain dirty forever, causing the loop to be infinite. This is why I leave this. Alternatively, I could run the loop only once.
				self.data = self.calc_data()
				self.touch()
				self.first_time_dirty = False # A bit UGLY
				dirty = False
		return self.data

def op_to_intelligent_op(op):
	def intelligent_op(self, operand):
		operand_type = type(operand)
		if operand_type is PreTarget:
			raise EnigmakeError("A stand-alone PreTarget has no functionality. Subclass PreTarget and implement __call__ and last_mod.")
		elif issubclass(operand_type, PreTarget): # This means that it is possible to call it
			def temp_calc():
				return op(self(), operand())
			dependencies = [self, operand]
		elif issubclass(operand_type, numbers.Number):
			def temp_calc():
				return op(self(), operand)
			dependencies = [self]
		else:
			return NotImplemented
		result = Target(temp_calc, dependencies) # temp_calc has been defined in one of the first ifs
		return result
	return intelligent_op

wanted = ["__add__", "__mul__", "__sub__", "__div__", "__pow__"] # Operators supported for PreTarget, will produce a Target
for opname in wanted:
	if opname in dir(operator):
		type.__setattr__(PreTarget, opname, op_to_intelligent_op(operator.__getattribute__(opname)))
		type.__setattr__(PreTarget, "__r" + opname[2:], op_to_intelligent_op(operator.__getattribute__(opname)))

class Parameter(TouchPreTarget): #TESTME BEAUTIFYME (inheritance)
	def __init__(self, init_data = None, title = None):
		self.data = init_data
		PreTarget.__init__(self, title=title)
	@property
	def data(self):
		return self._data
	@data.setter
	def data(self, value):
		self.touch()
		self._data = value
	def __call__(self):
		return self.data
