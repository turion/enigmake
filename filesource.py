#! /usr/bin/python
# -*- coding: utf-8 -*-

"""enigmake.filesource
Intelligent read-only file as a dependency"""

import files, enigmake


class FileSource(object): # Vielleicht doch als Klasse mit Target in Verbindung bringen? Mit gemeinsamer Überklasse?
	"""Keeps track of the time of last modification of a given file and allocates its contents in the attribute data. The file can be modified during runtime, and the FileSource will correctly assign the modified time.
	This is not an enigmake.Target since it has no writing access and the data is merely loaded from the given file. But a FileSource can be used as a dependency for an enigmake.Target since it has the same syntax regarding data, dirty and __call__."""
	def __init__(self, filename, load_file_method, load_now=False):
		self.last_mod = 0 # I hope, no one will ever use this module on a file created before the unix epoch. If so, it will never load the file. In regular use, this makes it dirty from the beginning.
		self.filename = filename
		self.load_file_method = load_file_method
		if load_now:
			self()
	def dirty(self):
		self.new_mod = files.time_of_last_modification(self.filename)
		return self.new_mod > self.last_mod
	def __call__(self):
		if self.dirty():
			self.data = self.load_file_method()
			self.last_mod = self.new_mod # In case load_file_method raises an error, last_time stays unchanged and the source is still dirty.
		return self.data # Raises AttributeError only if last_time is messed up before calling the source the first time, e.g. on a file older than the unix epoch.

class PickleFileSource(FileSource):
	def __init__(self, filename, **kwargs):
		FileSource.__init__(self, filename, files.pickle_load_file_method(filename, **kwargs))

if __name__ == "__main__":
	filename = 'bla.txt' # Create this file and enter some number.
	def load_text_to_number():
		with open(filename) as textfile:
			number = int(textfile.readline())
		return number
	source = FileSource(filename, load_text_to_number)
	def root():
		return source()**0.5
	middle = files.PickleFileTarget(root, [source], 'middle.pickle')
	def third_power():
		return middle()**3
	drain = enigmake.Target(third_power, [middle])
	import time
	while True:
		print drain()
		print "Type some letter to quit."
		if raw_input():
			break
