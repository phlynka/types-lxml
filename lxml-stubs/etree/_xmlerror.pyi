#
# Types for lxml/xmlerror.pxi
#

import enum
from abc import ABCMeta, abstractmethod
from logging import Logger, LoggerAdapter
from typing import Any, Collection, Iterable, Iterator, final, overload

@final
class _LogEntry:
    """Log message entry from an error log

    Attributes
    ----------
    message: str
        the message text
    domain: ErrorDomains
        domain ID
    type: ErrorTypes
        message type ID
    level: ErrorLevels
        log level ID
    line: int
        the line at which the message originated, if applicable
    column: int
        the character column at which the message originated, if applicable
    filename: str, optional
        the name of the file in which the message originated, if applicable
    path: str, optional
        the location in which the error was found, if available"""

    @property
    def domain(self) -> ErrorDomains: ...
    @property
    def type(self) -> ErrorTypes: ...
    @property
    def level(self) -> ErrorLevels: ...
    @property
    def line(self) -> int: ...
    @property
    def column(self) -> int: ...
    @property
    def domain_name(self) -> str: ...
    @property
    def type_name(self) -> str: ...
    @property
    def level_name(self) -> str: ...
    @property
    def message(self) -> str: ...
    @property
    def filename(self) -> str: ...
    @property
    def path(self) -> str | None: ...

class _BaseErrorLog(metaclass=ABCMeta):
    """The base class of all other error logs"""

    @property
    def last_error(self) -> _LogEntry | None: ...
    # copy() method is originally under _BaseErrorLog class. However
    # PyErrorLog overrides it with a dummy version, denoting it
    # shouldn't be used. So move copy() to the only other subclass
    # inherited from _BaseErrorLog, that is _ListErrorLog.
    @abstractmethod
    def receive(self, entry: _LogEntry) -> None: ...

class _ListErrorLog(_BaseErrorLog, Collection[_LogEntry]):
    """Immutable base version of a list based error log"""

    def __init__(
        self,
        entries: list[_LogEntry],
        first_error: _LogEntry | None,
        last_error: _LogEntry | None,
    ) -> None: ...
    def __iter__(self) -> Iterator[_LogEntry]: ...
    def __len__(self) -> int: ...
    def __getitem__(self, __k: int) -> _LogEntry: ...
    def __contains__(self, __o: object) -> bool: ...
    def filter_domains(self, domains: int | Iterable[int]) -> _ListErrorLog: ...
    def filter_types(self, types: int | Iterable[int]) -> _ListErrorLog: ...
    def filter_levels(self, levels: int | Iterable[int]) -> _ListErrorLog: ...
    def filter_from_level(self, level: int) -> _ListErrorLog: ...
    def filter_from_fatals(self) -> _ListErrorLog: ...
    def filter_from_errors(self) -> _ListErrorLog: ...
    def filter_from_warnings(self) -> _ListErrorLog: ...
    def clear(self) -> None: ...
    # Context manager behavior is internal to cython, not usable
    # in python code, so dropped altogether.
    # copy() is originally implemented in _BaseErrorLog, see
    # comment there for more info.
    def copy(self) -> _ListErrorLog: ...  # not Self, subclasses won't survive
    def receive(self, entry: _LogEntry) -> None: ...

# The interaction between _ListErrorLog and _ErrorLog is interesting
def _ErrorLog() -> _ListErrorLog:
    """
    Annotation notes
    ----------------
    `_ErrorLog` is originally a class itself. However, it has very
    special property that it is now annotated as function.

    `_ErrorLog`, when instantiated, generates `_ListErrorLog` object
    instead, and then patches it with extra runtime methods. `Mypy`
    becomes malevolent on any attempt of annotating such behavior.

    Therefore, besides making it a function, all extra properties
    and methods are merged into `_ListErrorLog`, since `_ListErrorLog`
    is seldom instantiated by itself.
    """

class _RotatingErrorLog(_ListErrorLog):
    """Error log that has entry limit and uses FIFO rotation"""

    def __init__(self, max_len: int) -> None: ...

# Maybe there's some sort of hidden commercial version of lxml
# that supports _DomainErrorLog, if such thing exists? Anyway,
# the class in open source lxml is entirely broken and not touched
# since 2006.

class PyErrorLog(_BaseErrorLog):
    """Global error log that connects to the Python stdlib logging package

    Original Docstring
    ------------------
    The constructor accepts an optional logger name or a readily
    instantiated logger instance.

    If you want to change the mapping between libxml2's ErrorLevels and Python
    logging levels, you can modify the level_map dictionary from a subclass.

    The default mapping is::

    ```python
    ErrorLevels.WARNING = logging.WARNING
    ErrorLevels.ERROR   = logging.ERROR
    ErrorLevels.FATAL   = logging.CRITICAL
    ```

    You can also override the method ``receive()`` that takes a LogEntry
    object and calls ``self.log(log_entry, format_string, arg1, arg2, ...)``
    with appropriate data.
    """

    @property
    def level_map(self) -> dict[int, int]: ...
    # Only either one of the 2 args in __init__ is effective;
    # when both are specified, 'logger_name' is ignored
    @overload
    def __init__(
        self,
        logger_name: str | None = None,
    ) -> None: ...
    @overload
    def __init__(
        self,
        *,
        logger: Logger | LoggerAdapter[Any] | None = None,
    ) -> None: ...
    # copy() is disallowed, implementation chooses to fail in a
    # silent way by returning dummy _ListErrorLog. We skip it altogether.
    def log(self, log_entry: _LogEntry, message: str, *args: object) -> None: ...
    def receive(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, log_entry: _LogEntry
    ) -> None: ...

def clear_error_log() -> None: ...
def use_global_python_log(log: PyErrorLog) -> None: ...

# Container for libxml2 constants
# It's overkill to include zillions of constants into type checker;
# and more no-no for updating constants along with each lxml releases
# unless these stubs are bundled with lxml together. So we only do
# minimal enums which do not involve much work. No ErrorTypes. Never.
class ErrorLevels(enum.IntEnum):
    """Error severity level constants

    Annotation notes
    ----------------
    These integer constants sementically fit int enum better, but
    in the end they are just integers. No enum properties and mechanics
    would work on them.
    """

    NONE = ...
    WARNING = ...
    ERROR = ...
    FATAL = ...

class ErrorDomains(enum.IntEnum):
    """Part of the library that raised error

    Annotation notes
    ----------------
    These integer constants sementically fit int enum better, but
    in the end they are just integers. No enum properties and mechanics
    would work on them.
    """

    NONE = ...
    PARSER = ...
    TREE = ...
    NAMESPACE = ...
    DTD = ...
    HTML = ...
    MEMORY = ...
    OUTPUT = ...
    IO = ...
    FTP = ...
    HTTP = ...
    XINCLUDE = ...
    XPATH = ...
    XPOINTER = ...
    REGEXP = ...
    DATATYPE = ...
    SCHEMASP = ...
    SCHEMASV = ...
    RELAXNGP = ...
    RELAXNGV = ...
    CATALOG = ...
    C14N = ...
    XSLT = ...
    VALID = ...
    CHECK = ...
    WRITER = ...
    MODULE = ...
    I18N = ...
    SCHEMATRONV = ...
    BUFFER = ...
    URI = ...

# TODO implement ErrorTypes enum, looks like unavoidable
class ErrorTypes(enum.IntEnum):
    """The actual libxml2 error code

    Annotation notes
    ----------------
    These integer constants sementically fit int enum better, but
    in the end they are just integers. No enum properties and mechanics
    would work on them.

    Because of the vast amount of existing codes, and its ever-increasing
    nature due to newer libxml2 releases, error type constant names
    will not be explicitly listed in stub.
    """

    def __getattr__(self, name: str) -> ErrorTypes: ...

class RelaxNGErrorTypes(enum.IntEnum):
    """RelaxNG specific libxml2 error code

    Annotation notes
    ----------------
    These integer constants sementically fit int enum better, but
    in the end they are just integers. No enum properties and mechanics
    would work on them.
    """

    RELAXNG_OK = ...
    RELAXNG_ERR_MEMORY = ...
    RELAXNG_ERR_TYPE = ...
    RELAXNG_ERR_TYPEVAL = ...
    RELAXNG_ERR_DUPID = ...
    RELAXNG_ERR_TYPECMP = ...
    RELAXNG_ERR_NOSTATE = ...
    RELAXNG_ERR_NODEFINE = ...
    RELAXNG_ERR_LISTEXTRA = ...
    RELAXNG_ERR_LISTEMPTY = ...
    RELAXNG_ERR_INTERNODATA = ...
    RELAXNG_ERR_INTERSEQ = ...
    RELAXNG_ERR_INTEREXTRA = ...
    RELAXNG_ERR_ELEMNAME = ...
    RELAXNG_ERR_ATTRNAME = ...
    RELAXNG_ERR_ELEMNONS = ...
    RELAXNG_ERR_ATTRNONS = ...
    RELAXNG_ERR_ELEMWRONGNS = ...
    RELAXNG_ERR_ATTRWRONGNS = ...
    RELAXNG_ERR_ELEMEXTRANS = ...
    RELAXNG_ERR_ATTREXTRANS = ...
    RELAXNG_ERR_ELEMNOTEMPTY = ...
    RELAXNG_ERR_NOELEM = ...
    RELAXNG_ERR_NOTELEM = ...
    RELAXNG_ERR_ATTRVALID = ...
    RELAXNG_ERR_CONTENTVALID = ...
    RELAXNG_ERR_EXTRACONTENT = ...
    RELAXNG_ERR_INVALIDATTR = ...
    RELAXNG_ERR_DATAELEM = ...
    RELAXNG_ERR_VALELEM = ...
    RELAXNG_ERR_LISTELEM = ...
    RELAXNG_ERR_DATATYPE = ...
    RELAXNG_ERR_VALUE = ...
    RELAXNG_ERR_LIST = ...
    RELAXNG_ERR_NOGRAMMAR = ...
    RELAXNG_ERR_EXTRADATA = ...
    RELAXNG_ERR_LACKDATA = ...
    RELAXNG_ERR_INTERNAL = ...
    RELAXNG_ERR_ELEMWRONG = ...
    RELAXNG_ERR_TEXTWRONG = ...
