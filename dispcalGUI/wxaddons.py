# -*- coding: utf-8 -*-

import os
import sys
import types

from wxfixes import wx
from wx.lib.buttons import ThemedGenButton

def GetRealClientArea(self):
	""" Return the real (non-overlapping) client area of a display """
	# need to fix overlapping ClientArea on some Linux multi-display setups
	# the client area must be always smaller than the geometry
	clientarea = list(self.ClientArea)
	if self.Geometry[0] > clientarea[0]:
		clientarea[0] = self.Geometry[0]
	if self.Geometry[1] > clientarea[1]:
		clientarea[1] = self.Geometry[1]
	if self.Geometry[2] < clientarea[2]:
		clientarea[2] = self.Geometry[2]
	if self.Geometry[3] < clientarea[3]:
		clientarea[3] = self.Geometry[3]
	return wx.Rect(*clientarea)

wx.Display.GetRealClientArea = GetRealClientArea


def GetAllChildren(self, skip=None):
	""" Get children of window and its subwindows """
	if not isinstance(skip, (list, tuple)):
		skip = [skip]
	children = filter(lambda child: child not in skip, self.GetChildren())
	allchildren = []
	for child in children:
		allchildren += [child]
		if hasattr(child, "GetAllChildren") and hasattr(child.GetAllChildren,
														"__call__"):
			allchildren += child.GetAllChildren(skip)
	return allchildren

wx.Window.GetAllChildren = GetAllChildren


def GetDisplay(self):
	""" Return the display the window is shown on """
	display_no = wx.Display.GetFromWindow(self)
	if display_no < 0: # window outside visible area
		display_no = 0
	return wx.Display(display_no)

wx.Window.GetDisplay = GetDisplay


def SetMaxFontSize(self, pointsize=11):
	font = self.GetFont()
	if font.GetPointSize() > pointsize:
		font.SetPointSize(pointsize)
		self.SetFont(font)

wx.Window.SetMaxFontSize = SetMaxFontSize


def SetSaneGeometry(self, x=None, y=None, w=None, h=None):
	"""
	Set a 'sane' window position and/or size (within visible screen area).
	"""
	if not None in (x, y):
		# First, move to coordinates given
		self.SetPosition((x, y))
	# Returns the first display's client area if the window 
	# is completely outside the client area of all displays
	display_client_rect = self.GetDisplay().ClientArea 
	if sys.platform not in ("darwin", "win32"): # Linux
		safety_margin = 45
	else:
		safety_margin = 20
	if not None in (w, h):
		# Set given size, but resize if needed to fit inside client area
		self.SetSize((min(display_client_rect[2] - safety_margin, w), 
			min(display_client_rect[3] - safety_margin, h))) 
	if not None in (x, y):
		if not display_client_rect.ContainsXY(x, y) or \
		   not display_client_rect.ContainsRect((x, y, 100, 100)):
			# If outside client area or near the borders,
			# move to leftmost / topmost coordinates of client area
			self.SetPosition(display_client_rect[0:2])

wx.Window.SetSaneGeometry = SetSaneGeometry


def GridGetSelectedRowsFromSelection(self):
	"""
	Return the number of fully selected rows.
	
	Unlike GetSelectedRows, include rows that have been selected
	by chosing individual cells.
	
	"""
	sel = self.GetSelection()
	numcols = self.GetNumberCols()
	rows = []
	i = -1
	for cell in sel:
		row, col = cell
		if row > i:
			i = row
			rownumcols = 0
		rownumcols += 1
		if rownumcols == numcols:
			rows += [row]
	return rows

wx.grid.Grid.GetSelectedRowsFromSelection = GridGetSelectedRowsFromSelection


def GridGetSelectionRows(self):
	"""
	Return the selected rows, even if not all cells in a row are selected.
	"""
	sel = self.GetSelection()
	rows = []
	i = -1
	for cell in sel:
		row, col = cell
		if row > i:
			i = row
			rows += [row]
	return rows

wx.grid.Grid.GetSelectionRows = GridGetSelectionRows


def IsSizer(self):
	""" Check if the window is a sizer """
	return isinstance(self, wx.Sizer)

wx.Window.IsSizer = IsSizer


wx.BitmapButton._SetBitmapDisabled = wx.BitmapButton.SetBitmapDisabled

def SetBitmapDisabled(self, bitmap=None):
	bitmap = self.GetBitmapLabel()
	if not bitmap:
		return
	image = bitmap.ConvertToImage()
	if image.HasMask():
		image.InitAlpha()
	if image.HasAlpha():
		alphabuffer = image.GetAlphaBuffer()
		for i, byte in enumerate(alphabuffer):
			if byte > "\0":
				alphabuffer[i] = chr(int(round(ord(byte) * .3)))
		bitmap = image.ConvertToBitmap()
	self._SetBitmapDisabled(bitmap)

wx.BitmapButton.SetBitmapDisabled = SetBitmapDisabled


def get_dc_font_size(size, dc):
	""" Get correct font size for DC """
	pointsize = (1.0, 1.0)
	if isinstance(dc, wx.GCDC):
		pointsize = tuple(1.0 / scale for scale in dc.GetLogicalScale())
	if (sys.platform in ("darwin", "win32") or not isinstance(dc, wx.GCDC) or
		wx.VERSION >= (2, 9)):
		return size * (sum(pointsize) / 2.0)
	else:
		# On Linux, we need to correct the font size by a certain factor if
		# wx.GCDC is used, to make text the same size as if wx.GCDC weren't used
		screenppi = map(float, wx.ScreenDC().GetPPI())
		ppi = dc.GetPPI()
		return size * ((screenppi[0] / ppi[0] * pointsize[0] + screenppi[1] / ppi[1] * pointsize[1]) / 2.0)


def get_platform_window_decoration_size():
	if sys.platform in ("darwin", "win32"):
		# Size includes windows decoration
		if sys.platform == "win32":
			border = 8  # Windows 7
			titlebar = 30  # Windows 7
		else:
			border = 0  # Mac OS X 10.7 Lion
			titlebar = 22  # Mac OS X 10.7 Lion
	else:
		# Linux. Size does not include window decoration
		border = 0
		titlebar = 0
	return border, titlebar


class CustomEvent(wx.PyEvent):

	def __init__(self, typeId, object, window=None):
		wx.PyEvent.__init__(self, typeId, object.GetId())
		self.evtType = [typeId]
		self.typeId = typeId
		self.object = object
		self.window = window

	def GetEventObject(self):
		return self.object

	def GetEventType(self):
		return self.typeId

	def GetWindow(self):
		return self.window


class BetterWindowDisabler(object):
	
	""" Also disables child windows instead of only top level windows. This is
	actually needed under Mac OS X where disabling a top level window will
	not prevent interaction with its children. """

	def __init__(self, skip=None):
		self._windows = []
		if skip:
			if not isinstance(skip, (list, tuple)):
				skip = [skip]
		self.skip = skip
		self.id = id(self)
		self.disable()

	def __del__(self):
		self.enable()
		
	def disable(self):
		self.enable(False)
	
	def enable(self, enable=True):
		if not enable:
			skip = self.skip
			toplevel = list(wx.GetTopLevelWindows())
			for w in toplevel:
				if w not in skip and "Inspection" not in "%s" % w:
					self._windows.append(w)
					for child in w.GetAllChildren(skip + toplevel):
						if child:
							self._windows.append(child)
			def Enable(w, enable=True):
				w._enabled = enable
			def Disable(w):
				w._enabled = False
			for w in reversed(self._windows):
				if hasattr(w, "_disabler_id"):
					continue
				w._disabler_id = self.id
				enabled = w.IsEnabled()
				w.Disable()
				w._Disable = w.Disable
				w.Disable = types.MethodType(Disable, w, type(w))
				w._Enable = w.Enable
				w.Enable = types.MethodType(Enable, w, type(w))
				w.Enable(enabled)
			return
		for w in self._windows:
			if w:
				if getattr(w, "_disabler_id", None) != self.id:
					continue
				if hasattr(w, "_Disable"):
					w.Disable = w._Disable
				if hasattr(w, "_Enable"):
					w.Enable = w._Enable
				if hasattr(w, "_enabled"):
					w.Enable(w._enabled)
					if isinstance(w, ThemedGenButton):
						w.Refresh()
						w.Update()
				del w._disabler_id


class CustomGridCellEvent(CustomEvent):
	def __init__(self, typeId, object, row=-1, col=-1, window=None):
		CustomEvent.__init__(self, typeId, object, window)
		self.row = row
		self.col = col

	@property
	def Col(self):
		return self.col

	def GetRow(self):
		return self.row

	def GetCol(self):
		return self.col

	@property
	def Row(self):
		return self.row


class FileDrop(wx.FileDropTarget):

	def __init__(self, drophandlers=None):
		wx.FileDropTarget.__init__(self)
		if drophandlers is None:
			drophandlers = {}
		self.drophandlers = drophandlers
		self.unsupported_handler = None

	def OnDropFiles(self, x, y, filenames):
		self._files = {}
		self._filenames = filenames

		for filename in filenames:
			name, ext = os.path.splitext(filename)
			if ext.lower() in self.drophandlers:
				self._files[ext.lower()] = filename

		if len(self._files):
			for key in self._files:
				wx.CallAfter(self.drophandlers[key], self._files[key])
		elif self.unsupported_handler:
			wx.CallAfter(self.unsupported_handler)
