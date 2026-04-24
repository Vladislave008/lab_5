import pytest
import asyncio
from src.task import Task
from src.task_collections import AsyncTaskQueue, TaskQueueException

@pytest.fixture(autouse=True)
def cleanup_task_ids():
    """Очищает глобальный set ID задач между тестами"""
    Task._all_ids.clear()
    yield
    Task._all_ids.clear()

@pytest.fixture
def task():
    """Создаёт задачу с уникальным ID"""
    return Task(id=100, payload="test")

@pytest.fixture
def tasks():
    """Создаёт список задач с уникальными ID"""
    return [Task(id=i, payload=f"task_{i}") for i in range(101, 106)]


@pytest.mark.asyncio
class TestAsyncTaskQueueAsync:
    """Асинхронные тесты очереди"""
    
    async def test_put_and_get_single(self, task):
        queue = AsyncTaskQueue()
        await queue.put(task)
        result = await queue.get()
        assert result == task
        assert len(queue) == 0
    
    async def test_get_waits_for_task(self):
        queue = AsyncTaskQueue()
        
        async def delayed_put():
            await asyncio.sleep(0.1)
            await queue.put(Task(id=201))
        
        asyncio.create_task(delayed_put())
        
        task = await queue.get()
        assert task.id == 201
    
    async def test_close_queue(self):
        queue = AsyncTaskQueue()
        queue.close()
        
        with pytest.raises(TaskQueueException, match="closed and empty"):
            await queue.get()
    
    async def test_close_with_pending_tasks(self):
        queue = AsyncTaskQueue()
        task_ids = list(range(401, 404))
        
        for tid in task_ids:
            await queue.put(Task(id=tid))
        
        queue.close()
        
        received = []
        for _ in range(len(task_ids)):
            received.append(await queue.get())
        
        with pytest.raises(TaskQueueException):
            await queue.get()
        
        assert len(received) == len(task_ids)
    
    async def test_async_iteration(self):
        queue = AsyncTaskQueue()
        task_ids = list(range(501, 504))
        
        for tid in task_ids:
            await queue.put(Task(id=tid))
        
        queue.close()
        
        received = []
        async for task in queue:
            received.append(task.id)
        
        assert received == task_ids
    
    async def test_async_filter_by(self):
        queue = AsyncTaskQueue()
        
        await queue.put(Task(id=601, status="created"))
        await queue.put(Task(id=602, status="started"))
        await queue.put(Task(id=603, status="created"))
        queue.close()
        
        received = []
        async for task in queue.async_filter_by(status="created"):
            received.append(task)
        
        assert len(received) == 2
        assert all(t.status == "created" for t in received)
    
    async def test_concurrent_puts(self):
        queue = AsyncTaskQueue()
        
        async def put_many(start, count):
            for i in range(start, start + count):
                await queue.put(Task(id=i))
        
        await asyncio.gather(
            put_many(701, 10),
            put_many(711, 10),
            put_many(721, 10)
        )
        
        assert len(queue) == 30