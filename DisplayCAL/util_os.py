# -*- coding: utf-8 -*-

from __future__ import absolute_import
from .encoding import get_encodings
from builtins import filter, object, range, str
from collections.abc import Callable, Sequence
import ctypes
import errno
import fnmatch
import glob
from io import BufferedRandom, BufferedReader, BufferedWriter, FileIO, TextIOWrapper
import os
import re
import shutil
import string
import struct
import subprocess as sp
import sys
import tempfile
import time
from typing import Any, BinaryIO, IO, Dict, List, LiteralString, Union

if sys.platform not in ("darwin", "win32"):
    # Linux
    import grp
    import pwd

if sys.platform != "win32":
    import fcntl

if sys.platform == "win32":
    import builtins
    import pywintypes
    import win32api
    import win32con
    from win32file import (
        FILE_FLAG_BACKUP_SEMANTICS,
        FILE_FLAG_OPEN_REPARSE_POINT,
        GENERIC_READ,
        OPEN_EXISTING,
        CloseHandle,
        CreateFileW,
        GetFileAttributes,
    )
    import win32file
    import win32net
    import winerror
    from winioctlcon import FSCTL_GET_REPARSE_POINT

# Remove the reloaded variable and its checks
# reloaded = 0
# try:
#     reloaded  # Check if reloaded is defined
# except NameError:
#     # First import. All fine
#     reloaded = 0
# else:
#     # Module is being reloaded. NOT recommended.
#     reloaded += 1
#     import warnings
#     warnings.warn("Module %s is being reloaded. This is NOT recommended." % __name__, RuntimeWarning)
#     warnings.warn("Implicitly reloading builtins", RuntimeWarning)
#     if sys.platform == "win32":
#         from importlib import reload
#         reload(builtins)
#     warnings.warn("Implicitly reloading os", RuntimeWarning)
#     reload(os)
#     warnings.warn("Implicitly reloading os.path", RuntimeWarning)
#     reload(os.path)
#     if sys.platform == "win32":
#         warnings.warn("Implicitly reloading win32api", RuntimeWarning)
#         reload(win32api)

# Cache used for safe_shell_filter() function
_cache: dict[str, re.Pattern[str]] = {}
_MAXCACHE = 100

FILE_ATTRIBUTE_REPARSE_POINT = 1024
IO_REPARSE_TAG_MOUNT_POINT = 0xA0000003  # Junction
IO_REPARSE_TAG_SYMLINK = 0xA000000C

fs_enc: str = get_encodings()[1] or sys.getfilesystemencoding() or 'utf-8'

_listdir: Callable[..., list[str] | list[bytes]] = os.listdir

if sys.platform == "win32":
    # Add support for long paths (> 260 chars)
    # and retry ERROR_SHARING_VIOLATION

    _open: Callable[
        ...,
        TextIOWrapper[Any] | FileIO | BufferedRandom | BufferedWriter | BufferedReader | BinaryIO | IO[Any],
        ] = builtins.open


    def retry_sharing_violation_factory(fn: Callable[..., Any], delay: float = 0.25, maxretries: int = 20) -> Callable[
        [Callable[..., Any], float, int],
        Callable[..., Any],
        ]:
        
        def retry_sharing_violation(*args: ..., **kwargs: ...) -> Callable[..., Any]:
            retries = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except WindowsError as exception:
                    if exception.winerror == winerror.ERROR_SHARING_VIOLATION:
                        if retries < maxretries:
                            retries += 1
                            time.sleep(delay)
                            continue
                    raise

        return retry_sharing_violation


    def open(
        path: str | bytes,
        *args: ...,
        **kwargs: ...,
        ) -> TextIOWrapper[Any] | FileIO | BufferedRandom | BufferedWriter | BufferedReader | BinaryIO | IO[Any]:
        """ Wrapper around __builtin__.open dealing with win32 long paths """
        return _open(make_win32_compatible_long_path(path), *args,
                                 **kwargs)

    builtins.open = open


    _access: Callable[[str | bytes, int], bool] = os.access

    def access(path: str | bytes, mode: int) -> bool:
        return _access(make_win32_compatible_long_path(path), mode)

    os.access = access


    _exists: Callable[[str | bytes], bool] = os.path.exists

    def exists(path: str | bytes) -> bool:
        return _exists(make_win32_compatible_long_path(path))

    os.path.exists = exists


    _isdir: Callable[[str | bytes], bool] = os.path.isdir

    def isdir(path: str | bytes) -> bool:
        return _isdir(make_win32_compatible_long_path(path))

    os.path.isdir = isdir


    _isfile: Callable[[str | bytes], bool] = os.path.isfile

    def isfile(path: str | bytes) -> bool:
        return _isfile(make_win32_compatible_long_path(path))

    os.path.isfile = isfile


    def listdir(path: str | bytes) -> list[str] | list[bytes]:
        return _listdir(make_win32_compatible_long_path(path))


    _lstat: Callable[[str | bytes], os.stat_result] = os.lstat

    def lstat(path: str | bytes) -> os.stat_result:
        return _lstat(make_win32_compatible_long_path(path))

    os.lstat = lstat


    _mkdir: Callable[[str | bytes, int], None] = os.mkdir

    def mkdir(path: str | bytes, mode: int = 0o777) -> None:
        return _mkdir(make_win32_compatible_long_path(path, 247), mode)

    os.mkdir = mkdir


    _makedirs: Callable[[str | bytes, int], None] = os.makedirs

    def makedirs(path: str | bytes, mode: int = 0o777) -> None:
        return _makedirs(make_win32_compatible_long_path(path, 247), mode)

    os.makedirs = makedirs


    _remove: Callable[[str | bytes], None] = os.remove

    def remove(path: str | bytes) -> None:
        return _remove(make_win32_compatible_long_path(path))

    os.remove = retry_sharing_violation_factory(remove)


    _rename: Callable[[str | bytes, str | bytes], None] = os.rename

    def rename(src: str | bytes, dst: str | bytes) -> None:
        src, dst = [make_win32_compatible_long_path(path) for path in (src, dst)]
        return _rename(src, dst)

    os.rename = retry_sharing_violation_factory(rename)


    _stat: Callable[[str | bytes], os.stat_result] = os.stat

    def stat(path: str | bytes) -> os.stat_result:
        return _stat(make_win32_compatible_long_path(path))

    os.stat = stat


    _unlink: Callable[[str | bytes], None] = os.unlink

    def unlink(path: str | bytes) -> None:
        return _unlink(make_win32_compatible_long_path(path))

    os.unlink = retry_sharing_violation_factory(unlink)


    _GetShortPathName: Callable[[str], str] = win32api.GetShortPathName

    def GetShortPathName(path: str | bytes) -> str:
        if isinstance(path, bytes):
            path = path.decode(fs_enc)
        long_path: str = make_win32_compatible_long_path(path)
        short_path: str = _GetShortPathName(long_path)
        return short_path

    win32api.GetShortPathName = GetShortPathName
else:
    def listdir(path: str | bytes) -> list[str] | list[bytes]:
        paths = _listdir(path)
        if isinstance(path, str):
            # Undecodable filenames will still be string objects. Ignore them.
            paths = [path for path in paths if isinstance(path, str)]
        return paths

os.listdir = listdir


def quote_args(args: list[str]) -> list[str]:
    """ Quote commandline arguments where needed. It quotes all arguments that 
    contain spaces or any of the characters ^!$%&()[]{}=;'+,`~ """
    args_out: list[str] = []
    for arg in args:
        if re.search(r'[\^!$%&\(\)\[\]{}=;\'`,~\s]', arg):
            arg: str = '"' + arg + '"'
        args_out.append(arg)
    return args_out


def dlopen(name: str | None, handle: int | None = None) -> ctypes.CDLL | None:
    try:
        return ctypes.CDLL(name, handle=handle)
    except:
        pass


def find_library(pattern: bytes, arch: Union[LiteralString, bytes, str, None] = None) -> Union[LiteralString, bytes, str, None]:
    """
    Use ldconfig cache to find installed library.
    
    Can use fnmatch-style pattern matching.
    
    """
    try:
        p = sp.Popen(["/sbin/ldconfig", "-p"], stdout=sp.PIPE)
        stdout: Union[None, str, bytes, LiteralString] = p.communicate()[0]
    except:
        return None
    if not arch:
        try:
            p = sp.Popen(["file", "-L", sys.executable], stdout=sp.PIPE)
            file_stdout: bytes = p.communicate()[0]
        except:
            pass
        else:
            # /usr/bin/python2.7: ELF 64-bit LSB shared object, x86-64,
            # version 1 (SYSV), dynamically linked, interpreter
            # /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0,
            # BuildID[sha1]=41a1f0d4da3afee8f22d1947cc13a9f33f59f2b8, stripped
            parts: List[bytes] = file_stdout.split(b",")
            if len(parts) > 1:
                arch = parts[1].strip()
    for line in stdout.splitlines():
        # libxyz.so (libc6,x86_64) => /lib64/libxyz.so.1
        parts = line.split(b" => ", 1)
        if len(parts) < 2:
            continue
        candidate: List[bytes] = parts[0].split(None, 1)
        if len(candidate) < 2:
            continue
        info: Sequence[Union[LiteralString, bytes, str]] = candidate[1].strip(b"( )").split(b",")
        if arch and len(info) > 1 and info[1].strip() != arch:
            # Skip libs for wrong arch
            continue
        filename: Union[LiteralString, bytes, str] = candidate[0]
        if fnmatch.fnmatch(filename, pattern):
            path: Union[LiteralString, bytes, str] = parts[1].strip()
            return path


def expanduseru(path: str) -> str:
    """ Unicode version of os.path.expanduser """
    if sys.platform == "win32":
        # The code in this if-statement is copied from Python 2.7's expanduser
        # in ntpath.py, but uses getenvu() instead of os.environ[]
        if path[:1] != '~':
            return path
        i = 1
        n: int = len(path)
        while i < n and path[i] not in '/\\':
            i: int = i + 1

        userhome: str | None = None

        if 'HOME' in os.environ:
            userhome = getenvu('HOME')
        elif 'USERPROFILE' in os.environ:
            userhome = getenvu('USERPROFILE')
        elif 'HOMEPATH' in os.environ:
            drive: str | None = getenvu('HOMEDRIVE', '')
            userhome = os.path.join(drive or '', getenvu('HOMEPATH') or '')
        else:
            return path

        if userhome is None:
            return path

        if i != 1:  # ~user
            userhome = os.path.join(os.path.dirname(userhome), path[1:i])

        return userhome + path[i:]
    return os.path.expanduser(path).encode(fs_enc).decode(fs_enc)


def expandvarsu(path: str) -> str:
    """ Unicode version of os.path.expandvars """
    if sys.platform == "win32":
        # The code in this if-statement is copied from Python 2.7's expandvars
        # in ntpath.py, but uses getenvu() instead of os.environ[]
        if '$' not in path and '%' not in path:
            return path
        varchars: LiteralString = string.ascii_letters + string.digits + '_-'
        res: str = ''
        index = 0
        pathlen: int = len(path)
        while index < pathlen:
            c: str = path[index]
            if c == '\'':   # no expansion within single quotes
                path = path[index + 1:]
                pathlen = len(path)
                try:
                    index: int = path.index('\'')
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
                        var: str = path[:index]
                        env_value: Union[str, None] = getenvu(var)
                        res = res + (env_value if env_value is not None else '%' + var + '%')
                    except ValueError:
                        res = res + '%' + path
                        index = pathlen - 1
            elif c == '$':  # variable or '$$'
                if path[index + 1:index + 2] == '$':
                    res = res + c
                    index = index + 1
                elif path[index + 1:index + 2] == '{':
                    path = path[index+2:]
                    pathlen = len(path)
                    try:
                        index = path.index('}')
                        var: str = path[:index]
                        env_value: Union[str, None] = getenvu(var)
                        res = res + (env_value if env_value is not None else '${' + var + '}')
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
                    env_value: Union[str, None] = getenvu(var)
                    res = res + (env_value if env_value is not None else '$' + var)
                    if c != '':
                        index = index - 1
            else:
                res = res + c
            index: int = index + 1
        return res
    return os.path.expandvars(path)


def fname_ext(path: str) -> tuple[str, str]:
    """ Get filename and extension """
    return os.path.splitext(os.path.basename(path))


def get_program_file(name: str, foldername: str) -> str | None:
    """ Get path to program file """
    if sys.platform == "win32":
        path_env: str | None = getenvu("PATH", os.defpath)
        if path_env is None:
            path_env = os.defpath  # Fallback to os.defpath if getenvu returns None
        paths: List[str] = path_env.split(os.pathsep)
        program_files: str | None = getenvu("PROGRAMFILES", "")
        program_w6432: str | None = getenvu("PROGRAMW6432", "")
        if program_files:
            paths += safe_glob(os.path.join(program_files, foldername))
        if program_w6432:
            paths += safe_glob(os.path.join(program_w6432, foldername))
        exe_ext = ".exe"
    else:
        paths = os.defpath.split(os.pathsep)  # Initialize paths with os.defpath for non-Windows platforms
        exe_ext = ""
    return which(name + exe_ext, paths=paths)


def getenvu(name: str, default: Union[str, None] = None) -> Union[str, None]:
    """ Unicode version of os.getenv """
    if sys.platform == "win32":
        name = str(name)
        # http://stackoverflow.com/questions/2608200/problems-with-umlauts-in-python-appdata-environvent-variable
        length: int = ctypes.windll.kernel32.GetEnvironmentVariableW(name, None, 0)
        if length == 0:
            return default
        buffer: ctypes.Array[ctypes.c_wchar] = ctypes.create_unicode_buffer(u'\0' * length)
        ctypes.windll.kernel32.GetEnvironmentVariableW(name, buffer, length)
        return buffer.value
    var = os.getenv(name, default)
    if isinstance(var, str):
        return var
    return None


def getgroups(username: Union[str, None] = None, names_only: bool = False) -> List[str]:
    """
    Return a list of groups that user is member of, or groups of current
    process if username not given
    """
    if os.name == 'posix':  # Check if the OS is Unix-like
        if username is None:
            groups: List[str] = [grp.getgrgid(g).gr_name for g in os.getgroups()]
        else:
            groups = [g for g in grp.getgrall() if username in g.gr_mem]
            gid = pwd.getpwnam(username).pw_gid
            groups.append(grp.getgrgid(gid))
    else:  # Handle Windows
        if username is None:
            groups: List[str] = []
        else:
            groups = []
            try:
                user_info: Dict[str, Any] = win32net.NetUserGetInfo(None, username, 1)  # Explicit type hint
                groups = user_info['groups']
            except Exception as e:
                print(f"Error getting groups for user {username}: {e}")
    
    if names_only:
        groups = [g.gr_name if isinstance(g, grp.struct_group) else g for g in groups]
    return groups


def islink(path):
    """
    Cross-platform islink implementation.
    
    Supports Windows NT symbolic links and reparse points.
    
    """
    if sys.platform != "win32" or sys.getwindowsversion()[0] < 6:
        return os.path.islink(path)
    return bool(os.path.exists(path) and GetFileAttributes(path) &
                FILE_ATTRIBUTE_REPARSE_POINT == FILE_ATTRIBUTE_REPARSE_POINT)


def is_superuser():
    if sys.platform == "win32":
        if sys.getwindowsversion() >= (5, 1):
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        else:
            try:
                return bool(ctypes.windll.advpack.IsNTAdmin(0, 0))
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
        kwargs = {}
        kwargs["startupinfo"] = sp.STARTUPINFO()
        kwargs["startupinfo"].dwFlags |= sp.STARTF_USESHOWWINDOW
        kwargs["startupinfo"].wShowWindow = sp.SW_HIDE
        kwargs["shell"] = True
        kwargs["close_fds"] = True
        retcode = sp.call('start "" "%s"' % filepath, **kwargs)
    elif which('xdg-open'):
        retcode = sp.call(['xdg-open', filepath], **kwargs)
    return retcode


def listdir_re(path, rex = None):
    """ Filter directory contents through a regular expression """
    files = os.listdir(path)
    if rex:
        rex = re.compile(rex, re.IGNORECASE)
        files = list(filter(rex.search, files))
    return files


def make_win32_compatible_long_path(path: str | bytes, maxpath: int = 259) -> str:
    if sys.platform == "win32" and len(path) > maxpath and os.path.isabs(path):
        if isinstance(path, str):
            if not path.startswith(r"\\?\\"):
                path = r"\\?\\" + path
        elif isinstance(path, bytes):
            if not path.startswith(b"\\\\?\\"):
                path = b"\\\\?\\" + path

            try:
                path = path.decode(fs_enc)  # Convert bytes to str
            except UnicodeDecodeError:
                raise ValueError(f"Failed to decode path with encoding {fs_enc}")
                
    return str(path)


def mkstemp_bypath(path, dir=None, text=False):
    """
    Wrapper around mkstemp that uses filename and extension from path as prefix 
    and suffix for the temporary file, and the directory component as temporary
    file directory if 'dir' is not given.
    
    """
    fname, ext = fname_ext(path)
    if not dir:
        dir = os.path.dirname(path)
    return tempfile.mkstemp(ext, fname + "-", dir, text)


def mksfile(filename):
    """
    Create a file safely and return (fd, abspath)
    
    If filename already exists, add '(n)' as suffix before extension (will
    try up to os.TMP_MAX or 10000 for n)
    
    Basically, this works in a similar way as _mkstemp_inner from the
    standard library 'tempfile' module.
    
    """

    flags = tempfile._bin_openflags

    fname, ext = os.path.splitext(filename)

    for seq in range(tempfile.TMP_MAX):
        if not seq:
            pth = filename
        else:
            pth = "%s(%i)%s" % (fname, seq, ext)
        try:
            fd = os.open(pth, flags, 0o600)
            tempfile._set_cloexec(fd)
            return (fd, os.path.abspath(pth))
        except OSError as e:
            if e.errno == errno.EEXIST:
                continue  # Try again
            raise

    raise IOError(errno.EEXIST, "No usable temporary file name found")


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
    if sys.platform == "win32" and isinstance(value, str):
        ctypes.windll.kernel32.SetEnvironmentVariableW(str(name), value)
    else:
        os.environ[name] = value.encode(fs_enc)


def parse_reparse_buffer(buf):
    """ Implementing the below in Python:

    typedef struct _REPARSE_DATA_BUFFER {
        ULONG  ReparseTag;
        USHORT ReparseDataLength;
        USHORT Reserved;
        union {
            struct {
                USHORT SubstituteNameOffset;
                USHORT SubstituteNameLength;
                USHORT PrintNameOffset;
                USHORT PrintNameLength;
                ULONG Flags;
                WCHAR PathBuffer[1];
            } SymbolicLinkReparseBuffer;
            struct {
                USHORT SubstituteNameOffset;
                USHORT SubstituteNameLength;
                USHORT PrintNameOffset;
                USHORT PrintNameLength;
                WCHAR PathBuffer[1];
            } MountPointReparseBuffer;
            struct {
                UCHAR  DataBuffer[1];
            } GenericReparseBuffer;
        } DUMMYUNIONNAME;
    } REPARSE_DATA_BUFFER, *PREPARSE_DATA_BUFFER;

    """
    # See https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/ntifs/ns-ntifs-_reparse_data_buffer

    data = {'tag': struct.unpack('<I', buf[:4])[0],
            'data_length': struct.unpack('<H', buf[4:6])[0],
            'reserved': struct.unpack('<H', buf[6:8])[0]}
    buf = buf[8:]

    if data['tag'] in (IO_REPARSE_TAG_MOUNT_POINT, IO_REPARSE_TAG_SYMLINK):
        keys = ['substitute_name_offset',
                'substitute_name_length',
                'print_name_offset',
                'print_name_length']
        if data['tag'] == IO_REPARSE_TAG_SYMLINK:
            keys.append('flags')

        # Parsing
        for k in keys:
            if k == 'flags':
                fmt, sz = '<I', 4
            else:
                fmt, sz = '<H', 2
            data[k] = struct.unpack(fmt, buf[:sz])[0]
            buf = buf[sz:]

    # Using the offset and lengths grabbed, we'll set the buffer.
    data['buffer'] = buf

    return data


def readlink(path):
    """
    Cross-platform implenentation of readlink.
    
    Supports Windows NT symbolic links and reparse points.
    
    """
    if sys.platform != "win32":
        return os.readlink(path)

    # This wouldn't return true if the file didn't exist
    if not islink(path):
        # Mimic POSIX error
        raise OSError(22, 'Invalid argument', path)

    # Open the file correctly depending on the string type.
    if type(path) is str:
        createfilefn = CreateFileW
    else:
        createfilefn = CreateFile
    # FILE_FLAG_OPEN_REPARSE_POINT alone is not enough if 'path'
    # is a symbolic link to a directory or a NTFS junction.
    # We need to set FILE_FLAG_BACKUP_SEMANTICS as well.
    # See https://docs.microsoft.com/en-us/windows/desktop/api/fileapi/nf-fileapi-createfilea
    handle = createfilefn(path, GENERIC_READ, 0, None, OPEN_EXISTING,
                          FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT, 0)

    # MAXIMUM_REPARSE_DATA_BUFFER_SIZE = 16384 = (16 * 1024)
    buf = DeviceIoControl(handle, FSCTL_GET_REPARSE_POINT, None, 16 * 1024)
    # Above will return an ugly string (byte array), so we'll need to parse it.

    # But first, we'll close the handle to our file so we're not locking it anymore.
    CloseHandle(handle)

    # Minimum possible length (assuming that the length is bigger than 0)
    if len(buf) < 9:
        return type(path)()
    # Parse and return our result.
    result = parse_reparse_buffer(buf)
    if result['tag'] in (IO_REPARSE_TAG_MOUNT_POINT, IO_REPARSE_TAG_SYMLINK):
        offset = result['substitute_name_offset']
        ending = offset + result['substitute_name_length']
        rpath = result['buffer'][offset:ending].decode('UTF-16-LE')
    else:
        rpath = result['buffer']
    if len(rpath) > 4 and rpath[0:4] == '\\??\\':
        rpath = rpath[4:]
    return rpath


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


def safe_glob(pathname):
    """
    Return a list of paths matching a pathname pattern.

    The pattern may contain simple shell-style wildcards a la
    fnmatch. However, unlike fnmatch, filenames starting with a
    dot are special cases that are not matched by '*' and '?'
    patterns.

    Like fnmatch.glob, but suppresses re.compile errors by escaping
    uncompilable path components.

    See https://bugs.python.org/issue738361

    """
    return list(safe_iglob(pathname))


def safe_iglob(pathname):
    """
    Return an iterator which yields the paths matching a pathname pattern.

    The pattern may contain simple shell-style wildcards a la
    fnmatch. However, unlike fnmatch, filenames starting with a
    dot are special cases that are not matched by '*' and '?'
    patterns.

    Like fnmatch.iglob, but suppresses re.compile errors by escaping
    uncompilable path components.
    
    See https://bugs.python.org/issue738361

    """
    dirname, basename = os.path.split(pathname)
    if not glob.has_magic(pathname):
        if basename:
            if os.path.lexists(pathname):
                yield pathname
        else:
            # Patterns ending with a slash should match only directories
            if os.path.isdir(dirname):
                yield pathname
        return
    if not dirname:
        for name in safe_glob1(os.curdir, basename):
            yield name
        return
    # `os.path.split()` returns the argument itself as a dirname if it is a
    # drive or UNC path.  Prevent an infinite recursion if a drive or UNC path
    # contains magic characters (i.e. r'\\?\C:').
    if dirname != pathname and glob.has_magic(dirname):
        dirs = safe_iglob(dirname)
    else:
        dirs = [dirname]
    if glob.has_magic(basename):
        glob_in_dir = safe_glob1
    else:
        glob_in_dir = glob.glob0
    for dirname in dirs:
        for name in glob_in_dir(dirname, basename):
            yield os.path.join(dirname, name)


def safe_glob1(dirname, pattern):
    if not dirname:
        dirname = os.curdir
    if isinstance(pattern, str) and not isinstance(dirname, str):
        dirname = str(dirname, sys.getfilesystemencoding() or
                                   sys.getdefaultencoding())
    try:
        names = os.listdir(dirname)
    except os.error:
        return []
    if pattern[0] != '.':
        names = [x for x in names if x[0] != '.']
    return safe_shell_filter(names, pattern)


def safe_shell_filter(names, pat):
    """
    Return the subset of the list NAMES that match PAT

    Like fnmatch.filter, but suppresses re.compile errors by escaping
    uncompilable path components.
    
    See https://bugs.python.org/issue738361
    
    """
    import posixpath
    result = []
    pat = os.path.normcase(pat)
    try:
        re_pat = _cache[pat]
    except KeyError:
        res: str = safe_translate(pat)
        if len(_cache) >= _MAXCACHE:
            _cache.clear()
        _cache[pat] = re_pat: Pattern[str] = re.compile(res)
    match = re_pat.match
    if os.path is posixpath:
        # normcase on posix is NOP. Optimize it away from the loop.
        for name in names:
            if match(name):
                result.append(name)
    else:
        for name in names:
            if match(os.path.normcase(name)):
                result.append(name)
    return result


def safe_translate(pat):
    """
    Translate a shell PATTERN to a regular expression.

    Like fnmatch.translate, but suppresses re.compile errors by escaping
    uncompilable path components.
    
    See https://bugs.python.org/issue738361
    
    """
    if isinstance(getattr(os.path, "altsep", None), str):
        # Normalize path separators
        pat = pat.replace(os.path.altsep, os.path.sep)
    components = pat.split(os.path.sep)
    for i, component in enumerate(components):
        translated = fnmatch.translate(component)
        try:
            re.compile(translated)
        except re.error:
            translated = re.escape(component)
        components[i] = translated
    return re.escape(os.path.sep).join(components)


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


def which(executable: str, paths: Union[list[str], None] = None) -> str | None:
    """ Return the full path of executable """
    if not paths:
        path_env: str | None = getenvu("PATH", os.defpath)
        if path_env is None:
            path_env = os.defpath  # Fallback to os.defpath if getenvu returns None
        paths = path_env.split(os.pathsep)
    for cur_dir in paths:
        filename: str = os.path.join(cur_dir, executable)
        if os.path.isfile(filename):
            try:
                # make sure file is actually executable
                if os.access(filename, os.X_OK):
                    return filename
            except Exception:
                pass
    return None


def whereis(names, bin=True, bin_paths=None, man=True, man_paths=None, src=True,
            src_paths=None, unusual=False, list_paths=False):
    """
    Wrapper around whereis
    
    """
    args = []
    if bin:
        args.append("-b")
    if bin_paths:
        args.append("-B")
        args.extend(bin_paths)
    if man:
        args.append("-m")
    if man_paths:
        args.append("-M")
        args.extend(man_paths)
    if src:
        args.append("-s")
    if src_paths:
        args.append("-S")
        args.extend(src_paths)
    if bin_paths or man_paths or src_paths:
        args.append("-f")
    if unusual:
        args.append("-u")
    if list_paths:
        args.append("-l")
    if isinstance(names, str):
        names = [names]
    p = sp.Popen(["whereis"] + args + names, stdout=sp.PIPE)
    stdout, stderr = p.communicate()
    result = {}
    for line in stdout.strip().splitlines():
        # $ whereis abc xyz
        # abc: /bin/abc
        # xyz: /bin/xyz /usr/bin/xyz
        match = line.split(":", 1)
        if match:
            result[match[0]] = match[-1].split()
    return result


class FileLock(object):

    if sys.platform == "win32":
        _exception_cls = pywintypes.error
    else:
        _exception_cls = IOError

    def __init__(self, file_, exclusive=False, blocking=False):
        self._file = file_
        self.exclusive = exclusive
        self.blocking = blocking
        self.lock()

    def __enter__(self):
        return self

    def __exit__(self, etype, value, traceback):
        self.unlock()

    def lock(self):
        if sys.platform == "win32":
            mode = 0
            if self.exclusive:
                mode |= win32con.LOCKFILE_EXCLUSIVE_LOCK
            if not self.blocking:
                mode |= win32con.LOCKFILE_FAIL_IMMEDIATELY
            self._handle = win32file._get_osfhandle(self._file.fileno())
            self._overlapped = pywintypes.OVERLAPPED()
            fn = win32file.LockFileEx
            args = (self._handle, mode, 0, -0x10000, self._overlapped)
        else:
            if self.exclusive:
                op = fcntl.LOCK_EX
            else:
                op = fcntl.LOCK_SH
            if not self.blocking:
                op |= fcntl.LOCK_NB
            fn = fcntl.flock
            args = (self._file.fileno(), op)
        self._call(fn, args, FileLock.LockingError)

    def unlock(self):
        if self._file.closed:
            return
        if sys.platform == "win32":
            fn = win32file.UnlockFileEx
            args = (self._handle, 0, -0x10000, self._overlapped)
        else:
            fn = fcntl.flock
            args = (self._file.fileno(), fcntl.LOCK_UN)
        self._call(fn, args, FileLock.UnlockingError)

    @staticmethod
    def _call(fn, args, exception_cls):
        try:
            fn(*args)
        except FileLock._exception_cls as exception:
            raise exception_cls(*exception.args)

    class Error(Exception):
        pass

    class LockingError(Error):
        pass

    class UnlockingError(Error):
        pass


if sys.platform == "win32" and sys.getwindowsversion() >= (6, ):
    class win64_disable_file_system_redirection(object):

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
