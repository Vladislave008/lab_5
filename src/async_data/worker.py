import asyncio
from src.async_data.dispatcher import Dispatcher
from task_collections import AsyncTaskQueue, TaskQueueException
import logging
logger = logging.getLogger(__name__)

async def worker(queue: AsyncTaskQueue, dispatcher: Dispatcher) -> None:
    """Бесконечный асинхронный воркер"""
    try:
        while True:
            try:
                task = await queue.get()
            except TaskQueueException:
                logger.info("[Worker] Queue closed and empty, shutting down")
                break
            
            try:
                await dispatcher.dispatch(task)
            except ValueError as e:
                logger.error(f"[Worker] No handler for task {task}: {e}")
            except Exception as e:
                logger.error(f"[Worker] Failed to process task {task}: {e}")
    except asyncio.CancelledError:
        logger.info("[Worker] Received cancel signal, shutting down")
        raise