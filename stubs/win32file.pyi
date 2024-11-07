from _typeshed import Incomplete
from _win32typing import (
    COMMTIMEOUTS,
    WIN32_FIND_DATA,
    CopyProgressRoutine,
    ExportCallback,
    ImportCallback,
    PyCOMSTAT,
    PyDCB,
    PyHANDLE,
    PyIID,
    PyOVERLAPPED,
    PyOVERLAPPEDReadBuffer,
    PySECURITY_ATTRIBUTES,
    PySID,
)
from socket import socket
from typing import Iterator, overload
from typing_extensions import deprecated
from win32.lib.pywintypes import (
    TimeType,
    error as error,
)

UNICODE: int

FILE_GENERIC_READ: int
FILE_GENERIC_WRITE: int
FILE_ALL_ACCESS: int

GENERIC_READ: int
GENERIC_WRITE: int
GENERIC_EXECUTE: int

FILE_SHARE_DELETE: int
FILE_SHARE_READ: int
FILE_SHARE_WRITE: int

CREATE_NEW: int
CREATE_ALWAYS: int
OPEN_EXISTING: int
OPEN_ALWAYS: int
TRUNCATE_EXISTING: int

FILE_ATTRIBUTE_ARCHIVE: int
FILE_ATTRIBUTE_DIRECTORY: int
FILE_ATTRIBUTE_COMPRESSED: int
FILE_ATTRIBUTE_HIDDEN: int
FILE_ATTRIBUTE_NORMAL: int
FILE_ATTRIBUTE_OFFLINE: int
FILE_ATTRIBUTE_READONLY: int
FILE_ATTRIBUTE_SYSTEM: int
FILE_ATTRIBUTE_TEMPORARY: int

FILE_FLAG_WRITE_THROUGH: int
FILE_FLAG_OVERLAPPED: int
FILE_FLAG_NO_BUFFERING: int
FILE_FLAG_RANDOM_ACCESS: int
FILE_FLAG_SEQUENTIAL_SCAN: int
FILE_FLAG_DELETE_ON_CLOSE: int
FILE_FLAG_BACKUP_SEMANTICS: int
FILE_FLAG_POSIX_SEMANTICS: int
FILE_FLAG_OPEN_REPARSE_POINT: int

SECURITY_ANONYMOUS: int
SECURITY_IDENTIFICATION: int
SECURITY_IMPERSONATION: int
SECURITY_DELEGATION: int
SECURITY_CONTEXT_TRACKING: int
SECURITY_EFFECTIVE_ONLY: int

def AreFileApisANSI() -> int: ...

def CancelIo(handle: PyHANDLE, /) -> None: ...

def CopyFile(_from: str, to: str, bFailIfExists: int, /) -> None: ...

def CopyFileW(_from: str, to: str, bFailIfExists: int, /) -> None: ...

def CreateDirectory(name: str, sa: PySECURITY_ATTRIBUTES | None, /) -> None: ...

def CreateDirectoryW(name: str, sa: PySECURITY_ATTRIBUTES | None, /) -> None: ...

def CreateDirectoryEx(templateName: str, newDirectory: str, sa: PySECURITY_ATTRIBUTES, /) -> None: ...

def CreateFile(
    fileName: str,
    desiredAccess: int,
    shareMode: int,
    attributes: PySECURITY_ATTRIBUTES | None,
    CreationDisposition: int,
    flagsAndAttributes: int,
    hTemplateFile: PyHANDLE,
    /,
) -> PyHANDLE: ...

def CreateIoCompletionPort(handle: PyHANDLE, existing: PyHANDLE, completionKey: int, numThreads: int, /) -> PyHANDLE: ...

def CreateMailslot(
    Name: str, MaxMessageSize: int, ReadTimeout: int, SecurityAttributes: PySECURITY_ATTRIBUTES, /
) -> PyHANDLE: ...

def GetMailslotInfo(Mailslot: PyHANDLE, /) -> tuple[int, int, int, int]: ...

def SetMailslotInfo(Mailslot: PyHANDLE, ReadTimeout: int, /) -> None: ...

def DefineDosDevice(flags: int, deviceName: str, targetPath: str, /) -> None: ...
def DefineDosDeviceW(flags: int, deviceName: str, targetPath: str, /) -> None: ...

def DeleteFile(fileName: str, /) -> None: ...

def DeviceIoControl(
    Device: PyHANDLE,
    IoControlCode: int,
    InBuffer: str | memoryview | None,
    OutBuffer: int | memoryview,
    Overlapped: PyOVERLAPPED | None = ...,
) -> str | memoryview: ...

def OVERLAPPED() -> PyOVERLAPPED: ...

def FindClose(hFindFile: int, /) -> None: ...

def FindCloseChangeNotification(hChangeHandle: int, /) -> None: ...

def FindFirstChangeNotification(pathName: str, bWatchSubtree: int, notifyFilter: int, /) -> int: ...

def FindNextChangeNotification(hChangeHandle: int, /) -> int: ...

INVALID_HANDLE_VALUE: int

def FlushFileBuffers(hFile: PyHANDLE, /) -> None: ...

def GetBinaryType(appName: str, /) -> int: ...
SCS_32BIT_BINARY: int
SCS_DOS_BINARY: int
SCS_OS216_BINARY: int
SCS_PIF_BINARY: int
SCS_POSIX_BINARY: int
SCS_WOW_BINARY: int

def GetDiskFreeSpace(rootPathName: str, /) -> tuple[int, int, int, int]: ...

def GetDiskFreeSpaceEx(rootPathName: str, /) -> tuple[int, int, int]: ...

def GetDriveType(rootPathName: str, /) -> int: ...
def GetDriveTypeW(rootPathName: str, /) -> int: ...

DRIVE_UNKNOWN: int
DRIVE_NO_ROOT_DIR: int
DRIVE_REMOVABLE: int
DRIVE_FIXED: int
DRIVE_REMOTE: int
DRIVE_CDROM: int
DRIVE_RAMDISK: int

def GetFileAttributes(fileName: str, /) -> int: ...

def GetFileAttributesW(fileName: str, /) -> int: ...

def GetFileTime(
    handle: PyHANDLE, creationTime: TimeType, accessTime: TimeType, writeTime: TimeType, /
) -> tuple[TimeType, TimeType, TimeType]: ...

def SetFileTime(
    File: PyHANDLE,
    CreationTime: TimeType | None = ...,
    LastAccessTime: TimeType | None = ...,
    LastWriteTime: TimeType | None = ...,
    UTCTimes: bool = ...,
) -> None: ...

def GetFileInformationByHandle(
    handle: PyHANDLE | int, /
) -> tuple[int, TimeType, TimeType, TimeType, int, int, int, int, int, int]: ...

def GetCompressedFileSize() -> int: ...

def GetFileSize() -> int: ...

def AllocateReadBuffer(bufSize: int, /) -> PyOVERLAPPEDReadBuffer: ...

@overload
def ReadFile(hFile: PyHANDLE | int, bufSize: int, /) -> tuple[int, str]: ...
@overload
def ReadFile(
    hFile: PyHANDLE | int, buffer: PyOVERLAPPEDReadBuffer, overlapped: PyOVERLAPPED | None = ..., /
) -> tuple[int, str]: ...

def WriteFile(hFile: PyHANDLE | int, data: str | PyOVERLAPPEDReadBuffer, ol: PyOVERLAPPED | None = ..., /) -> tuple[int, int]: ...

def CloseHandle(handle: PyHANDLE | int, /) -> None: ...

def LockFileEx(hFile: PyHANDLE | int, _int: int, _int1: int, _int2: int, ol: PyOVERLAPPED | None = ..., /) -> None: ...

def UnlockFileEx(hFile: PyHANDLE | int, _int: int, _int1: int, ol: PyOVERLAPPED | None = ..., /) -> None: ...

def GetQueuedCompletionStatus(hPort: PyHANDLE, timeOut: int, /) -> tuple[int, int, int, PyOVERLAPPED]: ...

def PostQueuedCompletionStatus(
    handle: PyHANDLE, numberOfbytes: int = ..., completionKey: int = ..., overlapped: PyOVERLAPPED | None = ..., /
) -> None: ...

def GetFileType(hFile: PyHANDLE, /) -> int: ...
FILE_TYPE_UNKNOWN: int
FILE_TYPE_DISK: int
FILE_TYPE_CHAR: int
FILE_TYPE_PIPE: int

def GetLogicalDrives() -> int: ...

def GetOverlappedResult(hFile: PyHANDLE, overlapped: PyOVERLAPPED, bWait: int, /) -> int: ...

def LockFile(
    hFile: PyHANDLE, offsetLow: int, offsetHigh: int, nNumberOfBytesToLockLow: int, nNumberOfBytesToLockHigh: int, /
) -> None: ...

def MoveFile(existingFileName: str, newFileName: str, /) -> None: ...
def MoveFileW(existingFileName: str, newFileName: str, /) -> None: ...

def MoveFileEx(existingFileName: str, newFileName: str | None, flags: int, /) -> None: ...
def MoveFileExW(existingFileName: str, newFileName: str | None, flags: int, /) -> None: ...
MOVEFILE_COPY_ALLOWED: int
MOVEFILE_DELAY_UNTIL_REBOOT: int
MOVEFILE_REPLACE_EXISTING: int
MOVEFILE_WRITE_THROUGH: int
MOVEFILE_CREATE_HARDLINK: int
MOVEFILE_FAIL_IF_NOT_TRACKABLE: int

def QueryDosDevice(DeviceName: str | None, /) -> str: ...

def ReadDirectoryChangesW(
    handle: PyHANDLE, size: int, bWatchSubtree: int, dwNotifyFilter: int, overlapped: PyOVERLAPPED | None = ..., /
) -> None: ...

def FILE_NOTIFY_INFORMATION(buffer: str, size: int, /) -> tuple[tuple[int, str], ...]: ...

def SetCurrentDirectory(lpPathName: str, /) -> None: ...

def SetEndOfFile(hFile: PyHANDLE, /) -> None: ...

def SetFileApisToANSI() -> None: ...

def SetFileApisToOEM() -> None: ...

def SetFileAttributes(filename: str, newAttributes: int, /) -> None: ...

@overload
@deprecated("Support for passing two ints to create a 64-bit value is deprecated; pass a single int instead")
def SetFilePointer(handle: PyHANDLE, offset: tuple[int, int], moveMethod: int, /) -> None: ...
@overload
def SetFilePointer(handle: PyHANDLE, offset: int, moveMethod: int, /) -> None: ...

FILE_BEGIN: int
FILE_END: int
FILE_CURRENT: int

def SetVolumeLabel(rootPathName: str, volumeName: str, /) -> None: ...

def UnlockFile(
    hFile: PyHANDLE, offsetLow: int, offsetHigh: int, nNumberOfBytesToUnlockLow: int, nNumberOfBytesToUnlockHigh: int, /
) -> None: ...

def _get_osfhandle(fd: int, /) -> int: ...
# win32pipe.FDCreatePipe is the only known public method to expose this. But it opens both read and write handles.
def _open_osfhandle(osfhandle: PyHANDLE, flags: int, /) -> int: ...

def _setmaxstdio(newmax: int, /) -> int: ...

def _getmaxstdio() -> int: ...

def TransmitFile(
    Socket: socket | int,
    File: PyHANDLE | int,
    NumberOfBytesToWrite: int,
    NumberOfBytesPerSend: int,
    Overlapped: PyOVERLAPPED | None,
    Flags: int,
    Head: memoryview | None = ...,
    Tail: memoryview | None = ...,
) -> None: ...

def ConnectEx(
    s: socket | int,
    name: tuple[str | bytes | None, str | bytes | int | None],
    Overlapped: PyOVERLAPPED,
    SendBuffer: memoryview | None = ...
) -> tuple[int, int]: ...

def AcceptEx(slistening: socket | int, sAccepting: socket | int, buffer: memoryview, ol: PyOVERLAPPED, /) -> None: ...

def CalculateSocketEndPointSize(socket: socket | int, /) -> int: ...

def GetAcceptExSockaddrs(
    sAccepting: socket | int, buffer: PyOVERLAPPEDReadBuffer, /
) -> tuple[int, tuple[str, int] | bytes, tuple[str, int] | bytes]: ...

def WSAEventSelect(socket: socket, hEvent: PyHANDLE, networkEvents: int, /) -> None: ...

def WSAEnumNetworkEvents(s: socket, hEvent: PyHANDLE | None, /) -> dict[int, int]: ...

def WSAAsyncSelect(socket: socket, hwnd: int, _int: int, networkEvents: int, /) -> None: ...

def WSASend(s: socket | int, buffer: str | memoryview, ol: PyOVERLAPPED, dwFlags: int | None, /) -> tuple[int, int]: ...

def WSARecv(s: socket | int, buffer: memoryview, ol: PyOVERLAPPED, dwFlags: int | None, /) -> tuple[int, int]: ...

SO_UPDATE_ACCEPT_CONTEXT: int
SO_UPDATE_CONNECT_CONTEXT: int
SO_CONNECT_TIME: int

WSAEWOULDBLOCK: int
WSAENETDOWN: int
WSAENOTCONN: int
WSAEINTR: int
WSAEINPROGRESS: int
WSAENETRESET: int
WSAENOTSOCK: int
WSAEFAULT: int
WSAEOPNOTSUPP: int
WSAESHUTDOWN: int
WSAEMSGSIZE: int
WSAEINVAL: int
WSAECONNABORTED: int
WSAECONNRESET: int
WSAENOBUFS: int
WSAEDISCON: int
WSA_IO_PENDING: int
WSA_OPERATION_ABORTED: int
FD_READ: int
FD_WRITE: int
FD_OOB: int
FD_ACCEPT: int
FD_CONNECT: int
FD_CLOSE: int
FD_QOS: int
FD_GROUP_QOS: int
FD_ROUTING_INTERFACE_CHANGE: int
FD_ADDRESS_LIST_CHANGE: int

def DCB(*args: Incomplete) -> Incomplete: ...  # incomplete

def BuildCommDCB(_def: str, dcb: PyDCB, /) -> PyDCB: ...

def ClearCommError(handle: PyHANDLE, /) -> tuple[int, PyCOMSTAT]: ...

def EscapeCommFunction(handle: PyHANDLE, /) -> None: ...

def GetCommState(handle: PyHANDLE, /) -> PyDCB: ...
def SetCommState(handle: PyHANDLE, dcb: PyDCB, /) -> None: ...

def ClearCommBreak(handle: PyHANDLE, /) -> None: ...

def GetCommMask(handle: PyHANDLE, /) -> int: ...

def SetCommMask(handle: PyHANDLE, val: int, /) -> int: ...

def GetCommModemStatus(handle: PyHANDLE, /) -> int: ...

def GetCommTimeouts(handle: PyHANDLE, /) -> COMMTIMEOUTS: ...

def SetCommTimeouts(handle: PyHANDLE, val: COMMTIMEOUTS, /) -> int: ...

def PurgeComm(handle: PyHANDLE, action: int, /) -> None: ...

def SetCommBreak(handle: PyHANDLE, /) -> None: ...

def SetupComm(handle: PyHANDLE, dwInQueue: int, dwOutQueue: int, /) -> None: ...

def TransmitCommChar(handle: PyHANDLE, cChar: str, /) -> None: ...

def WaitCommEvent(handle: PyHANDLE, overlapped: PyOVERLAPPED, /) -> None: ...

def SetVolumeMountPoint(VolumeMountPoint: str, VolumeName: str) -> str: ...

def DeleteVolumeMountPoint(VolumeMountPoint: str) -> None: ...

def GetVolumeNameForVolumeMountPoint(VolumeMountPoint: str) -> str: ...

def GetVolumePathName(FileName: str, BufferLength: int | None = ...) -> str: ...

def GetVolumePathNamesForVolumeName(VolumeName: str) -> list[str]: ...

def CreateHardLink(
    FileName: str,
    ExistingFileName: str,
    SecurityAttributes: PySECURITY_ATTRIBUTES | None = ...,
    Transaction: PyHANDLE | None = ...,
) -> None: ...

def CreateSymbolicLink(
    SymlinkFileName: str, TargetFileName: str, Flags: int = ..., Transaction: PyHANDLE | None = ...
) -> None: ...

def EncryptFile(filename: str, /) -> None: ...

def DecryptFile(filename: str, /) -> None: ...

def EncryptionDisable(DirName: str, Disable: bool, /) -> None: ...

def FileEncryptionStatus(FileName: str, /) -> int: ...

def QueryUsersOnEncryptedFile(FileName: str, /) -> tuple[PySID, bytes, str]: ...

def QueryRecoveryAgentsOnEncryptedFile(FileName: str, /) -> tuple[PySID, bytes, str]: ...

def RemoveUsersFromEncryptedFile(FileName: str, pHashes: tuple[tuple[PySID, bytes, str], ...], /) -> None: ...

def AddUsersToEncryptedFile(FileName: str, pUsers: tuple[tuple[PySID, str, int], ...], /) -> None: ...

def DuplicateEncryptionInfoFile(
    SrcFileName: str,
    DstFileName: str,
    CreationDisposition: int,
    Attributes: int,
    SecurityAttributes: PySECURITY_ATTRIBUTES | None = ...,
) -> None: ...

def BackupRead(
    hFile: PyHANDLE, NumberOfBytesToRead: int, Buffer: memoryview, bAbort: int, bProcessSecurity: int, lpContext: int, /
) -> tuple[int, memoryview, int]: ...

@overload
@deprecated("Support for passing two ints to create a 64-bit value is deprecated; pass a single int instead")
def BackupSeek(hFile: PyHANDLE, NumberOfBytesToSeek: tuple[int, int], lpContext: int, /) -> int: ...
@overload
def BackupSeek(hFile: PyHANDLE, NumberOfBytesToSeek: int, lpContext: int, /) -> int: ...

def BackupWrite(
    hFile: PyHANDLE, NumberOfBytesToWrite: int, Buffer: str, bAbort: int, bProcessSecurity: int, lpContext: int, /
) -> tuple[int, int]: ...

def SetFileShortName(hFile: PyHANDLE, ShortName: str, /) -> None: ...

def CopyFileEx(
    ExistingFileName: str,
    NewFileName: str,
    ProgressRoutine: CopyProgressRoutine | None = ...,
    Data: object | None = ...,
    Cancel: bool = ...,
    CopyFlags: int = ...,
    Transaction: PyHANDLE | None = ...,
) -> None: ...

def MoveFileWithProgress(
    ExistingFileName: str,
    NewFileName: str,
    ProgressRoutine: CopyProgressRoutine | None = ...,
    Data: object | None = ...,
    Flags: int = ...,
    Transaction: PyHANDLE | None = ...,
) -> None: ...

def ReplaceFile(
    ReplacedFileName: str,
    ReplacementFileName: str,
    BackupFileName: str | None = ...,
    ReplaceFlags: int = ...,
    Exclude: None = ...,
    Reserved: None = ...,
    /,
) -> None: ...

def OpenEncryptedFileRaw(FileName: str, Flags: int, /) -> object: ...

def ReadEncryptedFileRaw(ExportCallback: ExportCallback, CallbackContext: object, Context: object, /) -> None: ...

def WriteEncryptedFileRaw(ImportCallback: ImportCallback, CallbackContext: object, Context: object, /) -> None: ...

def CloseEncryptedFileRaw(Context: object, /) -> None: ...

def CreateFileW(
    FileName: str,
    DesiredAccess: int,
    ShareMode: int,
    SecurityAttributes: PySECURITY_ATTRIBUTES | None,
    CreationDisposition: int,
    FlagsAndAttributes: int,
    TemplateFile: PyHANDLE | None = ...,
    Transaction: PyHANDLE | None = ...,
    MiniVersion: int | None = ...,
    ExtendedParameter: None = ...,
) -> PyHANDLE: ...

def DeleteFileW(FileName: str, Transaction: PyHANDLE | None = ...) -> None: ...

def GetFileAttributesEx(
    FileName: str | bytes, InfoLevelId: int, Transaction: PyHANDLE | None = ...
) -> tuple[int, TimeType, TimeType, TimeType, int]: ...
def GetFileAttributesExW(*args: Incomplete) -> Incomplete: ...  # incomplete

def SetFileAttributesW(FileName: str, FileAttributes: int, Transaction: PyHANDLE | None = ...) -> None: ...

def CreateDirectoryExW(
    TemplateDirectory: str | None,
    NewDirectory: str,
    SecurityAttributes: PySECURITY_ATTRIBUTES | None = ...,
    Transaction: PyHANDLE | None = ...,
) -> None: ...

def RemoveDirectory(PathName: str, Transaction: PyHANDLE | None = ...) -> None: ...

def FindFilesW(FileName: str, Transaction: PyHANDLE | None = ...) -> list[WIN32_FIND_DATA]: ...

def FindFilesIterator(FileName: str, Transaction: PyHANDLE | None = ...) -> Iterator[WIN32_FIND_DATA]: ...

def FindStreams(FileName: str, Transaction: PyHANDLE | None = ...) -> list[tuple[int, str]]: ...

def FindFileNames(FileName: str, Transaction: PyHANDLE | None = ...) -> list[str]: ...

def GetFinalPathNameByHandle(File: PyHANDLE, Flags: int) -> str: ...

def SfcGetNextProtectedFile() -> list[str]: ...

def SfcIsFileProtected(ProtFileName: str, /) -> bool: ...

def GetLongPathName(ShortPath: str, Transaction: PyHANDLE | None = ...) -> str: ...

def GetFullPathName(FileName: bytes | str, Transaction: PyHANDLE | None = ...) -> str: ...

def Wow64DisableWow64FsRedirection() -> int: ...

def Wow64RevertWow64FsRedirection(OldValue: int, /) -> None: ...

def GetFileInformationByHandleEx(File: PyHANDLE, FileInformationClass: int) -> object: ...

@overload
@deprecated("Support for passing two ints to create a 64-bit value is deprecated; pass a single int instead")
def SetFileInformationByHandle(File: PyHANDLE, FileInformationClass: int, Information: tuple[int, int]) -> None: ...
@overload
def SetFileInformationByHandle(File: PyHANDLE, FileInformationClass: int, Information: object) -> None: ...

def ReOpenFile(OriginalFile: PyHANDLE, DesiredAccess: int, ShareMode: int, Flags: int) -> PyHANDLE: ...

@overload
@deprecated("Support for passing two ints to create a 64-bit value is deprecated; pass a single int instead")
def OpenFileById(
    File: PyHANDLE,
    FileId: tuple[int, int],
    DesiredAccess: int,
    ShareMode: int,
    Flags: int,
    SecurityAttributes: PySECURITY_ATTRIBUTES | None = ...,
) -> PyHANDLE: ...
@overload
def OpenFileById(
    File: PyHANDLE,
    FileId: int | PyIID,
    DesiredAccess: int,
    ShareMode: int,
    Flags: int,
    SecurityAttributes: PySECURITY_ATTRIBUTES | None = ...,
) -> PyHANDLE: ...

EV_BREAK: int
EV_CTS: int
EV_DSR: int
EV_ERR: int
EV_RING: int
EV_RLSD: int
EV_RXCHAR: int
EV_RXFLAG: int
EV_TXEMPTY: int
CBR_110: int
CBR_19200: int
CBR_300: int
CBR_38400: int
CBR_600: int
CBR_56000: int
CBR_1200: int
CBR_57600: int
CBR_2400: int
CBR_115200: int
CBR_4800: int
CBR_128000: int
CBR_9600: int
CBR_256000: int
CBR_14400: int
DTR_CONTROL_DISABLE: int
DTR_CONTROL_ENABLE: int
DTR_CONTROL_HANDSHAKE: int
RTS_CONTROL_DISABLE: int
RTS_CONTROL_ENABLE: int
RTS_CONTROL_HANDSHAKE: int
RTS_CONTROL_TOGGLE: int
EVENPARITY: int
MARKPARITY: int
NOPARITY: int
ODDPARITY: int
SPACEPARITY: int
ONESTOPBIT: int
ONE5STOPBITS: int
TWOSTOPBITS: int
CLRDTR: int
CLRRTS: int
SETDTR: int
SETRTS: int
SETXOFF: int
SETXON: int
SETBREAK: int
CLRBREAK: int
PURGE_TXABORT: int
PURGE_RXABORT: int
PURGE_TXCLEAR: int
PURGE_RXCLEAR: int

FILE_ENCRYPTABLE: int
FILE_IS_ENCRYPTED: int
FILE_SYSTEM_ATTR: int
FILE_ROOT_DIR: int
FILE_SYSTEM_DIR: int
FILE_UNKNOWN: int
FILE_SYSTEM_NOT_SUPPORT: int
FILE_USER_DISALLOWED: int
FILE_READ_ONLY: int

TF_DISCONNECT: int
TF_REUSE_SOCKET: int
TF_WRITE_BEHIND: int
TF_USE_DEFAULT_WORKER: int
TF_USE_SYSTEM_THREAD: int
TF_USE_KERNEL_APC: int

# flags used with CopyFileEx
COPY_FILE_ALLOW_DECRYPTED_DESTINATION: int
COPY_FILE_FAIL_IF_EXISTS: int
COPY_FILE_RESTARTABLE: int
COPY_FILE_OPEN_SOURCE_FOR_WRITE: int
COPY_FILE_COPY_SYMLINK: int

# return codes from CopyFileEx progress routine
PROGRESS_CONTINUE: int
PROGRESS_CANCEL: int
PROGRESS_STOP: int
PROGRESS_QUIET: int

# callback reasons from CopyFileEx
CALLBACK_CHUNK_FINISHED: int
CALLBACK_STREAM_SWITCH: int

# flags used with ReplaceFile
REPLACEFILE_IGNORE_MERGE_ERRORS: int
REPLACEFILE_WRITE_THROUGH: int

# flags for OpenEncryptedFileRaw
CREATE_FOR_IMPORT: int
CREATE_FOR_DIR: int
OVERWRITE_HIDDEN: int

# Info level for GetFileAttributesEx and GetFileAttributesTransacted (GET_FILEEX_INFO_LEVELS enum)
GetFileExInfoStandard: int

# Flags for CreateSymbolicLink/CreateSymbolicLinkTransacted
SYMBOLIC_LINK_FLAG_DIRECTORY: int
SYMBOLIC_LINK_FLAG_ALLOW_UNPRIVILEGED_CREATE: int

# FILE_INFO_BY_HANDLE_CLASS used with GetFileInformationByHandleEx
FileBasicInfo: int
FileStandardInfo: int
FileNameInfo: int
FileRenameInfo: int
FileDispositionInfo: int
FileAllocationInfo: int
FileEndOfFileInfo: int
FileStreamInfo: int
FileCompressionInfo: int
FileAttributeTagInfo: int
FileIdBothDirectoryInfo: int
FileIdBothDirectoryRestartInfo: int
FileIoPriorityHintInfo: int

IoPriorityHintVeryLow: int
IoPriorityHintLow: int
IoPriorityHintNormal: int

# used with OpenFileById
FileIdType: int
ObjectIdType: int
