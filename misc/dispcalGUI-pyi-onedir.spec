from distutils.util import get_platform

sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dispcalGUI.meta import name, version

if sys.platform in ("cygwin", "win32"):
	sys.path.insert(1, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "util"))
	from winmanifest import mktempmanifest
	from winversion import mktempver
	manifestpath = mktempmanifest(os.path.join("misc", name + 
		(".exe.VC90.manifest" if hasattr(sys, "version_info") and 
		sys.version_info[:2] >= (2,6) else ".exe.manifest")))
	versionpath = mktempver(os.path.join("misc", "winversion.txt"))
	additional_opts = {
		"icon": os.path.join(name, "theme", "icons", name + ".ico"),
		"manifest": manifestpath,
		"version": versionpath,
	}
else:
	additional_opts = {}

a = Analysis([os.path.join(HOMEPATH, "support", "_mountzlib.py"), 
	os.path.join(HOMEPATH, "support", "useUnicode.py"), os.path.join(name, 
	name + ".py")], pathex=[os.path.join(name)])
pyz = PYZ(a.pure,
	level=5) # zlib compression level 0-9
exe = EXE(pyz,
	a.scripts + [("O", "", "OPTION")],
	exclude_binaries=1,
	name=os.path.join("..", "build", "pyi.%s-%s-onedir" % (get_platform(), sys.version[:3]), name + 
		"-" + version, name + (".exe" if sys.platform in ("cygwin", "win32") 
		else "")),
	debug=False,
	strip=sys.platform not in ("cygwin", "win32"),
	upx=False,
	console=True,
	append_pkg=False,
	**additional_opts)
coll = COLLECT(exe,
	a.binaries + Tree(os.path.join(name, "lang"), "lang", [".svn"])
	+ Tree(os.path.join(name, "presets"), "presets", [".svn"])
	+ Tree(os.path.join(name, "theme"), "theme", [name + ".icns", name + 
		".ico", ".svn", "Thumbs.db"] + (["22x22", "24x24", "48x48", "256x256", 
		name + "-uninstall.png"] if sys.platform in ("cygwin", "win32") else 
		[name + "-uninstall.ico"]))
	+ Tree(os.path.join(name, "ti1"), "ti1", [".svn"])
	+ [("test.cal", os.path.join(name, "test.cal"), "DATA")]
	+ Tree("screenshots", "screenshots", [".svn", "Thumbs.db"])
	+ Tree("theme", "theme", [".svn", "Thumbs.db"])
	+ [("LICENSE.txt", "LICENSE.txt", "DATA")]
	+ [("README.html", "README.html", "DATA")],
	strip=sys.platform not in("cygwin", "win32"),
	upx=False,
	name=os.path.join("..", "dist", "pyi.%s-py%s-onedir" % (get_platform(), sys.version[:3]), name + 
		"-" + version))

if sys.platform in ("cygwin", "win32"):
	os.remove(manifestpath)
	os.rmdir(os.path.dirname(manifestpath))
	os.remove(versionpath)
	os.rmdir(os.path.dirname(versionpath))