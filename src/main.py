import asyncio
import logging
from async_data.handlers.async_handler_protocol import AsyncHandler
from async_data.handlers.async_handlers import PrintHandler, DatabaseHandler, HttpPostHandler
from task_collections import AsyncTaskQueue
from async_data.dispatcher import Dispatcher
from async_data.worker import worker
from src.task import Task

logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            #filename='logger.log',
            #filemode='a'
        )

async def main() -> None:
    queue = AsyncTaskQueue()
    
    handlers: list[AsyncHandler] = [
        #PrintHandler(),
        DatabaseHandler(),
        HttpPostHandler(),
    ]
    dispatcher = Dispatcher(handlers)

    workers = [asyncio.create_task(worker(queue, dispatcher)) for _ in range(3)]
    await queue.put(Task(id=11, payload="Simple string task"))
    await queue.put(Task(id=2, payload={"type": "http_request", "url": "https://httpbin.org/post", "data": {"key": "value"}}))

    await asyncio.sleep(2)
    queue.close()
    
    await asyncio.gather(*workers, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())