from typing import Any
from src.task import Task
import asyncio
from src.async_data.context_mgmt import DatabaseSession, HTTPSession
import logging

logger = logging.getLogger(__name__)

class PrintHandler:
    """Печатает задачу"""
    
    async def can_handle(self, task: Task) -> bool:
        return isinstance(task, Task)
    
    async def handle(self, task: Any) -> None:
        await asyncio.sleep(0.1)
        logger.info(f"[PrintHandler]: Handling {task}")


class HttpPostHandler:
    """Отправляет задачу через HTTP POST"""
    
    async def can_handle(self, task: Task) -> bool:
        return isinstance(task.payload, dict) and 'url' in task.payload
    
    async def handle(self, task: Task) -> None:
        url = task.payload['url']
        data = task.payload.get('data', {})
        
        async with HTTPSession(url) as http:
            logger.info(f"[HTTPHandler]: Posting {task}")
            response = await http.post("/api/task", json={"task_id": task.id, **data})
            logger.info(f"[HTTPHandler]: Response for {task}: '{response}'")

class DatabaseHandler:
    """Сохраняет задачу в базу данных"""
    
    async def can_handle(self, task: Task) -> bool:
        return isinstance(task.payload, dict) and 'needs_dump' in task.payload
    
    async def handle(self, task: Task) -> None:
        async with DatabaseSession("tasks.db") as conn:
            logger.info(f"[DatabaseHandler]: Dumping {task} with connection '{conn}'")
            await asyncio.sleep(0.15)
            logger.info(f"[DatabaseHandler]: Dumped {task}")