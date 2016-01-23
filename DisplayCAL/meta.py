# -*- coding: utf-8 -*-

"""
	Meta information

"""

import re
import sys

try:
	from __version__ import (BUILD_DATE as build, LASTMOD as lastmod, VERSION, 
							 VERSION_BASE, VERSION_STRING)
except ImportError:
	build = lastmod = "0000-00-00T00:00:00.0Z"
	VERSION = VERSION_BASE = (0, 0, 0, 0)
	VERSION_STRING = ".".join(str(n) for n in VERSION)

if sys.version_info[:2] < (3, ):
	author = "Florian Höch".decode("utf8")
else:
	author = "Florian Höch"
author_ascii = "Florian Hoech"
author_email = "florian@displaycal.net"
description = ("A graphical front-end for display calibration and profiling "
			   "using Argyll CMS")
longdesc = "\n".join(["Calibrates and characterizes display devices using a hardware sensor,",
					  "driven by the open source color management system Argyll CMS.",
					  "Supports multi-display setups and a variety of available settings like ",
					  "customizable whitepoint, luminance, black level, tone response curve ",
					  "as well as the creation of matrix and look-up-table ICC profiles with ",
					  "optional gamut mapping. Calibrations and profiles can be verified ",
					  "through measurements, and profiles can be installed to make them ",
					  "available to color management aware applications.",
					  "Profile installation can utilize Argyll CMS, Oyranos and/or GNOME ",
					  "Color Manager if available, for flexible integration."])
domain = "displaycal.net"
name = "DisplayCAL"
name_html = '<span class="appname">Display<span>CAL</span></span>'

py_maxversion = (2, 7)
py_minversion = (2, 6)

version = VERSION_STRING
version_lin = VERSION_STRING # Linux
version_mac = VERSION_STRING # Mac OS X
version_win = VERSION_STRING # Windows
version_src = VERSION_STRING
version_short = re.sub("(?:\.0){1,2}$", "", version)

version_tuple = VERSION # only ints allowed and must be exactly 4 values

wx_minversion = (2, 8, 8)


def script2pywname(script):
	""" Convert all-lowercase script name to mixed-case pyw name """
	a2b = {name + "-3dlut-maker": name + "-3DLUT-maker",
		   name + "-vrml-to-x3d-converter": name + "-VRML-to-X3D-converter"}
	if script.lower().startswith(name.lower()):
		pyw = name + script[len(name):]
		return a2b.get(pyw, pyw)
	return script
