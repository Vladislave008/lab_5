from src.task import Task
from typing import Generator, Union, Callable

class TaskQueueException(Exception):
    pass

class TaskIterator:
    """Итератор для прямого обхода TaskQueue"""
    def __init__(self, data: list[Task]):
        self._data = data
        self._index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._index >= len(self._data):
            raise StopIteration
        try:
            task = self._data[self._index]
            self._index += 1
            return task   
        except IndexError:
            raise StopIteration("Queue was modified during iteration")

class TaskReverseIterator:
    """Итератор для обратного обхода TaskQueue"""
    
    def __init__(self, data: list):
        self._data = data
        self._index = len(data) - 1
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._index < 0:
            raise StopIteration
        try:
            task = self._data[self._index]
            self._index -= 1
            return task
        except IndexError:
            raise StopIteration("Queue was modified during iteration")

class TaskQueue:
    def __init__(self, tasks: list[Task] = None):
        self._data = []
        if tasks is not None:
            for item in tasks:
                if not isinstance(item, Task):
                    raise TaskQueueException("All elements must be Task objects")
                self._data.append(item)

    def add(self, elem: Task) -> None:
        """Добавление объекта в коллекцию"""
        if not isinstance(elem, Task):
            raise TaskQueueException(f"Object {elem} is not a Task")
        self._data.append(elem)
    
    def __iter__(self) -> TaskIterator:
        """Реализация Iterable-поведения"""
        return TaskIterator(self._data)

    def __reversed__(self) -> TaskReverseIterator:
        """Поддержка обратной итерации: reversed(queue)"""
        return TaskReverseIterator(self._data)
    
    def filter_by(self, **kwargs) -> Generator:
        """Ленивый фильтр по заданным параметрам"""
        for task in self._data:
            if all(getattr(task, attr, None) == value for attr, value in kwargs.items()):
                yield task

    def __len__(self) -> int:
        """Длина коллекции"""
        return len(self._data)

    def __getitem__(self, key) -> Union[Task, 'TaskQueue']:
        """Чтение по индексу"""
        if isinstance(key, slice):
            return TaskQueue(self._data[key])
        return self._data[key]
    
    def __setitem__(self, key, value):
        """Изменение по индексу"""
        if not isinstance(value, Task):
            raise TaskQueueException(f"Cannot set non-Task object: {value}")
        self._data[key] = value
    
    def __delitem__(self, key):
        """Удаление по индексу"""
        del self._data[key]

    def is_empty(self) -> bool:
        """Проверка на пустоту"""
        return len(self._data) == 0

    def __contains__(self, item: Task) -> bool:
        """Проверка на вхождение объекта"""
        return item in self._data      

    def __add__(self, other: Union[Task, 'TaskQueue', list]) -> 'TaskQueue':
        """Конкатенация очередей
        Поддерживает:
        - Task: добавление конкретной задачи
        - TaskQueue: добавление всех задач, состоящих в другой очереди
        - list[Task]: добавление задач, состоящих в списке
        """
        new_data = self._data.copy()
        if isinstance(other, TaskQueue):
            new_data.extend(other._data)
        elif isinstance(other, Task):
            new_data.append(other)
        elif isinstance(other, list):
            for item in other:
                if not isinstance(item, Task):
                    raise TaskQueueException("List contains non-Task objects")
                new_data.append(item)
        else:
            raise TaskQueueException(f"Cannot add TaskQueue and {type(other)}")
        return TaskQueue(new_data)
    
    def __iadd__(self, other: Union[Task, 'TaskQueue', list]) -> 'TaskQueue':
        """Inplace-конкатенация очередей
        Поддерживает:
        - Task: добавление конкретной задачи
        - TaskQueue: добавление всех задач, состоящих в другой очереди
        - list[Task]: добавление задач, состоящих в списке
        """
        if isinstance(other, TaskQueue):
            self._data.extend(other._data)
        elif isinstance(other, Task):
            self._data.append(other)
        elif isinstance(other, list):
            for item in other:
                if not isinstance(item, Task):
                    raise TaskQueueException("List contains non-Task objects")
                self._data.append(item)
        else:
            raise TaskQueueException(f"Cannot add TaskQueue and {type(other)}")
        return self

    def __sub__(self, other: Union[Task, 'TaskQueue', list[Task], int, Callable]) -> 'TaskQueue':
        """Создаёт новую очередь без указанных задач
        Поддерживает:
        - Task: удаление конкретной задачи
        - TaskQueue: удаление всех задач, состоящих в другой очереди
        - list[Task]: удаление задач, состоящих в списке
        - int: удаление задачи по ID
        - callable: удаление задач, удовлетворяющих условию (queue = queue - (lambda t: t.id == 5))
        """
        new_data = self._data.copy()
        if isinstance(other, (TaskQueue, list)):
            exclude = set(other._data if isinstance(other, TaskQueue) else other)
            new_data = [t for t in new_data if t not in exclude]
        elif isinstance(other, Task):
            new_data = [t for t in new_data if t != other]
        elif isinstance(other, int):
            new_data = [t for t in new_data if t.id != other]
        elif callable(other):
            new_data = [t for t in new_data if not other(t)]
        else:
            raise TaskQueueException(f"Cannot subtract {type(other)} from TaskQueue")
        return TaskQueue(new_data)


    def __isub__(self, other: Union[Task, 'TaskQueue', list[Task], int, Callable]) -> 'TaskQueue':
        """Inplace-удаление задач
        Поддерживает:
        - Task: удаление конкретной задачи
        - TaskQueue: удаление всех задач, состоящих в другой очереди
        - list[Task]: удаление задач, состоящих в списке
        - int: удаление задачи по ID
        - callable: удаление задач, удовлетворяющих условию (queue -= (lambda t: t.id == 5))
        """
        if isinstance(other, (TaskQueue, list)):
            exclude = set(other._data if isinstance(other, TaskQueue) else other)
            self._data = [t for t in self._data if t not in exclude]
        elif isinstance(other, Task):
            self._data = [t for t in self._data if t != other]
        elif isinstance(other, int):
            self._data = [t for t in self._data if t.id != other]
        elif callable(other):
            self._data = [t for t in self._data if not other(t)]
        else:
            raise TaskQueueException(f"Cannot subtract {type(other)} from TaskQueue")
        return self

    def __repr__(self):
        tasks = [t for t in self._data]
        return f"Task queue: {tasks}"