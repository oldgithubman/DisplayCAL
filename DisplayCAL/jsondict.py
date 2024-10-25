# -*- coding: utf-8 -*-

from __future__ import absolute_import
# -*- coding: utf-8 -*-

from . import demjson_compat

from .lazydict import LazyDict


class JSONDict(LazyDict):

	"""
	JSON lazy dictionary
	
	"""
	
	def parse(self, fileobj):
		dict.update(self, demjson_compat.decode(fileobj.read()))
