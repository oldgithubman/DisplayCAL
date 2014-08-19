# -*- coding: utf-8 -*-

import locale
import os
import re
import shutil
import subprocess as sp
import sys
import tempfile
from os.path import join

if sys.platform == "win32":
	import ctypes

from encoding import get_encodings

fs_enc = get_encodings()[1]

if sys.platform == "win32":
	# Add support for long paths (> 260 chars)
	import __builtin__
	import win32api

	__builtin__._open = __builtin__.open

	def open(path, *args, **kwargs):
		return __builtin__._open(make_win32_compatible_long_path(path), *args,
								 **kwargs)

	__builtin__.open = open


	os._access = os.access

	def access(path, mode):
		return os._access(make_win32_compatible_long_path(path), mode)

	os.access = access


	os.path._exists = os.path.exists

	def exists(path):
		return os.path._exists(make_win32_compatible_long_path(path))

	os.path.exists = exists


	os.path._isdir = os.path.isdir

	def isdir(path):
		return os.path._isdir(make_win32_compatible_long_path(path))

	os.path.isdir = isdir


	os.path._isfile = os.path.isfile

	def isfile(path):
		return os.path._isfile(make_win32_compatible_long_path(path))

	os.path.isfile = isfile


	os._listdir = os.listdir

	def listdir(path):
		return os._listdir(make_win32_compatible_long_path(path))

	os.listdir = listdir


	os._lstat = os.lstat

	def lstat(path):
		return os._lstat(make_win32_compatible_long_path(path))

	os.lstat = lstat


	os._mkdir = os.mkdir

	def mkdir(path, mode=0777):
		return os._mkdir(make_win32_compatible_long_path(path, 247), mode)

	os.mkdir = mkdir


	os._makedirs = os.makedirs

	def makedirs(path, mode=0777):
		return os._makedirs(make_win32_compatible_long_path(path, 247), mode)

	os.makedirs = makedirs


	os._remove = os.remove

	def remove(path):
		return os._remove(make_win32_compatible_long_path(path))

	os.remove = remove


	os._rename = os.rename

	def rename(src, dst):
		src, dst = [make_win32_compatible_long_path(path) for path in
					(src, dst)]
		return os._rename(src, dst)

	os.rename = rename


	os._stat = os.stat

	def stat(path):
		return os._stat(make_win32_compatible_long_path(path))

	os.stat = stat


	win32api._GetShortPathName = win32api.GetShortPathName

	def GetShortPathName(path):
		return win32api._GetShortPathName(make_win32_compatible_long_path(path))

	win32api.GetShortPathName = GetShortPathName


def quote_args(args):
	""" Quote commandline arguments where needed. It quotes all arguments that 
	contain spaces or any of the characters ^!$%&()[]{}=;'+,`~ """
	args_out = []
	for arg in args:
		if re.search("[\^!$%&()[\]{}=;'+,`~\s]", arg):
			arg = '"' + arg + '"'
		args_out.append(arg)
	return args_out


def expanduseru(path):
	""" Unicode version of os.path.expanduser """
	if sys.platform == "win32":
		# The code in this if-statement is copied from Python 2.7's expanduser
		# in ntpath.py, but uses getenvu() instead of os.environ[]
		if path[:1] != '~':
			return path
		i, n = 1, len(path)
		while i < n and path[i] not in '/\\':
			i = i + 1

		if 'HOME' in os.environ:
			userhome = getenvu('HOME')
		elif 'USERPROFILE' in os.environ:
			userhome = getenvu('USERPROFILE')
		elif not 'HOMEPATH' in os.environ:
			return path
		else:
			try:
				drive = getenvu('HOMEDRIVE')
			except KeyError:
				drive = ''
			userhome = join(drive, getenvu('HOMEPATH'))

		if i != 1: #~user
			userhome = join(dirname(userhome), path[1:i])

		return userhome + path[i:]
	return unicode(os.path.expanduser(path), fs_enc)


def expandvarsu(path):
	""" Unicode version of os.path.expandvars """
	if sys.platform == "win32":
		# The code in this if-statement is copied from Python 2.7's expandvars
		# in ntpath.py, but uses getenvu() instead of os.environ[]
		if '$' not in path and '%' not in path:
			return path
		import string
		varchars = string.ascii_letters + string.digits + '_-'
		res = ''
		index = 0
		pathlen = len(path)
		while index < pathlen:
			c = path[index]
			if c == '\'':   # no expansion within single quotes
				path = path[index + 1:]
				pathlen = len(path)
				try:
					index = path.index('\'')
					res = res + '\'' + path[:index + 1]
				except ValueError:
					res = res + path
					index = pathlen - 1
			elif c == '%':  # variable or '%'
				if path[index + 1:index + 2] == '%':
					res = res + c
					index = index + 1
				else:
					path = path[index+1:]
					pathlen = len(path)
					try:
						index = path.index('%')
					except ValueError:
						res = res + '%' + path
						index = pathlen - 1
					else:
						var = path[:index]
						if var in os.environ:
							res = res + getenvu(var)
						else:
							res = res + '%' + var + '%'
			elif c == '$':  # variable or '$$'
				if path[index + 1:index + 2] == '$':
					res = res + c
					index = index + 1
				elif path[index + 1:index + 2] == '{':
					path = path[index+2:]
					pathlen = len(path)
					try:
						index = path.index('}')
						var = path[:index]
						if var in os.environ:
							res = res + getenvu(var)
						else:
							res = res + '${' + var + '}'
					except ValueError:
						res = res + '${' + path
						index = pathlen - 1
				else:
					var = ''
					index = index + 1
					c = path[index:index + 1]
					while c != '' and c in varchars:
						var = var + c
						index = index + 1
						c = path[index:index + 1]
					if var in os.environ:
						res = res + getenvu(var)
					else:
						res = res + '$' + var
					if c != '':
						index = index - 1
			else:
				res = res + c
			index = index + 1
		return res
	return unicode(os.path.expandvars(path), fs_enc)


def getenvu(name, default = None):
	""" Unicode version of os.getenv """
	if sys.platform == "win32":
		name = unicode(name)
		# http://stackoverflow.com/questions/2608200/problems-with-umlauts-in-python-appdata-environvent-variable
		length = ctypes.windll.kernel32.GetEnvironmentVariableW(name, None, 0)
		if length == 0:
			return default
		buffer = ctypes.create_unicode_buffer(u'\0' * length)
		ctypes.windll.kernel32.GetEnvironmentVariableW(name, buffer, length)
		return buffer.value
	var = os.getenv(name, default)
	if isinstance(var, basestring):
		return var if isinstance(var, unicode) else unicode(var, fs_enc)


def is_superuser():
	if sys.platform == "win32":
		if sys.getwindowsversion() >= (5, 1):
			return ctypes.windll.shell32.IsUserAnAdmin()
		else:
			try:
				return ctypes.windll.advpack.IsNTAdmin(0, 0)
			except Exception:
				return False
	else:
		return os.geteuid() == 0


def launch_file(filepath):
	"""
	Open a file with its assigned default app.
	
	Return tuple(returncode, stdout, stderr) or None if functionality not available
	
	"""
	filepath = filepath.encode(fs_enc)
	retcode = None
	kwargs = dict(stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
	if sys.platform == "darwin":
		retcode = sp.call(['open', filepath], **kwargs)
	elif sys.platform == "win32":
		# for win32, we could use os.startfile, but then we'd not be able
		# to return exitcode (does it matter?)
		kwargs["startupinfo"] = sp.STARTUPINFO()
		kwargs["startupinfo"].dwFlags |= sp.STARTF_USESHOWWINDOW
		kwargs["startupinfo"].wShowWindow = sp.SW_HIDE
		kwargs["shell"] = True
		retcode = sp.call('start "" /B "%s"' % filepath, **kwargs)
	elif which('xdg-open'):
		retcode = sp.call(['xdg-open', filepath], **kwargs)
	return retcode


def listdir_re(path, rex = None):
	""" Filter directory contents through a regular expression """
	files = os.listdir(path)
	if rex:
		rex = re.compile(rex, re.IGNORECASE)
		files = filter(rex.search, files)
	return files


def make_win32_compatible_long_path(path, maxpath=259):
	if (sys.platform == "win32" and len(path) > maxpath and
		os.path.isabs(path) and not path.startswith("\\\\?\\")):
		path = "\\\\?\\" + path
	return path


def movefile(src, dst, overwrite=True):
	""" Move a file to another location.
	
	dst can be a directory in which case a file with the same basename as src
	will be created in it.
	
	Set overwrite to True to make sure existing files are overwritten.

	"""
	if os.path.isdir(dst):
		dst = os.path.join(dst, os.path.basename(src))
	if os.path.isfile(dst) and overwrite:
		os.remove(dst)
	shutil.move(src, dst)


def putenvu(name, value):
	""" Unicode version of os.putenv (also correctly updates os.environ) """
	if sys.platform == "win32" and isinstance(value, unicode):
		ctypes.windll.kernel32.SetEnvironmentVariableW(unicode(name), value)
	else:
		os.environ[name] = value.encode(fs_enc)


def relpath(path, start):
	""" Return a relative version of a path """
	path = os.path.abspath(path).split(os.path.sep)
	start = os.path.abspath(start).split(os.path.sep)
	if path == start:
		return "."
	elif path[:len(start)] == start:
		return os.path.sep.join(path[len(start):])
	elif start[:len(path)] == path:
		return os.path.sep.join([".."] * (len(start) - len(path)))


def waccess(path, mode):
	""" Test access to path """
	if mode & os.R_OK:
		try:
			test = open(path, "rb")
		except EnvironmentError:
			return False
		test.close()
	if mode & os.W_OK:
		if os.path.isdir(path):
			dir = path
		else:
			dir = os.path.dirname(path)
		try:
			if os.path.isfile(path):
				test = open(path, "ab")
			else:
				test = tempfile.TemporaryFile(prefix=".", dir=dir)
		except EnvironmentError:
			return False
		test.close()
	if mode & os.X_OK:
		return os.access(path, mode)
	return True


def which(executable, paths = None):
	""" Return the full path of executable """
	if not paths:
		paths = getenvu("PATH", os.defpath).split(os.pathsep)
	for cur_dir in paths:
		filename = os.path.join(cur_dir, executable)
		if os.path.isfile(filename):
			try:
				# make sure file is actually executable
				if os.access(filename, os.X_OK):
					return filename
			except Exception, exception:
				pass
	return None


def whereis(filename):
	try:
		p = sp.Popen(["whereis", filename], stdout=sp.PIPE)
		stdout, stderr = p.communicate()
	except:
		return
	else:
		result = stdout.split(":", 1).pop().strip()
		if result:
			return result


if sys.platform == "win32" and sys.getwindowsversion() >= (6, ):
	class win64_disable_file_system_redirection:

		# http://code.activestate.com/recipes/578035-disable-file-system-redirector/

		r"""
		Disable Windows File System Redirection.

		When a 32 bit program runs on a 64 bit Windows the paths to
		C:\Windows\System32 automatically get redirected to the 32 bit version
		(C:\Windows\SysWow64), if you really do need to access the contents of
		System32, you need to disable the file system redirection first.
		
		"""

		_disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
		_revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection

		def __enter__(self):
			self.old_value = ctypes.c_long()
			self.success = self._disable(ctypes.byref(self.old_value))

		def __exit__(self, type, value, traceback):
			if self.success:
				self._revert(self.old_value)
