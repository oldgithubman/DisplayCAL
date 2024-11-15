from typing import Union, Any
from os import PathLike

class LockFlags:
    LOCK_EX: int = 1
    LOCK_SH: int = 2
    LOCK_NB: int = 4

def lock(file_: Union[int, PathLike[Any], str], flags: Union[int, LockFlags]) -> None: ...

def unlock(file_: Union[int, PathLike[Any], str]) -> None: ...
