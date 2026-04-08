import pytest
from datetime import timedelta
from src.task import Task
from src.task_collections import TaskQueue, TaskQueueException, TaskIterator, TaskReverseIterator

@pytest.fixture(autouse=True)
def cleanup_task_ids():
    """Очищает глобальный set ID задач между тестами"""
    Task._all_ids.clear()
    yield
    Task._all_ids.clear()

@pytest.fixture
def sample_task():
    """Создает тестовую задачу"""
    return Task(id=1, description="Test task", status="created", priority=5)

@pytest.fixture
def sample_tasks():
    """Создает список тестовых задач"""
    tasks = []
    for i in range(1, 6):
        task = Task(
            id=i,
            description=f"Task {i}",
            status="created" if i % 2 == 0 else "finished",
            priority=i,
            planned_time=timedelta(hours=i)
        )
        tasks.append(task)
    return tasks

@pytest.fixture
def empty_queue():
    """Создает пустую очередь"""
    return TaskQueue()

@pytest.fixture
def queue_with_tasks(sample_tasks):
    """Создает очередь с задачами"""
    return TaskQueue(sample_tasks)

@pytest.fixture
def queue_with_three_tasks():
    """Создает очередь с тремя задачами"""
    tasks = [
        Task(id=13, description="Task 1", status="created"),
        Task(id=214, description="Task 2", status="started"),
        Task(id=16, description="Task 3", status="finished")
    ]
    return TaskQueue(tasks)


class TestTaskQueueInitialization:
    """Тесты инициализации TaskQueue"""
    
    def test_init_empty_queue(self, empty_queue):
        """Тест создания пустой очереди"""
        assert len(empty_queue) == 0
        assert empty_queue.is_empty()
    
    def test_init_with_tasks(self, sample_tasks):
        """Тест создания очереди со списком задач"""
        queue = TaskQueue(sample_tasks)
        assert len(queue) == len(sample_tasks)
        assert not queue.is_empty()
    
    def test_init_with_invalid_tasks(self):
        """Тест создания очереди с некорректными элементами"""
        with pytest.raises(TaskQueueException, match="All elements must be Task objects"):
            TaskQueue([1, 2, 3, "not task"])
    
    def test_init_with_empty_list(self):
        """Тест создания очереди с пустым списком"""
        queue = TaskQueue([])
        assert len(queue) == 0
        assert queue.is_empty()


class TestTaskQueueAdd:
    """Тесты добавления задач в очередь"""
    
    def test_add_single_task(self, empty_queue, sample_task):
        """Тест добавления одной задачи"""
        empty_queue.add(sample_task)
        assert len(empty_queue) == 1
        assert sample_task in empty_queue
    
    def test_add_multiple_tasks(self, empty_queue, sample_tasks):
        """Тест добавления нескольких задач"""
        for task in sample_tasks:
            empty_queue.add(task)
        assert len(empty_queue) == len(sample_tasks)
    
    def test_add_invalid_task(self, empty_queue):
        """Тест добавления некорректного объекта"""
        with pytest.raises(TaskQueueException, match="is not a Task"):
            empty_queue.add("not a task")


class TestTaskQueueIteration:
    """Тесты итерации по очереди"""
    
    def test_forward_iteration(self, queue_with_tasks, sample_tasks):
        """Тест прямой итерации"""
        tasks = list(queue_with_tasks)
        assert len(tasks) == len(sample_tasks)
        for i, task in enumerate(tasks):
            assert task.id == sample_tasks[i].id
    
    def test_reverse_iteration(self, queue_with_tasks, sample_tasks):
        """Тест обратной итерации"""
        tasks = list(reversed(queue_with_tasks))
        assert len(tasks) == len(sample_tasks)
        for i, task in enumerate(tasks):
            assert task.id == sample_tasks[-(i + 1)].id
    
    def test_iteration_with_modification(self, queue_with_three_tasks):
        """Тест итерации при модификации очереди"""
        iterator = iter(queue_with_three_tasks)
        next(iterator)
        queue_with_three_tasks.add(Task(id=4))
        try:
            while True:
                next(iterator)
        except StopIteration:
            pass
    
    def test_empty_queue_iteration(self, empty_queue):
        """Тест итерации по пустой очереди"""
        tasks = list(empty_queue)
        assert len(tasks) == 0
        tasks_rev = list(reversed(empty_queue))
        assert len(tasks_rev) == 0


class TestTaskQueueFilter:
    """Тесты фильтрации очереди"""
    
    def test_filter_by_status(self, queue_with_tasks):
        """Тест фильтрации по статусу"""
        created_tasks = list(queue_with_tasks.filter_by(status="created"))
        assert all(task.status == "created" for task in created_tasks)
    
    def test_filter_by_priority(self, queue_with_tasks):
        """Тест фильтрации по приоритету"""
        tasks = list(queue_with_tasks.filter_by(priority=3))
        assert all(task.priority == 3 for task in tasks)
    
    def test_filter_by_multiple_attributes(self, queue_with_tasks):
        """Тест фильтрации по нескольким атрибутам"""
        tasks = list(queue_with_tasks.filter_by(status="finished", priority=3))
        for task in tasks:
            assert task.status == "finished"
            assert task.priority == 3
    
    def test_filter_no_results(self, queue_with_tasks):
        """Тест фильтрации без результатов"""
        tasks = list(queue_with_tasks.filter_by(status="nonexistent"))
        assert len(tasks) == 0
    
    def test_filter_is_lazy(self, queue_with_tasks):
        """Тест ленивой фильтрации"""
        generator = queue_with_tasks.filter_by(status="created")
        assert hasattr(generator, '__iter__')
        assert hasattr(generator, '__next__')


class TestTaskQueueGetItem:
    """Тесты доступа по индексу"""
    
    def test_get_item_by_index(self, queue_with_tasks, sample_tasks):
        """Тест получения элемента по индексу"""
        assert queue_with_tasks[0].id == sample_tasks[0].id
        assert queue_with_tasks[2].id == sample_tasks[2].id
    
    def test_get_item_slice(self, queue_with_tasks):
        """Тест получения среза"""
        sliced = queue_with_tasks[1:3]
        assert isinstance(sliced, TaskQueue)
        assert len(sliced) == 2
    
    def test_get_item_negative_index(self, queue_with_tasks, sample_tasks):
        """Тест получения по отрицательному индексу"""
        assert queue_with_tasks[-1].id == sample_tasks[-1].id
    
    def test_get_item_out_of_range(self, queue_with_tasks):
        """Тест выхода за границы"""
        with pytest.raises(IndexError):
            _ = queue_with_tasks[100]


class TestTaskQueueSetItem:
    """Тесты изменения по индексу"""
    
    def test_set_item_valid(self, queue_with_tasks):
        """Тест изменения элемента по индексу"""
        new_task = Task(id=100, description="New task")
        old_id = queue_with_tasks[0].id
        queue_with_tasks[0] = new_task
        assert queue_with_tasks[0].id != old_id
        assert queue_with_tasks[0].id == new_task.id
    
    def test_set_item_invalid(self, queue_with_tasks):
        """Тест изменения на некорректный элемент"""
        with pytest.raises(TaskQueueException, match="Cannot set non-Task object"):
            queue_with_tasks[0] = "not a task"


class TestTaskQueueDelItem:
    """Тесты удаления по индексу"""
    
    def test_del_item(self, queue_with_tasks):
        """Тест удаления элемента по индексу"""
        initial_len = len(queue_with_tasks)
        del queue_with_tasks[0]
        assert len(queue_with_tasks) == initial_len - 1
    
    def test_del_item_out_of_range(self, queue_with_tasks):
        """Тест удаления по несуществующему индексу"""
        with pytest.raises(IndexError):
            del queue_with_tasks[100]


class TestTaskQueueContains:
    """Тесты проверки вхождения"""

    def test_contains_correct(self, queue_with_three_tasks, sample_task):
        """Тест проверки вхождения в очередь"""
        q = queue_with_three_tasks
        q.add(sample_task)
        assert sample_task in q

    def test_contains_empty_queue(self, empty_queue, sample_task):
        """Тест проверки вхождения в пустую очередь"""
        assert sample_task not in empty_queue
   

class TestTaskQueueAddition:
    """Тесты операции сложения"""
    
    def test_add_taskqueue(self, queue_with_three_tasks):
        """Тест сложения двух очередей"""
        other_queue = TaskQueue([Task(id=4), Task(id=5)])
        result = queue_with_three_tasks + other_queue
        assert len(result) == 5
        assert isinstance(result, TaskQueue)
    
    def test_add_single_task(self, queue_with_three_tasks):
        """Тест сложения очереди и задачи"""
        new_task = Task(id=4)
        result = queue_with_three_tasks + new_task
        assert len(result) == 4
        assert new_task in result
    
    def test_add_list_of_tasks(self, queue_with_three_tasks, sample_tasks):
        """Тест сложения очереди и списка задач"""
        result = queue_with_three_tasks + sample_tasks
        assert len(result) == 3 + len(sample_tasks)
    
    def test_add_invalid_type(self, queue_with_three_tasks):
        """Тест сложения с некорректным типом"""
        with pytest.raises(TaskQueueException, match="Cannot add TaskQueue and"):
            _ = queue_with_three_tasks + "invalid"
    
    def test_iadd_taskqueue(self, queue_with_three_tasks):
        """Тест inplace сложения очередей"""
        other_queue = TaskQueue([Task(id=4), Task(id=5)])
        original_id = id(queue_with_three_tasks)
        queue_with_three_tasks += other_queue
        assert len(queue_with_three_tasks) == 5
        assert id(queue_with_three_tasks) == original_id
    
    def test_iadd_single_task(self, queue_with_three_tasks):
        """Тест inplace сложения с задачей"""
        new_task = Task(id=4)
        queue_with_three_tasks += new_task
        assert len(queue_with_three_tasks) == 4
    
    def test_iadd_invalid_type(self, queue_with_three_tasks):
        """Тест inplace сложения с некорректным типом"""
        with pytest.raises(TaskQueueException):
            queue_with_three_tasks += "invalid"


class TestTaskQueueSubtraction:
    """Тесты операции вычитания"""
    
    def test_subtract_task(self, queue_with_tasks, sample_tasks):
        """Тест вычитания одной задачи"""
        task_to_remove = sample_tasks[0]
        result = queue_with_tasks - task_to_remove
        assert task_to_remove not in result
        assert len(result) == len(queue_with_tasks) - 1
    
    def test_subtract_taskqueue(self, queue_with_tasks):
        """Тест вычитания другой очереди"""
        tasks_to_remove = TaskQueue([queue_with_tasks[0], queue_with_tasks[1]])
        result = queue_with_tasks - tasks_to_remove
        assert len(result) == len(queue_with_tasks) - 2
    
    def test_subtract_list(self, queue_with_tasks):
        """Тест вычитания списка задач"""
        tasks_to_remove = [queue_with_tasks[0], queue_with_tasks[1]]
        result = queue_with_tasks - tasks_to_remove
        assert len(result) == len(queue_with_tasks) - 2
    
    def test_subtract_by_id(self, queue_with_tasks):
        """Тест вычитания по ID"""
        task_id = queue_with_tasks[0].id
        result = queue_with_tasks - task_id
        assert all(task.id != task_id for task in result)
    
    def test_subtract_by_callable(self, queue_with_tasks):
        """Тест вычитания с использованием callable"""
        result = queue_with_tasks - (lambda t: t.priority > 3)
        assert all(task.priority <= 3 for task in result)
    
    def test_subtract_invalid_type(self, queue_with_tasks):
        """Тест вычитания с некорректным типом"""
        with pytest.raises(TaskQueueException):
            _ = queue_with_tasks - "invalid"
    
    def test_isub_task(self, queue_with_tasks, sample_tasks):
        """Тест inplace вычитания задачи"""
        task_to_remove = sample_tasks[0]
        original_id = id(queue_with_tasks)
        queue_with_tasks -= task_to_remove
        assert task_to_remove not in queue_with_tasks
        assert id(queue_with_tasks) == original_id
    
    def test_isub_by_id(self, queue_with_tasks):
        """Тест inplace вычитания по ID"""
        task_id = queue_with_tasks[0].id
        queue_with_tasks -= task_id
        assert all(task.id != task_id for task in queue_with_tasks)
    
    def test_isub_by_callable(self, queue_with_tasks):
        """Тест inplace вычитания с callable"""
        queue_with_tasks -= (lambda t: t.status == "created")
        assert all(task.status != "created" for task in queue_with_tasks)
    
    def test_subtract_nonexistent_task(self, queue_with_tasks):
        """Тест вычитания несуществующей задачи"""
        new_task = Task(id=999)
        result = queue_with_tasks - new_task
        assert len(result) == len(queue_with_tasks)


class TestTaskQueueLen:
    """Тесты длины очереди"""
    
    def test_len_empty(self, empty_queue):
        """Тест длины пустой очереди"""
        assert len(empty_queue) == 0
    
    def test_len_non_empty(self, queue_with_tasks, sample_tasks):
        """Тест длины непустой очереди"""
        assert len(queue_with_tasks) == len(sample_tasks)


class TestTaskQueueIsEmpty:
    """Тесты проверки пустоты"""
    
    def test_is_empty_true(self, empty_queue):
        """Тест пустой очереди"""
        assert empty_queue.is_empty()
    
    def test_is_empty_false(self, queue_with_tasks):
        """Тест непустой очереди"""
        assert not queue_with_tasks.is_empty()


class TestTaskQueueRepr:
    """Тесты строкового представления"""
    
    def test_repr_empty(self, empty_queue):
        """Тест представления пустой очереди"""
        assert repr(empty_queue) == "Task queue: []"
    
    def test_repr_non_empty(self, queue_with_three_tasks):
        """Тест представления непустой очереди"""
        repr_str = repr(queue_with_three_tasks)
        assert "Task queue:" in repr_str
        assert "Task '13'" in repr_str
        assert "Task '214'" in repr_str
        assert "Task '16'" in repr_str


class TestTaskQueueRandomCases:
    """Тесты случайных ситуаций"""
    
    def test_large_queue(self):
        """Тест с большой очередью"""
        tasks = [Task(id=i) for i in range(1000)]
        queue = TaskQueue(tasks)
        assert len(queue) == 1000
        assert queue[0].id == 0
        assert queue[999].id == 999
    
    def test_queue_with_all_statuses(self):
        """Тест очереди с задачами во всех статусах"""
        tasks = [
            Task(id=10, status="created"),
            Task(id=20, status="started"),
            Task(id=30, status="finished")
        ]
        queue = TaskQueue(tasks)
        assert len(list(queue.filter_by(status="created"))) == 1
        assert len(list(queue.filter_by(status="started"))) == 1
        assert len(list(queue.filter_by(status="finished"))) == 1

    def test_multiple_operations_chain(self, queue_with_three_tasks):
        """Тест цепочки операций"""
        new_task = Task(id=4)
        result = (queue_with_three_tasks + new_task) - new_task
        assert len(result) == 3
        assert new_task not in result


class TestTaskIterator:
    """Тесты TaskIterator"""
    
    def test_iterator_creation(self, sample_tasks):
        """Тест создания итератора"""
        iterator = TaskIterator(sample_tasks)
        assert iterator._data == sample_tasks
        assert iterator._index == 0
    
    def test_iterator_iteration(self, sample_tasks):
        """Тест итерации"""
        iterator = TaskIterator(sample_tasks)
        tasks = list(iterator)
        assert tasks == sample_tasks
    
    def test_iterator_stop_iteration(self):
        """Тест StopIteration"""
        iterator = TaskIterator([])
        with pytest.raises(StopIteration):
            next(iterator)


class TestTaskReverseIterator:
    """Тесты TaskReverseIterator"""
    
    def test_reverse_iterator_creation(self, sample_tasks):
        """Тест создания обратного итератора"""
        iterator = TaskReverseIterator(sample_tasks)
        assert iterator._data == sample_tasks
        assert iterator._index == len(sample_tasks) - 1
    
    def test_reverse_iterator_iteration(self, sample_tasks):
        """Тест обратной итерации"""
        iterator = TaskReverseIterator(sample_tasks)
        tasks = list(iterator)
        assert tasks == sample_tasks[::-1]
    
    def test_reverse_iterator_stop_iteration(self):
        """Тест StopIteration для обратного итератора"""
        iterator = TaskReverseIterator([])
        with pytest.raises(StopIteration):
            next(iterator)