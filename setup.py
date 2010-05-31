#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import RawConfigParser
from distutils.util import get_platform
from subprocess import call, Popen
from time import gmtime, strftime, timezone
from xml.dom import minidom
import glob
import os
import shutil
import subprocess as sp
import sys
import time

from dispcalGUI.util_os import which
from dispcalGUI.util_str import strtr

pypath = os.path.abspath(__file__)
pydir = os.path.dirname(pypath)

def create_appdmg():
	global name, version
	retcode = call(["hdiutil", "create", os.path.join(pydir, "dist", 
													  "%s-%s.dmg" % 
													  (name, version)), 
					"-volname", name, "-fs", "HFS+", "-srcfolder", 
					os.path.join(pydir, "dist", "py2app.%s-py%s" % 
					(get_platform(), sys.version[:3]), name + "-" + version)])
	if retcode != 0:
		sys.exit(retcode)


def svnversion_bump(svnversion):
	print "Bumping version number %s ->" % \
		  ".".join(svnversion),
	svnversion = svnversion_parse(
		str(int("".join(svnversion)) + 1))
	print ".".join(svnversion)
	return svnversion


def svnversion_parse(svnversion):
	svnversion = [n for n in svnversion]
	if len(svnversion) > 4:
		svnversion = ["".join(svnversion[:len(svnversion) - 3])] + \
					 svnversion[len(svnversion) - 3:]
		# e.g. ["1", "1", "2", "5", "0"] -> ["11", "2", "5", "0"]
	elif len(svnversion) < 4:
		svnversion.insert(0, "0")
		# e.g. ["2", "8", "3"] -> ["0", "2", "8", "3"]
	return svnversion


def setup():

	if sys.platform == "darwin":
		bdist_cmd = "py2app"
	elif sys.platform == "win32":
		bdist_cmd = "py2exe"
	else:
		bdist_cmd = "bdist_bbfreeze"
	if "bdist_standalone" in sys.argv[1:]:
		i = sys.argv.index("bdist_standalone")
		sys.argv = sys.argv[:i] + sys.argv[i + 1:]
		if not bdist_cmd in sys.argv[1:i]:
			sys.argv.insert(i, bdist_cmd)
	elif "bdist_bbfreeze" in sys.argv[1:]:
		bdist_cmd = "bdist_bbfreeze"
	elif "bdist_pyi" in sys.argv[1:]:
		bdist_cmd = "pyi"
	elif "py2app" in sys.argv[1:]:
		bdist_cmd = "py2app"
	elif "py2exe" in sys.argv[1:]:
		bdist_cmd = "py2exe"

	arch = None
	bdist_appdmg = "bdist_appdmg" in sys.argv[1:]
	bdist_deb = "bdist_deb" in sys.argv[1:]
	bdist_pyi = "bdist_pyi" in sys.argv[1:]
	setup_cfg = None
	dry_run = "-n" in sys.argv[1:] or "--dry-run" in sys.argv[1:]
	inno = "inno" in sys.argv[1:]
	onefile = "-F" in sys.argv[1:] or "--onefile" in sys.argv[1:]
	purge = "purge" in sys.argv[1:]
	purge_dist = "purge_dist" in sys.argv[1:]
	suffix = "onefile" if onefile else "onedir"
	
	for i in range(len(sys.argv[1:])):
		n = len(sys.argv) - i - 1
		arg = sys.argv[n]
		arg = arg.split("=")
		if len(arg) == 2:
			if arg[0] == "--force-arch":
				arch = arg[1]
			elif arg[0] == "--cfg":
				setup_cfg = arg[1]
				sys.argv = sys.argv[:n] + sys.argv[n + 1:]
	
	lastmod_time = 0
	
	non_build_args = filter(lambda arg: arg in sys.argv[1:], 
							["bdist_appdmg", "clean", "purge", "purge_dist", 
							 "uninstall", "-h", "--help", "--help-commands", 
							 "--name", "--fullname", "--author", 
							 "--author-email", "--maintainer", 
							 "--maintainer-email", "--contact", 
							 "--contact-email", "--url", "--license", 
							 "--licence", "--description", 
							 "--long-description", "--platforms", 
							 "--classifiers", "--keywords", "--provides", 
							 "--requires", "--obsoletes", "--quiet", "-q", 
							 "--verbose", "-v"])

	if os.path.isdir(os.path.join(pydir, ".svn")) and (which("svn") or
													   which("svn.exe")) and (
		not sys.argv[1:] or len(non_build_args) < len(sys.argv[1:])):
		print "Trying to get SVN version information..."
		svnversion = None
		try:
			p = Popen(["svnversion"], stdout=sp.PIPE, cwd=pydir)
		except Exception, exception:
			print "...failed:", exception
		else:
			svnversion = p.communicate()[0]
			svnversion = strtr(svnversion.strip().split(":")[-1], 
							   ["M", "P", "S"])
			svnversion = svnversion_parse(svnversion)
			svnbase = svnversion
		
		print "Trying to get SVN information..."
		mod = False
		lastmod = ""
		entries = []
		args = ["svn", "status", "--xml"]
		while not entries:
			try:
				p = Popen(args, stdout=sp.PIPE, cwd=pydir)
			except Exception, exception:
				print "...failed:", exception
				break
			else:
				xml = p.communicate()[0]
				xml = minidom.parseString(xml)
				entries = xml.getElementsByTagName("entry")
				if not entries:
					if "info" in args:
						break
					args = ["svn", "info", "-R", "--xml"]
		timestamp = None
		for entry in iter(entries):
			pth = entry.getAttribute("path")
			mtime = 0
			if "status" in args:
				status = entry.getElementsByTagName("wc-status")
				item = status[0].getAttribute("item")
				if item.lower() in ("none", "normal"):
					item = " "
				props = status[0].getAttribute("props")
				if props.lower() in ("none", "normal"):
					props = " "
				print item.upper()[0] + props.upper()[0] + " " * 5, pth
				mod = True
				if item.upper()[0] != "D":
					mtime = os.stat(pth).st_mtime
					if mtime > lastmod_time:
						lastmod_time = mtime
						timestamp = time.gmtime(mtime)
			schedule = entry.getElementsByTagName("schedule")
			if schedule:
				schedule = schedule[0].firstChild.wholeText.strip()
				if schedule != "normal":
					print schedule.upper()[0] + " " * 6, pth
					mod = True
					mtime = os.stat(pth).st_mtime
					if mtime > lastmod_time:
						lastmod_time = mtime
						timestamp = time.gmtime(mtime)
			lmdate = entry.getElementsByTagName("date")
			if lmdate:
				lmdate = lmdate[0].firstChild.wholeText.strip()
				dateparts = lmdate.split(".")  # split off milliseconds
				mtime = time.mktime(time.strptime(dateparts[0], 
													  "%Y-%m-%dT%H:%M:%S"))
				mtime += float("." + strtr(dateparts[1], "Z"))
				if mtime > lastmod_time:
					lastmod_time = mtime
					timestamp = time.localtime(mtime)
		if timestamp:
			lastmod = strftime("%Y-%m-%dT%H:%M:%S", timestamp) + \
					  str(round(mtime - int(mtime), 6))[1:] + \
					  "Z"
			## print lmdate, lastmod, pth
		
		if not dry_run:
			print "Generating __version__.py"
			versionpy = open(os.path.join(pydir, "dispcalGUI", "__version__.py"), "w")
			versionpy.write("# generated by setup.py\n\n")
			buildtime = time.time()
			versionpy.write("BUILD_DATE = %r\n" % 
							(strftime("%Y-%m-%dT%H:%M:%S", 
									 gmtime(buildtime)) + 
							 str(round(buildtime - int(buildtime), 6))[1:] + 
							 "Z"))
			if lastmod:
				versionpy.write("LASTMOD = %r\n" % lastmod)
			if svnversion:
				if mod:
					svnversion = svnversion_bump(svnversion)
				versionpy.write("VERSION = (%s)\n" % ", ".join(svnversion))
				versionpy.write("VERSION_BASE = (%s)\n" % ", ".join(svnbase))
				versionpy.write("VERSION_STRING = %r\n" % ".".join(svnversion))
				versiontxt = open(os.path.join(pydir, "VERSION"), "w")
				versiontxt.write(".".join(svnversion))
				versiontxt.close()
			versionpy.close()
	
	if not sys.argv[1:]:
		return
	
	global name, domain, version, version_lin, version_mac, version_src
	global version_tuple, version_win
	from dispcalGUI.meta import (name, domain, version, version_lin, 
								 version_mac, version_src, version_tuple, 
								 version_win)

	if setup_cfg:
		if not os.path.exists(os.path.join(pydir, "setup.cfg.backup")):
			shutil.copy2(os.path.join(pydir, "setup.cfg"), 
						 os.path.join(pydir, "setup.cfg.backup"))
		shutil.copy2(os.path.join(pydir, "misc", "setup.%s.cfg" % setup_cfg), 
					 os.path.join(pydir, "setup.cfg"))

	if purge or purge_dist:

		# remove the "build", "dispcalGUI.egg-info" and 
		# "pyinstaller/bincache*" directories and their contents recursively

		if dry_run:
			print "dry run - nothing will be removed"

		paths = []
		if purge:
			paths += glob.glob(os.path.join(pydir, "build")) + glob.glob(
						os.path.join(pydir, name + ".egg-info")) + glob.glob(
						os.path.join(pydir, "pyinstaller", "bincache*"))
			sys.argv.remove("purge")
		if purge_dist:
			paths += glob.glob(os.path.join(pydir, "dist"))
			sys.argv.remove("purge_dist")
		for path in paths:
			if os.path.exists(path):
				if dry_run:
					print path
					continue
				try:
					shutil.rmtree(path)
				except Exception, exception:
					print exception
				else:
					print "removed", path
		if len(sys.argv) == 1 or len(sys.argv) == 2 and dry_run:
			return

	if "readme" in sys.argv[1:]:
		readme_template_path = os.path.join(pydir, "misc", 
											"README.template.html")
		readme_template = open(readme_template_path, "rb")
		readme_template_html = readme_template.read()
		readme_template.close()
		for key, val in [
			("DATE", 
				strftime("%Y-%m-%d", 
						 gmtime(lastmod_time or 
								os.stat(readme_template_path).st_mtime))),
			("TIME", 
				strftime("%H:%M", 
						 gmtime(lastmod_time or 
								os.stat(readme_template_path).st_mtime))),
			("TIMESTAMP", 
				strftime("%Y-%m-%dT%H:%M:%S", 
						 gmtime(lastmod_time or 
								os.stat(readme_template_path).st_mtime)) +
						 ("+" if timezone < 0 else "-") +
						 strftime("%H:%M", gmtime(abs(timezone)))),
			("VERSION", version),
			("VERSION_LIN", version_lin),
			("VERSION_MAC", version_mac),
			("VERSION_WIN", version_win),
			("VERSION_SRC", version_src)
		]:
			readme_template_html = readme_template_html.replace("${%s}" % key, 
																val)
		readme = open(os.path.join(pydir, "README.html"), "rb")
		readme_html = readme.read()
		readme.close()
		if readme_html != readme_template_html:
			readme = open(os.path.join(pydir, "README.html"), "wb")
			readme.write(readme_template_html)
			readme.close()
		sys.argv.remove("readme")
		if len(sys.argv) == 1 or len(sys.argv) == 2 and dry_run:
			return

	if bdist_appdmg:
		i = sys.argv.index("bdist_appdmg")
		sys.argv = sys.argv[:i] + sys.argv[i + 1:]
		if len(sys.argv) == 1 or len(sys.argv) == 2 and dry_run:
			create_appdmg()
			return

	if bdist_deb:
		bdist_args = ["bdist_rpm"]
		if not arch:
			arch = get_platform().split("-")[1]
			bdist_args += ["--force-arch=" + arch]
		i = sys.argv.index("bdist_deb")
		sys.argv = sys.argv[:i] + bdist_args + sys.argv[i + 1:]

	if bdist_pyi:
		i = sys.argv.index("bdist_pyi")
		sys.argv = sys.argv[:i] + sys.argv[i + 1:]
		if not "build_ext" in sys.argv[1:i]:
			sys.argv.insert(i, "build_ext")
		if len(sys.argv) < i + 2 or sys.argv[i + 1] not in ("--inplace", "-i"):
			sys.argv.insert(i + 1, "-i")
		if "-F" in sys.argv[1:]:
			sys.argv.remove("-F")
		if "--onefile" in sys.argv[1:]:
			sys.argv.remove("--onefile")

	if inno and sys.platform == "win32":
		inno_template_path = os.path.join(pydir, "misc", "%s-Setup-%s.iss" % 
										  (name, ("pyi-" + 
												  suffix if bdist_pyi else 
												  bdist_cmd)))
		inno_template = open(inno_template_path, "r")
		inno_script = inno_template.read().decode("MBCS", "replace") % {
			"AppVerName": version,
			"AppPublisherURL": "http://" + domain,
			"AppSupportURL": "http://" + domain,
			"AppUpdatesURL": "http://" + domain,
			"VersionInfoVersion": ".".join(map(str, version_tuple)),
			"VersionInfoTextVersion": version,
			"AppVersion": version,
			"Platform": get_platform(),
			"PythonVersion": sys.version[:3],
			}
		inno_template.close()
		inno_path = os.path.join("dist", 
								 os.path.basename(inno_template_path).replace(
									bdist_cmd, "%s.%s-py%s" % 
									(bdist_cmd, get_platform(), 
									 sys.version[:3])))
		if not os.path.exists("dist"):
			os.makedirs("dist")
		inno_file = open(inno_path, "w")
		inno_file.write(inno_script.encode("MBCS", "replace"))
		inno_file.close()
		sys.argv.remove("inno")
		if len(sys.argv) == 1 or len(sys.argv) == 2 and dry_run:
			return

	from dispcalGUI.setup import setup
	setup()
	
	if bdist_appdmg:
		create_appdmg()

	if bdist_deb:
		# Read setup.cfg
		cfg = RawConfigParser()
		cfg.read(os.path.join(pydir, "setup.cfg"))
		# Get dependencies
		dependencies = [val.strip().split(None, 1) for val in 
						cfg.get("bdist_rpm", "Requires").split(",")]
		# Get maintainer
		if cfg.has_option("bdist_rpm", "maintainer"):
			maintainer = cfg.get("bdist_rpm", "maintainer")
		else:
			maintainer = None
		# Get packager
		if cfg.has_option("bdist_rpm", "packager"):
			packager = cfg.get("bdist_rpm", "packager")
		else:
			packager = None
		# Convert dependency format:
		# 'package >= version' to 'package (>= version)'
		for i in range(len(dependencies)):
			if len(dependencies[i]) > 1:
				dependencies[i][1] = "(%s)" % dependencies[i][1]
			dependencies[i] = " ".join(dependencies[i])
		release = 1 # TODO: parse setup.cfg
		rpm_filename = os.path.join(pydir, "dist", "%s-%s-%s.%s.rpm" % 
									(name, version, release, arch))
		# remove target directory (and contents) if it already exists
		target_dir = os.path.join(pydir, "dist", "%s-%s" % (name, version))
		if os.path.exists(target_dir):
			shutil.rmtree(target_dir)
		if os.path.exists(target_dir + ".orig"):
			shutil.rmtree(target_dir + ".orig")
		# use alien to create deb dir from rpm package
		retcode = call(["alien", "-c", "-g", "-k", 
						os.path.basename(rpm_filename)], 
						cwd=os.path.join(pydir, "dist"))
		if retcode != 0:
			sys.exit(retcode)
		# control filename
		control_filename = os.path.join(pydir, "dist", "%s-%s" % (name, 
																  version), 
										"debian", "control")
		# read control file from deb dir
		control = open(control_filename, "r")
		lines = [line.rstrip("\n") for line in control.readlines()]
		control.close()
		# update control with info from setup.cfg
		for i in range(len(lines)):
			if lines[i].startswith("Depends:"):
				# add dependencies
				lines[i] += ", " + ", ".join(dependencies)
			elif lines[i].startswith("Maintainer:") and (maintainer or 
														 packager):
				# set maintainer
				lines[i] = "Maintainer: " + (maintainer or packager)
		# write updated control file
		control = open(control_filename, "w")
		control.write("\n".join(lines))
		control.close()
		# create deb package
		retcode = call(["./debian/rules", "binary"], cwd=target_dir)
		if retcode != 0:
			sys.exit(retcode)

	if setup_cfg:
		shutil.copy2(os.path.join(pydir, "setup.cfg.backup"), 
					 os.path.join(pydir, "setup.cfg"))

	if bdist_pyi:

		# create an executable using pyinstaller

		if sys.platform != "win32": # Linux/Mac OS X
			retcode = call([sys.executable, "Make.py"], 
				cwd = os.path.join(pydir, "pyinstaller", "source", "linux"))
			if retcode != 0:
				sys.exit(retcode)
			retcode = call(["make"], cwd = os.path.join(pydir, "pyinstaller", 
														"source", "linux"))
			if retcode != 0:
				sys.exit(retcode)
		retcode = call([sys.executable, "-O", os.path.join(pydir, 
														   "pyinstaller", 
														   "Configure.py")])
		retcode = call([sys.executable, "-O", os.path.join(pydir, 
														   "pyinstaller", 
														   "Build.py"), 
						"-o", os.path.join(pydir, "build", "pyi.%s-%s-%s" % 
										   (get_platform(), sys.version[:3], 
										   suffix), name + "-" + version), 
						os.path.join(pydir, "misc", "%s-pyi-%s.spec" % 
									 (name, suffix))])
		if retcode != 0:
			sys.exit(retcode)


if __name__ == "__main__":
	setup()
