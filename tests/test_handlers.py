import pytest
import logging
from src.task import Task
from src.async_data.handlers.async_handlers import (
    PrintHandler, 
    DatabaseHandler, 
    HttpPostHandler
)

@pytest.fixture(autouse=True)
def cleanup_task_ids():
    """Очищает глобальный set ID задач между тестами"""
    Task._all_ids.clear()
    yield
    Task._all_ids.clear()

@pytest.fixture(autouse=True)
def setup_logging():
    """Настраивает логирование для тестов"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        force=True
    )


@pytest.mark.asyncio
class TestPrintHandler:
    """Тесты PrintHandler"""
    
    async def test_can_handle_any_task(self):
        handler = PrintHandler()
        
        assert await handler.can_handle(Task(id=1001))
        assert await handler.can_handle(Task(id=1002, payload="test"))
        assert await handler.can_handle(Task(id=1003, payload={"data": 123}))
    
    async def test_handle_task(self, caplog):
        caplog.set_level(logging.INFO)
        
        handler = PrintHandler()
        task = Task(id=1004, payload="test task")
        
        await handler.handle(task)
        
        assert "PrintHandler" in caplog.text
        assert "1004" in caplog.text
    
    async def test_handle_multiple_tasks(self, caplog):
        caplog.set_level(logging.INFO)
        
        handler = PrintHandler()
        tasks = [
            Task(id=1005, payload="task1"),
            Task(id=1006, payload="task2"),
            Task(id=1007, payload="task3"),
        ]
        
        for task in tasks:
            await handler.handle(task)
        
        assert caplog.text.count("PrintHandler") == 3
        assert "1005" in caplog.text
        assert "1006" in caplog.text
        assert "1007" in caplog.text


@pytest.mark.asyncio
class TestDatabaseHandler:
    """Тесты DatabaseHandler"""
    
    async def test_can_handle_with_needs_dump(self):
        handler = DatabaseHandler()
        
        task = Task(id=1101, payload={"needs_dump": True, "data": "important"})
        assert await handler.can_handle(task)
    
    async def test_can_handle_with_needs_dump_false(self):
        handler = DatabaseHandler()
        
        task = Task(id=1102, payload={"needs_dump": False, "data": "important"})
        assert await handler.can_handle(task)
    
    async def test_cannot_handle_without_needs_dump(self):
        handler = DatabaseHandler()
        
        task = Task(id=1103, payload={"no_dump": True})
        assert not await handler.can_handle(task)
    
    async def test_cannot_handle_non_dict_payload(self):
        handler = DatabaseHandler()
        
        task1 = Task(id=1104, payload="string payload")
        task2 = Task(id=1105, payload=123)
        task3 = Task(id=1106, payload=[1, 2, 3])
        
        assert not await handler.can_handle(task1)
        assert not await handler.can_handle(task2)
        assert not await handler.can_handle(task3)
    
    async def test_handle_task(self, caplog):
        caplog.set_level(logging.INFO)
        
        handler = DatabaseHandler()
        task = Task(id=1107, payload={"needs_dump": True, "table": "users"})
        
        await handler.handle(task)
        
        assert "DatabaseHandler" in caplog.text
        assert "Dumping" in caplog.text
        assert "1107" in caplog.text
        assert "Dumped" in caplog.text
        assert "[DB] Connecting" in caplog.text
        assert "[DB] Closing" in caplog.text


@pytest.mark.asyncio
class TestHttpPostHandler:
    """Тесты HttpPostHandler"""
    
    async def test_can_handle_with_url(self):
        handler = HttpPostHandler()
        
        task = Task(id=1201, payload={"url": "https://api.example.com"})
        assert await handler.can_handle(task)
    
    async def test_can_handle_with_url_and_method(self):
        handler = HttpPostHandler()
        
        task = Task(id=1202, payload={
            "url": "https://api.example.com",
            "method": "POST"
        })
        assert await handler.can_handle(task)
    
    async def test_cannot_handle_without_url(self):
        handler = HttpPostHandler()
        
        task = Task(id=1203, payload={"data": "no url"})
        assert not await handler.can_handle(task)
    
    async def test_cannot_handle_non_dict_payload(self):
        handler = HttpPostHandler()
        
        task1 = Task(id=1204, payload="string payload")
        task2 = Task(id=1205, payload=123)
        
        assert not await handler.can_handle(task1)
        assert not await handler.can_handle(task2)
    
    async def test_handle_post_request(self, caplog):
        caplog.set_level(logging.INFO)
        
        handler = HttpPostHandler()
        task = Task(id=1206, payload={
            "url": "https://httpbin.org",
            "data": {"key": "value"}
        })
        
        await handler.handle(task)
        
        assert "HTTPHandler" in caplog.text
        assert "Posting" in caplog.text
        assert "1206" in caplog.text
        assert "Response" in caplog.text
        assert "[HTTP] Connecting" in caplog.text
        assert "[HTTP] POST" in caplog.text
        assert "[HTTP] Closing" in caplog.text


@pytest.mark.asyncio
class TestHandlersIntegration:
    """Интеграционные тесты хендлеров с диспетчером"""
    
    async def test_dispatch_to_correct_handler(self, caplog):
        caplog.set_level(logging.INFO)
        
        from src.async_data.dispatcher import Dispatcher
        
        handlers = [
            DatabaseHandler(),
            HttpPostHandler(),
            PrintHandler(),
        ]
        dispatcher = Dispatcher(handlers)
        
        db_task = Task(id=1301, payload={"needs_dump": True})
        await dispatcher.dispatch(db_task)
        assert "DatabaseHandler" in caplog.text
        assert "1301" in caplog.text
        
        http_task = Task(id=1302, payload={"url": "https://api.example.com"})
        await dispatcher.dispatch(http_task)
        assert "HTTPHandler" in caplog.text
        assert "1302" in caplog.text
        
        print_task = Task(id=1303, payload="simple string")
        await dispatcher.dispatch(print_task)
        assert "PrintHandler" in caplog.text
        assert "1303" in caplog.text
        
    
    async def test_no_handler_for_task(self):
        from src.async_data.dispatcher import Dispatcher
        
        class PickyHandler:
            async def can_handle(self, task):
                return task.id == 9999
            
            async def handle(self, task):
                pass
        
        dispatcher = Dispatcher([PickyHandler()])
        task = Task(id=1306)
        
        with pytest.raises(ValueError, match="No handler found"):
            await dispatcher.dispatch(task)
