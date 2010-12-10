#! /usr/bin/python
# -*- coding: utf-8 -*-

"""enigmake.filesource
Intelligent read-only file as a dependency"""

#TESTME

import os, time
def time_of_last_modification(filename):
	return os.stat(filename).st_mtime # in seconds since the epoch

class FileSource(object):
	"""Keeps track of the time of last modification of a given file and allocates its contents in the attribute data.
	This is not an enigmake.Target since it has no writing access and the data is merely loaded from the given file. But a FileSource can be used as a dependency for an enigmake.Target since it has the same syntax regarding data, dirty and __call__."""
	def __init__(self, filename, load_file_method, load_now=False):
		self.last_time = 0 # I hope, no one will ever use this module on a file created before the unix epoch. If so, it will never load the file. In regular use, this makes it dirty from the beginning.
		self.filename = filename
		self.load_file_method = load_file_method
		if load_now:
			self()
	@property
	def dirty(self):
		self.new_time = time_of_last_modification(self.filename)
		return self.new_time > self.last_time
	def __call__(self):
		if self.dirty:
			self.data = self.load_file_method()
			self.last_time = self.new_time # In case load_file_method raises an error, last_time stays unchanged and the source is still dirty.
		return self.data # Raises AttributeError only if last_time is messed up before calling the source the first time, e.g. on a file older than the unix epoch.

class PickleFileSource(FileSource):
	def __init__(self, filename, **kwargs):
		import files
		FileSource.__init__(self, filename, files.pickle_load_file_method(filename, **kwargs))
