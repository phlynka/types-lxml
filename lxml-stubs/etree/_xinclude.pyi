from ._element import _Element
from ._module_misc import LxmlError
from ._xmlerror import _ListErrorLog

class XIncludeError(LxmlError): ...

class XInclude:
    def __init__(self) -> None: ...
    @property
    def error_log(self) -> _ListErrorLog: ...
    def __call__(self, node: _Element) -> None: ...
