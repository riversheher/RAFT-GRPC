from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AccountRequest(_message.Message):
    __slots__ = ("account_id", "account_type")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    account_type: str
    def __init__(self, account_id: _Optional[str] = ..., account_type: _Optional[str] = ...) -> None: ...

class AccountResponse(_message.Message):
    __slots__ = ("account_id", "message")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    message: str
    def __init__(self, account_id: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class BalanceResponse(_message.Message):
    __slots__ = ("account_id", "balance", "message")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    balance: float
    message: str
    def __init__(self, account_id: _Optional[str] = ..., balance: _Optional[float] = ..., message: _Optional[str] = ...) -> None: ...

class DepositRequest(_message.Message):
    __slots__ = ("account_id", "amount")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    amount: float
    def __init__(self, account_id: _Optional[str] = ..., amount: _Optional[float] = ...) -> None: ...

class WithdrawRequest(_message.Message):
    __slots__ = ("account_id", "amount")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    amount: float
    def __init__(self, account_id: _Optional[str] = ..., amount: _Optional[float] = ...) -> None: ...

class InterestRequest(_message.Message):
    __slots__ = ("account_id", "annual_interest_rate")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    ANNUAL_INTEREST_RATE_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    annual_interest_rate: float
    def __init__(self, account_id: _Optional[str] = ..., annual_interest_rate: _Optional[float] = ...) -> None: ...

class TransactionResponse(_message.Message):
    __slots__ = ("account_id", "message", "balance")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    message: str
    balance: float
    def __init__(self, account_id: _Optional[str] = ..., message: _Optional[str] = ..., balance: _Optional[float] = ...) -> None: ...

class HistoryRequest(_message.Message):
    __slots__ = ("account_id",)
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    def __init__(self, account_id: _Optional[str] = ...) -> None: ...

class HistoryResponse(_message.Message):
    __slots__ = ("account_id", "transactions")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    TRANSACTIONS_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    transactions: _containers.RepeatedCompositeFieldContainer[TransactionResponse]
    def __init__(self, account_id: _Optional[str] = ..., transactions: _Optional[_Iterable[_Union[TransactionResponse, _Mapping]]] = ...) -> None: ...
