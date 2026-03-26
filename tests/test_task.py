import pytest
from datetime import datetime, timedelta
from src.task import (Task, TaskException)
from freezegun import freeze_time


@pytest.fixture
def clean_ids():
    """Очищает множество ID перед каждым тестом"""
    Task._all_ids.clear()
    yield
    Task._all_ids.clear()


@pytest.fixture
def sample_task(clean_ids):
    """Создает базовую задачу"""
    task = Task(id=1, payload={"data": "test"}, description="Test task", 
                priority=5, status="created", planned_time=60)
    return task


@pytest.fixture
def started_task(clean_ids):
    """Создает запущенную задачу"""
    task = Task(id=2, payload="data", description="Started task", priority=3)
    task.status = "started"
    return task


@pytest.fixture
def finished_task(clean_ids):
    """Создает завершенную задачу"""
    task = Task(id=3, payload="data", description="Finished task", priority=7)
    task.status = "started"
    task.status = "finished"
    return task


class TestTaskCreation:
    """Тесты создания задач"""
    
    def test_create_task_with_all_params(self, clean_ids):
        """Создание задачи со всеми параметрами"""
        task = Task(
            id=100,
            payload={"key": "value"},
            description="Full task",
            priority=8,
            status="created",
            planned_time=120
        )
        
        assert task.id == 100
        assert task.payload == {"key": "value"}
        assert task.description == "Full task"
        assert task.priority == 8
        assert task.status == "created"
        assert task.planned_time == timedelta(seconds=120)
        assert task.created_at is not None
        assert isinstance(task.created_at, datetime)
    
    def test_create_task_minimal_params(self, clean_ids):
        """Создание задачи с минимальными параметрами"""
        task = Task(id=101)
        
        assert task.id == 101
        assert task.payload is None
        assert task.description == ""
        assert task.priority == 0
        assert task.status == "created"
        assert task.planned_time is None
    
    def test_create_task_without_id_raises_error(self, clean_ids):
        """Создание задачи без ID вызывает ошибку"""
        with pytest.raises(TypeError, match="Task must have an ID"):
            task = Task()
    
    def test_create_task_with_str_id(self, clean_ids):
        """Создание задачи со строковым ID"""
        task = Task(id="task_001")
        assert task.id == "task_001"
    
    def test_create_task_duplicate_id_raises_error(self, clean_ids):
        """Создание задачи с существующим ID вызывает ошибку"""
        task = Task(id=200)
        with pytest.raises(TaskException, match="already exists"):
            task1 = Task(id=200)
    
    def test_task_added_to_all_ids(self, clean_ids):
        """Задача добавляется в множество всех ID"""
        assert len(Task.get_all_ids()) == 0
        task = Task(id=300)
        a = set()
        a.add(300)
        assert Task.get_all_ids() == a
        task1 = Task(id=301)
        a.add(301)
        assert Task.get_all_ids() == a

class TestPriorityAttr:
    """Тесты атрибута priority"""
    
    def test_priority_set_valid(self, sample_task):
        """Установка корректного приоритета"""
        sample_task.priority = 7
        assert sample_task.priority == 7
    
    def test_priority_set_invalid_type(self, sample_task):
        """Установка приоритета неверного типа"""
        with pytest.raises(TypeError, match="Task 'priority' attribute must be int"):
            sample_task.priority = "5"
    
    def test_priority_set_below_min(self, sample_task):
        """Установка приоритета ниже минимального"""
        with pytest.raises(ValueError, match="Invalid task 'priority' value"):
            sample_task.priority = -1
    
    def test_priority_set_above_max(self, sample_task):
        """Установка приоритета выше максимального"""
        with pytest.raises(ValueError, match="Invalid task 'priority' value"):
            sample_task.priority = 11

class TestPlannedTimeAttr:
    """Тесты атрибута planned_time"""
    
    def test_planned_time_set_timedelta(self, sample_task):
        """Установка timedelta"""
        delta = timedelta(hours=2)
        sample_task.planned_time = delta
        assert sample_task.planned_time == delta
    
    def test_planned_time_set_seconds_int(self, sample_task):
        """Установка секунд как int"""
        sample_task.planned_time = 180
        assert sample_task.planned_time == timedelta(seconds=180)
    
    def test_planned_time_set_seconds_float(self, sample_task):
        """Установка секунд как float"""
        sample_task.planned_time = 90.5
        assert sample_task.planned_time == timedelta(seconds=90.5)
    
    def test_planned_time_set_none(self, sample_task):
        """Установка None"""
        sample_task.planned_time = None
        assert sample_task.planned_time is None
    
    def test_planned_time_set_negative_raises(self, sample_task):
        """Установка отрицательного времени вызывает ошибку"""
        with pytest.raises(ValueError, match="must be positive"):
            sample_task.planned_time = -10
    
    def test_planned_time_set_zero_raises(self, sample_task):
        """Установка нулевого времени вызывает ошибку"""
        with pytest.raises(ValueError, match="must be positive"):
            sample_task.planned_time = 0
    
    def test_planned_time_set_invalid_type(self, sample_task):
        """Установка неверного типа"""
        with pytest.raises(TypeError, match="must be timedelta, seconds, or None"):
            sample_task.planned_time = "invalid"


class TestIdAttr:
    """Тесты атрибута id"""
    
    def test_id_change_updates_all_ids(self, clean_ids):
        """Изменение ID обновляет множество all_ids"""
        task = Task(id=400)
        assert Task.get_all_ids() == {400}
        
        task.id = 401
        assert Task.get_all_ids() == {401}
        assert task.id == 401
    
    def test_id_change_to_existing_raises(self, clean_ids):
        """Изменение ID на существующий вызывает ошибку"""
        task = Task(id=500)
        task1 = Task(id=501)
        
        with pytest.raises(TaskException, match="Task with ID '500' already exists"):
            task1.id = 500
    
    def test_id_set_none_raises(self, sample_task):
        """Установка None как ID вызывает ошибку"""
        with pytest.raises(TypeError, match="Task must have an ID"):
            sample_task.id = None
    
    def test_id_set_invalid_type_raises(self, sample_task):
        """Установка неверного типа ID"""
        with pytest.raises(TypeError, match="Task 'ID' attribute must be str | int"):
            sample_task.id = 3.14


class TestStatusAttr:
    """Тесты атрибута status"""
    
    def test_status_created_resets_timers(self, started_task):
        """Сброс статуса на 'created' обнуляет таймеры"""
        assert started_task.started_at is not None
        started_task.status = "created"
        assert started_task.started_at is None
        assert started_task.finished_at is None
    
    def test_status_started_sets_started_at(self, sample_task):
        """Переход в статус 'started' устанавливает started_at"""
        assert sample_task.started_at is None
        sample_task.status = "started"
        assert sample_task.started_at is not None
    
    def test_status_started_already_started_raises(self, started_task):
        """Повторный запуск задачи вызывает ошибку"""
        with pytest.raises(TaskException, match="Task is already started"):
            started_task.status = "started"
    
    def test_status_finished_from_created_raises(self, sample_task):
        """Завершение незапущенной задачи вызывает ошибку"""
        with pytest.raises(TaskException, match="can't be finished"):
            sample_task.status = "finished"
    
    def test_status_finished_from_started(self, started_task):
        """Завершение запущенной задачи"""
        started_task.status = "finished"
        assert started_task.status == "finished"
        assert started_task.finished_at is not None
    
    def test_status_finished_already_finished_raises(self, finished_task):
        """Повторное завершение задачи вызывает ошибку"""
        with pytest.raises(TaskException, match="Task is already finished"):
            finished_task.status = "finished"
    
    def test_status_invalid_value_raises(self, sample_task):
        """Установка недопустимого статуса"""
        with pytest.raises(ValueError, match="Invalid task 'status' value"):
            sample_task.status = "invalid_status"


class TestCreatedAtAttr:
    def test_created_at_readonly(self, sample_task):
        """created_at нельзя изменить"""
        with pytest.raises(AttributeError, match="read-only"):
            sample_task.created_at = datetime.now()


class TestDurationAttr:
    """Тесты атрибута duration"""
    
    def test_duration_none_when_created(self, sample_task):
        """В статусе created duration = None"""
        assert sample_task.duration is None
        
    @freeze_time("2024-01-01 12:00:00")
    def test_duration_increases_when_started(self, started_task):
        """В статусе started duration увеличивается"""
        task = Task(id=1)
        task.status = "started"
        with freeze_time("2024-01-01 12:05:00"):
            assert task.duration == timedelta(seconds=300)

    def test_duration_cached_when_finished(self, finished_task):
        """В статусе finished duration кэшируется"""
        duration1 = finished_task.duration
        duration2 = finished_task.duration
        assert duration1 == duration2
    
    def test_duration_is_readonly(self, sample_task):
        """duration только для чтения"""
        with pytest.raises(AttributeError, match="read-only"):
            sample_task.duration = timedelta(seconds=10)


class TestIsReadyAttr:
    """Тесты атрибута is_ready"""
    
    def test_is_ready_true_with_payload_and_id(self, clean_ids):
        """is_ready = True при наличии payload и ID"""
        task = Task(id=1, payload="data")
        assert task.is_ready is True
    
    def test_is_ready_false_without_payload(self, clean_ids):
        """is_ready = False без payload"""
        task = Task(id=1)
        assert task.is_ready is False
    
    def test_is_ready_true_in_created_status(self, clean_ids):
        """is_ready = True в статусе created"""
        task = Task(id=1, payload="data", status="created")
        assert task.is_ready is True
    
    def test_is_ready_true_in_finished_status(self, clean_ids):
        """is_ready = True в статусе finished"""
        task = Task(id=1, payload="data", status="created")
        task.status = "started"
        task.status = "finished"
        assert task.is_ready is True
    
    def test_is_ready_false_in_started_status(self, clean_ids):
        """is_ready = False в статусе started"""
        task = Task(id=1, payload="data", status="created")
        task.status = "started"
        assert task.is_ready is False


class TestIsValidAttr:
    """Тесты атрибута is_valid"""
    
    def test_is_valid_returns_string(self, sample_task):
        """is_valid возвращает строку"""
        result = sample_task.is_valid
        assert isinstance(result, str)
        assert "Task '1' validity:" in result
        assert "Filled attributes:" in result
        assert "Empty attributes:" in result
    
    def test_is_valid_calculates_percentage(self, clean_ids):
        """Правильный расчет процента заполненности"""
        task = Task(id=1, payload="data", description="desc", priority=5, 
                    status="created", planned_time=60)
        result = task.is_valid
        assert "100" in result
        assert "Filled attributes:" in result
    
    def test_is_valid_partially_filled(self, clean_ids):
        """Частично заполненная задача"""
        task = Task(id=1)
        result = task.is_valid
        assert "33.33" in result
        assert "'id'" in result


class TestTaskDeletion:
    """Тесты удаления задач"""
    
    def test_delete_removes_id_from_all_ids(self, clean_ids):
        """Метод delete удаляет ID из множества"""
        task = Task(id=600)
        assert Task.get_all_ids() == {600}
        
        task.delete()
        assert Task.get_all_ids() == set()
    
    def test_del_removes_id_from_all_ids(self, clean_ids):
        """__del__ удаляет ID из множества"""
        task = Task(id=700)
        assert Task.get_all_ids() == {700}
        
        del task
        assert Task.get_all_ids() == set()


class TestAttributeRestriction:
    """Тесты запрета на добавление новых атрибутов"""
    
    def test_cannot_add_new_attribute(self, sample_task):
        """Нельзя добавить новый атрибут"""
        with pytest.raises(TaskException, match="Unknown attribute"):
            sample_task.new_attr = "value"
    
    def test_can_add_protected_attribute(self, sample_task):
        """Можно добавить защищенный атрибут"""
        sample_task._custom = "value"
        assert sample_task._custom == "value"
    
    def test_can_add_allowed_attribute(self, sample_task):
        """Можно добавить разрешенный атрибут"""
        sample_task.is_valid = "custom"
        assert sample_task.is_valid == "custom"


class TestGetters:
    """Тесты get-методов"""
    
    def test_started_at_getter(self, started_task):
        """getter started_at работает"""
        assert started_task.started_at is not None
    
    def test_started_at_none_when_created(self, sample_task):
        """started_at = None для новой задачи"""
        assert sample_task.started_at is None
    
    def test_finished_at_getter(self, finished_task):
        """getter finished_at работает"""
        assert finished_task.finished_at is not None
    
    def test_finished_at_none_when_not_finished(self, started_task):
        """finished_at = None для незавершенной задачи"""
        assert started_task.finished_at is None
    
    def test_get_all_ids_returns_copy(self, clean_ids):
        """get_all_ids возвращает копию множества"""
        task = Task(id=900)
        ids = Task.get_all_ids()
        ids.add(999)
        assert Task.get_all_ids() == {900}