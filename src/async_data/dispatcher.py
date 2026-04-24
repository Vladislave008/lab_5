from src.async_data.handlers.async_handler_protocol import AsyncHandler
from typing import Any
import logging

class DispatcherException(Exception):
    pass

logger = logging.getLogger(__name__)

class Dispatcher:
    def __init__(self, handlers: list[AsyncHandler]):
        if not all(isinstance(h, AsyncHandler) for h in handlers):
            raise DispatcherException("Got an invalid handler")
        self._handlers = handlers
    
    async def dispatch(self, task: Any) -> None:
        """Находит первый подходящий обработчик и вызывает его"""
        logger.info(f"[Dispathcer] Searching a handler for {task}")
        for handler in self._handlers:
            if await handler.can_handle(task):
                logger.info(f"[Dispathcer] Handler found for {task}: '{handler.__class__.__name__}'")
                await handler.handle(task)
                logger.info(f"[Dispathcer] Finished handling {task}")
                return
        raise ValueError(f"[Dispathcer] No handler found for {task}")