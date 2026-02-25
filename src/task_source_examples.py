from task_examples import TaskClass, TaskDataclass, TaskNamedTuple

class FileSource:
    '''Заглушка для имитации чтения задач из файла'''
    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_tasks(self) -> list[TaskDataclass]:
        print(f'Reading tasks from file: {self.file_path}')
        return [
            TaskDataclass(id=101, payload={'order_id': 5001, 'amount': 1500}),
            TaskDataclass(id=102, payload={'order_id': 5002, 'amount': 500}),
        ]

class BadFileSource:
    '''Заглушка для имитации чтения задач из файла'''
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_tasks(self) -> list[TaskDataclass]:
        print(f'Reading tasks from file: {self.file_path}')
        return [
            TaskDataclass(id=101, payload={'order_id': 5001, 'amount': 1500}),
            TaskDataclass(id=102, payload={'order_id': 5002, 'amount': 500}),
        ]

class ApiSource:
    '''Заглушка для имитации получение задач из API'''
    def __init__(self, api_url: str):
        self.api_url = api_url

    def get_tasks(self) -> list[TaskClass]:
        print(f'Reading tasks from API: {self.api_url}')
        return [
            TaskClass(id=201, payload={'user': 'john', 'action': 'send'}),
            TaskClass(id='bad_id', payload={'user': 'jane', 'action': 'update'}),
        ]

class GeneratorSource:
    '''Заглушка для имитации генератора задач'''
    def __init__(self, count: int):
        self.count = count

    def get_tasks(self) -> list[TaskNamedTuple]:
        print(f'Generating {self.count} tasks...')
        tasks = []
        for i in range(self.count):
            tasks.append(TaskNamedTuple(id=67 + i, payload=f'generated_task_payload{i}'))
        return tasks
