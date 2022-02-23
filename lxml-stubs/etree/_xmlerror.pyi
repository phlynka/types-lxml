#
# Types for lxml/xmlerror.pxi
#

import enum
from logging import Logger
from typing import Any, Iterator, Optional, Tuple, TypeVar, Union

Self = TypeVar("Self")

class _LogEntry:
    @property
    def doamin(self) -> int: ...
    @property
    def type(self) -> int: ...
    @property
    def level(self) -> int: ...
    @property
    def line(self) -> int: ...
    @property
    def column(self) -> int: ...
    @property
    def doamin_name(self) -> str: ...
    @property
    def type_name(self) -> str: ...
    @property
    def level_name(self) -> str: ...
    @property
    def message(self) -> str: ...
    @property
    def filename(self) -> Optional[str]: ...
    @property
    def path(self) -> str: ...

class _BaseErrorLog:
    @property
    def last_error(self) -> _LogEntry: ...
    def copy(self: Self) -> Self: ...
    def receive(self, log_entry: _LogEntry) -> None: ...

# Immutable list-like
class _ListErrorLog(_BaseErrorLog):
    def __iter__(self) -> Iterator[_LogEntry]: ...
    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> _LogEntry: ...
    def __contains__(self, type: int) -> bool: ...
    def filter_domains(self, domains: Union[int, Tuple[int]]) -> _ListErrorLog: ...
    def filter_types(self, types: Union[int, Tuple[int]]) -> _ListErrorLog: ...
    def filter_levels(self, levels: Union[int, Tuple[int]]) -> _ListErrorLog: ...
    def filter_from_level(self, level: int) -> _ListErrorLog: ...
    def filter_from_fatals(self) -> _ListErrorLog: ...
    def filter_from_errors(self) -> _ListErrorLog: ...
    def filter_from_warnings(self) -> _ListErrorLog: ...

# Behave like context manager, but return types don't quite match
class _ErrorLog(_ListErrorLog):
    def __enter__(self) -> int: ...
    def __exit__(self) -> None: ...
    def clear(self) -> None: ...

class _DomainErrorLog(_ErrorLog): ...
class _RotatingErrorLog(_ErrorLog): ...

def clear_error_log() -> None: ...

class PyErrorLog(_BaseErrorLog):
    @property
    def level_map(self) -> dict[int, int]: ...
    def __init__(
        self, logger_name: Optional[str] = ..., logger: Logger = ...
    ) -> None: ...
    # FIXME PyErrorLog.copy() is a dummy that doesn't really copy itself,
    # causing error on type checkers
    # def copy(self) -> _ListErrorLog: ...
    def log(self, log_entry: _LogEntry, message: str, *args: Any) -> None: ...

def use_global_python_log(log: PyErrorLog) -> None: ...

# Container for libxml2 constants
class ErrorLevels(enum.IntEnum):
    NONE = ...
    WARNING = ...
    ERROR = ...
    FATAL = ...

# It's overkill to include zillions of constants into type checker;
# and more no-no for updating constants along with each lxml releases
# unless these stubs are bundled with lxml together
class ErrorDomains:
    def __getattr__(self, name: str) -> int: ...

class ErrorTypes:
    def __getattr__(self, name: str) -> int: ...

class RelaxNGErrorTypes:
    def __getattr__(self, name: str) -> int: ...
