from typing import Protocol, runtime_checkable, Any
from collections.abc import Iterable

@runtime_checkable
class TaskProtocol(Protocol):
    '''Протокол контракта задач'''
    @property
    def id(self) -> int | str: ...
    
    @property
    def payload(self) -> Any: ...


@runtime_checkable
class TaskSourceProtocol(Protocol):
    '''Протокол истоника задач'''
    def get_tasks(self) -> Iterable[TaskProtocol]: ...
