#! /usr/bin/python
# -*- coding: utf-8 -*-

"""enigmake.makefile"""

#IMPLEMENTME

import enigmake
import enigmake.filesource

class MakeFile(enigmake.filesource.FileSource):
	"""Represents a makefile. It contains all the targets mentioned in the makefile as attributes of Makefile.targets."""
	# MakeFile.targets.bla hängt von der MF ab
