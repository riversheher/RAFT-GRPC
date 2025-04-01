from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class LogEntry(_message.Message):
    __slots__ = ("term", "index", "command", "data", "commit")
    TERM_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    COMMIT_FIELD_NUMBER: _ClassVar[int]
    term: int
    index: int
    command: str
    data: str
    commit: bool
    def __init__(self, term: _Optional[int] = ..., index: _Optional[int] = ..., command: _Optional[str] = ..., data: _Optional[str] = ..., commit: bool = ...) -> None: ...

class LogResponse(_message.Message):
    __slots__ = ("ack", "curr_term", "next_index")
    ACK_FIELD_NUMBER: _ClassVar[int]
    CURR_TERM_FIELD_NUMBER: _ClassVar[int]
    NEXT_INDEX_FIELD_NUMBER: _ClassVar[int]
    ack: bool
    curr_term: int
    next_index: int
    def __init__(self, ack: bool = ..., curr_term: _Optional[int] = ..., next_index: _Optional[int] = ...) -> None: ...
