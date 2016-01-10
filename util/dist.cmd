@echo off

REM Make sure __version__.py is current
python setup.py

for /F usebackq %%a in (`python -c "import sys;print sys.version[:3]"`) do (
	set python_version=%%a
)

for /F usebackq %%a in (`python -c "from DisplayCAL import meta;print meta.version"`) do (
	set version=%%a
)

for /F usebackq %%a in (`python -c "from DisplayCAL.meta import version_tuple;print '.'.join(str(n) for n in version_tuple[:2] + (str(version_tuple[2]) + str(version_tuple[3]), ))"`) do (
	set msi_version=%%a
)

REM Source tarball
if not exist dist\DisplayCAL-%version%.tar.gz (
	python setup.py sdist 0install --stability=stable --format=gztar --use-distutils 2>&1 | tee DisplayCAL-%version%.sdist.log
)

REM Standalone executable
if not exist dist\py2exe.win32-py%python_version%\DisplayCAL-%version% (
	python setup.py bdist_standalone inno --use-distutils 2>&1 | tee DisplayCAL-%version%.bdist_standalone-py%python_version%.log
)

REM Standalone executable - Setup
if not exist dist\DisplayCAL-%version%-Setup.exe (
	"C:\Program Files (x86)\Inno Setup 5\Compil32.exe" /cc dist/DisplayCAL-Setup-py2exe.win32-py%python_version%.iss
)

REM Standalone executable - ZIP
if not exist dist\DisplayCAL-%version%-win32.zip (
	pushd dist\py2exe.win32-py%python_version%
	zip -9 -r ..\DisplayCAL-%version%-win32.zip DisplayCAL-%version%
	popd
)

if "%~1"=="bdist_msi" (
	REM Python 2.5 MSI
	if not exist dist\DisplayCAL-%msi_version%.win32-py2.5.msi (
		REM C:\Python25\python.exe setup.py bdist_msi --use-distutils 2>&1 | tee DisplayCAL-%msi_version%.msi-py2.5.log
		REM C:\Python25\python.exe setup.py finalize_msi 2>&1 | tee -a DisplayCAL-%msi_version%.msi-py2.5.log
	)

	REM Python 2.6 MSI
	if not exist dist\DisplayCAL-%msi_version%.win32-py2.6.msi (
		C:\Python26\python.exe setup.py bdist_msi --use-distutils 2>&1 | tee DisplayCAL-%msi_version%.msi-py2.6.log
		C:\Python26\python.exe setup.py finalize_msi 2>&1 | tee -a DisplayCAL-%msi_version%.msi-py2.6.log
	)
)

if "%~1"=="bdist_wininst" (
	REM Python 2.5 Installer
	if not exist dist\DisplayCAL-%version%.win32-py2.5.exe (
		REM C:\Python25\python.exe setup.py bdist_wininst --use-distutils 2>&1 | tee DisplayCAL-%version%.wininst-py2.5.log
	)

	REM Python 2.6 Installer
	if not exist dist\DisplayCAL-%version%.win32-py2.6.exe (
		C:\Python26\python.exe setup.py bdist_wininst --user-access-control=auto --use-distutils 2>&1 | tee DisplayCAL-%version%.wininst-py2.6.log
	)
)

REM Cleanup
python util\tidy_dist.py
