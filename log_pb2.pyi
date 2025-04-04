from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class LogEntry(_message.Message):
    __slots__ = ("term", "index", "command", "data")
    TERM_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    term: int
    index: int
    command: str
    data: str
    def __init__(self, term: _Optional[int] = ..., index: _Optional[int] = ..., command: _Optional[str] = ..., data: _Optional[str] = ...) -> None: ...

class LogResponse(_message.Message):
    __slots__ = ("ack", "term", "index")
    ACK_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    ack: bool
    term: int
    index: int
    def __init__(self, ack: bool = ..., term: _Optional[int] = ..., index: _Optional[int] = ...) -> None: ...
