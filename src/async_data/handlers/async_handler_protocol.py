from typing import Protocol, Any
from typing import runtime_checkable

@runtime_checkable
class AsyncHandler(Protocol):
    """Контракт для асинхронного обработчика задач"""
    
    async def can_handle(self, task: Any) -> bool:
        """Проверяет, может ли обработчик взять эту задачу"""
        ...
    
    async def handle(self, task: Any) -> Any:
        """Асинхронно обрабатывает задачу"""
        ...