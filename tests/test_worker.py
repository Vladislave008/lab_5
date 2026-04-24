import pytest
import asyncio
from src.task import Task
from src.task_collections import AsyncTaskQueue
from src.async_data.dispatcher import Dispatcher
from src.async_data.worker import worker

class MockHandler:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.handled = []
    
    async def can_handle(self, task):
        return True
    
    async def handle(self, task):
        if self.should_fail:
            raise RuntimeError("Handler error")
        self.handled.append(task)

@pytest.mark.asyncio
class TestWorker:
    """Тесты воркера"""
    
    async def test_worker_processes_tasks(self):
        queue = AsyncTaskQueue()
        handler = MockHandler()
        dispatcher = Dispatcher([handler])
        
        worker_task = asyncio.create_task(worker(queue, dispatcher))
        
        await queue.put(Task(id=1))
        await queue.put(Task(id=2))
        
        await asyncio.sleep(0.2)

        queue.close()
        worker_task.cancel()
        
        try:
            await worker_task
        except asyncio.CancelledError:
            pass
        
        assert len(handler.handled) == 2
    
    async def test_worker_handles_errors(self, caplog):
        queue = AsyncTaskQueue()
        handler = MockHandler(should_fail=True)
        dispatcher = Dispatcher([handler])
        
        worker_task = asyncio.create_task(worker(queue, dispatcher))
        
        await queue.put(Task(id=1))
        await asyncio.sleep(0.2)
        
        queue.close()
        worker_task.cancel()
        
        try:
            await worker_task
        except asyncio.CancelledError:
            pass
        
        assert "Failed to process task" in caplog.text
    
    async def test_multiple_workers_concurrent(self):
        queue = AsyncTaskQueue()
        handler = MockHandler()
        dispatcher = Dispatcher([handler])
        
        workers = [asyncio.create_task(worker(queue, dispatcher)) for _ in range(3)]

        for i in range(10):
            await queue.put(Task(id=i))
        
        await asyncio.sleep(0.5)
        
        queue.close()
        
        for w in workers:
            w.cancel()
        
        await asyncio.gather(*workers, return_exceptions=True)
        
        assert len(handler.handled) == 10