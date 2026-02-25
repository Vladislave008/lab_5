from task_examples import TaskClass, TaskDataclass, TaskNamedTuple
from task_source_examples import FileSource, BadFileSource, ApiSource, GeneratorSource
from task_module import TaskModule

if __name__ == '__main__':
    task1 = TaskDataclass(id=1, payload={'data': 'test'})
    task2 = TaskNamedTuple(id='2', payload=[1, 2, 3])
    task3 = TaskClass(id=[3], payload='simple')
    task4 = {'id': 1, 'payload': [42]} 
    
    file_source = FileSource('tasks.json')
    bad_file_source = BadFileSource('project_122.flp')
    api_source = ApiSource('https://api.example.com/view/tasks')
    generator_source = GeneratorSource(3)

    tm = TaskModule()
    for task in [task1, task2, task3, task4]:
        tm.add_task(task)
    print('-----------------------------------------')
    for task_source in [file_source, bad_file_source, api_source, generator_source]:
        tm.add_source(task_source)
    print('-----------------------------------------')
    tm.get_tasks_from_sources()