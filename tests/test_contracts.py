import pytest
from typing import Any
from unittest.mock import Mock
from src.task_examples import TaskClass, TaskDataclass, TaskNamedTuple
from src.task_source_examples import FileSource, BadFileSource, ApiSource, GeneratorSource
from src.protocols import TaskProtocol, TaskSourceProtocol
from src.task_module import TaskModule


@pytest.fixture
def valid_task_class():
    return TaskClass(id=42, payload={'test': 'data'})

@pytest.fixture
def valid_task_dataclass():
    return TaskDataclass(id=43, payload=[1, 2, 3])

@pytest.fixture
def valid_task_namedtuple():
    return TaskNamedTuple(id=44, payload='simple payload')

@pytest.fixture
def invalid_task_wrong_id_type():
    return TaskNamedTuple(id={5}, payload='wrong id type')

@pytest.fixture
def invalid_task_missing_id():
    class NoIdTask:
        def __init__(self, payload):
            self.payload = payload
    return NoIdTask(payload='data')

@pytest.fixture
def invalid_task_missing_payload():
    class NoPayloadTask:
        def __init__(self, id):
            self.id = id
    return NoPayloadTask(id=46)

@pytest.fixture
def file_source():
    return FileSource('test_tasks.json')

@pytest.fixture
def api_source():
    return ApiSource('https://test-api.com/view/tasks')

@pytest.fixture
def generator_source():
    return GeneratorSource(5)

@pytest.fixture
def bad_source():
    return BadFileSource('bad_source.txt')

@pytest.fixture
def all_valid_sources(file_source, api_source, generator_source):
    return [file_source, api_source, generator_source]

@pytest.fixture
def task_module():
    return TaskModule()

class TestProtocols:
    '''Тесты инициализации протоколов'''
    def test_task_protocol_definition(self):
        assert hasattr(TaskProtocol, 'id')
        assert hasattr(TaskProtocol, 'payload')
        assert isinstance(TaskProtocol.id, property)
        assert isinstance(TaskProtocol.payload, property)

    def test_task_source_protocol_definition(self):
        assert hasattr(TaskSourceProtocol, 'get_tasks')
        assert callable(TaskSourceProtocol.get_tasks)


class TestTaskContract:
    '''Проверка соблюдения контракта для задач'''
    def test_valid_tasks_pass_contract(self, valid_task_class, valid_task_dataclass, valid_task_namedtuple, task_module):
        assert task_module._check_task_contract(valid_task_class) is True
        assert task_module._check_task_contract(valid_task_dataclass) is True
        assert task_module._check_task_contract(valid_task_namedtuple) is True

    def test_invalid_tasks_fail(self, invalid_task_wrong_id_type, invalid_task_missing_id, invalid_task_missing_payload, task_module):
        assert task_module._check_task_contract(invalid_task_wrong_id_type) is False
        assert task_module._check_task_contract(invalid_task_missing_id) is False
        assert task_module._check_task_contract(invalid_task_missing_payload) is False

    def test_dict_is_a_task(self, task_module):
        dict_task = {'id': 100, 'payload': 'data'}
        assert task_module._check_task_contract(dict_task) is True

    def test_task_with_complex_payload(self, task_module):
        complex_payload = {
            'something': {'list': [1, 2, 3], 'dict': {'a': 1}},
            'function': lambda x: x,
            'none': 67
        }
        task = TaskDataclass(id=1234, payload=complex_payload)
        assert task_module._check_task_contract(task) is True

class TestTaskSourceContract:
    '''Проверка соблюдения контракта для источников задач'''
    def test_valid_sources_pass_contract(self, all_valid_sources, task_module):
        for source in all_valid_sources:
            assert task_module._check_task_source_contract(source) is True

    def test_bad_source_fails_contract(self, bad_source, task_module):
        assert task_module._check_task_source_contract(bad_source) is False

    def test_task_is_not_source(self, valid_task_class, task_module):
        assert task_module._check_task_source_contract(valid_task_class) is False

    def test_source_with_custom_method_name_fails(self, task_module):
        class CustomSource:
            def fetch_tasks(self):
                return []
        source = CustomSource()
        assert task_module._check_task_source_contract(source) is False

class TestWithMocks:
    '''Проверка абстрактных мок-заглушек'''
    def test_mock_source_passes_contract(self, task_module):
        mock_source = Mock()
        mock_source.get_tasks = lambda : []
        assert task_module._check_task_source_contract(mock_source) is True

    def test_mock_source_with_wrong_method_fails(self, task_module):
        mock_source = Mock()
        mock_source.fetch_tasks.return_value = []
        assert task_module._check_task_source_contract(mock_source) is False

    def test_mock_task_passes_contract(self, task_module):
        mock_task = Mock()
        mock_task.id = 42
        mock_task.payload = 'data'
        assert task_module._check_task_contract(mock_task) is True

    def test_mock_task_with_wrong_id_type_fails(self, task_module):
        mock_task = Mock()
        mock_task.id = {23}
        mock_task.payload = 'data'
        assert task_module._check_task_contract(mock_task) is False

class TestExtensibility:
    '''Тесты расширяемости алгоритма'''
    def test_new_source(self, task_module):
        class DatabaseSource:
            def __init__(self, connection_string):
                self.connection_string = connection_string
            def get_tasks(self):
                return [
                    TaskClass(id=1001, payload='from_db_1'),
                    TaskClass(id=1002, payload='from_db_2'),
                ]
        db_source = DatabaseSource('sqlite://test.db')
        assert task_module._check_task_source_contract(db_source) is True
        tasks = db_source.get_tasks()
        for task in tasks:
            assert task_module._check_task_contract(task) is True

    def test_new_task(self, task_module):
        class NewTaskType:
            def __init__(self, task_id: int, data: Any):
                self.id = task_id
                self.payload = data
        new_task = NewTaskType(2000, {'new': 'type'})
        assert task_module._check_task_contract(new_task) is True

class TestTaskAddition:
    '''Тесты добавления задач в модуль'''
    def test_add_valid_task(self, valid_task_class, task_module):
        initial_count = len(task_module.tasks)
        task_module.add_task(valid_task_class)
        assert len(task_module.tasks) == initial_count + 1
        assert valid_task_class in task_module.tasks

    def test_add_multiple_valid_tasks(self, valid_task_class, valid_task_dataclass, valid_task_namedtuple, task_module):
        initial_count = len(task_module.tasks)
        task_module.add_task(valid_task_class)
        task_module.add_task(valid_task_dataclass)
        task_module.add_task(valid_task_namedtuple)
        assert len(task_module.tasks) == initial_count + 3

    def test_add_invalid_task_does_not_add(self, invalid_task_wrong_id_type, task_module):
        initial_count = len(task_module.tasks)
        task_module.add_task(invalid_task_wrong_id_type)
        assert len(task_module.tasks) == initial_count
        assert invalid_task_wrong_id_type not in task_module.tasks

    def test_get_tasks_from_sources(self, task_module, file_source, generator_source):
        task_module.add_source(file_source)
        task_module.add_source(generator_source)
        initial_task_count = len(task_module.tasks)
        task_module.get_tasks_from_sources()
        assert len(task_module.tasks) == initial_task_count + 7

class TestSourceAddition:
    '''Тесты добавления источников в модуль'''
    def test_add_valid_source(self, file_source, task_module):
        initial_count = len(task_module.sources)
        task_module.add_source(file_source)
        assert len(task_module.sources) == initial_count + 1
        assert file_source in task_module.sources

    def test_add_multiple_valid_sources(self, all_valid_sources, task_module):
        initial_count = len(task_module.sources)
        for source in all_valid_sources:
            task_module.add_source(source)
        assert len(task_module.sources) == initial_count + len(all_valid_sources)

    def test_add_invalid_source_does_not_add(self, bad_source, task_module):
        initial_count = len(task_module.sources)
        task_module.add_source(bad_source)
        assert len(task_module.sources) == initial_count
        assert bad_source not in task_module.sources

    def test_add_task_as_source_fails(self, valid_task_class, task_module):
        initial_count = len(task_module.sources)
        task_module.add_source(valid_task_class)
        assert len(task_module.sources) == initial_count
        assert valid_task_class not in task_module.sources
