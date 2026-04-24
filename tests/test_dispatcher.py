import pytest
from src.task import Task
from src.async_data.dispatcher import Dispatcher, DispatcherException

class MockHandler:
    def __init__(self, can_handle=True, handler_name="Mock"):
        self.can_handle_val = can_handle
        self.handler_name = handler_name
        self.handled_tasks = []
    
    async def can_handle(self, task):
        return self.can_handle_val
    
    async def handle(self, task):
        self.handled_tasks.append(task)

@pytest.mark.asyncio
class TestDispatcher:
    """Тесты диспетчера"""
    
    async def test_dispatch_to_correct_handler(self):
        handler1 = MockHandler(can_handle=False, handler_name="H1")
        handler2 = MockHandler(can_handle=True, handler_name="H2")
        handler3 = MockHandler(can_handle=True, handler_name="H3")
        
        dispatcher = Dispatcher([handler1, handler2, handler3])
        task = Task(id=1)
        
        await dispatcher.dispatch(task)
        
        assert len(handler1.handled_tasks) == 0
        assert len(handler2.handled_tasks) == 1
        assert len(handler3.handled_tasks) == 0
    
    async def test_dispatch_first_matching(self):
        handler1 = MockHandler(can_handle=True, handler_name="H1")
        handler2 = MockHandler(can_handle=True, handler_name="H2")
        
        dispatcher = Dispatcher([handler1, handler2])
        task = Task(id=1)
        
        await dispatcher.dispatch(task)
        
        assert len(handler1.handled_tasks) == 1
        assert len(handler2.handled_tasks) == 0
    
    async def test_no_handler_found(self):
        handler = MockHandler(can_handle=False)
        dispatcher = Dispatcher([handler])
        task = Task(id=1)
        
        with pytest.raises(ValueError, match="No handler found"):
            await dispatcher.dispatch(task)
    
    async def test_dispatcher_with_real_protocol(self):
        class RealHandler:
            async def can_handle(self, task: Task) -> bool:
                return task.id == 42
            
            async def handle(self, task: Task):
                task.payload = "handled"
        
        dispatcher = Dispatcher([RealHandler()])
        
        task1 = Task(id=1)
        task42 = Task(id=42)
        
        with pytest.raises(ValueError):
            await dispatcher.dispatch(task1)
        
        await dispatcher.dispatch(task42)
        assert task42.payload == "handled"
    
    async def test_invalid_handler_initialization(self):
        class InvalidHandler:
            pass
        
        with pytest.raises(DispatcherException, match="invalid handler"):
            Dispatcher([InvalidHandler()])
    
    async def test_empty_handlers(self):
        dispatcher = Dispatcher([])
        
        with pytest.raises(ValueError, match="No handler found"):
            await dispatcher.dispatch(Task(id=1))
    
    async def test_handler_exception_spreads(self):
        class FailingHandler:
            async def can_handle(self, task):
                return True
            
            async def handle(self, task):
                raise RuntimeError("Handler failed")
        
        dispatcher = Dispatcher([FailingHandler()])
        
        with pytest.raises(RuntimeError, match="Handler failed"):
            await dispatcher.dispatch(Task(id=1))