#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Python version check
import sys
from dispcalGUI.meta import py_minversion, py_maxversion

pyver = sys.version_info[:2]
if pyver < py_minversion or pyver > py_maxversion:
	raise RuntimeError("Need Python version >= %s <= %s, got %s" % 
					   (".".join(str(n) for n in py_minversion),
						".".join(str(n) for n in py_maxversion),
					    sys.version.split()[0]))

from dispcalGUI.dispcalGUI import main

main()