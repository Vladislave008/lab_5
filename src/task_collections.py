import asyncio
from src.task import Task
from typing import Generator, Union, Callable, AsyncIterator, AsyncGenerator, Iterator
from collections import deque

class TaskQueueException(Exception):
    pass

class TaskIterator:
    """Итератор для прямого обхода TaskQueue (синхронный)"""
    def __init__(self, data: list[Task]):
        self._data = data
        self._index = 0
    
    def __iter__(self) -> Iterator:
        return self
    
    def __next__(self) -> Task:
        if self._index >= len(self._data):
            raise StopIteration
        task = self._data[self._index]
        self._index += 1
        return task

class TaskReverseIterator:
    """Итератор для обратного обхода TaskQueue (синхронный)"""
    def __init__(self, data: list):
        self._data = data
        self._index = len(data) - 1
    
    def __iter__(self) -> Iterator:
        return self
    
    def __next__(self) -> Task:
        if self._index < 0:
            raise StopIteration
        task = self._data[self._index]
        self._index -= 1
        return task

class AsyncTaskQueue:
    """Асинхронная очередь задач"""
    
    def __init__(self, tasks: list[Task] = None):
        self._data: deque[Task] = deque()
        self._condition = asyncio.Condition()
        self._closed = False
        
        if tasks is not None:
            for item in tasks:
                if not isinstance(item, Task):
                    raise TaskQueueException("All elements must be Task objects")
                self._data.append(item)
    
    def add(self, elem: Task) -> None:
        """Синхронное добавление задачи"""
        if not isinstance(elem, Task):
            raise TaskQueueException(f"Object {elem} is not a Task")
        self._data.append(elem)
        asyncio.create_task(self._wake_up_waiters())
    
    async def _wake_up_waiters(self):
        """Внутренний метод для пробуждения ждущих get()"""
        async with self._condition:
            self._condition.notify_all()
    
    def __iter__(self) -> TaskIterator:
        """Синхронная итерация по текущим задачам"""
        return TaskIterator(list(self._data))
    
    def __reversed__(self) -> TaskReverseIterator:
        """Синхронная обратная итерация"""
        return TaskReverseIterator(list(self._data))
    
    def filter_by(self, **kwargs) -> Generator:
        """Ленивый фильтр (синхронный)"""
        for task in self._data:
            if all(getattr(task, attr) == value for attr, value in kwargs.items()):
                yield task
    
    async def async_filter_by(self, **kwargs) -> AsyncGenerator:
        """Ленивый фильтр (асинхронный)"""
        while not self._closed or len(self._data) > 0:
            try:
                task = await self.get()
            except TaskQueueException:
                break
            if all(getattr(task, attr) == value for attr, value in kwargs.items()):
                yield task

    def __len__(self) -> int:
        """Длина очереди"""
        return len(self._data)
    
    def __getitem__(self, key) -> Union[Task, 'AsyncTaskQueue']:
        """Достать по индексу/слайсу"""
        if isinstance(key, slice):
            return AsyncTaskQueue(list(self._data)[key])
        return list(self._data)[key]
    
    def __setitem__(self, key, value):
        """Установка элемента"""
        if not isinstance(value, Task):
            raise TaskQueueException(f"Cannot set non-Task object: {value}")
        temp = list(self._data)
        temp[key] = value
        self._data = deque(temp)
    
    def __delitem__(self, key):
        """Удаление элемента"""
        temp = list(self._data)
        del temp[key]
        self._data = deque(temp)
    
    def is_empty(self) -> bool:
        """Проверка на пустоту"""
        return len(self._data) == 0
    
    def __contains__(self, item: Task) -> bool:
        """Проверка на вхождение"""
        return item in self._data
    
    def __add__(self, other: Union[Task, 'AsyncTaskQueue', list]) -> 'AsyncTaskQueue':
        """Конкатенация очередей"""
        new_data = list(self._data)
        if isinstance(other, AsyncTaskQueue):
            new_data.extend(other._data)
        elif isinstance(other, Task):
            new_data.append(other)
        elif isinstance(other, list):
            for item in other:
                if not isinstance(item, Task):
                    raise TaskQueueException("List contains non-Task objects")
                new_data.append(item)
        else:
            raise TaskQueueException(f"Cannot add AsyncTaskQueue and {type(other)}")
        return AsyncTaskQueue(new_data)
    
    def __iadd__(self, other: Union[Task, 'AsyncTaskQueue', list]) -> 'AsyncTaskQueue':
        """In-place конкатенация очередей"""
        if isinstance(other, AsyncTaskQueue):
            self._data.extend(other._data)
        elif isinstance(other, Task):
            self._data.append(other)
        elif isinstance(other, list):
            for item in other:
                if not isinstance(item, Task):
                    raise TaskQueueException("List contains non-Task objects")
                self._data.append(item)
        else:
            raise TaskQueueException(f"Cannot add AsyncTaskQueue and {type(other)}")
        return self
    
    def __sub__(self, other: Union[Task, 'AsyncTaskQueue', list[Task], int, Callable]) -> 'AsyncTaskQueue':
        """Вычитание очередей"""
        new_data = list(self._data)
        if isinstance(other, (AsyncTaskQueue, list)):
            exclude = set(other._data if isinstance(other, AsyncTaskQueue) else other)
            new_data = [t for t in new_data if t not in exclude]
        elif isinstance(other, Task):
            new_data = [t for t in new_data if t != other]
        elif isinstance(other, int):
            new_data = [t for t in new_data if t.id != other]
        elif callable(other):
            new_data = [t for t in new_data if not other(t)]
        else:
            raise TaskQueueException(f"Cannot subtract {type(other)} from AsyncTaskQueue")
        return AsyncTaskQueue(new_data)
    
    def __isub__(self, other: Union[Task, 'AsyncTaskQueue', list[Task], int, Callable]) -> 'AsyncTaskQueue':
        """In-place вычитание очередей"""
        if isinstance(other, (AsyncTaskQueue, list)):
            exclude = set(other._data if isinstance(other, AsyncTaskQueue) else other)
            self._data = deque([t for t in self._data if t not in exclude])
        elif isinstance(other, Task):
            self._data = deque([t for t in self._data if t != other])
        elif isinstance(other, int):
            self._data = deque([t for t in self._data if t.id != other])
        elif callable(other):
            self._data = deque([t for t in self._data if not other(t)])
        else:
            raise TaskQueueException(f"Cannot subtract {type(other)} from AsyncTaskQueue")
        return self
    
    def __repr__(self) -> str:
        """Отображение очереди"""
        return f"AsyncTaskQueue: {list(self._data)}"
    
    async def get(self) -> Task:
        """
        Асинхронно получить задачу из очереди
        Если очередь пуста, ждет появления новых задач
        Если очередь закрыта и пуста, выбрасывает TaskQueueException
        """
        async with self._condition:
            while len(self._data) == 0 and not self._closed:
                await self._condition.wait()
            
            if self._closed and len(self._data) == 0:
                raise TaskQueueException("Queue is closed and empty")
            
            return self._data.popleft()
    
    async def put(self, task: Task) -> None:       
        """Асинхронно добавить задачу в очередь"""
        if not isinstance(task, Task):
            raise TaskQueueException(f"Object {task} is not a Task")
        
        self._data.append(task)
        async with self._condition:
            self._condition.notify_all()
    
    def close(self) -> None:
        """Закрыть очередь (graceful shutdown)"""
        self._closed = True
        asyncio.create_task(self._wake_up_waiters())
    
    def terminate(self):
        """Экстренное завершение - очищает и закрывает очередь"""
        self._data.clear()
        self._closed = True
        asyncio.create_task(self._wake_up_waiters())
    
    @property
    def is_closed(self) -> bool:
        """Проверка, закрыта ли очередь"""
        return self._closed
    
    def __aiter__(self) -> AsyncIterator[Task]:
        """Асинхронная итерация по задачам"""
        return self
    
    async def __anext__(self) -> Task:
        """Асинхронный next() для `async for task in queue`"""
        try:
            return await self.get()
        except TaskQueueException:
            raise StopAsyncIteration