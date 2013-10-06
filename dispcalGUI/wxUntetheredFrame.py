#!/usr/bin/env python2
# -*- coding: UTF-8 -*-


"""
Interactive display calibration UI

"""

import os
import re
import sys
import time

from wxaddons import wx

from config import getcfg, geticon, get_data_path, get_icon_bundle, setcfg
from log import get_file_logger
from meta import name as appname
from wxwindows import FlatShadedButton, numpad_keycodes
import CGATS
import colormath
import config
import localization as lang

BGCOLOUR = wx.Colour(0x33, 0x33, 0x33)
FGCOLOUR = wx.Colour(0x99, 0x99, 0x99)

if sys.platform == "darwin":
	FONTSIZE_LARGE = 11
	FONTSIZE_MEDIUM = 11
	FONTSIZE_SMALL = 10
else:
	FONTSIZE_LARGE = 10
	FONTSIZE_MEDIUM = 8
	FONTSIZE_SMALL = 8


class UntetheredFrame(wx.Frame):

	def __init__(self, parent=None, handler=None,
				 keyhandler=None, start_timer=True):
		wx.Frame.__init__(self, parent, wx.ID_ANY,
						  lang.getstr("measurement.untethered"),
						  style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER |
														   wx.MAXIMIZE_BOX))
		self.SetIcons(get_icon_bundle([256, 48, 32, 16], appname))
		self.sizer = wx.FlexGridSizer(2, 1)
		self.panel = wx.Panel(self)
		self.SetSizer(self.sizer)
		self.sizer.Add(self.panel, 1, wx.EXPAND)
		self.panel.SetBackgroundColour(BGCOLOUR)
		panelsizer = wx.FlexGridSizer(3, 2, 8, 8)
		self.panel.SetSizer(panelsizer)
		self.label_RGB = wx.StaticText(self.panel, wx.ID_ANY, " ")
		self.label_RGB.SetForegroundColour(FGCOLOUR)
		panelsizer.Add(self.label_RGB, 0, wx.TOP | wx.LEFT | wx.EXPAND,
					   border=8)
		self.label_XYZ = wx.StaticText(self.panel, wx.ID_ANY, " ")
		self.label_XYZ.SetForegroundColour(FGCOLOUR)
		panelsizer.Add(self.label_XYZ, 0, wx.TOP | wx.RIGHT | wx.EXPAND,
					   border=8)
		self.panel_RGB = wx.Panel(self.panel, size=(256, 256),
								  style=wx.BORDER_SIMPLE)
		panelsizer.Add(self.panel_RGB, 1, wx.LEFT | wx.EXPAND, border=8)
		self.panel_XYZ = wx.Panel(self.panel, size=(256, 256),
								  style=wx.BORDER_SIMPLE)
		panelsizer.Add(self.panel_XYZ, 1, wx.RIGHT | wx.EXPAND, border=8)
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.back_btn = FlatShadedButton(self.panel, bitmap=geticon(10, "back"),
										 label="",
										 fgcolour=FGCOLOUR)
		self.back_btn.Bind(wx.EVT_BUTTON, self.back_btn_handler)
		sizer.Add(self.back_btn, 0, wx.LEFT | wx.RIGHT, border=8)
		self.label_index = wx.StaticText(self.panel, wx.ID_ANY, " ")
		self.label_index.SetForegroundColour(FGCOLOUR)
		sizer.Add(self.label_index, 0, wx.ALIGN_CENTER_VERTICAL)
		self.next_btn = FlatShadedButton(self.panel, bitmap=geticon(10, "play"),
										 label="",
										 fgcolour=FGCOLOUR)
		self.next_btn.Bind(wx.EVT_BUTTON, self.next_btn_handler)
		sizer.Add(self.next_btn, 0, wx.LEFT, border=8)
		sizer.Add((12, 1), 1)
		self.measure_auto_cb = wx.CheckBox(self.panel, wx.ID_ANY,
										   lang.getstr("auto"))
		self.measure_auto_cb.SetForegroundColour(FGCOLOUR)
		self.measure_auto_cb.Bind(wx.EVT_CHECKBOX, self.measure_auto_ctrl_handler)
		sizer.Add(self.measure_auto_cb, 0, wx.ALIGN_CENTER_VERTICAL |
										   wx.ALIGN_RIGHT)
		panelsizer.Add(sizer, 0, wx.BOTTOM | wx.EXPAND, border=8)
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.measure_btn = FlatShadedButton(self.panel,
											bitmap=geticon(10, "play"),
											label=lang.getstr("measure"),
											fgcolour=FGCOLOUR)
		self.measure_btn.Bind(wx.EVT_BUTTON, self.measure_btn_handler)
		sizer.Add(self.measure_btn, 0, wx.RIGHT, border=6)
		# Sound when measuring
		# Needs to be stereo!
		try:
			self.measurement_sound = wx.Sound(get_data_path("beep.wav") or "")
			self.commit_sound = wx.Sound(get_data_path("camera_shutter.wav") or "")
		except NotImplementedError:
			pass
		if getcfg("measurement.play_sound"):
			bitmap = geticon(16, "sound_volume_full")
		else:
			bitmap = geticon(16, "sound_off")
		self.sound_on_off_btn = FlatShadedButton(self.panel, bitmap=bitmap,
												 fgcolour=FGCOLOUR)
		self.sound_on_off_btn.SetToolTipString(lang.getstr("measurement.play_sound"))
		self.sound_on_off_btn.Bind(wx.EVT_BUTTON,
								   self.measurement_play_sound_handler)
		sizer.Add(self.sound_on_off_btn, 0)
		sizer.Add((12, 1), 1)
		self.finish_btn = FlatShadedButton(self.panel,
										   label=lang.getstr("finish"),
										   fgcolour=FGCOLOUR)
		self.finish_btn.Bind(wx.EVT_BUTTON, self.finish_btn_handler)
		sizer.Add(self.finish_btn, 0, wx.RIGHT, border=8)
		panelsizer.Add(sizer, 0, wx.BOTTOM | wx.EXPAND, border=8)
		
		self.grid = wx.grid.Grid(self, -1, size=(536, 256))
		self.grid.CreateGrid(0, 8)
		self.grid.SetRowLabelSize(62)
		for i in xrange(8):
			if i in (3, 4):
				size = 20
			else:
				size = 62
			self.grid.SetColSize(i, size)
		for i, label in enumerate(["R", "G", "B", "", "", "L*", "a*", "b*"]):
			self.grid.SetColLabelValue(i, label)
		gridbgcolor = wx.Colour(234, 234, 234)
		self.grid.SetCellHighlightColour(gridbgcolor)
		self.grid.SetCellHighlightPenWidth(0)
		self.grid.SetCellHighlightROPenWidth(0)
		self.grid.SetDefaultCellBackgroundColour(gridbgcolor)
		self.grid.SetDefaultCellTextColour(BGCOLOUR)
		font = wx.Font(FONTSIZE_MEDIUM, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
					   wx.FONTWEIGHT_NORMAL)
		self.grid.SetDefaultCellFont(font)
		self.grid.SetDefaultRowSize(20)
		self.grid.SetLabelBackgroundColour(gridbgcolor)
		self.grid.DisableDragRowSize()
		self.grid.EnableDragColSize()
		self.grid.EnableEditing(False)
		self.grid.EnableGridLines(True)
		self.grid.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK,
					   self.grid_label_left_click_handler)
		self.sizer.Add(self.grid, 1, wx.EXPAND)
		
		self.Fit()
		
		self.keyhandler = keyhandler
		if sys.platform in ("darwin", "win32"):
			# Use an accelerator table for space, 0-9, A-Z, numpad
			keycodes = [ord(" ")] + range(ord("0"),
										  ord("9")) + range(ord("A"),
															ord("Z")) + numpad_keycodes
			self.id_to_keycode = {}
			for keycode in keycodes:
				self.id_to_keycode[wx.NewId()] = keycode
			accels = []
			for id, keycode in self.id_to_keycode.iteritems():
				self.Bind(wx.EVT_MENU, self.key_handler, id=id)
				accels += [(wx.ACCEL_NORMAL, keycode, id)]
			self.SetAcceleratorTable(wx.AcceleratorTable(accels))
		else:
			self.Bind(wx.EVT_CHAR_HOOK, self.key_handler)
		
		# Event handlers
		self.Bind(wx.EVT_CLOSE, self.OnClose, self)
		self.Bind(wx.EVT_MOVE, self.OnMove, self)
		self.timer = wx.Timer(self)
		if handler:
			self.Bind(wx.EVT_TIMER, handler, self.timer)
		self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy, self)
		
		# Final initialization steps
		self.logger = get_file_logger("untethered")
		self._setup()
		
		self.Show()
		
		if start_timer:
			self.start_timer()
	
	def EndModal(self, returncode=wx.ID_OK):
		return returncode
	
	def MakeModal(self, makemodal=False):
		pass
	
	def OnClose(self, event):
		config.writecfg()
		if not self.timer.IsRunning():
			self.Destroy()
		else:
			self.keepGoing = False
	
	def OnDestroy(self, event):
		self.stop_timer()
		del self.timer
		
	def OnMove(self, event):
		if self.IsShownOnScreen() and not self.IsIconized() and \
		   (not self.GetParent() or
		    not self.GetParent().IsShownOnScreen()):
			prev_x = getcfg("position.progress.x")
			prev_y = getcfg("position.progress.y")
			x, y = self.GetScreenPosition()
			if x != prev_x or y != prev_y:
				setcfg("position.progress.x", x)
				setcfg("position.progress.y", y)

	def Pulse(self, msg=""):
		if msg == lang.getstr("instrument.initializing"):
			self.label_RGB.SetLabel(msg)
		return self.keepGoing, False
	
	def Resume(self):
		self.keepGoing = True
	
	def Update(self, value, msg=""):
		return self.Pulse(msg)
	
	def UpdatePulse(self, msg=""):
		return self.Pulse(msg)
	
	def back_btn_handler(self, event):
		if self.index > 0:
			self.update(self.index - 1)
	
	def enable_btns(self, enable=True):
		self.back_btn.Enable(enable and self.index > 0)
		self.next_btn.Enable(enable and self.index < self.index_max)
		self.measure_btn.Enable(enable)
	
	def finish_btn_handler(self, event):
		self.finish_btn.Disable()
		self.cgats[0].type = "CTI3"
		self.cgats[0].add_keyword("COLOR_REP", "RGB_XYZ")
		if self.white_XYZ[1] > 0:
			# Normalize to Y = 100
			query = self.cgats[0].DATA
			for i in query:
				XYZ = query[i]["XYZ_X"], query[i]["XYZ_Y"], query[i]["XYZ_Z"]
				XYZ = [v / self.white_XYZ[1] * 100 for v in XYZ]
				query[i]["XYZ_X"], query[i]["XYZ_Y"], query[i]["XYZ_Z"] = XYZ
			normalized = "YES"
		else:
			normalized = "NO"
		self.cgats[0].add_keyword("NORMALIZED_TO_Y_100", normalized)
		self.cgats[0].add_keyword("DEVICE_CLASS", "DISPLAY")
		self.cgats[0].add_keyword("INSTRUMENT_TYPE_SPECTRAL", "NO")
		if hasattr(self.cgats[0], "APPROX_WHITE_POINT"):
			self.cgats[0].remove_keyword("APPROX_WHITE_POINT")
		self.cgats[0].write(os.path.splitext(self.cgats.filename)[0] + ".ti3")
		self.safe_send("Q")
		time.sleep(.5)
		self.safe_send("Q")
	
	def flush(self):
		pass
	
	def get_Lab_RGB(self):
		row = self.cgats[0].DATA[self.index]
		XYZ = row["XYZ_X"], row["XYZ_Y"], row["XYZ_Z"]
		self.last_XYZ = XYZ
		Lab = colormath.XYZ2Lab(*XYZ)
		rgb_space = list(colormath.rgb_spaces["sRGB"])
		if self.white_XYZ[1] > 0:
			XYZ = [v / self.white_XYZ[1] * 100 for v in XYZ]
			white_XYZ_Y100 = [v / self.white_XYZ[1] * 100 for v in self.white_XYZ]
			white_CCT = colormath.XYZ2CCT(*white_XYZ_Y100)
			if white_CCT:
				white_CIEDCCT_Lab = colormath.XYZ2Lab(*colormath.CIEDCCT2XYZ(white_CCT,
																			 scale=100.0))
				white_planckianCCT_Lab = colormath.XYZ2Lab(*colormath.planckianCT2XYZ(white_CCT,
																					  scale=100.0))
				white_Lab = colormath.XYZ2Lab(*white_XYZ_Y100)
				if (colormath.delta(*white_CIEDCCT_Lab + white_Lab)["E"] < 6 or
					colormath.delta(*white_planckianCCT_Lab + white_Lab)["E"] < 6):
					# Is white close enough to daylight or planckian locus?
					rgb_space[1] = tuple([v / 100.0 for v in white_XYZ_Y100])
		color = [int(round(v)) for v in
				 colormath.XYZ2RGB(*[v / 100.0 for v in XYZ],
								   rgb_space=rgb_space,
								   scale=255)]
		return Lab, color
	
	def grid_label_left_click_handler(self, event):
		if not self.is_measuring:
			row, col = event.GetRow(), event.GetCol()
			if row == -1 and col > -1: # col label clicked
				pass
			elif col == -1 and row > -1: # row label clicked
				self.update(row)
		event.Skip()
	
	def has_worker_subprocess(self):
		return bool(getattr(self, "worker", None) and
					getattr(self.worker, "subprocess", None))
	
	def isatty(self):
		return True
	
	def key_handler(self, event):
		keycode = None
		if event.GetEventType() in (wx.EVT_CHAR.typeId,
									wx.EVT_CHAR_HOOK.typeId,
									wx.EVT_KEY_DOWN.typeId):
			keycode = event.GetKeyCode()
		elif event.GetEventType() == wx.EVT_MENU.typeId:
			keycode = self.id_to_keycode.get(event.GetId())
		if keycode is not None:
			if self.has_worker_subprocess():
				if keycode == 27 or chr(keycode) == "Q":
					# ESC or Q
					self.worker.safe_send(chr(keycode))
				elif not self.is_measuring:
					# Any other key
					self.measure()
		else:
			event.Skip()
	
	def measure(self, event=None):
		self.enable_btns(False)
		self.is_measuring = True
		# Use a delay to allow for TFT lag
		wx.CallLater(200, self.safe_send, " ")
	
	def measure_auto_ctrl_handler(self, event):
		auto = self.measure_auto_cb.GetValue()
		setcfg("untethered.measure.auto", int(auto))
	
	def measure_btn_handler(self, event):
		self.last_XYZ = (-1, -1, -1)
		self.measure_count = 1
		self.measure_auto_cb.Disable()
		self.measure()
	
	def measurement_play_sound_handler(self, event):
		setcfg("measurement.play_sound",
			   int(not(bool(getcfg("measurement.play_sound")))))
		if getcfg("measurement.play_sound"):
			bitmap = geticon(16, "sound_volume_full")
		else:
			bitmap = geticon(16, "sound_off")
		self.sound_on_off_btn._bitmap = bitmap
	
	def next_btn_handler(self, event):
		if self.index < self.index_max:
			self.update(self.index + 1)

	def parse_txt(self, txt):
		if not txt or not self.keepGoing:
			return
		self.logger.info("%r" % txt)
		data_len = len(self.cgats[0].DATA)
		if (self.grid.GetNumberRows() < data_len):
			self.index_max = data_len - 1
			self.grid.AppendRows(data_len - self.grid.GetNumberRows())
			for i in self.cgats[0].DATA:
				self.grid.SetRowLabelValue(i, "%i" % (i + 1))
				row = self.cgats[0].DATA[i]
				RGB = []
				for j, label in enumerate("RGB"):
					value = int(round(float(str(row["RGB_%s" % label] * 2.55))))
					self.grid.SetCellValue(row.SAMPLE_ID - 1, j, "%i" % value)
					RGB.append(value)
				self.grid.SetCellBackgroundColour(row.SAMPLE_ID - 1, 3,
												  wx.Colour(*RGB))
		if "Connecting to the instrument" in txt:
			self.Pulse(lang.getstr("instrument.initializing"))
		if "Spot read failed" in txt:
			self.last_error = txt
		if "Result is XYZ:" in txt:
			self.last_error = None
			if (getattr(self, "measurement_sound", None) and
				getcfg("measurement.play_sound") and
				self.measurement_sound.IsOk()):
				self.measurement_sound.Play(wx.SOUND_ASYNC)
			# Result is XYZ: d.dddddd d.dddddd d.dddddd, D50 Lab: d.dddddd d.dddddd d.dddddd
			XYZ = re.search("XYZ:\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)",
							txt)
			if not XYZ:
				return
			XYZ = [float(v) for v in XYZ.groups()]
			row = self.cgats[0].DATA[self.index]
			if (row["RGB_R"] == 100 and
				row["RGB_G"] == 100 and
				row["RGB_B"] == 100):
				# White
				if XYZ[1] > 0:
					self.cgats[0].add_keyword("LUMINANCE_XYZ_CDM2",
											  "%.6f %.6f %.6f" % tuple(XYZ))
					self.white_XYZ = XYZ
			Lab1 = colormath.XYZ2Lab(*self.last_XYZ)
			Lab2 = colormath.XYZ2Lab(*XYZ)
			delta = colormath.delta(*Lab1 + Lab2)
			if delta["E"] > 1 or (abs(delta["L"]) > .3 and abs(delta["C"]) < 1):
				self.measure_count += 1
				if self.measure_count == 2:
					if (getattr(self, "commit_sound", None) and
						getcfg("measurement.play_sound") and
						self.commit_sound.IsOk()):
						self.commit_sound.Play(wx.SOUND_ASYNC)
					self.measure_count = 0
					# Reset row label
					self.grid.SetRowLabelValue(self.index, "%i" % (self.index + 1))
					# Update CGATS
					query = self.cgats[0].queryi({"RGB_R": row["RGB_R"],
												  "RGB_G": row["RGB_G"],
												  "RGB_B": row["RGB_B"]})
					for i in query:
						index = query[i].SAMPLE_ID - 1
						if index not in self.measured:
							self.measured.append(index)
						if index == self.index + 1:
							# Increment the index if we have consecutive patches
							self.index = index
						query[i]["XYZ_X"], query[i]["XYZ_Y"], query[i]["XYZ_Z"] = XYZ
					if getcfg("untethered.measure.auto"):
						self.show_RGB(False, False)
					self.show_XYZ()
					Lab, color = self.get_Lab_RGB()
					for i in query:
						row = query[i]
						self.grid.SetCellBackgroundColour(query[i].SAMPLE_ID - 1,
														  4, wx.Colour(*color))
						for j in xrange(3):
							self.grid.SetCellValue(query[i].SAMPLE_ID - 1, 5 + j, "%.2f" % Lab[j])
					self.grid.MakeCellVisible(self.index, 0)
					self.grid.ForceRefresh()
					if len(self.measured) == data_len:
						self.finished = True
						self.finish_btn.Enable()
					else:
						# Jump to the next or previous unmeasured patch, if any
						index = self.index
						for i in xrange(self.index + 1, data_len):
							if not i in self.measured:
								self.index = i
								break
						if self.index == index:
							for i in xrange(self.index - 1, -1, -1):
								if not i in self.measured:
									self.index = i
									break
						if self.index != index:
							# Mark the row containing the next/previous patch
							self.grid.SetRowLabelValue(self.index, u"\u25ba %i" % (self.index + 1))
							self.grid.MakeCellVisible(self.index, 0)
		if "key to take a reading" in txt and not self.last_error:
			self.is_measuring = False
			self.measure_auto_cb.Enable()
			if getcfg("untethered.measure.auto") and self.index > 0:
				if not self.finished:
					self.measure()
				else:
					self.enable_btns()
			else:
				show_XYZ = self.index in self.measured
				wx.CallLater(1000, self.show_RGB, not show_XYZ)
				if show_XYZ:
					wx.CallLater(1000, self.show_XYZ)
				wx.CallLater(1000, self.enable_btns)
	
	def reset(self):
		self._setup()
	
	def _setup(self):
		self.logger.info("-" * 80)
		self.is_measuring = False
		self.keepGoing = True
		self.last_error = None
		self.index = 0
		self.index_max = 0
		self.last_XYZ = (-1, -1, -1)
		self.white_XYZ = (-1, -1, -1)
		self.measure_count = 0
		self.measured = []
		self.finished = False
		self.label_RGB.SetLabel(" ")
		self.label_XYZ.SetLabel(" ")
		self.panel_RGB.SetBackgroundColour(BGCOLOUR)
		self.panel_RGB.Refresh()
		self.panel_RGB.Update()
		self.panel_XYZ.SetBackgroundColour(BGCOLOUR)
		self.panel_XYZ.Refresh()
		self.panel_XYZ.Update()
		self.label_index.SetLabel(" ")
		self.enable_btns(False)
		self.measure_auto_cb.SetValue(bool(getcfg("untethered.measure.auto")))
		self.measure_auto_cb.Disable()
		self.finish_btn.Disable()
		
		if self.grid.GetNumberRows():
			self.grid.DeleteRows(0, self.grid.GetNumberRows())
		
		# Set position
		placed = False
		if self.GetParent():
			if self.GetParent().IsShownOnScreen():
				self.Center()
				placed = True
			else:
				x = getcfg("position.progress.x", False) or self.GetParent().GetScreenPosition()[0]
				y = getcfg("position.progress.y", False) or self.GetParent().GetScreenPosition()[1]
		else:
			x = getcfg("position.progress.x")
			y = getcfg("position.progress.y")
		if not placed:
			self.SetSaneGeometry(x, y)
	
	def safe_send(self, bytes):
		if self.has_worker_subprocess() and not self.worker.subprocess_abort:
			self.worker.safe_send(bytes)
	
	def show_RGB(self, clear_XYZ=True, mark_current_row=True):
		row = self.cgats[0].DATA[self.index]
		self.label_RGB.SetLabel("RGB %i %i %i" % (round(row["RGB_R"] * 2.55),
												  round(row["RGB_G"] * 2.55),
												  round(row["RGB_B"] * 2.55)))
		color = [int(round(v * 2.55)) for v in
				 (row["RGB_R"], row["RGB_G"], row["RGB_B"])]
		self.panel_RGB.SetBackgroundColour(wx.Colour(*color))
		self.panel_RGB.Refresh()
		self.panel_RGB.Update()
		if clear_XYZ:
			self.label_XYZ.SetLabel(" ")
			self.panel_XYZ.SetBackgroundColour(BGCOLOUR)
			self.panel_XYZ.Refresh()
			self.panel_XYZ.Update()
		if mark_current_row:
			self.grid.SetRowLabelValue(self.index, u"\u25ba %i" % (self.index + 1))
		self.grid.SelectRow(self.index)
		self.grid.MakeCellVisible(self.index, 0)
		self.label_index.SetLabel("%i/%i" % (self.index + 1,
											 len(self.cgats[0].DATA)))
		self.label_index.GetContainingSizer().Layout()
	
	def show_XYZ(self):
		Lab, color = self.get_Lab_RGB()
		self.label_XYZ.SetLabel("L*a*b* %.2f %.2f %.2f" % Lab)
		self.panel_XYZ.SetBackgroundColour(wx.Colour(*color))
		self.panel_XYZ.Refresh()
		self.panel_XYZ.Update()
	
	def start_timer(self, ms=50):
		self.timer.Start(ms)
	
	def stop_timer(self):
		self.timer.Stop()
	
	def update(self, index):
		# Reset row label
		self.grid.SetRowLabelValue(self.index, "%i" % (self.index + 1))

		self.index = index
		show_XYZ = self.index in self.measured
		self.show_RGB(not show_XYZ)
		if show_XYZ:
			self.show_XYZ()
		self.enable_btns()
	
	def write(self, txt):
		wx.CallAfter(self.parse_txt, txt)


if __name__ == "__main__":
	from thread import start_new_thread
	from time import sleep
	class Subprocess():
		def send(self, bytes):
			start_new_thread(test, (bytes,))
	class Worker(object):
		def __init__(self):
			self.subprocess = Subprocess()
			self.subprocess_abort = False
		def safe_send(self, bytes):
			self.subprocess.send(bytes)
			return True
	config.initcfg()
	lang.init()
	lang.update_defaults()
	app = wx.App(0)
	frame = UntetheredFrame(start_timer=False)
	frame.cgats = CGATS.CGATS(getcfg("testchart.file"))
	frame.worker = Worker()
	frame.Show()
	i = 0
	def test(bytes=None):
		global i
		menu = r"""Place instrument on spot to be measured,
and hit [A-Z] to read white and setup FWA compensation (keyed to letter)
[a-z] to read and make FWA compensated reading from keyed reference
'r' to set reference, 's' to save spectrum,
'h' to toggle high res., 'k' to do a calibration
Hit ESC or Q to exit, any other key to take a reading:"""
		if not bytes:
			txt = menu
		elif bytes == " ":
			txt = ["""
 Result is XYZ: 95.153402 100.500147 109.625585

Place instrument on spot to be measured,
and hit [A-Z] to read white and setup FWA compensation (keyed to letter)
[a-z] to read and make FWA compensated reading from keyed reference
'r' to set reference, 's' to save spectrum,
'h' to toggle high res., 'k' to do a calibration
Hit ESC or Q to exit, any other key to take a reading:""", """
 Result is XYZ: 41.629826 21.903717 1.761510

Place instrument on spot to be measured,
and hit [A-Z] to read white and setup FWA compensation (keyed to letter)
[a-z] to read and make FWA compensated reading from keyed reference
'r' to set reference, 's' to save spectrum,
'h' to toggle high res., 'k' to do a calibration
Hit ESC or Q to exit, any other key to take a reading:""", """
 Result is XYZ: 35.336831 71.578641 11.180005

Place instrument on spot to be measured,
and hit [A-Z] to read white and setup FWA compensation (keyed to letter)
[a-z] to read and make FWA compensated reading from keyed reference
'r' to set reference, 's' to save spectrum,
'h' to toggle high res., 'k' to do a calibration
Hit ESC or Q to exit, any other key to take a reading:""", """
 Result is XYZ: 18.944662 7.614568 95.107897

Place instrument on spot to be measured,
and hit [A-Z] to read white and setup FWA compensation (keyed to letter)
[a-z] to read and make FWA compensated reading from keyed reference
'r' to set reference, 's' to save spectrum,
'h' to toggle high res., 'k' to do a calibration
Hit ESC or Q to exit, any other key to take a reading:"""][i]
			if i < 3:
				i += 1
			else:
				i -= 3
		elif bytes in ("Q", "q"):
			wx.CallAfter(frame.Close)
			return
		else:
			return
		for line in txt.split("\n"):
			sleep(.03125)
			if frame:
				wx.CallAfter(frame.write, line)
				print line
	start_new_thread(test, tuple())
	app.MainLoop()
