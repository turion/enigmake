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
	calc_data is still the way to calculate the data, but before calculating it, an attempt is made to load the data with load_file_method, if calc_now, load_now are the default False, True. So the file is not only used for persistence, but also for caching across several program runs.
	You can also use FileTarget to store the output of the dependent calculations in the format of choice, just specify the corresponding dump_file_method."""
	def __init__(self, calc_data, dependencies, filename, dump_file_method, load_file_method, load_now=True, **kwargs):
		self.dump_file_method = dump_file_method
		self.load_file_method = load_file_method
		if load_now:
			try:
				self._data = self.load_file_method() # Calls self.load_file_method()
				self.last_mod = time_of_last_modification(filename) # The file was opened correctly, no need to recalculate if none of the dependencies is dirty
			except: # self.load_file_method raised some error because e.g. the file didn't exist
				pass
		enigmake.Target.__init__(self, calc_data, dependencies, **kwargs)
		try: # UGLY
			self.last_mod
			self.first_time_dirty = False
		except AttributeError:
			pass
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
		

class PickleFileTarget(FileTarget):
	"""A convenient choice that works out of the box with all pickable data formats."""
	def __init__(self, calc_data, dependencies, filename, **kwargs):
		FileTarget.__init__(self, calc_data, dependencies, filename, pickle_dump_file_method(filename), pickle_load_file_method(filename), **kwargs)

class MultithreadingFileTarget(FileTarget):
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

