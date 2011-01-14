#! /usr/bin/python
# -*- coding: utf-8 -*-

"""enigmake.files
Dependent files
"""

import os, time
def time_of_last_modification(filename):
	return os.stat(filename).st_mtime # in seconds since the epoch

import enigmake

def pickle_dump_file_method(filename):
	import cPickle
	def dump_file_method(data):
		with open(filename, "w") as pickle_file:
			cPickle.dump(data, pickle_file)
	return dump_file_method

def pickle_load_file_method(filename):
	import cPickle
	def load_file_method():
		with open(filename) as pickle_file:
			return cPickle.load(pickle_file)
	return load_file_method


class FileTarget(enigmake.Target):
	"""Makes the data persistent by automatically storing it in a file on assignment.
	calc_data is still the way to calculate the data, but before calculating it, an attempt is made to load the data with load_file_method, if calc_now, load_now have the default values False, True. So the file is not only used for persistence, but also for caching across several program runs.
	You can also use FileTarget to store the output of the dependent calculations in the format of choice, just specify the corresponding dump_file_method."""
	def __init__(self, calc_data, dependencies, filename, dump_file_method, load_file_method, load_now=True, **kwargs):
		self.dump_file_method = dump_file_method
		self.load_file_method = load_file_method
		enigmake.Target.__init__(self, calc_data, dependencies, **kwargs)
		if load_now:
			try:
				self._data = self.load_file_method()
			except IOError: # self.load_file_method raised some error because e.g. the file didn't exist
				pass
			else: # The file was opened correctly, no need to recalculate if none of the dependencies is dirty
				self.last_mod = time_of_last_modification(filename)
				self.first_time_dirty = False
	@property
	def data(self):
		"""Do del FileTarget._data to enforce reloading."""
		return self._data
	@data.setter
	def data(self, value):
		self._data = value
		self.dump_file_method(self._data)
	def __call__(self):
		try:
			self.data
		except AttributeError:
			try:
				self.data = self.load_file_method()
			except IOError: # File didn't exist or was corrupted.
				self.first_time_dirty = True # Will be recalculated and rewritten in subsequent __call__.
		return enigmake.Target.__call__(self)

#TESTME
class SimpleFileTarget(FileTarget):
	"""Convenient, if the file reading and writing can be implemented in one block."""
	def __init__(self, calc_data, dependencies, filename, dump_filehandler_method, load_filehandler_method, **kwargs):
		def dump_file_method(data):
			with open(filename, "w") as filehandle:
				dump_filehandler_method(filehandle, data)
		def load_file_method():
			with open(filename) as filehandle:
				return load_filehandler_method(filehandle)
		FileTarget.__init__(self, calc_data, dependencies, filename, dump_file_method, load_file_method, **kwargs)

#TESTME
class LinesFileTarget(SimpleFileTarget):
	"""The data is a list containing all the lines of the file. This is a short example for SimpleFileTarget."""
	def __init__(self, calc_data, dependencies, filename, **kwargs):
		SimpleFileTarget.__init__(self, calc_data, dependencies, filename, lambda filehandle, data: filehandle.writelines(data), lambda filehandle: filehandle.readlines(), **kwargs)

class PickleFileTarget(FileTarget): # Could be implemented with help of SimpleFileTarget also.
	"""A convenient choice that works out of the box with all pickable data formats."""
	def __init__(self, calc_data, dependencies, filename, **kwargs):
		FileTarget.__init__(self, calc_data, dependencies, filename, pickle_dump_file_method(filename), pickle_load_file_method(filename), **kwargs)

class MultithreadingFileTarget(FileTarget): #TESTME (join)
	"""In case the writing procedure takes a long time, it is convenient to do the writing in another thread, so calculations and everything else can go on."""
	def __init__(self, calc_data, dependencies, dump_file_method, *args, **kwargs):
		import threading
		self.write_lock = threading.Lock()
		self.write_queue_size = 0
		def threading_dump_file_method():
			def threading_dump():
				self.write_queue_size += 1 # Tell self that an attempt to write the data in a subthread is made
				with self.write_lock:
					self.write_queue_size -= 1
					if not self.write_queue_size: # There are no other *later* attempts to write. If there were, do not write and leave writing to the later ones, to avoid writing redundant data.
						dump_file_method()
			thread = threading.Thread(target=threading_dump)
			thread.start() # I never spent a thought on how and when to join the thread.
			
#class MultithreadingPickleFileTarget
#	I will write this as soon as I understand super classes

#BEAUTIFYME? join with FileTarget and Parameter somehow.
class PickleRuntimeConstant(enigmake.PreTarget):
	"""Similar to a parameter, but init_constant_data must be immutable and the data contained cannot change at runtime. It may change, however, from one run of the program to the next. It is pickled internally and compared to the last value, thus allowing to estimate the modification time and being considered as dirty automatically. For comparison, the == operator must be implemented, and it must be pickleable."""
	def __init__(self, init_constant_data, filename):
		try:
			stored_data = pickle_load_file_method(filename)()
		except IOError: # File is corrupt or doesn't exist
			pass
		try:
			assert stored_data == init_constant_data # Needs == to be implemented!
		except (AssertionError, NameError): # They were unequal or stored_data wasn't loaded
			pickle_dump_file_method(filename)(init_constant_data)
		self.last_mod = time_of_last_modification(filename)
		self.data = init_constant_data
	def __call__(self):
		return self.data

# IMPLEMENTME Something for long, stepwise calculation that is slightly KeyboardInterrupt safe: try finally, or subclass Shelf
# IMPLEMENTME Picklify returns some FileTarget subclass in pickled version
